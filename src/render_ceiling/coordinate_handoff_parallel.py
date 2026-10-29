from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import threading
import time
import fcntl
from pathlib import Path
from render_ceiling import coordinate_handoff_sonnet as S


def main(stage='main'):
    (S.ROOT / 'outputs').mkdir(exist_ok=True)
    lockfile = (S.ROOT/'outputs/sonnet_handoff.lock').open('a')
    fcntl.flock(lockfile, fcntl.LOCK_EX|fcntl.LOCK_NB)
    state = json.loads(S.OUT.read_text())
    S.check(state)
    if stage == 'main':
        assert state.get('pilot_gate', {}).get('passed') is True
    assert state['pending'] is None and not state.get('parallel_pending')
    assert state['uncertain_charge_reserve_usd'] == 0
    assert all(r['response'].get('stop_reason') in ['end_turn', 'max_tokens'] for r in state['records'])
    identity = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    amendment = {'runner_sha256': identity, 'workers': 4, 'scope': 'Scheduling only; fixed requests, repetitions, output limits, scoring and budget unchanged; sequential repeats within each input', 'budget': 'Durable reservation for every in-flight call under one shared lock; unknown outcomes retain reservation and stop new work'}
    if 'parallel_execution' in state:
        assert state['parallel_execution'] == amendment
    else:
        state['parallel_execution'] = amendment
    state['parallel_pending'] = {}
    state['status'] = 'RUNNING_' + stage.upper()
    S.save(state)
    mutex, stop = threading.Lock(), threading.Event()
    done = {(r['request_id'], r['repeat']) for r in state['records']}

    def group(q):
        for repeat in range(3):
            if (q['request_id'], repeat) in done:
                continue
            key = q['request_id'] + ':' + str(repeat)
            bound = S.reserve(q, state)
            with mutex:
                if stop.is_set():
                    return
                committed = state['reported_cost_usd'] + state['uncertain_charge_reserve_usd'] + sum(p['reservation_usd'] for p in state['parallel_pending'].values())
                if committed + bound > (7 if stage == 'pilot' else 35):
                    state['status'] = 'BUDGET_STOP'
                    stop.set()
                    S.save(state)
                    return
                state['parallel_pending'][key] = {'request_id': q['request_id'], 'repeat': repeat, 'reservation_usd': bound, 'started_at': time.time()}
                S.save(state)
            started = time.monotonic()
            response = S.request('messages', S.payload(q, True, state['protocol']['max_tokens']))
            usage = response.get('usage')
            cost = sum(usage.get(k, 0)*v for k,v in S.RATES.items())/1e6 if usage else None
            text = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
            row = {'request_id': q['request_id'], 'repeat': repeat, 'stage': stage, 'max_tokens': state['protocol']['max_tokens'], 'prediction': S.parse(text) if response.get('stop_reason') == 'end_turn' else None, 'response': response, 'reported_cost_usd': cost, 'reservation_usd': bound, 'elapsed_seconds': time.monotonic()-started}
            with mutex:
                del state['parallel_pending'][key]
                state['records'].append(row)
                if cost is None:
                    state['uncertain_charge_reserve_usd'] += bound
                else:
                    state['reported_cost_usd'] += cost
                good = response.get('model') == S.MODEL and response.get('stop_reason') in ['end_turn', 'max_tokens'] and cost is not None and cost <= bound
                if not good:
                    state['status'] = 'RESPONSE_AUDIT_STOP'
                    stop.set()
                S.save(state)
                print(json.dumps({'completed': len(state['records']), 'of': 210, 'prediction': row['prediction'], 'stop': response.get('stop_reason'), 'cache_read': (usage or {}).get('cache_read_input_tokens'), 'cost_usd': round(state['reported_cost_usd'], 6)}), flush=True)
    pilot = set(state['protocol']['pilot_request_ids'])
    selected = [q for q in state['requests'] if stage == 'main' or q['request_id'] in pilot]
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(group, selected))
    if not stop.is_set():
        expected = 210 if stage == 'main' else 3*len(pilot)
        assert len(state['records']) == len({(r['request_id'],r['repeat']) for r in state['records']}) == expected
        if stage == 'pilot':
            passed = any(r['response']['usage'].get('cache_read_input_tokens', 0)>0 for r in state['records']) and any(r['response']['usage'].get('cache_creation_input_tokens', 0)>0 for r in state['records'])
            state['pilot_gate'] = {'passed': passed, 'calls': len(state['records']), 'cost_usd': state['reported_cost_usd'], 'outcome_filter': False, 'truncations_retained': sum(r['response']['stop_reason']=='max_tokens' for r in state['records'])}
            state['status'] = 'PILOT_PASSED' if passed else 'CACHE_AUDIT_STOP'
        else:
            state['status'] = 'INFERENCE_COMPLETE'
    assert not state['parallel_pending']
    S.save(state)
    print(json.dumps({'status': state['status'], 'calls': len(state['records']), 'reported_cost_usd': state['reported_cost_usd'], 'uncertain_charge_reserve_usd': state['uncertain_charge_reserve_usd']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['pilot', 'main'])
    main(parser.parse_args().stage)

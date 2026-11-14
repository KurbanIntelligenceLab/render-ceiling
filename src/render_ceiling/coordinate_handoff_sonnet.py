import argparse
from collections import Counter
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/reconstruction_sonnet_pilot/study.json'
SOURCE = ROOT / 'results/reconstruction_vlm_pilot/study.json'
MODEL = 'claude-sonnet-5-5'
CLASSES = ['triclinic', 'monoclinic', 'orthorhombic', 'tetragonal', 'trigonal', 'hexagonal', 'cubic']
RATES = {'input_tokens': 2, 'output_tokens': 10, 'cache_creation_input_tokens': 2.5, 'cache_read_input_tokens': .1}


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def save(s):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(s, indent=2, allow_nan=False) + '\n')
    os.replace(tmp, OUT)


def parse(text):
    hits = re.findall(r'ANSWER:\s*(' + '|'.join(CLASSES) + r')\b', text, re.I)
    if len(hits) == 1:
        return hits[0].lower()
    clean = text.strip().lower().strip('.*` \n')
    return clean if clean in CLASSES else None


def request(endpoint, payload):
    key = os.environ['CLAUDE_API_KEY']
    req = urllib.request.Request('https://api.anthropic.com/v1/' + endpoint, data=json.dumps(payload).encode(), headers={'x-api-key': key, 'anthropic-version': '2026-10-21', 'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        return {'error': {'http_status': e.code, 'detail': e.read().decode(errors='replace').replace(key, '[REDACTED]')[:1000]}}
    except Exception as e:
        return {'error': {'type': type(e).__name__, 'detail': 'Uncertain request outcome; full reservation retained; no automatic retry'}}


def payload(q, generation=False, max_tokens=8192):
    p = {'model': MODEL, 'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': q['prompt'], 'cache_control': {'type': 'ephemeral', 'ttl': '5m'}}]}]}
    if generation:
        p['max_tokens'] = max_tokens
    return p


def prepare():
    assert not OUT.exists(), 'Existing experiment preserved'
    source = json.loads(SOURCE.read_text())
    assert source['status'] == 'COMPLETE'
    assert source['verification']['independent_token_delivery_audit']['complete_prompt_roundtrips'] == 70
    assert source['verification']['independent_scoring_audit']['status'] == 'PASS'
    requests = source['requests']
    cases = source['cases']
    for q in requests:
        assert hashlib.sha256(q['prompt'].encode()).hexdigest() == q['request_id']
        data = json.loads(q['prompt'].split('\n', 1)[1])
        assert set(data) <= {'lattice_rows_angstrom', 'atoms_atomic_number_fractional_xyz'}
        assert len(data['lattice_rows_angstrom']) == 3
    parents = sorted({c['material_id'] for c in cases if c['original_label'] in ['cubic', 'triclinic']})
    assert len(parents) == 2
    pilot_ids = {rid for c in cases if c['material_id'] in parents for rid in c['requests'].values()}
    ordered = sorted(requests, key=lambda q: (q['request_id'] not in pilot_ids, digest([20261028, 'sonnet_order', q['request_id']])))
    protocol = {'model': MODEL, 'api_version': '2026-10-21', 'budget_usd': 35, 'pilot_generation_limit_usd': 7, 'max_tokens': 8192, 'K': 3, 'sampling': 'Native API defaults; no temperature/top_p/top_k or effort override', 'input_policy': 'Exact same 70 audited prompts and 28 case mappings as the local Gemma pilot; no format tuning', 'pilot_parents': parents, 'pilot_request_ids': sorted(pilot_ids), 'pilot_gate': 'All planned pilot responses complete, end_turn, parseable, expected model; at least one eligible full-prefix cache read and at least one write. No accuracy threshold.', 'cache_policy': 'Explicit final text block, five-minute TTL, sequential repeats; prompts shorter than 512 provider tokens cannot cache', 'primary_contrast': 'Split minus Huber majority-vote accuracy on 28 matched cases; parent-cluster descriptive uncertainty', 'secondary': 'Original, stable changed, joint, false restoration, per-condition and per-class outcomes; exact and lattice controls; per-repeat stability', 'voting': 'Three responses per unique prompt; most frequent valid class, ties follow first occurrence; no valid vote is incorrect; invalid votes retained', 'retry_policy': 'No automatic retries, including errors or truncation; retain full charge reservation for unknown outcomes', 'budget_guard': 'Before every generation reserve 1.10*(counted_input_tokens+128)*5m_write_rate + 8192*output_rate; reported spend plus uncertain and in-flight reserves must remain <=35 USD', 'pricing_per_million': RATES, 'pricing_source': 'https://platform.claude.com/docs/en/about-claude/pricing', 'caching_source': 'https://platform.claude.com/docs/en/build-with-claude/prompt-caching', 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'requests_hash': digest(ordered), 'cases_hash': digest(cases)}
    s = {'protocol': protocol, 'protocol_hash': digest(protocol), 'requests': ordered, 'cases': cases, 'preflight': {}, 'records': [], 'pending': None, 'reported_cost_usd': 0, 'uncertain_charge_reserve_usd': 0, 'status': 'PREPARED', 'verification': {'all_input_prompts_identical_to_verified_local_pilot': True, 'cases': 28, 'unique_prompts': 70, 'target_or_method_fields_in_geometry': False}}
    save(s)
    print(json.dumps({'pilot_parents': parents, 'pilot_unique_inputs': len(pilot_ids), 'pilot_generation_calls': 3*len(pilot_ids), 'total_generation_calls': 3*len(ordered), 'budget_usd': 35}))


def check(s):
    p = s['protocol']
    assert digest(p) == s['protocol_hash']
    assert digest(s['requests']) == p['requests_hash'] and digest(s['cases']) == p['cases_hash']
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == p['source_sha256']
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == p['runner_sha256']
    assert p['budget_usd'] == 35


def reserve(q, s):
    n = s['preflight'][q['request_id']]['input_tokens']
    return (1.10*(n+128)*2.5 + s['protocol']['max_tokens']*10)/1e6


def preflight():
    s = json.loads(OUT.read_text())
    check(s)
    for q in s['requests']:
        if q['request_id'] in s['preflight']:
            continue
        result = request('messages/count_tokens', payload(q))
        s['preflight'][q['request_id']] = result
        save(s)
        assert isinstance(result.get('input_tokens'), int), 'Token preflight failed; see sanitized study record'
    pilot = set(s['protocol']['pilot_request_ids'])
    s['preflight_summary'] = {'max_input_tokens': max(v['input_tokens'] for v in s['preflight'].values()), 'cache_eligible_prompts': sum(v['input_tokens'] >= 512 for v in s['preflight'].values()), 'all_calls_upper_bound_usd': 3*sum(reserve(q, s) for q in s['requests']), 'pilot_upper_bound_usd': 3*sum(reserve(q, s) for q in s['requests'] if q['request_id'] in pilot)}
    assert s['preflight_summary']['all_calls_upper_bound_usd'] < 35
    assert s['preflight_summary']['pilot_upper_bound_usd'] < 7
    s['status'] = 'PREFLIGHT_PASSED'
    save(s)
    print(json.dumps(s['preflight_summary']))


def run(stage):
    s = json.loads(OUT.read_text())
    check(s)
    assert s.get('preflight_summary')
    if s['pending']:
        raise RuntimeError('An interrupted request is reserved; reconcile it before continuing')
    assert not s['uncertain_charge_reserve_usd'], 'Resolve uncertain charges before continuing'
    if stage == 'main':
        assert s.get('pilot_gate', {}).get('passed') is True
    pilot = set(s['protocol']['pilot_request_ids'])
    done = {(r['request_id'], r['repeat']) for r in s['records']}
    todo = [q for q in s['requests'] if stage == 'main' or q['request_id'] in pilot]
    if not s['records']:
        todo.sort(key=lambda q: (s['preflight'][q['request_id']]['input_tokens'] < 512, s['requests'].index(q)))
    s['status'] = 'RUNNING_' + stage.upper()
    save(s)
    for q in todo:
        for repeat in range(3):
            if (q['request_id'], repeat) in done:
                continue
            bound = reserve(q, s)
            ceiling = 7 if stage == 'pilot' else 35
            if s['reported_cost_usd'] + s['uncertain_charge_reserve_usd'] + bound > ceiling:
                s['status'] = 'BUDGET_STOP'
                save(s)
                return
            s['pending'] = {'request_id': q['request_id'], 'repeat': repeat, 'reservation_usd': bound, 'started_at': time.time()}
            save(s)
            response = request('messages', payload(q, True, s['protocol']['max_tokens']))
            elapsed = time.time() - s['pending']['started_at']
            usage = response.get('usage')
            cost = sum(usage.get(k, 0)*v for k, v in RATES.items())/1e6 if usage else None
            if cost is None:
                s['uncertain_charge_reserve_usd'] += bound
            else:
                s['reported_cost_usd'] += cost
            text = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
            row = {'request_id': q['request_id'], 'repeat': repeat, 'stage': stage, 'max_tokens': s['protocol']['max_tokens'], 'prediction': parse(text) if response.get('stop_reason') == 'end_turn' else None, 'response': response, 'reported_cost_usd': cost, 'reservation_usd': bound, 'elapsed_seconds': elapsed}
            s['records'].append(row)
            s['pending'] = None
            save(s)
            print(json.dumps({'completed': len(s['records']), 'stage': stage, 'prediction': row['prediction'], 'stop': response.get('stop_reason'), 'cache_read': (usage or {}).get('cache_read_input_tokens'), 'cache_write': (usage or {}).get('cache_creation_input_tokens'), 'cost_usd': round(s['reported_cost_usd'], 6), 'seconds': round(elapsed, 1)}), flush=True)
            good = response.get('model') == MODEL and response.get('stop_reason') in ['end_turn', 'max_tokens'] and cost is not None and cost <= bound
            if not good:
                s['status'] = 'RESPONSE_AUDIT_STOP'
                save(s)
                return
            if repeat == 1 and len(s['records']) == 2 and s['preflight'][q['request_id']]['input_tokens'] >= 512 and not usage.get('cache_read_input_tokens', 0):
                s['status'] = 'CACHE_AUDIT_STOP'
                save(s)
                return
    if stage == 'pilot':
        records = [r for r in s['records'] if r['request_id'] in pilot]
        passed = len(records) == 3*len(pilot) and all(r['response'].get('stop_reason') in ['end_turn', 'max_tokens'] for r in records)
        passed = passed and any(r['response']['usage'].get('cache_read_input_tokens', 0)>0 for r in records) and any(r['response']['usage'].get('cache_creation_input_tokens', 0)>0 for r in records)
        s['pilot_gate'] = {'passed': passed, 'calls': len(records), 'cost_usd': s['reported_cost_usd'], 'outcome_filter': False}
        s['status'] = 'PILOT_PASSED' if passed else 'PILOT_STOP'
    else:
        s['status'] = 'INFERENCE_COMPLETE'
    save(s)
    print(json.dumps({'status': s['status'], 'cost_usd': s['reported_cost_usd']}), flush=True)


def score():
    import numpy as np
    s = json.loads(OUT.read_text())
    check(s)
    groups = {}
    for r in s['records']:
        text = '\n'.join(b.get('text', '') for b in r['response'].get('content', []) if b.get('type') == 'text')
        assert (parse(text) if r['response'].get('stop_reason') == 'end_turn' else None) == r['prediction']
        groups.setdefault(r['request_id'], []).append(r)
    votes = {}
    for rid, records in groups.items():
        if len(records) != 3:
            continue
        seq = [r['prediction'] for r in sorted(records, key=lambda r: r['repeat']) if r['prediction'] is not None]
        votes[rid] = Counter(seq).most_common(1)[0][0] if seq else None
    cases = [c for c in s['cases'] if all(rid in votes for rid in c['requests'].values())]
    assert cases
    def fraction(values):
        return {'correct': sum(values), 'n': len(values), 'percent': 100*sum(values)/len(values) if values else None}
    metrics = {}
    for arm in ['lattice', 'exact', 'huber', 'split']:
        pred = lambda c: votes[c['requests'][arm]]
        originals = [c for c in cases if c['variant'] == 'original']
        changed = [c for c in cases if c['variant'] == 'large' and c['stable'] and c['label'] != c['original_label']]
        pairs = [(c, next(o for o in originals if o['material_id'] == c['material_id'] and o['condition'] == c['condition'])) for c in changed]
        metrics[arm] = {'all': fraction([pred(c)==c['label'] for c in cases]), 'original': fraction([pred(c)==c['label'] for c in originals]), 'stable_changed': fraction([pred(c)==c['label'] for c in changed]), 'joint': fraction([pred(c)==c['label'] and pred(o)==o['label'] for c, o in pairs]), 'false_restoration': fraction([pred(c)==c['original_label'] for c in changed]), 'conditions': {cond: fraction([pred(c)==c['label'] for c in cases if c['condition']==cond]) for cond in ['gaussian', 'one_view_error']}}
    parent_diffs = [np.mean([int(votes[c['requests']['split']]==c['label'])-int(votes[c['requests']['huber']]==c['label']) for c in cases if c['material_id']==mid]) for mid in sorted({c['material_id'] for c in cases})]
    boot = np.random.default_rng(20261028).choice(parent_diffs, size=(20000, len(parent_diffs)), replace=True).mean(axis=1)*100
    metrics['split_minus_huber'] = {'difference_pp': float(np.mean(parent_diffs)*100), 'descriptive_parent_bootstrap_95': np.quantile(boot, [.025,.975]).tolist(), 'corrected': sum(votes[c['requests']['split']]==c['label'] and votes[c['requests']['huber']]!=c['label'] for c in cases), 'regressed': sum(votes[c['requests']['split']]!=c['label'] and votes[c['requests']['huber']]==c['label'] for c in cases)}
    all_attempts = s['records'] + s.get('prior_attempts', [])
    cost = sum(sum(r['response'].get('usage', {}).get(k, 0)*v for k,v in RATES.items())/1e6 for r in all_attempts)
    assert abs(cost-s['reported_cost_usd']) < 1e-9
    assert cost+s['uncertain_charge_reserve_usd'] <= 35
    usage = {k: sum(r['response'].get('usage', {}).get(k, 0) for r in all_attempts) for k in RATES}
    s['scores'] = {'evaluated_cases': len(cases), 'unique_prompt_votes': len(votes), 'metrics': metrics, 'votes': votes, 'case_predictions': [{**c, 'predictions': {arm: votes[rid] for arm,rid in c['requests'].items()}} for c in cases], 'usage': usage, 'recomputed_cost_usd': cost, 'cache_hit_calls': sum(r['response'].get('usage', {}).get('cache_read_input_tokens', 0)>0 for r in all_attempts), 'total_attempts': len(all_attempts), 'superseded_attempts': len(s.get('prior_attempts', []))}
    save(s)
    print(json.dumps({k:v for k,v in s['scores'].items() if k not in ['votes','case_predictions']}, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['prepare','preflight','pilot','main','score'])
    args = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / 'outputs').mkdir(exist_ok=True)
    lock = (ROOT/'outputs/sonnet_handoff.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    if args.action in ['pilot','main']:
        run(args.action)
    else:
        globals()[args.action]()

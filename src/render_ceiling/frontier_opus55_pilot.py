import os
import concurrent.futures
import signal
import threading
import sys
import base64
import collections
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/geometry_substitution/opus55/pilot/run.json'
from render_ceiling.prompt_cache import with_cache, token_cost
MODEL = 'claude-opus-5-5'
SYSTEMS = ['cubic', 'hexagonal', 'monoclinic', 'orthorhombic', 'tetragonal', 'triclinic', 'trigonal']


def main():
    key = os.environ['CLAUDE_API_KEY']
    if OUT.exists():
        raise RuntimeError('Existing run preserved; refusing automatic rerun')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    state = {'model': MODEL, 'api_version': '2026-10-21', 'status': 'preflight', 'scope': 'Table 1 pilot only; not manuscript results', 'sampling': 'First manifest entry per crystal system, selected before calls', 'K': 3, 'max_tokens': 4096, 'budget_usd': 5.0, 'workers': 5, 'max_active_requests': 0, 'request_events': [], 'pricing_usd_per_million': {'input': 4, 'output': 20, 'cache_write': 5, 'cache_read': 0.2}, 'protocol_deviations': ['Seven structures instead of 210', 'Native Anthropic API instead of archived OpenRouter route', 'Temperature omitted: Opus 5.5 rejects sampling parameters; legacy temperature was 0.7', '4096 output-token cap including default adaptive thinking; stop on truncation'], 'reasoning': 'provider default; no thinking or effort override', 'records': [], 'preflight': [], 'estimated_cost_usd': 0, 'selection': []}

    lock = threading.RLock()
    stopped = threading.Event()
    active = 0
    signal.signal(signal.SIGTERM, lambda *_: stopped.set())
    signal.signal(signal.SIGINT, lambda *_: stopped.set())

    def save():
        temporary = OUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, indent=2) + '\n')
        temporary.replace(OUT)

    def request(path, payload):
        req = urllib.request.Request('https://api.anthropic.com/v1/' + path, data=json.dumps(payload).encode(), headers={'x-api-key': key, 'anthropic-version': state['api_version'], 'content-type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.load(resp)
                result['_transport'] = {'status': resp.status, 'headers': {k.lower(): v for k, v in resp.headers.items() if k.lower().startswith('anthropic-ratelimit-') or k.lower() in ['request-id', 'retry-after']}}
                return result
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors='replace').replace(key, '[REDACTED]')
            return {'error': {'http_status': e.code, 'detail': detail[:1500], 'retry_after': e.headers.get('retry-after')}}
        except Exception as e:
            return {'error': {'type': type(e).__name__, 'detail': 'Request did not complete; no automatic retry'}}

    rows = [json.loads(l) for l in (ROOT / 'data/primary/eval.jsonl').read_text().splitlines()]
    texts = {r['material_id']: r for r in map(json.loads, (ROOT / 'release/eval_coords_as_text.jsonl').read_text().splitlines())}
    selected = {}
    for row in rows:
        selected.setdefault(row['crystal_system'], row)
    assert len(selected) == 7
    jobs = []
    for truth, row in selected.items():
        mid = row['material_id']
        assert texts[mid]['crystal_system'] == truth
        state['selection'].append({'material_id': mid, 'truth': truth})
        for arm in ['image', 'text']:
            question = row['question'] if arm == 'image' else texts[mid]['question']
            content = [{'type': 'text', 'text': question}]
            hashes = []
            if arm == 'image':
                assert len(row['images']) == 5
                for rel in row['images']:
                    raw = (ROOT / rel).read_bytes()
                    assert raw.startswith(b'\x89PNG\r\n\x1a\n')
                    hashes.append({'path': rel, 'sha256': hashlib.sha256(raw).hexdigest()})
                    content.append({'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/png', 'data': base64.b64encode(raw).decode()}})
            payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': content}]}
            counted = request('messages/count_tokens', payload)
            meta = {'material_id': mid, 'arm': arm, 'truth': truth, 'question_sha256': hashlib.sha256(question.encode()).hexdigest(), 'images': hashes, 'count_response': counted}
            state['preflight'].append(meta)
            if 'input_tokens' not in counted:
                state['status'] = 'stopped_preflight_error';save();print(json.dumps({'status': state['status'], 'error': counted}), flush=True);return
            jobs.append((meta, dict(payload, max_tokens=4096)))
    bound = sum(m['count_response']['input_tokens'] * 5e-6 + 4096 * 20e-6 for m, p in jobs) * 3
    state['preflight_worst_case_usd'] = bound
    save()
    print(json.dumps({'preflight_calls': len(jobs), 'maximum_generation_calls': len(jobs)*3, 'estimated_upper_bound_usd': bound}), flush=True)
    if bound > 5:
        state['status'] = 'stopped_budget_preflight';save();return
    state['started_at'] = time.time()
    state['status'] = 'running';save()

    def group(job):
        nonlocal active
        meta, plain_payload = job
        payload, cached = with_cache(plain_payload, meta['count_response']['input_tokens'], 3)
        for repeat in range(3):
            if stopped.is_set():
                return
            started = time.time()
            with lock:
                active += 1
                state['max_active_requests'] = max(active, state['max_active_requests'])
                state['request_events'].append({'time': started, 'delta': 1, 'material_id': meta['material_id'], 'arm': meta['arm'], 'repeat': repeat})
            response = request('messages', payload)
            ended = time.time()
            text = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
            hits = [(text.lower().rfind(s), s) for s in SYSTEMS if s in text.lower()]
            pred = max(hits)[1] if hits else None
            cost = token_cost(MODEL, response.get('usage', {}))
            record = {'material_id': meta['material_id'], 'arm': meta['arm'], 'repeat': repeat, 'prediction': pred, 'started_at': started, 'ended_at': ended, 'elapsed_seconds': ended-started, 'cache_enabled': cached, 'estimated_cost_usd': cost, 'response': response}
            with lock:
                active -= 1
                state['request_events'].append({'time': ended, 'delta': -1, 'material_id': meta['material_id'], 'arm': meta['arm'], 'repeat': repeat})
                state['estimated_cost_usd'] += cost
                state['records'].append(record)
                if 'error' in response or response.get('stop_reason') != 'end_turn' or pred is None:
                    stopped.set()
                save()
                print(json.dumps({'completed': len(state['records']), 'arm': meta['arm'], 'material_id': meta['material_id'], 'stop_reason': response.get('stop_reason'), 'cache_read_tokens': response.get('usage', {}).get('cache_read_input_tokens', 0), 'estimated_cost_usd': round(state['estimated_cost_usd'], 6), 'error': response.get('error')}), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(group, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    state['finished_at'] = time.time()
    state['status'] = 'completed' if len(state['records']) == 42 and not stopped.is_set() else 'stopped_response_issue_or_signal'
    save()


if __name__ == '__main__':
    main()

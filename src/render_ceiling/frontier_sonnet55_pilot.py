import os
import base64
import collections
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/geometry_substitution/sonnet55/pilot/run.json'
MODEL = 'claude-sonnet-5-5'
SYSTEMS = ['cubic', 'hexagonal', 'monoclinic', 'orthorhombic', 'tetragonal', 'triclinic', 'trigonal']


def main():
    key = os.environ['CLAUDE_API_KEY']
    if OUT.exists():
        raise RuntimeError('Existing run preserved; refusing automatic rerun')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    state = {'model': MODEL, 'api_version': '2026-10-21', 'status': 'preflight', 'scope': 'Table 1 pilot only; not manuscript results', 'sampling': 'First manifest entry per crystal system, selected before calls', 'K': 3, 'max_tokens': 4096, 'budget_usd': 3.0, 'pricing_usd_per_million': {'input': 2, 'output': 10}, 'protocol_deviations': ['Seven structures instead of 210', 'Native Anthropic API instead of archived OpenRouter route', 'Temperature omitted: Sonnet 5.5 rejects sampling parameters; legacy temperature was 0.7', '4096 output-token cap including default adaptive thinking; stop on truncation'], 'reasoning': 'provider default; no thinking or effort override', 'records': [], 'preflight': [], 'estimated_cost_usd': 0, 'selection': []}

    def save():
        OUT.write_text(json.dumps(state, indent=2) + '\n')

    def request(path, payload):
        req = urllib.request.Request('https://api.anthropic.com/v1/' + path, data=json.dumps(payload).encode(), headers={'x-api-key': key, 'anthropic-version': state['api_version'], 'content-type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors='replace').replace(key, '[REDACTED]')
            return {'error': {'http_status': e.code, 'detail': detail[:1500]}}
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
    bound = sum(m['count_response']['input_tokens'] * 2e-6 + 4096 * 10e-6 for m, p in jobs) * 3
    state['preflight_worst_case_usd'] = bound
    save()
    print(json.dumps({'preflight_calls': len(jobs), 'maximum_generation_calls': len(jobs)*3, 'estimated_upper_bound_usd': bound}), flush=True)
    if bound > 3:
        state['status'] = 'stopped_budget_preflight';save();return
    state['status'] = 'running';save()
    for meta, payload in jobs:
        for repeat in range(3):
            reserve = meta['count_response']['input_tokens']*2e-6 + 4096*10e-6
            if state['estimated_cost_usd'] + reserve > 3:
                state['status'] = 'stopped_budget';save();return
            started = time.time();response = request('messages', payload)
            text = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
            hits = [(text.lower().rfind(s), s) for s in SYSTEMS if s in text.lower()]
            pred = max(hits)[1] if hits else None
            usage = response.get('usage', {})
            cost = usage.get('input_tokens', 0)*2e-6 + usage.get('output_tokens', 0)*10e-6 + usage.get('cache_read_input_tokens', 0)*0.1e-6 + usage.get('cache_creation_input_tokens', 0)*2.5e-6
            state['estimated_cost_usd'] += cost
            record = {'material_id': meta['material_id'], 'arm': meta['arm'], 'repeat': repeat, 'prediction': pred, 'elapsed_seconds': round(time.time()-started, 3), 'estimated_cost_usd': cost, 'response': response}
            state['records'].append(record);save()
            print(json.dumps({'completed': len(state['records']), 'arm': meta['arm'], 'material_id': meta['material_id'], 'prediction': pred, 'stop_reason': response.get('stop_reason'), 'estimated_cost_usd': round(state['estimated_cost_usd'], 6), 'error': response.get('error')}), flush=True)
            if 'error' in response or response.get('stop_reason') != 'end_turn' or pred is None:
                state['status'] = 'stopped_response_issue';save();return
    state['status'] = 'completed';save()


if __name__ == '__main__':
    main()

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import signal
from render_ceiling.prompt_cache import with_cache, token_cost
from pathlib import Path
import threading
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/geometry_substitution/sonnet55/full/run.json'
PILOT = ROOT / 'results/geometry_substitution/sonnet55/pilot/run.json'
MODEL = 'claude-sonnet-5-5'
SYSTEMS = ['cubic', 'hexagonal', 'monoclinic', 'orthorhombic', 'tetragonal', 'triclinic', 'trigonal']
LOCK = threading.Lock()
STOP = threading.Event()
signal.signal(signal.SIGTERM, lambda signum, frame: STOP.set())
signal.signal(signal.SIGINT, lambda signum, frame: STOP.set())


def main():
    key = os.environ['CLAUDE_API_KEY']
    rows = list(map(json.loads, (ROOT/'data/primary/eval.jsonl').read_text().splitlines()))
    texts = {r['material_id']: r for r in map(json.loads, (ROOT/'release/eval_coords_as_text.jsonl').read_text().splitlines())}
    assert len(rows) == len({r['material_id'] for r in rows}) == len(texts) == 210
    pilot = json.loads(PILOT.read_text())
    assert pilot['status'] == 'completed' and len(pilot['records']) == 42
    OUT.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(OUT.read_text()) if OUT.exists() else {'model': MODEL, 'api_version': '2026-10-21', 'status': 'preflight', 'scope': 'Full 210-structure Table 1 follow-up; paired image/exact-geometry evaluation', 'K': 3, 'max_tokens': 4096, 'budget_usd': 25.0, 'pricing_usd_per_million': {'input': 2, 'output': 10}, 'reasoning': 'provider default; no thinking or effort override', 'protocol_deviations': [x for x in pilot['protocol_deviations'] if not x.startswith('Seven')], 'pilot_reuse': {'path': str(PILOT.relative_to(ROOT)), 'sha256': hashlib.sha256(PILOT.read_bytes()).hexdigest(), 'requests': 42}, 'records': pilot['records'], 'preflight': pilot['preflight'], 'selection': [{'material_id': r['material_id'], 'truth': r['crystal_system']} for r in rows], 'estimated_cost_usd': pilot['estimated_cost_usd']}
    state['caching'] = {'policy': 'Explicit final-block breakpoint, five-minute TTL, minimum 512 tokens; skip inputs with fewer than two remaining repeats', 'scheduling': 'Repeats sequential within each input; independent inputs concurrent', 'activated_after_records': state.get('cache_migration',{}).get('completed_records_preserved',len(state['records'])), 'source': 'https://platform.claude.com/docs/en/build-with-claude/prompt-caching'}
    unknown_reserve = state.get('cache_migration',{}).get('unreported_charge_reserve_usd',0)
    assert state['model'] == MODEL and state['K'] == 3 and state['max_tokens'] == 4096
    state['protocol_deviations'] = [x.replace('; stop on truncation', '; truncated responses retained and flagged') for x in state['protocol_deviations']]

    def save():
        tmp = OUT.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, indent=2)+'\n')
        os.replace(tmp, OUT)

    def request(path, payload):
        req = urllib.request.Request('https://api.anthropic.com/v1/'+path, data=json.dumps(payload).encode(), headers={'x-api-key': key, 'anthropic-version': '2026-10-21', 'content-type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            return {'error': {'http_status': e.code, 'detail': e.read().decode(errors='replace').replace(key, '[REDACTED]')[:1500]}}
        except Exception as e:
            return {'error': {'type': type(e).__name__, 'detail': 'Request did not complete; no timeout retry'}}

    def payload_for(row, arm):
        question = row['question'] if arm == 'image' else texts[row['material_id']]['question']
        content = [{'type': 'text', 'text': question}]
        hashes = []
        if arm == 'image':
            assert len(row['images']) == 5
            for rel in row['images']:
                raw = (ROOT/rel).read_bytes();assert raw.startswith(b'\x89PNG\r\n\x1a\n')
                hashes.append({'path': rel, 'sha256': hashlib.sha256(raw).hexdigest()})
                content.append({'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/png', 'data': base64.b64encode(raw).decode()}})
        return {'model': MODEL, 'messages': [{'role': 'user', 'content': content}]}, {'material_id': row['material_id'], 'arm': arm, 'truth': row['crystal_system'], 'question_sha256': hashlib.sha256(question.encode()).hexdigest(), 'images': hashes}

    pre = {(r['material_id'],r['arm']):r for r in state['preflight']}
    todo = []
    for row in rows:
        assert texts[row['material_id']]['crystal_system'] == row['crystal_system']
        for arm in ['image','text']:
            if (row['material_id'],arm) not in pre:todo.append((row,arm))
            else:
                payload, meta = payload_for(row,arm)
                assert all(pre[row['material_id'],arm][k] == meta[k] for k in meta)

    def count(job):
        row,arm = job;payload,meta = payload_for(row,arm)
        counted = request('messages/count_tokens',payload)
        meta['count_response'] = counted
        return meta

    state['status'] = 'preflight';save()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for future in as_completed([pool.submit(count,j) for j in todo]):
            meta = future.result();state['preflight'].append(meta);save()
            if len(state['preflight'])%50 == 0:print(json.dumps({'preflight':len(state['preflight']),'of':420}),flush=True)
    if any('input_tokens' not in r['count_response'] for r in state['preflight']):
        state['status'] = 'stopped_preflight_error';save();print(state['status'],flush=True);return
    pre = {(r['material_id'],r['arm']):r for r in state['preflight']}
    done = {(r['material_id'],r['arm'],r['repeat']) for r in state['records']}
    assert len(done) == len(state['records'])
    jobs = [(row,arm,repeat) for row in rows for arm in ['image','text'] for repeat in range(3) if (row['material_id'],arm,repeat) not in done]
    state['preflight_full_max_cost_usd'] = sum(r['count_response']['input_tokens']*2e-6+4096*10e-6 for r in state['preflight'])*3
    state['status'] = 'running';save()
    print(json.dumps({'remaining_requests':len(jobs),'reused_requests':len(done),'full_max_cost_at_token_cap':state['preflight_full_max_cost_usd'],'spend_guard_usd':25}),flush=True)
    reserved = [0.0]

    def generate(job, cache_enabled=False):
        if STOP.is_set():return None
        row,arm,repeat = job;meta = pre[row['material_id'],arm]
        reserve = meta['count_response']['input_tokens']*(2.5e-6 if cache_enabled else 2e-6)+4096*10e-6
        with LOCK:
            if state['estimated_cost_usd']+unknown_reserve+reserved[0]+reserve>state['budget_usd']:return None
            reserved[0]+=reserve
        payload,_ = payload_for(row,arm);payload['max_tokens']=4096
        if cache_enabled:payload,_ = with_cache(payload,meta['count_response']['input_tokens'],2)
        started=time.time();attempts=[]
        for attempt in range(3):
            response=request('messages',payload);attempts.append(response)
            code=response.get('error',{}).get('http_status')
            if code not in [429,500,502,503,529] or attempt==2:break
            time.sleep(3*(attempt+1))
        text='\n'.join(b.get('text','') for b in response.get('content',[]) if b.get('type')=='text')
        hits=[(text.lower().rfind(s),s) for s in SYSTEMS if s in text.lower()]
        pred=max(hits)[1] if hits else None
        cost=0
        for resp in attempts:
            cost+=token_cost(MODEL,resp.get('usage',{}))
        record={'material_id':row['material_id'],'arm':arm,'repeat':repeat,'prediction':pred,'elapsed_seconds':round(time.time()-started,3),'estimated_cost_usd':cost,'response':response,'previous_attempts':attempts[:-1],'cache_requested':cache_enabled}
        with LOCK:
            reserved[0]-=reserve;state['estimated_cost_usd']+=cost;state['records'].append(record);save()
            n=len(state['records'])
            if n%12==0 or 'error' in response or response.get('stop_reason')!='end_turn':
                print(json.dumps({'completed':n,'of':1260,'estimated_cost_usd':round(state['estimated_cost_usd'],5),'last_stop_reason':response.get('stop_reason'),'last_error':response.get('error')}),flush=True)
        return record

    grouped = {}
    for job in jobs:grouped.setdefault((job[0]['material_id'],job[1]),[]).append(job)

    def run_group(group):
        meta=pre[group[0][0]['material_id'],group[0][1]]
        enabled=meta['count_response']['input_tokens']>=512 and len(group)>=2
        for job in group:
            if STOP.is_set():break
            generate(job,enabled)

    with ThreadPoolExecutor(max_workers=8) as pool:
        for result in pool.map(run_group,grouped.values()):pass
    state['records'].sort(key=lambda r: (next(i for i,x in enumerate(rows) if x['material_id']==r['material_id']),r['arm'],r['repeat']))
    state['status']='completed' if len(state['records'])==1260 else ('stopped_by_signal' if STOP.is_set() else 'stopped_budget')
    state['summary_counts']={'api_errors':sum('error' in r['response'] for r in state['records']),'non_end_turn':sum(r['response'].get('stop_reason')!='end_turn' for r in state['records']),'unparsed':sum(r['prediction'] is None for r in state['records'])}
    save();print(json.dumps({'status':state['status'],'records':len(state['records']),'cost':state['estimated_cost_usd'],'counts':state['summary_counts']}),flush=True)


if __name__ == '__main__':
    main()

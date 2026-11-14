import os
import base64
import json
from pathlib import Path
import sys
import time
import urllib.request

root = Path(__file__).resolve().parents[2]
from render_ceiling.prompt_cache import token_cost
p = root / 'results/geometry_substitution/fable51/pilot/run.json'
d = json.loads(p.read_text())
assert d['status'] == 'stopped_response_issue_or_signal'
key = os.environ['CLAUDE_API_KEY']
rows = {r['material_id']: r for r in map(json.loads, (root / 'data/primary/eval.jsonl').read_text().splitlines())}
texts = {r['material_id']: r for r in map(json.loads, (root / 'release/eval_coords_as_text.jsonl').read_text().splitlines())}
pre = {(r['material_id'], r['arm']): r for r in d['preflight']}
records = {(r['material_id'], r['arm'], r['repeat']): r for r in d['records']}
labels = ['cubic','hexagonal','monoclinic','orthorhombic','tetragonal','triclinic','trigonal']
for c in d['selection']:
    for arm in ['image','text']:
        for repeat in range(3):
            slot = c['material_id'],arm,repeat
            old = records.get(slot)
            if old and old['response'].get('stop_reason') == 'end_turn':continue
            assert not old or old['response'].get('stop_reason') == 'max_tokens'
            cap = 16384 if old else 4096
            mid = c['material_id']
            source = rows[mid] if arm == 'image' else texts[mid]
            content = [{'type':'text','text':source['question']}]
            if arm == 'image':
                for rel in source['images']:
                    content.append({'type':'image','source':{'type':'base64','media_type':'image/png','data':base64.b64encode((root/rel).read_bytes()).decode()}})
            bound = (pre[mid,arm]['count_response']['input_tokens']*1.02+128)*12.5e-6+cap*50e-6
            assert d['estimated_cost_usd']+bound < 10
            payload = {'model':'claude-fable-5-1','max_tokens':cap,'messages':[{'role':'user','content':content}]}
            request = urllib.request.Request('https://api.anthropic.com/v1/messages', data=json.dumps(payload).encode(),headers={'x-api-key':key,'anthropic-version':'2026-10-21','content-type':'application/json'})
            start=time.time()
            d['inflight_reserve_usd']=bound
            p.write_text(json.dumps(d,indent=2)+'\n')
            with urllib.request.urlopen(request,timeout=240) as resp:response=json.load(resp)
            end=time.time()
            answer='\n'.join(b.get('text','') for b in response.get('content',[]) if b['type']=='text')
            hits=[(answer.lower().rfind(s),s) for s in labels if s in answer.lower()]
            cost=token_cost('claude-fable-5-1',response['usage'])
            record={'material_id':mid,'arm':arm,'repeat':repeat,'prediction':max(hits)[1] if hits else None,'started_at':start,'ended_at':end,'elapsed_seconds':end-start,'cache_enabled':False,'estimated_cost_usd':cost,'response':response,'final_max_tokens':cap}
            if old:
                record['previous_attempts']=old.get('previous_attempts',[])+[old['response']]
                record['estimated_cost_usd']+=old['estimated_cost_usd']
                record['repair_reason']='original response reached max_tokens'
                d['records'][d['records'].index(old)]=record
            else:d['records'].append(record)
            d['request_events'] += [{'time':start,'delta':1,'material_id':mid,'arm':arm,'repeat':repeat},{'time':end,'delta':-1,'material_id':mid,'arm':arm,'repeat':repeat}]
            d['estimated_cost_usd']+=cost
            d['inflight_reserve_usd']=0
            p.write_text(json.dumps(d,indent=2)+'\n')
            print(json.dumps({'slot':slot,'cap':cap,'stop_reason':response.get('stop_reason'),'cost':d['estimated_cost_usd']}),flush=True)
            assert response.get('stop_reason')=='end_turn' and record['prediction']
assert len(d['records'])==42
assert all(r['response'].get('stop_reason')=='end_turn' for r in d['records'])
d['status']='completed'
d['protocol_deviations'].append('One truncated pilot response replaced at 16384 tokens; original retained and cost included')
p.write_text(json.dumps(d,indent=2)+'\n')

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import urllib.error
import urllib.request
from render_ceiling.prompt_cache import token_cost

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'results/geometry_substitution/sonnet55/full/run.json'
LOCK=threading.Lock()


def main():
    d=json.loads(P.read_text());assert d['status']=='completed'
    if 'truncation_repair' in d:raise RuntimeError('Repair already recorded; no automatic repeated repair')
    jobs=[i for i,r in enumerate(d['records']) if r['response'].get('stop_reason')=='max_tokens']
    key = os.environ['CLAUDE_API_KEY']
    rows={r['material_id']:r for r in map(json.loads,(ROOT/'data/primary/eval.jsonl').read_text().splitlines())}
    texts={r['material_id']:r for r in map(json.loads,(ROOT/'release/eval_coords_as_text.jsonl').read_text().splitlines())}
    pre={(x['material_id'],x['arm']):x for x in d['preflight']}
    d['truncation_repair']={'rule':'One replacement generation only for max_tokens responses, independent of labels or correctness; original responses retained in previous_attempts','original_run_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'initial_truncations':len(jobs),'fallback_max_tokens':16384,'attempted':0,'input_cache':'Disabled for isolated repair calls: no planned repeated input','status':'running'}
    d['protocol_deviations'].append('Responses truncated at 4096 tokens receive one replacement attempt at 16384 tokens; original attempts retained and billed usage included')
    reserved=[0.0]

    def save():
        tmp=P.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');os.replace(tmp,P)

    save()

    def work(index):
        r=d['records'][index];mid=r['material_id'];arm=r['arm'];meta=pre[mid,arm]
        bound=meta['count_response']['input_tokens']*2e-6+16384*10e-6
        with LOCK:
            if d['estimated_cost_usd']+reserved[0]+bound+d.get('cache_migration',{}).get('unreported_charge_reserve_usd',0)>d['budget_usd']:return None
            reserved[0]+=bound
        source=rows[mid] if arm=='image' else texts[mid]
        content=[{'type':'text','text':source['question']}]
        if arm=='image':
            for rel in source['images']:
                content.append({'type':'image','source':{'type':'base64','media_type':'image/png','data':base64.b64encode((ROOT/rel).read_bytes()).decode()}})
        payload={'model':'claude-sonnet-5-5','max_tokens':16384,'messages':[{'role':'user','content':content}]}
        req=urllib.request.Request('https://api.anthropic.com/v1/messages',data=json.dumps(payload).encode(),headers={'x-api-key':key,'anthropic-version':'2026-10-21','content-type':'application/json'})
        started=time.time()
        try:
            with urllib.request.urlopen(req,timeout=180) as resp:response=json.load(resp)
        except urllib.error.HTTPError as e:
            response={'error':{'http_status':e.code,'detail':e.read().decode(errors='replace').replace(key,'[REDACTED]')[:1000]}}
        except Exception as e:response={'error':{'type':type(e).__name__,'detail':'No automatic timeout retry'}}
        text='\n'.join(x.get('text','') for x in response.get('content',[]) if x.get('type')=='text');labels=['cubic','hexagonal','monoclinic','orthorhombic','tetragonal','triclinic','trigonal'];hits=[(text.lower().rfind(s),s) for s in labels if s in text.lower()]
        extra=token_cost('claude-sonnet-5-5',response.get('usage',{}))
        with LOCK:
            r.setdefault('previous_attempts',[]).append(r['response']);r['response']=response;r['prediction']=max(hits)[1] if hits else None;r['estimated_cost_usd']+=extra;r['elapsed_seconds']+=round(time.time()-started,3);r['final_max_tokens']=16384;r['repair_reason']='original response reached max_tokens';r['cache_requested']=False
            d['estimated_cost_usd']+=extra;reserved[0]-=bound;d['truncation_repair']['attempted']+=1;save()
            print(json.dumps({'repaired_attempts':d['truncation_repair']['attempted'],'of':len(jobs),'stop_reason':response.get('stop_reason'),'cost':round(d['estimated_cost_usd'],5)}),flush=True)
        return index

    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(work,jobs):pass
    d['truncation_repair']['status']='completed' if d['truncation_repair']['attempted']==len(jobs) else 'budget_limited'
    d['summary_counts']={'api_errors':sum('error' in r['response'] for r in d['records']),'non_end_turn':sum(r['response'].get('stop_reason')!='end_turn' for r in d['records']),'unparsed':sum(r['prediction'] is None for r in d['records'])};save()


if __name__=='__main__':
    main()

import collections
import hashlib
import json
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'results/geometry_substitution/opus55/full'
d=json.loads((FOLDER/'run.json').read_text())
assert d['status']=='completed' and len(d['records'])==1260
manifest=list(map(json.loads,(ROOT/'data/primary/eval.jsonl').read_text().splitlines()))
coords={r['material_id']:r for r in map(json.loads,(ROOT/'release/eval_coords_as_text.jsonl').read_text().splitlines())}
from render_ceiling.frontier_parser import parse_system as parser
assert len({(r['material_id'],r['arm'],r['repeat']) for r in d['records']})==1260
assert collections.Counter(r['crystal_system'] for r in manifest)=={s:30 for s in ['triclinic','monoclinic','orthorhombic','tetragonal','trigonal','hexagonal','cubic']}
pre={(r['material_id'],r['arm']):r for r in d['preflight']}
for row in manifest:
    for arm in ['image','text']:
        meta=pre[row['material_id'],arm]
        q=row['question'] if arm=='image' else coords[row['material_id']]['question']
        assert meta['question_sha256']==hashlib.sha256(q.encode()).hexdigest()
        assert row['crystal_system']==meta['truth']==coords[row['material_id']]['crystal_system']
        if arm=='image':
            assert len(meta['images'])==5 and [x['path'] for x in meta['images']]==row['images']
            for im in meta['images']:assert hashlib.sha256((ROOT/im['path']).read_bytes()).hexdigest()==im['sha256']
pilot=json.loads((ROOT/'results/geometry_substitution/opus55/pilot/run.json').read_text())
bykey={(r['material_id'],r['arm'],r['repeat']):r for r in d['records']}
for r in pilot['records']:assert bykey[r['material_id'],r['arm'],r['repeat']]==r
cases=[]
for row in manifest:
    case={'material_id':row['material_id'],'truth':row['crystal_system']}
    for arm in ['image','text']:
        samples=[bykey[row['material_id'],arm,k] for k in range(3)]
        votes=[]
        failures=[]
        for r in samples:
            resp=r['response'];text='\n'.join(x.get('text','') for x in resp.get('content',[]) if x.get('type')=='text');pred=parser(text)
            assert pred==r['prediction']
            valid=resp.get('stop_reason')=='end_turn' and pred is not None and 'error' not in resp
            if valid:
                assert resp['model']=='claude-opus-5-5';votes.append(pred)
            else:failures.append({'repeat':r['repeat'],'stop_reason':resp.get('stop_reason'),'parse_failed':pred is None,'api_error':'error' in resp})
        count=collections.Counter(votes);rank=count.most_common();pred=rank[0][0] if rank else None
        case[arm]={'pred':pred,'votes':dict(count),'valid_votes':len(votes),'failures':failures,'tie':len(rank)>1 and rank[0][1]==rank[1][1],'correct':pred==row['crystal_system']}
    cases.append(case)
n=len(cases);image=sum(c['image']['correct'] for c in cases);text=sum(c['text']['correct'] for c in cases)
both=sum(c['image']['correct'] and c['text']['correct'] for c in cases);corrected=sum(not c['image']['correct'] and c['text']['correct'] for c in cases);wrong=sum(c['image']['correct'] and not c['text']['correct'] for c in cases);neither=sum(not c['image']['correct'] and not c['text']['correct'] for c in cases)
assert image==both+wrong and text==both+corrected and both+wrong+corrected+neither==n and text-image==corrected-wrong
usage=collections.Counter()
for r in d['records']:
    for resp in r.get('previous_attempts',[])+[r['response']]:
        u=resp.get('usage',{})
        for k in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']:usage[k]+=u.get(k,0)
cost=usage['input_tokens']*4e-6+usage['output_tokens']*20e-6+usage['cache_read_input_tokens']*.2e-6+usage['cache_creation_input_tokens']*5e-6
assert abs(cost-d['estimated_cost_usd'])<1e-7
summary={'model':d['model'],'n':n,'K':3,'run_sha256':hashlib.sha256((FOLDER/'run.json').read_bytes()).hexdigest(),'image_correct':image,'image_accuracy_percent':100*image/n,'text_correct':text,'text_accuracy_percent':100*text/n,'both_correct':both,'corrected':corrected,'newly_wrong':wrong,'both_wrong':neither,'net_gain_percentage_points':100*(text-image)/n,'closed_deficit_percent':100*(text-image)/(n-image) if image<n else None,'calls':len(d['records']),'new_calls':len(d['records'])-42,'pilot_reused':42,'usage':dict(usage),'estimated_cost_usd':cost,'additional_cost_usd':cost-pilot['estimated_cost_usd'],'api_errors':sum('error' in r['response'] for r in d['records']),'truncations':sum(r['response'].get('stop_reason')=='max_tokens' for r in d['records']),'unparseable_responses':sum(r['prediction'] is None for r in d['records']),'tie_rule':'Archived rule: first encountered among equally frequent valid labels, ordered by repeat index','ties':{a:sum(c[a]['tie'] for c in cases) for a in ['image','text']},'invalid_votes':{a:sum(len(c[a]['failures']) for c in cases) for a in ['image','text']},'no_valid_vote_cases':{a:sum(c[a]['valid_votes']==0 for c in cases) for a in ['image','text']},'protocol_deviations':d['protocol_deviations'],'per_class':{s:{'n':30,**{a:sum(c[a]['correct'] for c in cases if c['truth']==s) for a in ['image','text']}} for s in ['triclinic','monoclinic','orthorhombic','tetragonal','trigonal','hexagonal','cubic']},'cases':cases,'manuscript_modified':False}
summary['generation_attempts_with_responses']=sum(1+len(r.get('previous_attempts',[])) for r in d['records'])
summary['cache_migration']=d.get('cache_migration')
summary['truncation_repair']=d.get('truncation_repair')
summary['cache_hits']=sum(resp.get('usage',{}).get('cache_read_input_tokens',0)>0 for r in d['records'] for resp in r.get('previous_attempts',[])+[r['response']])
summary['net_cache_savings_usd']=usage['cache_read_input_tokens']*3.8e-6-usage['cache_creation_input_tokens']*1e-6
summary['all_three_valid_cases']={a:sum(c[a]['valid_votes']==3 for c in cases) for a in ['image','text']}
(FOLDER/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for arm in ['image','text']:
    result={'model':d['model'],'arm':arm,'K':3,'n':210,'micro':sum(c[arm]['correct'] for c in cases)/210,'temperature':'provider default; temperature parameter unsupported','max_tokens':{'initial':4096,'fallback':d.get('truncation_repair',{}).get('fallback_max_tokens')},'predictions':[{'material_id':c['material_id'],'truth':c['truth'],'pred':c[arm]['pred'],'votes':c[arm]['votes']} for c in cases]}
    (FOLDER/f'{arm}_predictions.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='cases'},indent=2))

from pathlib import Path
import collections
import json
import hashlib

root = Path(__file__).resolve().parents[2]
p = root / 'results/geometry_substitution/fable51/pilot/run.json'
d = json.loads(p.read_text())
assert d['status'] != 'running'
labels = ['cubic', 'hexagonal', 'monoclinic', 'orthorhombic', 'tetragonal', 'triclinic', 'trigonal']
rows = []
for case in d['selection']:
    row = dict(case)
    for arm in ['image', 'text']:
        records = [r for r in d['records'] if r['material_id'] == case['material_id'] and r['arm'] == arm]
        records.sort(key=lambda r: r['repeat'])
        votes = []
        for r in records:
            response = r['response']
            text = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
            hits = [(text.lower().rfind(s), s) for s in labels if s in text.lower()]
            parsed = max(hits)[1] if hits else None
            assert parsed == r['prediction']
            if parsed and response.get('stop_reason') == 'end_turn':votes.append(parsed)
        complete = len(votes) == 3
        counts = collections.Counter(votes)
        prediction = counts.most_common(1)[0][0] if complete else None
        row[arm] = {'complete': complete, 'prediction': prediction, 'votes': dict(counts), 'correct': prediction == case['truth'] if complete else None, 'tie': complete and max(counts.values()) == 1}
    rows.append(row)
complete = all(r[a]['complete'] for r in rows for a in ['image','text'])
metrics = None
if complete:
    image = sum(r['image']['correct'] for r in rows);text = sum(r['text']['correct'] for r in rows)
    corrected = sum(not r['image']['correct'] and r['text']['correct'] for r in rows)
    newly = sum(r['image']['correct'] and not r['text']['correct'] for r in rows)
    both = sum(r['image']['correct'] and r['text']['correct'] for r in rows)
    neither = sum(not r['image']['correct'] and not r['text']['correct'] for r in rows)
    assert text-image == corrected-newly and both+neither+corrected+newly == len(rows)
    metrics = {'n':len(rows),'image_correct':image,'text_correct':text,'corrected':corrected,'newly_wrong':newly,'both_correct':both,'both_wrong':neither,'closed_deficit_percent':100*(text-image)/(len(rows)-image) if image<len(rows) else None}
usage = {k:sum(resp.get('usage',{}).get(k,0) for r in d['records'] for resp in r.get('previous_attempts',[])+[r['response']]) for k in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']}
cost = usage['input_tokens']*10e-6+usage['output_tokens']*50e-6+usage['cache_read_input_tokens']*.25e-6+usage['cache_creation_input_tokens']*12.5e-6
assert abs(cost-d['estimated_cost_usd'])<1e-9
summary = {'run_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':d['status'],'calls':len(d['records']),'usage':usage,'estimated_cost_usd':cost,'metrics':metrics,'cases':rows,'verification':'Reparsed all response text; recomputed voting, paired counts, and token cost independently','protocol_deviations':d['protocol_deviations'],'pricing_source':'https://platform.claude.com/docs/en/models/fable-5-1/overview','not_for_manuscript':True}
(root/'results/geometry_substitution/fable51/pilot/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['cases','protocol_deviations']},indent=2))

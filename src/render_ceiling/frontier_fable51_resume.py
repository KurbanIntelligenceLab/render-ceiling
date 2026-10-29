import collections
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
p = root / 'results/geometry_substitution/fable51/full/run.json'
for recovery in range(8):
    d = json.loads(p.read_text())
    assert not d['inflight']
    failures = [r for r in d['records'] if 'error' in r['response']]
    if failures:
        counts = collections.Counter((r['material_id'], r['arm'], r['repeat']) for r in d.get('failed_records_before_resume', []))
        if any(counts[r['material_id'], r['arm'], r['repeat']] >= 2 for r in failures):
            print('Stopped: transport retry limit reached.', flush=True)
            break
        if d['estimated_cost_usd'] + d['unknown_charge_reserve_usd'] >= d['budget_usd']:
            print('Stopped: budget reached.', flush=True)
            break
        d.setdefault('failed_records_before_resume', []).extend(failures)
        d['records'] = [r for r in d['records'] if 'error' not in r['response']]
        d.setdefault('recovery_notes', []).append(f'Bounded transport recovery: retain {len(failures)} error records and uncertain-charge reservations; retry missing slots only. Maximum two transport retries per slot.')
        p.write_text(json.dumps(d, indent=2)+'\n')
        print(json.dumps({'transport_recovery': recovery+1, 'retry_slots':len(failures), 'preserved_records':len(d['records']), 'known_cost':d['estimated_cost_usd'], 'unknown_reserve':d['unknown_charge_reserve_usd']}), flush=True)
    elif d['status'] in ['completed', 'stopped_budget']:
        break
    elif d['status']=='completed_with_response_issues' and not any(r['response'].get('stop_reason')=='max_tokens' and r.get('final_max_tokens',4096)<32768 for r in d['records']):
        break
    completed = subprocess.run([sys.executable, str(Path(__file__).with_name('frontier_fable51_run.py'))])
    if completed.returncode:
        print('Stopped: runner returned an error; inspect before resuming.', flush=True)
        break

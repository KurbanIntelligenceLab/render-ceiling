from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import numpy as np

from render_ceiling import coordinate_handoff_extension as E


def raw_votes(state):
    groups = {}
    for r in state['records']:
        response = r['response']
        text = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
        hits = re.findall(r'ANSWER:\s*([A-Za-z]+)', text, re.I)
        hits = [p.lower() for p in hits if p.lower() in E.S.CLASSES]
        clean = text.strip().lower().strip('.*` \n')
        parsed = hits[0] if len(hits) == 1 else clean if clean in E.S.CLASSES else None
        if response.get('stop_reason') != 'end_turn':
            parsed = None
        assert parsed == r['prediction']
        assert r['repeat'] not in groups.setdefault(r['request_id'], {})
        groups[r['request_id']][r['repeat']] = parsed
    votes, ties = {}, []
    for rid, values in groups.items():
        assert set(values) == {0, 1, 2}
        seq = [values[i] for i in range(3) if values[i] is not None]
        votes[rid] = Counter(seq).most_common(1)[0][0] if seq else None
        independently = sorted(set(seq), key=lambda p: (-seq.count(p), seq.index(p)))[0] if seq else None
        assert votes[rid] == independently
        if seq and sum(seq.count(p) == max(seq.count(x) for x in set(seq)) for p in set(seq)) > 1:
            ties.append(rid)
    return votes, groups, ties


def metrics(cases, predictions, target='label'):
    arms = list(predictions)
    result = {}
    for arm in arms:
        pred = predictions[arm]
        originals = [c for c in cases if c['variant'] == 'original']
        changed = [c for c in cases if c['variant'] == 'large' and c['stable'] and c[target] != c['original_label']]
        pairs = [(c, next(o for o in originals if o['material_id'] == c['material_id'] and o['condition'] == c['condition'])) for c in changed]
        def count(rows):
            return {'correct': sum(pred[c['case_id']] == c[target] for c in rows), 'n': len(rows)}
        result[arm] = {'all': count(cases), 'original': count(originals), 'stable_changed': count(changed), 'joint': {'correct': sum(pred[c['case_id']] == c[target] and pred[o['case_id']] == o[target] for c, o in pairs), 'n': len(pairs)}, 'false_restoration': {'count': sum(pred[c['case_id']] == c['original_label'] for c in changed), 'n': len(changed)}, 'conditions': {cond: count([c for c in cases if c['condition'] == cond]) for cond in ['gaussian', 'one_view_error']}}
    delta = [np.mean([int(predictions['split'][c['case_id']] == c[target]) - int(predictions['huber'][c['case_id']] == c[target]) for c in cases if c['material_id'] == mid]) for mid in sorted({c['material_id'] for c in cases})]
    boot = np.random.default_rng(E.SEED).choice(delta, size=(20000, len(delta)), replace=True).mean(axis=1)*100
    result['contrast'] = {'difference_pp': float(np.mean(delta)*100), 'parent_bootstrap_95': np.quantile(boot, [.025, .975]).tolist(), 'corrected': sum(predictions['split'][c['case_id']] == c[target] and predictions['huber'][c['case_id']] != c[target] for c in cases), 'regressed': sum(predictions['split'][c['case_id']] != c[target] and predictions['huber'][c['case_id']] == c[target] for c in cases)}
    return result


def analyze():
    s = json.loads(E.OUT.read_text())
    E.check(s)
    assert s['status'] == 'INFERENCE_COMPLETE'
    assert s['protocol']['arms'] == ['huber', 'split', 'lattice']
    assert not s['parallel_pending'] and not s['uncertain_charge_reserve_usd']
    assert len(s['records']) == 3*len(s['requests']) == 534
    votes, groups, ties = raw_votes(s)
    assert len(votes) == len(s['requests']) == 178
    usage = {k: sum(r['response']['usage'].get(k, 0) for r in s['records']) for k in E.S.RATES}
    cost = sum(usage[k]*rate for k, rate in E.S.RATES.items())/1e6
    assert abs(cost-s['reported_cost_usd']) < 1e-9
    assert cost+s['protocol']['prior_cost_usd'] <= 35
    assert all(r['response']['model'] == E.S.MODEL and r['reported_cost_usd'] <= r['reservation_usd'] for r in s['records'])
    pilot = json.loads(E.PILOT.read_text())
    pvotes, _, _ = raw_votes(pilot)
    assert pvotes == pilot['scores']['votes']
    assert s['protocol']['prior_cost_usd'] == pilot['scores']['recomputed_cost_usd'] or abs(s['protocol']['prior_cost_usd'] - pilot['scores']['recomputed_cost_usd']) < 1e-9
    all_cases = pilot['cases'] + s['cases']
    assert len({c['case_id'] for c in all_cases}) == 112
    assert len({c['material_id'] for c in all_cases}) == 28
    pred = {arm: {c['case_id']: (pvotes if c in pilot['cases'] else votes)[c['requests'][arm]] for c in all_cases} for arm in ['lattice', 'huber', 'split']}
    source_requests = {q['request_id']: q for q in pilot['requests'] + s['requests']}
    numerical = {arm: {} for arm in ['huber', 'split']}
    for c in all_cases:
        for arm in numerical:
            g = json.loads(source_requests[c['requests'][arm]]['prompt'].split('\n', 1)[1])
            atoms, lattice = np.array(g['atoms_atomic_number_fractional_xyz']), np.array(g['lattice_rows_angstrom'])
            p = E.label(atoms[:, 1:] @ lattice, atoms[:, 0].astype(int), lattice, .02)
            numerical[arm][c['case_id']] = p
            if 'common_readout' in c:
                assert p == c['common_readout'][arm]
    scopes = {'pilot': pilot['cases'], 'extension': s['cases'], 'pooled': all_cases}
    scores = {name: {'sonnet': metrics(cases, pred), 'numerical': metrics(cases, numerical), 'coordinate_rmsd_mA': {arm: float(np.mean([c['coordinate_rmsd'][arm] for c in cases])*1000) for arm in ['huber', 'split']}} for name, cases in scopes.items()}
    for name, cases in scopes.items():
        scores[name]['original_algorithm_readout'] = {arm: sum(c['algorithm_labels'][arm] == c.get('benchmark_label', c['label']) for c in cases) for arm in ['huber', 'split']}
    scores['extension']['mean_max_atomic_error_mA'] = {arm: float(np.mean([c['max_atomic_error'][arm] for c in s['cases']])*1000) for arm in ['huber', 'split']}
    archived_cases = [{**c, 'archived_target': c.get('benchmark_label', c['label'])} for c in s['cases']]
    scores['archived_target_sensitivity'] = {'sonnet': metrics(archived_cases, pred, 'archived_target'), 'numerical': metrics(archived_cases, numerical, 'archived_target')}
    local = json.loads((E.ROOT / 'results/reconstruction_vlm_pilot/study.json').read_text())
    assert local['cases'] == pilot['cases']
    gemma = {arm: sum(local['responses'][c['requests'][arm]]['prediction'] == c['label'] for c in local['cases']) for arm in ['lattice', 'huber', 'split']}
    assert gemma == {'lattice': 2, 'huber': 0, 'split': 1}
    scores['gemma_pilot'] = {'n': 28, 'correct': gemma, 'generation': 'One greedy response per input; Gemma 3 4B MLX 4-bit; no expanded Gemma run'}
    per_repeat = {arm: [sum(groups[c['requests'][arm]][i] == c['label'] for c in s['cases']) for i in range(3)] for arm in ['lattice', 'huber', 'split']}
    audit = {'status': 'PASS', 'extension_cases': 84, 'extension_parents': 21, 'pooled_cases': 112, 'extension_responses': len(s['records']), 'invalid_responses': sum(r['prediction'] is None for r in s['records']), 'truncated_responses': sum(r['response']['stop_reason'] == 'max_tokens' for r in s['records']), 'tied_inputs': len(ties), 'usage': usage, 'extension_cost_usd': cost, 'total_cost_including_pilot_usd': cost+s['protocol']['prior_cost_usd'], 'cache_hit_calls': sum(r['response']['usage'].get('cache_read_input_tokens', 0) > 0 for r in s['records']), 'per_repeat_correct': per_repeat, 'raw_parser_and_vote_recheck': True}
    return s, scores, audit


def main():
    _, scores, _ = analyze()
    print(json.dumps(scores, indent=2))


if __name__ == '__main__':
    main()

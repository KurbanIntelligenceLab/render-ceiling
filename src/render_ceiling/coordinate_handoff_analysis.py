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
    s, scores, audit = analyze()
    s['scores'] = scores
    s['verification']['final_scoring_audit'] = audit
    E.save(s)
    lines = ['# Expanded reconstruction-to-Sonnet comparison', '', 'This completed extension adds 84 matched cases from all 21 remaining parents in the existing cohort. The original pilot had 28 cases from seven parents; the pooled analysis covers 112 cases from 28 parents. The extension evaluates lattice only, Huber reconstruction, and split one-SE reconstruction. No new exact-coordinate calls were made.', '', '## Model outcomes', '', '| Model / cohort | Cases | Lattice correct | Huber correct | Ours correct |', '| --- | ---: | ---: | ---: | ---: |', '| Gemma 3 4B, original pilot | 28 | 2 | 0 | 1 |']
    for name, title, n in [('pilot', 'Sonnet, original pilot', 28), ('extension', 'Sonnet, new replication', 84), ('pooled', 'Sonnet, pooled', 112)]:
        m = scores[name]['sonnet']
        lines.append(f'| {title} | {n} | {m["lattice"]["all"]["correct"]} | {m["huber"]["all"]["correct"]} | {m["split"]["all"]["correct"]} |')
    m = scores['extension']['sonnet']
    lines += ['', f'On the new replication, ours scores {m["split"]["all"]["correct"]}/84 versus {m["huber"]["all"]["correct"]}/84 for Huber and {m["lattice"]["all"]["correct"]}/84 for lattice alone. The observed split-minus-Huber change is {m["contrast"]["difference_pp"]:+.2f} percentage points. On stable class-changing structures, ours scores {m["split"]["stable_changed"]["correct"]}/{m["split"]["stable_changed"]["n"]} versus {m["huber"]["stable_changed"]["correct"]}/{m["huber"]["stable_changed"]["n"]}; original-structure accuracy is {m["split"]["original"]["correct"]}/42 versus {m["huber"]["original"]["correct"]}/42. This separates detection of actual departures from preservation of the original class.']
    lines += ['', 'Gemma uses one greedy response per input; Sonnet uses three responses per distinct input and the recorded voting rule. Gemma was not rerun on the 84 new cases. Its small absolute score should remain visible alongside the relative comparison.', '', '## Geometric fidelity and numerical readout', '', '| Cohort | Huber RMSD (mÅ) | Ours RMSD (mÅ) | Huber numerical correct | Ours numerical correct |', '| --- | ---: | ---: | ---: | ---: |']
    for name in ['pilot', 'extension', 'pooled']:
        m = scores[name]
        lines.append(f'| {name} | {m["coordinate_rmsd_mA"]["huber"]:.3f} | {m["coordinate_rmsd_mA"]["split"]:.3f} | {m["numerical"]["huber"]["all"]["correct"]} | {m["numerical"]["split"]["all"]["correct"]} |')
    lines += ['', 'The numerical detector uses the same 0.02 Å positional tolerance and 5° angle tolerance on both methods’ actual serialized coordinates. This measures recoverable symmetry information, separately from model interpretation. The original pilot Huber adaptive readout was 22/28; its common-tolerance result is 16/28. Those are different readout protocols.', '', '| Original method-specific readouts, archived benchmark targets | Huber | Ours |', '| --- | ---: | ---: |']
    for name in ['pilot', 'extension', 'pooled']:
        values = scores[name]['original_algorithm_readout']
        lines.append(f'| {name} | {values["huber"]} | {values["split"]} |')
    maximum = scores['extension']['mean_max_atomic_error_mA']
    lines += ['', f'The extension mean of the per-case maximum atomic error is {maximum["huber"]:.3f} mÅ for Huber and {maximum["split"]:.3f} mÅ for ours, recomputed with species-matched periodic assignments.', '', '## Paired comparisons', '', '| Cohort / readout | Ours minus Huber (percentage points) | Parent-bootstrap 95% interval | Corrections | Regressions |', '| --- | ---: | --- | ---: | ---: |']
    for name in ['pilot', 'extension', 'pooled']:
        for readout in ['sonnet', 'numerical']:
            d = scores[name][readout]['contrast']; lo, hi = d['parent_bootstrap_95']
            lines.append(f'| {name} / {readout} | {d["difference_pp"]:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {d["corrected"]} | {d["regressed"]} |')
    lines += ['', 'Intervals resample parents, preserving each parent’s four dependent cases. The original pilot is exploratory; the new Sonnet split-minus-Huber comparison was fixed before its inference. The common-detector extension was motivated by the pilot failure audit. These intervals are descriptive, and no equivalence margin was prespecified.', '', '## Conditions and paired structure changes', '', '| Cohort / input | Gaussian | Corrupted view | Original | Stable changed | Both original and changed correct | False restoration |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name in ['extension', 'pooled']:
        for arm in ['lattice', 'huber', 'split']:
            m = scores[name]['sonnet'][arm]
            entries = [m['conditions']['gaussian'], m['conditions']['one_view_error'], m['original'], m['stable_changed'], m['joint']]
            values = [f'{x["correct"]}/{x["n"]}' for x in entries]
            values.append(f'{m["false_restoration"]["count"]}/{m["false_restoration"]["n"]}')
            lines.append(f'| {name} / {arm} | '+' | '.join(values)+' |')
    lines += ['', '## Input and target audit', '', 'All remaining parents were included, with three per original crystal system. Selection was not based on observed reconstruction or model advantages. Conditions match the pilot: original and large-displacement structures, Gaussian and one-view corruption at 0.01 Å, frozen cameras, and noise repetition zero. Inputs contain lattice and, for reconstruction arms, atomic numbers and eight-decimal fractional coordinates. They omit method names, targets, material identifiers, and numerical readout labels.', '', 'Before any extension inference, the audit found two large-variant cases from mp-865981 whose archived benchmark target is triclinic but whose reference geometry is monoclinic at the prompt’s 0.02 Å tolerance. Both cases were retained, scored against the stated prompt tolerance, and preserved with their original benchmark labels. The archived-target sensitivity follows:', '', '| Target convention, extension | Huber Sonnet | Ours Sonnet | Huber numerical | Ours numerical |', '| --- | ---: | ---: | ---: | ---: |']
    for name, m in [('Prompt-matched reference', scores['extension']), ('Archived benchmark', scores['archived_target_sensitivity'])]:
        lines.append(f'| {name} | {m["sonnet"]["huber"]["all"]["correct"]} | {m["sonnet"]["split"]["all"]["correct"]} | {m["numerical"]["huber"]["all"]["correct"]} | {m["numerical"]["split"]["all"]["correct"]} |')
    lines += ['', 'The lattice arm was requested while the reconstruction run was underway and added for every parent. Its 21 distinct inputs share votes across each parent’s four cases. The protocol amendment and prior protocol hash are retained. No exact-reference calls were added; the original pilot’s 22/28 Sonnet exact-coordinate control remains available in its record. This is a text-geometry handoff study, not an image-plus-reconstruction intervention.', '', '## Inference, cost, and reproducibility', '', f'The extension contains {audit["extension_responses"]} responses: 471 for reconstruction inputs and 63 for lattice-only inputs. There are {audit["invalid_responses"]} invalid responses, including {audit["truncated_responses"]} truncations, and {audit["tied_inputs"]} tied input votes. Invalid responses are retained; valid labels vote, ties use first occurrence, and all-invalid inputs count incorrect. Every extension request has a 16,384-token output cap with native default inference settings. There are no correctness retries.', '', f'Extension token cost is **${audit["extension_cost_usd"]:.4f}**; total cost including the earlier pilot is **${audit["total_cost_including_pilot_usd"]:.4f}**, under the original $35 cap. The extension records {audit["cache_hit_calls"]} cache-hit calls. Charges are independently recomputed from provider-reported usage using [Anthropic’s pricing](https://platform.claude.com/docs/en/about-claude/pricing). Full possible charges were reserved before dispatch, including concurrent and unknown charges. Parent blocks were admitted by budget, never accuracy.', '', '| Input | Correct cases in repeats 1, 2, 3 / 84 |', '| --- | --- |']
    for arm, values in audit['per_repeat_correct'].items():
        lines.append(f'| {arm} | '+', '.join(map(str, values))+' |')
    lines += ['', 'An operational cache check paused after 378 responses because one parent’s prompts had 513–515 total input tokens but no cache writes. Inspection of 285 cached calls showed four tokens outside the cached prefix, implying only 509–511 cacheable tokens on that parent, below the 512-token minimum. All completed calls were retained, and the remaining parents resumed with unchanged inputs, settings, scoring, and spending limits. This audit made no extra generation calls.']
    lines += ['', 'The [single complete study record](study.json) contains input prompts, case mappings, both target conventions, all raw responses, protocol history, token accounting, numerical readouts, scores, and verification. Geometry checks and mocked spending safeguards passed twice before spending. Final analysis reparses raw answers, verifies votes using two implementations, recomputes charges and numerical labels, and checks original versus extension parent separation. This report is separate from the manuscript pending interpretation of the completed evidence.', '']
    E.OUT.with_name('report.md').write_text('\n'.join(lines))
    print(json.dumps({'audit': audit, 'scores': scores}, indent=2))


if __name__ == '__main__':
    main()

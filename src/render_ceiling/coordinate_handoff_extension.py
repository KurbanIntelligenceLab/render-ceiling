import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import fcntl
import hashlib
import json
from pathlib import Path
import threading
import time

import numpy as np
from pymatgen.core import Lattice, Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from scipy.optimize import linear_sum_assignment

from render_ceiling import coordinate_handoff_sonnet as S
from render_ceiling.correspondence import label
from render_ceiling.reconstruct import projection_matrices
from render_ceiling.render import VIEW_ORDER, VIEWS
from render_ceiling.robust_triangulation import robust_triangulation

ROOT = S.ROOT
OUT = ROOT / 'results/reconstruction_sonnet_extension/study.json'
PILOT = ROOT / 'results/reconstruction_sonnet_pilot/study.json'
SEED = 20261029


def filehash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(s):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(s, indent=2, allow_nan=False) + '\n')
    tmp.replace(OUT)


def prepare():
    assert not OUT.exists()
    pilot = json.loads(PILOT.read_text())
    source = ROOT / 'results/symmetry_selector_refinement'
    parents = json.loads((source / 'dataset.json').read_text())
    used = {c['material_id'] for c in pilot['cases']}
    parents = {p['material_id']: p for p in parents if p['material_id'] not in used}
    assert len(parents) == 21
    assert set(Counter(p['original_label'] for p in parents.values()).values()) == {3}
    ordered_parents = sorted(parents, key=lambda mid: S.digest([SEED, 'parent_order', mid]))
    rows = [json.loads(line) for line in (source / 'heldout.jsonl').read_text().splitlines()]
    rows = [r for r in rows if r['material_id'] in parents and r['sigma'] == .01 and r['noise_rep'] == 0 and r['camera'] == 'frozen' and r['variant'] in ['original', 'large']]
    assert len(rows) == 84
    instruction = pilot['requests'][0]['prompt'].split('\n', 1)[0] + '\n'
    requests, cases = {}, []
    cameras = projection_matrices(VIEW_ORDER, VIEWS)
    for r in sorted(rows, key=lambda r: (ordered_parents.index(r['material_id']), S.digest([SEED, r['case_id']]))):
        st = Structure.from_dict(parents[r['material_id']]['variants'][r['variant']]['structure'])
        rng = np.random.default_rng(r['noise_seed'])
        obs = []
        for camera in cameras:
            xy = st.cart_coords @ camera[:, :2] + rng.normal(0, r['sigma'], (len(st), 2))
            ix = rng.permutation(len(st))
            obs.append({'xy': xy[ix], 'species': np.asarray(st.atomic_numbers)[ix]})
        if r['corruption']:
            c = r['corruption']
            obs[c['view']]['xy'][c['observation_index']] += c['displacement']
        ih = S.digest({'observations': [{k: v.tolist() for k, v in o.items()} for o in obs], 'cameras': [c.tolist() for c in cameras], 'lattice': st.lattice.matrix.tolist()})
        assert ih == r['input_hash']
        robust = robust_triangulation(obs, cameras, st.lattice.matrix)
        split = r['result']['outputs'][r['selector']['selected']['paired_1se']]
        assert robust['predictions']['huber_adaptive_6'] == r['predictions']['huber_adaptive_6']
        target = label(st.cart_coords, np.asarray(st.atomic_numbers), st.lattice.matrix, .02)
        assert target == SpacegroupAnalyzer(st, symprec=.02, angle_tolerance=5).get_crystal_system()
        case = {k: r[k] for k in ['case_id', 'material_id', 'variant', 'condition', 'label', 'original_label', 'stable', 'input_hash']}
        case['benchmark_label'] = r['label']
        case['label'] = target
        case.update(requests={}, coordinate_rmsd={'huber': r['robust_geometry']['complete_rmsd'], 'split': r['geometry']['paired_1se']['complete_rmsd']}, max_atomic_error={}, algorithm_labels={'huber': r['predictions']['huber_adaptive_6'], 'split': r['predictions']['paired_1se']}, common_readout={})
        lattice = np.round(st.lattice.matrix, 8)
        for arm, result in [('huber', robust), ('split', split)]:
            cart, species = np.array(result['cart']), np.array(result['species'])
            distances = []
            for z in np.unique(st.atomic_numbers):
                cost = np.linalg.norm(st.cart_coords[np.array(st.atomic_numbers) == z, None] - cart[None, species == z], axis=2)
                ii, jj = linear_sum_assignment(cost)
                distances.extend(cost[ii, jj])
            assert abs(np.sqrt(np.mean(np.square(distances))) - case['coordinate_rmsd'][arm]) < 1e-10
            frac = (cart @ np.linalg.inv(st.lattice.matrix)) % 1
            atoms = sorted([[int(z), *[round(float(x), 8) for x in xyz]] for z, xyz in zip(species, frac)])
            content = {'lattice_rows_angstrom': lattice.tolist(), 'atoms_atomic_number_fractional_xyz': atoms}
            prompt = instruction + json.dumps(content, separators=(',', ':'))
            rid = hashlib.sha256(prompt.encode()).hexdigest()
            requests.setdefault(rid, {'request_id': rid, 'prompt': prompt})
            case['requests'][arm] = rid
            a = np.array(atoms)
            dslabel = label(a[:, 1:] @ lattice, a[:, 0].astype(int), lattice, .02)
            independent = SpacegroupAnalyzer(Structure(lattice, a[:, 0].astype(int), a[:, 1:]), symprec=.02, angle_tolerance=5).get_crystal_system()
            assert dslabel == independent
            case['common_readout'][arm] = dslabel
            periodic = []
            for z in np.unique(species):
                cost = Lattice(lattice).get_all_distances(st.frac_coords[np.array(st.atomic_numbers) == z], a[a[:, 0] == z, 1:])
                ii, jj = linear_sum_assignment(cost)
                periodic.extend(cost[ii, jj])
            assert abs(np.sqrt(np.mean(np.square(periodic))) - case['coordinate_rmsd'][arm]) < 1e-7
            case['max_atomic_error'][arm] = float(max(periodic))
        cases.append(case)
    ordered = sorted(requests.values(), key=lambda q: S.digest([SEED, q['request_id']]))
    p = {'model': S.MODEL, 'api_version': '2026-10-21', 'arms': ['huber', 'split'], 'max_tokens': 16384, 'repeats': 3, 'budget_usd_including_pilot': 35, 'prior_cost_usd': pilot['reported_cost_usd'], 'parent_order': ordered_parents, 'cohort': 'All 21 remaining parents from existing held-out cohort; three per original system; 84 original/large x Gaussian/corrupted cases; frozen cameras, sigma .01, repetition 0; no selection on results', 'primary': 'Sonnet split-minus-Huber majority-vote accuracy on 84 extension cases, parent-cluster bootstrap; original 28 and pooled 112 reported separately', 'secondary': 'Identical numerical readout at .02 angstrom and 5 degrees, coordinate RMSD, maximum atomic error, original accuracy, stable-changed accuracy, paired joint accuracy, false restoration, Gaussian and corrupted subsets', 'controls': 'No new exact-coordinate or lattice-only API calls; original controls retained in pilot record', 'format': 'Same instruction and eight-decimal species-sorted fractional coordinates as pilot; no target, method, parent identifier or numerical readout in prompt', 'voting': 'Three responses per distinct input; most common valid answer, ties by earliest occurrence; all-invalid is incorrect; identical input shares its responses', 'retry': 'No automatic retry; truncations and malformed answers are retained as invalid; unknown billing reserves full charge and stops', 'sampling': 'Native defaults, no temperature/top_p/top_k/effort overrides', 'cache': 'Explicit final text block 5-minute TTL; sequential repeats per input; audit actual reads', 'budget': 'Full conservative reservation per request; complete parent-block admission; previous pilot spend plus new spend plus pending or unknown charges never above 35; stop by cost, never accuracy', 'prices_per_million': S.RATES, 'source_hashes': {str(f.relative_to(ROOT)): filehash(f) for f in [PILOT, source / 'dataset.json', source / 'heldout.jsonl', Path(S.__file__), Path(__file__)]}, 'requests_hash': S.digest(ordered), 'cases_hash': S.digest(cases)}
    p['target_definition'] = 'Unperturbed reference structure numerical class at the prompt tolerance .02 angstrom and 5 degrees; archived benchmark_label retained. Two large-variant cases from unstable parent mp-865981 have reference monoclinic versus archived triclinic; resolved before any paid calls, no exclusions.'
    state = {'protocol': p, 'protocol_hash': S.digest(p), 'requests': ordered, 'cases': cases, 'records': [], 'preflight': {}, 'parallel_pending': {}, 'uncertain_charge_reserve_usd': 0, 'reported_cost_usd': 0, 'status': 'PREPARED', 'verification': {'input_hashes': 84, 'coordinate_rmsd_checks': 168, 'periodic_roundtrip_checks': 168, 'common_readout_checks': 168, 'reference_labels_checked_locally': 84}}
    save(state)
    print(json.dumps({'cases': len(cases), 'parents': len(parents), 'unique_inputs': len(ordered), 'planned_calls': len(ordered)*3, 'prior_cost_usd': p['prior_cost_usd']}))


def check(s):
    p = s['protocol']
    assert S.digest(p) == s['protocol_hash']
    assert S.digest(s['requests']) == p['requests_hash'] and S.digest(s['cases']) == p['cases_hash']
    for name, sha in p['source_hashes'].items():
        assert filehash(ROOT / name) == sha, name
    assert p['budget_usd_including_pilot'] == 35


def reserve(q, s):
    n = s['preflight'][q['request_id']]['input_tokens']
    return (1.10*(n+128)*2.5 + s['protocol']['max_tokens']*10)/1e6


def preflight():
    s = json.loads(OUT.read_text())
    check(s)
    todo = [q for q in s['requests'] if q['request_id'] not in s['preflight']]
    def count(q):
        return q['request_id'], S.request('messages/count_tokens', S.payload(q))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for rid, response in pool.map(count, todo):
            s['preflight'][rid] = response
            save(s)
            assert isinstance(response.get('input_tokens'), int)
    s['preflight_summary'] = {'max_input_tokens': max(x['input_tokens'] for x in s['preflight'].values()), 'cache_eligible': sum(x['input_tokens'] >= 512 for x in s['preflight'].values()), 'all_calls_maximum_usd': 3*sum(reserve(q, s) for q in s['requests']), 'remaining_budget_usd': 35-s['protocol']['prior_cost_usd']}
    s['status'] = 'PREFLIGHT_PASSED'
    save(s)
    print(json.dumps(s['preflight_summary']))


def run():
    s = json.loads(OUT.read_text())
    check(s)
    assert len(s['preflight']) == len(s['requests'])
    assert not s['parallel_pending'] and not s['uncertain_charge_reserve_usd']
    assert s['verification'].get('mock_runner_checks') == 'PASS'
    assert s['verification'].get('independent_input_audit') == 'PASS'
    qmap = {q['request_id']: q for q in s['requests']}
    done = {(r['request_id'], r['repeat']) for r in s['records']}
    assert len(done) == len(s['records'])
    mutex, stop = threading.Lock(), threading.Event()
    s['status'] = 'RUNNING'
    save(s)
    def group(q):
        for repeat in range(3):
            if (q['request_id'], repeat) in done:
                continue
            key = q['request_id'] + ':' + str(repeat)
            bound = reserve(q, s)
            with mutex:
                if stop.is_set():
                    return
                committed = s['protocol']['prior_cost_usd'] + s['reported_cost_usd'] + s['uncertain_charge_reserve_usd'] + sum(x['reservation_usd'] for x in s['parallel_pending'].values())
                if committed + bound > 35:
                    s['status'] = 'BUDGET_STOP'
                    stop.set()
                    save(s)
                    return
                s['parallel_pending'][key] = {'request_id': q['request_id'], 'repeat': repeat, 'reservation_usd': bound}
                save(s)
            started = time.monotonic()
            response = S.request('messages', S.payload(q, True, s['protocol']['max_tokens']))
            usage = response.get('usage')
            cost = sum(usage.get(k, 0)*v for k, v in S.RATES.items())/1e6 if usage else None
            answer = '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')
            row = {'request_id': q['request_id'], 'repeat': repeat, 'prediction': S.parse(answer) if response.get('stop_reason') == 'end_turn' else None, 'response': response, 'reported_cost_usd': cost, 'reservation_usd': bound, 'elapsed_seconds': time.monotonic()-started}
            with mutex:
                del s['parallel_pending'][key]
                s['records'].append(row)
                done.add((q['request_id'], repeat))
                if cost is None:
                    s['uncertain_charge_reserve_usd'] += bound
                else:
                    s['reported_cost_usd'] += cost
                if response.get('model') != S.MODEL or response.get('stop_reason') not in ['end_turn', 'max_tokens'] or cost is None or cost > bound:
                    s['status'] = 'RESPONSE_AUDIT_STOP'
                    stop.set()
                save(s)
                print(json.dumps({'completed': len(s['records']), 'of': len(s['requests'])*3, 'stop': response.get('stop_reason'), 'cache_read': (usage or {}).get('cache_read_input_tokens', 0), 'total_cost_usd': round(s['protocol']['prior_cost_usd']+s['reported_cost_usd'], 6)}), flush=True)
    for mid in s['protocol']['parent_order']:
        ids = {rid for c in s['cases'] if c['material_id'] == mid for rid in c['requests'].values()}
        todo = [qmap[rid] for rid in sorted(ids) if any((rid, repeat) not in done for repeat in range(3))]
        if not todo:
            continue
        block_reserve = sum(reserve(q, s)*sum((q['request_id'], repeat) not in done for repeat in range(3)) for q in todo)
        if s['protocol']['prior_cost_usd'] + s['reported_cost_usd'] + s['uncertain_charge_reserve_usd'] + block_reserve > 35:
            s['status'] = 'BUDGET_STOP_BEFORE_PARENT'
            stop.set()
            break
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(group, todo))
        if stop.is_set():
            break
        eligible = [q for q in todo if s['preflight'][q['request_id']]['input_tokens'] >= 512]
        if eligible and not any(r['response'].get('usage', {}).get('cache_read_input_tokens', 0) for r in s['records'] if r['request_id'] in {q['request_id'] for q in eligible}):
            s['status'] = 'CACHE_AUDIT_STOP'
            stop.set()
            break
        print(json.dumps({'completed_parent': mid, 'cost_usd_including_pilot': s['protocol']['prior_cost_usd'] + s['reported_cost_usd']}), flush=True)
    if not stop.is_set():
        assert len(s['records']) == len(s['requests'])*3
        s['status'] = 'INFERENCE_COMPLETE'
    assert not s['parallel_pending']
    save(s)
    print(json.dumps({'status': s['status'], 'calls': len(s['records']), 'total_cost_usd': s['protocol']['prior_cost_usd'] + s['reported_cost_usd']}), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['prepare', 'preflight', 'run'])
    (ROOT / 'outputs').mkdir(exist_ok=True)
    lock = (ROOT / 'outputs/sonnet_handoff.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    globals()[ap.parse_args().action]()

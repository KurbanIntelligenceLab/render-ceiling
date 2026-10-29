import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/reconstruction_vlm_pilot/study.json'
MODEL = Path(os.environ.get('GEMMA_MODEL_PATH', 'models/gemma-3-4b-it-4bit'))
CLASSES = ['triclinic', 'monoclinic', 'orthorhombic', 'tetragonal', 'trigonal', 'hexagonal', 'cubic']
SEED = 20261028


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def filehash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def write(value):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    tmp.replace(OUT)


def parse(text):
    matches = re.findall(r'ANSWER:\s*(' + '|'.join(CLASSES) + r')\b', text, flags=re.I)
    if len(matches) == 1:
        return matches[0].lower()
    clean = text.strip().lower().strip('.*` \n')
    return clean if clean in CLASSES else None


def prepare():
    assert not OUT.exists(), 'Existing study must be preserved'
    import numpy as np
    from pymatgen.core import Structure
    from scipy.optimize import linear_sum_assignment
    from render_ceiling.render import VIEW_ORDER, VIEWS
    from render_ceiling.reconstruct import projection_matrices
    from render_ceiling.robust_triangulation import robust_triangulation
    from render_ceiling.correspondence import label
    source = ROOT / 'results/symmetry_selector_refinement'
    parents = json.loads((source / 'dataset.json').read_text())
    selected = [min((p for p in parents if p['original_label'] == c), key=lambda p: digest([SEED, 'parent', p['material_id']])) for c in CLASSES]
    ids = {p['material_id'] for p in selected}
    parents = {p['material_id']: p for p in selected}
    rows = [json.loads(s) for s in (source / 'heldout.jsonl').read_text().splitlines()]
    rows = [r for r in rows if r['material_id'] in ids and r['sigma'] == .01 and r['noise_rep'] == 0 and r['camera'] == 'frozen' and r['variant'] in ['original', 'large']]
    assert len(rows) == 28
    requests, cases = {}, []
    instruction = 'Classify the crystal system of the supplied periodic structure. Allowed answers: triclinic, monoclinic, orthorhombic, tetragonal, trigonal, hexagonal, cubic. Use the full atomic basis when provided; lattice metrics alone need not determine structural symmetry. Coordinates may contain small measurement errors. Use a positional tolerance of 0.02 angstrom and an angular tolerance of 5 degrees. Return exactly one line: ANSWER: <crystal system>.\n'
    for r in sorted(rows, key=lambda r: digest([SEED, r['case_id']])):
        s = Structure.from_dict(parents[r['material_id']]['variants'][r['variant']]['structure'])
        cameras = projection_matrices(VIEW_ORDER, VIEWS)
        rng = np.random.default_rng(r['noise_seed'])
        obs = []
        for camera in cameras:
            xy = s.cart_coords @ camera[:, :2] + rng.normal(0, r['sigma'], (len(s), 2))
            ix = rng.permutation(len(s))
            obs.append({'xy': xy[ix], 'species': np.asarray(s.atomic_numbers)[ix]})
        if r['corruption']:
            c = r['corruption']
            obs[c['view']]['xy'][c['observation_index']] += c['displacement']
        ih = digest({'observations': [{k: v.tolist() for k, v in o.items()} for o in obs], 'cameras': [c.tolist() for c in cameras], 'lattice': s.lattice.matrix.tolist()})
        assert ih == r['input_hash'], (r['case_id'], ih)
        robust = robust_triangulation(obs, cameras, s.lattice.matrix)
        split = r['result']['outputs'][r['selector']['selected']['paired_1se']]
        def rmsd(cart, species):
            distances = []
            for z in np.unique(s.atomic_numbers):
                a = s.cart_coords[np.asarray(s.atomic_numbers) == z]
                b = np.asarray(cart)[np.asarray(species) == z]
                assert len(a) == len(b)
                d = np.linalg.norm(a[:, None] - b[None], axis=2)
                i, j = linear_sum_assignment(d)
                distances.extend(d[i, j])
            return float(np.sqrt(np.mean(np.square(distances))))
        assert abs(rmsd(robust['cart'], robust['species']) - r['robust_geometry']['complete_rmsd']) < 1e-10
        assert robust['predictions']['huber_adaptive_6'] == r['predictions']['huber_adaptive_6']
        assert abs(rmsd(split['cart'], split['species']) - r['geometry']['paired_1se']['complete_rmsd']) < 1e-10
        assert label(s.cart_coords, np.asarray(s.atomic_numbers), s.lattice.matrix, .02) == r['label']
        case = {k: r[k] for k in ['case_id', 'material_id', 'variant', 'condition', 'label', 'original_label', 'stable', 'input_hash']}
        case.update(requests={}, coordinate_rmsd={'huber': r['robust_geometry']['complete_rmsd'], 'split': r['geometry']['paired_1se']['complete_rmsd']}, algorithm_labels={'huber': r['predictions']['huber_adaptive_6'], 'split': r['predictions']['paired_1se']})
        lattice = [[round(float(v), 8) for v in row] for row in s.lattice.matrix]
        geometries = {'exact': (s.cart_coords, s.atomic_numbers), 'huber': (robust['cart'], robust['species']), 'split': (split['cart'], split['species']), 'lattice': None}
        for arm, geometry in geometries.items():
            content = {'lattice_rows_angstrom': lattice}
            if geometry is not None:
                cart, species = geometry
                frac = (np.asarray(cart) @ np.linalg.inv(s.lattice.matrix)) % 1
                atoms = sorted([[int(z), *[round(float(v), 8) for v in f]] for z, f in zip(species, frac)])
                content['atoms_atomic_number_fractional_xyz'] = atoms
                if arm == 'exact':
                    assert label(np.array([a[1:] for a in atoms]) @ np.array(lattice), np.array([a[0] for a in atoms]), np.array(lattice), .02) == r['label']
            prompt = instruction + json.dumps(content, separators=(',', ':'))
            rid = hashlib.sha256(prompt.encode()).hexdigest()
            requests.setdefault(rid, {'request_id': rid, 'prompt': prompt})
            case['requests'][arm] = rid
        cases.append(case)
    files = {str(p.relative_to(ROOT)): filehash(p) for p in [source / 'dataset.json', source / 'heldout.jsonl', Path(__file__)]}
    model_files = {p.name: filehash(p) for p in MODEL.iterdir() if p.is_file()}
    protocol = {'purpose': 'Exploratory reconstructed-coordinate handoff; no raster extraction tested', 'parent_selection': 'One parent per original crystal system, minimum SHA256([20261028,parent,material_id]); no outcome selection', 'parents': sorted(ids), 'selection_seed': SEED, 'conditions': 'sigma 0.01, frozen cameras, noise repetition 0, original and large variants, Gaussian and corrupted', 'primary_contrast': 'Split minus Huber downstream correctness on all 28 cases; descriptive parent-cluster bootstrap', 'secondary': 'Original accuracy; stable changed accuracy; paired joint correctness; false restoration; invalid responses; exact geometry and lattice controls', 'generation': {'temperature': 0, 'top_p': 1, 'top_k': 0, 'max_tokens': 256, 'repetitions': 1}, 'parser': 'Exactly one ANSWER: valid_class occurrence, otherwise exact standalone class; invalid counts incorrect; no spelling repairs', 'deduplication': 'Identical prompts share one deterministic response; repeated endpoints are not independent', 'source_hashes': files, 'model_path': str(MODEL), 'model_revision': MODEL.name, 'model_files_sha256': model_files, 'requests_hash': digest(list(requests.values())), 'cases_hash': digest(cases), 'no_correctness_retries': True}
    study = {'protocol': protocol, 'protocol_hash': digest(protocol), 'requests': sorted(requests.values(), key=lambda q: digest([SEED, q['request_id']])), 'cases': cases, 'responses': {}, 'status': 'PREPARED', 'verification': {'regenerated_observations_match': 28, 'huber_rmsd_and_labels_match': 28, 'split_rmsd_matches': 28, 'rounded_reference_labels_match': 28}}
    protocol['requests_hash'] = digest(study['requests'])
    study['protocol_hash'] = digest(protocol)
    write(study)
    print(json.dumps({'cases': len(cases), 'unique_requests': len(requests), 'parents': sorted(ids)}))


def run():
    for k in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_DATASETS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY']:
        os.environ[k] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    import ctypes
    import gc
    from importlib.metadata import distributions
    check = ctypes.CDLL('/usr/lib/libSystem.B.dylib').sandbox_check
    check.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    check.restype = ctypes.c_int
    assert check(os.getpid(), b'network-outbound', 0) == 1
    study = json.loads(OUT.read_text())
    p = study['protocol']
    assert digest(p) == study['protocol_hash']
    assert digest(study['requests']) == p['requests_hash'] and digest(study['cases']) == p['cases_hash']
    for path, h in p['source_hashes'].items():
        assert filehash(ROOT / path) == h
    for name, h in p['model_files_sha256'].items():
        assert filehash(MODEL / name) == h
    import mlx.core as mx
    from mlx_vlm import load, generate, prepare_inputs
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import should_add_special_tokens
    mx.set_memory_limit(18_000_000_000)
    mx.set_cache_limit(512_000_000)
    env = sorted(f'{d.metadata["Name"]}=={d.version}' for d in distributions())
    study['runtime'] = {'environment': env, 'network_denied': True, 'device': mx.device_info()}
    study['status'] = 'RUNNING'
    write(study)
    model, processor = load(str(MODEL), trust_remote_code=False)
    for q in study['requests']:
        rid = q['request_id']
        if rid in study['responses']:
            continue
        mx.random.seed(SEED)
        gc.collect()
        mx.clear_cache()
        mx.reset_peak_memory()
        start = time.monotonic()
        formatted = apply_chat_template(processor, model.config, q['prompt'], num_images=0)
        inputs = prepare_inputs(processor, images=None, prompts=formatted, add_special_tokens=should_add_special_tokens(model.config.model_type, processor), pad_to_uniform_size=False)
        n = inputs['input_ids'].shape[-1]
        assert n + 256 < 32768
        kwargs = {k: v for k, v in inputs.items() if k != 'attention_mask'}
        kwargs['mask'] = inputs.get('attention_mask')
        result = generate(model, processor, formatted, **p['generation'], prefill_step_size=512, verbose=False, **kwargs)
        mx.synchronize()
        assert result.cached_tokens == 0 and result.prompt_tokens == n
        study['responses'][rid] = {'raw_output': result.text, 'prediction': parse(result.text), 'prompt_tokens': n, 'generation_tokens': result.generation_tokens, 'finish_reason': result.finish_reason, 'truncated': result.generation_tokens >= 256 or result.finish_reason == 'length', 'formatted_prompt_sha256': hashlib.sha256(formatted.encode()).hexdigest(), 'seconds': time.monotonic() - start, 'metal_peak_bytes': mx.get_peak_memory()}
        write(study)
        print(f'{len(study["responses"])}/{len(study["requests"])} {result.text!r}', flush=True)
        del inputs, kwargs, result
    study['status'] = 'INFERENCE_COMPLETE'
    write(study)


def score():
    import numpy as np
    study = json.loads(OUT.read_text())
    assert len(study['responses']) == len(study['requests'])
    assert digest(study['protocol']) == study['protocol_hash']
    assert digest(study['cases']) == study['protocol']['cases_hash']
    assert digest(study['requests']) == study['protocol']['requests_hash']
    cases = study['cases']
    def pred(c, arm):
        response = study['responses'][c['requests'][arm]]
        assert parse(response['raw_output']) == response['prediction']
        return response['prediction']
    def fraction(flags):
        return {'correct': sum(flags), 'n': len(flags), 'percent': 100 * sum(flags) / len(flags) if flags else None}
    metrics = {}
    for arm in ['lattice', 'exact', 'huber', 'split']:
        original = [c for c in cases if c['variant'] == 'original']
        changed = [c for c in cases if c['variant'] == 'large' and c['stable'] and c['label'] != c['original_label']]
        paired = [(c, next(o for o in original if o['material_id'] == c['material_id'] and o['condition'] == c['condition'])) for c in changed]
        metrics[arm] = {'all': fraction([pred(c, arm) == c['label'] for c in cases]), 'original': fraction([pred(c, arm) == c['label'] for c in original]), 'stable_changed': fraction([pred(c, arm) == c['label'] for c in changed]), 'joint': fraction([pred(c, arm) == c['label'] and pred(o, arm) == o['label'] for c, o in paired]), 'false_restoration': fraction([pred(c, arm) == c['original_label'] for c in changed]), 'invalid': sum(pred(c, arm) is None for c in cases), 'by_condition': {condition: fraction([pred(c, arm) == c['label'] for c in cases if c['condition'] == condition]) for condition in sorted({c['condition'] for c in cases})}}
    parents = sorted({c['material_id'] for c in cases})
    deltas = [np.mean([int(pred(c, 'split') == c['label']) - int(pred(c, 'huber') == c['label']) for c in cases if c['material_id'] == mid]) for mid in parents]
    rng = np.random.default_rng(SEED)
    boot = np.mean(rng.choice(deltas, size=(20000, len(parents)), replace=True), axis=1) * 100
    metrics['primary_contrast'] = {'difference_pp': float(np.mean(deltas) * 100), 'descriptive_parent_bootstrap_95': np.quantile(boot, [.025, .975]).tolist(), 'split_correct_huber_wrong': sum(pred(c, 'split') == c['label'] and pred(c, 'huber') != c['label'] for c in cases), 'huber_correct_split_wrong': sum(pred(c, 'huber') == c['label'] and pred(c, 'split') != c['label'] for c in cases), 'parents': 7}
    metrics['coordinate_rmsd_mA'] = {arm: float(np.mean([c['coordinate_rmsd'][arm] for c in cases]) * 1000) for arm in ['huber', 'split']}
    metrics['algorithm_labels'] = {arm: fraction([c['algorithm_labels'][arm] == c['label'] for c in cases]) for arm in ['huber', 'split']}
    study['metrics'] = metrics
    study['status'] = 'COMPLETE'
    study['verification']['response_parser_rechecked'] = len(study['responses'])
    write(study)
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'score'])
    args = parser.parse_args()
    globals()[args.action]()

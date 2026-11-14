import argparse
import copy
import gc
import hashlib
import json
import os
from pathlib import Path
import statistics
import time

from render_ceiling.coordinate_handoff_inputs import ROOT, MODEL, digest, filehash, parse

ARMS = ['lattice', 'huber', 'split']
SEEDS = [20261029, 20261030, 20261031]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def prepare(path, model):
    assert not path.exists()
    cases, requests, sources = [], {}, {}
    for name in ['reconstruction_sonnet_pilot', 'reconstruction_sonnet_extension']:
        src = ROOT / 'results' / name / 'study.json'
        sources[str(src.relative_to(ROOT))] = filehash(src)
        old = json.loads(src.read_text())
        for c in old['cases']:
            c = copy.deepcopy(c)
            c['requests'] = {a: c['requests'][a] for a in ARMS}
            cases.append(c)
        for q in old['requests']:
            requests[q['request_id']] = q
    used = {rid for c in cases for rid in c['requests'].values()}
    requests = [requests[rid] for rid in sorted(used)]
    assert len(cases) == len({c['case_id'] for c in cases}) == 112
    assert len({c['material_id'] for c in cases}) == 28
    for q in requests:
        assert hashlib.sha256(q['prompt'].encode()).hexdigest() == q['request_id']
    protocol = {'arms': ARMS, 'seeds': SEEDS, 'generation': {'temperature': 1.0, 'top_p': .95, 'top_k': 64, 'max_tokens': 256}, 'model_path': str(model), 'model_revision': model.name, 'model_files_sha256': {p.name: filehash(p) for p in model.iterdir() if p.is_file()}, 'source_hashes': sources, 'runner_sha256': filehash(__file__), 'requests_hash': digest(requests), 'cases_hash': digest(cases), 'sampling': 'Each prompt starts with the same explicit seed for its replicate; three fixed seeds, fresh KV cache. Identical prompts share one response within each seed.', 'primary': 'Accuracy on all 112 cases per seed; arithmetic mean and sample standard deviation across three seeds. Seeds are repeated measurements of the same cases, not independent datasets.', 'targets': 'Frozen prompt-matched targets from Sonnet studies, including two mp-865981 large cases labeled monoclinic at 0.02 angstrom. Archived labels retained.', 'parser': 'Existing frozen ANSWER parser; invalid or truncated output is incorrect; no correctness retries.', 'selection': 'All 28 existing heldout parents, both variants and both conditions; no selection by model outcome.', 'comparison': 'Sampling experiment; distinct from preserved 28-case greedy Gemma pilot.'}
    save(path, {'protocol': protocol, 'protocol_hash': digest(protocol), 'cases': cases, 'requests': requests, 'responses': {}, 'verification': {}, 'status': 'PREPARED'})
    print(json.dumps({'cases': len(cases), 'unique_prompts': len(requests), 'generations': len(requests) * 3}))


def validate(s, check_model=True):
    p = s['protocol']
    assert digest(p) == s['protocol_hash']
    assert digest(s['cases']) == p['cases_hash']
    assert digest(s['requests']) == p['requests_hash']
    for src, h in p['source_hashes'].items():
        assert filehash(ROOT / src) == h
    if check_model:
        for name, h in p['model_files_sha256'].items():
            assert filehash(Path(p['model_path']) / name) == h


def run(path, limit):
    for key in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_DATASETS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY']:
        os.environ[key] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    import ctypes
    from importlib.metadata import distributions
    check = ctypes.CDLL('/usr/lib/libSystem.B.dylib').sandbox_check
    check.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    check.restype = ctypes.c_int
    assert check(os.getpid(), b'network-outbound', 0) == 1
    import mlx.core as mx
    from mlx_vlm import load, generate, prepare_inputs
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import should_add_special_tokens
    s = json.loads(path.read_text())
    validate(s)
    p = s['protocol']
    mx.set_memory_limit(18_000_000_000)
    mx.set_cache_limit(512_000_000)
    model, processor = load(p['model_path'], trust_remote_code=False)
    tokenizer = getattr(processor, 'tokenizer', processor)
    prepared = {}
    for q in s['requests']:
        formatted = apply_chat_template(processor, model.config, q['prompt'], num_images=0)
        inputs = prepare_inputs(processor, images=None, prompts=formatted, add_special_tokens=should_add_special_tokens(model.config.model_type, processor), pad_to_uniform_size=False)
        ids = inputs['input_ids'][0].tolist()
        decoded = tokenizer.decode(ids, skip_special_tokens=False)
        assert q['prompt'] in decoded, q['request_id']
        assert len(ids) + p['generation']['max_tokens'] < 32768
        prepared[q['request_id']] = (formatted, len(ids), digest(ids))
    s['verification']['complete_prompt_token_delivery'] = len(prepared)
    s['runtime'] = {'environment': sorted(f'{d.metadata["Name"]}=={d.version}' for d in distributions()), 'device': mx.device_info(), 'network_denied': True}
    s['status'] = 'RUNNING'
    save(path, s)
    count = 0
    for q in s['requests']:
        rid = q['request_id']
        for seed in p['seeds']:
            key = f'{seed}:{rid}'
            if key in s['responses']:
                continue
            mx.random.seed(seed)
            gc.collect()
            mx.clear_cache()
            mx.reset_peak_memory()
            formatted, n, ih = prepared[rid]
            inputs = prepare_inputs(processor, images=None, prompts=formatted, add_special_tokens=should_add_special_tokens(model.config.model_type, processor), pad_to_uniform_size=False)
            kwargs = {k: v for k, v in inputs.items() if k != 'attention_mask'}
            kwargs['mask'] = inputs.get('attention_mask')
            start = time.monotonic()
            result = generate(model, processor, formatted, seed=seed, **p['generation'], prefill_step_size=512, verbose=False, **kwargs)
            mx.synchronize()
            assert result.cached_tokens == 0 and result.prompt_tokens == n
            s['responses'][key] = {'request_id': rid, 'seed': seed, 'raw_output': result.text, 'prediction': parse(result.text), 'prompt_tokens': n, 'input_ids_sha256': ih, 'generation_tokens': result.generation_tokens, 'finish_reason': result.finish_reason, 'truncated': result.generation_tokens >= p['generation']['max_tokens'] or result.finish_reason == 'length', 'seconds': time.monotonic() - start, 'metal_peak_bytes': mx.get_peak_memory()}
            save(path, s)
            print(f'{len(s["responses"])}/{len(s["requests"])*3} seed={seed} tokens={n} output={result.text!r}', flush=True)
            del inputs, kwargs, result
            count += 1
            if limit and count >= limit:
                return
    s['status'] = 'INFERENCE_COMPLETE'
    save(path, s)


def score(path):
    s = json.loads(path.read_text())
    validate(s, check_model=False)
    p = s['protocol']
    assert len(s['responses']) == len(s['requests']) * len(SEEDS)
    for r in s['responses'].values():
        assert parse(r['raw_output']) == r['prediction']
    scores = {}
    for arm in ARMS:
        counts = []
        for seed in SEEDS:
            flags = []
            for c in s['cases']:
                r = s['responses'][f'{seed}:{c["requests"][arm]}']
                flags.append(not r['truncated'] and r['prediction'] == c['label'])
            counts.append(sum(flags))
        scores[arm] = {'correct_per_seed': counts, 'n_per_seed': 112, 'mean_percent': statistics.mean(counts) / 112 * 100, 'sample_sd_pp': statistics.stdev(counts) / 112 * 100}
    s['scores'] = scores
    s['verification']['parser_rechecked'] = len(s['responses'])
    s['status'] = 'COMPLETE'
    save(path, s)
    print(json.dumps(scores, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'score'])
    parser.add_argument('--name', default='gemma')
    parser.add_argument('--model', type=Path, default=MODEL)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    output = ROOT / 'results' / f'reconstruction_{args.name}_three_seed' / 'study.json'
    if args.action == 'prepare':
        prepare(output, args.model)
    elif args.action == 'run':
        run(output, args.limit)
    else:
        score(output)

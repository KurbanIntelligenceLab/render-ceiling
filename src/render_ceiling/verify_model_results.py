import collections
import hashlib
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
SYSTEMS = ['cubic', 'hexagonal', 'monoclinic', 'orthorhombic', 'tetragonal', 'triclinic', 'trigonal']


def load(path):
    return json.loads((ROOT / path).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def answer(response):
    return '\n'.join(b.get('text', '') for b in response.get('content', []) if b.get('type') == 'text')


def parse_handoff(text):
    hits = [p.lower() for p in re.findall(r'ANSWER:\s*([A-Za-z]+)', text, re.I) if p.lower() in SYSTEMS]
    clean = text.strip().lower().strip('.*` \n')
    return hits[0] if len(hits) == 1 else clean if clean in SYSTEMS else None


def majority(values):
    valid = [v for v in values if v is not None]
    return collections.Counter(valid).most_common(1)[0][0] if valid else None


def check_inputs(state):
    requests = {q['request_id']: q['prompt'] for q in state['requests']}
    for rid, text in requests.items():
        assert hashlib.sha256(text.encode()).hexdigest() == rid
    p = state['protocol']
    assert digest(p) == state['protocol_hash']
    assert digest(state['cases']) == p['cases_hash']
    assert digest(state['requests']) == p['requests_hash']
    for path, expected in p.get('source_hashes', {}).items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    return requests


def verify_frontier():
    output = {}
    cohort = [json.loads(s) for s in (ROOT / 'data/primary/eval.jsonl').read_text().splitlines()]
    truth = {r['material_id']: r['crystal_system'] for r in cohort}
    for tag in ['sonnet55', 'opus55', 'fable51']:
        folder = f'results/geometry_substitution/{tag}/full'
        d, s = load(folder + '/run.json'), load(folder + '/summary.json')
        assert len(d['records']) == 1260 and not d.get('inflight')
        assert hashlib.sha256((ROOT / folder / 'run.json').read_bytes()).hexdigest() == s['run_sha256']
        bykey = {(r['material_id'], r['arm'], r['repeat']): r for r in d['records']}
        assert len(bykey) == 1260
        for r in load(f'results/geometry_substitution/{tag}/pilot/run.json')['records']:
            assert bykey[r['material_id'], r['arm'], r['repeat']] == r
        guesses = {}
        cost = 0
        rates = {'input_tokens': 2 if tag == 'sonnet55' else 4 if tag == 'opus55' else 10,
                 'output_tokens': 10 if tag == 'sonnet55' else 20 if tag == 'opus55' else 50,
                 'cache_creation_input_tokens': 2.5 if tag == 'sonnet55' else 5 if tag == 'opus55' else 12.5,
                 'cache_read_input_tokens': .1 if tag == 'sonnet55' else .2 if tag == 'opus55' else .25}
        for r in d['records']:
            response = r['response']
            assert response['stop_reason'] in ['end_turn', 'refusal'] and 'error' not in response
            hits = [(answer(response).lower().rfind(v), v) for v in SYSTEMS if v in answer(response).lower()]
            pred = max(hits)[1] if hits else None
            assert pred == r['prediction']
            for attempt in r.get('previous_attempts', []) + [response]:
                cost += sum(attempt.get('usage', {}).get(k, 0) * v for k, v in rates.items()) / 1e6
        assert abs(cost - s['estimated_cost_usd']) < 1e-7
        for mid in truth:
            guesses[mid] = {}
            for arm in ['image', 'text']:
                rs = [bykey[mid, arm, i] for i in range(3)]
                guesses[mid][arm] = majority([r['prediction'] if r['response']['stop_reason'] == 'end_turn' else None for r in rs])
        image = sum(g['image'] == truth[mid] for mid, g in guesses.items())
        text = sum(g['text'] == truth[mid] for mid, g in guesses.items())
        corrected = sum(g['image'] != truth[mid] and g['text'] == truth[mid] for mid, g in guesses.items())
        regressed = sum(g['image'] == truth[mid] and g['text'] != truth[mid] for mid, g in guesses.items())
        assert [image, text, corrected, regressed] == [s[k] for k in ['image_correct', 'text_correct', 'corrected', 'newly_wrong']]
        assert s['both_correct'] == image - regressed
        assert s['both_wrong'] == 210 - image - corrected
        assert abs(s['image_accuracy_percent'] - image / 210 * 100) < 1e-10
        assert abs(s['text_accuracy_percent'] - text / 210 * 100) < 1e-10
        assert abs(s['net_gain_percentage_points'] - (text - image) / 210 * 100) < 1e-10
        assert abs(s['closed_deficit_percent'] - (text - image) / (210 - image) * 100) < 1e-10
        for label, values in s['per_class'].items():
            for arm in ['image', 'text']:
                assert values[arm] == sum(g[arm] == truth[mid] for mid, g in guesses.items() if truth[mid] == label)
        for case in s['cases']:
            assert all(case[arm]['pred'] == guesses[case['material_id']][arm] for arm in ['image', 'text'])
        for arm in ['image', 'text']:
            predictions = load(folder + '/' + arm + '_predictions.json')['predictions']
            assert {c['material_id']: c['pred'] for c in predictions} == {mid: g[arm] for mid, g in guesses.items()}
        output[tag] = {'image': image, 'text': text, 'corrected': corrected, 'regressed': regressed, 'n': 210}
    return output



def verify_paired_outcomes():
    record = load('results/geometry_substitution/paired_geometry_outcomes.json')
    sources = {}
    for path, expected in record['input_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
        if path.startswith('release/predictions/'):
            data = load(path)
            arm = 'text' if Path(path).name.startswith('coords_as_text__') else 'image'
            sources.setdefault(data['model'], {})[arm] = data['predictions']
    assert len(record['rows']) == 17
    for row in record['rows']:
        if 'source' in row:
            source = load(row['source'])
            actual = [source[k] for k in ['image_correct', 'text_correct', 'corrected', 'newly_wrong']]
        else:
            arms = sources[row['model']]
            image = {c['material_id']: c for c in arms['image']}
            text = {c['material_id']: c for c in arms['text']}
            assert set(image) == set(text) and len(image) == 210
            assert all(image[mid]['truth'] == text[mid]['truth'] for mid in image)
            pairs = [(image[mid]['pred'] == image[mid]['truth'], text[mid]['pred'] == text[mid]['truth']) for mid in image]
            actual = [sum(a for a, b in pairs), sum(b for a, b in pairs), sum(not a and b for a, b in pairs), sum(a and not b for a, b in pairs)]
        assert actual == [row[k] for k in ['k4', 'k3', 'g', 'l']]
        assert row['counts'] == [row['k4'] - row['l'], row['g'], row['l'], 210 - row['k4'] - row['g']]
        assert abs(100 * (row['k3'] - row['k4']) / (210 - row['k4']) - row['closed_pct']) < 1e-10
    return {'models': len(record['rows']), 'matched_counts_and_source_checksums': 'PASS'}


def verify_handoff():
    summary = load('results/coordinate_handoff/coordinate_handoff_accuracy.json')
    for path, expected in summary['source_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    groups, cases = {}, []
    for name in ['reconstruction_sonnet_pilot', 'reconstruction_sonnet_extension']:
        d = load(f'results/{name}/study.json')
        check_inputs(d)
        cases += d['cases']
        for r in d['records']:
            pred = parse_handoff(answer(r['response'])) if r['response'].get('stop_reason') == 'end_turn' else None
            assert pred == r['prediction']
            assert r['repeat'] not in groups.setdefault(r['request_id'], {})
            groups[r['request_id']][r['repeat']] = pred
    assert len(cases) == len({c['case_id'] for c in cases}) == 112
    assert len({c['material_id'] for c in cases}) == 28
    output = {}
    for model, tag in [('Sonnet 5.5', 'sonnet'), ('Gemma 3 4B IT', 'gemma'), ('Qwen3 4B', 'qwen')]:
        if tag != 'sonnet':
            d = load(f'results/reconstruction_{tag}_three_seed/study.json')
            check_inputs(d)
            assert [c['case_id'] for c in d['cases']] == [c['case_id'] for c in cases]
            for local, source in zip(d['cases'], cases):
                assert local == {**source, 'requests': {arm: source['requests'][arm] for arm in ['lattice', 'huber', 'split']}}
            for response in d['responses'].values():
                assert parse_handoff(response['raw_output']) == response['prediction']
        counts = {}
        for arm in ['lattice', 'huber', 'split']:
            if tag == 'sonnet':
                values = [sum(groups[c['requests'][arm]][i] == c['label'] for c in cases) for i in range(3)]
                vote = sum(majority([groups[c['requests'][arm]][i] for i in range(3)]) == c['label'] for c in cases)
                assert vote == summary['sonnet_majority_counts'][arm]
            else:
                values = [sum(not d['responses'][f'{seed}:{c["requests"][arm]}']['truncated'] and d['responses'][f'{seed}:{c["requests"][arm]}']['prediction'] == c['label'] for c in d['cases']) for seed in d['protocol']['seeds']]
            expected = summary['summary'][model][arm]
            assert values == expected['counts']
            assert abs(statistics.mean(values) / 112 * 100 - expected['mean_percent']) < 1e-10
            assert abs(statistics.stdev(values) / 112 * 100 - expected['sample_sd_pp']) < 1e-10
            counts[arm] = values
        output[model] = counts
    return output


if __name__ == '__main__':
    print(json.dumps({'status': 'PASS', 'frontier': verify_frontier(), 'paired_outcomes': verify_paired_outcomes(), 'handoff': verify_handoff()}, indent=2))

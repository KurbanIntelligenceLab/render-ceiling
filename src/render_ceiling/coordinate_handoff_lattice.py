from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile

from render_ceiling import coordinate_handoff_extension as E


def main():
    s = json.loads(E.OUT.read_text())
    E.check(s)
    assert s['status'] == 'INFERENCE_COMPLETE'
    assert s['protocol']['arms'] == ['huber', 'split']
    assert not s['parallel_pending'] and s['uncertain_charge_reserve_usd'] == 0
    old_protocol = deepcopy(s['protocol'])
    old_hash = s['protocol_hash']
    qmap = {q['request_id']: q for q in s['requests']}
    new_ids = set()
    for c in s['cases']:
        q = qmap[c['requests']['huber']]
        prefix, raw = q['prompt'].split('\n', 1)
        g = json.loads(raw)
        content = {'lattice_rows_angstrom': g['lattice_rows_angstrom']}
        prompt = prefix + '\n' + json.dumps(content, separators=(',', ':'))
        rid = E.hashlib.sha256(prompt.encode()).hexdigest()
        qmap.setdefault(rid, {'request_id': rid, 'prompt': prompt})
        new_ids.add(rid)
        c['requests']['lattice'] = rid
        other = json.loads(qmap[c['requests']['split']]['prompt'].split('\n', 1)[1])
        assert content['lattice_rows_angstrom'] == other['lattice_rows_angstrom']
    assert len(new_ids) == 21
    for mid in s['protocol']['parent_order']:
        assert len({c['requests']['lattice'] for c in s['cases'] if c['material_id'] == mid}) == 1
    s['requests'] = sorted(qmap.values(), key=lambda q: E.S.digest([E.SEED, q['request_id']]))
    p = s['protocol']
    p['arms'] = ['huber', 'split', 'lattice']
    p['controls'] = 'User requested lattice-only during the two-reconstruction run; add all 21 parent lattices, same wording and three-response vote; no new exact-coordinate calls. Original exact controls retained.'
    p['source_hashes'][str(Path(__file__).relative_to(E.ROOT))] = E.filehash(__file__)
    p['requests_hash'] = E.S.digest(s['requests'])
    p['cases_hash'] = E.S.digest(s['cases'])
    s.setdefault('protocol_history', []).append({'protocol': old_protocol, 'protocol_hash': old_hash, 'reason': 'User requested lattice-only arm during reconstruction inference, without reference to observed extension scores', 'records_completed_before_lattice': len(s['records']), 'extension_cost_before_lattice_usd': s['reported_cost_usd']})
    s['protocol_hash'] = E.S.digest(p)
    s['status'] = 'PREPARED_LATTICE'
    s['verification']['lattice_input_audit'] = {'parent_lattices': 21, 'case_mappings': 84, 'same_lattice_as_both_reconstructions': True, 'no_target_metadata': True}
    real_out, real_request, real_check = E.OUT, E.S.request, E.check
    base = deepcopy(s)
    base['preflight'].update({rid: {'input_tokens': 300} for rid in new_ids})
    calls = []
    def response(endpoint, payload):
        assert endpoint == 'messages'
        calls.append(payload)
        assert set(json.loads(payload['messages'][0]['content'][0]['text'].split('\n', 1)[1])) == {'lattice_rows_angstrom'}
        return {'model': E.S.MODEL, 'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': 'ANSWER: cubic'}], 'usage': {'input_tokens': 300, 'output_tokens': 10}}
    try:
        with tempfile.TemporaryDirectory() as directory:
            E.OUT = Path(directory) / 'study.json'
            E.check = lambda s: None
            E.S.request = response
            E.save(base)
            with redirect_stdout(io.StringIO()):
                E.run()
            mock = json.loads(E.OUT.read_text())
            assert mock['status'] == 'INFERENCE_COMPLETE' and len(calls) == 63
            assert len(mock['records']) == len(s['records']) + 63
    finally:
        E.OUT, E.S.request, E.check = real_out, real_request, real_check
    s['verification']['lattice_mock_audit'] = 'PASS; exactly 63 additional calls and no reconstruction reruns'
    E.save(s)
    print(json.dumps({'status': s['status'], 'new_inputs': 21, 'new_calls': 63, 'new_paid_calls_so_far': 0}))


if __name__ == '__main__':
    main()

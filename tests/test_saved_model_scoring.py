import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('model', ['gemma', 'qwen'])
def test_saved_answers_score_without_model_weights(model, tmp_path):
    module = importlib.import_module(f'render_ceiling.coordinate_handoff_{model}')
    source = ROOT / f'results/reconstruction_{model}_three_seed/study.json'
    original = json.loads(source.read_text())
    path = tmp_path / 'study.json'
    original['protocol']['model_path'] = str(tmp_path / 'missing-model')
    original['protocol_hash'] = module.digest(original['protocol'])
    path.write_text(json.dumps(original))
    module.score(path)
    result = json.loads(path.read_text())
    assert result['scores'] == original['scores']
    assert result['responses'] == original['responses']
    assert result['cases'] == original['cases']


@pytest.mark.parametrize('model', ['gemma', 'qwen'])
def test_saved_answer_scoring_still_rejects_changed_prompts(model, tmp_path):
    module = importlib.import_module(f'render_ceiling.coordinate_handoff_{model}')
    state = json.loads((ROOT / f'results/reconstruction_{model}_three_seed/study.json').read_text())
    state['requests'][0]['prompt'] += ' changed'
    path = tmp_path / 'study.json'
    path.write_text(json.dumps(state))
    before = path.read_bytes()
    with pytest.raises(AssertionError):
        module.score(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize('model', ['gemma', 'qwen'])
def test_inference_validation_requires_model_files(model, tmp_path):
    module = importlib.import_module(f'render_ceiling.coordinate_handoff_{model}')
    state = json.loads((ROOT / f'results/reconstruction_{model}_three_seed/study.json').read_text())
    state['protocol']['model_path'] = str(tmp_path / 'missing-model')
    state['protocol_hash'] = module.digest(state['protocol'])
    with pytest.raises(FileNotFoundError):
        module.validate(state)

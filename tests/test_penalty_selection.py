from copy import deepcopy

from render_ceiling import penalty_selection as S


def fixture(values):
    return {
        "outputs": {name: {"parent_hypothesis": "cubic"} for name in values},
        "folds": [
            {f"cubic:{name}": {"loss": losses[i]} for name, losses in values.items()}
            for i in range(5)
        ],
    }


def test_equal_risk_prefers_fixed_four_and_null():
    r = fixture({name: [1] * 5 for name in ["split_2", "split_3", "split_4", "observation_only"]})
    assert S.choose(r)["selected"] == {
        "fixed_4": "split_4",
        "paired_1se": "split_4",
        "null_guard_1se": "observation_only",
    }


def test_clear_improvement_keeps_physical_departure():
    r = fixture(
        {"split_2": [1] * 5, "split_3": [2] * 5, "split_4": [3] * 5, "observation_only": [4] * 5}
    )
    assert S.choose(r)["selected"]["paired_1se"] == "split_2"
    assert S.choose(r)["selected"]["null_guard_1se"] == "split_2"


def test_small_variable_gain_prefers_stronger_penalty():
    r = fixture(
        {
            "split_2": [2] * 5,
            "split_3": [2] * 5,
            "split_4": [1, 1, 2, 3, 3.1],
            "observation_only": [4] * 5,
        }
    )
    assert S.choose(r)["minimum_config"] == "split_3"
    assert S.choose(r)["selected"]["paired_1se"] == "split_4"


def test_choices_do_not_use_target_fields_and_do_not_mutate_fit():
    r = fixture(
        {"split_2": [1] * 5, "split_3": [2] * 5, "split_4": [3] * 5, "observation_only": [4] * 5}
    )
    before = deepcopy(r)
    a = S.choose(r)
    assert r == before
    r.update(label="made-up", sigma=123, variant="original", material_id="irrelevant")
    assert S.choose(r) == a

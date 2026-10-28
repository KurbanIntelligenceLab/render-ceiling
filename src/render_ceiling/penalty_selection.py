import numpy as np

NAMES = ("fixed_4", "paired_1se", "null_guard_1se")


def losses(result, config):
    output = result["outputs"][config]
    key = output["parent_hypothesis"] + ":" + config
    values = np.asarray([fold[key]["loss"] for fold in result["folds"]], dtype=float)
    assert values.shape == (5,) and np.isfinite(values).all()
    return values


def paired_difference(a, b):
    delta = np.asarray(a) - np.asarray(b)
    return float(delta.mean()), float(delta.std(ddof=1) / np.sqrt(len(delta)))


def choose(result):
    configs = ["split_2", "split_3", "split_4"]
    ls = {name: losses(result, name) for name in configs + ["observation_only"]}
    best = min(configs, key=lambda name: (round(float(ls[name].sum()), 14), -int(name[-1])))
    differences = {name: paired_difference(ls[name], ls[best]) for name in configs}
    eligible = [name for name in configs if differences[name][0] <= differences[name][1] + 1e-14]
    conservative = max(eligible, key=lambda name: int(name[-1]))
    gain, se = paired_difference(ls["observation_only"], ls[conservative])
    guarded = conservative if gain > se + 1e-14 else "observation_only"
    return {
        "selected": {"fixed_4": "split_4", "paired_1se": conservative, "null_guard_1se": guarded},
        "minimum_config": best,
        "paired_excess_loss": differences,
        "null_improvement": gain,
        "null_paired_se": se,
    }


def attach(record):
    decision = choose(record["result"])
    for name, config in decision["selected"].items():
        record["predictions"][name] = record["predictions"][config]
        record["geometry"][name] = record["geometry"][config]
    record["selector"] = decision
    return record

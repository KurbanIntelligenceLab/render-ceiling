#!/usr/bin/env python
"""
E8: train ALIGNN for 7-way crystal-system classification on COCR's EXACT labels and split.

This is the fair-comparison row the external_baselines literature finding demanded: the published ALIGNN
number (75.6% crystal system, DeepCrysTet Table II) is on a different dataset with a random
split, so it is not comparable to our composition-exclusion result. This trains ALIGNN on
data/e3's own train/eval material_ids with the same spglib labels.

Runs in the /root/work/gnnenv venv on the GPU box (ALIGNN 2026.5.20 + torch 2.13).

Key correctness requirements:
  - keep_data_order=True and explicit n_train/n_val/n_test so OUR split assignment is preserved
    (ALIGNN would otherwise re-split randomly and leak eval structures into training).
  - classification over the 7 crystal systems, not regression.
  - the eval set must be exactly the 210 composition-exclusion ids, scored once at the end.

Usage (on the box):
  /root/work/gnnenv/bin/python scripts/train_alignn_e8.py --epochs 100 --out alignn_e8
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

SYSTEMS = ["cubic", "hexagonal", "monoclinic", "orthorhombic",
           "tetragonal", "triclinic", "trigonal"]


def build_dataset(data_dir: Path, structures: dict, sidecar: dict) -> tuple[list, int, int, int]:
    """Return ALIGNN-format records ordered train, val, test so keep_data_order works.

    ALIGNN consumes [{"atoms": <jarvis atoms dict>, "prop": <label>, "jid": <id>}, ...].
    The ORDER is load-bearing: with keep_data_order=True it slices the list by
    n_train / n_val / n_test, so our split must be laid out contiguously.
    """
    # jarvis-tools reads CIF natively, so this venv needs no pymatgen.
    import tempfile

    from jarvis.core.atoms import Atoms

    def rows(split: str) -> list[dict]:
        out = []
        for line in open(data_dir / f"{split}.jsonl"):
            r = json.loads(line)
            mid = r["material_id"]
            cif = structures.get(mid)
            if cif is None:
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".cif", delete=False) as fh:
                fh.write(cif["cif"])
                tmp = fh.name
            try:
                atoms = Atoms.from_cif(tmp, use_cif2cell=False)
            except Exception as exc:  # a CIF jarvis cannot parse is skipped, not guessed at
                print(f"[skip] {mid}: {type(exc).__name__} {exc}", flush=True)
                continue
            finally:
                os.unlink(tmp)
            # key must match TrainingConfig.target ("target"), not "prop"
            out.append({"atoms": atoms.to_dict(),
                        "target": SYSTEMS.index(sidecar[mid]["crystal_system"]),
                        "jid": mid})
        return out

    train = rows("train")
    test = rows("eval")
    # ALIGNN needs a val slice; carve it from the TAIL of train so eval is untouched.
    n_val = max(1, int(0.1 * len(train)))
    val = train[-n_val:]
    train = train[:-n_val]
    return train + val + test, len(train), len(val), len(test)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/e3")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--out", default="alignn_e8")
    args = ap.parse_args()

    dd = Path(args.data_dir)
    structures = json.load(open(dd / "structures.json"))
    sidecar = json.load(open(dd / "labels_sidecar.json"))
    dataset, n_tr, n_val, n_te = build_dataset(dd, structures, sidecar)
    print(f"[data] total={len(dataset)} train={n_tr} val={n_val} test={n_te}", flush=True)

    from alignn.config import TrainingConfig
    from alignn.train import train_dgl

    # NOTE on two enum constraints discovered from the live config schema:
    #  - `target` is a closed Literal of JARVIS property names; "target" is the generic slot
    #    for user data (our label lives in the record's "prop"/"target" field).
    #  - `criterion` offers only mse/l1/poisson/zig — there is no cross_entropy option, because
    #    ALIGNN's classification path selects its own loss when model.classification=True.
    #    So we set the flag on the MODEL and leave criterion at its default.
    cfg = TrainingConfig(
        dataset="user_data",
        target="target",
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        n_train=n_tr, n_val=n_val, n_test=n_te,
        keep_data_order=True,          # CRITICAL: preserve our split
        id_tag="jid",
        output_dir=args.out,
        random_seed=23,
        classification_threshold=None,
    )
    # 7-way classification head
    cfg.model.classification = True
    cfg.model.output_features = len(SYSTEMS)
    cfg.model.calculate_gradient = False
    cfg.model.grad_multiplier = 0
    cfg.model.gradwise_weight = 0.0
    cfg.model.energy_mult_natoms = False

    os.makedirs(args.out, exist_ok=True)

    # train_dgl only consults `config` when train_val_test_loaders is empty, and in that path it
    # calls get_train_val_loaders with dataset_array=None -> which tries to DOWNLOAD a JARVIS
    # database and dies with "Check DB name options." on a user dataset. Verified by reading the
    # source: `if not train_val_test_loaders: ... get_train_val_loaders(...) else: <use passed>`.
    # So build the loaders ourselves with dataset_array=<our records> and pass the 4-tuple in.
    from alignn.data import get_train_val_loaders

    loaders = get_train_val_loaders(
        dataset="user_data",
        dataset_array=dataset,
        target="target",
        n_train=n_tr, n_val=n_val, n_test=n_te,
        batch_size=args.batch_size,
        atom_features=cfg.atom_features,
        neighbor_strategy=cfg.neighbor_strategy,
        standardize=False,
        line_graph=True,
        id_tag="jid",
        keep_data_order=True,          # CRITICAL: our split order must be preserved
        classification_threshold=None,
        output_dir=args.out,
        cutoff=cfg.cutoff,
        max_neighbors=cfg.max_neighbors,
        workers=0,
        # use_lmdb=True is the SUPPORTED path. The non-LMDB branch is broken in this release:
        # get_train_val_loaders passes target_additional_output= to get_torch_dataset, but only
        # alignn.lmdb_dataset's variant accepts that kwarg (alignn.dataset's does not), so
        # use_lmdb=False raises TypeError. The library itself warns "not using LMDB might
        # result errors". Cache-staleness is handled by a per-run filename instead.
        use_lmdb=True,
        # `filename` is a PREFIX that the loader joins onto output_dir, so it must be a bare
        # name — passing a path here yields output_dir/output_dir/... and a FileNotFoundError.
        filename="cache_",
    )
    train_dgl(cfg, train_val_test_loaders=loaders)
    print("[train] done", flush=True)


if __name__ == "__main__":
    main()

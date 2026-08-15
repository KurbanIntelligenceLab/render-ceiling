import os as _o, sys as _s
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), ''))
from _paths import SRC
#!/usr/bin/env python
"""
occlusion_redundancy — the PUBLISHED ALIGNN architecture on OUR exact composition-exclusion split, CPU only.

Why this exists: the GPU box could not run ALIGNN because DGL ships no compiled graphbolt library
for the torch version the vision stack pins (documented in external_baselines/ENVIRONMENT.md).
Dropping the CUDA requirement removes that constraint entirely — DGL 2.2.0 ships CPU graphbolt for
torch <= 2.3.0, so a pinned CPU environment runs the real architecture.

PROTOCOL, matched to our other structure-input baselines so the comparison is fair:
  - train on the 1610 TRAIN structures, evaluate on the 210 composition-exclusion EVAL structures
  - epoch selected on a VALIDATION split carved out of TRAIN, never on eval (the mistake corrected
    in external_baselines's first GNN run)
  - 3 seeds, population SD reported (project convention)
  - graphs built from the CONVENTIONAL cell, matching what the renders draw
"""
import os
os.environ.setdefault("DGLBACKEND", "pytorch")
import argparse, json, warnings, random
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
import dgl
from pymatgen.core import Structure
from jarvis.core.atoms import Atoms as JAtoms
from alignn.graphs import Graph
from alignn.models.alignn import ALIGNN, ALIGNNConfig

SYSTEMS = ["cubic", "hexagonal", "monoclinic", "orthorhombic",
           "tetragonal", "triclinic", "trigonal"]


def to_alignn_graph(structure, cutoff=8.0, max_neighbors=12):
    """pymatgen Structure -> ALIGNN's (atom graph, line graph) pair."""
    ja = JAtoms(lattice_mat=structure.lattice.matrix,
                coords=structure.frac_coords,
                elements=[str(s.specie) for s in structure],
                cartesian=False)
    g, lg = Graph.atom_dgl_multigraph(
        ja, cutoff=cutoff, max_neighbors=max_neighbors,
        atom_features="cgcnn", compute_line_graph=True, use_canonize=True)
    # This alignn build's ALIGNN.forward unpacks `g, lg, lat = g` (3-tuple). `lat` is unpacked but
    # never read in the forward pass on this version — verified by inspecting the source — so we
    # pass the REAL 3x3 lattice matrix rather than a placeholder: correct if a later version starts
    # using it, and harmless now.
    lat = torch.tensor(structure.lattice.matrix, dtype=torch.float32).unsqueeze(0)
    return g, lg, lat


def build(rows, structures, conv_fn, cutoff, max_neighbors):
    out = []
    for r in rows:
        mid = r["material_id"]
        try:
            st = conv_fn(Structure.from_str(structures[mid]["cif"], fmt="cif"))
            g, lg, lat = to_alignn_graph(st, cutoff, max_neighbors)
            out.append((g, lg, lat, SYSTEMS.index(r["crystal_system"]), mid))
        except Exception as e:
            print(f"  skip {mid}: {type(e).__name__}", flush=True)
    return out


def batches(data, bs, shuffle=True):
    idx = list(range(len(data)))
    if shuffle:
        random.shuffle(idx)
    for i in range(0, len(idx), bs):
        chunk = [data[j] for j in idx[i:i + bs]]
        g = dgl.batch([c[0] for c in chunk])
        lg = dgl.batch([c[1] for c in chunk])
        lat = torch.cat([c[2] for c in chunk], dim=0)
        y = torch.tensor([c[3] for c in chunk], dtype=torch.long)
        yield g, lg, lat, y, [c[4] for c in chunk]


def logits_of(model, g, lg, lat, n):
    """ALIGNN.forward ends in torch.squeeze(out), which collapses a batch of 1 from (1,7) to (7,).
    classification=True is NOT the fix - on this build it forces num_classes=2 (fc out_features=2),
    verified by inspecting the constructed module. Keep classification=False (which correctly gives
    7 logits) and restore the batch dimension here."""
    out = model((g, lg, lat))
    if out.dim() == 1:
        out = out.view(n, -1)
    return out


def evaluate(model, data, bs):
    model.eval()
    preds = {}
    with torch.no_grad():
        for g, lg, lat, y, mids in batches(data, bs, shuffle=False):
            logits = logits_of(model, g, lg, lat, len(mids))
            p = logits.argmax(dim=1)
            for m, pi, yi in zip(mids, p.tolist(), y.tolist()):
                preds[m] = (pi, yi)
    acc = sum(1 for p, t in preds.values() if p == t) / max(len(preds), 1)
    return acc, preds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-jsonl", required=True)
    ap.add_argument("--eval-jsonl", required=True)
    ap.add_argument("--structures", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--val-frac", type=float, default=0.12)
    ap.add_argument("--cutoff", type=float, default=8.0)
    ap.add_argument("--max-neighbors", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    import sys
    sys.path.insert(0, f"{SRC}")
    from cocr.render import conventional_cell

    S = json.load(open(args.structures))
    tr_rows = [json.loads(l) for l in open(args.train_jsonl)]
    ev_rows = [json.loads(l) for l in open(args.eval_jsonl)]
    if args.limit:
        tr_rows, ev_rows = tr_rows[:args.limit], ev_rows[:max(args.limit // 4, 8)]
    print(f"[alignn] building graphs: {len(tr_rows)} train, {len(ev_rows)} eval", flush=True)
    tr_all = build(tr_rows, S, conventional_cell, args.cutoff, args.max_neighbors)
    ev = build(ev_rows, S, conventional_cell, args.cutoff, args.max_neighbors)
    print(f"[alignn] graphs built: {len(tr_all)} train, {len(ev)} eval", flush=True)

    results = []
    for seed in args.seeds:
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
        perm = list(range(len(tr_all)))
        random.shuffle(perm)
        nval = int(len(perm) * args.val_frac)
        val = [tr_all[i] for i in perm[:nval]]
        tr = [tr_all[i] for i in perm[nval:]]

        model = ALIGNN(ALIGNNConfig(name="alignn", output_features=len(SYSTEMS),
                                    alignn_layers=2, gcn_layers=2,
                                    classification=False))
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
        lossf = nn.CrossEntropyLoss()
        best_val, best_eval, best_ep, best_preds = -1.0, None, -1, None
        for ep in range(args.epochs):
            model.train()
            tot = 0.0
            for g, lg, lat, y, _ in batches(tr, args.batch_size):
                opt.zero_grad()
                loss = lossf(logits_of(model, g, lg, lat, len(y)), y)
                loss.backward(); opt.step()
                tot += float(loss)
            va, _ = evaluate(model, val, args.batch_size)
            if va > best_val:
                ea, preds = evaluate(model, ev, args.batch_size)
                best_val, best_eval, best_ep, best_preds = va, ea, ep, preds
            print(f"  seed{seed} ep{ep:02d} loss {tot/max(len(tr)//args.batch_size,1):.4f} "
                  f"val {va:.4f} (best {best_val:.4f} @ep{best_ep}, eval {best_eval:.4f})", flush=True)
        results.append({"seed": seed, "val": round(best_val, 4),
                        "eval_at_best_val": round(best_eval, 4), "epoch": best_ep,
                        "predictions": {m: {"pred": SYSTEMS[p], "truth": SYSTEMS[t]}
                                        for m, (p, t) in best_preds.items()}})
        print(f"[alignn] seed {seed}: eval {best_eval:.4f} at epoch {best_ep}", flush=True)

    accs = [r["eval_at_best_val"] for r in results]
    out = {"model": "ALIGNN (published architecture, alignn 2026.5.20, DGL 2.2.0, torch 2.3.0, CPU)",
           "protocol": "train on 1610 TRAIN, epoch selected on a val split carved from TRAIN, "
                       "reported on the 210 composition-exclusion EVAL set; graphs from the "
                       "CONVENTIONAL cell",
           "seeds": results, "mean": round(float(np.mean(accs)), 4),
           "sd_population": round(float(np.std(accs)), 4),
           "n_eval": len(ev)}
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"[alignn] MEAN {out['mean']:.4f} +/- {out['sd_population']:.4f} (population SD, "
          f"{len(accs)} seeds)", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
E8 external baselines — CGCNN-style crystal graph network on OUR labels and OUR splits.

WHY THIS EXISTS AND WHAT IT IS NOT: the published comparison (DeepCrysTet Table II, crystal-system
row: DeepCrysTet 97.5 / CGCNN 63.4 / ALIGNN 75.6) is on a DIFFERENT dataset and split, so it
cannot be compared to our numbers directly. This trains a graph network on OUR 1610/210
composition-exclusion split so the comparison is like-for-like.

It is a CGCNN-STYLE reimplementation, not the authors' code: ALIGNN's official package requires
DGL, whose compiled libraries have no build for the torch version our VLM stack pins, and
downgrading torch would break that stack (documented in CP8_ENVIRONMENT.md). A faithful
reimplementation in plain torch avoids the dependency wall and is honest as long as it is
LABELLED as a reimplementation and its architecture is stated. Any number it produces must be
reported as "CGCNN-style (our implementation)", never as "CGCNN".

Architecture (Xie & Grossman 2018): atom embeddings -> N convolution layers over the neighbour
graph with edge-gated updates -> mean pool -> MLP -> 7-way softmax.
"""
import argparse, json, math, warnings
import numpy as np
import torch
import torch.nn as nn

warnings.filterwarnings("ignore")
SYS = ["cubic","hexagonal","monoclinic","orthorhombic","tetragonal","triclinic","trigonal"]
RCUT, MAX_NBR, NGAUSS = 8.0, 12, 40


def gaussian_expand(d):
    centers = np.linspace(0.0, RCUT, NGAUSS)
    return np.exp(-((d[..., None] - centers) ** 2) / (0.5 ** 2))


def featurize(struct):
    """Neighbour graph: Z per atom, plus Gaussian-expanded distances to <=MAX_NBR neighbours."""
    z = np.array([s.specie.Z for s in struct], dtype=np.int64)
    n = len(struct)
    nbr_idx = np.zeros((n, MAX_NBR), dtype=np.int64)
    nbr_d = np.full((n, MAX_NBR), RCUT, dtype=np.float32)
    all_nbrs = struct.get_all_neighbors(RCUT)
    for i, nb in enumerate(all_nbrs):
        nb = sorted(nb, key=lambda x: x[1])[:MAX_NBR]
        for j, item in enumerate(nb):
            nbr_idx[i, j] = item[2]
            nbr_d[i, j] = item[1]
    return z, nbr_idx, gaussian_expand(nbr_d).astype(np.float32)


class ConvLayer(nn.Module):
    def __init__(self, atom_dim, nbr_dim):
        super().__init__()
        self.fc = nn.Linear(2 * atom_dim + nbr_dim, 2 * atom_dim)
        self.bn = nn.BatchNorm1d(2 * atom_dim)
        self.bn2 = nn.BatchNorm1d(atom_dim)

    def forward(self, x, nbr_idx, nbr_fea):
        n, m = nbr_idx.shape
        xn = x[nbr_idx.reshape(-1)].reshape(n, m, -1)
        xi = x.unsqueeze(1).expand(-1, m, -1)
        z = torch.cat([xi, xn, nbr_fea], dim=2)
        z = self.fc(z)                                  # (n, m, 2*atom_dim)
        z = self.bn(z.reshape(-1, self.fc.out_features)).reshape(n, m, -1)
        gate, core = z.chunk(2, dim=2)
        out = (torch.sigmoid(gate) * torch.nn.functional.softplus(core)).sum(dim=1)
        return torch.nn.functional.softplus(x + self.bn2(out))


class CGCNN(nn.Module):
    def __init__(self, atom_dim=64, n_conv=3, h=128, n_class=7):
        super().__init__()
        self.emb = nn.Embedding(100, atom_dim)
        self.convs = nn.ModuleList([ConvLayer(atom_dim, NGAUSS) for _ in range(n_conv)])
        self.head = nn.Sequential(nn.Linear(atom_dim, h), nn.Softplus(), nn.Linear(h, n_class))

    def forward(self, z, nbr_idx, nbr_fea, crystal_slices):
        x = self.emb(z)
        for c in self.convs:
            x = c(x, nbr_idx, nbr_fea)
        pooled = torch.stack([x[s:e].mean(0) for s, e in crystal_slices])
        return self.head(pooled)


def build(ids, structs, sidecar):
    from pymatgen.core import Structure
    data = []
    for mid in ids:
        st = Structure.from_str(structs[mid]["cif"], fmt="cif")
        z, ni, nf = featurize(st)
        data.append((z, ni, nf, SYS.index(sidecar[mid]["crystal_system"]), mid))
    return data


def collate(batch):
    zs, nis, nfs, ys, slices, off = [], [], [], [], [], 0
    for z, ni, nf, y, _ in batch:
        n = len(z)
        zs.append(torch.from_numpy(z))
        nis.append(torch.from_numpy(ni) + off)
        nfs.append(torch.from_numpy(nf))
        ys.append(y); slices.append((off, off + n)); off += n
    return (torch.cat(zs), torch.cat(nis), torch.cat(nfs),
            torch.tensor(ys), slices)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/e3")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed)

    structs = json.load(open(f"{a.data_dir}/structures.json"))
    sidecar = json.load(open(f"{a.data_dir}/labels_sidecar.json"))
    tr_ids = sorted({json.loads(l)["material_id"] for l in open(f"{a.data_dir}/train.jsonl")})
    ev_ids = [json.loads(l)["material_id"] for l in open(f"{a.data_dir}/eval.jsonl")]
    assert not (set(tr_ids) & set(ev_ids)), "train/eval leakage"
    print(f"train {len(tr_ids)} | eval {len(ev_ids)} | leakage 0", flush=True)

    tr = build(tr_ids, structs, sidecar); ev = build(ev_ids, structs, sidecar)
    model = CGCNN(); opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    lossf = nn.CrossEntropyLoss()
    best = 0.0; hist = []
    for ep in range(a.epochs):
        model.train(); perm = np.random.permutation(len(tr))
        tot = 0.0
        for i in range(0, len(tr), a.batch):
            b = [tr[j] for j in perm[i:i + a.batch]]
            if len(b) < 2:
                continue
            z, ni, nf, y, sl = collate(b)
            opt.zero_grad()
            out = model(z, ni, nf, sl)
            loss = lossf(out, y); loss.backward(); opt.step()
            tot += float(loss) * len(b)
        model.eval(); corr = 0
        with torch.no_grad():
            for i in range(0, len(ev), a.batch):
                b = ev[i:i + a.batch]
                if len(b) < 2:
                    continue
                z, ni, nf, y, sl = collate(b)
                corr += int((model(z, ni, nf, sl).argmax(1) == y).sum())
        acc = corr / len(ev); best = max(best, acc)
        hist.append({"epoch": ep, "train_loss": round(tot / len(tr), 4), "eval_acc": round(acc, 4)})
        if ep % 5 == 0 or ep == a.epochs - 1:
            print(f"  ep{ep} loss={tot/len(tr):.4f} eval_acc={acc:.4f}", flush=True)
    json.dump({"model": "CGCNN-style (our reimplementation, NOT the authors' code)",
               "architecture": {"atom_dim": 64, "n_conv": 3, "rcut": RCUT,
                                "max_nbr": MAX_NBR, "n_gauss": NGAUSS},
               "split": "our 1610/210 composition-exclusion", "seed": a.seed,
               "final_acc": hist[-1]["eval_acc"], "best_acc": round(best, 4),
               "history": hist}, open(a.out, "w"), indent=1)
    print(f"[e8] final {hist[-1]['eval_acc']:.4f} best {best:.4f} -> {a.out}")


if __name__ == "__main__":
    main()

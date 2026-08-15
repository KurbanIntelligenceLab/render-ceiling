#!/usr/bin/env python
"""
E1 — zero-shot symmetry-perception probe -> ledger/zeroshot/

Evaluates the open base model + frontier VLMs (via OpenRouter) zero-shot on four
tasks, sweeping view count {1,3,5}, on canonical AND contamination-control (perturbed
re-render) view sets. Writes incrementally to results.jsonl so a crash/interrupt loses
at most one query; the summary is aggregated in a separate step.

Usage:
  python run_e1_zeroshot.py --stage prepare --per-system 10   # build sample + renders
  python run_e1_zeroshot.py --stage query --models m1,m2      # run the probe (resumable)
"""
import argparse, json, os, sys, time, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import warnings; warnings.filterwarnings("ignore")

from collections import Counter
from cocr.data import fetch_mp_stratified, fetch_jarvis_stratified
from cocr.render import (render_views, conventional_cell, VIEW_SWEEP, VIEWS,
                         VIEWS_PERTURBED)
from cocr.labels import make_labels

LEDGER = os.path.join(os.path.dirname(__file__), "..", "ledger", "zeroshot")
RENDERS = os.path.join(os.path.dirname(__file__), "..", "data", "renders", "e1")
VIEW_COUNTS = [1, 3, 5]

MODELS = {
    "base":     "qwen/qwen3-vl-8b-instruct",
    "gpt":      "openai/gpt-5.6-terra-pro",
    "opus":     "anthropic/claude-opus-4.8",
    "grok":     "x-ai/grok-4.5",
    "gemini":   "google/gemini-3.6-flash",
}


def modal_coordination(coord):
    """Pick a representative element + its modal coordination number for the CN task.

    coord: list of per-site dicts with 'element' and 'coordination_number' (from
    cocr.labels._coordination on the conventional cell).
    """
    if not coord:
        return None, None
    by_el = {}
    for c in coord:
        by_el.setdefault(c["element"], []).append(c.get("coordination_number"))
    # choose the element whose CN is most consistent (mode fraction highest), tie -> most frequent element
    best = None
    for el, cns in by_el.items():
        cns = [x for x in cns if x is not None]
        if not cns:
            continue
        mode, mcount = Counter(cns).most_common(1)[0]
        frac = mcount / len(cns)
        score = (frac, len(cns))
        if best is None or score > best[0]:
            best = (score, el, mode)
    if best is None:
        return None, None
    return best[1], best[2]


def prepare(args):
    random.seed(args.seed)
    mp = fetch_mp_stratified(args.per_system, num_elements=(2, 4), num_sites=(2, 20))
    jv = fetch_jarvis_stratified(args.per_system, min_sites=2, max_sites=20)
    pool = mp + jv
    random.shuffle(pool)
    os.makedirs(RENDERS, exist_ok=True)
    os.makedirs(LEDGER, exist_ok=True)
    manifest = []
    per_sys_cap = args.per_system + 3
    seen = Counter()
    for rc in pool:
        try:
            conv = conventional_cell(rc["structure"])
            lab = make_labels(rc["structure"], rc["material_id"], rc["source"])
        except Exception:
            continue
        s = lab["crystal_system"]
        if seen[s] >= per_sys_cap:
            continue
        seen[s] += 1
        mid = rc["material_id"].replace("/", "_")
        # render canonical + perturbed at max (5) views; subsets index into these
        cdir = os.path.join(RENDERS, "canonical"); pdir = os.path.join(RENDERS, "perturbed")
        render_views(conv, cdir, mid, supercell=(2, 2, 2),
                     view_names=VIEW_SWEEP[5], view_map=VIEWS)
        render_views(conv, pdir, mid, supercell=(2, 2, 2),
                     view_names=VIEW_SWEEP[5], view_map=VIEWS_PERTURBED, radii=0.66)
        from cocr.labels import _coordination
        el, cn = modal_coordination(_coordination(conv))
        manifest.append({
            "material_id": rc["material_id"], "stem": mid, "source": rc["source"],
            "crystal_system": lab["crystal_system"],
            "space_group": lab["space_group"]["number"],
            "lattice_angles": [lab["lattice"]["alpha"], lab["lattice"]["beta"], lab["lattice"]["gamma"]],
            "cn_element": el, "cn_value": cn,
        })
        if len(manifest) >= args.n:
            break
    json.dump({"structures": manifest, "view_counts": VIEW_COUNTS,
               "n": len(manifest), "seed": args.seed,
               "dist": dict(Counter(m["crystal_system"] for m in manifest))},
              open(os.path.join(LEDGER, "sample.json"), "w"), indent=1)
    print(f"[prepare] {len(manifest)} structures, dist={dict(Counter(m['crystal_system'] for m in manifest))}")
    print(f"[prepare] renders in {RENDERS}/canonical and /perturbed")


def _do_one(job):
    """Execute one query job (thread worker). Returns the scored result record."""
    from cocr.zeroshot import (build_messages, query_openrouter, score_crystal_system,
                               score_lattice_angles, score_space_group_topk, score_coordination)
    mkey, model, st, style, subdir, nv = job
    views = VIEW_SWEEP[nv]
    task = st["_task"]
    imgs = [os.path.join(RENDERS, subdir, f"{st['stem']}_view{i}.png")
            for i in range(len(views))]
    kw = {"k": 5, "element": st["cn_element"] or "the metal"}
    msgs = build_messages(task, imgs, **kw)
    resp = query_openrouter(model, msgs, max_tokens=900)
    rec = {"model_key": mkey, "model": model, "stem": st["stem"],
           "material_id": st["material_id"], "source": st["source"],
           "crystal_system": st["crystal_system"], "task": task,
           "views": nv, "style": style, "ok": resp["ok"],
           "text": resp["text"], "usage": resp.get("usage", {})}
    if resp["ok"]:
        try:
            if task == "crystal_system":
                rec["correct"] = score_crystal_system(resp["text"], st["crystal_system"])
            elif task == "lattice_angles":
                rec["score"] = score_lattice_angles(resp["text"], tuple(st["lattice_angles"]))
            elif task == "space_group_topk":
                rec["score"] = score_space_group_topk(resp["text"], st["space_group"], k=5)
            elif task == "coordination":
                rec["score"] = score_coordination(resp["text"], st["cn_value"])
        except Exception as e:
            rec["ok"] = False
            rec["error"] = f"score_error: {type(e).__name__}: {str(e)[:100]}"
    else:
        rec["error"] = resp.get("error")
    return rec


def query(args):
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed
    sample = json.load(open(os.path.join(LEDGER, "sample.json")))
    structs = sample["structures"]
    models = {k: MODELS[k] for k in args.models.split(",")} if args.models else MODELS
    out_path = os.path.join(LEDGER, "results.jsonl")
    # resume: skip already-done (model,stem,task,views,style) keys
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            try:
                r = json.loads(line); done.add((r["model_key"], r["stem"], r["task"], r["views"], r["style"]))
            except Exception:
                pass
    # build the full independent-job list
    tasks_all = ["crystal_system", "lattice_angles", "space_group_topk", "coordination"]
    jobs = []
    for mkey, model in models.items():
        for st in structs:
            for style, subdir in [("canonical", "canonical"), ("perturbed", "perturbed")]:
                for nv in VIEW_COUNTS:
                    for task in tasks_all:
                        if task == "coordination" and not st["cn_element"]:
                            continue
                        if (mkey, st["stem"], task, nv, style) in done:
                            continue
                        sj = dict(st); sj["_task"] = task
                        jobs.append((mkey, model, sj, style, subdir, nv))
    print(f"[query] {len(structs)} structs x {len(models)} models; {len(done)} done, {len(jobs)} to run")
    lock = threading.Lock()
    f = open(out_path, "a")
    n_done = [0]
    t0 = time.time()

    def run(job):
        rec = _do_one(job)
        with lock:
            f.write(json.dumps(rec) + "\n"); f.flush()
            n_done[0] += 1
            if n_done[0] % 100 == 0:
                rate = n_done[0] / (time.time() - t0)
                print(f"  {n_done[0]}/{len(jobs)} ({rate:.1f}/s)", flush=True)
        return rec["ok"]

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        n_ok = sum(1 for fu in as_completed(futs) if fu.result())
    f.close()
    print(f"[query] wrote {len(jobs)} results ({n_ok} ok) in {time.time()-t0:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["prepare", "query"], required=True)
    ap.add_argument("--per-system", type=int, default=10)
    ap.add_argument("--n", type=int, default=70)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--models", default="")
    ap.add_argument("--workers", type=int, default=8,
                    help="concurrent OpenRouter requests (IO-bound; 8-16 is safe)")
    args = ap.parse_args()
    (prepare if args.stage == "prepare" else query)(args)


if __name__ == "__main__":
    main()

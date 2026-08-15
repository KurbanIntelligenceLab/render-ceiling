#!/usr/bin/env python
"""
frontier_ceiling — frontier ceiling on the EXACT 210-structure composition-exclusion eval set.

Protocol is deliberately identical to the trained arms (eval_e3.py): same structures, same frozen
5-view renders, same QUESTION prompt, majority vote over K samples, denominators FIXED at 210 with
parse failures scored as ERRORS. Reports micro, macro-F1 and per-crystal-system breakdown.

Runs each model on BOTH canonical and element-anonymized renders (the pre-registered contamination
control) when the anonymized renders are supplied.
"""
import argparse, base64, collections, json, math, os, re, time
import urllib.request, urllib.error

SYS = ["cubic","hexagonal","monoclinic","orthorhombic","tetragonal","triclinic","trigonal"]
API = "https://openrouter.ai/api/v1/chat/completions"


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def parse_system(text):
    """Last-mention fallback, same convention as the trained-arm scorer."""
    if not text:
        return None
    t = text.lower()
    hits = [(t.rfind(s), s) for s in SYS if s in t]
    hits = [(i, s) for i, s in hits if i >= 0]
    return max(hits)[1] if hits else None


NO_IMAGES = False   # no_image_control control switch, set from --no-images


def ask(model, question, image_paths, key, temperature, max_retries=4):
    content = [{"type": "text", "text": question}]
    if NO_IMAGES:
        image_paths = []          # byte-identical prompt text, image blocks removed
    for p in (image_paths or []):
        content.append({"type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64(p)}"}})
    body = {"model": model, "temperature": temperature,
            "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(max_retries):
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=180).read())
            return r["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < max_retries - 1:
                time.sleep(4 * (attempt + 1)); continue
            return f"__ERROR__ HTTP {e.code}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(4 * (attempt + 1)); continue
            return f"__ERROR__ {type(e).__name__}"
    return "__ERROR__ retries exhausted"


def macro_f1(pairs):
    f1s = []
    for s in SYS:
        tp = sum(1 for t, p in pairs if t == s and p == s)
        fp = sum(1 for t, p in pairs if t != s and p == s)
        fn = sum(1 for t, p in pairs if t == s and p != s)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    return sum(f1s) / len(f1s), {s: round(f, 4) for s, f in zip(SYS, f1s)}


def run(model, rows, render_dir, key, k, temperature, limit, workers=12):
    """Parallel over (structure, sample) pairs — independent API calls, no shared state.

    Serial execution is ~12.3 s/call, which is 12.9 h for the full 3-model matrix; the
    calls are independent so a bounded thread pool is the fix. Concurrency is capped
    because the constraint is provider rate limiting, and ask() keeps its own backoff.
    """
    from concurrent.futures import ThreadPoolExecutor

    rows = rows[:limit] if limit else rows
    jobs = []
    for ri, ex in enumerate(rows):
        imgs = [os.path.join(render_dir, os.path.basename(p)) for p in ex["images"]]
        imgs = [p for p in imgs if os.path.exists(p)]
        for _ in range(k):
            jobs.append((ri, ex, imgs))

    results = [None] * len(jobs)
    done = [0]

    def work(j):
        ji, (ri, ex, imgs) = j
        txt = ask(model, ex["question"], imgs, key, temperature)
        results[ji] = (ri, txt)
        done[0] += 1
        if done[0] % 100 == 0:
            print(f"    [{model}] {done[0]}/{len(jobs)} calls", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, list(enumerate(jobs))))

    by_row = collections.defaultdict(list)
    errs = 0
    for ri, txt in results:
        # ask() returns None when every retry is exhausted; treat that as an API error rather than
        # crashing the whole run. Previously this raised AttributeError and the model wrote NO output
        # file at all while the shell loop still reported DONE — a silent whole-arm loss.
        if txt is None or txt.startswith("__ERROR__"):
            errs += 1; continue
        by_row[ri].append(parse_system(txt))

    pairs, per, unparse = [], collections.defaultdict(lambda: [0, 0]), 0
    detail = []
    for ri, ex in enumerate(rows):
        good = [v for v in by_row.get(ri, []) if v]
        pred = collections.Counter(good).most_common(1)[0][0] if good else None
        if pred is None:
            unparse += 1                      # scored as an ERROR, never dropped
        truth = ex["crystal_system"]
        pairs.append((truth, pred))
        per[truth][1] += 1; per[truth][0] += (pred == truth)
        detail.append({"material_id": ex["material_id"], "truth": truth, "pred": pred,
                       "votes": dict(collections.Counter(good))})
    n = len(pairs)
    micro = sum(1 for t, p in pairs if t == p) / n
    mac, perf1 = macro_f1(pairs)
    return {"model": model, "n": n, "micro": round(micro, 4), "macro_f1": round(mac, 4),
            "per_system_f1": perf1,
            "per_system_acc": {s: f"{per[s][0]}/{per[s][1]}" for s in SYS},
            "unparseable_scored_as_error": unparse, "api_errors": errs,
            "k": k, "temperature": temperature, "predictions": detail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-jsonl", required=True)
    ap.add_argument("--renders", required=True, help="canonical render dir")
    ap.add_argument("--renders-anon", default=None, help="element-anonymized render dir")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--no-images", action="store_true",
                help="no_image_control control: send the byte-identical prompt with image blocks REMOVED")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    global NO_IMAGES
    NO_IMAGES = bool(getattr(a, 'no_images', False))
    key = os.environ["OPENROUTER_API_KEY"]
    rows = [json.loads(l) for l in open(a.eval_jsonl)]
    out = {"protocol": {"structures": len(rows), "k": a.k, "temperature": a.temperature,
                        "denominator": "fixed at n; parse failures scored as errors",
                        "renders": "frozen 5-view set, unchanged files"},
           "canonical": {}, "anonymized": {}}
    for m in a.models:
        print(f"[canonical] {m}", flush=True)
        out["canonical"][m] = run(m, rows, a.renders, key, a.k, a.temperature, a.limit, a.workers)
        r = out["canonical"][m]
        print(f"  -> micro {r['micro']} macro {r['macro_f1']} "
              f"unparseable {r['unparseable_scored_as_error']} api_errors {r['api_errors']}")
        json.dump(out, open(a.out, "w"), indent=1)          # write incrementally
        if a.renders_anon:
            print(f"[anonymized] {m}", flush=True)
            out["anonymized"][m] = run(m, rows, a.renders_anon, key, a.k, a.temperature, a.limit, a.workers)
            ra = out["anonymized"][m]
            print(f"  -> micro {ra['micro']} (canonical - anon = "
                  f"{round(r['micro'] - ra['micro'], 4)})")
            json.dump(out, open(a.out, "w"), indent=1)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()

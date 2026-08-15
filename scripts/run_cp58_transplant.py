"""perception_transplant arm A3 — strong model extracts, weak model reasons.

Two legs per structure. Leg 1: the strong model sees the five renders and emits ONLY species and
fractional coordinates, with the symmetry question withheld so it cannot leak an answer. Leg 2: the weak
model sees that text, no images, and answers the symmetry question with the frozen R3 wording.
"""
import os as _o, sys as _s
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), ''))
from _paths import ROOT
import json, os, re, sys, time, importlib.util
from concurrent.futures import ThreadPoolExecutor

ROOT = f"{ROOT}"
_s = importlib.util.spec_from_file_location("pf", f"{ROOT}/scripts/probe_frontier.py")
pf = importlib.util.module_from_spec(_s); _s.loader.exec_module(pf)

STRONG = "google/gemini-3.6-flash"
WEAK   = "meta-llama/llama-4-scout"

EXTRACT_PROMPT = (
    "You are shown standardized multi-view ball-and-stick renders of a crystal structure "
    "(principal-axis and oblique views of the conventional cell). Report ONLY the atoms you can see: "
    "for each atom give its chemical element and its fractional coordinates within the cell. "
    "Do NOT identify the crystal system, space group, or any symmetry property. "
    "Output one atom per line in exactly this format and nothing else:\n"
    "ELEMENT x y z\n"
    "for example:\n"
    "Ba 0.00000 0.50000 0.25000"
)

ANSWER_PROMPT = (
    "You are given the atoms of a crystal structure as text, extracted from images by another system. "
    "Identify the crystal system (one of: triclinic, monoclinic, orthorhombic, tetragonal, trigonal, "
    "hexagonal, cubic). Reason from the atomic arrangement given below."
)

ATOM = re.compile(r"^\s*([A-Z][a-z]?)\s+(-?\d*\.?\d+)\s+(-?\d*\.?\d+)\s+(-?\d*\.?\d+)\s*$")

def parse_atoms(txt):
    out = []
    for line in (txt or "").splitlines():
        m = ATOM.match(line.strip().lstrip("-*• ").replace(",", " "))
        if m:
            try: out.append((m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))))
            except ValueError: pass
    return out

def one(rec, key, k, temperature):
    mid = rec["material_id"]
    imgs = [os.path.join(ROOT, p) for p in rec["images"]]
    ex = pf.ask(STRONG, EXTRACT_PROMPT, imgs, key, temperature)
    if ex is None or (isinstance(ex, str) and ex.startswith("__ERROR__")):
        return {"material_id": mid, "truth": rec["crystal_system"], "extract_error": True}
    atoms = parse_atoms(ex)
    if not atoms:
        return {"material_id": mid, "truth": rec["crystal_system"], "n_atoms_emitted": 0,
                "unparseable_extraction": True, "raw_head": (ex or "")[:200]}
    body = "\n".join(f"  {a[0]} {a[1]:.5f} {a[2]:.5f} {a[3]:.5f}" for a in atoms)
    q = ANSWER_PROMPT + f"\n\nNumber of atoms reported: {len(atoms)}.\nAtoms (element x y z):\n" + body
    votes = []
    for _ in range(k):
        t = pf.ask(WEAK, q, [], key, temperature)
        c = pf.parse_claim(t) if hasattr(pf, "parse_claim") else None
        if c is None and t:
            for cs in ("triclinic","monoclinic","orthorhombic","tetragonal","trigonal","hexagonal","cubic"):
                if cs in t.lower(): c = cs
        if c: votes.append(c)
    pred = max(set(votes), key=votes.count) if votes else None
    return {"material_id": mid, "truth": rec["crystal_system"], "pred": pred,
            "n_atoms_emitted": len(atoms), "emitted": atoms, "votes": votes,
            "correct": pred == rec["crystal_system"]}

if __name__ == "__main__":
    key = os.environ["OPENROUTER_API_KEY"]
    rows = [json.loads(l) for l in open(f"{ROOT}/data/e3/eval.jsonl")]
    out, t0 = [], time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(one, r, key, 3, 0.7) for r in rows]
        for i, f in enumerate(futs):
            out.append(f.result())
            if i % 30 == 29: print(f"  {i+1}/{len(rows)} {time.time()-t0:.0f}s", flush=True)
            json.dump(out, open(f"{ROOT}/ledger/perception_transplant/a3_raw.json", "w"))
    k = sum(1 for x in out if x.get("correct")); n = len(out)
    print(f"A3: {k}/{n} = {k/n:.4f} | extract errors {sum(1 for x in out if x.get('extract_error'))} "
          f"| unparseable extractions {sum(1 for x in out if x.get('unparseable_extraction'))}", flush=True)
    print("perception_transplant A3 COMPLETE", flush=True)

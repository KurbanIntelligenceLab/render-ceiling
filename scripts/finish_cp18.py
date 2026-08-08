#!/usr/bin/env python
"""Finish CP18 once V2b's expansion generations land: pooled paired tests at n=420."""
import json, sys, collections
import numpy as np
from scipy.stats import binomtest

def vote(rec):
    cl=[s.get("claim") for s in rec.get("samples",[]) if s.get("claim")]
    return collections.Counter(cl).most_common(1)[0][0] if cl else None

def load(path):
    d=json.load(open(path))
    recs=d.get("predictions") or d.get("records")
    out={}
    for r in recs:
        p=r.get("pred") if "pred" in r else vote(r)
        out[r["material_id"]]=bool(p==r["truth"])
    return out, d

def mcnemar(a,b):
    ks=set(a)&set(b)
    n01=sum(1 for k in ks if a[k] and not b[k])
    n10=sum(1 for k in ks if b[k] and not a[k])
    p=binomtest(n01,n01+n10,0.5).pvalue if n01+n10 else 1.0
    return n01,n10,p,len(ks)

if __name__=="__main__":
    v2b_new, meta = load(sys.argv[1])
    print(f"V2b on expansion: {sum(v2b_new.values())}/{len(v2b_new)} = "
          f"{sum(v2b_new.values())/len(v2b_new):.4f}")
    # TERMINATION CHECK — the hypothesis for the long runtime
    recs = meta.get("predictions") or meta.get("records")
    texts=[s.get("text","") for r in recs for s in r.get("samples",[]) if isinstance(s,dict)]
    if texts:
        reach=sum(1 for t in texts if "[ANSWER]" in t or "ANSWER" in t)
        print(f"  samples reaching an answer line: {reach}/{len(texts)} = {reach/len(texts):.3f}")
        print(f"  mean sample length: {np.mean([len(t) for t in texts]):.0f} chars")
    print(json.dumps({k:v for k,v in meta.items() if k not in ("predictions","records")}, indent=1)[:400])

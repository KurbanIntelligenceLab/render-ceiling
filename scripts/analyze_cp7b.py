#!/usr/bin/env python
"""
certification certification analysis — runs the PRE-REGISTERED endpoint with its homogeneity gate.

Reads the K=8 generations for B1 (answerer) and each certifying chain, then for every chain:
  - the 2x2 (agree/disagree x correct/incorrect) stratified by B1 self-confidence
  - a BRESLOW-DAY homogeneity test, which GATES the CMH per the prereg amendment
  - CMH common odds ratio if homogeneity holds; per-stratum ORs with CIs if it does not
  - the PREDICTION SUPPORT table (which systems the chain ever emits) — a certifier that can
    only certify 3 of 7 systems is a different instrument from one covering all 7 (H-CERT-3)

Primary comparison: V2b's certification vs B3's (process-trained vs outcome-only).
"""
import argparse, json, math, collections

SYS = ["cubic","hexagonal","monoclinic","orthorhombic","tetragonal","triclinic","trigonal"]
STRATA = [0.500, 0.625, 0.750, 0.875, 1.000]   # pre-declared; 0.375 excluded (n=2)
MIN_CELL = 3


def majority(claims):
    v = [c for c in claims if c]
    return collections.Counter(v).most_common(1)[0][0] if v else None


def vote(rec):
    claims = [s["claim"] for s in rec["samples"]]
    p = majority(claims)
    v = [c for c in claims if c]
    return p, (collections.Counter(v)[p]/len(v) if v and p else 0.0)


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k/n; d = 1+z*z/n; c = p+z*z/(2*n)
    m = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (round((c-m)/d, 4), round((c+m)/d, 4))


def lift_test(k, n, p0):
    """Exact one-sided binomial test of the certified slice against the answerer's base rate.
    Reports BOTH directions so a below-base-rate arm is described as null, not as harmful."""
    if not n:
        return None
    obs = k/n
    def binom_ge(kk):
        return sum(math.comb(n, i) * p0**i * (1-p0)**(n-i) for i in range(kk, n+1))
    def binom_le(kk):
        return sum(math.comb(n, i) * p0**i * (1-p0)**(n-i) for i in range(0, kk+1))
    if obs >= p0:
        p, direction = binom_ge(k), "above"
    else:
        p, direction = binom_le(k), "below"
    return {"k": k, "n": n, "observed": round(obs, 4), "base_rate": p0,
            "lift": round(obs-p0, 4), "direction": direction,
            "one_sided_p": float(f"{p:.3g}"),
            "verdict": ("significant" if p < 0.05 else
                        "NULL — point estimate %s base rate but not significant" % direction)}


def tables(B, C):
    """Per-stratum 2x2 counts: [x1 (agree & correct), n1 (agree), x2, n2] keyed by B1 confidence."""
    out = collections.defaultdict(lambda: [0, 0, 0, 0])
    for mid, brec in B.items():
        if mid not in C:
            continue
        bp, bconf = vote(brec)
        cp, _ = vote(C[mid])
        lev = min(STRATA, key=lambda s: abs(s-bconf))
        if abs(lev-bconf) > 1e-6:
            continue                      # confidence not on a declared stratum -> excluded
        ok = (bp == brec["truth"])
        t = out[lev]
        if bp == cp:
            t[1] += 1; t[0] += ok
        else:
            t[3] += 1; t[2] += ok
    return dict(out)


def cmh(tabs):
    """Cochran-Mantel-Haenszel statistic and common odds ratio."""
    num = den = 0.0; rnum = rden = 0.0
    used = []
    for lev, (x1, n1, x2, n2) in sorted(tabs.items()):
        n = n1+n2; x = x1+x2
        if n1 < MIN_CELL or n2 < MIN_CELL or n < 2 or x in (0, n):
            continue
        used.append(lev)
        num += x1 - n1*x/n
        den += n1*n2*x*(n-x)/(n*n*(n-1))
        a, b, c, d = x1, n1-x1, x2, n2-x2
        rnum += a*d/n; rden += b*c/n
    z = num/math.sqrt(den) if den > 0 else float("nan")
    or_mh = rnum/rden if rden > 0 else float("nan")
    return {"z": round(z, 4), "common_or": round(or_mh, 4), "strata_used": used}


def breslow_day(tabs, or_mh):
    """Breslow-Day homogeneity test. Rejecting means a COMMON odds ratio is not defensible."""
    if not (or_mh and or_mh > 0 and math.isfinite(or_mh)):
        return {"stat": None, "df": 0, "reject": None,
                "note": "common OR undefined; homogeneity untestable"}
    stat = 0.0; df = 0
    for lev, (x1, n1, x2, n2) in sorted(tabs.items()):
        n = n1+n2; x = x1+x2
        if n1 < MIN_CELL or n2 < MIN_CELL or x in (0, n):
            continue
        # expected a under the common OR: solve a(d)/(b c) = OR
        A = or_mh - 1.0
        Bq = -(or_mh*(n1+x) + (n2-x))
        Cq = or_mh*n1*x
        a = (n1*x/n) if abs(A) < 1e-12 else (-Bq - math.sqrt(max(Bq*Bq - 4*A*Cq, 0)))/(2*A)
        a = min(max(a, 1e-9), min(n1, x)-1e-9)
        b = n1-a; c = x-a; d = n2-c
        if min(b, c, d) <= 0:
            continue
        var = 1.0/(1.0/a + 1.0/b + 1.0/c + 1.0/d)
        stat += (x1-a)**2/var; df += 1
    df = max(df-1, 0)
    # chi-square upper tail via Wilson-Hilferty
    p = None
    if df > 0:
        wh = ((stat/df)**(1/3) - (1 - 2/(9*df)))/math.sqrt(2/(9*df))
        p = 0.5*math.erfc(wh/math.sqrt(2))
    return {"stat": round(stat, 4), "df": df,
            "p": (round(p, 5) if p is not None else None),
            "reject": (p is not None and p < 0.05)}


def support(C):
    """Prediction support: which systems this chain ever emits (H-CERT-3)."""
    c = collections.Counter(vote(r)[0] for r in C.values())
    return {"distribution": dict(c.most_common()),
            "systems_emitted": sum(1 for s in SYS if c.get(s, 0) > 0),
            "never_emitted": [s for s in SYS if c.get(s, 0) == 0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answerer", required=True, help="B1 K=8 generation json")
    ap.add_argument("--chains", nargs="+", required=True, help="name=path pairs")
    ap.add_argument("--base-rate", type=float, default=0.6143,
                    help="answerer's unconditional accuracy, for the exact-binomial lift test")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    B = {r["material_id"]: r for r in json.load(open(a.answerer))["records"]}
    res = {"answerer_n": len(B), "strata": STRATA, "min_cell": MIN_CELL, "chains": {}}
    for spec in a.chains:
        name, path = spec.split("=", 1)
        C = {r["material_id"]: r for r in json.load(open(path))["records"]}
        tabs = tables(B, C)
        st = cmh(tabs)
        bd = breslow_day(tabs, st["common_or"])
        cov = sum(t[1] for t in tabs.values())
        # COVERAGE DENOMINATOR: the FULL answerer population, not just on-stratum structures.
        # The stratified CMH can only use confidences on a declared stratum (2 structures sit at
        # 0.375, an undeclared level), but coverage is a population quantity and off-stratum
        # structures are scored NOT-CERTIFIED per the standing convention. One quantity, one value.
        tot = len(B)
        n_offstratum = tot - sum(t[1]+t[3] for t in tabs.values())
        acc_cov = sum(t[0] for t in tabs.values())/cov if cov else None
        res["chains"][name] = {
            "per_stratum": {str(k): {"agree_correct": v[0], "agree_n": v[1],
                                     "disagree_correct": v[2], "disagree_n": v[3]}
                            for k, v in sorted(tabs.items())},
            "cmh": st, "breslow_day": bd,
            "homogeneity_gate": ("CMH reportable" if not bd.get("reject")
                                 else "CMH NOT reportable — per-stratum only"),
            "coverage": round(cov/tot, 4) if tot else None,
            "coverage_counts": {"certified": cov, "population": tot,
                                "off_stratum_scored_not_certified": n_offstratum},
            "cmh_denominator": sum(t[1]+t[3] for t in tabs.values()),
            "acc_on_covered": round(acc_cov, 4) if acc_cov is not None else None,
            "acc_on_covered_wilson95": wilson(sum(t[0] for t in tabs.values()), cov),
            "lift_vs_base_rate": lift_test(sum(t[0] for t in tabs.values()), cov, a.base_rate),
            "prediction_support": support(C)}
        # FALSE-CERTIFICATION RATE: of the structures where the CHAIN is wrong, how often does
        # the answerer nonetheless agree? This is the non-tautological reliability quantity.
        wrong = agreed_wrong = 0
        for mid, brec in B.items():
            if mid not in C:
                continue
            bp, _ = vote(brec); cp, _ = vote(C[mid])
            if cp != C[mid]["truth"]:
                wrong += 1
                agreed_wrong += (bp == cp)
        res["chains"][name]["false_certification"] = {
            "chain_wrong_n": wrong, "answerer_agreed_with_wrong": agreed_wrong,
            "rate": round(agreed_wrong/wrong, 4) if wrong else None,
            "wilson95": wilson(agreed_wrong, wrong)}
        c = res["chains"][name]
        print(f"{name}: cov={c['coverage']} ({c['coverage_counts']['certified']}/"
              f"{c['coverage_counts']['population']}) acc_cov={c['acc_on_covered']} "
              f"lift p={c['lift_vs_base_rate']['one_sided_p']} ({c['lift_vs_base_rate']['direction']}) "
              f"| CMH z={st['z']} OR={st['common_or']} BD p={bd.get('p')} "
              f"| false-cert {c['false_certification']['rate']} "
              f"| emits {c['prediction_support']['systems_emitted']}/7")

    # two-proportion comparison of false-certification rates, BOTH pooled and unpooled
    ns = list(res["chains"].keys())
    if len(ns) == 2:
        f1, f2 = (res["chains"][n]["false_certification"] for n in ns)
        k1, n1 = f1["answerer_agreed_with_wrong"], f1["chain_wrong_n"]
        k2, n2 = f2["answerer_agreed_with_wrong"], f2["chain_wrong_n"]
        p1, p2 = k1/n1, k2/n2
        pp = (k1+k2)/(n1+n2)
        se_p = math.sqrt(pp*(1-pp)*(1/n1+1/n2))
        se_u = math.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
        res["false_certification_comparison"] = {
            "arms": ns, "rates": [round(p1, 4), round(p2, 4)],
            "difference": round(p2-p1, 4),
            "z_pooled": round((p2-p1)/se_p, 3), "z_unpooled": round((p2-p1)/se_u, 3),
            "note": "z_unpooled is the headline; pooled reported alongside, conclusion unchanged"}
        print(f"false-cert {ns[0]} {p1:.4f} vs {ns[1]} {p2:.4f} | "
              f"z_pooled={res['false_certification_comparison']['z_pooled']} "
              f"z_unpooled={res['false_certification_comparison']['z_unpooled']}")
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()

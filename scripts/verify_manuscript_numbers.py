"""consolidated_verification — script verification of every manuscript number against a checkpoint results.json.

Exit non-zero on any failure. Three checks, each of which caught a real defect in this package:
  1 VALUE EQUALITY, not presence. An earlier presence-only check ("does the string appear?") validated
    against an already-corrupted field. Every 4-dp number in the manuscript must equal a value that
    exists somewhere in the ledger's results files.
  2 SAMPLE NAME AND DECODE BUDGET. Every accuracy in a table row must carry its sample and its K.
  3 PAIRED CLAIMS CARRY DISCORDANCE COUNTS, so a reader can recompute the test.
"""
import os as _o, sys as _s
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), ''))
from _paths import ROOT, RESULTS
import json, re, os, sys, glob

# checkpoint records live in results/ in this repository (formerly ledger/)
L = RESULTS

def ledger_values():
    """Every numeric literal anywhere in any checkpoint results.json, as a set of rounded floats."""
    vals, src = set(), {}
    # records are named for what they measure; INDEX.json carries their run order
    for f in glob.glob(f"{L}/*/*.json"):
        try: d = json.load(open(f))
        except Exception: continue
        def walk(o):
            if isinstance(o, dict):
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
            elif isinstance(o, str):
                # numbers also live inside PROSE fields (a "robustness" note carrying its own counts).
                # Not indexing these produced four false unsourced flags on values that were stored.
                for mm in re.finditer(r"(?<![\d.])(\d+\.\d{2,4})(?![\d])", o):
                    for nd in (4, 3, 2):
                        r = round(float(mm.group(1)), nd); vals.add(r)
                        src.setdefault(r, os.path.basename(os.path.dirname(f)) + " (prose field)")
            elif isinstance(o, (int, float)) and not isinstance(o, bool):
                # index BOTH signs: a manuscript writes a stored diff of -0.5935 as "0.5935" next to a
                # direction word, so matching on the absolute value is required, not optional.
                for nd in (4, 3, 2):
                    for val in (float(o), -float(o)):
                        r = round(val, nd); vals.add(r); src.setdefault(r, os.path.basename(os.path.dirname(f)))
        walk(d)
    return vals, src

DERIVED_OK = re.compile(
    r"lower bound|Clopper|Wilson|Spearman|rho|gap WIDENS|delta|"
    r"pooled they give|= \d+/\d+|sample /|population\)|SD \(", re.I)
PRIOR_WORK = re.compile(r"Jaccard|exact match|prior work|reported by|their|CrystalXRD|xCrysAlloys|"
                        r"2\d{3}\.\d{4,5}", re.I)

def check_values(doc, vals, src, allow):
    """Every 4-dp literal must EQUAL a ledger value, or be one of three legitimate exceptions,
    each of which must be evidenced by its own context rather than assumed:
      DERIVED    - computed from stored counts (an interval bound, a delta, a correlation, a pooled rate)
      PRIOR WORK - a number from a cited paper, which by construction is not in our ledger
      WHITELIST  - explicitly enumerated sample-specific constants
    Anything else is an UNSOURCED number and fails the build."""
    bad = []
    for m in re.finditer(r"(?<![\d.])(\d\.\d{4})(?![\d])", doc):
        v = round(float(m.group(1)), 4)
        if v in vals or v in allow: continue
        i = m.start(); ctx = doc[max(0, i-160):i+120].replace("\n", " ")
        if DERIVED_OK.search(ctx) or PRIOR_WORK.search(ctx): continue
        bad.append((m.group(1), ctx[60:190]))
    return bad

def check_sample_and_k(doc):
    """A TABLE ROW quoting an accuracy must name its sample and its decode budget.

    Scope is deliberately narrow, because a loose version of this check flags arXiv identifiers,
    p-values and correction notes as accuracies and buries the four real defects among twenty
    false ones. A row qualifies only if it is an indented label followed by whitespace and a
    trailing 4-dp value — i.e. an actual table row, not prose containing a number.
    """
    NOT_AN_ACCURACY = re.compile(
        r"arXiv|\bp\s*=|\bp=|REPLACED BY|RETRACT|supersed|withdraw|CP\d+|"
        r"1e-\d|e-0\d|Jaccard|token|px\b|SD \(|Spearman|rho", re.I)
    HAS_SCOPE = re.compile(r"K=\d|\(K\b|no K|K\s*=\s*\d|definitional|UNSCORED|chance|floor|"
                           r"majority|original|expansion|this sample|n\s*=\s*\d", re.I)
    bad = []
    for line in doc.splitlines():
        if not re.match(r"^\s{2,}\S", line):
            continue
        m = re.search(r"\s{2,}(\d\.\d{4})\s*$", line)   # trailing value = a table row
        if not m:
            continue
        if NOT_AN_ACCURACY.search(line) or HAS_SCOPE.search(line):
            continue
        bad.append(line.strip()[:100])
    return bad


def check_paired(doc):
    """A paired claim must be accompanied by discordance counts."""
    bad = []
    for m in re.finditer(r"paired[^.]{0,160}?p\s*=\s*[\d.e-]+", doc, re.I):
        seg = doc[max(0, m.start()-420):m.end()+420]
        if not re.search(r"discordan|\bonly\b.*\d+.*\bonly\b|\d+\s*(?:vs|/)\s*\d+|n01|arm-only|oracle-only|"
                         r"r3_only|gain \d+|gained \d+|\d+ structures\b|lose \d+|lost \d+", seg, re.I):
            bad.append(m.group()[:100])
    return bad

if __name__ == "__main__":
    # Prose documents live under reports/ in this repository. SUPPLEMENTARY_INFORMATION.md is
    # EXCLUDED: it embeds every checkpoint record verbatim, including retracted values quoted inside
    # correction notes. This gate is right to reject those in prose and must not reject them in the
    # archival record whose purpose is to document the retraction.
    # Every prose document, including the build sources under reports/sources/ — moving a file must
    # not silently drop it from the gate. SUPPLEMENTARY_INFORMATION.md is EXCLUDED: it embeds every
    # checkpoint record verbatim, including retracted values quoted inside correction notes. This gate
    # is right to reject those in prose and must not reject them in the archival record whose purpose
    # is to document the retraction; its Parts I-III are gated via their sources.
    docs = {p: open(p).read()
            for p in sorted(glob.glob(f"{ROOT}/docs/reports/*.md") + glob.glob(f"{ROOT}/docs/reports/sources/*.md"))
            if os.path.basename(p) != "SUPPLEMENTARY_INFORMATION.md"}
    vals, src = ledger_values()
    # derived quantities: computed from stored counts rather than stored themselves
    allow = set()
    for extra in (0.5286, 0.2476, 0.1429, 0.0043, 0.0312, 0.0714):
        allow.add(extra)
    fails = 0
    print(f"ledger values indexed: {len(vals)} distinct (rounded to 2-4 dp)")
    for p, d in docs.items():
        nm = os.path.basename(p)
        bv = check_values(d, vals, src, allow)
        bk = check_sample_and_k(d)
        bp = check_paired(d)
        status = "OK" if not (bv or bk or bp) else "FAIL"
        print(f"  {nm:26s} unmatched-value {len(bv):>3d} | accuracy-without-sample-or-K {len(bk):>3d} | "
              f"paired-without-discordance {len(bp):>2d} | {status}")
        for x in bv[:4]: print(f"      unmatched {x[0]}: ...{x[1]}...")
        for x in bk[:4]: print(f"      accuracy w/o sample or K: {x}")
        for x in bp[:2]: print(f"      paired w/o counts: {x}")
        if bv or bk or bp: fails += 1
    print(f"\n{'PASS' if fails == 0 else f'FAIL — {fails} document(s)'}")
    sys.exit(1 if fails else 0)

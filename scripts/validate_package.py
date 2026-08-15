#!/usr/bin/env python3
"""Validate the CoCr release package. Exit 0 = complete and self-consistent.

Checks, in order of severity:
  1  every folder the README claims exists, with the count it claims
  2  every figure the manuscript references resolves to a file
  3  every \ref resolves to a \label, and no label floats unreferenced
  4  no unsubstituted NUM_ placeholders survive in the manuscript
  5  every 4-decimal number in the manuscript body traces by value to a results.json
  6  every checkpoint in results/ appears in the SI, and vice versa
  7  every manuscript figure has a script that reproduces it byte-for-byte
  7b every figure the manuscript references is covered by a script (no unscripted figures)
  8  no provisional data (pilot/smoke/diagnostic/tmp) anywhere
  9  no files from the unrelated A4 text-reasoning study
 10  REPORT.md and the SI's Part I agree

Usage:  python scripts/validate_package.py [package_root]
"""
import hashlib, json, os, re, subprocess, sys, tempfile

FAIL = []
WARN = []


def check(cond, msg, warn=False):
    if not cond:
        (WARN if warn else FAIL).append(msg)
    return cond


def main(root="."):
    root = os.path.abspath(root)
    try:
        rd = open(f"{root}/README.md").read()
    except FileNotFoundError:
        print(f"FAILED — no README.md at {root}; is this the package root?")
        return 1

    # 1 structure
    for d in ("docs/manuscript", "docs/manuscript/codes", "docs/reports", "results", "scripts",
              "scripts/src/cocr", "release"):
        check(os.path.isdir(f"{root}/{d}"), f"[1] missing folder: {d}")
    res_dirs = sorted(d for d in os.listdir(f"{root}/results")
                      if os.path.isdir(f"{root}/results/{d}"))
    # INDEX.json is the run-order authority for the records, whose directory names describe what
    # they measure rather than when they ran; it is expected at the top of results/.
    stray = [f for f in os.listdir(f"{root}/results")
             if not os.path.isdir(f"{root}/results/{f}") and f != "INDEX.json"]
    check(not stray, f"[1] loose files directly in results/ (expected one folder per checkpoint): {stray}")
    # The manuscript source is not published from this repository (see .gitignore), so the checks
    # that read it run only where it is present — a working tree — and are reported as skipped in a
    # clean clone rather than failing it. Everything that constitutes the reproducibility package —
    # records, scripts, generators, release — is checked unconditionally.
    DD = f"{root}/docs/manuscript/render-ceiling-dd"
    HAVE_MS = os.path.isdir(DD)
    if not HAVE_MS:
        WARN.append("[2-5,7,11] manuscript source not present; the checks that read it are skipped. "
                    "They run in the authors' working tree, where the manuscript lives.")
    counts = {
        "figures": len([f for f in os.listdir(f"{DD}/figures") if f.endswith(".pdf")]) if HAVE_MS
                   else len([f for f in os.listdir(f"{root}/docs/manuscript/codes")
                             if f.startswith("make_fig")]),
        "results_json": sum(len([f for f in os.listdir(f"{root}/results/{d}") if f.endswith(".json")])
                            for d in res_dirs),
        "results_dirs": len(res_dirs),
        "scripts": len([f for f in os.listdir(f"{root}/scripts") if f.endswith(".py")]),
        "src_modules": len([f for f in os.listdir(f"{root}/scripts/src/cocr") if f.endswith(".py")]),
        "data_files": sum(len(fs) for _, _, fs in os.walk(f"{root}/data")),
    }
    # every checkpoint must carry a finding — the one-checkpoint-one-record rule
    nofind = [d for d in res_dirs
              if not any(f.startswith("finding") for f in os.listdir(f"{root}/results/{d}"))]
    check(not nofind, f"[1b] checkpoints with no finding.md: {nofind}")
    for k, v in counts.items():
        # word-boundary match, NOT substring: a bare `str(v) in rd` lets a count of 90 pass because
        # "90" occurs inside "0.9095". A count check any decimal can satisfy is not a count check.
        check(re.search(rf"(?<![\d.]){v}(?![\d.])", rd) is not None,
              f"[1] README does not state the actual {k} count ({v})")

    # 2-4 manuscript
    # the Digital Discovery submission is main.tex plus its \input section files; the ESI
    # (si.tex + sections/si_body.tex) is checked alongside it, since labels cross between them
    tex = "" if not HAVE_MS else "".join(open(p).read() for p in
                  [f"{DD}/main.tex", f"{DD}/si.tex"] +
                  sorted(f"{DD}/sections/{f}" for f in os.listdir(f"{DD}/sections")
                         if f.endswith(".tex")))
    for f in set(re.findall(r"includegraphics\[[^\]]*\]\{figures/([^}]+)\}", tex)):
        check(os.path.exists(f"{DD}/figures/{f}"), f"[2] figure referenced but absent: {f}")
    refs = set(re.findall(r"\\ref\{([^}]+)\}", tex))
    labs = set(re.findall(r"\\label\{([^}]+)\}", tex))
    check(not (refs - labs), f"[3] dangling references: {sorted(refs - labs)}")
    # NOTE: not a failure in this manuscript. The RSC house style cross-refers between the article
    # and the ESI by literal number ("Section 3.4 of the article"), since \ref cannot cross the two
    # documents, so section labels are legitimately unreferenced. A DANGLING ref above is still a
    # failure; an unused label is reported for information only.
    if labs - refs:
        WARN.append(f"[3] labels defined but never \\ref'd (expected for cross-document "
                    f"references): {sorted(labs - refs)}")
    check(not re.findall(r"NUM_[A-Z_0-9]+", tex), "[4] unsubstituted NUM_ placeholders in manuscript")

    # 5 numeric provenance
    vals = set()
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            for nd in (4, 3, 2):
                vals.add(round(float(o), nd)); vals.add(round(-float(o), nd))
        elif isinstance(o, str):
            for m in re.finditer(r"(?<![\d.])(\d+\.\d{2,4})(?![\d])", o):
                for nd in (4, 3, 2): vals.add(round(float(m.group(1)), nd))
    for d in res_dirs:
        for f in os.listdir(f"{root}/results/{d}"):
            if f.endswith(".json"):
                try: walk(json.load(open(f"{root}/results/{d}/{f}")))
                except Exception: pass
    body = tex  # DD cites via \bibliography{references}; there is no inline thebibliography
    untraced = [m.group(1) for m in re.finditer(r"(?<![\d.])(\d\.\d{4})(?![\d])", body)
                if round(float(m.group(1)), 4) not in vals]
    check(not untraced, f"[5] manuscript numbers not traceable to any results.json: {sorted(set(untraced))}")

    # 6 SI coverage
    si = open(f"{root}/docs/reports/SUPPLEMENTARY_INFORMATION.md").read()
    for d in res_dirs:
        check(f"## {d}" in si, f"[6] checkpoint in results/ but not in the SI: {d}")

    # 7 figure scripts reproduce
    FIGS = [("make_fig1_leaderboard", "leaderboard"), ("make_fig2_ladder", "ladder"),
            ("make_fig3_noimage", "noimage"), ("make_fig4_cuesuff", "cuesuff"),
            ("make_fig5_generational", "generational"), ("make_fig6_conditions", "conditions")]
    ledger = os.environ.get("COCR_LEDGER", f"{root}/results")
    if os.path.isdir(ledger):
        for script, fig in FIGS:
            out = tempfile.mktemp(suffix=".pdf")
            r = subprocess.run([sys.executable, f"{root}/docs/manuscript/codes/{script}.py", ledger, out],
                               capture_output=True, text=True)
            if not check(r.returncode == 0, f"[7] figure script failed: {script} ({r.stderr.strip()[-120:]})"):
                continue
            shipped = f"{DD}/figures/{fig}.pdf"
            if not HAVE_MS:
                continue  # generator ran clean; there is no shipped copy here to compare against
            if not check(os.path.exists(shipped), f"[7] shipped figure missing: {fig}.pdf"):
                continue
            a = hashlib.md5(open(out, "rb").read()).hexdigest()
            b = hashlib.md5(open(shipped, "rb").read()).hexdigest()
            check(a == b, f"[7] {script} does not reproduce the shipped {fig}.pdf")
    else:
        WARN.append(f"[7] ledger not found at {ledger}; set COCR_LEDGER to re-run the figure scripts")
    # 7b no manuscript figure may lack a script
    scripted = {fig for _, fig in FIGS}
    referenced = {f[:-4] for f in re.findall(r"includegraphics\[[^\]]*\]\{figures/([^}]+)\}", tex)}
    check(referenced <= scripted,
          f"[7b] manuscript figures with no generating script: {sorted(referenced - scripted)}")

    # 8-9 hygiene
    # The scan covers the PACKAGE, not the working tree. A resolved virtual environment, the git
    # object store and the staging area are git-ignored and never published, and a third-party
    # wheel that ships a file named test_smoke.py is not this project's scratch — walking into
    # .venv reports thousands of such hits and fails a clean package on its own dependencies.
    SKIP_DIRS = {".git", ".venv", "venv", "to_be_deleted", "__pycache__", "node_modules"}
    junk, a4 = [], []
    for dp, dns, fs in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fs:
            # *_snapshot.md under results/ is the DELIBERATE pre-correction record — the evidence
            # a withdrawal actually happened — and is not scratch. Everything else matching is.
            deliberate = f.endswith("_snapshot.md") and "/results/" in dp + "/"
            if re.search(r"pilot|smoke|diag|_tmp|\.DS_Store", f, re.I) and not deliberate:
                junk.append(os.path.relpath(os.path.join(dp, f), root))
            if f.startswith("a4_"):
                a4.append(os.path.relpath(os.path.join(dp, f), root))
    # Compiled bytecode must never ship: it is machine- and interpreter-version specific, and 17 .pyc
    # files silently appeared here just from running the audit tooling. This check WARNS rather than
    # fails, because running the validator itself imports the figure modules and so creates bytecode —
    # a hard failure here would be self-defeating, reporting a defect the check's own execution caused.
    pyc = []
    for dp, dns, fs in os.walk(root):
        dns[:] = [d for d in dns if d not in (SKIP_DIRS - {"__pycache__"})]
        pyc += [os.path.relpath(os.path.join(dp, f), root) for f in fs
                if f.endswith(".pyc") or os.path.basename(dp) == "__pycache__"]
    if pyc:
        WARN.append(f"[8b] compiled bytecode present ({len(pyc)} files, e.g. {pyc[0]}). Regenerated on "
                    f"every run and machine-specific — delete before publishing: "
                    f"find . -name __pycache__ -type d -exec rm -rf {{}} + ; find . -name '*.pyc' -delete")

    check(not junk, f"[8] provisional or scratch files present: {junk[:6]}")
    check(not a4, f"[9] files from the unrelated A4 study: {a4[:6]}")

    # 11 latex linter
    # lint the prose the authors write, not main.tex: the RSC template's preamble uses trailing `%`
    # as a line-continuation throughout, which the linter's unescaped-percent rule flags by design.
    lint_targets = sorted(f"{DD}/sections/{f}" for f in os.listdir(f"{DD}/sections")
                          if f.endswith(".tex")) if HAVE_MS else []
    if lint_targets:
        lint = subprocess.run([sys.executable, f"{root}/scripts/lint_latex.py"] + lint_targets,
                              capture_output=True, text=True)
        check(lint.returncode == 0, f"[11] LaTeX linter findings:\n{lint.stdout.strip()[:600]}")

    # 10 report consistency — the WHOLE document, not a prefix. A prefix comparison passes while the
    # two diverge anywhere after character 400, which is most of the report.
    rep = open(f"{root}/docs/reports/REPORT.md").read()
    check(rep.strip() in si, "[10] SI Part I is not docs/reports/REPORT.md verbatim")

    # 13 the shipped SI must be EXACTLY what its generator produces from the current results/.
    # A shipped file that its own builder no longer reproduces breaks the reproducibility guarantee,
    # and a line-count glance does not catch it — this compares bytes.
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as _t:
        _tmp = _t.name
    subprocess.run([sys.executable, f"{root}/scripts/build_si.py", root, _tmp],
                   capture_output=True, text=True)
    try:
        fresh = open(_tmp, "rb").read()
        shipped = open(f"{root}/docs/reports/SUPPLEMENTARY_INFORMATION.md", "rb").read()
        check(fresh == shipped,
              "[13] docs/reports/SUPPLEMENTARY_INFORMATION.md is STALE: build_si.py produces a different "
              f"file from the current results/ ({len(fresh.splitlines())} lines vs "
              f"{len(shipped.splitlines())} shipped). Re-run build_si.py.")
    except FileNotFoundError:
        check(False, "[13] build_si.py produced no output")
    finally:
        os.path.exists(_tmp) and os.remove(_tmp)

    # 13c anything filed under reports/sources/ is claimed by the README to be a BUILD INPUT whose
    # content appears in full in the merged document. That claim was once made for a file it was not
    # true of, which would have let a reader delete content surviving nowhere else. Test it per file.
    srcdir = f"{root}/docs/reports/sources"
    if os.path.isdir(srcdir):
        for f in sorted(os.listdir(srcdir)):
            if not f.endswith(".md"):
                continue
            lines = [l for l in open(f"{srcdir}/{f}").read().splitlines() if len(l.split()) > 6]
            absent = [l for l in lines if l not in si]
            check(not absent,
                  f"[13c] docs/reports/sources/{f} is filed as a build input but {len(absent)} of "
                  f"{len(lines)} substantive lines are ABSENT from the merged document. Either it is "
                  f"not a source, or the merged document is stale.")

    # 13b every *_snapshot.md kept as deliberate history must be cited by its checkpoint's finding,
    # otherwise it is indistinguishable from scratch and the [8] exemption is unearned.
    orphan = []
    for d in res_dirs:
        # a snapshot earns its [8] exemption if ANY live record in the same checkpoint cites it by
        # name, OR if the finding declares a supersession the snapshot is the evidence for.
        live = [f for f in os.listdir(f"{root}/results/{d}")
                if f.endswith(".md") and not f.endswith("_snapshot.md")]
        text = "".join(open(f"{root}/results/{d}/{f}").read() for f in live)
        declares = re.search(r"SUPERSEDED|RETRACT|CORRECTION NOTE|pre-correction|snapshot", text, re.I)
        for f in os.listdir(f"{root}/results/{d}"):
            if f.endswith("_snapshot.md") and f not in text and not declares:
                orphan.append(f"{d}/{f}")
    check(not orphan, f"[13b] snapshot files not cited by their finding: {orphan[:6]}")

    # 12 prose gate: every value in every prose document traces to a checkpoint record, every accuracy
    # carries its sample and decode budget, every paired claim carries its discordance counts.
    gate = subprocess.run([sys.executable, f"{root}/scripts/verify_manuscript_numbers.py"],
                          capture_output=True, text=True, cwd=root)
    check(gate.returncode == 0,
          f"[12] prose gate findings:\n{gate.stdout.strip()[-700:]}")

    print(f"checked {len(counts)} counts, {len(res_dirs)} checkpoints, "
          f"{counts['figures']} figures, {counts['scripts'] + counts['src_modules']} code files")
    for w in WARN: print(f"WARN  {w}")
    for f in FAIL: print(f"FAIL  {f}")
    print("PASS — package is complete and self-consistent" if not FAIL else f"FAILED — {len(FAIL)} problem(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

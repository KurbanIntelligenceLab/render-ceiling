#!/usr/bin/env python3
"""Rebuild SUPPLEMENTARY_INFORMATION.md — the single merged document — from the repo's own records.

Four parts, in one file:
  I    the narrative report (reports/REPORT.md)
  II   supplementary sections S1-S14 (generated in process, and also written to reports/sources/)
  III  reviewer questions answered from the records (reports/sources/PART_C_ANSWERS.md)
  IV   the complete checkpoint record: every pre-registration and finding, read from results/CP*/

Each Part IV section names the results files it is backed by, so a claim can be traced from prose to
the exact JSON without searching.

Usage:  python scripts/build_si.py <repo_root> <out.md>
"""
import os, re, sys, json

HEADER = """# render-ceiling — Supplementary Information

Everything this project ran, in one document. Reading it end to end is the complete record; nothing
material lives outside it except the raw per-structure vectors in `release/predictions/` and the
figures in `figures/`.

| part | contents |
|---|---|
| I | narrative report — the instrument, what it attributes, where the models sit |
| II | supplementary sections S1-S14 — dataset, protocol, oracle, ladder, rosters, baselines |
| III | reviewer questions answered directly from the records |
| IV | complete checkpoint record — every pre-registration and finding, verbatim |

HOW TO READ A CHECKPOINT. Each Part IV section opens with the results files backing it, then its
pre-registration where one exists, then its finding. A pre-registration present means the reading was
committed before the numbers existed; where it is absent, or where the record is a post-hoc analysis
record, the finding says so in its own text.

WHAT IS AND IS NOT VERIFIED. Every number in Parts I-III traces by value to a `results.json` under
`results/`, enforced by `scripts/verify_manuscript_numbers.py`, which also refuses any accuracy stated
without its sample and decode budget. Nothing is omitted from Part IV — including analyses whose outcome
contradicted the registered expectation, claims that were withdrawn, and defects found in this project's
own work. Retracted values are preserved inside labelled correction notes rather than deleted.

"""


def backing_files(rdir, cp):
    """The results files a checkpoint's claims are backed by, largest first."""
    fs = [(f, os.path.getsize(f"{rdir}/{cp}/{f}"))
          for f in sorted(os.listdir(f"{rdir}/{cp}")) if f.endswith(".json")]
    return sorted(fs, key=lambda x: (x[0] != "results.json", -x[1]))


def main(root, out):
    rdir = f"{root}/results"
    cps = sorted((d for d in os.listdir(rdir) if d.startswith("CP")),
                 key=lambda x: (int(re.match(r"CP(\d+)", x).group(1)), x))

    # Part II is generated IN PROCESS, not copied and not shelled out to — this document cannot drift
    # from its own generator, and there is one builder rather than two. build_supplementary.main also
    # writes reports/sources/SUPPLEMENTARY_SECTIONS.md, which is kept as the standalone S1-S14 document.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_supplementary
    sect_path = f"{root}/reports/sources/SUPPLEMENTARY_SECTIONS.md"
    build_supplementary.main(rdir, sect_path)
    sections = open(sect_path).read()
    # drop its standalone title, it becomes a part here
    sections = re.sub(r"\A# [^\n]*\n", "", sections).lstrip()

    toc = ["## Checkpoint index\n",
           "| checkpoint | pre-registered | results files | status |", "|---|---|---|---|"]
    npre = 0
    part4 = []
    for cp in cps:
        mds = [f for f in os.listdir(f"{rdir}/{cp}") if f.endswith(".md")]
        pre = sorted(f for f in mds if f.startswith("prereg"))
        fin = sorted(f for f in mds if f.startswith("finding"))
        npre += bool(pre)
        back = backing_files(rdir, cp)
        st = ""
        if fin:
            m = re.search(r"^STATUS:\s*(.+)$", open(f"{rdir}/{cp}/{fin[0]}").read(), re.M)
            if m:
                st = " ".join(m.group(1).split())[:90]
        toc.append(f"| [{cp}](#{cp.lower().replace('_', '-')}) | {'yes' if pre else 'no'} | "
                   f"{len(back)} | {st} |")
        part4.append(f"\n## {cp}\n")
        if back:
            part4.append("BACKED BY: " + ", ".join(f"`results/{cp}/{f}`" for f, _ in back) + "\n")
        else:
            part4.append("BACKED BY: no numeric results — this checkpoint is a reasoned cut or was "
                         "subsumed, and carries a finding only.\n")
        for f in pre + fin:
            part4.append(f"\n### {f}\n\n```\n" + open(f"{rdir}/{cp}/{f}").read().rstrip() + "\n```\n")

    doc = (HEADER + "\n".join(toc) + "\n\n---\n\n"
           + "\n# PART I — NARRATIVE REPORT\n\n" + open(f"{root}/reports/REPORT.md").read()
           + "\n\n---\n\n# PART II — SUPPLEMENTARY SECTIONS\n\n" + sections
           + "\n\n---\n\n# PART III — REVIEWER QUESTIONS, ANSWERED FROM THE RECORDS\n\n"
           + re.sub(r"\A# [^\n]*\n", "", open(f"{root}/reports/sources/PART_C_ANSWERS.md").read()).lstrip()
           + "\n\n---\n\n# PART IV — COMPLETE CHECKPOINT RECORD\n" + "\n".join(part4))
    open(out, "w").write(doc)
    nback = sum(len(backing_files(rdir, c)) for c in cps)
    print(f"{out}: {len(doc.splitlines())} lines, 4 parts, {len(cps)} checkpoints "
          f"({npre} pre-registered), {nback} results files pointed at")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

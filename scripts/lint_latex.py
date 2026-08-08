#!/usr/bin/env python3
"""LaTeX build linter. Four checks, all of which have bitten this project.

  1  unescaped % (LaTeX comments out the rest of the line, silently)
  2  odd count of unescaped $ per line (unbalanced math mode)
  3  \times, ^ or _ outside math mode
  4  undefined \ref / \cite keys

Usage:  python scripts/lint_latex.py <file.tex>   -> exit 0 clean, 1 on any finding
"""
import re, sys

def strip_math(line):
    """Replace math spans with spaces so outside-math checks do not see them."""
    out = list(line); depth = 0; i = 0
    while i < len(line):
        if line[i] == "$" and (i == 0 or line[i-1] != "\\"):
            if line[i:i+2] == "$$": depth ^= 1; out[i] = out[i+1] = " "; i += 2; continue
            depth ^= 1; out[i] = " "; i += 1; continue
        if depth: out[i] = " "
        i += 1
    return "".join(out)

def main(path):
    src = open(path).read()
    lines = src.split("\n")
    fails = []
    for n, line in enumerate(lines, 1):
        code = line.split("%")[0] if re.match(r"^\s*%", line) else line
        # 1 unescaped percent (a leading-% comment line is legitimate)
        if not re.match(r"^\s*%", line):
            for m in re.finditer(r"(?<!\\)%", line):
                fails.append((n, "unescaped-percent", line[max(0, m.start()-40):m.start()+20].strip()))
        # 2 unbalanced math
        if line.replace("\\$", "").count("$") % 2:
            fails.append((n, "odd-dollar-count", line.strip()[:70]))
        # 2b math span that ENDS in an operator, e.g. "$p = $0.0039" — balanced but wrong,
        #    so the dollar-count check above cannot see it. This exact bug shipped twice.
        for m in re.finditer(r"\$[^$]{0,30}?(?:=|\\approx|<|>)\s*\$", line):
            fails.append((n, "math-ends-in-operator", m.group(0)))
        # 3 math-only constructs outside math
        outside = strip_math(line)
        # drop args where _ and ^ are legal, but keep the target tokens themselves
        outside = re.sub(r"\\(?:label|ref|cite[a-z]*|includegraphics|texttt|url|bibitem|input|bibliographystyle|usepackage|documentclass|newcommand|renewcommand)(?:\[[^\]]*\])?\{[^}]*\}", " ", outside)
        outside = re.sub(r"\\bibliographystyle|\\bibliography", " ", outside)
        for tok, name in ((r"\\times(?![a-zA-Z])", "times-outside-math"),
                          (r"(?<!\\)\^", "superscript-outside-math"),
                          (r"(?<!\\)_", "subscript-outside-math")):
            for m in re.finditer(tok, outside):
                fails.append((n, name, line.strip()[:70]))
    # 4 undefined ref/cite keys
    labels = set(re.findall(r"\\label\{([^}]+)\}", src))
    bibkeys = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", src))
    for m in re.finditer(r"\\ref\{([^}]+)\}", src):
        if m.group(1) not in labels:
            fails.append((src[:m.start()].count("\n") + 1, "undefined-ref", m.group(1)))
    for m in re.finditer(r"\\cite[a-z]*\{([^}]+)\}", src):
        for key in (k.strip() for k in m.group(1).split(",")):
            if key and key not in bibkeys:
                fails.append((src[:m.start()].count("\n") + 1, "undefined-cite", key))
    for n, kind, ctx in sorted(fails):
        print(f"line {n:5d}  {kind:26s} {ctx}")
    print(f"{path}: {len(fails)} finding(s)" if fails else f"{path}: clean "
          f"({len(lines)} lines, {len(labels)} labels, {len(bibkeys)} bib keys)")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

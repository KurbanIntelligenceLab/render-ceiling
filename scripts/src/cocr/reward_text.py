"""
A4 text-domain reward server — the replication port of cocr.reward.

Mirrors src/cocr/reward.py one-for-one so the process-vs-outcome contrast is the SAME
manipulation in a different domain. The only thing that changes is what makes a step
verifiable:

    CoCr (VLM)   step targets are deterministic from the source CIF (spglib/pymatgen)
    A4   (text)  step targets are deterministic from a CALCULATOR (exact rational arithmetic)

In both cases NO MODEL is in the loop. That is the substantive differentiation from
StepGRPO (arXiv 2503.12937), whose key steps are GPT-4-extracted. Preserving that
property is the whole point of the replication — a text harness that used an LLM judge
for step rewards would replicate the wrong thing.

Chain schema (A4):
    [PLAN]  one-line restatement                (format only, not scored for content)
    [STEP]  <arithmetic expression> = <result>  (per-step verifiable, repeatable)
    [ANSWER] <number>                           (final reward)

FORMAT reward mirrors reward.py exactly: +1 well-formed and terminating, 0.0 terminates
but malformed, -1 never terminates. The -1 branch is what starves the repetition trap
(the text analogue of the MOTIF loop that sank the pure-SFT chains in CP2).

REWARD-HACKING GUARD (the E4 audit lesson, ported forward). A step whose arithmetic is
merely internally true ("1+1=2") is trivially emittable and would let the process arms
farm dense reward without doing the problem. So a step earns FULL credit only if it is
both ARITHMETICALLY correct and GROUNDED: every operand must trace to a number stated in
the question or to the result of an earlier step. Ungrounded-but-true steps earn partial
credit and are counted separately in the log so the audit can report the hacking rate
straight rather than hiding it inside the mean.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

SECTIONS = ["PLAN", "STEP", "ANSWER"]

# credit for a step that is arithmetically true but whose operands are not grounded
# in the question or in a previous step (see REWARD-HACKING GUARD above)
UNGROUNDED_CREDIT = 0.25

# Small integer constants a solver legitimately introduces ("half" -> 2, "dozen" -> 12,
# percent -> 100). Without this the gold chain's own "48 / 2 = 24" is scored ungrounded
# because 2 never appears in the question — i.e. correct reasoning would be PENALIZED.
# Caught by the adversarial smoke test before any training run.
FREE_CONSTANTS = {Fraction(n) for n in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 24, 52, 60,
                                        100, 365, 1000)} | {Fraction(1, 2), Fraction(1, 4)}

# Numbers: allow a LEADING DECIMAL (".01", ".5"). GSM8K's human solutions write percentages
# that way and the first version of this regex scored 59/1666 gold steps unscoreable.
_NUM = re.compile(r"\d*\.\d+|\d+")
_SIGNED_NUM = re.compile(r"-?\d*\.?\d+")   # RESULT side only; operands stay unsigned
_TOKEN = re.compile(r"\d*\.\d+|\d+|[()+\-*/]|\s+")


def operands_of(lhs: str) -> set:
    """The numeric LITERALS on the left-hand side, via the tokenizer — not a bare regex.

    A regex with an optional leading '-' reads "100-50-30-15" as {100, -50, -30, -15},
    so none of the operands match the positive values in the grounding pool and a
    perfectly grounded human step is scored ungrounded. This was the single largest
    scorer defect found against real GSM8K gold chains (333 of 1666 steps). Tokenizing
    keeps '-' an OPERATOR and yields {100, 50, 30, 15}.
    """
    out, pos = set(), 0
    while pos < len(lhs):
        m = _TOKEN.match(lhs, pos)
        if not m:
            return out
        t = m.group(0)
        pos = m.end()
        if not t.isspace() and _NUM.fullmatch(t):
            out.add(_to_frac(t))
    return out


def _is_trivial(operands: set, result) -> bool:
    """A step that performs no work.

      - the result just restates an operand (x*1, x+0)  -> no new quantity produced
      - a single distinct operand yielding 0 (x - x)    -> self-cancellation

    NOTE the earlier version also called any single-distinct-operand step trivial, which
    wrongly zeroed legitimate squarings like "2*2=4" (97 of 1666 gold steps). Squaring
    does real work; self-cancellation does not.
    """
    if result in operands:
        return True
    return len(operands) == 1 and result == 0


def _to_frac(tok: str) -> Fraction:
    """Exact rational parse — avoids float error deciding a reward."""
    return Fraction(tok)


def safe_eval(expr: str) -> Fraction | None:
    """Evaluate a pure-arithmetic expression exactly. Returns None if not evaluable.

    Deliberately NOT python eval: the string comes from a language model, so only
    digits, the four operators and parentheses are accepted. Anything else -> None
    (unscoreable step), never an exception and never arbitrary execution.
    """
    if not expr or len(expr) > 200:
        return None
    # a single operand with a runaway digit count is not arithmetic a solver produced,
    # and exact-rational ops on it are needlessly expensive
    if any(len(t) > 30 for t in _NUM.findall(expr)):
        return None
    pos, toks = 0, []
    while pos < len(expr):
        m = _TOKEN.match(expr, pos)
        if not m:
            return None                      # illegal character -> unscoreable
        t = m.group(0)
        pos = m.end()
        if not t.isspace():
            toks.append(t)
    if not toks:
        return None

    # recursive-descent over (+,-) / (*,/) / atom, on exact Fractions
    i = 0

    def atom():
        nonlocal i
        if i < len(toks) and toks[i] == "(":
            i += 1
            v = expr_()
            if v is None or i >= len(toks) or toks[i] != ")":
                return None
            i += 1
            return v
        if i < len(toks) and toks[i] == "-":      # unary minus
            i += 1
            v = atom()
            return None if v is None else -v
        if i < len(toks) and _NUM.fullmatch(toks[i]):
            v = _to_frac(toks[i])
            i += 1
            return v
        return None

    def term():
        nonlocal i
        v = atom()
        if v is None:
            return None
        while i < len(toks) and toks[i] in "*/":
            op = toks[i]
            i += 1
            r = atom()
            if r is None:
                return None
            if op == "/":
                if r == 0:
                    return None               # division by zero -> unscoreable
                v = v / r
            else:
                v = v * r
        return v

    def expr_():
        nonlocal i
        v = term()
        if v is None:
            return None
        while i < len(toks) and toks[i] in "+-":
            op = toks[i]
            i += 1
            r = term()
            if r is None:
                return None
            v = v + r if op == "+" else v - r
        return v

    v = expr_()
    return v if i == len(toks) else None       # trailing junk -> unscoreable



def _f(x) -> float | None:
    """float() for LOGGING only. A model can emit a number with a huge exponent
    (e.g. a runaway digit string), and Fraction -> float then raises OverflowError,
    which would crash the reward server mid-training. Reward decisions themselves are
    always made on exact Fractions; only the log value degrades to None."""
    try:
        return float(x)
    except (OverflowError, ValueError):
        return None


def parse_chain(text: str) -> dict[str, Any]:
    """Split an emitted A4 chain into PLAN / ordered STEP list / ANSWER."""
    tags = list(re.finditer(r"\[([A-Z]+)\]", text))
    steps: list[str] = []
    plan, answer = None, None
    order: list[str] = []
    for i, mt in enumerate(tags):
        name = mt.group(1)
        if name not in SECTIONS:
            continue
        order.append(name)
        start = mt.end()
        end = tags[i + 1].start() if i + 1 < len(tags) else len(text)
        body = text[start:end].strip()
        if name == "STEP":
            steps.append(body)
        elif name == "PLAN" and plan is None:
            plan = body
        elif name == "ANSWER" and answer is None:
            answer = body
    return {"plan": plan, "steps": steps, "answer": answer, "tag_order": order}


def _final_number(ans_text: str | None) -> Fraction | None:
    if not ans_text:
        return None
    m = _NUM.search(ans_text.replace(",", ""))
    return _to_frac(m.group(0)) if m else None


def score_chain(text: str, label: dict[str, Any]) -> dict[str, Any]:
    """Score an emitted A4 chain. Mirrors cocr.reward.score_chain's return contract.

    label = {"question": str, "answer": float|str}

    Returns per_step (a LIST here, since step count varies by problem — the VLM chain
    had a fixed 6 slots), final_reward, format_reward, and a decision log carrying the
    reward-hacking counters.
    """
    p = parse_chain(text)
    steps, order = p["steps"], p["tag_order"]
    log: dict[str, Any] = {}

    # ---- FORMAT: PLAN once, >=1 STEP, terminating ANSWER, canonical order ----
    has_plan = order.count("PLAN") == 1
    has_steps = len(steps) >= 1
    n_ans = order.count("ANSWER")
    final_val = _final_number(p["answer"])
    terminates = n_ans >= 1 and final_val is not None
    # canonical order: PLAN before every STEP, ANSWER last
    canonical = False
    if terminates and has_plan and has_steps:
        canonical = (order[0] == "PLAN" and order[-1] == "ANSWER"
                     and all(t == "STEP" for t in order[1:-1]))
    if canonical and n_ans == 1:
        fmt = 1.0
    elif terminates:
        fmt = 0.0
    else:
        fmt = -1.0            # never terminated -> hard penalty (repetition trap)
    log["format"] = {"has_plan": has_plan, "n_steps": len(steps), "terminates": terminates,
                     "canonical": canonical, "n_answer": n_ans, "reward": fmt}

    # ---- grounding pool: numbers stated in the question, plus results of prior steps ----
    q_nums = {_to_frac(m) for m in _NUM.findall(str(label.get("question", "")).replace(",", ""))}
    # NOTE _NUM no longer carries a sign, so question operands are positive literals,
    # matching how operands_of() reads the left-hand side of a step.
    available = set(q_nums)
    derived = set(q_nums)   # values traceable to the QUESTION (see grounding note below)

    per_step: list[float] = []
    seen_sigs: set = set()
    step_log: list[dict[str, Any]] = []
    n_correct = n_grounded = n_ungrounded_true = n_unscoreable = n_trivial = 0

    for s in steps:
        # A [STEP] body frequently carries material that is not part of the arithmetic:
        #   - currency/percent symbols     "$10 + $8 = $18"
        #   - a trailing narration line    "50 * 2 = 100\n\nStep 2: Calculate ..."
        #   - an echo of the prompt template itself
        # These are PRESENTATION, not reasoning errors, and scoring them as unscoreable
        # understates faithfulness (35.8% of SFT-model steps, diagnosed on real rollouts).
        # Normalise them away; anything still unparseable is genuinely not arithmetic
        # (e.g. symbolic algebra "r = 2g"), which stays unscoreable by design.
        body = s.split("\n")[0]                      # first line only — drop trailing prose
        body = body.replace(",", "")
        body = re.sub(r"[$£€%]", "", body)            # currency / percent markers
        body = re.sub(r"\*\*|__", "", body)            # markdown emphasis
        if "<arithmetic>" in body or "one per line" in body:
            body = ""                                  # prompt-template echo
        # a leading "1)" / "1." / "1:" / bare "1 " step number left over from markdown
        # numbering ("**1**  $10 + $8 = $18") would otherwise become a stray operand
        body = re.sub(r"^\s*\d+\s*[).:]\s+", "", body)
        body = re.sub(r"^\s*(?:Step|STEP)\s*\d*\s*[).:]?\s*", "", body)
        if "=" in body:
            _lhs_probe = body.rsplit("=", 1)[0]
            m_lead = re.match(r"^\s*(\d+)\s{2,}(?=[\d(])", _lhs_probe)
            if m_lead:                                 # "1  10 + 8" -> "10 + 8"
                body = body[m_lead.end():]
        # accept "lhs = rhs" (last '=' wins, so "a=b=c" reads as (a=b)=c)
        if "=" not in body:
            per_step.append(0.0)
            step_log.append({"step": s[:60], "verdict": "no_equals", "reward": 0.0})
            n_unscoreable += 1
            continue
        lhs, rhs = body.rsplit("=", 1)
        # The RESULT side may legitimately be negative ("5 - 9 = -4"). _NUM is deliberately
        # UNSIGNED — that is the fix for the operand-grounding bug, where "100-50-30" wrongly
        # tokenized -50/-30 as negative operands. But applying it to the RHS made every step
        # with a negative result score arith_ok=False (found while validating Reasoning Gym
        # chains, where negatives are common; GSM8K gold has only 7/23716 such steps, so no
        # published A4 number changes). Read the RHS with an explicit optional sign.
        lhs_v, rhs_m = safe_eval(lhs.strip()), _SIGNED_NUM.search(rhs.strip())
        if lhs_v is None or rhs_m is None:
            per_step.append(0.0)
            step_log.append({"step": s[:60], "verdict": "unscoreable", "reward": 0.0})
            n_unscoreable += 1
            continue
        rhs_v = _to_frac(rhs_m.group(0))
        arith_ok = (lhs_v == rhs_v)
        operands = operands_of(lhs)
        # GROUNDED requires (a) every operand traceable to the question, a prior result,
        # or a small universal constant, AND (b) at least ONE operand that is genuinely
        # problem-specific. Clause (b) is what stops a chain of free-constant identities
        # ("1+1=2", "2+2=4") from farming full credit while doing none of the problem.
        all_ok = len(operands) > 0 and operands.issubset(available | FREE_CONSTANTS)
        # "problem-specific" means derived from the QUESTION, not merely present in the
        # pool: a step's own result enters `available`, so a chain of free-constant
        # identities ("1+1=2" then "2+2=4") would otherwise bootstrap its own grounding.
        # `derived` tracks only values traceable to the question.
        uses_problem_number = bool(operands & derived)
        grounded = all_ok and uses_problem_number
        trivial = _is_trivial(operands, rhs_v)
        # REPEAT: the same computation emitted twice earns credit once. Keyed on the
        # operand multiset + result, NOT on "the result is already known" — a genuine
        # step whose value coincides with an earlier number is not a repeat (that
        # over-broad rule zeroed 104 of 1666 legitimate gold steps).
        sig = (tuple(sorted(operands)), rhs_v)
        novel = sig not in seen_sigs
        seen_sigs.add(sig)

        if arith_ok and (trivial or not novel):
            r = 0.0                        # true but does no work -> no credit, audited
            n_correct += 1
            n_trivial += 1
        elif arith_ok and grounded:
            r = 1.0
            n_correct += 1
            n_grounded += 1
        elif arith_ok:
            r = UNGROUNDED_CREDIT          # true but not traceable -> partial, audited
            n_correct += 1
            n_ungrounded_true += 1
        else:
            r = 0.0
        per_step.append(r)
        step_log.append({"step": s[:60], "lhs": _f(lhs_v), "rhs": _f(rhs_v),
                         "arith_ok": arith_ok, "grounded": grounded,
                         "trivial": trivial, "novel": novel, "reward": r})
        # a step's RESULT becomes available to later steps regardless of grounding,
        # so a long chain is not punished for building on its own earlier work
        available.add(rhs_v)
        # ...but it only counts as PROBLEM-DERIVED if the step that produced it actually
        # used a problem-derived quantity. This keeps grounding from bootstrapping.
        if uses_problem_number:
            derived.add(rhs_v)

    # ---- FINAL answer reward ----
    # A label answer is not always a bare number: Reasoning Gym renders prime factorizations
    # as "2 \u00d7 433" and countdown answers as expressions. _to_frac raises on those, which
    # crashed the synthesizer validation. Non-numeric answers get a string comparison instead
    # of an exception; the numeric path is unchanged.
    try:
        true_v = _to_frac(str(label["answer"]).replace(",", "").strip())
    except (ValueError, ZeroDivisionError):
        true_v = None            # non-numeric label -> exact-string comparison below
    if true_v is None:
        emitted_s = (p["answer"] or "").strip()
        norm = lambda t: str(t).strip().replace(" ", "")
        final_reward = 1.0 if norm(emitted_s) == norm(label["answer"]) else 0.0
        log["final"] = {"emitted": emitted_s, "truth": str(label["answer"]),
                        "reward": final_reward, "non_numeric_answer": True}
    else:
        final_reward = 1.0 if (final_val is not None and final_val == true_v) else 0.0
        log["final"] = {"emitted": _f(final_val) if final_val is not None else None,
                        "truth": _f(true_v), "reward": final_reward}
    log["steps"] = step_log
    log["hacking_audit"] = {"n_steps": len(steps), "n_arith_correct": n_correct,
                            "n_grounded": n_grounded,
                            "n_ungrounded_true": n_ungrounded_true,
                            "n_trivial_or_repeat": n_trivial,
                            "n_unscoreable": n_unscoreable}

    return {"per_step": per_step, "final_reward": final_reward,
            "format_reward": fmt, "log": log}


def score_outcome(text: str, label: dict[str, Any]) -> dict[str, Any]:
    """B3-text arm: final answer only, mirroring cocr.reward.score_outcome.

    Same fallback as the VLM version — if no [ANSWER] tag parses, take the LAST number
    anywhere in the text, so the outcome arm is never disadvantaged by a formatting slip
    that the process arms' format term would also see. (Matched-arm discipline.)
    """
    p = parse_chain(text)
    final_val = _final_number(p["answer"])
    if final_val is None:
        nums = _NUM.findall(text.replace(",", ""))
        final_val = _to_frac(nums[-1]) if nums else None
    # A label answer is not always a bare number: Reasoning Gym renders prime factorizations
    # as "2 \u00d7 433" and countdown answers as expressions. _to_frac raises on those, which
    # crashed the synthesizer validation. Non-numeric answers get a string comparison instead
    # of an exception; the numeric path is unchanged.
    try:
        true_v = _to_frac(str(label["answer"]).replace(",", "").strip())
    except (ValueError, ZeroDivisionError):
        emitted = (p["answer"] or "").strip()
        exact = emitted.replace(" ", "") == str(label["answer"]).strip().replace(" ", "")
        return {"format_reward": fmt, "per_step": per_step,
                "final_reward": 1.0 if exact else 0.0,
                "log": {"steps": step_log, "hacking_audit": audit, "non_numeric_answer": True}}
    return {"final_reward": 1.0 if (final_val is not None and final_val == true_v) else 0.0,
            "emitted": _f(final_val) if final_val is not None else None,
            "truth": _f(true_v)}

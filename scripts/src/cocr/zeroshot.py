"""
CoCr E1 — zero-shot symmetry-perception probe.

Evaluates VLMs (via OpenRouter, OpenAI-compatible chat/completions with image inputs)
zero-shot on four crystallographic perception tasks, sweeping view count, with a
contamination-control (perturbed re-render) arm. No training.

Tasks (each with a strict parseable answer format scored against the pipeline labels):
  crystal_system  : 7-way classification
  lattice_angles  : read alpha/beta/gamma (degrees) from the cell
  space_group_topk: name up to k candidate space-group numbers (top-k accuracy)
  coordination    : coordination number of a specified element

Answer parsing keys on a required final "ANSWER: ..." line so scoring is deterministic.
"""
from __future__ import annotations

import base64
import json
import os
import re
import time
import urllib.request
from typing import Any

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

CRYSTAL_SYSTEMS = ["triclinic", "monoclinic", "orthorhombic", "tetragonal",
                   "trigonal", "hexagonal", "cubic"]


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _img_block(path: str) -> dict:
    return {"type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{_b64(path)}"}}


# ---- task prompts -----------------------------------------------------------
_PREAMBLE = (
    "You are shown {n} ball-and-stick rendering(s) of the SAME crystal structure's "
    "conventional unit cell, viewed from different fixed camera angles. Unit-cell "
    "edges are drawn. Atom colors distinguish chemical elements. Use only what you "
    "can see in the images.\n\n"
)

TASKS = {
    "crystal_system": {
        "prompt": _PREAMBLE + (
            "Identify the CRYSTAL SYSTEM of this structure. Choose exactly one of: "
            "triclinic, monoclinic, orthorhombic, tetragonal, trigonal, hexagonal, cubic.\n"
            "Reason briefly, then end with a line exactly of the form:\n"
            "ANSWER: <one crystal system>"),
    },
    "lattice_angles": {
        "prompt": _PREAMBLE + (
            "Estimate the three unit-cell angles alpha, beta, gamma in degrees from the "
            "cell-edge geometry. End with a line exactly of the form:\n"
            "ANSWER: alpha=<deg>, beta=<deg>, gamma=<deg>"),
    },
    "space_group_topk": {
        "prompt": _PREAMBLE + (
            "Give your best {k} candidate SPACE GROUP numbers (International Tables "
            "1-230), most likely first. End with a line exactly of the form:\n"
            "ANSWER: <n1>, <n2>, ... (up to {k} integers)"),
    },
    "coordination": {
        "prompt": _PREAMBLE + (
            "Estimate the COORDINATION NUMBER (number of nearest-neighbor atoms) of a "
            "{element} atom in this structure. End with a line exactly of the form:\n"
            "ANSWER: <integer>"),
    },
}


def build_messages(task: str, image_paths: list[str], **kw) -> list[dict]:
    p = TASKS[task]["prompt"].format(n=len(image_paths),
                                     k=kw.get("k", 5),
                                     element=kw.get("element", "the metal"))
    content = [{"type": "text", "text": p}] + [_img_block(x) for x in image_paths]
    return [{"role": "user", "content": content}]


def query_openrouter(model: str, messages: list[dict], api_key: str | None = None,
                     max_tokens: int = 1024, temperature: float = 0.0,
                     retries: int = 2, timeout: int = 60) -> dict:
    key = api_key or os.environ["OPENROUTER_API_KEY"]
    body = json.dumps({"model": model, "messages": messages,
                       "max_tokens": max_tokens, "temperature": temperature}).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                OPENROUTER_URL, data=body,
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.load(r)
            txt = d["choices"][0]["message"].get("content")
            usage = d.get("usage", {})
            # Some models return a valid response with null/empty content (refusal,
            # length-cap with no text, filter). Treat as a non-crashing failure so the
            # thread pool records it and moves on instead of raising.
            if not txt:
                return {"text": "", "usage": usage, "ok": False,
                        "error": "empty_content", "finish": d["choices"][0].get("finish_reason")}
            return {"text": txt, "usage": usage, "ok": True}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:150]}"
            time.sleep(2 * (attempt + 1))
    return {"text": "", "usage": {}, "ok": False, "error": last}


# ---- answer parsing + scoring ----------------------------------------------
def _answer_line(text: str) -> str:
    if not text:
        return ""
    m = list(re.finditer(r"ANSWER:\s*(.+)", text, re.IGNORECASE))
    return m[-1].group(1).strip() if m else ""


def score_crystal_system(text: str, truth: str) -> bool:
    a = _answer_line(text).lower()
    found = [s for s in CRYSTAL_SYSTEMS if s in a]
    return len(found) == 1 and found[0] == truth.lower()


def score_lattice_angles(text: str, truth: tuple[float, float, float],
                         tol: float = 5.0) -> dict:
    a = _answer_line(text)
    nums = re.findall(r"(?:alpha|beta|gamma)\s*=\s*([0-9.]+)", a, re.IGNORECASE)
    if len(nums) != 3:
        nums = re.findall(r"([0-9]{2,3}(?:\.[0-9]+)?)", a)
    if len(nums) < 3:
        return {"ok": False, "parsed": None}
    got = [float(x) for x in nums[:3]]
    err = [abs(g - t) for g, t in zip(got, truth)]
    return {"ok": all(e <= tol for e in err), "parsed": got, "abs_err": err}


def score_space_group_topk(text: str, truth: int, k: int = 5) -> dict:
    a = _answer_line(text)
    nums = [int(x) for x in re.findall(r"\b([0-9]{1,3})\b", a) if 1 <= int(x) <= 230][:k]
    return {"top1": bool(nums) and nums[0] == truth,
            "topk": truth in nums, "parsed": nums}


def score_coordination(text: str, truth: int, tol: int = 0) -> dict:
    a = _answer_line(text)
    m = re.search(r"\b([0-9]{1,2})\b", a)
    if not m:
        return {"ok": False, "parsed": None}
    got = int(m.group(1))
    return {"ok": abs(got - truth) <= tol, "parsed": got, "exact": got == truth}

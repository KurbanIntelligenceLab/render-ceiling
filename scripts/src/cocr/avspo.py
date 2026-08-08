"""
AVSPO — Adaptive Virtual Sample Policy Optimization (arXiv 2605.21125, ICML 2026).

REIMPLEMENTED FROM THE PAPER, NOT FROM THE AUTHORS' CODE. The repository named in our brief
(github.com/hexixiang/Advantage-Collapse-Rate) contains only a LICENSE and a one-line README
at commit d20d3ac — zero Python files. The paper's own link is qingyonghu.github.io/AVSPO.
Every equation and constant below is transcribed from the arXiv HTML (2605.21125v1) §4.1-4.2;
paper equation numbers are cited inline so a reader can check the transcription.

WHY IT MATTERS FOR US: AVSPO restores gradient by injecting VIRTUAL REWARD VALUES into the
normalization statistics while keeping the OUTCOME objective — so the restored gradient still
points at final-answer correctness. Our process arms instead add a different objective (step
correctness), so the restored gradient points at a proxy. That contrast is the whole point of
the three-arm comparison: same mechanism relief, different target.

NOTE ON ACR vs OUR STATISTIC: ACR (Eq. 6) is the fraction of groups whose reward SD is below
tau=1e-6. Our frac_reward_zero_std is the fraction of groups with max-min < 1e-9. These are
the same quantity at a marginally stricter tolerance, so our published silent-group rates ARE
ACR values and the collapse-reduction magnitudes are directly comparable.
"""
from __future__ import annotations

import math

# Paper defaults, §4.2. Do not silently retune these — a "tuned AVSPO" is not AVSPO.
ALPHA = 0.5          # sensitivity, Eq. 8; paper: "Setting alpha = 0.5 provides effective scaling"
R_ANCHOR = 0.1       # Eq. 9; paper: "we use r_anchor = 0.1 in all experiments"
TAU_ADAPT_INIT = 0.5 # Eq. 10; "initialized conservatively"
ETA = 0.01           # Eq. 10 threshold learning rate
TAU_COLLAPSE = 1e-6  # Eq. 6 numerical-precision threshold


def group_sd(rewards) -> float:
    """Population SD of a group's rewards (Eq. 6 uses 1/G, i.e. ddof=0)."""
    g = len(rewards)
    if g == 0:
        return 0.0
    mu = sum(rewards) / g
    return math.sqrt(sum((r - mu) ** 2 for r in rewards) / g)


def acr(groups) -> float:
    """Advantage Collapse Rate, Eq. 6: fraction of groups with reward SD < tau."""
    if not groups:
        return 0.0
    return sum(1 for g in groups if group_sd(g) < TAU_COLLAPSE) / len(groups)


def n_virtual(group_size: int, acr_n: float, alpha: float = ALPHA) -> int:
    """Eq. 8: K = max(1, min(G, ceil(G * ACR^alpha)))."""
    return max(1, min(group_size, math.ceil(group_size * (acr_n ** alpha))))


def virtual_rewards(observed, k: int, r_anchor: float = R_ANCHOR) -> list:
    """Eq. 9, stratified assignment.

    r_obs = max(R_j).
      r_obs > 0 : r_vk = r_obs * (1 - k/(K+1))      -> spreads BELOW the observed value
      r_obs = 0 : r_vk = r_anchor * (K-k+1)/K       -> spreads ABOVE zero
    Handles both all-correct and all-incorrect collapse, which is why it is "stratified".
    """
    r_obs = max(observed) if observed else 0.0
    if r_obs > 0:
        return [r_obs * (1.0 - kk / (k + 1)) for kk in range(1, k + 1)]
    return [r_anchor * (k - kk + 1) / k for kk in range(1, k + 1)]


class AVSPOState:
    """Adaptive triggering, Eq. 10. Carries tau_adapt, the previous batch reward, and the
    ACR WINDOW.

    WHY THE WINDOW EXISTS (this is the attempt-2 bug fix, see FINDING_4A_NOT_SCOREABLE.md).
    Eq. 6 defines ACR over a BATCH of N prompt-groups. Under TRL with group_size 8 and
    micro_bs 4, the reward function receives ONE group per call, so a per-call ACR is binary
    {0, 1}: it equals 1.0 whenever that single group collapsed, and 1.0 exceeds tau_adapt for
    any tau < 1. The adaptive trigger was therefore INERT and every collapsed group was
    augmented unconditionally — strictly more aggressive than the published method. The
    diagnostic that exposed it: frac_groups_augmented came out EXACTLY equal to mean_acr in all
    six runs.

    The fix accumulates each group's collapse indicator in a rolling window approximating one
    optimizer step, and evaluates ACR over that window. ACR can then lie strictly between 0 and
    1, which is the condition Eq. 10 needs to gate anything. The invariant to check afterwards
    is frac_augmented < mean_acr; exact equality means the trigger is still inert.
    """

    def __init__(self, tau_adapt: float = TAU_ADAPT_INIT, eta: float = ETA,
                 window: int = 16):
        self.tau_adapt = tau_adapt
        self.eta = eta
        self.prev_J = None
        self.n_augmented = 0
        self.n_groups = 0
        self.window = window
        self._collapsed_hist: list = []   # 1 if that group collapsed, else 0
        self._reward_hist: list = []      # per-rollout rewards, for Jhat over the window

    def windowed_acr(self) -> float:
        """ACR (Eq. 6) over the rolling window of recent groups, not over one group."""
        h = self._collapsed_hist[-self.window:]
        return (sum(h) / len(h)) if h else 0.0

    def observe(self, groups) -> None:
        """Record this call's groups into the window BEFORE the trigger is evaluated."""
        for g in groups:
            self._collapsed_hist.append(1 if group_sd(g) < TAU_COLLAPSE else 0)
            self._reward_hist.extend(g)
        cap = max(self.window * 4, 64)
        if len(self._collapsed_hist) > cap:
            self._collapsed_hist = self._collapsed_hist[-cap:]
        if len(self._reward_hist) > cap * 8:
            self._reward_hist = self._reward_hist[-cap * 8:]

    def windowed_J(self) -> float:
        """Jhat over the window: mean reward, Eq. 10's policy-improvement estimate."""
        h = self._reward_hist[-self.window * 8:]
        return (sum(h) / len(h)) if h else 0.0

    def update_threshold(self, acr_n: float, J_n: float) -> None:
        """tau <- tau + eta * sign(dJ) * (ACR - tau).

        dJ = Jhat(theta_n) - Jhat(theta_{n-1}), Jhat = mean batch reward. On the first
        iteration there is no previous J, so the threshold is left at its initial value
        (the paper defines dJ only for n >= 1).
        """
        if self.prev_J is not None:
            dJ = J_n - self.prev_J
            s = (dJ > 0) - (dJ < 0)
            self.tau_adapt += self.eta * s * (acr_n - self.tau_adapt)
        self.prev_J = J_n


def avspo_advantages(groups, state: AVSPOState):
    """Return per-rollout advantages with AVSPO augmentation applied where triggered.

    Conditional integration (paper, §4.2): virtual samples enter the normalization
    statistics ONLY when ACR^(n) > tau_adapt^(n) AND that specific group has collapsed.
    Virtual samples never receive a gradient term — they are reward values only, so the
    returned advantage list has exactly one entry per REAL rollout.
    """
    # BATCH-LEVEL ACR. The window is updated first, then ACR and Jhat are read from it, so
    # the trigger sees a batch-scale statistic rather than this call's single group.
    state.observe(groups)
    acr_n = state.windowed_acr()
    J_n = state.windowed_J()
    state.update_threshold(acr_n, J_n)
    trigger = acr_n > state.tau_adapt

    out = []
    for g in groups:
        state.n_groups += 1
        sd = group_sd(g)
        pool = list(g)
        if trigger and sd < TAU_COLLAPSE:
            pool = pool + virtual_rewards(g, n_virtual(len(g), acr_n))
            state.n_augmented += 1
        mu = sum(pool) / len(pool)
        sd2 = group_sd(pool)
        # real rollouts only; virtual entries shift mu/sd but carry no gradient
        out.extend([(r - mu) / (sd2 + 1e-8) for r in g])
    return out, {"acr": acr_n, "tau_adapt": state.tau_adapt, "triggered": bool(trigger)}

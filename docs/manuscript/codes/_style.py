"""Shared style for CoCr figures. Import before plotting.

R12: every figure is drawn at the ICLR text-column width (5.5in) and every
font role is fixed at 8pt, so that \\includegraphics[width=\\linewidth] with
no extra scaling places text at exactly 8pt. Output is vector PDF.
"""
import matplotlib as mpl

TEXTWIDTH_IN = 5.5  # ICLR 2027 single-column text width, inches
FONT_PT = 8.0        # every role uses this size (R12 rule: no size ladder)

# Digital Discovery (RSC two-column) placement width. The template's
# \textwidth measures 528.93675pt, so \includegraphics[width=0.92\textwidth]
# places a figure at 486.62pt = 6.7333in = 17.10cm, which is exactly the RSC
# double-column figure width. Drawing at this size means no rescaling, so
# FONT_PT lands at 8pt on the page.
DDWIDTH_IN = 6.7333

# ESI placement width. The ESI is single-column with 2.2cm margins, so
# \linewidth measures 472.31595pt = 6.5354in; drawing at that width and
# including at width=\linewidth again means no rescaling.
SIWIDTH_IN = 6.5354


def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 300, "savefig.facecolor": "white",
        "font.size": FONT_PT, "axes.titlesize": FONT_PT, "axes.labelsize": FONT_PT,
        "xtick.labelsize": FONT_PT, "ytick.labelsize": FONT_PT,
        "legend.fontsize": FONT_PT, "figure.titlesize": FONT_PT,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": True, "legend.framealpha": 0.95,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })

CHANCE = 1.0 / 7.0

# --- Digital Discovery: shared per-model marker identity -------------------
# Model identity is a (marker, colour) pair assigned once, in a fixed order, so
# the same model reads the same way in every panel of every figure that uses
# this key. Names are wrapped at a hyphen for the two-row roster key: the full
# identifier is preserved, only the line break is added, so no label is
# abbreviated or truncated.
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "<", ">", "p", "h", "*", "d", "8"]
MODEL_COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#8c564b", "#e377c2",
                "#7f7f7f", "#bcbd22", "#17becf", "#ff7f0e", "#393b79", "#8c6d31",
                "#843c39", "#5254a3"]


def model_styles(names):
    """(marker, colour) per model, in the order given."""
    return {n: (MARKERS[i % len(MARKERS)], MODEL_COLORS[i % len(MODEL_COLORS)])
            for i, n in enumerate(names)}


def panel_letter(ax, letter, dx=0.0, dy=1.0):
    """Draw a bold panel letter at the panel's top-left, in axes coordinates.

    DD: multi-panel figures carry (a)/(b) here instead of per-panel titles; the
    claim they used to state lives in the figure caption, so it is made once.
    """
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes, ha="left",
            va="bottom", fontsize=FONT_PT, weight="bold", color="#111")


def wrap_label(name, min_len=11):
    """Break a model identifier at the hyphen that most evens the two lines.

    Nothing is dropped: the wrapped form joined on '-' is the original. Short
    identifiers are left on one line. Wrapping is what makes a two-row,
    seven-column roster key fit the RSC double-column width at 8pt.
    """
    if len(name) < min_len or "-" not in name:
        return name
    parts = name.split("-")
    best = None
    for k in range(1, len(parts)):
        a = "-".join(parts[:k]) + "-"
        b = "-".join(parts[k:])
        cost = max(len(a), len(b))
        if best is None or cost < best[0]:
            best = (cost, a + "\n" + b)
    return best[1]


def save_pdf(fig, out):
    """Write a byte-reproducible vector PDF.

    matplotlib stamps a wall-clock /CreationDate into every PDF, so two runs of
    the same script differ in bytes while being pixel-identical. That defeats a
    md5 reproduction check on the shipped figure. Pinning the date makes the
    output a pure function of the data and the code, which is what the release's
    validator asserts.

    Explicit margins are set by the caller via subplots_adjust; this helper
    deliberately does NOT pass bbox_inches="tight", which would crop the page
    below the placement width and reintroduce LaTeX rescaling.
    """
    fig.savefig(out, metadata={"CreationDate": None})

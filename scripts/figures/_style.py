"""Shared style for CoCr figures. Import before plotting."""
import matplotlib as mpl

def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.facecolor": "white",
        "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": True, "legend.framealpha": 0.95,
    })

CHANCE = 1.0 / 7.0

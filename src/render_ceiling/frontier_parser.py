SYS = ["cubic", "hexagonal", "monoclinic", "orthorhombic", "tetragonal", "triclinic", "trigonal"]


def parse_system(text):
    """Last-mention fallback, same convention as the trained-arm scorer."""
    if not text:
        return None
    t = text.lower()
    hits = [(t.rfind(s), s) for s in SYS if s in t]
    hits = [(i, s) for i, s in hits if i >= 0]
    return max(hits)[1] if hits else None

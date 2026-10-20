"""Pairwise Manglik (Kuja dosha) compatibility."""
def manglik_match(mb: dict, mg: dict) -> dict:
    b, g = mb.get("is_manglik"), mg.get("is_manglik")
    sev = {"none": 0, "low": 1, "medium": 2, "high": 3}
    if b and g: v = "Both are Manglik — the doshas cancel each other; compatible."
    elif not b and not g: v = "Neither is Manglik — no Mangal dosha concern."
    else:
        who = "boy" if b else "girl"; m = mb if b else mg
        if m.get("cancellations") or sev.get(m.get("severity"), 2) <= 1:
            v = f"Only the {who} is Manglik, but the dosha is mild/cancelled — generally acceptable."
        else:
            v = f"Only the {who} is Manglik — traditionally a mismatch unless cancelled by other factors; remedies advised."
    return {"boy": {k: mb.get(k) for k in ("is_manglik", "severity", "cancellations")},
            "girl": {k: mg.get(k) for k in ("is_manglik", "severity", "cancellations")},
            "compatible": (bool(b) == bool(g)) or "acceptable" in v, "verdict": v}

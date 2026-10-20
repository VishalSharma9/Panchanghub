"""Personal day, two-city snapshot, and namakarana syllables.

Chandrabala houses 1, 3, 6, 7, 10, 11 from the birth sign are the classical
favourable set already used in panchang.compute. Tarabala uses the nine-tara
cycle. Naming syllables are the published pada aksharas (Ashwini Chu…Revati Chi).
Nothing here invents a score.
"""
from __future__ import annotations
from datetime import datetime

from .ephem import NAKSHATRAS, RASHIS, PLANETS, calc, nakshatra_of, to_utc, jd_from_utc

# (roman, devanagari) for padas 1–4. Retroflex letters keep a dot so धा and ढा stay distinct.
SYLLABLES = [
    [("Chu", "चु"), ("Che", "चे"), ("Cho", "चो"), ("La", "ला")],
    [("Li", "ली"), ("Lu", "लू"), ("Le", "ले"), ("Lo", "लो")],
    [("A", "अ"), ("I", "ई"), ("U", "उ"), ("E", "ए")],
    [("O", "ओ"), ("Va", "वा"), ("Vi", "वी"), ("Vu", "वु")],
    [("Ve", "वे"), ("Vo", "वो"), ("Ka", "का"), ("Ki", "की")],
    [("Ku", "कु"), ("Gha", "घ"), ("Nga", "ङ"), ("Chha", "छ")],
    [("Ke", "के"), ("Ko", "को"), ("Ha", "हा"), ("Hi", "ही")],
    [("Hu", "हु"), ("He", "हे"), ("Ho", "हो"), ("Da", "डा")],
    [("Di", "डी"), ("Du", "डू"), ("De", "डे"), ("Do", "डो")],
    [("Ma", "मा"), ("Mi", "मी"), ("Mu", "मू"), ("Me", "मे")],
    [("Mo", "मो"), ("Ta", "टा"), ("Ti", "टी"), ("Tu", "टू")],
    [("Te", "टे"), ("To", "टो"), ("Pa", "पा"), ("Pi", "पी")],
    [("Pu", "पु"), ("Sha", "ष"), ("Na", "ण"), ("Tha", "ठ")],
    [("Pe", "पे"), ("Po", "पो"), ("Ra", "रा"), ("Ri", "री")],
    [("Ru", "रू"), ("Re", "रे"), ("Ro", "रो"), ("Ta", "ता")],
    [("Ti", "ती"), ("Tu", "तू"), ("Te", "ते"), ("To", "तो")],
    [("Na", "ना"), ("Ni", "नी"), ("Nu", "नू"), ("Ne", "ने")],
    [("No", "नो"), ("Ya", "या"), ("Yi", "यी"), ("Yu", "यू")],
    [("Ye", "ये"), ("Yo", "यो"), ("Bha", "भा"), ("Bhi", "भी")],
    [("Bhu", "भू"), ("Dha", "धा"), ("Pha", "फा"), ("Ḍha", "ढा")],
    [("Bhe", "भे"), ("Bho", "भो"), ("Ja", "जा"), ("Ji", "जी")],
    [("Khi", "खी"), ("Khu", "खू"), ("Khe", "खे"), ("Kho", "खो")],
    [("Ga", "गा"), ("Gi", "गी"), ("Gu", "गु"), ("Ge", "गे")],
    [("Go", "गो"), ("Sa", "सा"), ("Si", "सी"), ("Su", "सू")],
    [("Se", "से"), ("So", "सो"), ("Da", "दा"), ("Di", "दी")],
    [("Du", "दू"), ("Tha", "थ"), ("Jha", "झ"), ("Nya", "ञ")],
    [("De", "दे"), ("Do", "दो"), ("Cha", "चा"), ("Chi", "ची")],
]

GOOD_CHOG = {"Good", "Gain"}


def syllable(nak_index: int, pada: int):
    """nak_index 0–26, pada 1–4."""
    roman, deva = SYLLABLES[nak_index][pada - 1]
    return {"nakshatra": NAKSHATRAS[nak_index], "pada": pada, "roman": roman, "devanagari": deva,
            "all": [{"pada": i + 1, "roman": a, "devanagari": b} for i, (a, b) in enumerate(SYLLABLES[nak_index])]}


def moon_syllable(date: str, time: str, tz: str):
    if len(time) == 5:
        time += ":00"
    dt = datetime.fromisoformat(f"{date}T{time}")
    jd = jd_from_utc(to_utc(dt, tz))
    lon, _, _ = calc(jd, PLANETS["Moon"])
    i, pada = nakshatra_of(lon)
    out = syllable(i, pada)
    out["moon_longitude"] = round(lon, 4)
    out["rashi"] = RASHIS[int(lon // 30)]
    return out


def _overlaps(a, b) -> bool:
    if not a or not b or not a.get("start") or not b.get("start"):
        return False
    return a["start"] < b["end"] and b["start"] < a["end"]


def _first(slots, avoid, now_iso):
    for s in slots:
        if _overlaps(s, avoid):
            continue
        if now_iso and s.get("end") and s["end"] <= now_iso:
            continue
        return s
    return None


def for_you(p: dict, ch: dict, rashi_i: int | None, nak_i: int | None, now_iso: str | None):
    """rashi_i and nak_i are 0-based, or None when the visitor has not set a birth star."""
    rahu = (p.get("muhurta") or {}).get("rahu_kalam")
    slots = list(ch.get("day") or []) + list(ch.get("night") or [])
    puja = _first([s for s in slots if s.get("quality") in GOOD_CHOG], rahu, now_iso)
    money = _first([s for s in slots if s.get("name") == "Labh"], rahu, now_iso)
    travel = _first([s for s in slots if s.get("name") == "Char"], rahu, now_iso)

    chandra = None
    if rashi_i is not None:
        name = RASHIS[rashi_i]
        spans = []
        for c in p.get("chandrabalam") or []:
            spans.append({"until": c.get("until"), "moon": c.get("moon_rashi"),
                          "favourable": name in (c.get("good_for") or []),
                          "ashtama": c.get("ashtama_rashi") == name})
        chandra = {"rashi": name, "now": spans[0] if spans else None, "later": spans[1:]}

    tara = None
    if nak_i is not None:
        name = NAKSHATRAS[nak_i]
        spans = []
        for t in p.get("tarabalam") or []:
            spans.append({"until": t.get("until"), "moon_nakshatra": t.get("nakshatra"),
                          "favourable": name in (t.get("good_for") or [])})
        tara = {"nakshatra": name, "now": spans[0] if spans else None, "later": spans[1:]}

    return {"chandra": chandra, "tara": tara, "abhijit": (p.get("muhurta") or {}).get("abhijit"),
            "rahu": rahu, "puja": puja, "money": money, "travel": travel}

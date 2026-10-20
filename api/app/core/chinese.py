"""Chinese astrology: zodiac by year (lunar new year), BaZi four pillars, elements, compatibility, Kua number."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import swisseph as swe
from .ephem import jd_from_utc, utc_from_jd, sun_lon, next_boundary, angdiff
from .panchang import elong

STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
STEM_EL = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
TRINES = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3, 7, 11}]
CLASH = {i: (i + 6) % 12 for i in range(12)}
CN_TZ = timezone(timedelta(hours=8))

def _sun_trop(j): return sun_lon(j, False)

def lunar_new_year(year: int):
    """Second new moon after the winter solstice (China time)."""
    j = swe.julday(year - 1, 12, 15, 0)
    ws, _ = next_boundary(_sun_trop, j, 90.0, forward=True, max_days=30, scan=1)
    t = ws; count = 0
    while True:
        e, idx = next_boundary(elong, t, 12.0, forward=True, max_days=3, scan=0.25)
        t = e + 1e-4
        if idx == 0:
            count += 1
            if count == 2:
                return utc_from_jd(e).astimezone(CN_TZ).date()

def pillar(i60):
    return {"stem": STEMS[i60 % 10], "branch": BRANCHES[i60 % 12], "element": STEM_EL[i60 % 10], "animal": ANIMALS[i60 % 12],
            "yin_yang": "Yang" if i60 % 2 == 0 else "Yin"}

def zodiac_year(dt: datetime):
    d = dt.date()
    lny = lunar_new_year(d.year)
    y = d.year if d >= lny else d.year - 1
    i = (y - 4) % 60
    return {"year": y, "lunar_new_year": lunar_new_year(y).isoformat(), **pillar(i)}

def bazi(dt_local: datetime):
    dt_utc = dt_local.astimezone(timezone.utc); jd = jd_from_utc(dt_utc)
    sl = _sun_trop(jd)
    # Year changes at Lichun (sun 315°)
    y = dt_local.year
    if dt_local.month <= 2 and 270 <= sl < 315:
        y -= 1
    yi = (y - 4) % 60
    # month: index by solar term from 315 (Yin month)
    mbranch = (int(((sl - 315) % 360) // 30) + 2) % 12
    mstem = ((yi % 10) % 5 * 2 + 2 + (mbranch - 2) % 12) % 10
    mi = next(k for k in range(60) if k % 10 == mstem and k % 12 == mbranch)
    jdn = int(jd_from_utc(datetime(dt_local.year, dt_local.month, dt_local.day, 12, tzinfo=timezone.utc)) + 0.5)
    if dt_local.hour >= 23: jdn += 1
    di = (jdn + 49) % 60
    hb = ((dt_local.hour + 1) // 2) % 12
    hstem = ((di % 10) % 5 * 2 + hb) % 10
    hi = next(k for k in range(60) if k % 10 == hstem and k % 12 == hb)
    pills = {"year": pillar(yi), "month": pillar(mi), "day": pillar(di), "hour": pillar(hi)}
    counts = {}
    for p in pills.values(): counts[p["element"]] = counts.get(p["element"], 0) + 1
    return {"pillars": pills, "day_master": pills["day"]["stem"] + " " + pills["day"]["element"], "element_counts": counts}

def compatibility(a: int, b: int):
    if any(a in t and b in t for t in TRINES): s, txt = 90, "Excellent – same trine"
    elif CLASH[a] == b: s, txt = 30, "Challenging – opposing (clash) signs"
    elif a == b: s, txt = 70, "Good – same sign"
    else: s, txt = 60, "Neutral"
    return {"animal1": ANIMALS[a], "animal2": ANIMALS[b], "score": s, "summary": txt}

def kua(year: int, gender: str):
    s = sum(int(c) for c in str(year)[-2:])
    while s > 9: s = sum(int(c) for c in str(s))
    if gender == "male":
        k = (10 - s) % 9 if year < 2000 else (9 - s) % 9
        k = k or 9
        if k == 5: k = 2
    else:
        k = (s + 5) % 9 if year < 2000 else (s + 6) % 9
        k = k or 9
        if k == 5: k = 8
    east = k in (1, 3, 4, 9)
    dirs = {1: ["SE", "E", "S", "N"], 2: ["NE", "W", "NW", "SW"], 3: ["S", "N", "SE", "E"], 4: ["N", "S", "E", "SE"],
            6: ["W", "NE", "SW", "NW"], 7: ["NW", "SW", "NE", "W"], 8: ["SW", "NW", "W", "NE"], 9: ["E", "SE", "N", "S"]}
    return {"kua_number": k, "group": "East" if east else "West", "favourable_directions": dict(zip(["success", "health", "relationships", "growth"], dirs[k]))}

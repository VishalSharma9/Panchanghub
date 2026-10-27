"""Rule-based horoscopes from real transits: daily/weekly/monthly/yearly by Moon sign (Vedic) or Sun sign (Western).
Text is generated from transit house positions — deterministic and explainable."""
from __future__ import annotations
from datetime import date as Date, datetime, timedelta, timezone
from .ephem import swe, calc, jd_from_utc, SIGNS, RASHIS, NAKSHATRAS

AREA = {1: "self, health and confidence", 2: "money, family and speech", 3: "courage, siblings and short trips",
        4: "home, mother and inner peace", 5: "romance, creativity and children", 6: "work routine, health and competition",
        7: "partnerships and marriage", 8: "sudden changes, research and shared finances", 9: "luck, travel and higher learning",
        10: "career and public image", 11: "gains, friends and wishes", 12: "expenses, rest and spirituality"}
TONE = {"Sun": "authority and vitality", "Moon": "mood and daily affairs", "Mars": "energy and drive", "Mercury": "communication and deals",
        "Jupiter": "growth and blessings", "Venus": "love and comfort", "Saturn": "discipline and delays", "Rahu": "ambition and restlessness",
        "Ketu": "detachment and insight"}
GOOD = {"Sun": [3, 6, 10, 11], "Moon": [1, 3, 6, 7, 10, 11], "Mars": [3, 6, 11], "Mercury": [2, 4, 6, 8, 10, 11],
        "Jupiter": [2, 5, 7, 9, 11], "Venus": [1, 2, 3, 4, 5, 8, 9, 11, 12], "Saturn": [3, 6, 11], "Rahu": [3, 6, 11], "Ketu": [3, 6, 11]}
BODIES = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
          "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
LUCKY_COLOR = ["Red", "White", "Green", "Silver", "Gold", "Green", "Pink", "Maroon", "Yellow", "Blue", "Violet", "Sea green"]

def _sign_idx(s):
    s = s.lower()
    for i, (a, b) in enumerate(zip(SIGNS, RASHIS)):
        if s in (a.lower(), b.lower()): return i
    raise ValueError(f"unknown sign {s}")

def _transits(jd, sidereal):
    out = {}
    for n, b in BODIES.items():
        out[n] = int(calc(jd, b, sidereal)[0] // 30)
    out["Ketu"] = (out["Rahu"] + 6) % 12
    return out

def horoscope(sign: str, period: str = "daily", on: Date | None = None, system: str = "vedic"):
    on = on or Date.today(); si = _sign_idx(sign); sid = system == "vedic"
    span = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}[period]
    mid = on + timedelta(days=span // 2)
    jd = jd_from_utc(datetime(mid.year, mid.month, mid.day, 12, tzinfo=timezone.utc))
    tr = _transits(jd, sid)
    focus = ["Moon", "Sun", "Venus", "Mercury"] if period == "daily" else ["Sun", "Mars", "Venus", "Mercury"] if period in ("weekly", "monthly") else ["Jupiter", "Saturn", "Rahu", "Ketu"]
    lines = []; score = 0
    for p in focus:
        h = (tr[p] - si) % 12 + 1; good = h in GOOD[p]; score += 1 if good else -1
        lines.append(f"{p} transits your {h}{'th' if h > 3 else ['st','nd','rd'][h-1]} house, highlighting {AREA[h]}; "
                     f"{'favourable' if good else 'testing'} {TONE[p]}.")
    rating = max(1, min(5, 3 + score // 2 + (1 if score > 2 else 0)))
    seed = (si * 31 + on.toordinal()) % 12
    return {"sign": SIGNS[si], "rashi": RASHIS[si], "system": system, "period": period, "from": on.isoformat(),
            "to": (on + timedelta(days=span - 1)).isoformat(), "rating": rating, "prediction": " ".join(lines),
            "areas": {"career": rating if tr["Sun"] != (si + 7) % 12 else max(1, rating - 1), "love": 4 if (tr["Venus"] - si) % 12 + 1 in GOOD["Venus"] else 2,
                      "health": 4 if (tr["Mars"] - si) % 12 + 1 in GOOD["Mars"] else 2, "finance": 4 if (tr["Jupiter"] - si) % 12 + 1 in GOOD["Jupiter"] else 3},
            "lucky_color": LUCKY_COLOR[seed], "lucky_number": seed % 9 + 1,
            "transits": {p: SIGNS[s] for p, s in tr.items()}}

def nakshatra_prediction(nak_index: int, on: Date):
    jd = jd_from_utc(datetime(on.year, on.month, on.day, 6, tzinfo=timezone.utc))
    cur = int(calc(jd, swe.MOON, True)[0] // (360 / 27))
    tara = ((cur - nak_index) % 27) % 9 + 1
    names = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyari", "Sadhaka", "Vadha", "Mitra", "Parama Mitra"]
    good = tara in (2, 4, 6, 8, 9)
    return {"birth_nakshatra": NAKSHATRAS[nak_index], "date": on.isoformat(), "moon_nakshatra_today": NAKSHATRAS[cur],
            "tara": names[tara - 1], "favourable": good,
            "prediction": ("A supportive day for new initiatives and meetings." if good else "Proceed carefully; avoid major commitments today.")}

def life_report(kundli: dict):
    P = {p["name"]: p for p in kundli["planets"]}
    asc = kundli["lagna"]["sign"]
    lord_house = lambda h: P[[p for p in P if False] and "Sun" or "Sun"]
    rep = {
        "personality": f"With {asc} rising and the Moon in {kundli['moon']['rashi']} ({kundli['moon']['nakshatra']}), you combine {AREA[1]} themes with emotional depth.",
        "career": f"10th-house influences: {', '.join(p for p in P if P[p]['house'] == 10) or 'no planets'}; Sun in house {P['Sun']['house']} shapes ambition.",
        "love": f"Venus in {P['Venus']['sign']} (house {P['Venus']['house']}) and 7th-house occupants: {', '.join(p for p in P if P[p]['house'] == 7) or 'none'}.",
        "health": f"Lagna lord dignity and 6th-house occupants: {', '.join(p for p in P if P[p]['house'] == 6) or 'none'}. Mars in house {P['Mars']['house']}.",
        "finance": f"2nd/11th houses hold {', '.join(p for p in P if P[p]['house'] in (2, 11)) or 'no planets'}; Jupiter in {P['Jupiter']['sign']}.",
    }
    return rep

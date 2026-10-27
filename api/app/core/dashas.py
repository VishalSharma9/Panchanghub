"""Additional dasha systems: Jaimini Chara dasha (K.N.), Kalachakra dasha (BPHS / B.V. pada tables),
conditional nakshatra dashas (Shodashottari, Dwadashottari, Panchottari, Shatabdika, Chaturashiti-sama,
Dwisaptati-sama, Shashtihayani, Shattrimsha-sama) and Ghata Chakra."""
from __future__ import annotations
from .ephem import SIGNS, SIGN_LORDS, NAKSHATRAS, local_from_jd, norm
from .kundli import YEAR_DAYS, EXALT

def _d(jd, tz): return local_from_jd(jd, tz).date().isoformat()

# ---------------- Chara dasha ----------------
DIRECT = {0, 1, 2, 6, 7, 8}  # odd-footed groups (savya) counted forward

def _sign_lord(s, sign_of, pos):
    if s == 7: cands = ["Mars", "Ketu"]
    elif s == 10: cands = ["Saturn", "Rahu"]
    else: return SIGN_LORDS[s]
    a, b = cands
    na = sum(1 for p, v in sign_of.items() if v == sign_of[a] and p != a)
    nb = sum(1 for p, v in sign_of.items() if v == sign_of[b] and p != b)
    if sign_of[a] == s and sign_of[b] != s: return b
    if sign_of[b] == s and sign_of[a] != s: return a
    if na != nb: return a if na > nb else b
    return a if pos[a]["longitude"] % 30 >= pos[b]["longitude"] % 30 else b

def chara_dasha(pos: dict, asc: float, birth_jd: float, tz, cycles: int = 2):
    sign_of = {p: int(v["longitude"] // 30) for p, v in pos.items() if p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")}
    lag = int(asc // 30)
    forward = ((lag + 8) % 12) in DIRECT
    seq = [(lag + (i if forward else -i)) % 12 for i in range(12)]
    years = {}
    for s in range(12):
        L = _sign_lord(s, sign_of, pos); ls = sign_of[L]
        n = ((ls - s) % 12) if s in DIRECT else ((s - ls) % 12)
        y = 12 if n == 0 else n
        if L in EXALT and EXALT[L] == ls: y += 1
        if L in EXALT and (EXALT[L] + 6) % 12 == ls: y -= 1
        years[s] = max(1, min(12, y))
    out = []; t = birth_jd
    for c in range(cycles):
        for s in seq:
            y = years[s] if c == 0 else 12 - years[s]
            if y <= 0: continue
            e = t + y * YEAR_DAYS
            subs = []; st = t; sub_fw = s in DIRECT
            for k in range(1, 13):
                ss = (s + (k if sub_fw else -k)) % 12; se = st + y * YEAR_DAYS / 12
                subs.append({"sign": SIGNS[ss], "start": _d(st, tz), "end": _d(se, tz)}); st = se
            out.append({"sign": SIGNS[s], "years": y, "start": _d(t, tz), "end": _d(e, tz), "antardasha": subs})
            t = e
    return {"method": "Jaimini Chara dasha (K.N.): sequence from Lagna, direction by 9th house footedness",
            "direction": "forward" if forward else "reverse", "periods": out}

# ---------------- Kalachakra ----------------
KC_YEARS = [7, 16, 9, 21, 5, 9, 16, 7, 10, 4, 4, 10]
# B.V. savya pada tables (Capricorn written as 'Cp')
SAVYA = [[0, 1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 7, 6, 5, 3, 4, 2], [1, 0, 11, 10, 9, 8, 0, 1, 2], [3, 4, 5, 6, 7, 8, 9, 10, 11]]
APASAVYA = [[7, 6, 5, 3, 4, 2, 1, 0, 11], [10, 9, 8, 0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11, 7, 6, 5], [3, 4, 2, 1, 0, 11, 10, 9, 8]]
SAVYA_NAK = {0, 1, 2, 6, 7, 8, 12, 13, 14, 18, 19, 20, 24, 25, 26}

def kalachakra(moon_lon: float, birth_jd: float, tz):
    pada_span = 360 / 108
    gp = int(moon_lon // pada_span); ni = gp // 4; pada = gp % 4
    frac = (moon_lon - gp * pada_span) / pada_span
    savya = ni in SAVYA_NAK
    seq = (SAVYA if savya else APASAVYA)[pada]
    total = sum(KC_YEARS[s] for s in seq)
    elapsed = frac * total
    t = birth_jd - elapsed * YEAR_DAYS
    out = []
    for s in seq:
        e = t + KC_YEARS[s] * YEAR_DAYS
        out.append({"sign": SIGNS[s], "years": KC_YEARS[s], "start": _d(t, tz), "end": _d(e, tz)}); t = e
    return {"method": "Kalachakra dasha (BPHS / B.V. pada tables)", "nakshatra": NAKSHATRAS[ni], "pada": pada + 1,
            "group": "Savya" if savya else "Apasavya", "deha": SIGNS[seq[0]], "jeeva": SIGNS[seq[-1]],
            "paramayu_years": total, "elapsed_at_birth_years": round(elapsed, 4), "periods": out}

# ---------------- conditional nakshatra dashas ----------------
NAK_DASHAS = {
    "shodashottari": (["Sun", "Mars", "Jupiter", "Saturn", "Ketu", "Moon", "Mercury", "Venus"], [11, 12, 13, 14, 15, 16, 17, 18], 7, 1,
                      "Applicable when Lagna is in Moon's hora in Krishna paksha (day) or Sun's hora in Shukla paksha (night)"),
    "dwadashottari": (["Sun", "Jupiter", "Ketu", "Mercury", "Rahu", "Mars", "Saturn", "Moon"], [7, 9, 11, 13, 15, 17, 19, 21], 26, -1,
                      "Applicable when Lagna falls in Venus's navamsa"),
    "panchottari": (["Sun", "Mercury", "Saturn", "Mars", "Venus", "Moon", "Jupiter"], [12, 13, 14, 15, 16, 17, 18], 16, 1,
                    "Applicable when Lagna is Cancer and in Cancer dwadashamsa"),
    "shatabdika": (["Sun", "Moon", "Venus", "Mercury", "Jupiter", "Mars", "Saturn"], [5, 5, 10, 10, 20, 20, 30], 26, 1,
                   "Applicable when Lagna is in vargottama"),
    "chaturashiti_sama": (["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"], [12] * 7, 14, 1,
                          "Applicable when the 10th lord is in the 10th house"),
    "dwisaptati_sama": (["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"], [9] * 8, 18, 1,
                        "Applicable when the Lagna lord is in the 7th or the 7th lord in Lagna"),
    "shashtihayani": (["Jupiter", "Sun", "Mars", "Moon", "Mercury", "Venus", "Saturn", "Rahu"], [10, 10, 10, 6, 6, 6, 6, 6], 0, 1,
                      "Applicable when the Sun is in Lagna"),
    "shattrimsha_sama": (["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"], [1, 2, 3, 4, 5, 6, 7, 8], 21, 1,
                         "Applicable for day birth with Lagna in Sun's hora or night birth in Moon's hora"),
}

def nakshatra_dasha(kind: str, moon_lon: float, birth_jd: float, tz, cycles: int = 1):
    lords, yrs, start_nak, direction, cond = NAK_DASHAS[kind]
    span = 360 / 27; ni = int(moon_lon // span); frac = (moon_lon - ni * span) / span
    n = len(lords)
    k = ((ni - start_nak) if direction == 1 else (start_nak - ni)) % 27
    i0 = k % n
    t = birth_jd - frac * yrs[i0] * YEAR_DAYS
    out = []
    for c in range(n * cycles):
        i = (i0 + c) % n; e = t + yrs[i] * YEAR_DAYS
        out.append({"lord": lords[i], "years": yrs[i], "start": _d(t, tz), "end": _d(e, tz)}); t = e
    return {"system": kind, "cycle_years": sum(yrs), "applicability": cond,
            "balance_at_birth": {"lord": lords[i0], "years_remaining": round((1 - frac) * yrs[i0], 4)}, "periods": out}

def applicable(kind: str, k: dict) -> bool:
    """Evaluate classical applicability conditions from a compute_kundli() result."""
    pl = {p["name"]: p for p in k["planets"]}; lag = k["lagna"]; ls = SIGNS.index(lag["sign"])
    if kind == "dwadashottari": return lag["vargas"]["D9"] in ("Taurus", "Libra")
    if kind == "panchottari": return lag["sign"] == "Cancer" and lag["vargas"]["D12"] == "Cancer"
    if kind == "shatabdika": return lag["vargas"]["D9"] == lag["sign"]
    if kind == "chaturashiti_sama": return pl[SIGN_LORDS[(ls + 9) % 12]]["house"] == 10
    if kind == "dwisaptati_sama": return pl[SIGN_LORDS[ls]]["house"] == 7 or pl[SIGN_LORDS[(ls + 6) % 12]]["house"] == 1
    if kind == "shashtihayani": return pl["Sun"]["house"] == 1
    return False

def all_dashas(k: dict, pos: dict, asc: float, birth_jd: float, tz):
    moon = pos["Moon"]["longitude"]
    other = {}
    for kind in NAK_DASHAS:
        d = nakshatra_dasha(kind, moon, birth_jd, tz)
        d["applicable"] = applicable(kind, k)
        other[kind] = d
    return {"chara": chara_dasha(pos, asc, birth_jd, tz), "kalachakra": kalachakra(moon, birth_jd, tz), "conditional": other}

# ---------------- Ghata chakra ----------------
_GHATA = [  # by janma rashi: masa, tithi group, vara, nakshatra, yoga, karana, prahar, ghata moon sign
    ("Kartika", "Nanda (1, 6, 11)", "Sunday", "Magha", "Vishkumbha", "Bava", 1, "Aries"),
    ("Margashirsha", "Purna (5, 10, 15)", "Saturday", "Hasta", "Shula", "Shakuni", 4, "Virgo"),
    ("Ashadha", "Bhadra (2, 7, 12)", "Monday", "Swati", "Parigha", "Kaulava", 3, "Aquarius"),
    ("Pausha", "Bhadra (2, 7, 12)", "Wednesday", "Anuradha", "Vyaghata", "Naga", 1, "Leo"),
    ("Jyeshtha", "Jaya (3, 8, 13)", "Saturday", "Mula", "Dhriti", "Bava", 1, "Capricorn"),
    ("Bhadrapada", "Purna (5, 10, 15)", "Saturday", "Shravana", "Shula", "Kaulava", 1, "Gemini"),
    ("Magha", "Rikta (4, 9, 14)", "Thursday", "Shatabhisha", "Shukla", "Taitila", 4, "Sagittarius"),
    ("Ashwin", "Nanda (1, 6, 11)", "Friday", "Revati", "Vyatipata", "Garaja", 1, "Taurus"),
    ("Shravana", "Jaya (3, 8, 13)", "Friday", "Ashwini", "Vajra", "Taitila", 1, "Pisces"),
    ("Vaishakha", "Rikta (4, 9, 14)", "Tuesday", "Rohini", "Vaidhriti", "Shakuni", 4, "Leo"),
    ("Chaitra", "Jaya (3, 8, 13)", "Thursday", "Ardra", "Ganda", "Kimstughna", 3, "Sagittarius"),
    ("Phalguna", "Purna (5, 10, 15)", "Friday", "Ashlesha", "Vajra", "Chatushpada", 4, "Aquarius"),
]
def ghata_chakra(moon_sign: int):
    m, t, v, n, y, k, pr, ms = _GHATA[moon_sign]
    return {"janma_rashi": SIGNS[moon_sign], "masa": m, "tithi": t, "vara": v, "nakshatra": n, "yoga": y, "karana": k,
            "prahar": pr, "moon_sign": ms,
            "note": "Ghata (inauspicious) factors for the native per the traditional Ghata Chakra table; avoid starting important work when they coincide. Regional tables differ slightly."}

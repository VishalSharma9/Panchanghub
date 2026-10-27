"""Vedic Kundli: lagna, planets, 16 vargas, dashas, ashtakavarga, partial shadbala, doshas and yogas."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from .ephem import (swe, all_positions, houses, sign_info, nakshatra_of, norm, angdiff, dms, jd_from_utc, utc_from_jd,
                    SIGNS, RASHIS, NAKSHATRAS, NAK_LORDS, SIGN_LORDS, VEDIC_PLANETS, calc, ayanamsa, next_boundary,
                    local_from_jd)

YEAR_DAYS = 365.2425  # mean Gregorian year, used for Vimshottari
VIM_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
YOGINIS = [("Mangala", "Moon", 1), ("Pingala", "Sun", 2), ("Dhanya", "Jupiter", 3), ("Bhramari", "Mars", 4),
           ("Bhadrika", "Mercury", 5), ("Ulka", "Saturn", 6), ("Siddha", "Venus", 7), ("Sankata", "Rahu", 8)]
EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 1, "Ketu": 7}
EXALT_DEG = {"Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165, "Jupiter": 95, "Venus": 357, "Saturn": 200}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
MOOLA = {"Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5, "Jupiter": 8, "Venus": 6, "Saturn": 10}
FRIENDS = {"Sun": (["Moon", "Mars", "Jupiter"], ["Mercury"], ["Venus", "Saturn"]),
           "Moon": (["Sun", "Mercury"], ["Mars", "Jupiter", "Venus", "Saturn"], []),
           "Mars": (["Sun", "Moon", "Jupiter"], ["Venus", "Saturn"], ["Mercury"]),
           "Mercury": (["Sun", "Venus"], ["Mars", "Jupiter", "Saturn"], ["Moon"]),
           "Jupiter": (["Sun", "Moon", "Mars"], ["Saturn"], ["Mercury", "Venus"]),
           "Venus": (["Mercury", "Saturn"], ["Mars", "Jupiter"], ["Sun", "Moon"]),
           "Saturn": (["Mercury", "Venus"], ["Jupiter"], ["Sun", "Moon", "Mars"])}
COMBUST_ORB = {"Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11, "Venus": 10, "Saturn": 15}

def relation(a: str, b: str) -> str:
    if a not in FRIENDS or b not in FRIENDS: return "neutral"
    f, n, e = FRIENDS[a]
    return "friend" if b in f else "enemy" if b in e else "neutral"

def dignity(planet: str, lon: float) -> str:
    s = int(lon // 30)
    if planet in EXALT and EXALT[planet] == s: return "exalted"
    if planet in EXALT and (EXALT[planet] + 6) % 12 == s: return "debilitated"
    if planet in MOOLA and MOOLA[planet] == s: return "moolatrikona"
    if planet in OWN and s in OWN[planet]: return "own"
    if planet in FRIENDS:
        r = relation(planet, SIGN_LORDS[s])
        return {"friend": "friendly", "enemy": "enemy", "neutral": "neutral"}[r]
    return "-"

# ---------------- Vargas ----------------
def varga_sign(lon: float, n: int) -> int:
    s, d = int(lon // 30) % 12, lon % 30
    odd = s % 2 == 0  # Aries is odd sign
    mod = s % 3  # 0 movable, 1 fixed, 2 dual
    if n == 1: return s
    p = int(d // (30 / n)) if n not in (30,) else 0
    if n == 2: return (4 if d < 15 else 3) if odd else (3 if d < 15 else 4)
    if n == 3: return (s + 4 * p) % 12
    if n == 4: return (s + 3 * p) % 12
    if n == 7: return (s + p) % 12 if odd else (s + 6 + p) % 12
    if n == 9: return int(lon // (10 / 3)) % 12
    if n == 10: return (s + p) % 12 if odd else (s + 8 + p) % 12
    if n == 12: return (s + p) % 12
    if n == 16: return ([0, 4, 8][mod] + p) % 12
    if n == 20: return ([0, 8, 4][mod] + p) % 12
    if n == 24: return ((4 if odd else 3) + p) % 12
    if n == 27: return ([0, 3, 6, 9][s % 4] + p) % 12
    if n == 30:
        if odd:
            return 0 if d < 5 else 10 if d < 10 else 8 if d < 18 else 2 if d < 25 else 6
        return 1 if d < 5 else 5 if d < 12 else 11 if d < 20 else 9 if d < 25 else 7
    if n == 40: return ((0 if odd else 6) + p) % 12
    if n == 45: return ([0, 4, 8][mod] + p) % 12
    if n == 60: return (s + p) % 12
    raise ValueError(n)

VARGAS = {1: "Rashi", 2: "Hora", 3: "Drekkana", 4: "Chaturthamsa", 7: "Saptamsa", 9: "Navamsa", 10: "Dasamsa",
          12: "Dwadasamsa", 16: "Shodasamsa", 20: "Vimsamsa", 24: "Chaturvimsamsa", 27: "Bhamsa", 30: "Trimsamsa",
          40: "Khavedamsa", 45: "Akshavedamsa", 60: "Shashtiamsa"}

# ---------------- Dashas ----------------
def _add_years(jd, years): return jd + years * YEAR_DAYS

def vimshottari(moon_lon: float, birth_jd: float, tz, levels: int = 3):
    span = 360 / 27
    ni = int(moon_lon // span)
    frac = (moon_lon - ni * span) / span
    lord0 = NAK_LORDS[ni % 9]
    i0 = VIM_ORDER.index(lord0)
    start = birth_jd - frac * VIM_YEARS[lord0] * YEAR_DAYS
    def sub(lord, s, total_years, depth):
        res = []; i = VIM_ORDER.index(lord); t = s
        for k in range(9):
            L = VIM_ORDER[(i + k) % 9]
            y = total_years * VIM_YEARS[L] / 120
            e = _add_years(t, y)
            item = {"lord": L, "start": local_from_jd(t, tz).date().isoformat(), "end": local_from_jd(e, tz).date().isoformat()}
            if depth < levels:
                item["sub"] = sub(L, t, y, depth + 1)
            res.append(item); t = e
        return res
    md = []; t = start
    for k in range(9):
        L = VIM_ORDER[(i0 + k) % 9]; y = VIM_YEARS[L]; e = _add_years(t, y)
        item = {"lord": L, "start": local_from_jd(t, tz).date().isoformat(), "end": local_from_jd(e, tz).date().isoformat(), "years": y}
        if levels >= 2: item["antardasha"] = sub(L, t, y, 2) if levels > 1 else []
        md.append(item); t = e
    # rename nested keys for clarity
    for m in md:
        for a in m.get("antardasha", []):
            a["pratyantardasha"] = a.pop("sub", [])
    return {"balance_at_birth": {"lord": lord0, "years_remaining": round((1 - frac) * VIM_YEARS[lord0], 4)},
            "mahadasha": md}

def yogini(moon_lon: float, birth_jd: float, tz, cycles: int = 3):
    span = 360 / 27
    ni = int(moon_lon // span); frac = (moon_lon - ni * span) / span
    k0 = (ni + 1 + 3) % 8; k0 = 8 if k0 == 0 else k0
    idx = k0 - 1
    yrs0 = YOGINIS[idx][2]
    t = birth_jd - frac * yrs0 * YEAR_DAYS
    out = []
    for c in range(8 * cycles):
        name, lord, y = YOGINIS[(idx + c) % 8]
        e = _add_years(t, y)
        out.append({"yogini": name, "lord": lord, "years": y, "start": local_from_jd(t, tz).date().isoformat(), "end": local_from_jd(e, tz).date().isoformat()})
        t = e
    return {"balance_at_birth": {"yogini": YOGINIS[idx][0], "years_remaining": round((1 - frac) * yrs0, 4)}, "periods": out}

# ---------------- Ashtakavarga ----------------
_AV = {
 "Sun": {"Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11], "Mercury": [3,5,6,9,10,11,12],
         "Jupiter": [5,6,9,11], "Venus": [6,7,12], "Saturn": [1,2,4,7,8,9,10,11], "Lagna": [3,4,6,10,11,12]},
 "Moon": {"Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11], "Mercury": [1,3,4,5,7,8,10,11],
          "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11], "Saturn": [3,5,6,11], "Lagna": [3,6,10,11]},
 "Mars": {"Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,10,11], "Mercury": [3,5,6,11], "Jupiter": [6,10,11,12],
          "Venus": [6,8,11,12], "Saturn": [1,4,7,8,9,10,11], "Lagna": [1,3,6,10,11]},
 "Mercury": {"Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11], "Mars": [1,2,4,7,8,9,10,11], "Mercury": [1,3,5,6,9,10,11,12],
             "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11], "Saturn": [1,2,4,7,8,9,10,11], "Lagna": [1,2,4,6,8,10,11]},
 "Jupiter": {"Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,7,9,11], "Mars": [1,2,4,7,8,10,11], "Mercury": [1,2,4,5,6,9,10,11],
             "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11], "Saturn": [3,5,6,12], "Lagna": [1,2,4,5,6,7,9,10,11]},
 "Venus": {"Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12], "Mars": [3,5,6,9,11,12], "Mercury": [3,5,6,9,11],
           "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11], "Saturn": [3,4,5,8,9,10,11], "Lagna": [1,2,3,4,5,8,9,11]},
 "Saturn": {"Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11], "Mars": [3,5,6,10,11,12], "Mercury": [6,8,9,10,11,12],
            "Jupiter": [5,6,11,12], "Venus": [6,11,12], "Saturn": [3,5,6,11], "Lagna": [1,3,4,6,10,11]},
}

def ashtakavarga(sign_of: dict):
    bav = {}
    for p, contrib in _AV.items():
        pts = [0] * 12
        for c, hs in contrib.items():
            for h in hs:
                pts[(sign_of[c] + h - 1) % 12] += 1
        bav[p] = pts
    sav = [sum(bav[p][i] for p in bav) for i in range(12)]
    return {"signs": SIGNS, "bhinnashtakavarga": bav, "sarvashtakavarga": sav, "total": sum(sav)}

# ---------------- Partial Shadbala ----------------
NAISARGIKA = {"Sun": 60, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29, "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
DIG_HOUSE = {"Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1, "Moon": 4, "Venus": 4, "Saturn": 7}

def partial_shadbala(pos, asc):
    out = {}
    cusp_of = lambda h: norm(asc + (h - 1) * 30)
    for p in NAISARGIKA:
        lon = pos[p]["longitude"]
        uccha = (180 - abs(angdiff(lon, EXALT_DEG[p]))) / 3  # 0..60 virupas
        dig = (180 - abs(angdiff(lon, cusp_of(DIG_HOUSE[p])))) / 3
        cheshta = 0.0
        if p not in ("Sun", "Moon"):
            cheshta = 60.0 if pos[p]["speed"] < 0 else 30.0 * min(1, abs(pos[p]["speed"]) / 1.0) / 1
        total = uccha + dig + NAISARGIKA[p] + cheshta
        out[p] = {"uccha_bala": round(uccha, 2), "dig_bala": round(dig, 2), "naisargika_bala": NAISARGIKA[p],
                  "cheshta_bala_approx": round(cheshta, 2), "total_virupas": round(total, 2), "total_rupas": round(total / 60, 2)}
    return {"note": "Partial Shadbala (Uccha, Dig, Naisargika, approximate Cheshta). Kala & full Sthana bala not included.",
            "planets": out}

# ---------------- Doshas ----------------
def manglik(houses_of, sign_of):
    from_lagna = houses_of["Mars"]
    from_moon = (sign_of["Mars"] - sign_of["Moon"]) % 12 + 1
    from_venus = (sign_of["Mars"] - sign_of["Venus"]) % 12 + 1
    bad = {1, 2, 4, 7, 8, 12}
    res = {"from_lagna": from_lagna in bad, "from_moon": from_moon in bad, "from_venus": from_venus in bad,
           "mars_house_from_lagna": from_lagna, "mars_house_from_moon": from_moon}
    cancellations = []
    ms = sign_of["Mars"]
    if ms in (0, 7, 9): cancellations.append("Mars in own sign or exalted")
    if dignity("Mars", ms * 30 + 1) == "exalted": pass
    if relation("Mars", SIGN_LORDS[ms]) == "friend" and False: pass
    res["is_manglik"] = res["from_lagna"] or res["from_moon"]
    res["severity"] = "high" if res["from_lagna"] and res["from_moon"] else ("low" if res["is_manglik"] else "none")
    res["cancellations"] = cancellations
    return res

def kaal_sarp(pos):
    r = pos["Rahu"]["longitude"]
    sides = []
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        sides.append(norm(pos[p]["longitude"] - r) < 180)
    full = all(sides) or not any(sides)
    names = ["Anant", "Kulik", "Vasuki", "Shankhapal", "Padma", "Mahapadma", "Takshak", "Karkotak", "Shankhachur", "Ghatak", "Vishdhar", "Sheshnag"]
    return {"present": full, "type": ("Kaal Sarp (Rahu→Ketu)" if all(sides) else "Kaal Amrit (Ketu→Rahu)") if full else None, "_names": names}

def sade_sati(moon_sign: int, jd_from: float, years: int = 100, tz=timezone.utc):
    """Saturn transits in 12th, 1st, 2nd from natal Moon sign (sidereal)."""
    sat = lambda j: calc(j, swe.SATURN, True)[0]
    periods = []; t = jd_from; cur = int(sat(t) // 30); start = t; step = 5.0
    end_jd = jd_from + years * 365.25
    segs = []
    while t < end_jd:
        t2 = t + step; s2 = int(sat(t2) // 30)
        if s2 != cur:
            a, b = t, t2
            for _ in range(40):
                m = (a + b) / 2
                if int(sat(m) // 30) == cur: a = m
                else: b = m
            segs.append((cur, start, b)); cur = s2; start = b
        t = t2
    segs.append((cur, start, end_jd))
    phase = {(moon_sign - 1) % 12: "Rising (12th)", moon_sign: "Peak (over Moon)", (moon_sign + 1) % 12: "Setting (2nd)",
             (moon_sign + 3) % 12: "Small Panoti / Dhaiya (4th)", (moon_sign + 7) % 12: "Small Panoti / Dhaiya (8th)"}
    for s, a, b in segs:
        if s in phase:
            periods.append({"phase": phase[s], "saturn_sign": RASHIS[s], "start": local_from_jd(a, tz).date().isoformat(), "end": local_from_jd(b, tz).date().isoformat()})
    return periods

# ---------------- Yogas ----------------
def detect_yogas(sign_of, houses_of, asc_sign):
    y = []
    kendra = {1, 4, 7, 10}
    rel = lambda a, b: (sign_of[b] - sign_of[a]) % 12 + 1
    if rel("Moon", "Jupiter") in kendra: y.append(("Gajakesari Yoga", "Jupiter in a kendra from the Moon"))
    if sign_of["Sun"] == sign_of["Mercury"]: y.append(("Budhaditya Yoga", "Sun and Mercury conjunct"))
    if sign_of["Moon"] == sign_of["Mars"]: y.append(("Chandra-Mangala Yoga", "Moon and Mars conjunct"))
    mp = {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa", "Venus": "Malavya", "Saturn": "Shasha"}
    for p, n in mp.items():
        s = sign_of[p]
        if houses_of[p] in kendra and (s in OWN[p] or EXALT[p] == s):
            y.append((f"{n} Yoga (Pancha Mahapurusha)", f"{p} in own/exaltation sign in a kendra"))
    others = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    second = [p for p in others if rel("Moon", p) == 2]; twelfth = [p for p in others if rel("Moon", p) == 12]
    if second and twelfth: y.append(("Durudhara Yoga", "Planets on both sides of the Moon"))
    elif second: y.append(("Sunapha Yoga", "Planet(s) in 2nd from the Moon"))
    elif twelfth: y.append(("Anapha Yoga", "Planet(s) in 12th from the Moon"))
    else:
        if not any(rel("Moon", p) in kendra and p != "Moon" for p in others + ["Sun"]):
            y.append(("Kemadruma Yoga", "No planets in 2nd/12th or kendra from the Moon"))
    if all(rel("Moon", p) in (6, 7, 8) for p in ["Mercury", "Jupiter", "Venus"]): y.append(("Adhi Yoga", "Benefics in 6/7/8 from Moon"))
    # Raja yoga: lord of kendra conjunct lord of trikona
    lord = lambda h: SIGN_LORDS[(asc_sign + h - 1) % 12]
    for k in (1, 4, 7, 10):
        for t in (5, 9):
            a, b = lord(k), lord(t)
            if a != b and sign_of[a] == sign_of[b]:
                y.append(("Raja Yoga", f"Lord of {k} ({a}) conjunct lord of {t} ({b})"))
    # Vipareeta Raja Yoga
    for h in (6, 8, 12):
        L = lord(h)
        if houses_of[L] in (6, 8, 12) and houses_of[L] != h or houses_of[L] == h and False:
            y.append(("Vipareeta Raja Yoga", f"Lord of {h} ({L}) in a dusthana"))
    # Dhana yoga: lords of 2 & 11 conjunct
    if sign_of[lord(2)] == sign_of[lord(11)] and lord(2) != lord(11): y.append(("Dhana Yoga", "Lords of 2nd and 11th conjunct"))
    # Neecha Bhanga (simple)
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        s = sign_of[p]
        if (EXALT[p] + 6) % 12 == s:
            dl = SIGN_LORDS[s]
            if houses_of[dl] in kendra or rel("Moon", dl) in kendra:
                y.append(("Neecha Bhanga Raja Yoga", f"Debilitated {p}; dispositor {dl} in kendra"))
    seen = set(); out = []
    for n, d in y:
        if (n, d) not in seen: seen.add((n, d)); out.append({"name": n, "description": d})
    return out

# ---------------- main ----------------
def compute_kundli(dt_utc: datetime, lat: float, lon: float, tz, true_node: bool = False, dasha_levels: int = 3,
                   house_system: str = "W"):
    jd = jd_from_utc(dt_utc)
    pos = all_positions(jd, sidereal=True, true_node=true_node)
    cusps, asc, mc = houses(jd, lat, lon, house_system, True)
    asc_sign = int(asc // 30)
    sun = pos["Sun"]["longitude"]
    planets = []
    sign_of = {"Lagna": asc_sign}; houses_of = {}
    for p in VEDIC_PLANETS + ["Uranus", "Neptune", "Pluto"]:
        L = pos[p]["longitude"]; s, d = sign_info(L); ni, pada = nakshatra_of(L)
        h = (s - asc_sign) % 12 + 1
        sign_of[p] = s; houses_of[p] = h
        retro = pos[p]["speed"] < 0 if p not in ("Rahu", "Ketu") else True
        comb = None
        if p in COMBUST_ORB:
            orb = COMBUST_ORB[p] - (2 if p == "Mercury" and retro else 0) - (2 if p == "Venus" and retro else 0)
            comb = abs(angdiff(L, sun)) < orb
        planets.append({"name": p, "longitude": round(L, 6), "sign": SIGNS[s], "rashi": RASHIS[s], "degree": round(d, 6),
                        "dms": dms(d), "nakshatra": NAKSHATRAS[ni], "pada": pada, "nakshatra_lord": NAK_LORDS[ni % 9],
                        "sign_lord": SIGN_LORDS[s], "house": h, "retrograde": retro, "combust": comb,
                        "dignity": dignity(p, L), "speed": round(pos[p]["speed"], 6),
                        "vargas": {f"D{n}": SIGNS[varga_sign(L, n)] for n in VARGAS}})
    ani, apada = nakshatra_of(asc)
    lagna = {"longitude": round(asc, 6), "sign": SIGNS[asc_sign], "rashi": RASHIS[asc_sign], "degree": round(asc % 30, 6),
             "dms": dms(asc % 30), "nakshatra": NAKSHATRAS[ani], "pada": apada, "sign_lord": SIGN_LORDS[asc_sign],
             "vargas": {f"D{n}": SIGNS[varga_sign(asc, n)] for n in VARGAS}}
    vargas = {}
    for n, name in VARGAS.items():
        vl = varga_sign(asc, n)
        chart = {"name": name, "ascendant_sign": SIGNS[vl], "planets": {}}
        for p in VEDIC_PLANETS:
            vs = varga_sign(pos[p]["longitude"], n)
            chart["planets"][p] = {"sign": SIGNS[vs], "house": (vs - vl) % 12 + 1}
        vargas[f"D{n}"] = chart
    moon = pos["Moon"]["longitude"]; mni, mpada = nakshatra_of(moon)
    av = ashtakavarga(sign_of)
    ks = kaal_sarp(pos)
    if ks["present"]:
        ks["name"] = ks["_names"][houses_of["Rahu"] - 1] + " Kaal Sarp"
    ks.pop("_names")
    from . import advanced as A
    from .ephem import utc_from_jd
    from datetime import datetime as _dt, timezone as _tz
    for pl in planets:
        pl["avastha"] = A.avastha(pl["longitude"])
    now_jd = jd_from_utc(_dt.now(_tz.utc))
    ed = A.extra_doshas(sign_of, houses_of)
    ed["kemadruma"] = any(y["name"] == "Kemadruma Yoga" for y in detect_yogas(sign_of, houses_of, asc_sign))
    pcusps = houses(jd, lat, lon, "P", True)[0]
    from . import shadbala as SB, dashas as D, yogas_extra as YX
    from .panchang import day_events
    try:
        ld = local_from_jd(jd, tz).date(); ev = day_events(ld, lat, lon, tz)
        sr, ssj = ev["sunrise"], ev["sunset"]
        if jd < sr:
            ev0 = day_events(ld - timedelta(days=1), lat, lon, tz); sr, ssj = ev0["sunrise"], ev0["sunset"]
    except Exception:
        sr = ssj = None
    sb = SB.shadbala(jd, lat, lon, pos, asc, None, sr, ssj)
    return {
        "avakahada": A.avakahada(moon, sun, asc),
        "current_dasha": A.current_vimshottari(moon, jd, now_jd, tz, 5),
        "ashtottari_dasha": A.ashtottari(moon, jd, tz),
        "jaimini": A.jaimini(pos, asc),
        "bhava_chalit": A.bhava_chalit(pos, pcusps),
        "friendship": A.friendship(sign_of),
        "remedies": A.remedies(asc),
        "lal_kitab": A.lal_kitab(pos, asc),
        "other_doshas": ed,
        "datetime_utc": dt_utc.isoformat(), "julian_day": jd, "ayanamsa": round(ayanamsa(jd), 6),
        "house_system": {"W": "Whole Sign", "P": "Placidus", "E": "Equal"}.get(house_system, house_system),
        "lagna": lagna, "planets": planets, "house_cusps": [round(c, 6) for c in cusps], "midheaven": round(mc, 6),
        "moon": {"rashi": RASHIS[int(moon // 30)], "nakshatra": NAKSHATRAS[mni], "pada": mpada, "nakshatra_lord": NAK_LORDS[mni % 9]},
        "vargas": vargas,
        "vimshottari_dasha": vimshottari(moon, jd, tz, dasha_levels),
        "yogini_dasha": yogini(moon, jd, tz),
        "ashtakavarga": av,
        "shadbala": sb,
        "bhavabala": SB.bhavabala(sb, pos, asc),
        "dashas_other": D.all_dashas({"planets": planets, "lagna": lagna}, pos, asc, jd, tz),
        "ghata_chakra": D.ghata_chakra(int(moon // 30)),
        "doshas": {"manglik": manglik(houses_of, sign_of), "kaal_sarp": ks,
                   "sade_sati": sade_sati(int(moon // 30), jd, 100, tz)},
        "yogas": _merge_yogas(detect_yogas(sign_of, houses_of, asc_sign) + YX.extra_yogas(sign_of, houses_of, asc_sign), sign_of, houses_of, asc_sign),
    }


def _merge_yogas(base, sign_of, houses_of, asc_sign):
    from .yogas_classical import classical_yogas
    seen = {y["name"] for y in base}
    return base + [y for y in classical_yogas(sign_of, houses_of, asc_sign) if y["name"] not in seen]

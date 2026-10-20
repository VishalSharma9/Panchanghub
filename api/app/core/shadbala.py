"""Full Shadbala (six-fold strength) and Bhavabala per Brihat Parashara Hora Shastra (BPHS ch. 27-28).

All values in virupas (60 virupas = 1 rupa). Implementation notes:
* Sthana bala = Uccha + Saptavargaja + Ojhayugma (D1 & D9) + Kendradi + Drekkana.
* Dig bala from the planet's distance to its powerless house cusp.
* Kala bala = Nathonnata + Paksha + Tribhaga + Abda/Masa/Vara/Hora lords + Ayana + Yuddha.
* Cheshta bala: Sun = ayana bala, Moon = paksha bala; others from motion state (Vakra 60, Anuvakra 30,
  Vikala 15, Mandatara 15, Manda 30, Sama 7.5, Chara 45, Atichara 30) per BPHS.
* Naisargika bala fixed. Drik bala = (sum of benefic aspects - malefic aspects)/4 using BPHS aspect virupas.
Abda/Masa lords use the ahargana-from-Kali-epoch formulae (B.V. Raman, "Graha and Bhava Balas").
"""
from __future__ import annotations
import math
import swisseph as swe
from .ephem import norm, angdiff, SIGN_LORDS, WEEKDAYS
from .kundli import EXALT_DEG, OWN, MOOLA, FRIENDS, varga_sign

PL = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NAISARGIKA = {"Sun": 60, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29, "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
REQUIRED_RUPAS = {"Sun": 6.5, "Moon": 6, "Mars": 5, "Mercury": 7, "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5}
DIG_ZERO_HOUSE = {"Sun": 4, "Mars": 4, "Jupiter": 7, "Mercury": 7, "Moon": 10, "Venus": 10, "Saturn": 1}  # weak points
MEAN_SPEED = {"Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083, "Venus": 1.2, "Saturn": 0.033}
CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
WEEKDAY_LORD = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
KALI_JD = 588465.5

def _compound(p, q, sign_of):
    """Panchadha maitri: natural + temporary."""
    if p == q: return "own"
    f, n, e = FRIENDS[p]
    nat = 1 if q in f else -1 if q in e else 0
    dist = (sign_of[q] - sign_of[p]) % 12 + 1
    tmp = 1 if dist in (2, 3, 4, 10, 11, 12) else -1
    s = nat + tmp
    return {2: "great_friend", 1: "friend", 0: "neutral", -1: "enemy", -2: "great_enemy"}[s]

SAPTA_PTS = {"moolatrikona": 45, "own": 30, "great_friend": 22.5, "friend": 15, "neutral": 7.5, "enemy": 3.75, "great_enemy": 1.875}

def drishti_value(angle: float, planet: str) -> float:
    """BPHS aspect strength (virupas) of `planet` on a point `angle` degrees ahead."""
    a = norm(angle)
    if a < 30 or a >= 300: v = 0.0
    elif a < 60: v = (a - 30) / 2
    elif a < 90: v = a - 45
    elif a < 120: v = 30 + (120 - a) / 2
    elif a < 150: v = 150 - a
    elif a < 180: v = 2 * (a - 150)
    else: v = (300 - a) / 2
    if planet == "Mars" and (90 <= a < 120 or 210 <= a < 240): v = 60
    if planet == "Jupiter" and (120 <= a < 150 or 240 <= a < 270): v = 60
    if planet == "Saturn" and (60 <= a < 90 or 270 <= a < 300): v = 60
    return v

def _benefic(p, moon_waxing, merc_with_malefic):
    if p in ("Jupiter", "Venus"): return True
    if p == "Moon": return moon_waxing
    if p == "Mercury": return not merc_with_malefic
    return False

def shadbala(jd: float, lat: float, lon: float, pos: dict, asc: float, cusps: list | None = None, sunrise_jd=None, sunset_jd=None):
    sign_of = {p: int(pos[p]["longitude"] // 30) for p in PL}
    sun, moon = pos["Sun"]["longitude"], pos["Moon"]["longitude"]
    elong = norm(moon - sun); waxing = elong < 180
    paksha_raw = (elong if elong <= 180 else 360 - elong) / 3  # 0..60
    merc_mal = any(sign_of[q] == sign_of["Mercury"] for q in ("Sun", "Mars", "Saturn"))
    asc_s = int(asc // 30)
    # equatorial for ayana & nathonnata
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    decl = {}
    for p, b in zip(PL, [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]):
        decl[p] = swe.calc_ut(jd, b, flags)[0][1]
    # time of day: sun's hour angle (0 = noon)
    armc = swe.houses(jd, lat, lon)[1][2]
    sun_ra = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    ha = norm(armc - sun_ra)  # degrees west of meridian
    from_midnight = abs(angdiff(ha, 180))  # 0 at midnight .. 180 at noon
    is_day = from_midnight > 90 if sunrise_jd is None else (sunrise_jd <= jd < sunset_jd)
    # tribhaga
    if sunrise_jd is not None and sunset_jd is not None:
        if is_day:
            part = int(3 * (jd - sunrise_jd) / (sunset_jd - sunrise_jd)); tri_lord = ["Mercury", "Sun", "Saturn"][min(part, 2)]
        else:
            nxt = sunrise_jd + 1; base = sunset_jd if jd >= sunset_jd else sunset_jd - 1
            part = int(3 * (jd - base) / (nxt - sunset_jd)) if jd >= sunset_jd else int(3 * (jd - base) / (sunrise_jd - base))
            tri_lord = ["Moon", "Venus", "Mars"][max(0, min(part, 2))]
    else:
        tri_lord = "Sun" if is_day else "Moon"
    # day lords (Vedic day starts at sunrise)
    civil = int(jd + 0.5 + (lon / 360))  # local-mean-day number
    if sunrise_jd is not None and jd < sunrise_jd: civil -= 1
    wd = (civil + 1) % 7  # 0 = Sunday
    vara_lord = WEEKDAY_LORD[wd]
    ahar = int(jd + lon / 360 - KALI_JD)
    abda_lord = WEEKDAY_LORD[(3 * (ahar // 360) + 1) % 7]
    masa_lord = WEEKDAY_LORD[(2 * (ahar // 30) + 1) % 7]
    if sunrise_jd is not None:
        hrs = int(((jd - sunrise_jd) % 1) * 24)
        hora_lord = CHALDEAN[(CHALDEAN.index(vara_lord) + hrs) % 7]
    else:
        hora_lord = vara_lord
    res = {}
    for p in PL:
        L = pos[p]["longitude"]; s = sign_of[p]
        uccha = (180 - abs(angdiff(L, EXALT_DEG[p]))) / 3
        sapta = 0.0; detail = {}
        for n in (1, 2, 3, 7, 9, 12, 30):
            vs = varga_sign(L, n)
            if n == 1 and MOOLA.get(p) == vs and (L % 30) <= {"Sun": 20, "Moon": 30, "Mars": 12, "Mercury": 20, "Jupiter": 10, "Venus": 15, "Saturn": 20}[p]:
                k = "moolatrikona"
            elif vs in OWN[p]: k = "own"
            else: k = _compound(p, SIGN_LORDS[vs], sign_of)
            if k == "own" and SIGN_LORDS[vs] != p: k = "neutral"
            detail[f"D{n}"] = k; sapta += SAPTA_PTS[k]
        oja = 0
        for n in (1, 9):
            vs = varga_sign(L, n); odd = vs % 2 == 0
            oja += 15 if ((p in ("Moon", "Venus")) != odd) else 0
        hk = (s - asc_s) % 12 + 1
        kendradi = 60 if hk in (1, 4, 7, 10) else 30 if hk in (2, 5, 8, 11) else 15
        dk = int((L % 30) // 10)
        drekkana = 15 if (p in ("Sun", "Mars", "Jupiter") and dk == 0) or (p in ("Mercury", "Saturn") and dk == 1) or (p in ("Moon", "Venus") and dk == 2) else 0
        sthana = uccha + sapta + oja + kendradi + drekkana
        weak = norm(asc + (DIG_ZERO_HOUSE[p] - 1) * 30) if not cusps else cusps[DIG_ZERO_HOUSE[p] - 1]
        dig = abs(angdiff(L, weak)) / 3
        # kala
        if p == "Mercury": nath = 60
        elif p in ("Sun", "Jupiter", "Venus"): nath = from_midnight / 3
        else: nath = (180 - from_midnight) / 3
        paksha = paksha_raw if _benefic(p, waxing, merc_mal) else 60 - paksha_raw
        if p == "Moon": paksha *= 2
        tribhaga = 60 if p == "Jupiter" or p == tri_lord else 0
        lords = (15 if p == abda_lord else 0) + (30 if p == masa_lord else 0) + (45 if p == vara_lord else 0) + (60 if p == hora_lord else 0)
        d = decl[p]
        if p == "Mercury": ayana = (24 + abs(d)) / 48 * 60
        elif p in ("Moon", "Saturn"): ayana = (24 - d) / 48 * 60
        else: ayana = (24 + d) / 48 * 60
        if p == "Sun": ayana *= 2
        ayana = max(0, ayana)
        # cheshta
        sp = pos[p]["speed"]
        if p == "Sun": cheshta = ayana / 2
        elif p == "Moon": cheshta = paksha / 2
        else:
            m = MEAN_SPEED[p]
            if sp < 0: cheshta = 60
            elif abs(sp) < 0.1 * m: cheshta = 15   # vikala (stationary)
            elif sp < 0.5 * m: cheshta = 15        # mandatara
            elif sp < m: cheshta = 30              # manda
            elif sp < 1.1 * m: cheshta = 7.5       # sama
            elif sp < 1.5 * m: cheshta = 45        # chara
            else: cheshta = 30                     # atichara
        res[p] = {"uccha": uccha, "saptavargaja": sapta, "saptavarga_dignities": detail, "ojhayugma": oja, "kendradi": kendradi,
                  "drekkana": drekkana, "sthana": sthana, "dig": dig, "nathonnata": nath, "paksha": paksha, "tribhaga": tribhaga,
                  "abda_masa_vara_hora": lords, "ayana": ayana, "cheshta": cheshta, "naisargika": NAISARGIKA[p]}
    # yuddha (planetary war among Mars..Saturn within 1 degree)
    star = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i, a in enumerate(star):
        for b in star[i + 1:]:
            if abs(angdiff(pos[a]["longitude"], pos[b]["longitude"])) < 1:
                ka = lambda q: res[q]["sthana"] + res[q]["dig"] + res[q]["nathonnata"] + res[q]["paksha"] + res[q]["tribhaga"] + res[q]["abda_masa_vara_hora"] + res[q]["ayana"]
                diff = abs(ka(a) - ka(b))
                w, l = (a, b) if ka(a) >= ka(b) else (b, a)
                res[w]["yuddha"] = res[w].get("yuddha", 0) + diff; res[l]["yuddha"] = res[l].get("yuddha", 0) - diff
    # drik
    for p in PL:
        tot = 0.0
        for q in PL:
            if q == p: continue
            v = drishti_value(pos[p]["longitude"] - pos[q]["longitude"], q)
            tot += v if _benefic(q, waxing, merc_mal) else -v
        res[p]["drik"] = tot / 4
    out = {}
    for p in PL:
        r = res[p]; r.setdefault("yuddha", 0)
        kala = r["nathonnata"] + r["paksha"] + r["tribhaga"] + r["abda_masa_vara_hora"] + r["ayana"] + r["yuddha"]
        total = r["sthana"] + r["dig"] + kala + r["cheshta"] + r["naisargika"] + r["drik"]
        ishta = math.sqrt(max(r["uccha"], 0) * max(r["cheshta"], 0))
        kashta = math.sqrt(max(60 - r["uccha"], 0) * max(60 - r["cheshta"], 0))
        rnd = lambda x: round(x, 2) if isinstance(x, (int, float)) else x
        out[p] = {k: rnd(v) for k, v in r.items()}
        out[p].update({"kala": round(kala, 2), "total_virupas": round(total, 2), "total_rupas": round(total / 60, 3),
                       "required_rupas": REQUIRED_RUPAS[p], "ratio": round(total / 60 / REQUIRED_RUPAS[p], 3),
                       "strong": total / 60 >= REQUIRED_RUPAS[p], "ishta_phala": round(ishta, 2), "kashta_phala": round(kashta, 2)})
    ranked = sorted(PL, key=lambda q: -out[q]["ratio"])
    for i, q in enumerate(ranked): out[q]["rank"] = i + 1
    return {"method": "BPHS six-fold strength (Sthana, Dig, Kala, Cheshta, Naisargika, Drik)",
            "lords": {"abda": abda_lord, "masa": masa_lord, "vara": vara_lord, "hora": hora_lord, "tribhaga": tri_lord},
            "planets": out, "strongest": ranked[0], "weakest": ranked[-1]}

NARA = {2, 5, 6, 10}; JALA = {3, 11}; KEETA = {7}; CHATUSH = {0, 1, 4}
def bhavabala(sb: dict, pos: dict, asc: float, cusps: list | None = None):
    """Bhava bala = Bhavadhipati bala + Bhava dig bala + Bhava drishti bala (BPHS ch. 28)."""
    sun, moon = pos["Sun"]["longitude"], pos["Moon"]["longitude"]
    waxing = norm(moon - sun) < 180
    sign_of = {p: int(pos[p]["longitude"] // 30) for p in PL}
    merc_mal = any(sign_of[q] == sign_of["Mercury"] for q in ("Sun", "Mars", "Saturn"))
    out = []
    for h in range(1, 13):
        cusp = cusps[h - 1] if cusps else norm(asc + (h - 1) * 30)
        s = int(cusp // 30); deg = cusp % 30
        lord = SIGN_LORDS[s]
        adhipati = sb["planets"][lord]["total_virupas"]
        if s in NARA or (s == 8 and deg < 15): strong = 1
        elif s in JALA or (s == 9 and deg >= 15): strong = 4
        elif s in KEETA: strong = 7
        else: strong = 10
        dist = min((h - strong) % 12, (strong - h) % 12)
        dig = (6 - dist) * 10
        dr = 0.0
        for q in PL:
            v = drishti_value(cusp - pos[q]["longitude"], q)
            dr += v if _benefic(q, waxing, merc_mal) else -v
        dr /= 4
        if any(sign_of[q] == s for q in ("Jupiter", "Mercury")): dr += 60
        if any(sign_of[q] == s for q in ("Saturn", "Mars", "Sun")): dr -= 60
        tot = adhipati + dig + dr
        out.append({"house": h, "lord": lord, "bhavadhipati": round(adhipati, 2), "dig": round(dig, 2), "drishti": round(dr, 2),
                    "total_virupas": round(tot, 2), "total_rupas": round(tot / 60, 3)})
    ranked = sorted(out, key=lambda x: -x["total_virupas"])
    for i, x in enumerate(ranked): x["rank"] = i + 1
    return {"houses": out, "strongest_house": ranked[0]["house"], "weakest_house": ranked[-1]["house"]}

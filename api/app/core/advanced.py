"""KP system, Jaimini, Lal Kitab, Varshaphal, Ashtottari, current dasha, avakahada, remedies, extra doshas,
bhava chalit, avastha, friendship tables, special panchang yogas."""
from __future__ import annotations
from datetime import timedelta
import swisseph as swe
from .ephem import find_root
from .ephem import (all_positions, houses, jd_from_utc, calc, norm, angdiff, SIGNS, RASHIS, NAKSHATRAS, NAK_LORDS,
                    SIGN_LORDS, VEDIC_PLANETS, local_from_jd, set_ayanamsa_mode, nakshatra_of, next_boundary, WEEKDAYS)
from .kundli import VIM_ORDER, VIM_YEARS, YEAR_DAYS, FRIENDS, relation, varga_sign, EXALT
from .matching import VARNA, VARNA_NAMES, vashya, VASHYA_NAMES, YONI, GANA, GANA_NAMES, NADI, NADI_NAMES

# ---------- KP ----------
def kp_lords(lon: float):
    span = 360 / 27
    ni = int(lon // span); off = lon - ni * span
    star = NAK_LORDS[ni % 9]
    i = VIM_ORDER.index(star); acc = 0.0; sub = subsub = None
    for k in range(9):
        L = VIM_ORDER[(i + k) % 9]; w = span * VIM_YEARS[L] / 120
        if off < acc + w:
            sub = L; o2 = off - acc; j = VIM_ORDER.index(L); a2 = 0.0
            for m in range(9):
                L2 = VIM_ORDER[(j + m) % 9]; w2 = w * VIM_YEARS[L2] / 120
                if o2 < a2 + w2: subsub = L2; break
                a2 += w2
            break
        acc += w
    return {"sign_lord": SIGN_LORDS[int(lon // 30)], "star_lord": star, "sub_lord": sub, "sub_sub_lord": subsub}

def kp_chart(dt_utc, lat, lon):
    from .ephem import _ayan_mode
    tok = set_ayanamsa_mode("kp")
    try:
        return _kp_chart(dt_utc, lat, lon)
    finally:
        _ayan_mode.reset(tok)

def _kp_chart(dt_utc, lat, lon, horary_asc=None):
    jd = jd_from_utc(dt_utc)
    pos = all_positions(jd, True, False, include_outer=False)
    cusps, asc, mc = houses(jd, lat, lon, "P", True)
    if horary_asc is not None:
        from .ephem import ayanamsa as _ay
        ay = _ay(jd); eps = swe.calc_ut(jd, swe.ECL_NUT)[0][0]; target = (horary_asc + ay) % 360
        def f(armc):
            return ((swe.houses_armc(armc % 360, lat, eps, b"P")[1][0] - target + 180) % 360) - 180
        best = min(range(0, 360, 2), key=lambda a: abs(f(a)))
        armc = find_root(f, best - 2, best + 2, 1e-9) if f(best - 2) * f(best + 2) < 0 else best
        c, am = swe.houses_armc(armc % 360, lat, eps, b"P")
        cusps = [(x - ay) % 360 for x in c[:12]]; asc = (am[0] - ay) % 360; mc = (am[1] - ay) % 360
    def house_of(L):
        for i in range(12):
            a, b = cusps[i], cusps[(i + 1) % 12]
            if (L - a) % 360 < (b - a) % 360: return i + 1
        return 12
    owned = {p: [h + 1 for h in range(12) if SIGN_LORDS[int(cusps[h] // 30)] == p] for p in VEDIC_PLANETS}
    planets = []
    occ = {}
    for p in VEDIC_PLANETS:
        L = pos[p]["longitude"]; h = house_of(L); occ[p] = h
        planets.append({"name": p, "longitude": round(L, 6), "sign": SIGNS[int(L // 30)], "house": h, **kp_lords(L)})
    sig = {}
    for pl in planets:
        p = pl["name"]; st = pl["star_lord"]
        sig[p] = {"A_star_lord_occupies": occ.get(st), "B_occupies": occ[p], "C_star_lord_owns": owned.get(st, []), "D_owns": owned[p]}
    house_sig = {}
    for h in range(1, 13):
        occupants = [p for p in VEDIC_PLANETS if occ[p] == h]
        house_sig[h] = {"occupants": occupants, "in_star_of_occupants": [p["name"] for p in planets if p["star_lord"] in occupants],
                        "owner": SIGN_LORDS[int(cusps[h - 1] // 30)],
                        "in_star_of_owner": [p["name"] for p in planets if p["star_lord"] == SIGN_LORDS[int(cusps[h - 1] // 30)]]}
    moon = pos["Moon"]["longitude"]
    wd = (dt_utc.weekday() + 1) % 7
    rp = {"day_lord": ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"][wd],
          "moon_sign_lord": SIGN_LORDS[int(moon // 30)], "moon_star_lord": kp_lords(moon)["star_lord"],
          "lagna_sign_lord": SIGN_LORDS[int(asc // 30)], "lagna_star_lord": kp_lords(asc)["star_lord"],
          "lagna_sub_lord": kp_lords(asc)["sub_lord"]}
    from .ephem import ayanamsa
    out = {"ayanamsa": "Krishnamurti", "ayanamsa_value": round(ayanamsa(jd), 6), "house_system": "Placidus",
           "cusps": [{"house": i + 1, "longitude": round(c, 6), "sign": SIGNS[int(c // 30)], **kp_lords(c)} for i, c in enumerate(cusps)],
           "planets": planets, "planet_significators": sig, "house_significators": house_sig, "ruling_planets": rp}
    return out

def kp_horary_chart(number: int, dt_utc, lat, lon):
    """Full KP horary (prashna) chart: ascendant fixed by the 1-249 number, planets for the judgement moment."""
    seg = kp_horary(number)
    from .ephem import _ayan_mode
    tok = set_ayanamsa_mode("kp")
    try:
        ch = _kp_chart(dt_utc, lat, lon, horary_asc=seg["ascendant_start"] + 1e-6)
    finally:
        _ayan_mode.reset(tok)
    return {"horary": seg, **ch}

def kp_horary(number: int):
    """KP horary 1-249: maps number to an ascendant degree (sign/star/sub divisions)."""
    if not 1 <= number <= 249: raise ValueError("number must be 1..249")
    segs = []; span = 360 / 27
    for ni in range(27):
        star = NAK_LORDS[ni % 9]; i = VIM_ORDER.index(star)
        nstart = ni * span; acc = nstart
        for k in range(9):
            L = VIM_ORDER[(i + k) % 9]; w = span * VIM_YEARS[L] / 120
            a, b = acc, acc + w
            # split at sign boundaries
            cut = (int(a // 30) + 1) * 30
            if a < cut < b - 1e-9:
                segs.append((a, cut, star, L)); segs.append((cut, b, star, L))
            else:
                segs.append((a, b, star, L))
            acc = b
    a, b, star, sub = segs[number - 1]
    return {"number": number, "ascendant_start": round(a, 6), "ascendant_end": round(b, 6), "sign": SIGNS[int(a // 30)],
            "star_lord": star, "sub_lord": sub, "total_segments": len(segs)}

# ---------- Jaimini ----------
KARAKAS = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"]

def jaimini(pos, asc):
    pl = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    order = sorted(pl, key=lambda p: -(pos[p]["longitude"] % 30))
    karakas = {KARAKAS[i]: p for i, p in enumerate(order)}
    asc_s = int(asc // 30)
    sign_of = {p: int(pos[p]["longitude"] // 30) for p in VEDIC_PLANETS}
    lords2 = {7: ["Mars", "Ketu"], 10: ["Saturn", "Rahu"]}
    def lord_sign(s):
        L = SIGN_LORDS[s]
        if s in lords2:  # dual lordship: stronger = the one with more planets / simple: Mars/Saturn default
            pass
        return sign_of[L]
    arudha = {}
    for h in range(12):
        s = (asc_s + h) % 12; ls = lord_sign(s)
        d = (ls - s) % 12; a = (ls + d) % 12
        if a == s: a = (s + 9) % 12
        elif a == (s + 6) % 12: a = (s + 3) % 12
        arudha[f"A{h + 1}" if h else "AL (Arudha Lagna)"] = SIGNS[a]
    ak = karakas["Atmakaraka"]
    return {"chara_karakas": karakas, "arudha_padas": arudha, "upapada": arudha["A12"],
            "karakamsha": SIGNS[varga_sign(pos[ak]["longitude"], 9)], "swamsha_note": "Karakamsha = navamsa sign of Atmakaraka"}

# ---------- Lal Kitab ----------
LK_REMEDY = {"Sun": "Offer water to the rising Sun; respect father", "Moon": "Keep silver; serve mother; avoid milk at night",
             "Mars": "Donate sweets (revdi/batasha) on Tuesday", "Mercury": "Feed green fodder to cows; avoid green clothes",
             "Jupiter": "Apply saffron tilak; respect teachers", "Venus": "Donate curd/camphor; respect spouse",
             "Saturn": "Donate mustard oil on Saturday; serve labourers", "Rahu": "Keep a solid silver ball; float coconut in river",
             "Ketu": "Feed dogs; donate a blanket"}

def lal_kitab(pos, asc):
    asc_s = int(asc // 30)
    house = {p: (int(pos[p]["longitude"] // 30) - asc_s) % 12 + 1 for p in VEDIC_PLANETS}
    lk_houses = {h: [p for p in VEDIC_PLANETS if house[p] == h] for h in range(1, 13)}
    rin = []
    H = lambda p, hs: house[p] in hs
    if any(H(p, [2, 5, 9, 12]) for p in ["Venus", "Mercury", "Rahu"]): rin.append("Pitru Rin (ancestral debt)")
    if H("Ketu", [4]): rin.append("Matru Rin (debt to mother)")
    if any(H(p, [2, 7]) for p in ["Sun", "Rahu", "Ketu"]): rin.append("Stree Rin (debt to women)")
    if any(H(p, [1, 8]) for p in ["Mercury", "Ketu"]): rin.append("Bhai-bandhu Rin (debt to relatives)")
    if any(H(p, [3, 6]) for p in ["Moon"]): rin.append("Beti/Behen Rin (debt to daughter/sister)")
    if any(H(p, [10, 11]) for p in ["Sun", "Moon", "Mars"]): rin.append("Zulm Rin (debt of cruelty)")
    if any(H(p, [12]) for p in ["Sun", "Venus", "Mars"]): rin.append("Ajanma Rin (debt of the unborn)")
    if any(H(p, [4]) for p in ["Rahu"]) or H("Ketu", [12]): rin.append("Kudrati Rin (debt to nature)")
    sleeping = [h for h in range(1, 13) if not lk_houses[h]]
    return {"note": "Lal Kitab uses the Kaal Purush chart: house 1 = Aries; planets placed by bhava from Lagna.",
            "planets": {p: {"house": house[p], "remedy": LK_REMEDY[p]} for p in VEDIC_PLANETS},
            "houses": lk_houses, "sleeping_houses": sleeping, "rin_debts": rin}

# ---------- Ashtottari ----------
ASHT = [("Sun", 6), ("Moon", 15), ("Mars", 8), ("Mercury", 17), ("Saturn", 10), ("Jupiter", 19), ("Rahu", 12), ("Venus", 21)]
ASHT_NAK = [6, 6, 6, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 7, 7, 7]
# index by nakshatra: Ardra(5)→Sun... built below
def _asht_map():
    m = {}; seq = [(5, 0), (6, 0), (7, 0), (8, 0), (9, 1), (10, 1), (11, 1), (12, 2), (13, 2), (14, 2), (15, 2), (16, 3), (17, 3), (18, 3),
                   (19, 4), (20, 4), (21, 4), (22, 5), (23, 5), (24, 5), (25, 6), (26, 6), (0, 6), (1, 6), (2, 7), (3, 7), (4, 7)]
    for n, l in seq: m[n] = l
    return m
ASHT_MAP = _asht_map()

def ashtottari(moon_lon, birth_jd, tz):
    span = 360 / 27; ni = int(moon_lon // span); frac = (moon_lon - ni * span) / span
    li = ASHT_MAP[ni]
    group = [n for n, l in ASHT_MAP.items() if l == li]; group.sort(key=lambda n: (n - 5) % 27)
    pos_in_group = group.index(ni); g = len(group)
    total = ASHT[li][1]
    elapsed = (pos_in_group + frac) / g * total
    t = birth_jd - elapsed * YEAR_DAYS; out = []
    for k in range(8):
        L, y = ASHT[(li + k) % 8]; e = t + y * YEAR_DAYS
        out.append({"lord": L, "years": y, "start": local_from_jd(t, tz).date().isoformat(), "end": local_from_jd(e, tz).date().isoformat()})
        t = e
    return {"balance_at_birth": {"lord": ASHT[li][0], "years_remaining": round(total - elapsed, 4)}, "mahadasha": out}

def current_vimshottari(moon_lon, birth_jd, now_jd, tz, levels=5):
    span = 360 / 27; ni = int(moon_lon // span); frac = (moon_lon - ni * span) / span
    lord = NAK_LORDS[ni % 9]
    start = birth_jd - frac * VIM_YEARS[lord] * YEAR_DAYS
    names = ["mahadasha", "antardasha", "pratyantardasha", "sookshma", "prana"]
    out = []; s = start; total = 120.0; L = lord
    # find mahadasha
    seq_start = s; i = VIM_ORDER.index(L)
    length = None
    for lvl in range(levels):
        span_y = total if lvl else None
        found = False
        t = s
        for k in range(9 if lvl else 30):
            P = VIM_ORDER[(i + k) % 9]
            y = VIM_YEARS[P] if lvl == 0 else total * VIM_YEARS[P] / 120
            e = t + y * YEAR_DAYS
            if t <= now_jd < e:
                out.append({"level": names[lvl], "lord": P, "start": local_from_jd(t, tz).isoformat(timespec="minutes"), "end": local_from_jd(e, tz).isoformat(timespec="minutes")})
                s, total, i = t, y, VIM_ORDER.index(P); found = True; break
            t = e
        if not found: break
    return out

# ---------- Avakahada / basic details ----------
SYLLABLES = ["Chu Che Cho La", "Li Lu Le Lo", "A I U E", "O Va Vi Vu", "Ve Vo Ka Ki", "Ku Gha Ng Chha", "Ke Ko Ha Hi",
             "Hu He Ho Da", "Di Du De Do", "Ma Mi Mu Me", "Mo Ta Ti Tu", "Te To Pa Pi", "Pu Sha Na Tha", "Pe Po Ra Ri",
             "Ru Re Ro Ta", "Ti Tu Te To", "Na Ni Nu Ne", "No Ya Yi Yu", "Ye Yo Bha Bhi", "Bhu Dha Pha Dha", "Bhe Bho Ja Ji",
             "Ju Je Jo Gha", "Ga Gi Gu Ge", "Go Sa Si Su", "Se So Da Di", "Du Tha Jha Na", "De Do Cha Chi"]
TATVA = ["Fire", "Earth", "Air", "Water"]

def avakahada(moon_lon, sun_lon, asc, tithi_idx=None, yoga_idx=None, karana_name=None):
    ni, pada = nakshatra_of(moon_lon); ms = int(moon_lon // 30)
    paya_idx = (ms - int(asc // 30)) % 12 + 1
    paya = "Gold" if paya_idx in (1, 6, 11) else "Silver" if paya_idx in (2, 5, 9) else "Copper" if paya_idx in (3, 7, 10) else "Iron"
    return {"varna": VARNA_NAMES[VARNA[ms]], "vashya": VASHYA_NAMES[vashya(moon_lon)], "yoni": YONI[ni], "gana": GANA_NAMES[GANA[ni]],
            "nadi": NADI_NAMES[NADI[ni]], "rashi": RASHIS[ms], "rashi_lord": SIGN_LORDS[ms], "nakshatra": NAKSHATRAS[ni], "pada": pada,
            "nakshatra_lord": NAK_LORDS[ni % 9], "naam_akshar": SYLLABLES[ni].split()[pada - 1], "nakshatra_syllables": SYLLABLES[ni].split(),
            "paya": paya, "tatva": TATVA[ms % 4], "sun_sign_sidereal": RASHIS[int(sun_lon // 30)]}

# ---------- remedies ----------
GEMS = {"Sun": ("Ruby (Manik)", "Ek Mukhi", "Om Hraam Hreem Hraum Sah Suryaya Namah"), "Moon": ("Pearl (Moti)", "Do Mukhi", "Om Shraam Shreem Shraum Sah Chandraya Namah"),
        "Mars": ("Red Coral (Moonga)", "Teen Mukhi", "Om Kraam Kreem Kraum Sah Bhaumaya Namah"), "Mercury": ("Emerald (Panna)", "Char Mukhi", "Om Braam Breem Braum Sah Budhaya Namah"),
        "Jupiter": ("Yellow Sapphire (Pukhraj)", "Panch Mukhi", "Om Graam Greem Graum Sah Gurave Namah"), "Venus": ("Diamond / White Sapphire", "Chhah Mukhi", "Om Draam Dreem Draum Sah Shukraya Namah"),
        "Saturn": ("Blue Sapphire (Neelam)", "Saat Mukhi", "Om Praam Preem Praum Sah Shanaye Namah"), "Rahu": ("Hessonite (Gomed)", "Aath Mukhi", "Om Bhraam Bhreem Bhraum Sah Rahave Namah"),
        "Ketu": ("Cat's Eye (Lehsunia)", "Nau Mukhi", "Om Sraam Sreem Sraum Sah Ketave Namah")}

def remedies(asc):
    a = int(asc // 30)
    lord = lambda h: SIGN_LORDS[(a + h - 1) % 12]
    g = lambda p: {"planet": p, "gemstone": GEMS[p][0], "rudraksha": GEMS[p][1], "mantra": GEMS[p][2]}
    return {"life_stone": g(lord(1)), "benefic_stone": g(lord(5)), "lucky_stone": g(lord(9)),
            "disclaimer": "Traditional suggestions only; consult an astrologer before wearing gemstones."}

# ---------- extra doshas ----------
def extra_doshas(sign_of, houses_of):
    same = lambda a, b: sign_of[a] == sign_of[b]
    return {"guru_chandal": same("Jupiter", "Rahu") or same("Jupiter", "Ketu"),
            "grahan": {"surya": same("Sun", "Rahu") or same("Sun", "Ketu"), "chandra": same("Moon", "Rahu") or same("Moon", "Ketu")},
            "pitra": same("Sun", "Rahu") or same("Sun", "Saturn") or houses_of["Rahu"] == 9,
            "kemadruma": None, "angarak": same("Mars", "Rahu"), "shrapit": same("Saturn", "Rahu"),
            "vish": same("Moon", "Saturn")}

# ---------- chalit, avastha, friendship ----------
def bhava_chalit(pos, cusps):
    mids = cusps  # Placidus/Sripati-style: cusp = bhava madhya; bhava starts at midpoint between cusps
    starts = [norm(mids[i - 1] + norm(mids[i] - mids[i - 1]) / 2) for i in range(12)]
    res = {}
    for p in VEDIC_PLANETS:
        L = pos[p]["longitude"]
        for i in range(12):
            a, b = starts[i], starts[(i + 1) % 12]
            if (L - a) % 360 < (b - a) % 360: res[p] = i + 1; break
    return {"bhava_start": [round(s, 4) for s in starts], "bhava_madhya": [round(m, 4) for m in mids], "planet_bhava": res}

def avastha(lon):
    s, d = int(lon // 30), lon % 30
    names = ["Bala (infant)", "Kumara (youth)", "Yuva (adult)", "Vriddha (old)", "Mrita (dead)"]
    k = min(int(d // 6), 4)
    return names[k] if s % 2 == 0 else names[4 - k]

def friendship(sign_of):
    pl = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    nat, tmp, comp = {}, {}, {}
    for a in pl:
        nat[a], tmp[a], comp[a] = {}, {}, {}
        for b in pl:
            if a == b: continue
            n = relation(a, b); d = (sign_of[b] - sign_of[a]) % 12 + 1
            t = "friend" if d in (2, 3, 4, 10, 11, 12) else "enemy"
            sc = {"friend": 1, "neutral": 0, "enemy": -1}[n] + (1 if t == "friend" else -1)
            c = {2: "great friend", 1: "friend", 0: "neutral", -1: "enemy", -2: "great enemy"}[sc]
            nat[a][b] = n; tmp[a][b] = t; comp[a][b] = c
    return {"natural": nat, "temporary": tmp, "compound": comp}

# ---------- Varshaphal ----------
def solar_return(birth_jd, natal_sun, year, sidereal=True):
    from .ephem import sun_lon
    y, m, d, h = swe.revjul(birth_jd)
    guess = swe.julday(year, m, d, h)
    f = lambda j: angdiff(sun_lon(j, sidereal), natal_sun)
    t = guess
    for _ in range(20):
        t -= f(t) / 0.9856
    return t

TAJIK = [("Ithasala", "applying aspect"), ("Ishrafa", "separating aspect")]

def varshaphal(birth_utc, lat, lon, year, tz):
    from .kundli import compute_kundli
    bjd = jd_from_utc(birth_utc)
    natal_sun = calc(bjd, swe.SUN, True)[0]
    rj = solar_return(bjd, natal_sun, year, True)
    from .ephem import utc_from_jd
    k = compute_kundli(utc_from_jd(rj), lat, lon, tz, dasha_levels=1)
    nat = compute_kundli(birth_utc, lat, lon, tz, dasha_levels=1)
    age = year - birth_utc.year
    muntha = (SIGNS.index(nat["lagna"]["sign"]) + age) % 12
    # Mudda (Vimshottari compressed to 1 year: 120y -> 360 days)
    moon = [p for p in k["planets"] if p["name"] == "Moon"][0]["longitude"]
    span = 360 / 27; ni = int(moon // span); frac = (moon - ni * span) / span
    L0 = NAK_LORDS[(ni + age - 2) % 9] if False else NAK_LORDS[ni % 9]
    i0 = VIM_ORDER.index(L0); t = rj - frac * VIM_YEARS[L0] * 3; mudda = []
    for kk in range(9):
        L = VIM_ORDER[(i0 + kk) % 9]; e = t + VIM_YEARS[L] * 3.0
        mudda.append({"lord": L, "start": local_from_jd(t, tz).date().isoformat(), "end": local_from_jd(e, tz).date().isoformat()}); t = e
    # Tajik aspects (orbs per deeptamsha)
    DEEPT = {"Sun": 15, "Moon": 12, "Mars": 8, "Mercury": 7, "Jupiter": 9, "Venus": 7, "Saturn": 9}
    P = {p["name"]: p for p in k["planets"]}
    yogas = []
    for a in DEEPT:
        for b in DEEPT:
            if a >= b: continue
            sep = abs(angdiff(P[a]["longitude"], P[b]["longitude"]))
            for ang in (0, 60, 90, 120, 180):
                orb = (DEEPT[a] + DEEPT[b]) / 2
                if abs(sep - ang) <= orb:
                    fast, slow = (a, b) if abs(P[a]["speed"]) > abs(P[b]["speed"]) else (b, a)
                    applying = (P[fast]["longitude"] % 30) < (P[slow]["longitude"] % 30)
                    yogas.append({
                        "planets": [a, b],
                        "aspect": ang,
                        "yoga": "Ithasala" if applying else "Ishrafa",
                        "note": f"{fast} applies to {slow} ({ang}° aspect)" if applying else f"{fast} separates from {slow} ({ang}° aspect)",
                    })
    # Sahams (day formulae)
    asc = k["lagna"]["longitude"]; S = lambda p: P[p]["longitude"]
    sahams = {"Punya": norm(S("Moon") - S("Sun") + asc), "Vidya": norm(S("Sun") - S("Moon") + asc),
              "Yashas": norm(S("Jupiter") - norm(S("Moon") - S("Sun") + asc) + asc), "Karma": norm(S("Mars") - S("Mercury") + asc),
              "Vivaha": norm(S("Venus") - S("Saturn") + asc), "Putra": norm(S("Jupiter") - S("Moon") + asc)}
    # ---- extra Tajik yogas ----
    hs = {p: P[p]["house"] for p in DEEPT}
    if all(h in (1, 2, 4, 5, 7, 8, 10, 11) for h in hs.values()): yogas.append({"planets": list(DEEPT), "aspect": 0, "yoga": "Ikkabal", "note": "all planets in kendra/panapara: success"})
    elif all(h in (3, 6, 9, 12) for h in hs.values()): yogas.append({"planets": list(DEEPT), "aspect": 0, "yoga": "Induvara", "note": "all planets in apoklima: obstacles"})
    asp = lambda a, b: any(abs(abs(angdiff(P[a]["longitude"], P[b]["longitude"])) - g) <= (DEEPT[a] + DEEPT[b]) / 2 for g in (0, 60, 90, 120, 180))
    pairs = [(a, b) for a in DEEPT for b in DEEPT if a < b]
    for a, b in pairs:
        if asp(a, b): continue
        for c in DEEPT:
            if c in (a, b) or not (asp(c, a) and asp(c, b)): continue
            sp = lambda x: abs(P[x]["speed"])
            if sp(c) > max(sp(a), sp(b)): yogas.append({"planets": [a, b, c], "aspect": 60, "yoga": "Nakta", "note": f"{c} transfers light between {a} and {b}"})
            elif sp(c) < min(sp(a), sp(b)): yogas.append({"planets": [a, b, c], "aspect": 120, "yoga": "Yamaya", "note": f"{c} collects light of {a} and {b}"})
    ith = [y for y in yogas if y.get("yoga") == "Ithasala"]
    for y in ith:
        a, b = y["planets"]
        for x in (a, b):
            if P[x]["retrograde"] or P[x].get("combust"): yogas.append({"planets": [a, b], "aspect": y["aspect"], "yoga": "Radda", "note": f"{x} retrograde/combust spoils the Ithasala"})
        if "Moon" not in (a, b) and any(set(z["planets"]) in ({"Moon", a}, {"Moon", b}) for z in ith):
            yogas.append({"planets": [a, b, "Moon"], "aspect": y["aspect"], "yoga": "Kamboola", "note": "Moon in Ithasala with a participant strengthens it"})
        for m in ("Mars", "Saturn"):
            if m not in (a, b) and (asp(m, a) or asp(m, b)) and P[m]["speed"] > 0:
                yogas.append({"planets": [a, b, m], "aspect": y["aspect"], "yoga": "Manau", "note": f"malefic {m} interferes with the Ithasala"}); break
    if not any("Moon" in z["planets"] and z.get("yoga") == "Ithasala" for z in ith):
        yogas.append({"planets": ["Moon"], "aspect": 0, "yoga": "Khallasara", "note": "Moon forms no applying aspect: matters lack support"})
    # ---- Pancha-adhikari and Varsheshwara (year lord) ----
    wd = (local_from_jd(rj, tz).weekday() + 1) % 7
    vsun = P["Sun"]["house"]; day = vsun in (7, 8, 9, 10, 11, 12)
    TRI = {"Aries": ("Sun", "Jupiter"), "Taurus": ("Venus", "Moon"), "Gemini": ("Saturn", "Mercury"), "Cancer": ("Venus", "Mars"),
           "Leo": ("Jupiter", "Sun"), "Virgo": ("Moon", "Venus"), "Libra": ("Mercury", "Saturn"), "Scorpio": ("Mars", "Venus"),
           "Sagittarius": ("Saturn", "Saturn"), "Capricorn": ("Mars", "Mars"), "Aquarius": ("Jupiter", "Jupiter"), "Pisces": ("Moon", "Moon")}
    adhikari = {"muntha_lord": SIGN_LORDS[muntha], "janma_lagna_lord": SIGN_LORDS[SIGNS.index(nat["lagna"]["sign"])],
                "varsha_lagna_lord": SIGN_LORDS[SIGNS.index(k["lagna"]["sign"])],
                "dina_ratri_lord": SIGN_LORDS[SIGNS.index(P["Sun"]["sign"])] if day else SIGN_LORDS[SIGNS.index(P["Moon"]["sign"])],
                "trirashi_lord": TRI[k["lagna"]["sign"]][0 if day else 1]}
    vl = SIGNS.index(k["lagna"]["sign"])
    sees = lambda p: ((vl - SIGNS.index(P[p]["sign"])) % 12 + 1) in (1, 3, 4, 5, 7, 9, 10, 11)
    strength = {p: k["shadbala"]["planets"][p]["total_virupas"] for p in set(adhikari.values()) if p in k["shadbala"]["planets"]}
    cands = [p for p in strength if sees(p)] or list(strength)
    year_lord = max(cands, key=lambda p: strength[p]) if cands else adhikari["muntha_lord"]
    return {"year": year, "age": age, "solar_return_moment": local_from_jd(rj, tz).isoformat(timespec="seconds"),
            "varsha_lagna": k["lagna"], "planets": k["planets"], "muntha": {"sign": SIGNS[muntha], "house": (muntha - SIGNS.index(k["lagna"]["sign"])) % 12 + 1},
            "pancha_adhikari": adhikari, "year_lord": year_lord, "birth_in_day": day, "adhikari_strength_virupas": {p: round(v, 1) for p, v in strength.items()},
            "year_lord_note": "Varsheshwara = strongest (Shadbala) of the Pancha-adhikari that aspects the Varsha Lagna (Tajik aspects).",
            "mudda_dasha": mudda, "tajik_yogas": yogas, "sahams": {k2: {"longitude": round(v, 4), "sign": SIGNS[int(v // 30)]} for k2, v in sahams.items()}}

# ---------- special panchang yogas ----------
ANANDADI = ["Ananda", "Kaladanda", "Dhumra", "Prajapati", "Saumya", "Dhwanksha", "Dhwaja", "Shrivatsa", "Vajra", "Mudgara",
            "Chhatra", "Mitra", "Manasa", "Padma", "Lumbaka", "Utpata", "Mrityu", "Kana", "Siddhi", "Shubha", "Amrita",
            "Musala", "Gada", "Matanga", "Rakshasa", "Chara", "Sthira", "Vardhamana"]
ANANDADI_GOOD = {"Ananda", "Prajapati", "Saumya", "Dhwaja", "Shrivatsa", "Chhatra", "Mitra", "Manasa", "Padma", "Siddhi", "Shubha", "Amrita", "Matanga", "Sthira", "Vardhamana"}
ANANDADI_START = [0, 4, 8, 12, 16, 20, 24]  # in 28-nakshatra list (Abhijit after U.Ashadha)

def nak28(ni27):
    return ni27 if ni27 <= 20 else ni27 + 1

def anandadi(weekday, ni27):
    k = (nak28(ni27) - ANANDADI_START[weekday]) % 28
    return {"name": ANANDADI[k], "auspicious": ANANDADI[k] in ANANDADI_GOOD}

def special_yogas(weekday, tithi_idx, ni27, sun_ni27):
    t = tithi_idx % 15 + 1; y = []
    if weekday == 0 and ni27 == 7: y.append("Ravi Pushya Yoga")
    if weekday == 4 and ni27 == 7: y.append("Guru Pushya Yoga")
    if weekday in (0, 2, 6) and t in (2, 7, 12):
        if ni27 in (4, 13, 22): y.append("Dwipushkar Yoga")
        if ni27 in (2, 6, 11, 15, 20, 24): y.append("Tripushkar Yoga")
    if ((ni27 - sun_ni27) % 27 + 1) in (4, 6, 9, 10, 13, 20): y.append("Ravi Yoga")
    return y

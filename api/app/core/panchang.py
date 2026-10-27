"""Daily Panchang: tithi, nakshatra, yoga, karana, vara, sun/moon rise-set, months, samvat, muhurtas."""
from __future__ import annotations
import math
from datetime import date as Date, datetime, timedelta
from .ephem import (swe, sun_lon, moon_lon, norm, next_boundary, rise_set, local_midnight_jd, fmt, make_tz,
                    NAKSHATRAS, NAK_LORDS, RASHIS, SIGNS, WEEKDAYS, VARAS, sign_info, nakshatra_of, ascendant,
                    find_root, angdiff, local_from_jd, ayanamsa)

TITHIS = ["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami",
          "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
          "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami",
          "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Amavasya"]
YOGAS = ["Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti","Shula","Ganda",
         "Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva",
         "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
MOVABLE_KARANAS = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]
MONTHS = ["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada","Ashwin","Kartika",
          "Margashirsha","Pausha","Magha","Phalguna"]
RITUS = ["Vasanta","Grishma","Varsha","Sharad","Hemanta","Shishira"]
SAMVATSARAS = ["Prabhava","Vibhava","Shukla","Pramoda","Prajapati","Angirasa","Shrimukha","Bhava","Yuva","Dhatri",
 "Ishvara","Bahudhanya","Pramathi","Vikrama","Vrisha","Chitrabhanu","Svabhanu","Tarana","Parthiva","Vyaya",
 "Sarvajit","Sarvadhari","Virodhi","Vikriti","Khara","Nandana","Vijaya","Jaya","Manmatha","Durmukhi",
 "Hevilambi","Vilambi","Vikari","Sharvari","Plava","Shubhakrit","Shobhakrit","Krodhi","Vishvavasu","Parabhava",
 "Plavanga","Kilaka","Saumya","Sadharana","Virodhikrit","Paridhavi","Pramadi","Ananda","Rakshasa","Nala",
 "Pingala","Kalayukta","Siddharthi","Raudra","Durmati","Dundubhi","Rudhirodgari","Raktakshi","Krodhana","Akshaya"]

def karana_name(i: int) -> str:  # i in 0..59
    if i == 0: return "Kimstughna"
    if i >= 57: return ["Shakuni","Chatushpada","Naga"][i - 57]
    return MOVABLE_KARANAS[(i - 1) % 7]

# angle functions (monotonic increasing)
elong = lambda jd: norm(moon_lon(jd, False) - sun_lon(jd, False))
moon_sid = lambda jd: moon_lon(jd, True)
yoga_ang = lambda jd: norm(moon_lon(jd, True) + sun_lon(jd, True))
sun_sid = lambda jd: sun_lon(jd, True)

def tithi_at(jd): return int(elong(jd) // 12)
def nak_at(jd): return int(moon_sid(jd) // (360 / 27))
def yoga_at(jd): return int(yoga_ang(jd) // (360 / 27))
def karana_at(jd): return int(elong(jd) // 6)

def spans(func, step, names_fn, jd_from, jd_to, tz, extra=None, max_days=3):
    """List elements (index, name, start, end) of func's step-segments overlapping [jd_from, jd_to]."""
    out = []
    t = jd_from
    start, _ = next_boundary(func, t + 1e-6, step, forward=False, max_days=max_days)
    while True:
        idx = int((func(t + 1e-6) % 360) // step)
        end, _ = next_boundary(func, t + 1e-6, step, forward=True, max_days=max_days)
        item = {"index": idx + 1, "name": names_fn(idx), "start": fmt(start, tz), "end": fmt(end, tz),
                "_s": start, "_e": end}
        if extra: item.update(extra(idx))
        out.append(item)
        if end is None or end >= jd_to:
            break
        t = end + 1e-6; start = end
    return out

def strip(items):
    return [{k: v for k, v in i.items() if not k.startswith("_")} for i in items]

# ---------------- sun / moon events ----------------
def day_events(d: Date, lat, lon, tz, alt=0.0):
    j0 = local_midnight_jd(d, tz)
    sr = rise_set(j0, swe.SUN, lat, lon, alt, True)
    ss = rise_set(sr if sr else j0, swe.SUN, lat, lon, alt, False)
    nsr = rise_set((ss or j0) , swe.SUN, lat, lon, alt, True)
    # Panchang day = sunrise to next sunrise
    base = sr if sr else j0
    end = nsr if nsr else base + 1
    # Moon: disc centre, no refraction
    mr = rise_set(base, swe.MOON, lat, lon, alt, True, True, True)
    ms = rise_set(base, swe.MOON, lat, lon, alt, False, True, True)
    if mr and mr >= end: mr = None
    if ms and ms >= end: ms = None
    return dict(midnight=j0, sunrise=sr, sunset=ss, next_sunrise=nsr, moonrise=mr, moonset=ms)

# ---------------- lunar month ----------------
def new_moon_before(jd):
    t, _ = next_boundary(elong, jd, 360.0 if False else 12.0, forward=False)  # placeholder (unused)
    return t

def prev_new_moon(jd):
    # move back to tithi 0 start
    t = jd
    for _ in range(40):
        i = tithi_at(t)
        if i == 0:
            s, _ = next_boundary(elong, t, 12.0, forward=False)
            return s
        s, _ = next_boundary(elong, t, 12.0, forward=False)
        t = s - 1e-4
    return None

def next_new_moon(jd):
    t = jd
    for _ in range(40):
        e, idx = next_boundary(elong, t, 12.0, forward=True)
        if idx == 0:
            return e
        t = e + 1e-4
    return None

def lunar_month(jd):
    """Amanta month at jd: (index 0=Chaitra, adhika flag, nm_start, nm_end)."""
    nm1 = prev_new_moon(jd); nm2 = next_new_moon(jd)
    s1 = int(sun_sid(nm1) // 30); s2 = int(sun_sid(nm2) // 30)
    adhika = (s1 == s2)
    idx = (s1 + 1) % 12  # Sun in Meena at new moon -> Chaitra
    return idx, adhika, nm1, nm2

def samvat_info(d: Date, month_idx: int):
    g = d.year
    # Hindu year starts Chaitra Shukla Pratipada (≈ Mar/Apr)
    before_new_year = (d.month <= 4 and month_idx >= 8)
    shaka = g - 78 - (1 if before_new_year else 0)
    vikram = shaka + 135
    gujarati = vikram if (month_idx >= 7 or month_idx <= 0 and False) else vikram - 1
    if month_idx >= 7 or before_new_year: gujarati = vikram if month_idx >= 7 else vikram
    if 0 <= month_idx <= 6 and not before_new_year: gujarati = vikram - 1
    samv = SAMVATSARAS[(shaka + 11) % 60]  # Shaka 1947 -> Vishvavasu (South Indian / Shaka cycle)
    vsamv = SAMVATSARAS[(shaka + 24) % 60]  # North Indian (Brihaspati) name, approximate (changes mid-year in reality)
    return {"shaka": shaka, "vikram": vikram, "gujarati": gujarati, "shaka_samvatsara": samv,
            "vikram_samvatsara": vsamv, "kaliyuga": shaka + 3179}

# ---------------- muhurta tables ----------------
RAHU_SEG = [8, 2, 7, 5, 6, 4, 3]
YAMA_SEG = [5, 4, 3, 2, 1, 7, 6]
GULI_SEG = [7, 6, 5, 4, 3, 2, 1]
DUR_DAY = {0: [14], 1: [9, 12], 2: [4], 3: [8], 4: [6, 12], 5: [4, 9], 6: [1, 2]}
DUR_NIGHT = {2: [7]}
VARJYAM_G = [50,24,30,40,14,21,30,20,32,30,20,18,21,20,14,14,10,14,20,24,20,10,10,18,16,24,30]
AMRIT_G = [42,48,54,52,38,35,54,44,56,54,44,42,45,44,38,38,34,38,44,48,44,34,34,42,40,48,54]
SARVARTHA = {0: [12,18,11,7,0,20,25], 1: [21,3,4,7,16], 2: [0,25,2,8], 3: [3,16,12,2,4],
             4: [26,16,0,6,7], 5: [26,16,0,6,21], 6: [21,3,14]}
AMRIT_SIDDHI = {0: 12, 1: 4, 2: 0, 3: 16, 4: 7, 5: 26, 6: 3}
DISHA_SHOOL = ["West","East","North","North","South","West","East"]
TARAS = ["Janma","Sampat","Vipat","Kshema","Pratyari","Sadhaka","Vadha","Mitra","Parama Mitra"]

def weekday_of(d: Date) -> int:  # 0 = Sunday
    return (d.weekday() + 1) % 7

def seg(start, end, n, k):  # k 1-based
    L = (end - start) / n
    return start + (k - 1) * L, start + k * L

def window(a, b, tz, **kw):
    return {"start": fmt(a, tz), "end": fmt(b, tz), **kw}

def nak_windows(nak_spans, table, tz):
    out = []
    for n in nak_spans:
        s, e = n["_s"], n["_e"]
        if s is None or e is None: continue
        g = (e - s) / 60
        a = s + table[n["index"] - 1] * g
        out.append({"nakshatra": n["name"], "start": fmt(a, tz), "end": fmt(a + 4 * g, tz), "_s": a, "_e": a + 4 * g})
    return out

GODHULI_RULE = {  # Muhurta Chintamani, Vivaha-prakarana v.98: the "cow-dust" moment depends on the season
    "hemanta": "sun still a full round disc above the horizon (lower limb touching)",
    "grishma": "sun half set (disc centre on the apparent horizon)",
    "varsha": "sun fully set (upper limb gone = ordinary sunset)",
}

def godhuli_season(m_idx: int) -> str:
    """Amanta month 0=Chaitra. Four months from Margashirsha = hemanta, from Chaitra = grishma, from Shravana = varsha."""
    return "grishma" if m_idx <= 3 else ("varsha" if m_idx <= 7 else "hemanta")

def godhuli_start(ss, lat, lon, alt, m_idx):
    season = godhuli_season(m_idx)
    if season == "varsha":
        return ss, season
    fl = swe.BIT_DISC_BOTTOM if season == "hemanta" else swe.BIT_DISC_CENTER
    try:
        res, tret = swe.rise_trans(ss - 0.05, swe.SUN, swe.CALC_SET | fl, (lon, lat, alt), 1013.25, 15.0, swe.FLG_SWIEPH)
        t = tret[0] if res == 0 and ss - 0.05 < tret[0] <= ss else ss
    except swe.Error:
        t = ss
    return t, season

def compute_panchang(d: Date, lat: float, lon: float, tz_name: str | None = None, utc_offset: float | None = None,
                     alt: float = 0.0, janma_rashi: int | None = None, janma_nakshatra: int | None = None):
    tz = make_tz(tz_name, utc_offset)
    ev = day_events(d, lat, lon, tz, alt)
    sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
    if sr is None or ss is None:
        raise ValueError("Sun does not rise/set at this location on this date (polar day/night)")
    wd = weekday_of(d)
    ayan = ayanamsa(sr)

    tithis = spans(elong, 12.0, lambda i: TITHIS[i], sr, nsr, tz,
                   extra=lambda i: {"paksha": "Shukla" if i < 15 else "Krishna"})
    naks = spans(moon_sid, 360 / 27, lambda i: NAKSHATRAS[i], sr, nsr, tz, extra=lambda i: {"lord": NAK_LORDS[i % 9]})
    yogas = spans(yoga_ang, 360 / 27, lambda i: YOGAS[i], sr, nsr, tz)
    karanas = spans(elong, 6.0, karana_name, sr, nsr, tz)
    # nakshatra padas
    padas = spans(moon_sid, 360 / 108, lambda i: f"{NAKSHATRAS[i // 4]} {i % 4 + 1}", sr, nsr, tz)
    moon_signs = spans(moon_sid, 30.0, lambda i: RASHIS[i], sr, nsr, tz, extra=lambda i: {"sign": SIGNS[i]})
    sun_n = spans(sun_sid, 360 / 27, lambda i: NAKSHATRAS[i], sr, nsr, tz, max_days=16)

    t_idx = tithi_at(sr)
    paksha = "Shukla" if t_idx < 15 else "Krishna"
    m_idx, adhika, nm1, nm2 = lunar_month(sr)
    purn_idx = m_idx if paksha == "Shukla" else (m_idx + 1) % 12
    sam = samvat_info(d, m_idx)
    sun_trop = sun_lon(sr, False); sun_s = sun_lon(sr, True)
    solar_ritu = RITUS[int(norm(sun_trop + 30) // 60)]
    vedic_ritu = RITUS[m_idx // 2]
    solar_ayana = "Uttarayana" if (sun_trop >= 270 or sun_trop < 90) else "Dakshinayana"
    vedic_ayana = "Uttarayana" if (sun_s >= 270 or sun_s < 90) else "Dakshinayana"

    day = ss - sr; night = nsr - ss
    dm = day / 15; nm = night / 15
    mid = sr + day / 2
    mu = {}
    a, b = seg(sr, ss, 8, RAHU_SEG[wd]); mu["rahu_kalam"] = window(a, b, tz)
    a, b = seg(sr, ss, 8, YAMA_SEG[wd]); mu["yamaganda"] = window(a, b, tz)
    a, b = seg(sr, ss, 8, GULI_SEG[wd]); mu["gulikai_kalam"] = window(a, b, tz)
    mu["abhijit"] = None if wd == 3 else window(sr + 7 * dm, sr + 8 * dm, tz)
    mu["brahma_muhurta"] = window(nsr - 2 * nm, nsr - nm, tz, note="for next morning")
    pb = ev["sunrise"]
    # Brahma muhurta of *this* morning uses previous night length
    try:
        prev = day_events(d - timedelta(days=1), lat, lon, tz, alt)
        pnm = (sr - prev["sunset"]) / 15
    except OverflowError:
        pnm = nm
    mu["brahma_muhurta"] = window(sr - 2 * pnm, sr - pnm, tz)
    mu["pratah_sandhya"] = window(sr - 1.5 * pnm, sr, tz)
    mu["vijaya_muhurta"] = window(sr + 10 * dm, sr + 11 * dm, tz)
    gs, gseason = godhuli_start(ss, lat, lon, alt, m_idx)
    mu["godhuli_muhurta"] = window(gs, gs + nm / 2, tz, season=gseason)
    mu["sayahna_sandhya"] = window(ss, ss + 1.5 * nm, tz)
    mu["nishita_muhurta"] = window(ss + 7 * nm, ss + 8 * nm, tz)
    durs = [window(*seg(sr, ss, 15, k), tz) for k in DUR_DAY[wd]] + [window(*seg(ss, nsr, 15, k), tz) for k in DUR_NIGHT.get(wd, [])]
    mu["dur_muhurtam"] = durs
    # Varjyam / Amrit Kalam for nakshatras overlapping the day (and previous one)
    nak_ext = spans(moon_sid, 360 / 27, lambda i: NAKSHATRAS[i], sr - 1.2, nsr, tz)
    def in_day(lst):
        return [{k: v for k, v in x.items() if not k.startswith("_")} for x in lst if sr <= x["_s"] < nsr]
    mu["varjyam"] = in_day(nak_windows(nak_ext, VARJYAM_G, tz))
    mu["amrit_kalam"] = in_day(nak_windows(nak_ext, AMRIT_G, tz))

    # Special yogas (weekday + nakshatra) within sunrise..next sunrise
    sy = []
    for n in naks:
        i = n["index"] - 1
        s = max(n["_s"], sr); e = min(n["_e"], nsr)
        if i in SARVARTHA[wd]: sy.append({"yoga": "Sarvartha Siddhi Yoga", "start": fmt(s, tz), "end": fmt(e, tz)})
        if AMRIT_SIDDHI[wd] == i: sy.append({"yoga": "Amrit Siddhi Yoga", "start": fmt(s, tz), "end": fmt(e, tz)})
    from .advanced import anandadi, special_yogas
    sun_ni = int(sun_sid(sr) // (360 / 27))
    for n in naks:
        for name in special_yogas(wd, t_idx, n["index"] - 1, sun_ni):
            sy.append({"yoga": name, "start": fmt(max(n["_s"], sr), tz), "end": fmt(min(n["_e"], nsr), tz)})
    mu["special_yogas"] = sy
    mu["anandadi_yoga"] = [{**anandadi(wd, n["index"] - 1), "until": n["end"]} for n in naks]
    mu["panchaka"] = [{"start": n["start"], "end": n["end"]} for n in naks if n["index"] - 1 in (22, 23, 24, 25, 26) and False] or \
        [{"nakshatra": m["name"], "start": m["start"], "end": m["end"]} for m in strip(moon_signs) if m["name"] in ("Kumbha", "Meena")]
    mu["ganda_moola"] = [{"nakshatra": n["name"], "start": n["start"], "end": n["end"]} for n in strip(naks) if n["index"] - 1 in (0, 8, 9, 17, 18, 26)]
    bh = [k for k in karanas if k["name"] == "Vishti"]
    mu["bhadra"] = [{"start": k["start"], "end": k["end"]} for k in strip(bh)]

    # Chandrabalam follows the Moon's sign, so it changes when the sign changes.
    GOOD_H = (1, 3, 6, 7, 10, 11)
    chandrabalam = []
    for ms in moon_signs:
        mr_i = ms["index"] - 1
        chandrabalam.append({
            "moon_rashi": ms["name"], "until": ms["end"],
            "good_for": [RASHIS[(mr_i - (h - 1)) % 12] for h in GOOD_H],
            "ashtama_rashi": RASHIS[(mr_i - 7) % 12],
        })
    good_taras = {2, 4, 6, 8, 0}
    moon_r = int(moon_sid(sr) // 30); cur_nak = nak_at(sr)
    tarabalam = []
    for n in naks:
        ci = n["index"] - 1
        tarabalam.append({"nakshatra": n["name"], "until": n["end"],
                          "good_for": [NAKSHATRAS[j] for j in range(27) if ((ci - j) % 27 + 1) % 9 in good_taras]})
    personal = {}
    if janma_rashi is not None:
        h = (moon_r - janma_rashi) % 12 + 1
        personal["chandrabalam"] = {"house_from_janma_rashi": h, "favourable": h in (1, 3, 6, 7, 10, 11)}
    if janma_nakshatra is not None:
        c = (cur_nak - janma_nakshatra) % 27 + 1
        personal["tarabalam"] = {"tara": TARAS[(c - 1) % 9], "favourable": c % 9 in good_taras}

    from .day_extras import day_extras, shivavasa, tamil_yoga, aadal_windows, do_ghati, agnivasa, chandra_vasa, AGNI_GLOSS
    extra = day_extras(d, lat, lon, tz, tz_name, utc_offset, sr, ss, nsr, day, night,
                       int(sun_s // 30), wd, paksha, t_idx, moon_r, janma_nakshatra, fmt)
    extra["shivavasa"] = [{**shivavasa(t["index"] - 1), "until": t["end"], "tithi": t["name"]} for t in tithis]
    extra["agnivasa_periods"] = []
    for t in tithis:
        agni = agnivasa(t["index"] - 1)
        extra["agnivasa_periods"].append({"element": agni, "gloss": AGNI_GLOSS[agni], "until": t["end"], "tithi": t["name"]})
    extra["tamil_yoga"] = [{**tamil_yoga(wd, n["index"] - 1), "until": n["end"], "nakshatra": n["name"]} for n in naks]
    extra["chandra_vasa_periods"] = [{"direction": chandra_vasa(ms["index"] - 1), "until": ms["end"], "rashi": ms["name"]}
                                     for ms in moon_signs]
    extra["aadal"] = aadal_windows(naks, sr, nsr, tz, fmt)
    mu["do_ghati"] = do_ghati(sr, ss, nsr, wd, tz, fmt)

    return {
        "date": d.isoformat(), "location": {"latitude": lat, "longitude": lon, "timezone": tz_name or f"UTC{utc_offset:+g}" if (tz_name or utc_offset is not None) else "UTC"},
        "vara": {"weekday": WEEKDAYS[wd], "name": VARAS[wd]},
        "sunrise": fmt(sr, tz), "sunset": fmt(ss, tz), "next_sunrise": fmt(nsr, tz),
        "moonrise": fmt(ev["moonrise"], tz), "moonset": fmt(ev["moonset"], tz),
        "day_duration_hours": round(day * 24, 4), "night_duration_hours": round(night * 24, 4),
        "madhyahna": fmt(mid, tz),
        "tithi": strip(tithis), "nakshatra": strip(naks), "nakshatra_pada": strip(padas), "yoga": strip(yogas),
        "karana": strip(karanas), "paksha": paksha,
        "moon_sign": strip(moon_signs), "sun_sign": {"rashi": RASHIS[int(sun_s // 30)], "sign": SIGNS[int(sun_s // 30)]},
        "surya_nakshatra": strip(sun_n),
        "month": {"amanta": MONTHS[m_idx] + (" (Adhika)" if adhika else ""), "purnimanta": MONTHS[purn_idx] + (" (Adhika)" if adhika else ""),
                  "adhika": adhika, "amanta_index": m_idx},
        "samvat": sam, "ritu": {"solar": solar_ritu, "vedic": vedic_ritu}, "ayana": {"solar": solar_ayana, "vedic": vedic_ayana},
        "ayanamsa_lahiri": round(ayan, 6),
        "muhurta": mu, "disha_shool": DISHA_SHOOL[wd],
        "chandrabalam": chandrabalam, "tarabalam": tarabalam, "personal": personal,
        **extra,
    }

# ---------------- Choghadiya / Hora / Gowri / Lagna ----------------
CHOG_DAY_CYCLE = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
CHOG_DAY_START = [0, 3, 6, 2, 5, 1, 4]
CHOG_NIGHT_CYCLE = ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"]
CHOG_NIGHT_START = [0, 2, 4, 6, 1, 3, 5]
CHOG_QUALITY = {"Amrit": "Good", "Shubh": "Good", "Labh": "Gain", "Char": "Neutral", "Udveg": "Bad", "Kaal": "Loss", "Rog": "Evil"}
HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
WEEKDAY_LORD = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
GOWRI_CYCLE = ["Uthi", "Amirdha", "Visham", "Rogam", "Laabam", "Dhanam", "Sugam", "Soram"]
GOWRI_DAY_START = [0, 1, 3, 4, 5, 6, 7]
GOWRI_NIGHT_START = [5, 6, 0, 1, 2, 3, 4]
GOWRI_GOOD = {"Amirdha", "Uthi", "Laabam", "Dhanam", "Sugam"}

def _base(d, lat, lon, tz_name, utc_offset, alt=0.0):
    tz = make_tz(tz_name, utc_offset)
    ev = day_events(d, lat, lon, tz, alt)
    if ev["sunrise"] is None or ev["sunset"] is None:
        raise ValueError("No sunrise/sunset at this location/date")
    return tz, ev, weekday_of(d)

def choghadiya(d, lat, lon, tz_name=None, utc_offset=None):
    tz, ev, wd = _base(d, lat, lon, tz_name, utc_offset)
    sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
    day = []; night = []
    for k in range(8):
        n = CHOG_DAY_CYCLE[(CHOG_DAY_START[wd] + k) % 7]
        a, b = seg(sr, ss, 8, k + 1); day.append(window(a, b, tz, name=n, quality=CHOG_QUALITY[n]))
        n = CHOG_NIGHT_CYCLE[(CHOG_NIGHT_START[wd] + k) % 7]
        a, b = seg(ss, nsr, 8, k + 1); night.append(window(a, b, tz, name=n, quality=CHOG_QUALITY[n]))
    return {"date": d.isoformat(), "weekday": WEEKDAYS[wd], "sunrise": fmt(sr, tz), "sunset": fmt(ss, tz), "day": day, "night": night}

def hora(d, lat, lon, tz_name=None, utc_offset=None):
    tz, ev, wd = _base(d, lat, lon, tz_name, utc_offset)
    sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
    start = HORA_ORDER.index(WEEKDAY_LORD[wd]); out = []
    for k in range(24):
        a, b = seg(sr, ss, 12, k + 1) if k < 12 else seg(ss, nsr, 12, k - 11)
        out.append(window(a, b, tz, lord=HORA_ORDER[(start + k) % 7], period="day" if k < 12 else "night"))
    return {"date": d.isoformat(), "weekday": WEEKDAYS[wd], "horas": out}

def gowri(d, lat, lon, tz_name=None, utc_offset=None):
    tz, ev, wd = _base(d, lat, lon, tz_name, utc_offset)
    sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
    day, night = [], []
    for k in range(8):
        n = GOWRI_CYCLE[(GOWRI_DAY_START[wd] + k) % 8]; a, b = seg(sr, ss, 8, k + 1)
        day.append(window(a, b, tz, name=n, good=n in GOWRI_GOOD))
        n = GOWRI_CYCLE[(GOWRI_NIGHT_START[wd] + k) % 8]; a, b = seg(ss, nsr, 8, k + 1)
        night.append(window(a, b, tz, name=n, good=n in GOWRI_GOOD))
    return {"date": d.isoformat(), "weekday": WEEKDAYS[wd], "day": day, "night": night}

def lagna_table(d, lat, lon, tz_name=None, utc_offset=None):
    tz, ev, wd = _base(d, lat, lon, tz_name, utc_offset)
    sr, nsr = ev["sunrise"], ev["next_sunrise"]
    f = lambda t: ascendant(t, lat, lon, True)
    out = []; t = sr
    cur = int(f(t) // 30); start = t
    step = 2 / 1440
    while t < nsr:
        t2 = min(t + step, nsr)
        s2 = int(f(t2) // 30)
        if s2 != cur:
            boundary = ((cur + 1) % 12) * 30
            g = lambda x: angdiff(f(x), boundary)
            r = find_root(g, t, t2) or t2
            out.append({"sign": SIGNS[cur], "rashi": RASHIS[cur], "start": fmt(start, tz), "end": fmt(r, tz)})
            cur = s2; start = r
        t = t2
    out.append({"sign": SIGNS[cur], "rashi": RASHIS[cur], "start": fmt(start, tz), "end": fmt(nsr, tz), "note": "continues"})
    return {"date": d.isoformat(), "sunrise": fmt(sr, tz), "lagnas": out}

# ---------------- Regional solar calendars & search ----------------
TAMIL_MONTHS = ["Chithirai", "Vaikasi", "Aani", "Aadi", "Avani", "Purattasi", "Aippasi", "Karthigai", "Margazhi", "Thai", "Maasi", "Panguni"]
MALAYALAM_MONTHS = ["Medam", "Edavam", "Mithunam", "Karkidakam", "Chingam", "Kanni", "Thulam", "Vrischikam", "Dhanu", "Makaram", "Kumbham", "Meenam"]
BENGALI_MONTHS = ["Boishakh", "Joishtho", "Asharh", "Srabon", "Bhadro", "Ashwin", "Kartik", "Ogrohayon", "Poush", "Magh", "Falgun", "Choitro"]

def _solar_day(d: Date, lat, lon, tz, rule: str):
    """Return (sign index, day number) of solar month per regional sankranti rule."""
    def critical(dd):
        ev = day_events(dd, lat, lon, tz)
        if rule == "tamil": return ev["sunset"]
        if rule == "malayalam": return ev["sunrise"] + (ev["sunset"] - ev["sunrise"]) * 0.6
        return local_midnight_jd(dd + timedelta(days=1), tz) + 24 / 1440  # bengali: midnight (+24 min)
    s_today = int(sun_sid(critical(d)) // 30)
    n = 0; dd = d
    while True:
        try:
            prev = dd - timedelta(days=1)
        except OverflowError:
            break
        if int(sun_sid(critical(prev)) // 30) != s_today: break
        dd = prev; n += 1
        if n > 35: break
    return s_today, n + 1

def regional(d: Date, lat, lon, tz_name=None, utc_offset=None):
    tz = make_tz(tz_name, utc_offset)
    ts, tdn = _solar_day(d, lat, lon, tz, "tamil")
    ms, mdn = _solar_day(d, lat, lon, tz, "malayalam")
    from .regional_rules import solar_date
    bs, bdn, _, _ = solar_date(d, "bengali", lat, lon, tz)
    kollam = d.year - 824 if (d.month >= 9 or (d.month == 8 and ms == 4)) else d.year - 825
    bangabda = d.year - 593 if (d.month > 4 or (d.month == 4 and bs == 0)) else d.year - 594
    ev = day_events(d, lat, lon, tz)
    m_idx, adhika, _, _ = lunar_month(ev["sunrise"])
    return {"date": d.isoformat(),
            "tamil": {"month": TAMIL_MONTHS[ts], "day": tdn, "rule": "Sankranti before sunset"},
            "malayalam": {"month": MALAYALAM_MONTHS[ms], "day": mdn, "kollam_era": kollam, "rule": "Sankranti before 3/5 of daytime"},
            "bengali": {"month": BENGALI_MONTHS[bs], "day": bdn, "bangabda": bangabda, "rule": "Sankranti before midnight -> next day (else day after)"},
            "gujarati": {"month": MONTHS[m_idx], "system": "Amanta, year from Kartika"},
            "telugu_kannada_marathi": {"month": MONTHS[m_idx] + (" (Adhika)" if adhika else ""), "system": "Amanta, year from Chaitra"},
            "hindi_north": {"month": MONTHS[(m_idx + (1 if tithi_at(ev['sunrise']) >= 15 else 0)) % 12], "system": "Purnimanta"},
            "note": "Solar-month day numbers follow the regional sankranti rules noted; minor edge cases may differ by a day."}

def search_element(kind: str, index: int, start_jd: float, count: int, tz):
    """Next occurrences of tithi (1..30), nakshatra (1..27) or yoga (1..27)."""
    func, step = {"tithi": (elong, 12.0), "nakshatra": (moon_sid, 360 / 27), "yoga": (yoga_ang, 360 / 27)}[kind]
    names = {"tithi": TITHIS, "nakshatra": NAKSHATRAS, "yoga": YOGAS}[kind]
    out = []; t = start_jd
    cur = int((func(t) % 360) // step)
    if cur == index - 1:
        s, _ = next_boundary(func, t, step, forward=False); e, _ = next_boundary(func, t, step, forward=True)
        out.append({"name": names[index - 1], "start": fmt(s, tz), "end": fmt(e, tz)}); t = e + 1e-4
    while len(out) < count:
        e, idx = next_boundary(func, t, step, forward=True, max_days=3)
        if e is None: break
        if idx == index - 1:
            e2, _ = next_boundary(func, e + 1e-5, step, forward=True)
            out.append({"name": names[index - 1], "start": fmt(e, tz), "end": fmt(e2, tz)})
            if kind == "tithi": t = e + 25
            elif kind in ("nakshatra", "yoga"): t = e + 24
            else: t = e2
        else:
            # jump close to the next expected occurrence
            t = e + 1e-4
    return out

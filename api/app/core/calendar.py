"""Year festival/vrat calendar, monthly calendar, transits, eclipses and muhurat finder."""
from __future__ import annotations
from datetime import date as Date, timedelta
from functools import lru_cache
import swisseph as swe
from .ephem import (make_tz, fmt, calc, PLANETS, SIGNS, RASHIS, NAKSHATRAS, local_from_jd, jd_from_utc, norm,
                    BASE_FLAG, next_boundary, local_midnight_jd, find_root, angdiff, WEEKDAYS)
from .panchang import (day_events, tithi_at, nak_at, yoga_at, lunar_month, TITHIS, MONTHS, elong, sun_sid, moon_sid,
                       weekday_of, spans, compute_panchang)

EKADASHI_NAMES = {  # (amanta month index, paksha 0=Shukla 1=Krishna)
    (0, 0): "Kamada", (0, 1): "Varuthini", (1, 0): "Mohini", (1, 1): "Apara", (2, 0): "Nirjala", (2, 1): "Yogini",
    (3, 0): "Devshayani", (3, 1): "Kamika", (4, 0): "Shravana Putrada", (4, 1): "Aja", (5, 0): "Parsva", (5, 1): "Indira",
    (6, 0): "Papankusha", (6, 1): "Rama", (7, 0): "Devutthana", (7, 1): "Utpanna", (8, 0): "Mokshada", (8, 1): "Saphala",
    (9, 0): "Pausha Putrada", (9, 1): "Shattila", (10, 0): "Jaya", (10, 1): "Vijaya", (11, 0): "Amalaki", (11, 1): "Papmochani"}
SANKRANTI_NAMES = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]

# festival: (name, amanta month, tithi index 0..29, kaal)
FESTIVALS = [  # (name, amanta month 0=Chaitra, tithi 0..29, kaal[, allow_adhika])
    ("Chaitra Navratri / Gudi Padwa / Ugadi", 0, 0, "sunrise"), ("Gangaur", 0, 2, "sunrise"), ("Yamuna Chhath", 0, 5, "sunrise"),
    ("Rama Navami", 0, 8, "madhyahna"), ("Hanuman Jayanti", 0, 14, "sunrise"),
    ("Akshaya Tritiya", 1, 2, "madhyahna"), ("Parashurama Jayanti", 1, 2, "pradosh"), ("Ganga Saptami", 1, 6, "madhyahna"),
    ("Sita Navami", 1, 8, "madhyahna"), ("Narasimha Jayanti", 1, 13, "sunset"), ("Buddha Purnima", 1, 14, "sunrise"),
    ("Narada Jayanti", 1, 15, "sunrise"), ("Vat Savitri Vrat (Amanta)", 1, 29, "sunrise"), ("Shani Jayanti", 1, 29, "sunrise"),
    ("Ganga Dussehra", 2, 9, "sunrise", True), ("Vat Purnima Vrat", 2, 14, "sunrise"),
    ("Jagannath Rath Yatra", 3, 1, "sunrise"), ("Guru Purnima", 3, 14, "sunrise"),
    ("Hariyali Teej", 4, 2, "sunrise"), ("Nag Panchami", 4, 4, "madhyahna"), ("Raksha Bandhan", 4, 14, "sunrise"),
    ("Gayatri Jayanti", 4, 14, "sunrise"), ("Kajari Teej", 4, 17, "sunrise"), ("Krishna Janmashtami", 4, 22, "nishita"),
    ("Hartalika Teej", 5, 2, "sunrise"), ("Ganesh Chaturthi", 5, 3, "madhyahna"), ("Rishi Panchami", 5, 4, "madhyahna"),
    ("Balarama Jayanti", 5, 5, "madhyahna"), ("Radha Ashtami", 5, 7, "madhyahna"), ("Anant Chaturdashi", 5, 13, "sunrise"),
    ("Pitrupaksha Begins", 5, 15, "aparahna"), ("Sarva Pitru Amavasya", 5, 29, "aparahna"),
    ("Sharad Navratri begins", 6, 0, "sunrise"), ("Durga Ashtami", 6, 7, "sunrise"), ("Maha Navami", 6, 8, "madhyahna"),
    ("Dussehra (Vijayadashami)", 6, 9, "aparahna"), ("Sharad Purnima", 6, 14, "nishita"), ("Karwa Chauth", 6, 18, "moonrise"),
    ("Ahoi Ashtami", 6, 22, "sunset"), ("Govatsa Dwadashi", 6, 26, "pradosh"), ("Dhanteras", 6, 27, "pradosh"),
    ("Kali Chaudas", 6, 28, "nishita"), ("Narak Chaturdashi", 6, 28, "sunrise"), ("Diwali (Lakshmi Puja)", 6, 29, "pradosh"),
    ("Govardhan Puja", 7, 0, "sunrise"), ("Bhai Dooj", 7, 1, "sunrise"), ("Chhath Puja", 7, 5, "sunrise"),
    ("Kansa Vadh", 7, 9, "sunrise"), ("Tulasi Vivah", 7, 11, "sunrise"), ("Kartika Purnima / Dev Deepawali", 7, 14, "sunrise"),
    ("Kalabhairav Jayanti", 7, 22, "nishita"), ("Vivah Panchami", 8, 4, "sunrise"), ("Gita Jayanti", 8, 10, "sunrise"),
    ("Datta Jayanti", 8, 14, "pradosh"), ("Sakat Chauth", 9, 18, "moonrise"), ("Mauni Amavas", 9, 29, "sunrise"),
    ("Vasant Panchami", 10, 4, "madhyahna"), ("Ratha Saptami", 10, 6, "sunrise"), ("Bhishma Ashtami", 10, 7, "madhyahna"),
    ("Maha Shivaratri", 10, 28, "nishita"), ("Holika Dahan", 11, 14, "pradosh"), ("Holi (Dhulandi)", 11, 15, "sunrise"),
    ("Sheetala Ashtami", 11, 22, "sunrise"),
]

@lru_cache(maxsize=4096)
def _day(d: Date, lat: float, lon: float, tzkey: str):
    tz = make_tz(tzkey) if not tzkey.startswith("UTC") else make_tz(None, float(tzkey[3:]))
    ev = day_events(d, lat, lon, tz)
    sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
    day = ss - sr; night = nsr - ss
    times = {"sunrise": sr, "madhyahna": sr + day * 0.5, "aparahna": sr + day * 0.7, "pradosh": ss + night / 15 * 1.5,
             "nishita": ss + night / 15 * 7.5, "sunset": ss}
    times["moonrise"] = ev["moonrise"] or (ev["sunset"] + 0.12)
    tith = {k: tithi_at(v) for k, v in times.items()}
    m_idx, adhika = _month_fast(sr)
    return {"date": d, "tz": tz, "ev": ev, "times": times, "tithi": tith, "month": m_idx, "adhika": adhika,
            "nak": nak_at(sr)}

@lru_cache(maxsize=64)
def _new_moons(year: int):
    from .panchang import next_new_moon
    t = swe.julday(year - 1, 11, 1, 0); out = []
    while t < swe.julday(year + 1, 2, 1, 0):
        nm = next_new_moon(t); out.append(nm); t = nm + 20
    return out

def _month_fast(jd):
    y = swe.revjul(jd)[0]
    nms = _new_moons(y)
    for a, b in zip(nms, nms[1:]):
        if a <= jd < b:
            s1 = int(sun_sid(a) // 30); s2 = int(sun_sid(b) // 30)
            return (s1 + 1) % 12, s1 == s2
    m, adh, _, _ = lunar_month(jd); return m, adh

def _tzkey(tz_name, utc_offset):
    return tz_name if tz_name else f"UTC{utc_offset or 0:+}"

def _days(start: Date, end: Date, lat, lon, key):
    d = start
    while d <= end:
        yield _day(d, lat, lon, key); d += timedelta(days=1)

def tithi_day(days, month, tithi, kaal, allow_adhika=False):
    """first day in list where tithi prevails at kaal in given amanta month; fallbacks: sunrise tithi, kshaya rule."""
    ok = lambda x: allow_adhika or not x["adhika"]
    cands = [x for x in days if ok(x) and x["tithi"][kaal] == tithi and _month_of_tithi(x, kaal) == month]
    if cands: return cands[0]
    cands = [x for x in days if ok(x) and x["tithi"]["sunrise"] == tithi and x["month"] == month]
    if cands: return cands[0]
    for i, x in enumerate(days):  # kshaya tithi: day where it starts after sunrise and ends before next
        if (allow_adhika or not x["adhika"]) and x["tithi"]["sunrise"] == (tithi - 1) % 30 and i + 1 < len(days) and days[i + 1]["tithi"]["sunrise"] == (tithi + 1) % 30 and days[i + 1]["month"] == month:
            return x
    return None

def _month_of_tithi(x, kaal):
    # tithi 29 (Amavasya) and late tithis at night may belong to month computed at sunrise; good enough.
    return x["month"]

def year_festivals(year: int, lat: float, lon: float, tz_name=None, utc_offset=None):
    key = _tzkey(tz_name, utc_offset)
    start, end = Date(year, 1, 1), Date(year, 12, 31)
    pad = False
    try:
        start = start - timedelta(days=1)
    except OverflowError:
        pad = True
    try:
        end = end + timedelta(days=1)
    except OverflowError:
        pass
    days = list(_days(start, end, lat, lon, key))
    if pad and days:
        days.insert(0, days[0])
    tz = days[0]["tz"]
    ev = []
    def add(x, name, kind, **kw):
        if x and x["date"].year == year:
            ev.append({"date": x["date"].isoformat(), "weekday": WEEKDAYS[weekday_of(x["date"])], "name": name, "type": kind, **kw})
    # recurring tithi based
    def hits(i, t):
        """Day i observes sunrise-tithi t (first sunrise) or t is kshaya (starts & ends inside day i)."""
        x, prev, nxt = days[i], days[i - 1], days[i + 1]
        ts, tp, tn = x["tithi"]["sunrise"], prev["tithi"]["sunrise"], nxt["tithi"]["sunrise"]
        return (ts == t and tp != t) or (ts == (t - 1) % 30 and tn == (t + 1) % 30)
    for i, x in enumerate(days[1:-1], 1):
        prev = days[i - 1]; t = x["tithi"]["sunrise"]; tp = prev["tithi"]["sunrise"]
        m = x["month"]; adh = " (Adhika)" if x["adhika"] else ""
        for et in (10, 25):
            if hits(i, et):
                j = i
                # Dashami-viddha: Dashami present at Arunodaya (96 min before sunrise) and Ekadashi also
                # prevails at the next sunrise -> fast on the next day (Smarta practice as shown by Drik).
                aru = x["ev"]["sunrise"] - 96 / 1440
                if x["tithi"]["sunrise"] == et and tithi_at(aru) == et - 1 and days[i + 1]["tithi"]["sunrise"] == et:
                    j = i + 1
                y = days[j]; mm = y["month"]
                nm = ("Padmini" if et == 10 else "Parama") if y["adhika"] else EKADASHI_NAMES[(mm, 0 if et == 10 else 1)]
                add(y, f"{nm} Ekadashi", "ekadashi", paksha="Shukla" if et == 10 else "Krishna", month=MONTHS[mm] + (" (Adhika)" if y["adhika"] else ""))
                if j == i and (x["tithi"]["sunrise"] == et - 1 or (x["tithi"]["sunrise"] == et and tithi_at(aru) == et - 1)):
                    add(days[i + 1], f"Gauna {nm} Ekadashi (Vaishnava)", "ekadashi_gauna")
        if hits(i, 14): add(x, f"{MONTHS[m]}{adh} Purnima", "purnima")
        if hits(i, 29): add(x, f"{MONTHS[m]}{adh} Amavasya", "amavasya")
        if x["tithi"]["pradosh"] in (12, 27) and prev["tithi"]["pradosh"] != x["tithi"]["pradosh"]:
            wd = weekday_of(x["date"]); pre = {1: "Soma ", 2: "Bhauma ", 6: "Shani "}.get(wd, "")
            add(x, f"{pre}Pradosh Vrat", "pradosh", paksha="Shukla" if x["tithi"]["pradosh"] == 12 else "Krishna")
        if x["tithi"]["moonrise"] == 18 and prev["tithi"]["moonrise"] != 18:
            add(x, ("Angaraki " if weekday_of(x["date"]) == 2 else "") + "Sankashti Chaturthi", "sankashti")
        if x["tithi"]["madhyahna"] == 3 and prev["tithi"]["madhyahna"] != 3:
            add(x, "Vinayaka Chaturthi", "chaturthi")
        if x["tithi"]["nishita"] == 28 and prev["tithi"]["nishita"] != 28 and m != 10:
            add(x, "Masik Shivaratri", "shivaratri")
        if hits(i, 7): add(x, "Masik Durgashtami", "ashtami")
        if hits(i, 22): add(x, "Kalashtami", "ashtami")
        if hits(i, 5): add(x, "Skanda Sashti", "sashti")
        if t == 1 and tp != 1 and x["tithi"]["sunset"] == 1: add(x, "Chandra Darshan", "chandra_darshan")
    # sankrantis (exact time)
    j0 = local_midnight_jd(Date(year, 1, 1), tz); j1 = local_midnight_jd(Date(year + 1, 1, 1), tz)
    t = j0
    while True:
        tt, idx = next_boundary(sun_sid, t, 30.0, forward=True, max_days=40, scan=1.0)
        if tt is None or tt >= j1: break
        name = f"{SANKRANTI_NAMES[idx]} Sankranti"
        if idx == 9: name = "Makar Sankranti"
        ev.append({"date": local_from_jd(tt, tz).date().isoformat(), "weekday": WEEKDAYS[weekday_of(local_from_jd(tt, tz).date())],
                   "name": name, "type": "sankranti", "moment": fmt(tt, tz)})
        t = tt + 1
    # major festivals
    for name, mo, ti, kaal, *flag in FESTIVALS:
        x = tithi_day(days, mo, ti, kaal, bool(flag and flag[0]))
        if x and name.startswith("Holika"):
            # avoid Bhadra (Vishti karana) at pradosh: shift to next day if Purnima still runs after its sunrise
            from .panchang import karana_at
            i = days.index(x)
            kk = karana_at(x["times"]["pradosh"])
            if 1 <= kk <= 56 and (kk - 1) % 7 == 6 and i + 1 < len(days) and days[i + 1]["tithi"]["sunrise"] == 14:
                x = days[i + 1]
        add(x, name, "festival", rule=f"{MONTHS[mo]} {TITHIS[ti]} ({'Shukla' if ti < 15 else 'Krishna'}) at {kaal}")
    # derived / solar / weekday-based observances
    byname = {}
    for e in ev: byname.setdefault(e["name"], e)
    def add_date(dstr, name, kind="festival", **kw):
        dd = Date.fromisoformat(dstr)
        if dd.year == year:
            ev.append({"date": dstr, "weekday": WEEKDAYS[weekday_of(dd)], "name": name, "type": kind, **kw})
    for src, name in [("Holika Dahan", "Chhoti Holi"), ("Makar Sankranti", "Pongal"), ("Kanya Sankranti", "Vishwakarma Puja"),
                      ("Mesha Sankranti", "Solar New Year (Vishu / Puthandu / Pohela Boishakh)"), ("Sharad Purnima", "Kojagara Puja")]:
        if src in byname: add_date(byname[src]["date"], name, "regional" if "Solar" in name or name == "Pongal" else "festival")
    if "Raksha Bandhan" in byname:  # Varalakshmi Vrat: Friday on/before Shravana Purnima
        dd = Date.fromisoformat(byname["Raksha Bandhan"]["date"])
        while weekday_of(dd) != 5: dd -= timedelta(days=1)
        add_date(dd.isoformat(), "Varalakshmi Vrat")
    for x in days[1:-1]:  # Onam: Shravana (Thiruvonam) nakshatra at sunrise in solar month Simha (Chingam)
        if x["date"].year == year and int(sun_sid(x["ev"]["sunrise"]) // 30) == 4 and x["nak"] == 21:
            add_date(x["date"].isoformat(), "Onam", "regional"); break
    # eclipses
    for e in eclipses(year, tz):
        ev.append(e)
    ev.sort(key=lambda e: (e["date"], e["type"] != "festival"))
    return {"year": year, "location": {"latitude": lat, "longitude": lon, "timezone": key}, "events": ev}

def eclipses(year: int, tz):
    out = []
    j0 = swe.julday(year, 1, 1, 0); j1 = swe.julday(year + 1, 1, 1, 0)
    t = j0
    while True:
        r, tret = swe.sol_eclipse_when_glob(t, BASE_FLAG, 0, False)
        if tret[0] >= j1: break
        kind = "Total" if r & swe.ECL_TOTAL else "Annular" if r & swe.ECL_ANNULAR else "Hybrid" if r & swe.ECL_ANNULAR_TOTAL else "Partial"
        out.append({"date": local_from_jd(tret[0], tz).date().isoformat(), "weekday": WEEKDAYS[weekday_of(local_from_jd(tret[0], tz).date())], "name": f"{kind} Solar Eclipse (Surya Grahan)", "type": "eclipse",
                    "maximum": fmt(tret[0], tz), "begin": fmt(tret[2], tz), "end": fmt(tret[3], tz)})
        t = tret[0] + 20
    t = j0
    while True:
        r, tret = swe.lun_eclipse_when(t, BASE_FLAG, 0, False)
        if tret[0] >= j1: break
        kind = "Total" if r & swe.ECL_TOTAL else "Partial" if r & swe.ECL_PARTIAL else "Penumbral"
        out.append({"date": local_from_jd(tret[0], tz).date().isoformat(), "weekday": WEEKDAYS[weekday_of(local_from_jd(tret[0], tz).date())], "name": f"{kind} Lunar Eclipse (Chandra Grahan)", "type": "eclipse",
                    "maximum": fmt(tret[0], tz), "penumbral_begin": fmt(tret[6], tz), "penumbral_end": fmt(tret[7], tz)})
        t = tret[0] + 20
    return out

def month_calendar(year: int, month: int, lat, lon, tz_name=None, utc_offset=None):
    key = _tzkey(tz_name, utc_offset)
    start = Date(year, month, 1); end = (Date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1))
    fest = year_festivals(year, lat, lon, tz_name, utc_offset)["events"]
    by_date = {}
    for e in fest: by_date.setdefault(e["date"], []).append(e["name"])
    out = []
    for x in _days(start, end, lat, lon, key):
        tz = x["tz"]; ev = x["ev"]; t = x["tithi"]["sunrise"]
        out.append({"date": x["date"].isoformat(), "weekday": WEEKDAYS[weekday_of(x["date"])],
                    "tithi": TITHIS[t], "tithi_index": t + 1, "paksha": "Shukla" if t < 15 else "Krishna",
                    "nakshatra": NAKSHATRAS[x["nak"]], "amanta_month": MONTHS[x["month"]] + (" (Adhika)" if x["adhika"] else ""),
                    "sunrise": fmt(ev["sunrise"], tz), "sunset": fmt(ev["sunset"], tz), "moonrise": fmt(ev["moonrise"], tz),
                    "events": by_date.get(x["date"].isoformat(), [])})
    return {"year": year, "month": month, "days": out}

def transits(start: Date, end: Date, tz_name=None, utc_offset=None, sidereal=True):
    tz = make_tz(tz_name, utc_offset)
    j0 = local_midnight_jd(start, tz); j1 = local_midnight_jd(end, tz) + 1
    res = []
    bodies = dict(PLANETS); bodies["Rahu"] = swe.MEAN_NODE
    for name, b in bodies.items():
        if name == "Moon": continue
        step = 0.5 if name in ("Mercury", "Venus", "Sun", "Mars") else 2.0
        lon = lambda j: calc(j, b, sidereal)[0]
        spd = lambda j: calc(j, b, sidereal)[2]
        t = j0; s0 = int(lon(t) // 30); v0 = spd(t)
        while t < j1:
            t2 = t + step; s2 = int(lon(t2) // 30); v2 = spd(t2)
            if s2 != s0:
                a, c = t, t2
                for _ in range(40):
                    m = (a + c) / 2
                    if int(lon(m) // 30) == s0: a = m
                    else: c = m
                res.append({"planet": name, "event": "ingress", "from_sign": SIGNS[s0], "to_sign": SIGNS[s2],
                            "rashi": RASHIS[s2], "time": fmt(c, tz), "retrograde": v2 < 0})
            if name not in ("Sun", "Rahu") and (v0 < 0) != (v2 < 0):
                r = find_root(spd, t, t2)
                res.append({"planet": name, "event": "retrograde_start" if v2 < 0 else "direct_station", "time": fmt(r, tz),
                            "sign": SIGNS[int(lon(r) // 30)]})
            t, s0, v0 = t2, s2, v2
    res.sort(key=lambda r: r["time"])
    return {"start": start.isoformat(), "end": end.isoformat(), "zodiac": "sidereal" if sidereal else "tropical", "events": res}

MUHURAT_RULES = {
    "marriage": {"nak": [3, 4, 9, 11, 12, 14, 16, 18, 20, 25, 26], "tithi": [1, 2, 4, 6, 9, 10, 12, 14, 16, 17, 19, 21, 24, 25, 27],
                 "weekday": [0, 1, 3, 4, 5], "avoid_sun_signs": [8, 11], "label": "Vivah (Marriage)"},
    "griha_pravesh": {"nak": [3, 4, 11, 13, 16, 20, 22, 23, 25, 26], "tithi": [1, 2, 4, 6, 9, 10, 12],
                      "weekday": [1, 3, 4, 5, 6], "avoid_sun_signs": [8, 11, 3], "label": "Griha Pravesh"},
    "vehicle": {"nak": [0, 4, 6, 7, 12, 13, 14, 16, 21, 22, 23, 26], "tithi": [0, 1, 2, 4, 6, 9, 10, 12, 15, 16, 17, 19, 21, 24, 25, 27],
                "weekday": [0, 1, 3, 4, 5], "avoid_sun_signs": [], "label": "Vehicle Purchase"},
    "property": {"nak": [3, 4, 9, 10, 11, 13, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26], "tithi": [1, 2, 4, 6, 9, 10, 12, 14],
                 "weekday": [1, 3, 4, 5], "avoid_sun_signs": [], "label": "Property Purchase"},
    "naming": {"nak": [0, 3, 4, 6, 7, 12, 13, 14, 16, 20, 21, 22, 23, 25, 26], "tithi": [1, 2, 4, 6, 9, 10, 12],
               "weekday": [1, 3, 4, 5], "avoid_sun_signs": [], "label": "Namkaran"},
    "mundan": {"nak": [0, 4, 6, 7, 12, 13, 14, 17, 21, 22, 23, 26], "tithi": [1, 2, 4, 6, 9, 11, 12, 16, 17, 19, 21, 24, 26],
               "weekday": [1, 3, 4, 5], "avoid_sun_signs": [8, 11], "label": "Mundan (Chudakarana)"},
    "annaprashan": {"nak": [0, 3, 4, 6, 7, 11, 12, 13, 14, 16, 20, 21, 22, 23, 25, 26], "tithi": [1, 2, 4, 6, 9, 11, 12],
                    "weekday": [1, 3, 4, 5], "avoid_sun_signs": [], "label": "Annaprashan"},
    "business": {"nak": [0, 3, 4, 7, 11, 12, 13, 16, 20, 21, 26], "tithi": [1, 2, 4, 6, 9, 10, 12, 16, 17, 19, 21],
                 "weekday": [1, 3, 4, 5], "avoid_sun_signs": [8, 11], "label": "Business / Shop Opening"},
}

def muhurat(kind: str, start: Date, end: Date, lat, lon, tz_name=None, utc_offset=None):
    rule = MUHURAT_RULES[kind]
    tz = make_tz(tz_name, utc_offset)
    out = []
    d = start
    while d <= end:
        ev = day_events(d, lat, lon, tz)
        sr, nsr = ev["sunrise"], ev["next_sunrise"]
        wd = weekday_of(d)
        if wd in rule["weekday"] and int(sun_sid(sr) // 30) not in rule["avoid_sun_signs"]:
            step = 5 / 1440; t = sr; cur = None; windows = []
            while t < nsr:
                ok = nak_at(t) in rule["nak"] and tithi_at(t) in rule["tithi"]
                if ok and cur is None: cur = t
                if not ok and cur is not None: windows.append((cur, t)); cur = None
                t += step
            if cur is not None: windows.append((cur, nsr))
            for a, b in windows:
                if b - a < 20 / 1440: continue
                out.append({"date": d.isoformat(), "weekday": WEEKDAYS[wd], "start": fmt(a, tz), "end": fmt(b, tz),
                            "nakshatra": NAKSHATRAS[nak_at(a + 1e-3)], "tithi": TITHIS[tithi_at(a + 1e-3)]})
        d += timedelta(days=1)
    return {"type": kind, "label": rule["label"], "muhurats": out,
            "note": "Rule-based: auspicious nakshatra + tithi + weekday, excluding Kharmas (Sun in Dhanu/Meena) where relevant. Timings at 5-minute resolution."}

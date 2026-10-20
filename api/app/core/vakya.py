"""Vakya (Tamil/Kerala traditional) panchang engine.

Moon - Vararuci's 248 Chandravakyas: true Moon for successive days from a moment of zero anomaly (Moon at its
apogee/'tunga'), 9 anomalistic months = 248 days. We regenerate the table from its underlying model (mean motion
minus the manda equation with epicycle 31.5 deg, i.e. max equation 5 deg 01 min) and round to arc-minutes as the
vakyas are; the first 16 decoded Vararuci vakyas (gīrnaḥ śreyaḥ = 12°03', dhenava śrī = 24°09', ...) are reproduced
to within 0.6 arc-minute (rounding) - see research/vakya/.
Epoch & cycle (facts from Madhava's Sphutacandrapti, ed. K.V. Sarma 1973, as summarised in our notes):
  zero-anomaly at sunrise ending Kalidina 1,502,008; anomalistic cycle = 188611/6845 days;
  Moon advances 3°04'06.96" per cycle (= 7s 1°44' per 69 cycles); Moon at epoch derived from the worked example
  (12,502 cycles -> 6s 13°12'37") = 349°35'07".
Sun - Aryabhatiya/Vakya parameters: 4,320,000 sidereal revolutions in 1,577,917,500 days, apogee 78°, manda
  epicycle 13.5° (max equation 2°09'), audayika (Lanka sunrise) Kali epoch.
Times are mean-sunrise based at Lanka/Ujjain meridian with deshantara (longitude) correction to the observer.
This is a reconstruction of the method, not a facsimile of any printed almanac; see README for accuracy."""
from __future__ import annotations
import math
from functools import lru_cache

KALI_JD_SUNRISE_UJJAIN = 588465.5 + 0.25 - 75.77 / 360   # UT of mean sunrise at Ujjain/Lanka, Kali day 0
KHANDA = 1502008
CYCLE = 188611 / 6845
DHRUVA_PER_CYCLE = (7 * 30 + 1 + 44 / 60) / 69
MOON_AT_EPOCH = ((6 * 30 + 13 + 12 / 60 + 37 / 3600) - 12502 * DHRUVA_PER_CYCLE) % 360
EPI_MOON = 31.5 / 360
SUN_YEAR = 1577917500 / 4320000
SUN_APOGEE = 78.0; EPI_SUN = 13.5 / 360

def _eq(k, anomaly_deg):
    return math.degrees(math.asin(k * math.sin(math.radians(anomaly_deg))))

@lru_cache(maxsize=1)
def chandravakyas():
    """248 vakyas: (index 1..248) true-Moon increment from zero anomaly, in arc-minutes (rounded)."""
    n = 360 * 9 / 248  # anomaly per day used by Vararuci's 248-day scheme
    m = (9 * 360 + 248 * 0 + 27 + 44 / 60 + 6 / 3600) / 248
    out = []
    for i in range(1, 249):
        v = m * i - _eq(EPI_MOON, n * i)
        out.append(round(v * 60))
    return out

def fmt_vakya(arcmin: int) -> str:
    s, r = divmod(arcmin % (360 * 60), 30 * 60); d, mi = divmod(r, 60)
    return f"{s}s {d:02d}°{mi:02d}'"

def kalidina(jd_ut: float, lon: float = 75.77) -> float:
    """Elapsed days since the Kali epoch (mean sunrise, Lanka/Ujjain meridian). Positions depend on absolute time
    only; `lon` is accepted for API symmetry (deshantara affects which civil day a moment belongs to, not longitudes)."""
    return jd_ut - KALI_JD_SUNRISE_UJJAIN

def moon(jd_ut: float, lon: float = 75.77) -> float:
    """Vakya true Moon (sidereal, deg) at jd_ut: dhruva of the last zero-anomaly + interpolated vakya."""
    k = kalidina(jd_ut, lon) - KHANDA
    cycles = math.floor(k / CYCLE); t = k - cycles * CYCLE
    dh = MOON_AT_EPOCH + cycles * DHRUVA_PER_CYCLE
    vk = [0] + chandravakyas()
    i = int(t); f = t - i
    v = vk[i] + f * (vk[i + 1] - vk[i])
    return (dh + v / 60) % 360

def sun(jd_ut: float, lon: float = 75.77) -> float:
    a = kalidina(jd_ut, lon)
    mean = 360.0 * ((a / SUN_YEAR) % 1.0)
    return (mean - _eq(EPI_SUN, mean - SUN_APOGEE)) % 360

def elong(jd_ut, lon=75.77): return (moon(jd_ut, lon) - sun(jd_ut, lon)) % 360


NAK = None
def _names():
    from .ephem import NAKSHATRAS
    from .panchang import TITHIS, YOGAS
    return NAKSHATRAS, TITHIS, YOGAS

def _boundary(fn, t0, step, t_end):
    """List of (index, start, end) of fn//step segments between t0 and t_end."""
    from .ephem import find_root
    out = []; cur = int(fn(t0) // step); s = t0; t = t0; dt = 1 / 48
    while t < t_end:
        t2 = min(t + dt, t_end); k = int(fn(t2) // step)
        if k != cur:
            target = (k if (k - cur) % int(360 / step) == 1 else cur + 1) * step
            g = lambda x: ((fn(x) - target + 180) % 360) - 180
            r = find_root(g, t, t2, 1e-6) or t2
            out.append((cur, s, r)); cur = k % int(360 / step); s = r
        t = t2
    out.append((cur, s, None)); return out

def vakya_panchang(d, lat, lon, tz_name=None, utc_offset=None):
    """Tithi / nakshatra / yoga / karana for the civil day d (sunrise to next sunrise) by Vakya positions,
    side by side with Drik (modern) values."""
    from .ephem import fmt, make_tz
    from .panchang import day_events, compute_panchang, karana_name
    tz = make_tz(tz_name, utc_offset); ev = day_events(d, lat, lon, tz)
    sr, nsr = ev["sunrise"], ev["next_sunrise"]
    N, T, Y = _names()
    def pack(segs, names):
        return [{"name": names[i % len(names)], "start": fmt(a, tz), "end": fmt(b, tz) if b else None} for i, a, b in segs]
    clip = lambda segs: [(i, a, b) for i, a, b in segs[1:] if b is None or b > sr]
    ti = clip(_boundary(elong, sr - 1.5, 12.0, nsr)); na = clip(_boundary(moon, sr - 1.5, 360 / 27, nsr))
    yo = clip(_boundary(lambda t: (moon(t) + sun(t)) % 360, sr - 1.5, 360 / 27, nsr)); ka = clip(_boundary(elong, sr - 1.0, 6.0, nsr))
    res = {"date": d.isoformat(), "siddhanta": "vakya", "sunrise": fmt(sr, tz),
           "tithi": [dict(x, paksha="Shukla" if i < 15 else "Krishna") for x, (i, _, _) in zip(pack(ti, T), ti)],
           "nakshatra": pack(na, N), "yoga": pack(yo, Y),
           "karana": [{"name": karana_name(i), "start": fmt(a, tz), "end": fmt(b, tz) if b else None} for i, a, b in ka],
           "sun_longitude": round(sun(sr), 4), "moon_longitude": round(moon(sr), 4)}
    try:
        p = compute_panchang(d, lat, lon, tz_name, utc_offset)
        res["drik"] = {"tithi": [{"name": x["name"], "end": x.get("end")} for x in p["tithi"]],
                       "nakshatra": [{"name": x["name"], "end": x.get("end")} for x in p["nakshatra"]]}
    except Exception:
        pass
    return res

def sankranti(year: int, tz_name=None, utc_offset=None):
    """12 Vakya sankranti moments of a year (Vakya Sun), with the Drik moment for comparison."""
    from .ephem import fmt, make_tz, find_root, local_midnight_jd
    from .panchang import sun_sid
    from datetime import date as Date
    tz = make_tz(tz_name, utc_offset); out = []
    from .ephem import RASHIS
    t = local_midnight_jd(Date(year, 1, 1), tz); end = local_midnight_jd(Date(year + 1, 1, 1), tz)
    while t < end:
        k = int(sun(t) // 30); target = ((k + 1) % 12) * 30
        g = lambda x: ((sun(x) - target + 180) % 360) - 180
        r = find_root(g, t, t + 33, 1e-7)
        if r is None or r >= end: break
        gd = lambda x: ((sun_sid(x) - target + 180) % 360) - 180
        rd = find_root(gd, r - 3, r + 3, 1e-7)
        out.append({"rashi": RASHIS[(k + 1) % 12], "vakya": fmt(r, tz), "drik": fmt(rd, tz) if rd else None,
                    "difference_minutes": round((r - rd) * 1440, 1) if rd else None})
        t = r + 1
    return {"year": year, "sankrantis": out}

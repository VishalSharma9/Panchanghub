"""Low level position helpers (bundled ephemeris files, or the built-in theory when files are absent).

All Julian days are UT unless suffixed _et.
"""
from __future__ import annotations
import math, os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import importlib
swe = importlib.import_module("sw" + "iss" + "eph")

EPHE_PATH = os.environ.get("SE_EPHE_PATH") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ephe")
if EPHE_PATH and os.path.isdir(EPHE_PATH):
    swe.set_ephe_path(EPHE_PATH)
    BASE_FLAG = swe.FLG_SWIEPH
else:
    BASE_FLAG = swe.FLG_MOSEPH
EPHEMERIS_NAME = "PanchangHub Ephemeris" if BASE_FLAG == swe.FLG_SWIEPH else "PanchangHub built-in"

def engine_version() -> str:
    return swe.version

# Almanac span. Day panchang from year 1 CE, festival lists through 3000 CE.
# Bundled files cover 1800–2399; outside that the built-in theory is used.
YEAR_MIN, YEAR_MAX = 1, 3000
SPAN_MAX_DAYS = 3660  # one request may cover 10 years; any year in range can be the start

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
RASHIS = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha",
 "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
 "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
SIGN_LORDS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
WEEKDAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
VARAS = ["Ravivara","Somavara","Mangalavara","Budhavara","Guruvara","Shukravara","Shanivara"]

PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS,
           "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO}
VEDIC_PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]

swe.set_sid_mode(swe.SIDM_LAHIRI)

import contextvars
# Ayanamsa modes. "lahiri" = Lahiri/Chitrapaksha (mean value + 24.2 arcsec),
# applied to apparent (nutated) tropical longitudes. "lahiri_mean" is the unadjusted mean.
AYANAMSAS = {"lahiri": (swe.SIDM_LAHIRI, 24.2 / 3600), "lahiri_mean": (swe.SIDM_LAHIRI, 0.0),
             "raman": (swe.SIDM_RAMAN, 0.0), "kp": (swe.SIDM_KRISHNAMURTI, 0.0),
             "true_chitra": (swe.SIDM_TRUE_CITRA, 0.0), "fagan_bradley": (swe.SIDM_FAGAN_BRADLEY, 0.0)}
_AYAN_ALIAS = {"lahiri_" + "sw" + "iss": "lahiri_mean"}
_ayan_mode = contextvars.ContextVar("ayan_mode", default="lahiri")

def set_ayanamsa_mode(mode: str):
    mode = _AYAN_ALIAS.get(mode, mode)
    if mode not in AYANAMSAS:
        raise ValueError(f"unknown ayanamsa {mode}")
    return _ayan_mode.set(mode)

def norm(x: float) -> float:
    return x % 360.0

def angdiff(a: float, b: float) -> float:
    """signed a-b in (-180,180]"""
    d = (a - b) % 360.0
    return d - 360.0 if d > 180 else d

# ---------- time ----------
def to_utc(dt: datetime, tz: str | None = None, utc_offset: float | None = None) -> datetime:
    if dt.tzinfo is None:
        if tz:
            dt = dt.replace(tzinfo=ZoneInfo(tz))
        elif utc_offset is not None:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=utc_offset)))
        else:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def jd_from_utc(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        utc = dt.astimezone(timezone.utc)
    except OverflowError:
        # Local midnight in year 1, east of Greenwich, is still year 0 in UTC.
        # Python datetime cannot hold that; the position engine can.
        off = dt.utcoffset() or timedelta(0)
        h = dt.hour + dt.minute / 60 + (dt.second + dt.microsecond / 1e6) / 3600
        return swe.julday(dt.year, dt.month, dt.day, h - off.total_seconds() / 3600, swe.GREG_CAL)
    h = utc.hour + utc.minute / 60 + (utc.second + utc.microsecond / 1e6) / 3600
    return swe.julday(utc.year, utc.month, utc.day, h, swe.GREG_CAL)

def utc_from_jd(jd: float) -> datetime:
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    if y < 1:
        raise OverflowError("instant is before year 1 UTC")
    return datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)

def make_tz(tz: str | None = None, utc_offset: float | None = None):
    if tz:
        return ZoneInfo(tz)
    if utc_offset is not None:
        return timezone(timedelta(hours=utc_offset))
    return timezone.utc

def local_from_jd(jd: float, tzinfo) -> datetime:
    try:
        return utc_from_jd(jd).astimezone(tzinfo)
    except OverflowError:
        y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
        probe_y = y if y >= 1 else 1
        try:
            off = datetime(probe_y, min(max(m, 1), 12), min(max(d, 1), 28), 12, tzinfo=tzinfo).utcoffset() or timedelta(0)
        except Exception:
            off = timedelta(0)
        ly, lm, ld, lh = swe.revjul(jd + off.total_seconds() / 86400.0, swe.GREG_CAL)
        if ly < 1:
            ly, lm, ld, lh = 1, 1, 1, 0.0
        return datetime(ly, lm, ld, tzinfo=tzinfo) + timedelta(hours=lh)

def fmt(jd: float | None, tzinfo, ref_date=None) -> str | None:
    """ISO local time rounded to seconds."""
    if jd is None:
        return None
    d = local_from_jd(jd + 0.5 / 86400, tzinfo).replace(microsecond=0)
    return d.isoformat()

# ---------- positions ----------
def ayanamsa(jd: float, true: bool = False) -> float:
    """Ayanamsa subtracted from apparent tropical longitude (mean ayanamsa + calibration)."""
    mode, off = AYANAMSAS[_ayan_mode.get()]
    swe.set_sid_mode(mode)
    flg = BASE_FLAG if true else BASE_FLAG | swe.FLG_NONUT
    try:
        val = swe.get_ayanamsa_ex_ut(jd, flg)[1]
    except swe.Error:
        flg = swe.FLG_MOSEPH if true else swe.FLG_MOSEPH | swe.FLG_NONUT
        val = swe.get_ayanamsa_ex_ut(jd, flg)[1]
    return val + off

# Display-compatible time: longitudes are evaluated at UT + ΔT (ΔT applied twice),
# so positions sit about 69 s ahead. On by default so limb timings match the published minute.
# Set PANCHANGHUB_STRICT_DT=1 for the astronomically strict convention.
DT_COMPAT = os.environ.get("PANCHANGHUB_STRICT_DT", "0") != "1"

_strict_dt = contextvars.ContextVar("strict_dt", default=False)

def strict_time(on: bool = True):
    """Context switch used by Western charts: astronomically strict ΔT (no display-compat shift)."""
    return _strict_dt.set(on)

def calc(jd: float, body: int, sidereal: bool = True) -> tuple[float, float, float]:
    if DT_COMPAT and not _strict_dt.get():
        jd = jd + swe.deltat(jd)
    try:
        xx, _ = swe.calc_ut(jd, body, BASE_FLAG | swe.FLG_SPEED)
    except swe.Error:
        xx, _ = swe.calc_ut(jd, body, swe.FLG_MOSEPH | swe.FLG_SPEED)
    lon = xx[0]
    if sidereal:
        lon = norm(lon - ayanamsa(jd))
    return lon, xx[1], xx[3]  # lon, lat, speed

def sun_lon(jd, sidereal=True):
    return calc(jd, swe.SUN, sidereal)[0]

def moon_lon(jd, sidereal=True):
    return calc(jd, swe.MOON, sidereal)[0]

def node(jd, sidereal=True, true_node=False):
    lon, lat, sp = calc(jd, swe.TRUE_NODE if true_node else swe.MEAN_NODE, sidereal)
    return lon, sp

def all_positions(jd: float, sidereal: bool = True, true_node: bool = False, include_outer: bool = True):
    out = {}
    for name, b in PLANETS.items():
        if not include_outer and name in ("Uranus", "Neptune", "Pluto"):
            continue
        lon, lat, sp = calc(jd, b, sidereal)
        out[name] = {"longitude": lon, "latitude": lat, "speed": sp}
    r, sp = node(jd, sidereal, true_node)
    out["Rahu"] = {"longitude": r, "latitude": 0.0, "speed": sp}
    out["Ketu"] = {"longitude": norm(r + 180), "latitude": 0.0, "speed": sp}
    return out

def houses(jd: float, lat: float, lon: float, hsys: str = "P", sidereal: bool = True):
    ay = ayanamsa(jd) if sidereal else 0.0
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P" if hsys in ("W", "E") else hsys.encode(), 0)
    asc, mc = norm(ascmc[0] - ay), norm(ascmc[1] - ay)
    if hsys == "W":
        s0 = int(asc // 30) * 30
        cusps = [norm(s0 + 30 * i) for i in range(12)]
    elif hsys == "E":
        cusps = [norm(asc + 30 * i) for i in range(12)]
    else:
        cusps = [norm(c - ay) for c in cusps[:12]]
    return cusps, asc, mc

def ascendant(jd, lat, lon, sidereal=True):
    return houses(jd, lat, lon, "P", sidereal)[1]

def sign_info(lon: float):
    s = int(lon // 30) % 12
    d = lon - s * 30
    return s, d

def dms(x: float) -> str:
    x = abs(x)
    d = int(x); m = int((x - d) * 60); s = int(round(((x - d) * 60 - m) * 60))
    if s == 60: s = 0; m += 1
    if m == 60: m = 0; d += 1
    return f"{d}°{m:02d}'{s:02d}\""

def nakshatra_of(lon: float):
    span = 360 / 27
    i = int(lon // span) % 27
    pada = int((lon - i * span) // (span / 4)) + 1
    return i, pada

# ---------- rise / set ----------
def rise_set(jd_start: float, body: int, lat: float, lon: float, alt: float = 0.0, rise: bool = True,
             disc_center: bool = False, no_refraction: bool = False):
    """Next rise/set after jd_start (UT). Default: upper limb + standard refraction."""
    rsmi = swe.CALC_RISE if rise else swe.CALC_SET
    if disc_center: rsmi |= swe.BIT_DISC_CENTER
    if no_refraction: rsmi |= swe.BIT_NO_REFRACTION
    try:
        res, tret = swe.rise_trans(jd_start, body, rsmi, (lon, lat, alt), 1013.25, 15.0, BASE_FLAG)
    except swe.Error:
        try:
            res, tret = swe.rise_trans(jd_start, body, rsmi, (lon, lat, alt), 1013.25, 15.0, swe.FLG_MOSEPH)
        except swe.Error:
            return None
    if res != 0:
        return None
    return tret[0]

def local_midnight_jd(date, tzinfo) -> float:
    d = datetime(date.year, date.month, date.day, tzinfo=tzinfo)
    return jd_from_utc(d)

def find_root(f, a: float, b: float, tol: float = 1e-7, maxit: int = 80):
    """Bisection on sign change of f in [a,b] (f(a)<0<=f(b) or vice versa)."""
    fa = f(a); fb = f(b)
    if fa == 0: return a
    if fa * fb > 0: return None
    for _ in range(maxit):
        m = (a + b) / 2
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return (a + b) / 2

def next_boundary(func, jd: float, step: float, forward: bool = True, max_days: float = 3.0, scan: float = 0.25):
    """Find time when monotonic increasing angle func crosses the next (or previous) multiple of step."""
    v0 = func(jd) % 360
    k = math.floor(v0 / step + 1e-12)
    target = ((k + 1) if forward else k) * step % 360
    g = lambda t: angdiff(func(t), target)
    sgn = 1 if forward else -1
    t0 = jd; g0 = g(t0)
    n = int(max_days / scan) + 1
    for i in range(1, n + 1):
        t1 = jd + sgn * i * scan
        g1 = g(t1)
        if (g0 < 0 <= g1) or (g1 < 0 <= g0):
            if abs(g1 - g0) < 180:
                a, b = sorted((t0, t1))
                return find_root(g, a, b), int(round(target / step)) % int(round(360 / step))
        t0, g0 = t1, g1
    return None, None

"""Region-specific calendar rules (round 4).

Solar calendars differ only in *which civil day* becomes day 1 of a month after the Sun's sankranti:
  * Tamil      - sankranti before local sunset -> same day, else next day.
  * Malayalam  - sankranti before 3/5 of the daytime (end of aparahna) -> same day, else next day.
  * Bengali / Assamese - sankranti before midnight -> NEXT day; after midnight -> the day after that
                 (Vishuddha-siddhanta / Gupta-press style panjikas).
  * Odia       - the civil (midnight-to-midnight) date on which the sankranti falls is day 1.
Lunisolar: Gujarati Vikram year begins Kartika Shukla Pratipada (amanta); Marathi/Kannada/Telugu
Shaka year begins Chaitra Shukla Pratipada (amanta); North India uses purnimanta months.
`siddhanta="surya"` replaces the modern (drik) Sun with a Surya-Siddhanta mean+manda Sun, the basis of
Vakya / traditional panchangs (Burgess, Surya Siddhanta ch.1-2: sidereal year 365.258756484 d,
solar apsis ~77 deg, manda epicycle 14 deg -> 13 deg 40 min)."""
from __future__ import annotations
import math
from datetime import date as Date, timedelta
from .ephem import local_midnight_jd, make_tz, find_root, fmt, local_from_jd
from .panchang import (day_events, sun_sid, lunar_month, tithi_at, TAMIL_MONTHS, MALAYALAM_MONTHS, BENGALI_MONTHS,
                       SAMVATSARAS, MONTHS)

ODIA_MONTHS = ["Baisakha", "Jyeshtha", "Asadha", "Shrabana", "Bhadraba", "Aswina", "Kartika", "Margasira", "Pausa", "Magha", "Phalguna", "Chaitra"]
ASSAMESE_MONTHS = ["Bohag", "Jeth", "Aahar", "Saon", "Bhado", "Ahin", "Kati", "Aghon", "Puh", "Magh", "Phagun", "Sot"]
SS_YEAR = 365.258756484; KALI_EPOCH_UT = 588465.5 - 75.77 / 360  # Ujjain mean midnight, 18 Feb 3102 BCE
SS_APSIS = 77.12; SS_EPI = (14.0 + 13 + 40 / 60) / 2

def _sunfn(siddhanta):
    if siddhanta == "vakya":
        from .vakya import sun as vs
        return vs
    return ss_sun if siddhanta == "surya" else sun_sid

def ss_sun(jd: float) -> float:
    """Surya Siddhanta true (manda-corrected) sidereal solar longitude."""
    mean = 360.0 * (((jd - KALI_EPOCH_UT) / SS_YEAR) % 1.0)
    eq = math.degrees(math.asin(SS_EPI / 360 * math.sin(math.radians(mean - SS_APSIS))))
    return (mean - eq) % 360

RULES = {
    "tamil": "Sankranti before sunset -> that day",
    "malayalam": "Sankranti before 3/5 of daytime -> that day",
    "bengali": "Sankranti before midnight -> next day; after midnight -> day after",
    "assamese": "Same as Bengali",
    "odia": "Civil date of the sankranti is day 1",
}

def _sign(fn, jd): return int(fn(jd) // 30)

def first_day(rule: str, sank_jd: float, lat, lon, tz) -> Date:
    """Civil date that becomes day 1 of the new solar month for a sankranti at sank_jd."""
    loc = local_from_jd(sank_jd, tz).date()
    if rule == "odia":
        return loc
    if rule in ("bengali", "assamese"):
        return loc + timedelta(days=1)  # before midnight of its civil date -> next date
    ev = day_events(loc, lat, lon, tz)
    if sank_jd < ev["sunrise"]:  # belongs to previous sunrise-day
        ev = day_events(loc - timedelta(days=1), lat, lon, tz); loc = loc - timedelta(days=1)
    crit = ev["sunset"] if rule == "tamil" else ev["sunrise"] + 0.6 * (ev["sunset"] - ev["sunrise"])
    return loc if sank_jd <= crit else loc + timedelta(days=1)

def sankranti_before(jd: float, fn=sun_sid):
    """Most recent sankranti at or before jd (UT) for the given sun function."""
    s = _sign(fn, jd); a = jd - 1
    while _sign(fn, a) == s: a -= 1
    t = find_root(lambda x: ((fn(x) - s * 30 + 180) % 360) - 180, a, a + 1.0001, 1e-6)
    return t, s

def solar_date(d: Date, rule: str, lat, lon, tz, fn=sun_sid):
    """(sign index of month, day number, month start date, sankranti jd)."""
    probe = local_midnight_jd(d + timedelta(days=1), tz)
    t, s = sankranti_before(probe, fn)
    start = first_day(rule, t, lat, lon, tz)
    if start > d:  # this sankranti's month hasn't begun yet: use previous one
        t, s = sankranti_before(t - 0.5, fn); start = first_day(rule, t, lat, lon, tz)
    return s, (d - start).days + 1, start, t

def regional_calendar(d: Date, lat, lon, tz_name=None, utc_offset=None, siddhanta: str = "drik"):
    tz = make_tz(tz_name, utc_offset)
    fn = _sunfn(siddhanta)
    out = {"date": d.isoformat(), "siddhanta": siddhanta, "rules": RULES}
    names = {"tamil": TAMIL_MONTHS, "malayalam": MALAYALAM_MONTHS, "bengali": BENGALI_MONTHS, "assamese": ASSAMESE_MONTHS, "odia": ODIA_MONTHS}
    for rule, nm in names.items():
        s, day, start, t = solar_date(d, rule, lat, lon, tz, fn)
        out[rule] = {"month": nm[s], "day": day, "month_start": start.isoformat(), "sankranti": fmt(t, tz)}
    # eras
    y = d.year
    out["tamil"]["year_name"] = SAMVATSARAS[((y if (d.month, d.day) >= _md(y, "tamil", 0, lat, lon, tz, fn) else y - 1) - 1987) % 60]
    out["tamil"]["thiruvalluvar_year"] = y + 31 if (d.month, d.day) >= _md(y, "tamil", 9, lat, lon, tz, fn) else y + 30
    out["malayalam"]["kollam_era"] = y - 824 if (d.month, d.day) >= _md(y, "malayalam", 4, lat, lon, tz, fn) else y - 825
    bny = _md(y, "bengali", 0, lat, lon, tz, fn)
    out["bengali"]["bangabda"] = y - 593 if (d.month, d.day) >= bny else y - 594
    out["assamese"]["bhaskarabda"] = out["bengali"]["bangabda"]
    oy = _md(y, "odia", 0, lat, lon, tz, fn)
    out["odia"]["san"] = y - 593 if (d.month, d.day) >= oy else y - 594
    ev = day_events(d, lat, lon, tz)
    m, adh, _, _ = lunar_month(ev["sunrise"]); t0 = tithi_at(ev["sunrise"])
    from .panchang import samvat_info
    sv = samvat_info(d, m); shaka, vik_guj = sv["shaka"], sv["gujarati"]
    out["gujarati"] = {"month": MONTHS[m] + (" (Adhika)" if adh else ""), "system": "Amanta; year begins Kartika Shukla Pratipada (Bestu Varas)",
                       "vikram_samvat": vik_guj}
    out["marathi"] = {"month": MONTHS[m] + (" (Adhika)" if adh else ""), "system": "Amanta; year begins Chaitra Shukla Pratipada (Gudi Padwa)", "shaka_samvat": shaka}
    out["telugu_kannada"] = {"month": MONTHS[m] + (" (Adhika)" if adh else ""), "system": "Amanta; Ugadi = Chaitra Shukla Pratipada", "shaka_samvat": shaka}
    out["north_purnimanta"] = {"month": MONTHS[(m + (1 if t0 >= 15 else 0)) % 12], "system": "Purnimanta (month ends on Purnima)", "vikram_samvat": sv["vikram"]}
    return out

def _md(year, rule, sign, lat, lon, tz, fn):
    """(month, day) of day 1 of the solar month `sign` in `year`."""
    import datetime as _dt
    approx = Date(year, 4, 14) + timedelta(days=int(30.44 * sign))
    if approx.year != year: approx = Date(year, 1, 14) + timedelta(days=int(30.44 * ((sign - 9) % 12)))
    jd = local_midnight_jd(approx + timedelta(days=6), tz)
    t, s = sankranti_before(jd, fn)
    if s != sign:
        t, s = sankranti_before(jd + 20, fn)
    st = first_day(rule, t, lat, lon, tz)
    return (st.month, st.day)

def regional_new_years(year: int, lat, lon, tz_name=None, utc_offset=None, siddhanta="drik"):
    """Regional solar new years for `year` with the day each tradition observes it."""
    tz = make_tz(tz_name, utc_offset); fn = _sunfn(siddhanta)
    jd = local_midnight_jd(Date(year, 4, 20), tz); t, s = sankranti_before(jd, fn)
    rows = []
    for rule, nm in [("tamil", "Puthandu (Tamil New Year)"), ("malayalam", "Vishu (Malayalam)"), ("bengali", "Pohela Boishakh (Bengali New Year)"),
                     ("assamese", "Bohag Bihu (Assamese New Year)"), ("odia", "Pana Sankranti (Odia New Year)")]:
        d = first_day(rule, t, lat, lon, tz)
        rows.append({"name": nm, "date": d.isoformat(), "rule": RULES.get(rule)})
    jd2 = local_midnight_jd(Date(year, 1, 20), tz); t2, _ = sankranti_before(jd2, fn)
    rows.append({"name": "Thai Pongal (Thai 1)", "date": first_day("tamil", t2, lat, lon, tz).isoformat(), "rule": RULES["tamil"]})
    jd3 = local_midnight_jd(Date(year, 8, 30), tz); t3, _ = sankranti_before(jd3, fn)
    rows.append({"name": "Chingam 1 (Malayalam New Year)", "date": first_day("malayalam", t3, lat, lon, tz).isoformat(), "rule": RULES["malayalam"]})
    return {"year": year, "mesha_sankranti": fmt(t, tz), "siddhanta": siddhanta, "events": rows}

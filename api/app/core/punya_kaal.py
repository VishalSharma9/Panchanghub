"""Sankranti punya-kaal (Nirnayasindhu pt.1 'Sankranti-nirnaya'; Dharmasindhu pt.1), canonical classical rules.

Ghati G = 1/30 of the observing day's daytime (sunrise to sunset); the long Karka (30) and Makara (40) spans
use standard 24-minute ghatis (canonical classical formula, e.g. Karka punya-kaal starting 12 h before the moment).
Day-time sankranti (between sunrise and sunset) - window relative to the moment t, clipped to daylight:
  * Mesha, Tula (Vishuva, equinoctial) ............ 10 G before and 10 G after
  * Karka (Dakshinayana) ............................ 30 G before
  * Makara (Uttarayana) ............................. 40 G after
  * Vrishabha, Simha, Vrishchika, Kumbha (Vishnupadi) 16 G before
  * Mithuna, Kanya, Dhanu, Meena (Shadashiti-mukhi) . 16 G after
  Maha punya-kaal = 5 G on the same side(s) of the moment.
Night sankranti (after sunset / before the next sunrise):
  * before the middle of the night -> afternoon half of the preceding day: 15 G before sunset (maha: last 5 G);
  * after the middle of the night  -> forenoon half of the following day: 15 G after sunrise (maha: first 5 G).
  Exceptions: Makara at night is always kept the following day (whole day, 40 G clipped; maha first 5 G);
  Karka at night is always kept the preceding day (afternoon)."""
from __future__ import annotations
from datetime import date as Date, timedelta
from .ephem import make_tz, fmt, local_from_jd, next_boundary, local_midnight_jd, RASHIS
from .panchang import day_events, sun_sid

BEFORE_AFTER = {0: (10, 10), 6: (10, 10), 3: (30, 0), 9: (0, 40), 1: (16, 0), 4: (16, 0), 7: (16, 0), 10: (16, 0),
                2: (0, 16), 5: (0, 16), 8: (0, 16), 11: (0, 16)}
CLASS = {0: "Vishuva", 6: "Vishuva", 3: "Dakshinayana", 9: "Uttarayana", 1: "Vishnupadi", 4: "Vishnupadi", 7: "Vishnupadi",
         10: "Vishnupadi", 2: "Shadashiti", 5: "Shadashiti", 8: "Shadashiti", 11: "Shadashiti"}

def punya_kaal(t: float, sign: int, lat, lon, tz):
    ld = local_from_jd(t, tz).date()
    ev = day_events(ld, lat, lon, tz)
    if t < ev["sunrise"]:
        ld = ld - timedelta(days=1); ev = day_events(ld, lat, lon, tz)
    sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
    if sr <= t <= ss:
        G = (ss - sr) / 30; b, a = BEFORE_AFTER[sign]
        Gp = 1 / 60 if sign in (3, 9) else G  # Karka/Makara spans (30/40 ghatis) are counted in standard 24-min ghatis
        p = (max(sr, t - b * Gp), min(ss, t + a * Gp))
        m = (max(sr, t - (5 if b else 0) * G), min(ss, t + (5 if a else 0) * G))
        day, kind = ld, "day"
    else:
        mid = (ss + nsr) / 2
        nxt = (t >= mid or sign == 9) and sign != 3
        if nxt:
            day = ld + timedelta(days=1); e2 = day_events(day, lat, lon, tz); s2, ss2 = e2["sunrise"], e2["sunset"]; G = (ss2 - s2) / 30
            span = 40 if sign == 9 else 15
            p = (s2, min(ss2, s2 + span * G)); m = (s2, s2 + 5 * G); kind = "night (kept next day)"
        else:
            day = ld; G = (ss - sr) / 30
            p = (max(sr, ss - 15 * G), ss); m = (ss - 5 * G, ss); kind = "night (kept preceding day)"
    return {"rashi": RASHIS[sign], "class": CLASS[sign], "moment": fmt(t, tz), "observed_on": day.isoformat(), "type": kind,
            "punya_kaal": {"start": fmt(p[0], tz), "end": fmt(p[1], tz), "minutes": round((p[1] - p[0]) * 1440)},
            "maha_punya_kaal": {"start": fmt(m[0], tz), "end": fmt(m[1], tz), "minutes": round((m[1] - m[0]) * 1440)}}

def year_punya_kaal(year: int, lat, lon, tz_name=None, utc_offset=None):
    tz = make_tz(tz_name, utc_offset)
    t = local_midnight_jd(Date(year, 1, 1), tz); end = local_midnight_jd(Date(year + 1, 1, 1), tz); out = []
    while True:
        tt, idx = next_boundary(sun_sid, t, 30.0, forward=True, max_days=40, scan=1.0)
        if tt is None or tt >= end: break
        out.append(punya_kaal(tt, idx, lat, lon, tz)); t = tt + 1
    return {"year": year, "sankrantis": out, "rules": __doc__}

"""Western extras: synastry, composite, Davison, progressions, solar arc, returns, astrocartography,
Chiron/Lilith/asteroids, declinations, moon phases, compatibility score."""
from __future__ import annotations
import math
from datetime import timedelta
from .ephem import swe, BASE_FLAG, jd_from_utc, utc_from_jd, norm, angdiff, SIGNS, sign_info, dms, calc, next_boundary, fmt, PLANETS
from .western import natal_chart, ASPECTS, house_of

EXTRA = {"Chiron": swe.CHIRON, "Lilith (Mean)": swe.MEAN_APOG, "Ceres": swe.CERES, "Pallas": swe.PALLAS, "Juno": swe.JUNO, "Vesta": swe.VESTA}

def extra_points(jd, sidereal=False):
    out = []
    for n, b in EXTRA.items():
        try:
            lon, lat, sp = calc(jd, b, sidereal)
        except swe.Error:
            continue
        s, d = sign_info(lon)
        out.append({"name": n, "longitude": round(lon, 6), "sign": SIGNS[s], "degree": round(d, 6), "retrograde": sp < 0})
    return out

def declinations(jd):
    out = []
    for n, b in PLANETS.items():
        xx, _ = swe.calc_ut(jd, b, BASE_FLAG | swe.FLG_EQUATORIAL)
        dec = xx[1]
        out.append({"name": n, "right_ascension": round(xx[0], 6), "declination": round(dec, 6), "out_of_bounds": abs(dec) > 23.44})
    return out

def cross_aspects(p1, p2, orb_scale=1.0):
    res = []
    for a in p1:
        for b in p2:
            sep = abs(angdiff(a["longitude"], b["longitude"]))
            for nm, ang, orb in ASPECTS:
                if abs(sep - ang) <= orb * orb_scale:
                    res.append({"planet1": a["name"], "planet2": b["name"], "aspect": nm, "orb": round(abs(sep - ang), 3)})
    return res

WEIGHT = {"Conjunction": 3, "Trine": 3, "Sextile": 2, "Square": -2, "Opposition": -1}
KEY = {"Sun", "Moon", "Venus", "Mars", "Ascendant", "Mercury", "Jupiter", "Saturn"}

def synastry(dt1, lat1, lon1, dt2, lat2, lon2):
    c1 = natal_chart(dt1, lat1, lon1); c2 = natal_chart(dt2, lat2, lon2)
    p1 = [p for p in c1["planets"] if p["name"] != "Ketu"] + [{"name": "Ascendant", "longitude": c1["ascendant"]["longitude"]}]
    p2 = [p for p in c2["planets"] if p["name"] != "Ketu"] + [{"name": "Ascendant", "longitude": c2["ascendant"]["longitude"]}]
    asp = cross_aspects(p1, p2, 0.75)
    score = 50
    for a in asp:
        if a["planet1"] in KEY and a["planet2"] in KEY:
            w = WEIGHT[a["aspect"]]
            if a["aspect"] == "Conjunction" and {"Saturn", "Mars"} & {a["planet1"], a["planet2"]}: w = 0
            score += w * (1.5 if {a["planet1"], a["planet2"]} & {"Sun", "Moon", "Venus"} else 1)
    overlays = [{"planet": p["name"], "falls_in_partner_house": house_of(p["longitude"], [h["cusp"] for h in c2["houses"]])} for p in c1["planets"]]
    return {"aspects": asp, "compatibility_score": max(0, min(100, round(score))), "house_overlays_person1_in_person2": overlays}

def composite(dt1, lat1, lon1, dt2, lat2, lon2):
    c1 = natal_chart(dt1, lat1, lon1); c2 = natal_chart(dt2, lat2, lon2)
    def mid(a, b): return norm(a + angdiff(b, a) / 2)
    planets = []
    for a, b in zip(c1["planets"], c2["planets"]):
        L = mid(a["longitude"], b["longitude"]); s, d = sign_info(L)
        planets.append({"name": a["name"], "longitude": round(L, 6), "sign": SIGNS[s], "degree": round(d, 6)})
    asc = mid(c1["ascendant"]["longitude"], c2["ascendant"]["longitude"]); mc = mid(c1["midheaven"]["longitude"], c2["midheaven"]["longitude"])
    return {"method": "midpoint composite", "planets": planets, "ascendant": {"longitude": round(asc, 6), "sign": SIGNS[int(asc // 30)]},
            "midheaven": {"longitude": round(mc, 6), "sign": SIGNS[int(mc // 30)]}}

def davison(dt1, lat1, lon1, dt2, lat2, lon2):
    j = (jd_from_utc(dt1) + jd_from_utc(dt2)) / 2
    lat = (lat1 + lat2) / 2; lon = lon1 + angdiff(lon2, lon1) / 2
    return {"method": "Davison relationship chart", "datetime_utc": utc_from_jd(j).isoformat(), "latitude": lat, "longitude": lon,
            "chart": natal_chart(utc_from_jd(j), lat, lon)}

def progressions(dt, lat, lon, on_date):
    bj = jd_from_utc(dt)
    age_days = (jd_from_utc(on_date) - bj) / 365.2422
    pj = bj + age_days  # one day per year
    prog = natal_chart(utc_from_jd(pj), lat, lon)
    natal = natal_chart(dt, lat, lon)
    arc = norm(prog["planets"][0]["longitude"] - natal["planets"][0]["longitude"])
    solar_arc = [{"name": p["name"], "longitude": round(norm(p["longitude"] + arc), 6), "sign": SIGNS[int(norm(p["longitude"] + arc) // 30)]} for p in natal["planets"]]
    return {"age_years": round(age_days, 4), "secondary_progressed": {"datetime_utc": prog["datetime_utc"], "planets": prog["planets"], "ascendant": prog["ascendant"], "midheaven": prog["midheaven"]},
            "solar_arc": {"arc_degrees": round(arc, 6), "planets": solar_arc}}

def planet_return(dt, lat, lon, body_name: str, after_utc):
    b = PLANETS[body_name]
    target = calc(jd_from_utc(dt), b, False)[0]
    t = jd_from_utc(after_utc)
    f = lambda j: angdiff(calc(j, b, False)[0], target)
    step = 0.5 if body_name == "Moon" else 2.0
    g0 = f(t)
    for i in range(1, 20000):
        t1 = t + step; g1 = f(t1)
        if g0 < 0 <= g1 and abs(g1 - g0) < 90:
            a, c = t, t1
            for _ in range(60):
                m = (a + c) / 2
                if f(m) < 0: a = m
                else: c = m
            r = utc_from_jd(c)
            return {"body": body_name, "return_moment_utc": r.isoformat(), "chart": natal_chart(r, lat, lon)}
        t, g0 = t1, g1
    return None

def astrocartography(dt, step_lat: float = 5.0):
    jd = jd_from_utc(dt)
    gst = swe.sidtime(jd) * 15
    lines = {}
    for n, b in PLANETS.items():
        xx, _ = swe.calc_ut(jd, b, BASE_FLAG | swe.FLG_EQUATORIAL)
        ra, dec = xx[0], xx[1]
        mc = ((ra - gst + 180) % 360) - 180; ic = ((mc + 360) % 360) - 180
        asc, dsc = [], []
        lat = -75.0
        while lat <= 75.0001:
            x = -math.tan(math.radians(lat)) * math.tan(math.radians(dec))
            if -1 <= x <= 1:
                h0 = math.degrees(math.acos(x))
                asc.append([lat, round(((mc - h0 + 180) % 360) - 180, 3)]); dsc.append([lat, round(((mc + h0 + 180) % 360) - 180, 3)])
            lat += step_lat
        lines[n] = {"MC_longitude": round(mc, 3), "IC_longitude": round(((mc) % 360) - 180, 3), "ASC_line": asc, "DSC_line": dsc}
    return {"datetime_utc": dt.isoformat(), "lines": lines, "note": "Longitudes in degrees east; ASC/DSC lines as [lat, lon] points."}

PHASES = ["New Moon", "First Quarter", "Full Moon", "Last Quarter"]

def moon_phases(start_utc, days: int, tz):
    from .panchang import elong
    t = jd_from_utc(start_utc); end = t + days; out = []
    while True:
        tt, idx = next_boundary(elong, t, 90.0, forward=True, max_days=10, scan=0.5)
        if tt is None or tt > end: break
        out.append({"phase": PHASES[idx], "moment": fmt(tt, tz)}); t = tt + 0.01
    cur = elong(jd_from_utc(start_utc))
    illum = (1 - math.cos(math.radians(cur))) / 2
    return {"current": {"elongation": round(cur, 3), "illumination": round(illum, 4), "waxing": cur < 180}, "phases": out}

"""Western (or generic) natal chart: planets, houses, aspects. Also zodiac sign reference data."""
from __future__ import annotations
from .ephem import all_positions, houses, sign_info, dms, angdiff, nakshatra_of, SIGNS, NAKSHATRAS, NAK_LORDS, jd_from_utc, ayanamsa

ASPECTS = [("Conjunction", 0, 8), ("Sextile", 60, 6), ("Square", 90, 7), ("Trine", 120, 8), ("Opposition", 180, 8)]
HOUSE_SYSTEMS = {"placidus": "P", "koch": "K", "equal": "E", "whole_sign": "W", "porphyry": "O", "regiomontanus": "R", "campanus": "C"}

def house_of(lon, cusps):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 12

def natal_chart(dt_utc, lat, lon, system="tropical", house_system="placidus", true_node=False):
    from .ephem import strict_time, _strict_dt
    tok = strict_time(system == "tropical")
    try:
        return _natal_chart(dt_utc, lat, lon, system, house_system, true_node)
    finally:
        _strict_dt.reset(tok)

def _natal_chart(dt_utc, lat, lon, system, house_system, true_node):
    jd = jd_from_utc(dt_utc)
    sid = system == "sidereal"
    hs = HOUSE_SYSTEMS[house_system]
    pos = all_positions(jd, sid, true_node)
    cusps, asc, mc = houses(jd, lat, lon, hs, sid)
    planets = []
    for name, p in pos.items():
        s, d = sign_info(p["longitude"])
        item = {"name": name, "longitude": round(p["longitude"], 6), "latitude": round(p["latitude"], 6),
                "sign": SIGNS[s], "degree": round(d, 6), "dms": dms(d), "house": house_of(p["longitude"], cusps),
                "retrograde": p["speed"] < 0, "speed": round(p["speed"], 6)}
        if sid:
            ni, pada = nakshatra_of(p["longitude"])
            item.update(nakshatra=NAKSHATRAS[ni], pada=pada)
        planets.append(item)
    pts = [(p["name"], p["longitude"]) for p in planets if p["name"] != "Ketu"] + [("Ascendant", asc), ("MC", mc)]
    aspects = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, la = pts[i]; b, lb = pts[j]
            if {a, b} == {"Ascendant", "MC"}: continue
            sep = abs(angdiff(la, lb))
            for nm, ang, orb in ASPECTS:
                if abs(sep - ang) <= orb:
                    aspects.append({"planet1": a, "planet2": b, "aspect": nm, "angle": ang, "orb": round(abs(sep - ang), 4)})
    sa, da = sign_info(asc); sm, dm = sign_info(mc)
    return {"datetime_utc": dt_utc.isoformat(), "julian_day": jd, "system": system,
            "ayanamsa": round(ayanamsa(jd), 6) if sid else None, "house_system": house_system,
            "ascendant": {"longitude": round(asc, 6), "sign": SIGNS[sa], "degree": round(da, 6), "dms": dms(da)},
            "midheaven": {"longitude": round(mc, 6), "sign": SIGNS[sm], "degree": round(dm, 6), "dms": dms(dm)},
            "planets": planets, "houses": [{"house": i + 1, "cusp": round(c, 6), "sign": SIGNS[int(c // 30)]} for i, c in enumerate(cusps)],
            "aspects": aspects}

ZODIAC = {
 "aries": ("Aries", "Mesha", "♈", "Mar 21 – Apr 19", "Fire", "Cardinal", "Mars", "Mars", "Sun", ["courageous", "energetic", "impulsive"], "Head"),
 "taurus": ("Taurus", "Vrishabha", "♉", "Apr 20 – May 20", "Earth", "Fixed", "Venus", "Venus", "Moon", ["patient", "reliable", "stubborn"], "Neck, throat"),
 "gemini": ("Gemini", "Mithuna", "♊", "May 21 – Jun 20", "Air", "Mutable", "Mercury", "Mercury", None, ["curious", "adaptable", "restless"], "Arms, lungs"),
 "cancer": ("Cancer", "Karka", "♋", "Jun 21 – Jul 22", "Water", "Cardinal", "Moon", "Moon", "Jupiter", ["nurturing", "intuitive", "moody"], "Chest, stomach"),
 "leo": ("Leo", "Simha", "♌", "Jul 23 – Aug 22", "Fire", "Fixed", "Sun", "Sun", None, ["confident", "generous", "proud"], "Heart, spine"),
 "virgo": ("Virgo", "Kanya", "♍", "Aug 23 – Sep 22", "Earth", "Mutable", "Mercury", "Mercury", "Mercury", ["analytical", "practical", "critical"], "Intestines"),
 "libra": ("Libra", "Tula", "♎", "Sep 23 – Oct 22", "Air", "Cardinal", "Venus", "Venus", "Saturn", ["diplomatic", "fair", "indecisive"], "Kidneys, lower back"),
 "scorpio": ("Scorpio", "Vrishchika", "♏", "Oct 23 – Nov 21", "Water", "Fixed", "Pluto / Mars", "Mars", None, ["intense", "loyal", "secretive"], "Reproductive organs"),
 "sagittarius": ("Sagittarius", "Dhanu", "♐", "Nov 22 – Dec 21", "Fire", "Mutable", "Jupiter", "Jupiter", None, ["optimistic", "adventurous", "blunt"], "Hips, thighs"),
 "capricorn": ("Capricorn", "Makara", "♑", "Dec 22 – Jan 19", "Earth", "Cardinal", "Saturn", "Saturn", "Mars", ["disciplined", "ambitious", "reserved"], "Knees, bones"),
 "aquarius": ("Aquarius", "Kumbha", "♒", "Jan 20 – Feb 18", "Air", "Fixed", "Uranus / Saturn", "Saturn", None, ["independent", "inventive", "detached"], "Ankles, circulation"),
 "pisces": ("Pisces", "Meena", "♓", "Feb 19 – Mar 20", "Water", "Mutable", "Neptune / Jupiter", "Jupiter", "Venus", ["compassionate", "imaginative", "escapist"], "Feet"),
}
SIDEREAL_DATES = ["Apr 14 – May 14", "May 15 – Jun 14", "Jun 15 – Jul 16", "Jul 17 – Aug 16", "Aug 17 – Sep 16", "Sep 17 – Oct 16",
                  "Oct 17 – Nov 15", "Nov 16 – Dec 15", "Dec 16 – Jan 13", "Jan 14 – Feb 12", "Feb 13 – Mar 13", "Mar 14 – Apr 13"]

def zodiac_info(sign: str):
    k = sign.lower()
    alias = {v[1].lower(): kk for kk, v in ZODIAC.items()}
    k = alias.get(k, k)
    if k not in ZODIAC: return None
    n, r, sym, dates, el, mod, ruler, vruler, exalt, traits, body = ZODIAC[k]
    i = list(ZODIAC).index(k)
    naks = [NAKSHATRAS[j] for j in range(27) if (j * 40 // 3) // 1 < (i + 1) * 30 and (j + 1) * 40 / 3 > i * 30]
    return {"sign": n, "rashi": r, "symbol": sym, "index": i + 1, "tropical_dates": dates, "sidereal_dates_approx": SIDEREAL_DATES[i],
            "element": el, "modality": mod, "ruler_western": ruler, "ruler_vedic": vruler, "exalted_planet": exalt,
            "polarity": "Positive (masculine)" if i % 2 == 0 else "Negative (feminine)", "traits": traits, "body_part": body,
            "degrees": [i * 30, (i + 1) * 30], "nakshatras": naks}

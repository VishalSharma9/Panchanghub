"""Extended features: KP, Jaimini, Lal Kitab, Varshaphal, numerology, tarot, Chinese, horoscopes, Western extras,
regional panchang, element search, SVG charts, PDF reports, batch matching."""
from __future__ import annotations
from datetime import date as Date, datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from ...models import BirthData, KundliRequest
from ...core import ephem, numerology as N, tarot as T, chinese as CN, horoscope as H, western_ext as W, advanced as A
from ...core import panchang as P
from ...core.kundli import compute_kundli
from ...core.matching import ashtakoota, porutham
from ...core.western import natal_chart
from ...core.charts_svg import north_indian, south_indian, east_indian, western_wheel
from ..deps import birth_utc, loc_params, wrap

router = APIRouter()
tz_of = lambda b: ephem.make_tz(b.timezone, b.utc_offset)

# ---- KP / Jaimini / Lal Kitab / Varshaphal ----
@router.post("/kp/chart", tags=["KP System"], summary="KP planets & cusps with star/sub/sub-sub lords, significators, ruling planets")
def kp(req: BirthData):
    return wrap(A.kp_chart, birth_utc(req), req.latitude, req.longitude)

@router.get("/kp/horary/{number}", tags=["KP System"], summary="KP horary number (1-249) to ascendant segment")
def kp_horary(number: int):
    return wrap(A.kp_horary, number)

def _k(req): return compute_kundli(birth_utc(req), req.latitude, req.longitude, tz_of(req), dasha_levels=1)

@router.post("/jaimini", tags=["Jaimini"])
def jaimini(req: BirthData): return _k(req)["jaimini"]

@router.post("/lal-kitab", tags=["Lal Kitab"])
def lal_kitab(req: BirthData): return _k(req)["lal_kitab"]

class VarshaReq(BirthData):
    year: int = Field(..., ge=1, le=3000)

@router.post("/varshaphal", tags=["Varshaphal"], summary="Annual (Tajik) chart: Muntha, Mudda dasha, Tajik yogas, Sahams")
def varshaphal(req: VarshaReq):
    return wrap(A.varshaphal, birth_utc(req), req.latitude, req.longitude, req.year, tz_of(req))

@router.post("/kundli/report", tags=["Kundli & Matching"], summary="Life / career / love / health / finance report")
def life_report(req: BirthData):
    k = _k(req); return {"report": H.life_report(k), "yogas": k["yogas"], "doshas": k["doshas"]["manglik"]}

# ---- SVG / PDF ----
@router.post("/kundli/svg", tags=["Charts"], summary="Render chart SVG (north|south|east Indian, any varga)",
             response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}})
def kundli_svg(req: BirthData, style: Literal["north", "south", "east"] = "north", varga: str = "D1"):
    k = _k(req)
    if varga not in k["vargas"]: raise HTTPException(422, "unknown varga")
    v = k["vargas"][varga]; asc = ephem.SIGNS.index(v["ascendant_sign"])
    pl = [{"name": n, "sign": ephem.SIGNS.index(d["sign"]), "retrograde": next(p["retrograde"] for p in k["planets"] if p["name"] == n)} for n, d in v["planets"].items()]
    fn = {"north": north_indian, "south": south_indian, "east": east_indian}[style]
    return Response(fn(asc, pl, 400, varga), media_type="image/svg+xml")

@router.post("/chart/svg", tags=["Charts"], summary="Western natal wheel SVG", response_class=Response)
def wheel_svg(req: BirthData):
    c = natal_chart(birth_utc(req), req.latitude, req.longitude)
    return Response(western_wheel(c["ascendant"]["longitude"], [h["cusp"] for h in c["houses"]], c["planets"]), media_type="image/svg+xml")

@router.post("/kundli/pdf", tags=["Charts"], summary="Kundli PDF report", response_class=Response)
def kundli_pdf(req: KundliRequest):
    from ...core.report_pdf import kundli_pdf as build
    k = compute_kundli(birth_utc(req), req.latitude, req.longitude, tz_of(req), dasha_levels=2)
    return Response(build(k, req.name or "Native"), media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="kundli.pdf"'})

# ---- Batch matching ----
class BatchMatch(BaseModel):
    person: BirthData
    person_is: Literal["boy", "girl"] = "boy"
    candidates: list[BirthData] = Field(..., min_length=1, max_length=500)

@router.post("/matching/batch", tags=["Kundli & Matching"], summary="Match one profile against up to 500")
def batch(req: BatchMatch):
    m = P.moon_sid(ephem.jd_from_utc(birth_utc(req.person))); out = []
    for i, c in enumerate(req.candidates):
        o = P.moon_sid(ephem.jd_from_utc(birth_utc(c)))
        b, g = (m, o) if req.person_is == "boy" else (o, m)
        a = ashtakoota(b, g); po = porutham(b, g)
        out.append({"index": i, "guna": a["total"], "verdict": a["verdict"], "doshas": a["doshas"], "porutham": po["matched"]})
    out.sort(key=lambda r: -r["guna"])
    return {"results": out}

@router.get("/matching/nakshatra", tags=["Kundli & Matching"], summary="Nakshatra-only matching (no birth time)")
def nak_match(boy_nakshatra: int = Query(..., ge=1, le=27), boy_pada: int = Query(1, ge=1, le=4),
              girl_nakshatra: int = Query(..., ge=1, le=27), girl_pada: int = Query(1, ge=1, le=4)):
    lon = lambda n, p: (n - 1) * 360 / 27 + (p - 0.5) * 360 / 108
    b, g = lon(boy_nakshatra, boy_pada), lon(girl_nakshatra, girl_pada)
    return {"ashtakoota": ashtakoota(b, g), "porutham": porutham(b, g)}

# ---- Panchang extras ----
@router.get("/panchang/regional", tags=["Panchang"], summary="Tamil, Malayalam, Bengali, Gujarati, Telugu month & day")
def regional(date: Date | None = None, loc=Depends(loc_params)):
    return wrap(P.regional, date or Date.today(), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/search/{kind}", tags=["Panchang"], summary="Next occurrences of a tithi / nakshatra / yoga")
def search(kind: Literal["tithi", "nakshatra", "yoga"], index: int = Query(..., ge=1, le=30), count: int = Query(5, ge=1, le=24),
           start: Date | None = None, tz: str = "Asia/Kolkata"):
    if kind != "tithi" and index > 27: raise HTTPException(422, "index 1..27")
    tzi = ephem.make_tz(tz); s = start or Date.today()
    return {"kind": kind, "results": P.search_element(kind, index, ephem.local_midnight_jd(s, tzi), count, tzi)}

@router.get("/moon-phases", tags=["Transits"])
def moon_phases(start: Date | None = None, days: int = Query(30, ge=1, le=3660), tz: str = "UTC"):
    s = start or Date.today()
    return W.moon_phases(datetime(s.year, s.month, s.day, tzinfo=timezone.utc), days, ephem.make_tz(tz))

@router.get("/gochar", tags=["Transits"], summary="Current transits relative to a natal Moon sign")
def gochar(moon_sign: str, datetime_: str | None = Query(None, alias="datetime")):
    dt = datetime.fromisoformat(datetime_) if datetime_ else datetime.now(timezone.utc)
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    h = H.horoscope(moon_sign, "daily", dt.date(), "vedic")
    si = ephem.SIGNS.index(h["sign"])
    return {"moon_sign": h["sign"], "transits": {p: {"sign": s, "house_from_moon": (ephem.SIGNS.index(s) - si) % 12 + 1,
            "favourable": ((ephem.SIGNS.index(s) - si) % 12 + 1) in H.GOOD.get(p, [])} for p, s in h["transits"].items()}}

# ---- Horoscopes ----
@router.get("/horoscope/nakshatra/{index}", tags=["Horoscopes"])
def nak_pred(index: int, date: Date | None = None):
    if not 1 <= index <= 27: raise HTTPException(422, "1..27")
    return H.nakshatra_prediction(index - 1, date or Date.today())

@router.get("/horoscope/{period}/{sign}", tags=["Horoscopes"])
def horoscope(period: Literal["daily", "weekly", "monthly", "yearly"], sign: str, date: Date | None = None,
              system: Literal["vedic", "western"] = "vedic"):
    return wrap(H.horoscope, sign, period, date, system)

# ---- Numerology ----
class AstroNumerologyReq(BirthData):
    name: str = Field(..., min_length=1, max_length=120)
    system: Literal["pythagorean", "chaldean"] = "pythagorean"
    transit_date: Date | None = None

@router.get("/numerology", tags=["Numerology"], summary="Full Numerology Profile with Core Numbers, Karmic Debts, Pinnacles & Optional Kundli Synthesis")
def numerology(name: str = Query(..., min_length=1, max_length=120), dob: Date = Query(...),
               system: Literal["pythagorean", "chaldean"] = "pythagorean",
               time: str | None = Query(None, description="Birth time in HH:MM:SS format"),
               lat: float | None = Query(None, description="Birth latitude"),
               lon: float | None = Query(None, description="Birth longitude"),
               tz: str = Query("Asia/Kolkata", description="Timezone name or offset"),
               transit_date: Date | None = Query(None, description="Date for transit calculations (defaults to today)")):
    birth_details = None
    if lat is not None and lon is not None:
        birth_details = {"time": time or "12:00:00", "latitude": lat, "longitude": lon, "timezone": tz}
    return N.profile(name, dob, system, birth_details, transit_date)

@router.post("/numerology/chart", tags=["Numerology"], summary="Comprehensive Astro-Numerology Kundli Synthesis & Transit Harmonics")
def numerology_chart(req: AstroNumerologyReq):
    bd = {"time": req.time.isoformat() if hasattr(req.time, "isoformat") else str(req.time),
          "latitude": req.latitude, "longitude": req.longitude,
          "timezone": req.timezone or "Asia/Kolkata", "utc_offset": req.utc_offset}
    return N.profile(req.name, req.date, req.system, birth_details=bd, transit_date=req.transit_date)

@router.get("/numerology/lucky", tags=["Numerology"], summary="Personal Lucky Numbers, Compound Power Numbers & Shatru Anka (Avoid)")
def numerology_lucky(dob: Date = Query(..., description="Date of birth"), name: str = Query("Soul", description="Name")):
    m = N.reduce_single(dob.day)
    b = N.reduce_single(sum(int(c) for c in dob.strftime("%d%m%Y")))
    nam = N.reduce_single(N.name_sum(name, N.CHALD))
    return {"lucky_numbers": N.generate_lucky_bundle(m, b, nam), "numbers_to_avoid": N.get_numbers_to_avoid(m, b)}

@router.get("/numerology/transits", tags=["Numerology"], summary="Current Gochar Transit Numerology & Daily Transit-Harmonized Numbers")
def numerology_transits(dob: Date = Query(...), date: Date | None = Query(None)):
    return N.analyze_current_transits_numerology(dob, date)

@router.get("/numerology/pinnacles", tags=["Numerology"], summary="4 Life Pinnacles, Challenges & Age Epochs")
def numerology_pinnacles(dob: Date = Query(...)):
    lp = N.reduce_single(N.reduce(dob.year) + N.reduce(dob.month) + N.reduce(dob.day))
    return N.calculate_pinnacles_and_challenges(dob, lp)

@router.get("/numerology/daily", tags=["Numerology"])
def numerology_daily(dob: Date, date: Date | None = None): return N.daily(dob, date or Date.today())

@router.get("/numerology/compatibility", tags=["Numerology"])
def numerology_compat(name1: str, dob1: Date, name2: str, dob2: Date): return N.compatibility(name1, dob1, name2, dob2)

@router.get("/biorhythm", tags=["Other"])
def biorhythm(dob: Date, date: Date | None = None, days: int = Query(7, ge=1, le=90)): return N.biorhythm(dob, date or Date.today(), days)

@router.get("/angel-number/{number}", tags=["Other"])
def angel(number: str): return wrap(N.angel_number, number)

# ---- Tarot ----
@router.get("/tarot/draw", tags=["Tarot"])
def tarot(spread: Literal["single", "yes_no", "three_card", "love", "celtic_cross"] = "three_card", question: str | None = None, seed: str | None = None):
    return T.draw(spread, seed, question)

@router.get("/tarot/daily", tags=["Tarot"])
def tarot_daily(key: str = "", date: Date | None = None): return T.daily(date or Date.today(), key)

@router.get("/tarot/cards", tags=["Tarot"])
def tarot_cards(): return {"cards": T.deck()}

# ---- Chinese ----
@router.get("/chinese/zodiac", tags=["Chinese"])
def chinese_zodiac(date: Date): return CN.zodiac_year(datetime(date.year, date.month, date.day, 12))

@router.post("/chinese/bazi", tags=["Chinese"], summary="BaZi four pillars")
def bazi(req: BirthData):
    return CN.bazi(datetime.combine(req.date, req.time).replace(tzinfo=tz_of(req)))

@router.get("/chinese/compatibility", tags=["Chinese"])
def cn_compat(year1: int, year2: int): return CN.compatibility((year1 - 4) % 12, (year2 - 4) % 12)

@router.get("/chinese/kua", tags=["Chinese"])
def kua(year: int, gender: Literal["male", "female"]): return CN.kua(year, gender)

# ---- Western extras ----
class TwoPeople(BaseModel):
    person1: BirthData
    person2: BirthData

@router.post("/western/synastry", tags=["Western"])
def synastry(req: TwoPeople):
    a, b = req.person1, req.person2
    return W.synastry(birth_utc(a), a.latitude, a.longitude, birth_utc(b), b.latitude, b.longitude)

@router.post("/western/composite", tags=["Western"])
def composite(req: TwoPeople):
    a, b = req.person1, req.person2
    return W.composite(birth_utc(a), a.latitude, a.longitude, birth_utc(b), b.latitude, b.longitude)

@router.post("/western/davison", tags=["Western"])
def davison(req: TwoPeople):
    a, b = req.person1, req.person2
    return W.davison(birth_utc(a), a.latitude, a.longitude, birth_utc(b), b.latitude, b.longitude)

class ProgReq(BirthData):
    on_date: Date

@router.post("/western/progressions", tags=["Western"], summary="Secondary progressions and solar arc directions")
def progressions(req: ProgReq):
    return W.progressions(birth_utc(req), req.latitude, req.longitude, datetime(req.on_date.year, req.on_date.month, req.on_date.day, tzinfo=timezone.utc))

class ReturnReq(BirthData):
    body: Literal["Sun", "Moon", "Jupiter", "Saturn"] = "Sun"
    after: Date

@router.post("/western/return", tags=["Western"], summary="Solar / lunar / planetary return chart")
def ret(req: ReturnReq):
    return W.planet_return(birth_utc(req), req.latitude, req.longitude, req.body, datetime(req.after.year, req.after.month, req.after.day, tzinfo=timezone.utc))

@router.post("/western/astrocartography", tags=["Western"])
def acg(req: BirthData): return W.astrocartography(birth_utc(req))

@router.post("/western/extras", tags=["Western"], summary="Chiron, Lilith, asteroids and declinations / out-of-bounds")
def wextras(req: BirthData):
    jd = ephem.jd_from_utc(birth_utc(req))
    return {"points": W.extra_points(jd), "declinations": W.declinations(jd)}

"""Round-3 features: full Shadbala/Bhavabala, extra dashas, Ghata chakra, interpretations, multilingual glossary,
Human Design, Vastu, I-Ching, palmistry, Kabbalah, Mayan, dreams, crystals, Chinese yearly forecast, remedies,
Manglik match, matching/varshaphal PDF, KP horary chart, transit search & Western transit chart, MCP endpoint
and a rule-based assistant."""
from __future__ import annotations
from datetime import date as Date, datetime, timezone, timedelta
from typing import Literal, Optional, Any
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from ...models import BirthData, KundliRequest, MatchRequest
from ...core import ephem, i18n, interpret as I, esoteric as E, human_design as HD, dashas as D, advanced as A
from ...core import calendar as C, panchang as P, horoscope as H, numerology as N, western_ext as W
from ...core.kundli import compute_kundli
from ...core.matching import ashtakoota, porutham
from ...core.manglik_match import manglik_match
from ...core.western import natal_chart
from ..deps import birth_utc, wrap

router = APIRouter()
tz_of = lambda b: ephem.make_tz(b.timezone, b.utc_offset)
def _k(req, levels=2): return compute_kundli(birth_utc(req), req.latitude, req.longitude, tz_of(req), dasha_levels=levels)

# ---- strength / dashas ----
@router.post("/kundli/shadbala", tags=["Kundli"], summary="Full six-fold Shadbala (BPHS) + Bhavabala")
def shadbala(req: BirthData):
    k = _k(req, 1); return {"shadbala": k["shadbala"], "bhavabala": k["bhavabala"]}

@router.post("/kundli/dashas", tags=["Dashas"], summary="Chara, Kalachakra and 8 conditional nakshatra dashas (+ Vimshottari, Yogini, Ashtottari)")
def dashas(req: BirthData):
    k = _k(req, 2)
    return {"vimshottari": k["vimshottari_dasha"], "yogini": k["yogini_dasha"], "ashtottari": k["ashtottari_dasha"], **k["dashas_other"]}

@router.post("/kundli/ghata-chakra", tags=["Kundli"])
def ghata(req: BirthData): return _k(req, 1)["ghata_chakra"]

@router.post("/kundli/interpretation", tags=["Interpretations"], summary="Written reading: planets in signs/houses, nakshatras, yogas, doshas, dashas")
def interpretation(req: BirthData): return I.kundli_reading(_k(req, 1))

@router.post("/kundli/remedies", tags=["Remedies"], summary="Puja, mantra & dosha remedies from the chart")
def remedies(req: BirthData):
    k = _k(req, 1); return {**E.remedies_for(k), "gemstones_rudraksha": k["remedies"], "lal_kitab": k["lal_kitab"].get("remedies")}

@router.post("/western/interpretation", tags=["Western"], summary="Written natal reading (planets in signs/houses & aspects)")
def western_interp(req: BirthData):
    return I.western_reading(natal_chart(birth_utc(req), req.latitude, req.longitude))

class TransitReq(BirthData):
    transit_datetime: Optional[datetime] = Field(None, description="UTC; default now")
@router.post("/western/transits", tags=["Western"], summary="Transit-to-natal aspects (Western transit chart)")
def western_transits(req: TransitReq):
    t = req.transit_datetime or datetime.now(timezone.utc)
    if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
    nat = natal_chart(birth_utc(req), req.latitude, req.longitude); tr = natal_chart(t, req.latitude, req.longitude)
    asp = W.cross_aspects(tr["planets"], nat["planets"], 0.5)
    for a in asp: a["text"] = f"Transiting {a['planet1']} {a['aspect'].lower()} natal {a['planet2']}: " + I.ASPECT[a["aspect"]].format(a=I.WEST_PLANET_KEY.get(a["planet1"], a["planet1"]), b=I.WEST_PLANET_KEY.get(a["planet2"], a["planet2"])) + "."
    return {"transit_utc": t.isoformat(), "transit_planets": tr["planets"], "aspects_to_natal": sorted(asp, key=lambda x: x["orb"])}

@router.get("/interpretation/planet/{planet}", tags=["Interpretations"])
def interp_planet(planet: str, sign: Optional[str] = None, house: Optional[int] = Query(None, ge=1, le=12)):
    p = planet.title()
    if p not in I.PLANET: raise HTTPException(404, "unknown planet")
    out = {"planet": p, "nature": I.PLANET[p], "dasha": I.dasha_text(p)}
    if sign: out["in_sign"] = I.planet_in_sign(p, sign.title())
    if house: out["in_house"] = I.planet_in_house(p, house)
    return out

@router.get("/interpretation/nakshatra/{index}", tags=["Interpretations"])
def interp_nak(index: int):
    if not 1 <= index <= 27: raise HTTPException(422, "1..27")
    return {"index": index, "nakshatra": ephem.NAKSHATRAS[index - 1], "text": I.NAK[index - 1]}

@router.get("/interpretation/yogas", tags=["Interpretations"])
def interp_yogas(): return {"yogas": I.YOGA, "doshas": I.DOSHA, "dashas": I.DASHA}

# ---- i18n ----
@router.get("/languages", tags=["Multilingual"])
def languages(): return {"languages": i18n.LANGS, "usage": "append ?lang=<code> to any endpoint"}

@router.get("/i18n/{lang}", tags=["Multilingual"], summary="Glossary of all localized names/labels")
def glossary(lang: str): return wrap(i18n.glossary, lang)

# ---- matching ----
@router.post("/matching/manglik", tags=["Matching"], summary="Pairwise Manglik compatibility")
def mmatch(req: MatchRequest):
    kb, kg = _k(req.boy, 1), _k(req.girl, 1)
    return manglik_match(kb["doshas"]["manglik"], kg["doshas"]["manglik"])

class MatchPdf(MatchRequest):
    boy_name: str = "Boy"; girl_name: str = "Girl"
@router.post("/matching/pdf", tags=["Matching"], response_class=Response, summary="Matching report PDF")
def match_pdf(req: MatchPdf):
    from ...core.report_pdf import matching_pdf
    kb, kg = _k(req.boy, 1), _k(req.girl, 1)
    mb = next(p for p in kb["planets"] if p["name"] == "Moon")["longitude"]; mg = next(p for p in kg["planets"] if p["name"] == "Moon")["longitude"]
    res = {"ashtakoota": ashtakoota(mb, mg), "porutham": porutham(mb, mg), "manglik": manglik_match(kb["doshas"]["manglik"], kg["doshas"]["manglik"])}
    return Response(matching_pdf(res, req.boy_name, req.girl_name), media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="matching.pdf"'})

class VarshaPdf(BirthData):
    year: int = Field(..., ge=1, le=3000); name: str = "Native"
@router.post("/varshaphal/pdf", tags=["Varshaphal"], response_class=Response, summary="Yearly (Varshaphal) report PDF")
def varsha_pdf(req: VarshaPdf):
    from ...core.report_pdf import varshaphal_pdf
    v = A.varshaphal(birth_utc(req), req.latitude, req.longitude, req.year, tz_of(req))
    return Response(varshaphal_pdf(v, req.name), media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="varshaphal.pdf"'})

# ---- KP horary ----
class Horary(BaseModel):
    number: int = Field(..., ge=1, le=249); latitude: float = Field(..., ge=-90, le=90); longitude: float = Field(..., ge=-180, le=180)
    datetime_utc: Optional[datetime] = None
@router.post("/kp/horary/chart", tags=["KP System"], summary="Full KP horary (prashna) chart for a number 1-249")
def kp_hchart(req: Horary):
    t = req.datetime_utc or datetime.now(timezone.utc)
    if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
    return wrap(A.kp_horary_chart, req.number, t, req.latitude, req.longitude)

# ---- transit search ----
@router.get("/transits/search", tags=["Transits"], summary="When does a planet enter a sign / station (searches up to 30 years)")
def transit_search(planet: str, sign: Optional[str] = None, event: Literal["ingress", "retrograde_start", "direct_station"] = "ingress",
                   start: Optional[Date] = None, years: int = Query(5, ge=1, le=30), count: int = Query(3, ge=1, le=20),
                   sidereal: bool = True, tz: str = "Asia/Kolkata"):
    s = start or Date.today(); out = []
    for y in range(years):
        a = s + timedelta(days=365 * y); b = a + timedelta(days=365)
        for e in C.transits(a, b, tz, None, sidereal)["events"]:
            if e["planet"].lower() == planet.lower() and e["event"] == event and (not sign or (e.get("to_sign") or e.get("sign", "")).lower() == sign.lower()):
                if e not in out: out.append(e)
        if len(out) >= count: break
    return {"planet": planet, "event": event, "sign": sign, "results": out[:count]}

# ---- Human Design ----
@router.post("/human-design", tags=["Other domains"], summary="Human Design bodygraph: type, authority, profile, centers, channels, gates")
def human_design(req: BirthData): return HD.bodygraph(birth_utc(req))

# ---- I-Ching ----
@router.get("/iching/cast", tags=["Other domains"], summary="Cast a hexagram (three-coin method)")
def iching(question: Optional[str] = None, seed: Optional[str] = None): return E.iching_cast(question, seed)
@router.get("/iching/hexagrams", tags=["Other domains"])
def iching_all(): return {"hexagrams": E.iching_all()}
@router.get("/iching/hexagram/{number}", tags=["Other domains"])
def iching_one(number: int):
    if not 1 <= number <= 64: raise HTTPException(422, "1..64")
    return E.iching_all()[number - 1]

# ---- Vastu ----
class VastuReq(BaseModel):
    facing: Optional[str] = Field(None, examples=["East"])
    layout: Optional[dict[str, str]] = Field(None, examples=[{"kitchen": "South-East", "puja room": "North-East", "master bedroom": "South-West"}])
@router.post("/vastu", tags=["Other domains"], summary="Vastu directions guide + layout evaluation score")
def vastu_post(req: VastuReq): return E.vastu(req.layout, req.facing)
@router.get("/vastu", tags=["Other domains"])
def vastu_get(facing: Optional[str] = None): return E.vastu(None, facing)

# ---- Palmistry / Kabbalah / Mayan / Dreams / Crystals / Chinese forecast ----
@router.get("/palmistry", tags=["Other domains"], summary="Palmistry reference + reading from described features")
def palm(hand_shape: Optional[Literal["earth", "air", "fire", "water"]] = None, heart: Optional[str] = None, head: Optional[str] = None,
         life: Optional[str] = None, fate: Optional[str] = None):
    return E.palmistry(hand_shape, heart, head, life, fate)
@router.get("/kabbalah", tags=["Other domains"])
def kabbalah(name: str = Query(..., min_length=1, max_length=100), dob: Optional[Date] = None): return E.kabbalah(name, dob)
@router.get("/mayan", tags=["Other domains"], summary="Mayan Long Count, Tzolk'in and Haab'")
def mayan(on: Optional[Date] = None): return E.mayan(on or Date.today())
@router.get("/dreams", tags=["Other domains"])
def dreams(symbol: Optional[str] = None): return E.dream(symbol)
@router.get("/crystals", tags=["Other domains"])
def crystals(sign: Optional[str] = None, planet: Optional[str] = None, chakra: Optional[str] = None): return E.crystals(sign, planet, chakra)
@router.get("/chinese/forecast", tags=["Chinese"], summary="Chinese zodiac yearly forecast")
def cforecast(birth_year: int = Query(..., ge=1900, le=2100), year: Optional[int] = Query(None, ge=1900, le=2100)):
    return E.chinese_forecast(birth_year, year or Date.today().year)

# ---- Rule-based assistant ----
class Ask(BaseModel):
    question: str = Field(..., max_length=500)
    latitude: float = 28.6139; longitude: float = 77.209; timezone: str = "Asia/Kolkata"
@router.post("/ask", tags=["Assistant"], summary="Rule-based astrology assistant (intent matching over our API, no LLM)")
def ask(req: Ask):
    q = req.question.lower(); today = datetime.now(ephem.make_tz(req.timezone)).date()
    def pan(): return P.compute_panchang(today, req.latitude, req.longitude, req.timezone)
    if "ekadashi" in q or "purnima" in q or "amavasya" in q:
        kind = "ekadashi" if "ekadashi" in q else "purnima" if "purnima" in q else "amavasya"
        ev = [e for e in C.year_festivals(today.year, req.latitude, req.longitude, req.timezone)["events"] + C.year_festivals(today.year + 1, req.latitude, req.longitude, req.timezone)["events"]
              if e["type"] == kind and e["date"] >= today.isoformat()][:3]
        return {"intent": f"next_{kind}", "answer": f"Next {kind.title()}: " + "; ".join(f"{e['name']} on {e['date']}" for e in ev), "data": ev}
    def _ampm(iso_s: str | None) -> str:
        if not iso_s:
            return ""
        try:
            return datetime.fromisoformat(iso_s).strftime("%I:%M %p")
        except Exception:
            return iso_s[11:16] if len(iso_s) >= 16 else iso_s

    if "rahu" in q:
        p = pan(); r = p["muhurta"]["rahu_kalam"]; return {"intent": "rahu_kaal", "answer": f"Rahu Kaal today: {_ampm(r['start'])} – {_ampm(r['end'])}", "data": r}
    if "tithi" in q:
        t = pan()["tithi"][0]; return {"intent": "tithi", "answer": f"Today's tithi: {t['paksha']} {t['name']} until {_ampm(t.get('end'))}", "data": t}
    if "nakshatra" in q:
        n = pan()["nakshatra"][0]; return {"intent": "nakshatra", "answer": f"Today's nakshatra: {n['name']} until {_ampm(n.get('end'))}", "data": n}
    if "sunrise" in q or "sunset" in q:
        p = pan(); return {"intent": "sun", "answer": f"Sunrise {_ampm(p['sunrise'])}, sunset {_ampm(p['sunset'])}"}
    if "festival" in q or "diwali" in q or "holi" in q:
        ev = [e for e in C.year_festivals(today.year, req.latitude, req.longitude, req.timezone)["events"] if e["type"] == "festival" and e["date"] >= today.isoformat()]
        for nm in ("diwali", "holi", "navratri", "dussehra", "janmashtami", "shivaratri"):
            if nm in q: ev = [e for e in ev if nm in e["name"].lower()] or ev
        return {"intent": "festival", "answer": "Upcoming: " + "; ".join(f"{e['name']} {e['date']}" for e in ev[:5]), "data": ev[:5]}
    for s in ephem.SIGNS:
        if s.lower() in q:
            h = H.horoscope(s, "daily"); return {"intent": "horoscope", "answer": h.get("overall") or h.get("text") or str(h)[:300], "data": h}
    return {"intent": "unknown", "answer": "I can answer: next Ekadashi/Purnima/Amavasya, today's Rahu Kaal, tithi, nakshatra, sunrise/sunset, upcoming festivals, or a sign's daily horoscope.",
            "note": "Rule-based assistant; for free-form AI chat connect an LLM via the MCP endpoint (/api/mcp)."}

# ---- MCP (Model Context Protocol, JSON-RPC over HTTP) ----
MCP_TOOLS = [
    {"name": "panchang", "description": "Daily panchang for a date and location", "inputSchema": {"type": "object", "properties": {"date": {"type": "string"}, "lat": {"type": "number"}, "lon": {"type": "number"}, "tz": {"type": "string"}}, "required": ["date", "lat", "lon", "tz"]}},
    {"name": "festivals", "description": "Hindu festival & vrat calendar for a year", "inputSchema": {"type": "object", "properties": {"year": {"type": "integer"}, "lat": {"type": "number"}, "lon": {"type": "number"}, "tz": {"type": "string"}}, "required": ["year", "lat", "lon", "tz"]}},
    {"name": "kundli", "description": "Vedic birth chart summary", "inputSchema": {"type": "object", "properties": {"date": {"type": "string"}, "time": {"type": "string"}, "lat": {"type": "number"}, "lon": {"type": "number"}, "tz": {"type": "string"}}, "required": ["date", "time", "lat", "lon", "tz"]}},
    {"name": "horoscope", "description": "Daily/weekly/monthly/yearly horoscope for a sign", "inputSchema": {"type": "object", "properties": {"sign": {"type": "string"}, "period": {"type": "string"}}, "required": ["sign"]}},
    {"name": "numerology", "description": "Numerology profile", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "dob": {"type": "string"}}, "required": ["name", "dob"]}},
    {"name": "ask", "description": "Rule-based astrology Q&A", "inputSchema": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}},
]
def _mcp_call(name, a):
    if name == "panchang": return P.compute_panchang(Date.fromisoformat(a["date"]), a["lat"], a["lon"], a["tz"])
    if name == "festivals": return C.year_festivals(int(a["year"]), a["lat"], a["lon"], a["tz"])
    if name == "kundli":
        dt = ephem.to_utc(datetime.fromisoformat(f"{a['date']}T{a['time']}"), a["tz"]); k = compute_kundli(dt, a["lat"], a["lon"], ephem.make_tz(a["tz"]), dasha_levels=1)
        return {"lagna": k["lagna"], "planets": [{x: p[x] for x in ("name", "sign", "house", "nakshatra", "pada", "dignity")} for p in k["planets"]], "yogas": k["yogas"], "doshas": k["doshas"]["manglik"], "reading": I.kundli_reading(k)["ascendant"]}
    if name == "horoscope": return H.horoscope(a["sign"].title(), a.get("period", "daily"))
    if name == "numerology": return N.profile(a["name"], Date.fromisoformat(a["dob"]))
    if name == "ask": return ask(Ask(question=a["question"]))
    raise ValueError(f"unknown tool {name}")

@router.post("/mcp", tags=["Assistant"], summary="MCP server (JSON-RPC 2.0: initialize, tools/list, tools/call)")
async def mcp(request: Request):
    import json
    msg = await request.json()
    def reply(mid, result=None, error=None):
        r = {"jsonrpc": "2.0", "id": mid}; r["error" if error else "result"] = error or result; return r
    def handle(m):
        mid, method, params = m.get("id"), m.get("method"), m.get("params") or {}
        if method == "initialize":
            return reply(mid, {"protocolVersion": "2025-03-26", "serverInfo": {"name": "panchanghub", "version": "1.0.0"}, "capabilities": {"tools": {}}})
        if method == "notifications/initialized": return None
        if method == "tools/list": return reply(mid, {"tools": MCP_TOOLS})
        if method == "tools/call":
            try:
                res = _mcp_call(params.get("name"), params.get("arguments") or {})
                return reply(mid, {"content": [{"type": "text", "text": json.dumps(res, default=str)[:100000]}]})
            except Exception as e:
                return reply(mid, {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
        return reply(mid, error={"code": -32601, "message": f"method not found: {method}"})
    if isinstance(msg, list):
        out = [r for r in (handle(m) for m in msg) if r]; return JSONResponse(out)
    r = handle(msg)
    return JSONResponse(r) if r else Response(status_code=202)

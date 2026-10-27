"""Original endpoints: /health, /chart, /planets, /zodiac/{sign}, /nakshatra."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Depends
from ...models import ChartRequest
from ...core import ephem
from ...core.western import natal_chart, zodiac_info
from ..deps import birth_utc, loc_params, wrap

router = APIRouter(tags=["Core"])

@router.get("/health")
def health():
    return {"status": "ok", "engine_version": ephem.engine_version(), "ephemeris": ephem.EPHEMERIS_NAME, "time_utc": datetime.now(timezone.utc).isoformat()}

@router.post("/chart", summary="Natal chart (tropical or sidereal)")
def chart(req: ChartRequest):
    hs = req.house_system or ("whole_sign" if req.system == "sidereal" else "placidus")
    ephem.set_ayanamsa_mode(req.ayanamsa)
    return wrap(natal_chart, birth_utc(req), req.latitude, req.longitude, req.system, hs, req.true_node)

def _parse_dt(s: str | None, tz: str | None):
    if not s: return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(422, "datetime must be ISO 8601, e.g. 2026-10-10T12:00:00Z")
    return ephem.to_utc(dt, tz)

@router.get("/planets", summary="Planet positions at a moment (default now)")
def planets(datetime_: str | None = Query(None, alias="datetime", description="ISO 8601; naive = UTC unless tz given"),
            tz: str | None = None, system: str = Query("tropical", pattern="^(tropical|sidereal)$"), true_node: bool = False):
    dt = _parse_dt(datetime_, tz)
    jd = ephem.jd_from_utc(dt)
    pos = ephem.all_positions(jd, system == "sidereal", true_node)
    out = []
    for n, p in pos.items():
        s, d = ephem.sign_info(p["longitude"])
        item = {"name": n, "longitude": round(p["longitude"], 6), "sign": ephem.SIGNS[s], "degree": round(d, 6),
                "dms": ephem.dms(d), "retrograde": p["speed"] < 0, "speed": round(p["speed"], 6)}
        if system == "sidereal":
            ni, pada = ephem.nakshatra_of(p["longitude"]); item.update(nakshatra=ephem.NAKSHATRAS[ni], pada=pada)
        out.append(item)
    return {"datetime_utc": dt.isoformat(), "system": system, "ayanamsa": round(ephem.ayanamsa(jd), 6) if system == "sidereal" else None, "planets": out}

@router.get("/zodiac/{sign}", summary="Zodiac sign reference info (English or Sanskrit name)")
def zodiac(sign: str):
    z = zodiac_info(sign)
    if not z: raise HTTPException(404, f"unknown sign '{sign}'")
    return z

@router.get("/nakshatra", summary="Moon nakshatra & pada (sidereal Lahiri)")
def nakshatra(datetime_: str | None = Query(None, alias="datetime"), tz: str | None = None):
    from ...core.panchang import moon_sid
    dt = _parse_dt(datetime_, tz)
    jd = ephem.jd_from_utc(dt)
    lon = moon_sid(jd); ni, pada = ephem.nakshatra_of(lon)
    span = 360 / 27
    start, _ = ephem.next_boundary(moon_sid, jd, span, forward=False)
    end, _ = ephem.next_boundary(moon_sid, jd, span, forward=True)
    tzinfo = ephem.make_tz(tz) if tz else timezone.utc
    return {"datetime_utc": dt.isoformat(), "moon_longitude": round(lon, 6), "rashi": ephem.RASHIS[int(lon // 30)],
            "nakshatra": ephem.NAKSHATRAS[ni], "number": ni + 1, "pada": pada, "lord": ephem.NAK_LORDS[ni % 9],
            "degree_in_nakshatra": round(lon - ni * span, 6), "start": ephem.fmt(start, tzinfo), "end": ephem.fmt(end, tzinfo)}

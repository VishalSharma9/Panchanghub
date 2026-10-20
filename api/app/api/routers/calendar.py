from __future__ import annotations
from datetime import date as Date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from ...core import calendar as C
from ...core.ephem import make_tz, YEAR_MIN, YEAR_MAX, SPAN_MAX_DAYS
from ..deps import loc_params, wrap

router = APIRouter(tags=["Calendar, Festivals, Transits, Muhurat"])

@router.get("/festivals", summary="Festival & vrat calendar for a year")
def festivals(year: int = Query(..., ge=YEAR_MIN, le=YEAR_MAX), loc=Depends(loc_params), type: str | None = Query(None, description="filter by type, e.g. ekadashi")):
    r = wrap(C.year_festivals, year, loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])
    if type: r["events"] = [e for e in r["events"] if e["type"] == type]
    return r

@router.get("/calendar/month", summary="Monthly panchang calendar")
def month(year: int = Query(..., ge=YEAR_MIN, le=YEAR_MAX), month: int = Query(..., ge=1, le=12), loc=Depends(loc_params)):
    return wrap(C.month_calendar, year, month, loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/eclipses")
def eclipses(year: int = Query(..., ge=YEAR_MIN, le=YEAR_MAX), tz: str = "UTC"):
    return {"year": year, "eclipses": C.eclipses(year, make_tz(tz))}

@router.get("/transits", summary="Sign ingresses and retrograde/direct stations")
def transits(start: Date, end: Date, tz: str | None = "UTC", system: str = Query("sidereal", pattern="^(tropical|sidereal)$")):
    if end < start or (end - start).days > 3660: raise HTTPException(422, "range must be 0..10 years")
    return C.transits(start, end, tz, None, system == "sidereal")

@router.get("/muhurat", summary="Muhurat finder (marriage, griha_pravesh, vehicle, property, naming, mundan, annaprashan, business)")
def muhurat(type: str = Query(..., pattern="^(marriage|griha_pravesh|vehicle|property|naming|mundan|annaprashan|business)$"), start: Date = Query(...),
            end: Date = Query(...), loc=Depends(loc_params)):
    if start.year < YEAR_MIN or end.year < YEAR_MIN or start.year > YEAR_MAX or end.year > YEAR_MAX:
        raise HTTPException(422, f"dates must fall between {YEAR_MIN} CE and {YEAR_MAX} CE")
    if end < start or (end - start).days > SPAN_MAX_DAYS:
        raise HTTPException(422, f"one search covers up to 10 years ({SPAN_MAX_DAYS} days). Any day from {YEAR_MIN} CE through {YEAR_MAX} CE is allowed")
    return wrap(C.muhurat, type, start, end, loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

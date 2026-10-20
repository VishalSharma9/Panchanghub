from __future__ import annotations
from datetime import date as Date
from fastapi import APIRouter, Depends, Query
from ...core import panchang as P
from ..deps import loc_params, wrap

router = APIRouter(tags=["Panchang"])

def _d(d): return d or Date.today()

@router.get("/panchang", summary="Full daily panchang with exact start/end times")
def panchang(date: Date | None = None, loc=Depends(loc_params), alt: float = Query(0.0, ge=-500, le=9000),
             janma_rashi: int | None = Query(None, ge=1, le=12), janma_nakshatra: int | None = Query(None, ge=1, le=27)):
    return wrap(P.compute_panchang, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"], alt,
                janma_rashi - 1 if janma_rashi else None, janma_nakshatra - 1 if janma_nakshatra else None)

@router.get("/muhurta/daily", summary="Auspicious & inauspicious timings for the day")
def muhurta(date: Date | None = None, loc=Depends(loc_params)):
    p = wrap(P.compute_panchang, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])
    return {"date": p["date"], "sunrise": p["sunrise"], "sunset": p["sunset"], **p["muhurta"]}

@router.get("/choghadiya")
def choghadiya(date: Date | None = None, loc=Depends(loc_params)):
    return wrap(P.choghadiya, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/hora")
def hora(date: Date | None = None, loc=Depends(loc_params)):
    return wrap(P.hora, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/gowri")
def gowri(date: Date | None = None, loc=Depends(loc_params)):
    return wrap(P.gowri, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/lagna-table")
def lagna(date: Date | None = None, loc=Depends(loc_params)):
    return wrap(P.lagna_table, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/rahu-kaal")
def rahu(date: Date | None = None, loc=Depends(loc_params)):
    p = wrap(P.compute_panchang, _d(date), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])
    m = p["muhurta"]
    return {"date": p["date"], "rahu_kalam": m["rahu_kalam"], "yamaganda": m["yamaganda"], "gulikai_kalam": m["gulikai_kalam"]}

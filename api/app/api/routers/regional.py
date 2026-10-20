"""Round 4: region-specific calendars, Vakya/Surya-Siddhanta option, muhurta doshas, yoga catalogue, festival rules."""
from __future__ import annotations
from datetime import date as Date
from typing import Literal
from fastapi import APIRouter, Depends, Query
from ...core import vakya as VK, punya_kaal as PK, regional_rules as R, muhurta_doshas as MD, yogas_classical as YC, festival_rules as FR, panchang as P
from ..deps import loc_params, wrap

router = APIRouter()

@router.get("/panchang/regional/v2", tags=["Panchang"], summary="Tamil, Malayalam, Bengali, Assamese, Odia solar dates + Gujarati/Marathi/North lunisolar, with Surya-Siddhanta option")
def regional_v2(date: Date | None = None, siddhanta: Literal["drik", "surya", "vakya"] = "drik", loc=Depends(loc_params)):
    return wrap(R.regional_calendar, date or Date.today(), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"], siddhanta)

@router.get("/festivals/regional-new-years", tags=["Calendar"], summary="Puthandu, Vishu, Pohela Boishakh, Bohag Bihu, Pana Sankranti, Thai Pongal, Chingam 1")
def new_years(year: int = Query(..., ge=1, le=3000), siddhanta: Literal["drik", "surya", "vakya"] = "drik", loc=Depends(loc_params)):
    return wrap(R.regional_new_years, year, loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"], siddhanta)

@router.get("/festivals/rules", tags=["Calendar"], summary="Festival determination rules (Nirnayasindhu / Dharmasindhu) incl. Smarta vs Vaishnava")
def festival_rules():
    return {"rules": FR.RULES}

@router.get("/muhurta/doshas", tags=["Muhurta"], summary="Panchaka & Panchaka-rahita, Bhadra residence, Dagdha tithi, Krakacha/Samvartaka, Gand-mool, Tarabala/Chandrabala detail")
def doshas(date: Date | None = None, janma_nakshatra: int | None = Query(None, ge=1, le=27), janma_rashi: int | None = Query(None, ge=1, le=12), loc=Depends(loc_params)):
    return wrap(MD.day_doshas, date or Date.today(), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"], janma_nakshatra, janma_rashi)

@router.get("/yogas/catalog", tags=["Kundli"], summary="All yoga rules detected by the engine, with classical citations")
def yoga_catalog():
    return YC.catalog()

@router.get("/muhurta/godhuli", tags=["Muhurta"], summary="Godhuli muhurta with the seasonal Muhurta-Chintamani rule")
def godhuli(date: Date | None = None, loc=Depends(loc_params)):
    p = wrap(P.compute_panchang, date or Date.today(), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])
    g = (p.get("muhurtas") or p.get("muhurta") or {}).get("godhuli_muhurta")
    return {"date": (date or Date.today()).isoformat(), "godhuli": g, "rules": P.GODHULI_RULE,
            "source": "Muhurta Chintamani, Vivaha-prakarana v.98 (hemanta: disc still round above horizon; grishma: half-set; varsha: fully set); ends half a night-muhurta after sunset"}


@router.get("/panchang/vakya", tags=["Panchang"], summary="Vakya panchang: tithi, nakshatra, yoga, karana by Vararuci Chandravakyas + Vakya Sun (with Drik side-by-side)")
def panchang_vakya(date: Date | None = None, loc=Depends(loc_params)):
    return wrap(VK.vakya_panchang, date or Date.today(), loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

@router.get("/vakya/sankranti", tags=["Panchang"], summary="Vakya sankranti moments for a year vs Drik")
def vakya_sankranti(year: int = Query(..., ge=1, le=3000), tz: str = "Asia/Kolkata"):
    return wrap(VK.sankranti, year, tz, None)

@router.get("/vakya/chandravakyas", tags=["Panchang"], summary="The 248 Chandravakyas (reconstructed, arc-minutes) and Vakya constants")
def chandravakyas():
    v = VK.chandravakyas()
    return {"count": len(v), "vakyas": [{"n": i + 1, "arcmin": x, "value": VK.fmt_vakya(x)} for i, x in enumerate(v)],
            "constants": {"khanda_kalidina": VK.KHANDA, "anomalistic_cycle_days": VK.CYCLE, "dhruva_per_cycle_deg": VK.DHRUVA_PER_CYCLE,
                          "moon_at_epoch_deg": VK.MOON_AT_EPOCH, "moon_epicycle": "31.5 deg", "sun_year_days": VK.SUN_YEAR}}

@router.get("/sankranti/punya-kaal", tags=["Calendar"], summary="Punya kaal & Maha punya kaal for every sankranti of a year (Dharmasindhu/Nirnayasindhu rules)")
def punya(year: int = Query(..., ge=1, le=3000), loc=Depends(loc_params)):
    return wrap(PK.year_punya_kaal, year, loc["lat"], loc["lon"], loc["tz"], loc["utc_offset"])

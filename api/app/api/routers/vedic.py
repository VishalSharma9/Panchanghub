from __future__ import annotations
from fastapi import APIRouter
from ...models import KundliRequest, MatchRequest
from ...core import ephem
from ...core.kundli import compute_kundli
from ...core.matching import ashtakoota, porutham
from ...core.panchang import moon_sid
from ..deps import birth_utc, wrap

router = APIRouter(tags=["Kundli & Matching"])
HS = {"whole_sign": "W", "placidus": "P", "equal": "E"}

@router.post("/kundli", summary="Vedic birth chart: lagna, planets, D1–D60, dashas, ashtakavarga, doshas, yogas")
def kundli(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    k = wrap(compute_kundli, birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
             req.true_node, req.dasha_levels, HS[req.house_system])
    k["name"] = req.name
    return k

@router.post("/matching", summary="Ashtakoota (36 guna) + 10 Porutham matching")
def matching(req: MatchRequest):
    b = moon_sid(ephem.jd_from_utc(birth_utc(req.boy))); g = moon_sid(ephem.jd_from_utc(birth_utc(req.girl)))
    return {"ashtakoota": ashtakoota(b, g), "porutham": porutham(b, g)}

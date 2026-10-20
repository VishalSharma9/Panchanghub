from __future__ import annotations
from datetime import datetime
from fastapi import HTTPException, Query
from ..models import valid_tz
from ..core.ephem import make_tz, to_utc

def loc_params(lat: float = Query(..., ge=-90, le=90, description="Latitude", examples=[28.6139]),
               lon: float = Query(..., ge=-180, le=180, description="Longitude", examples=[77.209]),
               tz: str | None = Query(None, description="IANA timezone", examples=["Asia/Kolkata"]),
               utc_offset: float | None = Query(None, ge=-14, le=14, description="UTC offset hours if tz omitted")):
    if tz:
        try: valid_tz(tz)
        except ValueError as e: raise HTTPException(422, str(e))
    elif utc_offset is None:
        tz = "UTC"
    return {"lat": lat, "lon": lon, "tz": tz, "utc_offset": utc_offset}

def birth_utc(b):
    dt = datetime.combine(b.date, b.time)
    return to_utc(dt, b.timezone, b.utc_offset)

def wrap(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except ValueError as e:
        raise HTTPException(422, str(e))

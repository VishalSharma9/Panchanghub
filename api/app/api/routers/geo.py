from __future__ import annotations
import json, os, re, sqlite3, unicodedata
from functools import lru_cache
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(tags=["Geo"])
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
SQLITE = os.path.join(ROOT, "places.sqlite")
JSON = os.path.join(ROOT, "cities.json")

def _n(s: str) -> str:
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()

@lru_cache(maxsize=1)
def _json_cities():
    return json.load(open(JSON, encoding="utf8"))

def _db():
    if not os.path.exists(SQLITE):
        return None
    con = sqlite3.connect(f"file:{SQLITE}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

_CON = None
def conn():
    global _CON
    if _CON is None:
        _CON = _db()
    return _CON

def _format_name(c, q: str | None = None) -> str:
    orig_name = c["name"]
    if not q:
        return orig_name
    qn = _n(q)
    name_n = _n(orig_name)
    ascii_n = _n(c["ascii"])

    if qn == name_n or qn == ascii_n or name_n.startswith(qn) or ascii_n.startswith(qn):
        return orig_name

    alts = [x.strip() for x in (c["alt"] or "").split(",") if x.strip()]
    matched_alt = None
    for a in alts:
        if _n(a) == qn:
            matched_alt = a
            break
    if not matched_alt:
        for a in alts:
            if _n(a).startswith(qn):
                matched_alt = a
                break

    if matched_alt:
        if _n(matched_alt) == ascii_n or _n(matched_alt) == name_n:
            return matched_alt
        return f"{matched_alt} ({orig_name})"

    return orig_name

def _row(c, q: str | None = None):
    name = _format_name(c, q)
    return {"name": name, "country": c["cc"], "country_name": c["country"],
            "admin1": c["admin"], "admin1_name": c["admin_name"],
            "latitude": c["lat"], "longitude": c["lon"], "timezone": c["tz"],
            "population": c["pop"], "feature": c["fcode"]}

def _fts_query(q: str) -> str | None:
    parts = re.findall(r"[\w]+", q, flags=re.UNICODE)
    if not parts:
        return None
    bits = [f'"{p}"' for p in parts[:-1]]
    bits.append(f'"{parts[-1]}"*')
    return " AND ".join(bits)

def _rank(q, rows):
    """Prefer the real city over a hamlet that happens to share a prefix, checking primary names and aliases."""
    qn = _n(q)
    def key(c):
        a, name = _n(c["ascii"]), _n(c["name"])
        pop = c["pop"] or 0
        alts = [_n(x) for x in (c["alt"] or "").split(",") if x.strip()]
        if a == qn or name == qn or qn in alts:
            boost = 50
        elif a.startswith(qn) or name.startswith(qn) or any(x.startswith(qn) for x in alts):
            boost = 8
        else:
            boost = 1
        return -(pop * boost)
    return sorted(rows, key=key)

@router.get("/cities", summary="City and town search — global populated places atlas")
def search(q: str = Query(..., min_length=2, max_length=80), limit: int = Query(12, ge=1, le=50)):
    db = conn()
    if db is None:
        qn = _n(q)
        out = []
        for name, cc, adm, lat, lon, tz, pop in _json_cities():
            if _n(name).startswith(qn):
                out.append({"name": name, "country": cc, "admin1": adm, "latitude": lat, "longitude": lon, "timezone": tz, "population": pop})
            if len(out) >= limit:
                break
        return {"query": q, "results": out}
    match = _fts_query(q)
    rows = []
    if match:
        try:
            rows = db.execute(
                """SELECT p.* FROM places_fts f JOIN places p ON p.id = f.rowid
                   WHERE places_fts MATCH ? ORDER BY p.pop DESC LIMIT 60""",
                (match,)).fetchall()
        except sqlite3.OperationalError:
            rows = []
    picked = _rank(q, rows)[:limit]
    return {"query": q, "results": [_row(c, q) for c in picked]}

@router.get("/cities/nearest", summary="Nearest populated place to coordinates")
def nearest(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    db = conn()
    if db is None:
        best = min(_json_cities(), key=lambda c: (c[3] - lat) ** 2 + ((c[4] - lon) * 0.7) ** 2)
        name, cc, adm, la, lo, tz, pop = best
        return {"name": name, "country": cc, "admin1": adm, "latitude": la, "longitude": lo, "timezone": tz, "population": pop}
    def cell(la, lo):
        return min(719, max(0, int((la + 90) * 4))) * 1440 + int((lo + 180) * 4) % 1440
    best, best_d = None, 1e9
    for ring in (1, 2, 4, 8, 16):
        cells = []
        for dy in range(-ring, ring + 1):
            for dx in range(-ring, ring + 1):
                if ring > 1 and abs(dy) < ring and abs(dx) < ring:
                    continue
                la = min(719, max(0, int((lat + 90) * 4) + dy))
                lo = (int((lon + 180) * 4) + dx) % 1440
                cells.append(la * 1440 + lo)
        qmarks = ",".join("?" * len(cells))
        for c in db.execute(f"SELECT * FROM places WHERE cell IN ({qmarks})", cells):
            d = (c["lat"] - lat) ** 2 + ((c["lon"] - lon) * 0.7) ** 2
            if d < best_d:
                best, best_d = c, d
        if best is not None and ring >= 1:
            break
    if best is None:
        best = db.execute("SELECT * FROM places ORDER BY pop DESC LIMIT 1").fetchone()
    return _row(best)

@router.get("/cities/timezone", summary="Largest populated place in an IANA timezone")
def by_timezone(tz: str = Query(..., min_length=1, max_length=80)):
    tz = tz.strip()
    db = conn()
    if db is None:
        best = None
        for name, cc, adm, lat, lon, zone, pop in _json_cities():
            if zone == tz and (best is None or pop > best[6]):
                best = (name, cc, adm, lat, lon, zone, pop)
        if best is None:
            raise HTTPException(404, "No place in that timezone")
        name, cc, adm, lat, lon, zone, pop = best
        return {"name": name, "country": cc, "admin1": adm, "latitude": lat, "longitude": lon, "timezone": zone, "population": pop}
    row = db.execute("SELECT * FROM places WHERE tz=? ORDER BY pop DESC LIMIT 1", (tz,)).fetchone()
    if row is None:
        raise HTTPException(404, "No place in that timezone")
    return _row(row)

@router.get("/cities/stats", summary="How many places the search covers")
def stats():
    db = conn()
    if db is None:
        return {"count": len(_json_cities()), "source": "bundled subset"}
    n = db.execute("SELECT COUNT(*) FROM places").fetchone()[0]
    return {"count": n, "source": "Global Populated Places Atlas, excluding historical, abandoned and destroyed"}

from __future__ import annotations
import importlib, json
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from . import api

BRAND = "PanchangHub"
app = FastAPI(
    title=f"{BRAND} Astrology API",
    version="1.0.0",
    description=("Vedic-first astrology & panchang REST API powered by the Swiss Ephemeris. "
                 "Sidereal Lahiri (calibrated to canonical Drik astronomical standards) by default, tropical Western charts too. "
                 "Add `?lang=hi|mr|gu|bn|ta|te|kn|ml` to any endpoint for localized names. Website: https://panchanghub.com"),
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json",
)
@app.middleware("http")
async def lang_middleware(request, call_next):
    """`?lang=hi|mr|gu|bn|ta|te|kn|ml` on any JSON endpoint translates names/labels to that language."""
    lang = request.query_params.get("lang")
    resp = await call_next(request)
    if not lang or lang == "en" or not resp.headers.get("content-type", "").startswith("application/json"):
        return resp
    from .core import i18n
    if lang not in i18n.MAPS:
        return resp
    body = b"".join([c async for c in resp.body_iterator])
    try:
        data = i18n.translate(json.loads(body), lang)
    except Exception:
        return Response(body, status_code=resp.status_code, media_type="application/json")
    headers = {k: v for k, v in resp.headers.items() if k.lower() not in ("content-length", "content-type")}
    headers["content-language"] = lang
    return JSONResponse(data, status_code=resp.status_code, headers=headers)

@app.middleware("http")
async def geo_policy(request, call_next):
    resp = await call_next(request)
    resp.headers["Permissions-Policy"] = "geolocation=(self)"
    return resp

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

for name in api.ROUTERS:
    mod = importlib.import_module(f".api.routers.{name}", __package__)
    app.include_router(mod.router, prefix="/api")
    if name in api.ROOT_ALIASES:
        app.include_router(mod.router, include_in_schema=False)

try:
    from .web import register
    register(app)
except ImportError:  # API-only deployment
    pass

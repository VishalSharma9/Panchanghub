from __future__ import annotations
import importlib, json
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from . import api
from .core.cleanslate import alias_query, cleanslate_text

BRAND = "PanchangHub"
app = FastAPI(
    title=f"{BRAND} Astrology API",
    version="1.0.0",
    description=(f"Vedic-first astrology and panchang REST API by {BRAND}. "
                 "Sidereal Lahiri by default, tropical Western charts too. "
                 "Add `?lang=hi|mr|gu|bn|ta|te|kn|ml` to any endpoint for localized names. "
                 "Website: https://panchanghub.com"),
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json",
)

def _media(resp) -> str:
    return (resp.headers.get("content-type") or resp.media_type or "").lower()

async def _apply_cleanslate(resp):
    ctype = _media(resp)
    if "json" not in ctype and not ctype.startswith("text/html") and not ctype.startswith("text/plain"):
        return resp
    body = b"".join([c async for c in resp.body_iterator])
    try:
        text = body.decode("utf-8")
    except Exception:
        headers = {k: v for k, v in resp.headers.items() if k.lower() != "content-length"}
        return Response(body, status_code=resp.status_code, headers=headers, media_type=resp.media_type)
    cleaned = cleanslate_text(text)
    raw = cleaned.encode("utf-8")
    headers = {k: v for k, v in resp.headers.items() if k.lower() != "content-length"}
    return Response(raw, status_code=resp.status_code, headers=headers, media_type=resp.media_type)

@app.middleware("http")
async def lang_middleware(request, call_next):
    """`?lang=hi|mr|gu|bn|ta|te|kn|ml` on any JSON endpoint translates names/labels to that language."""
    lang = request.query_params.get("lang")
    resp = await call_next(request)
    if not lang or lang == "en" or "json" not in _media(resp):
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

@app.middleware("http")
async def cleanslate_middleware(request, call_next):
    qs = request.scope.get("query_string") or b""
    rewritten = alias_query(qs)
    if rewritten != qs:
        request.scope["query_string"] = rewritten
    resp = await call_next(request)
    return await _apply_cleanslate(resp)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(Exception)
async def _no_foreign_trace(request: Request, exc: Exception):
    """Engine errors must not quote another library or product in the body."""
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse({"detail": "PanchangHub could not compute that request."}, status_code=500)

@app.middleware("http")
async def head_as_get(request, call_next):
    if request.method != "HEAD":
        return await call_next(request)
    request.scope["method"] = "GET"
    resp = await call_next(request)
    headers = {k: v for k, v in resp.headers.items() if k.lower() != "content-length"}
    return Response(status_code=resp.status_code, headers=headers, media_type=resp.media_type)

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

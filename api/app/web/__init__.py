"""PanchangHub website: server-rendered Jinja pages that call the API handlers in-process (same code path as /api),
plus client JS that calls the public /api endpoints (city search, geolocation, SVG, PDF)."""
from __future__ import annotations
import json, os
from datetime import date as Date, datetime, timedelta, timezone
from urllib.parse import unquote, urlencode
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..models import BirthData, KundliRequest, MatchRequest, ChartRequest, VarshaphalaRequest, KPRequest, PrashnaRequest
from ..models import normalize_date_str
from ..api.routers import panchang as RP, vedic as RV, calendar as RC, core as RCore, extras as RX
from ..core import ephem, i18n
from ..api.routers import more as RM
from ..api.routers import studio as ST
from ..core import interpret as INTERP, esoteric as ESO, human_design as HDM
import re as _re
from ..core.for_you import for_you, syllable, moon_syllable
from ..core.kundli import sade_sati
from ..core.ephem import RASHIS
from ..core.charts_svg import north_indian, south_indian, east_indian, western_wheel

# Two layouts, one code path:
#   live tree:  <project>/app/web/__init__.py  and  <project>/web/{templates,static}
#   zip bundle: <bundle>/api/app/web/__init__.py  and  <bundle>/website/{templates,static}
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PARENT = os.path.dirname(_APP_DIR)
_BUNDLE = os.path.dirname(_PARENT)
if os.path.isdir(os.path.join(_BUNDLE, "website", "templates")):
    ROOT = _BUNDLE
    WEB_ROOT = os.path.join(_BUNDLE, "website")
else:
    ROOT = _PARENT
    WEB_ROOT = os.path.join(_PARENT, "web")
SITE = "https://panchanghub.com"
BRAND = "PanchangHub"
templates = Jinja2Templates(directory=os.path.join(WEB_ROOT, "templates"))
DEFAULT_LOC = {"city": "New Delhi, India", "lat": 28.6139, "lon": 77.209, "tz": "Asia/Kolkata"}

def _parse_iso(s):
    return datetime.fromisoformat(s) if s else None

def hm(s, ref: str | None = None):
    """'2026-10-10T21:19:32+05:30' -> '09:20 PM' (+ ', Oct 11' when on another day)."""
    if not s: return "—"
    d = _parse_iso(s)
    d = (d + timedelta(seconds=30)).replace(second=0, microsecond=0)
    out = d.strftime("%I:%M %p")
    if ref and d.date().isoformat() != ref[:10]:
        out += d.strftime(", %B %d")
    return out

def dt_ampm(s):
    if not s:
        return "—"
    try:
        d = _parse_iso(str(s))
        d = (d + timedelta(seconds=30)).replace(second=0, microsecond=0)
        return f"{d.date().isoformat()} {d.strftime('%I:%M %p')}"
    except Exception:
        return str(s)

def span(item, ref):
    return f"{hm(item.get('start'), ref)} – {hm(item.get('end'), ref)}" if item else "—"

templates.env.filters["hm"] = hm
templates.env.filters["dt_ampm"] = dt_ampm
templates.env.globals.update(span=span, BRAND=BRAND, SITE=SITE, SIGNS=ephem.SIGNS, RASHIS=ephem.RASHIS, NAKSHATRAS=ephem.NAKSHATRAS)

def loc_from(request: Request):
    q = request.query_params
    if "lat" in q and "lon" in q:
        try:
            return {"city": q.get("city", f"{float(q['lat']):.3f}, {float(q['lon']):.3f}"), "lat": float(q["lat"]),
                    "lon": float(q["lon"]), "tz": q.get("tz", "UTC"), "source": "query"}
        except ValueError:
            pass
    c = request.cookies.get("ph_loc")
    if c:
        try:
            v = json.loads(c); return {"city": v["city"], "lat": float(v["lat"]), "lon": float(v["lon"]), "tz": v["tz"], "source": v.get("src") or "saved"}
        except Exception:
            pass
    loc = dict(DEFAULT_LOC)
    loc["source"] = "default"
    return loc

def L(loc):
    return {"lat": loc["lat"], "lon": loc["lon"], "tz": loc["tz"], "utc_offset": None}

def qdate(request, key="date"):
    v = request.query_params.get(key)
    try:
        d = Date.fromisoformat(v) if v else Date.today()
    except ValueError:
        return Date.today()
    if d.year < ephem.YEAR_MIN or d.year > ephem.YEAR_MAX:
        raise HTTPException(422, f"Choose a date from {ephem.YEAR_MIN} CE through {ephem.YEAR_MAX} CE.")
    return d

def neighbor(d: Date, days: int):
    try:
        n = d + timedelta(days=days)
    except OverflowError:
        return None
    if n.year < ephem.YEAR_MIN or n.year > ephem.YEAR_MAX:
        return None
    return n.isoformat()

def _opt_int(v, lo, hi):
    if v is None or v == "": return None
    try: n = int(v)
    except (TypeError, ValueError): return None
    return n if lo <= n <= hi else None

def janma_from(request):
    q = request.query_params
    if "janma_rashi" in q or "janma_nakshatra" in q:
        return _opt_int(q.get("janma_rashi"), 1, 12), _opt_int(q.get("janma_nakshatra"), 1, 27), True
    c = request.cookies.get("ph_janma")
    if c:
        try:
            v = json.loads(c)
            return _opt_int(v.get("rashi"), 1, 12), _opt_int(v.get("nak"), 1, 27), False
        except Exception:
            pass
    return None, None, False

def loc2_from(request):
    q = request.query_params
    if q.get("lat2") and q.get("lon2"):
        try:
            return {"city": q.get("city2") or "Other place", "lat": float(q["lat2"]), "lon": float(q["lon2"]),
                    "tz": q.get("tz2") or "UTC"}, True
        except ValueError:
            pass
    c = request.cookies.get("ph_loc2")
    if c:
        try:
            v = json.loads(c)
            return {"city": v["city"], "lat": float(v["lat"]), "lon": float(v["lon"]), "tz": v["tz"]}, False
        except Exception:
            pass
    return None, False

def _ics_text(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", " ")

def festivals_ics(events, city: str) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//PanchangHub//EN", "CALSCALE:GREGORIAN",
             f"X-WR-CALNAME:{_ics_text('PanchangHub ' + city)}"]
    for e in events:
        ds = e["date"].replace("-", "")
        name = _ics_text(e["name"])
        lines += ["BEGIN:VEVENT", f"UID:{ds}-{name}@panchanghub", f"DTSTART;VALUE=DATE:{ds}",
                  f"SUMMARY:{name}", f"DESCRIPTION:{_ics_text(e.get('type') or '')} · {_ics_text(city)}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"

def _with_cookie(resp, key, payload):
    resp.set_cookie(key, json.dumps(payload), max_age=31536000, path="/", samesite="lax")
    return resp

def year_of(request):
    try:
        y = int(request.query_params.get("year", Date.today().year))
    except ValueError:
        y = Date.today().year
    if y < ephem.YEAR_MIN or y > ephem.YEAR_MAX:
        raise HTTPException(422, f"Years run from {ephem.YEAR_MIN} CE through {ephem.YEAR_MAX} CE.")
    return y

def lang_of(request):
    l = request.query_params.get("lang") or request.cookies.get("ph_lang") or "en"
    return l if l in i18n.LANGS else "en"

_TERMS = {}
def _term_re(lang):
    if lang not in _TERMS:
        keys = sorted(i18n.MAPS[lang], key=len, reverse=True)
        _TERMS[lang] = _re.compile(r"(?<![A-Za-z])(" + "|".join(_re.escape(k) for k in keys) + r")(?![A-Za-z])")
    return _TERMS[lang]

def localize_html(html: str, lang: str) -> str:
    """Translate every visible string. Scripts stay untouched. Language names stay as written."""
    if lang == "en": return html
    import re as _re2
    locked = []
    def hold(m):
        locked.append(m.group(0))
        return f"<!--PHLOCK{len(locked)-1}-->"
    html = _re2.sub(r'<span id="langSwitch">.*?</span>', hold, html, count=1, flags=_re2.S)
    from ..core.ui_lang import translate_plain
    def plain(text):
        out = translate_plain(text, lang)
        if out == text:
            return text
        return out.replace("&", "&").replace("<", "<").replace(">", ">")
    def tag(part):
        if part.startswith("<script") or part.startswith("<style") or part.startswith("<textarea"):
            return part
        def attr(mm):
            val = plain(mm.group(2)).replace(chr(34), chr(38) + "quot;")
            return f'{mm.group(1)}="{val}"'
        return _re.sub(r'(placeholder|aria-label|title|alt)="([^"]*)"', attr, part)
    parts = _re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<textarea\b.*?</textarea>|<[^>]+>)", html, flags=_re.S | _re.I)
    for i, part in enumerate(parts):
        if not part: continue
        parts[i] = tag(part) if part.startswith("<") else plain(part)
    out = "".join(parts)
    for i, chunk in enumerate(locked):
        out = out.replace(f"<!--PHLOCK{i}-->", chunk)
    return out

def page(request, tpl, title, desc, path, **ctx):
    from ..core.ui_lang import client_pack, translate_plain
    loc = ctx.pop("loc", None) or loc_from(request)
    lang = lang_of(request)
    if lang != "en":
        title = translate_plain(title, lang)
        desc = translate_plain(desc, lang)
    resp = templates.TemplateResponse(request, tpl, {"title": title, "desc": desc, "canonical": SITE + path, "lang": lang, "LANGS": i18n.LANGS,
                                                     "path": path, "loc": loc, "locq": urlencode({"city": loc["city"], "lat": loc["lat"], "lon": loc["lon"], "tz": loc["tz"], **({"lang": lang} if lang != "en" else {})}),
                                                     "ui_pack": client_pack(lang), "ui_json": json.dumps(client_pack(lang), ensure_ascii=False), **ctx})
    if lang == "en":
        resp.delete_cookie("ph_lang", path="/")
    else:
        body = localize_html(resp.body.decode(), lang)
        resp = HTMLResponse(body, status_code=resp.status_code, headers={"Content-Language": lang})
        resp.set_cookie("ph_lang", lang, max_age=31536000, path="/", samesite="lax")
    if getattr(request.state, "ph_birth_to_save", None):
        resp.set_cookie("ph_birth", json.dumps(request.state.ph_birth_to_save), max_age=31536000, path="/", samesite="lax")
    return resp

NAV = [("/", "Home"), ("/mine", "For You"), ("/week", "This Week"), ("/compare", "Two Cities"),
       ("/names", "Names"), ("/sade-sati", "Sade Sati"), ("/panchang", "Daily Panchang"),
       ("/calendar", "Calendar"), ("/festivals", "Festivals"), ("/choghadiya", "Choghadiya"),
       ("/kundli", "Kundli"), ("/reports", "Detailed Reports & 22 Dashas"), ("/destiny", "Destiny"), ("/traditions", "Traditions"), ("/vargas", "Vargas"),
       ("/varshaphala", "Varshaphala"), ("/kp", "KP"), ("/prashna", "Prashna"), ("/yogas", "Yogas"), ("/reading", "Reading"),
       ("/matching", "Matching"), ("/muhurat", "Muhurat"),
       ("/hora", "Hora"), ("/rahu-kaal", "Rahu Kaal"), ("/lagna-table", "Lagna & Gowri"), ("/transits", "Transits"),
       ("/western", "Western Chart"), ("/horoscope", "Horoscope"), ("/numerology", "Numerology"), ("/tarot", "Tarot"),
       ("/human-design", "Human Design"), ("/vastu", "Vastu"), ("/iching", "I-Ching"), ("/palmistry", "Palmistry"), ("/tools", "More Tools"), ("/regional", "Regional Calendars")]
templates.env.globals["NAV"] = NAV

def _resolve_city_coords(city_str: str, lat: float, lon: float, tz: str):
    if not city_str or len(city_str.strip()) < 2:
        return city_str, lat, lon, tz
    try:
        from ..api.routers import geo as RGeo
        q_clean = city_str.split(",")[0].strip()
        if len(q_clean) >= 2:
            res = RGeo.search(q=q_clean, limit=1).get("results", [])
            if res:
                top = res[0]
                if abs(top["latitude"] - lat) > 0.5 or abs(top["longitude"] - lon) > 0.5:
                    full_label = ", ".join(x for x in (top.get("name"), top.get("admin1_name"), top.get("country_name") or top.get("country")) if x)
                    return full_label or city_str, float(top["latitude"]), float(top["longitude"]), top.get("timezone") or tz
    except Exception:
        pass
    return city_str, lat, lon, tz

def _read_birth_cookie(request):
    c = request.cookies.get("ph_birth")
    if not c:
        return None
    try:
        raw = unquote(c) if "%" in c else c
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        v = json.loads(raw)
        if not v.get("date"):
            return None
        fixed = normalize_date_str(v["date"], default=None)
        if not fixed:
            return None
        v["date"] = fixed
        v["bad_date"] = False
        v["name"] = (v.get("name") or "").strip()
        return v
    except Exception:
        return None


def birth_from_query(request, prefix="", fallback=False):
    """Birth details for this session.

    A page updates the saved birth only when the user actually submitted one
    (their name, or a birth form). A panchang day or a city change must not
    replace it, and the sample person is never filled in for them.
    """
    q = request.query_params
    g = lambda k, d=None: q.get(prefix + k, d)
    raw_date = g("date") or g("dob")
    raw_name = (g("name") or "").strip()
    has_place = bool(g("lat") or g("city") or g("tz"))
    explicit = bool(raw_name) or g("save_birth") == "1" or bool(raw_date and g("time") and has_place) or (prefix in ("b_", "g_") and bool(raw_date and has_place))
    saved = _read_birth_cookie(request) if prefix in ("", "b_") else None
    if explicit and raw_date:
        tm = g("time") or (saved or {}).get("time") or ""
        if tm and len(tm) == 5:
            tm += ":00"
        lat_raw = g("lat")
        lon_raw = g("lon")
        if lat_raw is None and saved and saved.get("latitude") is not None:
            lat_raw = str(saved["latitude"])
            lon_raw = lon_raw if lon_raw is not None else str(saved.get("longitude") or "")
        city_in = g("city") or (saved.get("city") if saved else "") or ""
        tz_in = g("tz") or (saved.get("timezone") if saved else "") or ""
        lat_f = float(lat_raw) if lat_raw not in (None, "") else None
        lon_f = float(lon_raw) if lon_raw not in (None, "") else None
        if lat_f is not None and lon_f is not None:
            city_s, lat_f, lon_f, tz_s = _resolve_city_coords(city_in, lat_f, lon_f, tz_in or "Asia/Kolkata")
        else:
            city_s, tz_s = city_in, tz_in
        clean = normalize_date_str(raw_date, default=None)
        name = raw_name
        if not name and saved and saved.get("date") == (clean or raw_date):
            name = saved.get("name") or ""
        res = dict(date=clean or raw_date, time=tm, latitude=lat_f, longitude=lon_f,
                   timezone=tz_s or None, name=name, city=city_s, bad_date=clean is None)
        if prefix in ("", "b_") and clean and (name or g("save_birth") == "1"):
            payload = {k: v for k, v in res.items() if k != "bad_date" and v is not None}
            try:
                request.state.ph_birth_to_save = payload
            except Exception:
                pass
        return res
    if saved:
        return saved
    if fallback and prefix == "g_":
        return dict(date="1992-08-20", time="14:15:00", latitude=19.0760, longitude=72.8777,
                    timezone="Asia/Kolkata", name="Gargi", city="Mumbai, India", bad_date=False)
    if fallback:
        return dict(date="1990-05-15", time="10:30:00", latitude=28.6139, longitude=77.2090,
                    timezone="Asia/Kolkata", name="Aryabhata", city="New Delhi, India", bad_date=False)
    return None


def _chartable(b):
    return bool(b and b.get("date") and b.get("time") and b.get("timezone") and b.get("latitude") is not None and b.get("longitude") is not None and not b.get("bad_date"))


def register(app: FastAPI):
    app.mount("/static", StaticFiles(directory=os.path.join(WEB_ROOT, "static")), name="static")

    @app.exception_handler(HTTPException)
    async def html_errors(request: Request, exc: HTTPException):
        path = request.url.path
        if path.startswith("/api") or path.startswith("/static"):
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        accept = request.headers.get("accept", "")
        if "text/html" not in accept and "*/*" not in accept and accept:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        resp = page(request, "error.html", "Out of range", str(exc.detail), path, msg=str(exc.detail))
        resp.status_code = exc.status_code
        return resp

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home(request: Request):
        loc = loc_from(request); d = Date.today()
        jr, jn, _ = janma_from(request)
        place = "your location" if loc.get("source") == "default" else loc["city"]
        p = RP.panchang(d, L(loc), 0.0, jr, jn); ch = RP.choghadiya(d, L(loc))
        fest = RC.festivals(d.year, L(loc), None)["events"]
        upcoming = [e for e in fest if e["date"] >= d.isoformat()][:10]
        return page(request, "home.html", f"{BRAND} – Today's Panchang, Choghadiya, Kundli & Hindu Calendar",
                    f"Accurate daily Panchang for {place}: tithi, nakshatra, yoga, karana, sunrise, Rahu Kaal, Choghadiya and festivals.",
                    "/", loc=loc, p=p, ch=ch, upcoming=upcoming, d=d, jr=jr, jn=jn,
                    prev=neighbor(d, -1), next=neighbor(d, 1))

    @app.get("/mine", response_class=HTMLResponse, include_in_schema=False)
    def mine(request: Request):
        loc = loc_from(request); d = qdate(request)
        jr, jn, explicit = janma_from(request)
        p = RP.panchang(d, L(loc), 0.0, jr, jn)
        ch = RP.choghadiya(d, L(loc))
        now = datetime.now(ephem.make_tz(loc["tz"]))
        now_iso = now.isoformat(timespec="seconds") if now.date() == d else None
        you = for_you(p, ch, None if jr is None else jr - 1, None if jn is None else jn - 1, now_iso)
        extra = {"city": loc["city"], "lat": loc["lat"], "lon": loc["lon"], "tz": loc["tz"]}
        if jr: extra["janma_rashi"] = jr
        if jn: extra["janma_nakshatra"] = jn
        resp = page(request, "mine.html", f"For you – {d.isoformat()} | {BRAND}",
                    "Today’s choghadiya marked for your janma rashi and nakshatra.",
                    "/mine", loc=loc, p=p, d=d, you=you, jr=jr, jn=jn,
                    prev=neighbor(d, -1), next=neighbor(d, 1), locq=urlencode(extra))
        if explicit:
            _with_cookie(resp, "ph_janma", {"rashi": jr, "nak": jn})
        return resp

    @app.get("/compare", response_class=HTMLResponse, include_in_schema=False)
    def compare(request: Request):
        loc = loc_from(request); d = qdate(request)
        loc2, explicit = loc2_from(request)
        p = RP.panchang(d, L(loc), 0.0, None, None)
        p2 = RP.panchang(d, L(loc2), 0.0, None, None) if loc2 else None
        extra = {"city": loc["city"], "lat": loc["lat"], "lon": loc["lon"], "tz": loc["tz"]}
        if loc2:
            extra.update(city2=loc2["city"], lat2=loc2["lat"], lon2=loc2["lon"], tz2=loc2["tz"])
        resp = page(request, "compare.html", f"Two cities – {d.isoformat()} | {BRAND}",
                    "Panchang for two places on the same day, so sunrise tithi and Rahu Kalam can be compared.",
                    "/compare", loc=loc, loc2=loc2, p=p, p2=p2, d=d,
                    prev=neighbor(d, -1), next=neighbor(d, 1), locq=urlencode(extra))
        if explicit and loc2:
            _with_cookie(resp, "ph_loc2", loc2)
        return resp

    @app.get("/names", response_class=HTMLResponse, include_in_schema=False)
    def names(request: Request):
        loc = loc_from(request)
        b = birth_from_query(request, fallback=False)
        q = request.query_params
        syl = None
        nak, pada = _opt_int(q.get("nak"), 1, 27), _opt_int(q.get("pada"), 1, 4)
        if b and not b.get("bad_date"):
            syl = moon_syllable(b["date"], b["time"], b["timezone"])
        elif nak and pada and not q.get("date"):
            syl = syllable(nak - 1, pada)
        return page(request, "names.html", f"Naming syllable | {BRAND}",
                    "Namakarana starting syllable from the Moon’s nakshatra pada.",
                    "/names", loc=loc, b=b, syl=syl, nak=nak, pada=pada or 1)

    @app.get("/week", response_class=HTMLResponse, include_in_schema=False)
    def week(request: Request):
        loc = loc_from(request); d0 = qdate(request)
        jr, jn, explicit = janma_from(request)
        tz = ephem.make_tz(loc["tz"])
        today = datetime.now(tz).date()
        rows = []
        for k in range(7):
            try:
                d = d0 + timedelta(days=k)
            except OverflowError:
                break
            if d.year > ephem.YEAR_MAX:
                break
            p = RP.panchang(d, L(loc), 0.0, jr, jn)
            ch = RP.choghadiya(d, L(loc))
            now_iso = datetime.now(tz).isoformat(timespec="seconds") if d == today else None
            you = for_you(p, ch, None if jr is None else jr - 1, None if jn is None else jn - 1, now_iso)
            rows.append({"d": d, "p": p, "you": you})
        extra = {"city": loc["city"], "lat": loc["lat"], "lon": loc["lon"], "tz": loc["tz"]}
        if jr: extra["janma_rashi"] = jr
        if jn: extra["janma_nakshatra"] = jn
        resp = page(request, "week.html", f"This week – {loc['city']} | {BRAND}",
                    "Seven days of tithi, Rahu Kalam, Abhijit and the next clean hour for your birth star.",
                    "/week", loc=loc, rows=rows, d=d0, jr=jr, jn=jn, locq=urlencode(extra))
        if explicit:
            _with_cookie(resp, "ph_janma", {"rashi": jr, "nak": jn})
        return resp

    @app.get("/sade-sati", response_class=HTMLResponse, include_in_schema=False)
    def sade(request: Request):
        loc = loc_from(request)
        q = request.query_params
        rashi = _opt_int(q.get("rashi"), 1, 12)
        b = birth_from_query(request)
        sign = None
        moon_name = None
        if rashi and not q.get("date"):
            sign = rashi - 1
            moon_name = RASHIS[sign]
        elif _chartable(b):
            syl = moon_syllable(b["date"], b["time"], b["timezone"])
            moon_name = syl["rashi"]
            sign = RASHIS.index(moon_name)
        elif rashi:
            sign = rashi - 1
            moon_name = RASHIS[sign]
        periods, current, nxt = [], None, None
        if sign is not None:
            tz = ephem.make_tz(loc["tz"])
            jd = ephem.jd_from_utc(datetime.now(timezone.utc))
            periods = sade_sati(sign, jd - 8 * 365.25, 32, tz)
            today = datetime.now(tz).date().isoformat()
            for item in periods:
                if item["start"] <= today <= item["end"]:
                    current = item
                elif item["start"] > today and nxt is None:
                    nxt = item
        return page(request, "sade.html", f"Sade Sati | {BRAND}",
                    "Whether Saturn is in the 12th, 1st or 2nd from your Moon, and the small Panoti houses.",
                    "/sade-sati", loc=loc, b=b, rashi=rashi, moon_name=moon_name,
                    periods=periods, current=current, nxt=nxt)

    @app.get("/festivals.ics", include_in_schema=False)
    def festivals_feed(request: Request):
        loc = loc_from(request)
        y = year_of(request)
        events = RC.festivals(y, L(loc), None)["events"]
        body = festivals_ics(events, loc["city"])
        return Response(body, media_type="text/calendar; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="panchanghub-{y}.ics"'})

    @app.get("/panchang", response_class=HTMLResponse, include_in_schema=False)
    def panchang(request: Request):
        loc = loc_from(request); d = qdate(request)
        jr, jn, explicit = janma_from(request)
        try:
            p = RP.panchang(d, L(loc), 0.0, jr, jn)
        except HTTPException as e:
            return page(request, "error.html", "Panchang unavailable", "", "/panchang", msg=e.detail)
        reg = RX.regional(d, L(loc))
        live = datetime.now(ephem.make_tz(loc["tz"])).date() == d
        resp = page(request, "panchang.html", f"Panchang {d.strftime('%d %B %Y')} – {loc['city']} | {BRAND}",
                    f"Daily Panchang for {d.strftime('%B %d, %Y')} in {loc['city']} with tithi, nakshatra end times, Rahu Kaal, Abhijit, Pancha Pakshi and Mantri Mandala.",
                    "/panchang", loc=loc, p=p, reg=reg, d=d, prev=neighbor(d, -1), next=neighbor(d, 1),
                    janma_rashi=jr, janma_nakshatra=jn, live=live)
        if explicit:
            _with_cookie(resp, "ph_janma", {"rashi": jr, "nak": jn})
        return resp

    @app.get("/calendar", response_class=HTMLResponse, include_in_schema=False)
    def calendar(request: Request):
        loc = loc_from(request); t = Date.today()
        y = year_of(request); m = int(request.query_params.get("month", t.month))
        if not 1 <= m <= 12: m = t.month
        cal = RC.month(y, m, L(loc))
        first = Date(y, m, 1); lead = (first.weekday() + 1) % 7
        try:
            pm = first - timedelta(days=1)
            if pm.year < ephem.YEAR_MIN: pm = None
        except OverflowError:
            pm = None
        nm = (first + timedelta(days=32)).replace(day=1)
        if nm.year > ephem.YEAR_MAX: nm = None
        return page(request, "calendar.html", f"Panchang · Vikram Samvat {first.strftime('%B %Y')} – {loc['city']} | {BRAND}",
                    f"Monthly Hindu calendar for {first.strftime('%B %Y')} with tithi, nakshatra and festivals.", "/calendar",
                    loc=loc, cal=cal, lead=lead, first=first, pm=pm, nm=nm, today=t.isoformat())

    def _timing(request, kind):
        loc = loc_from(request); d = qdate(request)
        data = {"choghadiya": RP.choghadiya, "hora": RP.hora}[kind](d, L(loc))
        return loc, d, data

    @app.get("/choghadiya", response_class=HTMLResponse, include_in_schema=False)
    def chog(request: Request):
        loc, d, data = _timing(request, "choghadiya")
        return page(request, "choghadiya.html", f"Choghadiya {d.strftime('%d %B %Y')} – {loc['city']} | {BRAND}",
                    f"Day and night Choghadiya muhurat for {loc['city']}.", "/choghadiya", loc=loc, c=data, d=d,
                    prev=neighbor(d, -1), next=neighbor(d, 1))

    @app.get("/hora", response_class=HTMLResponse, include_in_schema=False)
    def hora(request: Request):
        loc, d, data = _timing(request, "hora")
        return page(request, "hora.html", f"Hora Timings {d.strftime('%d %B %Y')} – {loc['city']} | {BRAND}",
                    f"Planetary hora table for {loc['city']}.", "/hora", loc=loc, h=data, d=d,
                    prev=neighbor(d, -1), next=neighbor(d, 1))

    @app.get("/rahu-kaal", response_class=HTMLResponse, include_in_schema=False)
    def rahu(request: Request):
        loc = loc_from(request); d = qdate(request)
        rows = []
        for k in range(7):
            dd = d + timedelta(days=k); r = RP.rahu(dd, L(loc)); rows.append((dd, r))
        return page(request, "rahu.html", f"Rahu Kaal Today – {loc['city']} | {BRAND}", f"Rahu Kalam, Yamaganda and Gulika for the week in {loc['city']}.",
                    "/rahu-kaal", loc=loc, rows=rows, d=d)

    @app.get("/lagna-table", response_class=HTMLResponse, include_in_schema=False)
    def lagna(request: Request):
        loc = loc_from(request); d = qdate(request)
        lt = RP.lagna(d, L(loc)); gw = RP.gowri(d, L(loc))
        return page(request, "lagna.html", f"Lagna Table & Gowri Panchangam – {loc['city']} | {BRAND}", "Udaya lagna timings and Gowri Nalla Neram.",
                    "/lagna-table", loc=loc, lt=lt, gw=gw, d=d, prev=neighbor(d, -1), next=neighbor(d, 1))

    @app.get("/festivals", response_class=HTMLResponse, include_in_schema=False)
    def festivals(request: Request):
        loc = loc_from(request); y = year_of(request); typ = request.query_params.get("type") or None
        f = RC.festivals(y, L(loc), typ)
        months = {}
        for e in f["events"]: months.setdefault(e["date"][:7], []).append(e)
        types = ["festival", "ekadashi", "purnima", "amavasya", "sankranti", "pradosh", "sankashti", "shivaratri", "chaturthi", "eclipse", "dwadashi", "shraddha", "sashti", "ashtami", "chandra_darshan", "karthigai"]
        return page(request, "festivals.html", f"Hindu Festivals & Vrat Calendar {y} – {loc['city']} | {BRAND}",
                    f"Complete {y} list of Hindu festivals, Ekadashi, Purnima, Amavasya, Pradosh, Sankranti and eclipses.", "/festivals",
                    loc=loc, months=months, year=y, typ=typ, types=types)

    @app.get("/kundli", response_class=HTMLResponse, include_in_schema=False)
    def kundli(request: Request):
        b = birth_from_query(request); k = None; charts = {}; style = request.query_params.get("style", "north")
        ready = _chartable(b)
        special_lagnas = None; av_suite = None; sudarshan_data = None; varshaphala_data = None; kp_data = None; holistic_reading = None; soul_guidance = None; remedies_corpus = None
        if ready:
            req = KundliRequest(**{kk: v for kk, v in b.items() if kk not in ("city", "bad_date")})
            k = RV.kundli(req)
            k["reading"] = INTERP.kundli_reading(k)
            k["remedy_plan"] = ESO.remedies_for(k)
            fn = {"north": north_indian, "south": south_indian, "east": east_indian}.get(style, north_indian)
            retro = {p["name"]: p["retrograde"] for p in k["planets"]}
            for vk in ["D1", "D9", "D10", "D2", "D3", "D4", "D7", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
                v = k["vargas"][vk]
                pl = [{"name": n, "sign": ephem.SIGNS.index(x["sign"]), "retrograde": retro[n]} for n, x in v["planets"].items()]
                charts[vk] = fn(ephem.SIGNS.index(v["ascendant_sign"]), pl, 340 if vk in ("D1", "D9") else 250, vk)
            moon_s = ephem.SIGNS.index(k["lagna"]["sign"])
            mp = [{"name": p["name"], "sign": ephem.SIGNS.index(p["sign"]), "retrograde": p["retrograde"]} for p in k["planets"][:9]]
            charts["Moon"] = fn(ephem.RASHIS.index(k["moon"]["rashi"]), mp, 340, "Chandra")
            try:
                from ..core.special_lagnas import compute_special_lagnas
                from ..core.ashtakavarga_ext import full_ashtakavarga_suite
                from ..core.charts_svg import sudarshan_chakra_svg
                from ..api.deps import birth_utc

                pos_dict = {p["name"]: {"longitude": p["longitude"], "speed": p["speed"]} for p in k["planets"]}
                asc_lon = k["lagna"]["longitude"]
                sun_lon = pos_dict["Sun"]["longitude"]
                moon_lon = pos_dict["Moon"]["longitude"]
                birth_jd = ephem.jd_from_utc(birth_utc(req))

                special_lagnas = compute_special_lagnas(birth_jd, req.latitude, req.longitude, asc_lon, sun_lon, moon_lon, pos_dict)

                sign_of = {p["name"]: ephem.SIGNS.index(p["sign"]) for p in k["planets"]}
                sign_of["Lagna"] = ephem.SIGNS.index(k["lagna"]["sign"])
                av_suite = full_ashtakavarga_suite(sign_of, pos_dict, asc_lon)

                asc_s = ephem.SIGNS.index(k["lagna"]["sign"])
                moon_s = ephem.RASHIS.index(k["moon"]["rashi"])
                sun_s = ephem.SIGNS.index([p["sign"] for p in k["planets"] if p["name"] == "Sun"][0])
                pls = [{"name": p["name"], "sign": ephem.SIGNS.index(p["sign"]), "longitude": p["longitude"], "retrograde": p["retrograde"]} for p in k["planets"] if p["name"] in ephem.VEDIC_PLANETS]
                sudarshan_svg = sudarshan_chakra_svg(asc_s, moon_s, sun_s, pls, size=520, title=f"Sudarshan Chakra - {req.name or 'Native'}")
                sectors = []
                for h in range(12):
                    s_lagna = (asc_s + h) % 12
                    s_moon = (moon_s + h) % 12
                    s_sun = (sun_s + h) % 12
                    sectors.append({
                        "house": h + 1,
                        "lagna_sign": ephem.SIGNS[s_lagna],
                        "lagna_planets": [p["name"] for p in pls if p["sign"] == s_lagna],
                        "moon_sign": ephem.SIGNS[s_moon],
                        "moon_planets": [p["name"] for p in pls if p["sign"] == s_moon],
                        "sun_sign": ephem.SIGNS[s_sun],
                        "sun_planets": [p["name"] for p in pls if p["sign"] == s_sun],
                    })
                sudarshan_data = {"svg": sudarshan_svg, "sectors": sectors}
            except Exception:
                special_lagnas = None
                av_suite = None
                sudarshan_data = None

            holistic_reading = None
            try:
                from ..core.interpret_ext import generate_holistic_reading
                holistic_reading = generate_holistic_reading(pos_dict, asc_lon)
            except Exception:
                holistic_reading = None

            try:
                v_req = VarshaphalaRequest(**{kk: v for kk, v in b.items() if kk != "city"})
                varshaphala_data = ST.varshaphala_endpoint(v_req)
            except Exception:
                varshaphala_data = None
            try:
                kp_req = KPRequest(**{kk: v for kk, v in b.items() if kk != "city"})
                kp_data = ST.kp_endpoint(kp_req)
            except Exception:
                kp_data = None

            try:
                from ..core.remedies_corpus import get_complete_remedies_for_chart
                remedies_corpus = get_complete_remedies_for_chart(k)
                soul_guidance = remedies_corpus.get("soul_guidance")
            except Exception:
                remedies_corpus = None
                soul_guidance = None

        if ready:
            qs_val = urlencode({"name": b.get("name") or "", "date": b["date"], "time": b["time"], "lat": b["latitude"], "lon": b["longitude"], "tz": b.get("timezone") or "", "city": b.get("city") or ""})
        else:
            qs_val = ""
        return page(request, "kundli.html", f"Free Kundli (Janam Kundali) Online – {BRAND}",
                    "Free Vedic birth chart with North/South Indian charts, D1–D60 vargas, Vimshottari & Yogini dasha, ashtakavarga, doshas and yogas.",
                    "/kundli", b=b, k=k, charts=charts, style=style, qs=qs_val,
                    special_lagnas=special_lagnas, av_suite=av_suite, sudarshan_data=sudarshan_data,
                    varshaphala_data=varshaphala_data, kp_data=kp_data, holistic_reading=holistic_reading,
                    soul_guidance=soul_guidance, remedies_corpus=remedies_corpus)


    @app.get("/vargas", response_class=HTMLResponse, include_in_schema=False)
    def vargas_view(request: Request):
        b = birth_from_query(request)
        style = request.query_params.get("style", "north")
        ayan = request.query_params.get("ayanamsa", "lahiri")
        v_filter = request.query_params.get("varga", "all")
        vdata = None
        charts = {}
        sahams = None
        asc_nadi = None
        asc_drekkana = None
        if _chartable(b):
            req_dict = {kk: v for kk, v in b.items() if kk != "city"}
            req_dict["ayanamsa"] = ayan
            req = KundliRequest(**req_dict)
            vdata = ST.vargas(req)
            fn = {"north": north_indian, "south": south_indian, "east": east_indian}.get(style, north_indian)
            for vk, vinfo in vdata["vargas"].items():
                asc_s = ephem.SIGNS.index(vinfo["ascendant"]["sign_name"])
                pl = [{"name": p["name"], "sign": ephem.SIGNS.index(p["sign_name"]), "retrograde": False} for p in vinfo["planets"]]
                charts[vk] = fn(asc_s, pl, 320, vk)

            taj_res = ST.tajika_sahams_endpoint(req)
            sahams = taj_res["sahams"]
            asc_nadi = taj_res["ascendant_nadiamsha"]
            asc_drekkana = taj_res["ascendant_drekkana_body_part"]

        return page(request, "vargas.html", f"31 Divisional Charts (Parashara, Tajika, Nadi & Iyer) | {BRAND}",
                    "Complete 31 classical Vedic divisional charts including 16 Parashara Shodashavargas, 5 Tajika/Nadi vargas, and 10 Seshadhri Iyer harmonic vargas with Sahams and Nadiamshas.",
                    "/vargas", b=b, vdata=vdata, charts=charts, style=style, ayanamsa=ayan, v_filter=v_filter,
                    sahams=sahams, asc_nadi=asc_nadi, asc_drekkana=asc_drekkana)

    @app.get("/yogas", response_class=HTMLResponse, include_in_schema=False)
    def yogas_view(request: Request):
        b = birth_from_query(request)
        ayan = request.query_params.get("ayanamsa", "lahiri")
        ydata = None
        if _chartable(b):
            req_dict = {kk: v for kk, v in b.items() if kk != "city"}
            req_dict["ayanamsa"] = ayan
            req = KundliRequest(**req_dict)
            ydata = ST.comprehensive_yogas_endpoint(req)
        return page(request, "yogas.html", f"Classical Vedic Yogas Scanner (60+ Yogas) | {BRAND}",
                    "Automated detection of classical Vedic planetary yogas: Pancha Mahapurusha, Raja, Dhana, Viparita, Saraswati, and Solar/Lunar combinations.",
                    "/yogas", b=b, ydata=ydata, ayanamsa=ayan)

    @app.get("/reading", response_class=HTMLResponse, include_in_schema=False)
    def reading_view(request: Request):
        b = birth_from_query(request)
        ayan = request.query_params.get("ayanamsa", "lahiri")
        rdata = None
        cur_dasha = None
        karakas = None
        corpus_data = None
        if _chartable(b):
            req_dict = {kk: v for kk, v in b.items() if kk != "city"}
            req_dict["ayanamsa"] = ayan
            req = KundliRequest(**req_dict)
            rdata = ST.holistic_reading_endpoint(req)
            cur_dasha = ST.current_dasha_endpoint(req)
            karakas = ST.chara_karakas_endpoint(req)
            corpus_data = ST.planetary_placements_corpus(req)
        return page(request, "reading.html", f"Holistic Vedic Life Reading & 144 House Lords Analysis | {BRAND}",
                    "Detailed Vedic life reading including Ascendant portrait, 144 House Lord combinations, 12-house Shad Phala, and current dasha period.",
                    "/reading", b=b, rdata=rdata, cur_dasha=cur_dasha, karakas=karakas, corpus_data=corpus_data, ayanamsa=ayan)

    @app.get("/varshaphala", response_class=HTMLResponse, include_in_schema=False)
    def varshaphala_view(request: Request):
        b = birth_from_query(request)
        style = request.query_params.get("style", "north")
        yr = request.query_params.get("year")
        year = int(yr) if yr and yr.isdigit() else None
        vdata = None
        varsha_chart_svg = None
        if _chartable(b):
            v_req = VarshaphalaRequest(**{kk: v for kk, v in b.items() if kk != "city"}, year=year)
            vdata = ST.varshaphala_endpoint(v_req)
            fn = {"north": north_indian, "south": south_indian, "east": east_indian}.get(style, north_indian)
            v_asc = ephem.SIGNS.index(vdata["varsha_lagna"]["sign"])
            v_pls = [{"name": p["name"], "sign": ephem.SIGNS.index(p["sign"]), "retrograde": p.get("retrograde", False)} for p in vdata["planets"][:9]]
            varsha_chart_svg = fn(v_asc, v_pls, 360, f"Varsha Kundli {vdata['year']}")
        return page(request, "varshaphala.html", f"Tajika Varshaphala (Annual Solar Return Chart) | {BRAND}",
                    "Authentic Tajika Solar Return chart with Muntha, Varshesha Year Lord, Mudda Dasha, 24 Sahams, and Tajika Yogas.",
                    "/varshaphala", b=b, vdata=vdata, varsha_chart_svg=varsha_chart_svg, style=style,
                    year=year or (vdata["year"] if vdata else 2026), qs=str(request.query_params))

    @app.get("/kp", response_class=HTMLResponse, include_in_schema=False)
    def kp_view(request: Request):
        b = birth_from_query(request)
        h_num = request.query_params.get("horary")
        horary_number = int(h_num) if h_num and h_num.isdigit() and 1 <= int(h_num) <= 249 else None
        kp_data = None
        if _chartable(b):
            kp_req = KPRequest(**{kk: v for kk, v in b.items() if kk != "city"}, horary_number=horary_number)
            kp_data = ST.kp_endpoint(kp_req)
        return page(request, "kp.html", f"KP System (KP System Astrology) | {BRAND}",
                    "Accurate KP System astrology: Placidus cusps, Sign/Star/Sub/Sub-Sub lords, 4-fold Significators, Ruling Planets, and 1-249 Horary table.",
                    "/kp", b=b, kp_data=kp_data, horary_number=horary_number, qs=str(request.query_params))

    @app.get("/prashna", response_class=HTMLResponse, include_in_schema=False)
    def prashna_view(request: Request):
        loc = loc_from(request)
        q = request.query_params
        category = q.get("category", "career")
        q_text = q.get("q_text", "")
        style = q.get("style", "north")

        import zoneinfo
        try:
            tz_obj = zoneinfo.ZoneInfo(loc["tz"])
            local_now = datetime.now(tz_obj)
        except Exception:
            local_now = datetime.now()

        q_date_str = q.get("date") or local_now.strftime("%Y-%m-%d")
        q_time_str = q.get("time") or local_now.strftime("%H:%M:%S")

        pdata = None
        chart_svg = None
        try:
            d_val = Date.fromisoformat(q_date_str)
            t_parts = q_time_str.split(":")
            from datetime import time as Time
            if len(t_parts) == 2:
                t_val = Time(int(t_parts[0]), int(t_parts[1]), 0)
            elif len(t_parts) >= 3:
                t_val = Time(int(t_parts[0]), int(t_parts[1]), int(float(t_parts[2])))
            else:
                t_val = Time(12, 0, 0)

            lat = float(q.get("lat") or loc["lat"])
            lon = float(q.get("lon") or loc["lon"])
            tz = q.get("tz") or loc["tz"]

            p_req = PrashnaRequest(
                date=d_val,
                time=t_val,
                latitude=lat,
                longitude=lon,
                timezone=tz,
                query_category=category,
                question_text=q_text or None
            )
            pdata = ST.prashna_endpoint(p_req)

            fn = {"north": north_indian, "south": south_indian, "east": east_indian}.get(style, north_indian)
            asc_s = ephem.SIGNS.index(pdata["prashna_lagna"]["sign"])
            pls = [{"name": p["name"], "sign": ephem.SIGNS.index(p["sign"]), "retrograde": False} for p in pdata["planets"] if p["name"] in ephem.VEDIC_PLANETS]
            chart_svg = fn(asc_s, pls, 360, f"Prashna: {pdata['query_title']}")
        except Exception:
            pdata = None
            chart_svg = None

        return page(request, "prashna.html", f"Vedic Prashna Kundali (Classical Horary Divination) | {BRAND}",
                    "Instant Vedic Horary Astrology (Prashna Tantra & Daivajna Vallabha): definitive answers, confidence index, and fulfillment timeline.",
                    "/prashna", pdata=pdata, chart_svg=chart_svg, q_date=q_date_str, q_time=q_time_str,
                    category=category, q_text=q_text, style=style, loc=loc)

    @app.get("/matching", response_class=HTMLResponse, include_in_schema=False)
    def matching(request: Request):
        bb = birth_from_query(request, "b_"); gg = birth_from_query(request, "g_"); m = None
        if bb and gg:
            strip = lambda x: {kk: v for kk, v in x.items() if kk not in ("city", "name")}
            m = RV.matching(MatchRequest(boy=BirthData(**strip(bb)), girl=BirthData(**strip(gg))))
        return page(request, "matching.html", f"Kundli Matching – 36 Guna Milan & Porutham | {BRAND}",
                    "Free horoscope matching for marriage with Ashtakoota guna milan and South Indian 10 porutham.", "/matching", bb=bb, gg=gg, m=m)

    @app.get("/muhurat", response_class=HTMLResponse, include_in_schema=False)
    def muhurat(request: Request):
        loc = loc_from(request); typ = request.query_params.get("type", "marriage")
        s = qdate(request, "start"); e = Date.fromisoformat(request.query_params["end"]) if request.query_params.get("end") else s + timedelta(days=60)
        if e.year > ephem.YEAR_MAX: e = Date(ephem.YEAR_MAX, 12, 31)
        err = None
        if e < s or (e - s).days > ephem.SPAN_MAX_DAYS:
            err = f"One search covers up to 10 years. Any day from {ephem.YEAR_MIN} CE through {ephem.YEAR_MAX} CE can be the start."
            res = None
        else:
            res = RC.muhurat(typ, s, e, L(loc)) if typ in ("marriage", "griha_pravesh", "vehicle", "property", "naming", "mundan", "annaprashan", "business") else None
        return page(request, "muhurat.html", f"Shubh Muhurat Finder – {BRAND}", "Find auspicious muhurat for marriage, griha pravesh, vehicle and property purchase.",
                    "/muhurat", loc=loc, res=res, typ=typ, s=s, e=e, err=err)

    @app.get("/transits", response_class=HTMLResponse, include_in_schema=False)
    def transits(request: Request):
        y = year_of(request); tz = loc_from(request)["tz"]
        t = RC.transits(Date(y, 1, 1), Date(y, 12, 31), tz, "sidereal")
        planets = RCore.planets(None, tz, "sidereal", False)
        ph = RX.moon_phases(Date(y, 1, 1), 366, tz)
        return page(request, "transits.html", f"Planetary Transits & Retrogrades {y} | {BRAND}", f"Sidereal planet sign changes, retrograde and direct dates for {y}.",
                    "/transits", t=t, y=y, now=planets, ph=ph)

    @app.get("/western", response_class=HTMLResponse, include_in_schema=False)
    def western(request: Request):
        b = birth_from_query(request); c = None; svg = None
        if _chartable(b):
            hs = request.query_params.get("hs", "placidus")
            c = RCore.chart(ChartRequest(**{kk: v for kk, v in b.items() if kk not in ("city", "name")}, house_system=hs))
            svg = western_wheel(c["ascendant"]["longitude"], [h["cusp"] for h in c["houses"]], c["planets"])
        return page(request, "western.html", f"Western Natal Chart (Tropical) – {BRAND}", "Free tropical birth chart with Placidus houses, aspects and wheel.",
                    "/western", b=b, c=c, svg=svg)

    @app.get("/horoscope", response_class=HTMLResponse, include_in_schema=False)
    def horoscope(request: Request):
        period = request.query_params.get("period", "daily"); system = request.query_params.get("system", "vedic")
        hs = [RX.horoscope(period, s, None, system) for s in ephem.SIGNS]
        return page(request, "horoscope.html", f"{period.title()} Horoscope (Rashifal) | {BRAND}", "Transit-based horoscope for all 12 signs.",
                    "/horoscope", hs=hs, period=period, system=system)

    @app.get("/numerology", response_class=HTMLResponse, include_in_schema=False)
    def numerology(request: Request):
        q = request.query_params; n = None
        b = birth_from_query(request)
        name = (q.get("name") or (b.get("name") if b else "") or "").strip()
        dob_str = normalize_date_str(q.get("dob") or q.get("date") or (b.get("date") if b else "") or "", default=None) or ""
        system = q.get("system", "pythagorean")
        lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b and b.get("latitude") is not None else None)
        lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b and b.get("longitude") is not None else None)
        tm = q.get("time") or (b.get("time") if b else "") or ""
        tz = q.get("tz") or (b.get("timezone") if b else "") or ""
        if name and dob_str:
            try:
                dob = Date.fromisoformat(dob_str)
                bd = {"time": tm, "latitude": lat, "longitude": lon, "timezone": tz} if (lat is not None and lon is not None) else None
                n = RX.N.profile(name, dob, system, birth_details=bd)
            except Exception:
                pass
        return page(request, "numerology.html", f"Astro-Numerology & Destiny Calculator – {BRAND}",
                    "Comprehensive Vedic Astro-Numerology, Lucky Numbers, Shatru Anka, Karmic Debts & Lo Shu Grid.",
                    "/numerology", n=n, q=q, b=b)

    @app.get("/destiny", response_class=HTMLResponse, include_in_schema=False)
    def destiny_page(request: Request):
        from ..core.destiny_engine import compute_master_destiny_dossier
        q = request.query_params
        loc = loc_from(request)
        b = birth_from_query(request)
        name = (q.get("name") or (b.get("name") if b else "") or "").strip()
        dob_str = normalize_date_str(q.get("date") or q.get("dob") or (b.get("date") if b else "") or "", default=None) or ""
        tm_str = q.get("time") or (b.get("time") if b else "") or ""
        if len(tm_str) == 5:
            tm_str += ":00"
        b_lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b and b.get("latitude") is not None else (28.6139 if dob_str else ""))
        b_lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b and b.get("longitude") is not None else (77.2090 if dob_str else ""))
        b_tz = q.get("tz") or (b.get("timezone") if b else "") or ""
        b_city = q.get("city") or (b.get("city") if b else "New Delhi, India")
        if dob_str and b_lat != "":
            b_city, b_lat, b_lon, b_tz = _resolve_city_coords(b_city, float(b_lat), float(b_lon), b_tz or "Asia/Kolkata")

        c_lat = float(q["cur_lat"]) if q.get("cur_lat") else loc["lat"]
        c_lon = float(q["cur_lon"]) if q.get("cur_lon") else loc["lon"]
        c_tz = q.get("cur_tz") or loc["tz"]
        c_city = q.get("cur_city") or loc["city"]
        c_city, c_lat, c_lon, c_tz = _resolve_city_coords(c_city, c_lat, c_lon, c_tz)
        scan_days = int(q.get("scan_days", 30)) if str(q.get("scan_days", "30")).isdigit() else 30

        dossier = None
        try:
            def _split_tz(tz_raw):
                if tz_raw is None:
                    return ("Asia/Kolkata", None)
                try:
                    return (None, float(tz_raw))
                except ValueError:
                    return (str(tz_raw), None)

            b_tz_name, b_utc_off = _split_tz(b_tz)
            c_tz_name, c_utc_off = _split_tz(c_tz)
            d_obj = Date.fromisoformat(dob_str)
            t_obj = datetime.strptime(tm_str, "%H:%M:%S").time()
            tz_b = ephem.make_tz(b_tz_name, b_utc_off)
            dt_utc = datetime.combine(d_obj, t_obj).replace(tzinfo=tz_b).astimezone(timezone.utc)
            dossier = compute_master_destiny_dossier(
                dt_utc, b_lat, b_lon, b_tz_name, b_utc_off, name=name,
                current_lat=c_lat, current_lon=c_lon, current_tz_name=c_tz_name, current_utc_offset=c_utc_off,
                current_city=c_city, scan_days=min(max(scan_days, 7), 90)
            )
        except Exception:
            pass
        return page(
            request, "destiny.html",
            f"Master Destiny, 9-Planet Control, Lottery, Longevity & Past/Future Life – {BRAND}",
            "Cross-linked Vedic astrology oracle: diseases, longevity, accident dates & hours, lottery luck, marriage count, children & grandchildren, past/future life, and Samhita 9-planet mastery.",
            "/destiny", dossier=dossier, q=q, b=b, cur_city=c_city,
            form={"name": name, "date": dob_str, "time": tm_str[:5], "lat": b_lat, "lon": b_lon, "tz": b_tz, "city": b_city,
                  "cur_lat": c_lat, "cur_lon": c_lon, "cur_tz": c_tz, "cur_city": c_city, "scan_days": scan_days}
        )

    @app.get("/vastu", response_class=HTMLResponse, include_in_schema=False)
    def vastu(request: Request):
        from ..core.astro_vastu_engine import compute_personalized_astro_vastu, compute_classical_feng_shui, PLAIN_ENGLISH_GLOSSARY
        q = request.query_params
        b = birth_from_query(request)
        dob_str = normalize_date_str(q.get("date") or q.get("dob") or (b.get("date") if b else "") or "", default=None) or ""
        tm_str = q.get("time") or (b.get("time") if b else "") or ""
        if len(tm_str) == 5:
            tm_str += ":00"
        gender = q.get("gender", "male") if q.get("gender") in ("male", "female") else "male"
        b_lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b and b.get("latitude") is not None else (28.6139 if dob_str else ""))
        b_lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b and b.get("longitude") is not None else (77.2090 if dob_str else ""))
        b_tz = q.get("tz") or (b.get("timezone") if b else "") or ""
        b_city = q.get("city") or (b.get("city") if b else "New Delhi, India")
        if dob_str and b_lat != "":
            b_city, b_lat, b_lon, b_tz = _resolve_city_coords(b_city, float(b_lat), float(b_lon), b_tz or "Asia/Kolkata")

        astro_vastu = None
        feng_shui = None
        try:
            try:
                tz_b = ephem.make_tz(None, float(b_tz))
            except (ValueError, TypeError):
                tz_b = ephem.make_tz(str(b_tz), None)
            d_obj = Date.fromisoformat(dob_str)
            dt_utc = datetime.combine(d_obj, datetime.strptime(tm_str, "%H:%M:%S").time()).replace(tzinfo=tz_b).astimezone(timezone.utc)
            jd = ephem.jd_from_utc(dt_utc)
            pos = ephem.all_positions(jd, sidereal=True)
            _, asc_lon, _ = ephem.houses(jd, b_lat, b_lon, "P", sidereal=True)
            astro_vastu = compute_personalized_astro_vastu(pos, asc_lon)
            feng_shui = compute_classical_feng_shui(
                d_obj.year, d_obj.month, d_obj.day, gender, pos=pos, asc_lon=asc_lon, facing=q.get("facing")
            )
        except Exception:
            astro_vastu = None
            try:
                feng_shui = compute_classical_feng_shui(Date.today().year, gender)
            except Exception:
                feng_shui = None

        layout = {r: q.get("room_" + r.replace(" ", "_")) for r in ESO.ROOM_BEST if q.get("room_" + r.replace(" ", "_"))}
        v = ESO.vastu(layout or None, q.get("facing"))
        return page(
            request, "vastu.html", f"Interactive Vastu & Classical Feng Shui Architect Studio – {BRAND}",
            "Interactive Visual House (Square/Rectangle) & Outer-Lot Vastu + Classical Feng Shui (Kua, Eight Mansions, Bagua & Flying Stars) Architect Studio.",
            "/vastu", v=v, q=q, rooms=list(ESO.ROOM_BEST), dirs=list(ESO.VASTU),
            astro_vastu=astro_vastu, feng_shui=feng_shui, glossary=PLAIN_ENGLISH_GLOSSARY,
            b_form={"date": dob_str, "time": tm_str[:5], "lat": b_lat, "lon": b_lon, "tz": b_tz, "city": b_city, "gender": gender}
        )


    @app.get("/reports", response_class=HTMLResponse, include_in_schema=False)
    def reports_page(request: Request):
        from ..core.detailed_reports_engine import get_reports_and_menus_catalog, generate_detailed_text_report
        q = request.query_params
        b = birth_from_query(request)
        name = (q.get("name") or (b.get("name") if b else "") or "").strip()
        dob_str = normalize_date_str(q.get("date") or q.get("dob") or (b.get("date") if b else "") or "", default=None) or ""
        tm_str = q.get("time") or (b.get("time") if b else "") or ""
        if len(tm_str) == 5:
            tm_str += ":00"
        gender = q.get("gender", "male") if q.get("gender") in ("male", "female") else "male"
        model_code = (q.get("model") or q.get("model_code") or "HP3").upper()
        b_lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b and b.get("latitude") is not None else (28.6139 if dob_str else ""))
        b_lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b and b.get("longitude") is not None else (77.2090 if dob_str else ""))
        b_tz = q.get("tz") or (b.get("timezone") if b else "") or ""
        b_city = q.get("city") or (b.get("city") if b else "New Delhi, India")
        if dob_str and b_lat != "":
            b_city, b_lat, b_lon, b_tz = _resolve_city_coords(b_city, float(b_lat), float(b_lon), b_tz or "Asia/Kolkata")

        catalog = get_reports_and_menus_catalog()
        report = None
        try:
            try:
                tz_b = ephem.make_tz(None, float(b_tz))
            except (ValueError, TypeError):
                tz_b = ephem.make_tz(str(b_tz), None)
            d_obj = Date.fromisoformat(dob_str)
            dt_utc = datetime.combine(d_obj, datetime.strptime(tm_str, "%H:%M:%S").time()).replace(tzinfo=tz_b).astimezone(timezone.utc)
            report = generate_detailed_text_report(
                dt_utc=dt_utc,
                lat=b_lat,
                lon=b_lon,
                tz=tz_b,
                name=name,
                gender=gender,
                model_code=model_code,
            )
        except Exception:
            report = None

        return page(
            request, "reports.html",
            f"Detailed Multi-Chapter Text Reports, All 22 Dashas & 9 Menus Studio – {BRAND}",
            "Generate book-formatted Vedic Horoscope Dossiers across 20 Report Models (HP3, HC3, KP2, VP2, HM2, MASTER_COMPLETE), browse all 9 Menus & Submenus, 22 Dasha Systems, 11 Upagrahas, 15 Sphutas, 4 Avastha Systems, Panchadha Maitri, Saturn Cycles, Gemstones, and Birth Time Rectification.",
            "/reports",
            catalog=catalog,
            report=report,
            b=b,
            form={
                "name": name,
                "date": dob_str,
                "time": tm_str[:5],
                "lat": b_lat,
                "lon": b_lon,
                "tz": b_tz,
                "city": b_city,
                "gender": gender,
                "model_code": model_code,
            },
        )

    @app.get("/traditions", response_class=HTMLResponse, include_in_schema=False)
    def traditions_page(request: Request):
        from ..core.traditions_engine import compute_traditions_report, get_traditions_catalog
        q = request.query_params
        b = birth_from_query(request)
        name = (q.get("name") or (b.get("name") if b else "") or "").strip()
        dob_str = normalize_date_str(q.get("date") or q.get("dob") or (b.get("date") if b else "") or "", default=None) or ""
        tm_str = q.get("time") or (b.get("time") if b else "") or ""
        if len(tm_str) == 5:
            tm_str += ":00"
        gender = q.get("gender", "male") if q.get("gender") in ("male", "female") else "male"
        goal = q.get("goal", "all")
        approach = q.get("approach", "all")
        selected_list = q.getlist("traditions") if hasattr(q, "getlist") else []
        b_lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b and b.get("latitude") is not None else (28.6139 if dob_str else ""))
        b_lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b and b.get("longitude") is not None else (77.2090 if dob_str else ""))
        b_tz = q.get("tz") or (b.get("timezone") if b else "") or ""
        b_city = q.get("city") or (b.get("city") if b else "New Delhi, India")
        if dob_str and b_lat != "":
            b_city, b_lat, b_lon, b_tz = _resolve_city_coords(b_city, float(b_lat), float(b_lon), b_tz or "Asia/Kolkata")

        catalog = get_traditions_catalog()
        report = None
        try:
            try:
                tz_b = ephem.make_tz(None, float(b_tz))
            except (ValueError, TypeError):
                tz_b = ephem.make_tz(str(b_tz), None)
            d_obj = Date.fromisoformat(dob_str)
            dt_utc = datetime.combine(d_obj, datetime.strptime(tm_str, "%H:%M:%S").time()).replace(tzinfo=tz_b).astimezone(timezone.utc)
            report = compute_traditions_report(
                dt_utc, b_lat, b_lon, tz_b, name=name, gender=gender,
                selected_traditions=selected_list or None,
                goal_filter=goal,
                approach_filter=approach,
            )
        except Exception:
            report = None

        return page(
            request, "traditions.html",
            f"Global Astrological Traditions & Vata-Pitta-Kapha / Five-Element Studio – {BRAND}",
            "Explore 14 Eastern/Vedic, Western, and Global astrological traditions (Lal Kitab, Parashari, Jaimini, KP, Nadi, Western Tropical, Hellenistic, Evolutionary, Uranian, Chinese BaZi, Feng Shui, Mayan, Celtic Tree) + Vata-Pitta-Kapha & Chinese Five Elements balance.",
            "/traditions", catalog=catalog, report=report, b=b,
            form={"name": name, "date": dob_str, "time": tm_str[:5], "lat": b_lat, "lon": b_lon, "tz": b_tz, "city": b_city,
                  "gender": gender, "goal": goal, "approach": approach}
        )

    @app.get("/palmistry", response_class=HTMLResponse, include_in_schema=False)
    def palmistry(request: Request):
        q = request.query_params
        b = birth_from_query(request)
        r = ESO.palmistry(
            q.get("hand_shape") or "fire",
            q.get("heart") or "curved",
            q.get("head") or "long",
            q.get("life") or "deep",
            q.get("fate") or "clear",
        )
        return page(request, "palmistry.html", f"Multi-Spectrum Vision Palmistry & Nadi Thumbprint Studio – {BRAND}",
                    "Upload a palm or thumbprint photo and switch across 10 color and spectral imaging modes to inspect palm lines, planetary mounts, and Nadi thumbprint whorls.",
                    "/palmistry", r=r, q=q, b=b)

    @app.get("/login", response_class=HTMLResponse, include_in_schema=False)
    def login_page(request: Request):
        from ..core import auth
        user = auth.get_user_from_request(request.cookies, dict(request.headers))
        return page(request, "login.html", f"Sign In & Email Verification | {BRAND}",
                    "Sign in or verify your email to unlock unlimited 31 divisional charts, Prashna Kundali, KP system and PDF life reports.",
                    "/login", user=user)

    @app.get("/logout", response_class=HTMLResponse, include_in_schema=False)
    def logout_page(request: Request):
        resp = RedirectResponse(url="/", status_code=303)
        resp.delete_cookie("ph_auth", path="/")
        return resp

    @app.get("/tarot/card/{slug}", include_in_schema=False)
    def tarot_card(slug: str):
        from ..core.tarot_art import svg_for
        svg = svg_for(slug)
        if not svg:
            raise HTTPException(404, "unknown card")
        return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/tarot", response_class=HTMLResponse, include_in_schema=False)
    def tarot(request: Request):
        q = request.query_params; sp = q.get("spread", "three_card")
        t = RX.tarot(sp if sp in ("single", "yes_no", "three_card", "love", "celtic_cross") else "three_card", q.get("question"), q.get("seed"))
        return page(request, "tarot.html", f"Tarot Reading – {BRAND}", "Free tarot card reading.", "/tarot", t=t, sp=sp, q=q)

    @app.get("/human-design", response_class=HTMLResponse, include_in_schema=False)
    def human_design(request: Request):
        b = birth_from_query(request); hd = None
        if _chartable(b): hd = RM.human_design(BirthData(**{kk: v for kk, v in b.items() if kk not in ("city", "name")}))
        return page(request, "humandesign.html", f"Human Design Chart Calculator – {BRAND}", "Free Human Design bodygraph: type, strategy, authority, profile, centers, channels and gates.",
                    "/human-design", b=b, hd=hd, CENTERS=list(HDM.CENTERS))

    @app.get("/iching", response_class=HTMLResponse, include_in_schema=False)
    def iching(request: Request):
        q = request.query_params; c = ESO.iching_cast(q.get("question"), q.get("seed")) if (q.get("question") or q.get("cast")) else None
        return page(request, "iching.html", f"I-Ching Oracle – {BRAND}", "Cast an I-Ching hexagram with the three-coin method; all 64 hexagrams.",
                    "/iching", c=c, q=q, all=ESO.iching_all())

    @app.get("/tools", response_class=HTMLResponse, include_in_schema=False)
    def tools(request: Request):
        q = request.query_params; today = Date.today()
        by = int(q.get("birth_year", 1990)); d = qdate(request, "on")
        ctx = {"mayan": ESO.mayan(d), "cf": ESO.chinese_forecast(by, today.year), "by": by,
               "kab": ESO.kabbalah(q["name"]) if q.get("name") else None, "dream": ESO.dream(q["symbol"]) if q.get("symbol") else None,
               "crys": ESO.crystals(), "q": q, "d": d}
        return page(request, "tools.html", f"Mayan, Chinese Forecast, Kabbalah, Dreams & Crystals – {BRAND}", "More free tools: Mayan calendar, Chinese yearly forecast, Kabbalah, dream meanings, crystals.",
                    "/tools", **ctx)

    @app.get("/regional", response_class=HTMLResponse, include_in_schema=False)
    def regional_page(request: Request):
        from ..core import regional_rules as RR, muhurta_doshas as MDZ, festival_rules as FRZ
        loc = loc_from(request); d = qdate(request); q = request.query_params
        raw = (q.get("siddhanta") or "hub").lower()
        sid = "hub" if raw in ("drik", "hub", "modern") else raw if raw in ("surya", "vakya") else "hub"
        jn = int(q["janma_nakshatra"]) if q.get("janma_nakshatra", "").isdigit() else None
        ctx = {"r": RR.regional_calendar(d, loc["lat"], loc["lon"], loc["tz"], siddhanta=sid),
               "ny": RR.regional_new_years(d.year, loc["lat"], loc["lon"], loc["tz"], siddhanta=sid),
               "md": MDZ.day_doshas(d, loc["lat"], loc["lon"], loc["tz"], janma_nakshatra=jn), "fr": FRZ.RULES, "vk": __import__("app.core.vakya", fromlist=["x"]).vakya_panchang(d, loc["lat"], loc["lon"], loc["tz"]), "pk": __import__("app.core.punya_kaal", fromlist=["x"]).year_punya_kaal(d.year, loc["lat"], loc["lon"], loc["tz"]), "d": d, "sid": sid, "jn": jn, "loc": loc}
        return page(request, "regional.html", f"Regional Calendars, Panchaka & Muhurta Doshas – {BRAND}",
                    "Tamil, Malayalam, Bengali, Assamese, Odia, Gujarati and Marathi calendar dates, Vakya/Surya Siddhanta option, Panchaka, Bhadra and festival rules.",
                    "/regional", **ctx)

    @app.get("/widget/panchang", response_class=HTMLResponse, include_in_schema=False)
    def widget(request: Request):
        loc = loc_from(request); p = RP.panchang(Date.today(), L(loc), 0.0, None, None)
        resp = templates.TemplateResponse(request, "widget.html", {"p": p, "loc": loc})
        lang = lang_of(request)
        return resp if lang == "en" else HTMLResponse(localize_html(resp.body.decode(), lang))

    @app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
    def robots():
        return f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {SITE}/sitemap.xml\n"

    @app.get("/sitemap.xml", include_in_schema=False)
    def sitemap():
        today = Date.today().isoformat()
        urls = [p for p, _ in NAV] + ["/api/docs", "/systems", "/gallery", "/lyrics"]
        y = Date.today().year
        urls += [f"/festivals?year={yy}" for yy in (y - 1, y, y + 1)]
        body = "".join(f"<url><loc>{SITE}{u.replace('&', '&amp;')}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq></url>" for u in urls)
        return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>', media_type="application/xml")

    from .library_routes import mount as mount_library
    mount_library(app, page, loc_from, year_of, qdate, L)

    @app.get("/systems", response_class=HTMLResponse, include_in_schema=False)
    def systems(request: Request):
        return page(request, "systems.html", f"Calendar systems – Vikram Samvat, Shaka, Tamil, Bengali | {BRAND}",
                    "Vikram Samvat, Shaka, Tamil, Malayalam, Bengali, Odia, Telugu, Kannada, Gujarati, Marathi, Nepali and Gaudiya calendars.",
                    "/systems")

    @app.get("/gallery", response_class=HTMLResponse, include_in_schema=False)
    def gallery(request: Request):
        return page(request, "gallery.html", f"Festival gallery | {BRAND}", "Original festival paintings: lamps, rangoli, kalash and deepak.", "/gallery")

    @app.get("/lyrics", response_class=HTMLResponse, include_in_schema=False)
    def lyrics(request: Request):
        from ..core.library_text import LYRICS
        return page(request, "lyrics.html", f"Aarti, chalisa and stotra | {BRAND}", "Traditional public-domain verses: aarti, Hanuman Chalisa, stotra, ashtakam and mantra.", "/lyrics", sections=LYRICS)

"""PanchangHub website: server-rendered Jinja pages that call the API handlers in-process (same code path as /api),
plus client JS that calls the public /api endpoints (city search, geolocation, SVG, PDF)."""
from __future__ import annotations
import json, os
from datetime import date as Date, datetime, timedelta, timezone
from urllib.parse import urlencode
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..models import BirthData, KundliRequest, MatchRequest, ChartRequest, VarshaphalaRequest, KPRequest, PrashnaRequest
from ..api.routers import panchang as RP, vedic as RV, calendar as RC, core as RCore, extras as RX
from ..core import ephem, i18n
from ..api.routers import more as RM
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
        out += d.strftime(", %b %d")
    return out

def span(item, ref):
    return f"{hm(item.get('start'), ref)} – {hm(item.get('end'), ref)}" if item else "—"

templates.env.filters["hm"] = hm
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
            from urllib.parse import unquote
            raw = unquote(c) if ("%" in c) else c
            v = json.loads(raw)
            return {"city": v["city"], "lat": float(v["lat"]), "lon": float(v["lon"]), "tz": v["tz"], "source": v.get("src") or "saved"}
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
        raise HTTPException(422, f"Choose a date from {ephem.YEAR_MIN} CE through {ephem.YEAR_MAX} CE. That covers the complete canonical ephemeris span, from year 1 through 3000 CE.")
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
            from urllib.parse import unquote
            raw = unquote(c) if ("%" in c) else c
            v = json.loads(raw)
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
            from urllib.parse import unquote
            raw = unquote(c) if ("%" in c) else c
            v = json.loads(raw)
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
    """Translate known names/labels inside text nodes (not tags, scripts, styles or form values)."""
    if lang == "en": return html
    rx = _term_re(lang); m = i18n.MAPS[lang]
    parts = _re.split(r"(<script.*?</script>|<style.*?</style>|<textarea.*?</textarea>|<option[^>]*>.*?</option>|<[^>]+>)", html, flags=_re.S)
    for i, part in enumerate(parts):
        if part and not part.startswith("<"):
            parts[i] = rx.sub(lambda mm: m[mm.group(1)], part)
    return "".join(parts)

def page(request, tpl, title, desc, path, **ctx):
    loc = ctx.pop("loc", None) or loc_from(request)
    lang = lang_of(request)
    from ..core import auth
    current_user = auth.get_user_from_request(request.cookies, dict(request.headers))
    resp = templates.TemplateResponse(request, tpl, {"title": title, "desc": desc, "canonical": SITE + path, "lang": lang, "LANGS": i18n.LANGS,
                                                     "path": path, "loc": loc, "current_user": current_user, "locq": urlencode({"city": loc["city"], "lat": loc["lat"], "lon": loc["lon"], "tz": loc["tz"]}), **ctx})
    if lang == "en": return resp
    body = localize_html(resp.body.decode(), lang)
    return HTMLResponse(body, status_code=resp.status_code, headers={"Content-Language": lang})

NAV = [("/", "Home"), ("/mine", "For You"), ("/week", "This Week"), ("/compare", "Two Cities"),
       ("/names", "Names"), ("/sade-sati", "Sade Sati"), ("/panchang", "Daily Panchang"),
       ("/calendar", "Calendar"), ("/festivals", "Festivals"), ("/choghadiya", "Choghadiya"),
       ("/kundli", "Kundli"), ("/destiny", "Destiny & Ravana Mastery"), ("/vargas", "Shodashavargas"), ("/varshaphala", "Varshaphala"), ("/kp", "KP System"),
       ("/prashna", "Prashna"), ("/yogas", "Classical Yogas"), ("/reading", "Vedic Reading"),
       ("/matching", "Matching"), ("/muhurat", "Muhurat"),
       ("/hora", "Hora"), ("/rahu-kaal", "Rahu Kaal"), ("/lagna-table", "Lagna & Gowri"), ("/transits", "Transits"),
       ("/western", "Western Chart"), ("/horoscope", "Horoscope"), ("/numerology", "Numerology"), ("/tarot", "Tarot"),
       ("/human-design", "Human Design"), ("/vastu", "Vastu"), ("/iching", "I-Ching"), ("/palmistry", "Palmistry"), ("/tools", "More Tools"), ("/regional", "Regional Calendars")]
templates.env.globals["NAV"] = NAV

def birth_from_query(request, prefix=""):
    q = request.query_params
    g = lambda k, d=None: q.get(prefix + k, d)
    if not g("date") or not g("lat"):
        return None
    tm = g("time", "12:00")
    return dict(date=g("date"), time=tm if len(tm) > 5 else tm + ":00", latitude=float(g("lat")), longitude=float(g("lon")),
                timezone=g("tz", "Asia/Kolkata"), name=g("name"), city=g("city", ""))

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
        b = birth_from_query(request)
        q = request.query_params
        syl = None
        nak, pada = _opt_int(q.get("nak"), 1, 27), _opt_int(q.get("pada"), 1, 4)
        if b:
            syl = moon_syllable(b["date"], b["time"], b["timezone"])
        elif nak and pada:
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
        b = birth_from_query(request) if q.get("date") and q.get("lat") else None
        sign = None
        moon_name = None
        if b:
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
        return page(request, "calendar.html", f"Hindu Calendar {first.strftime('%B %Y')} – {loc['city']} | {BRAND}",
                    f"Monthly Hindu calendar for {first.strftime('%B %Y')} with tithi, nakshatra and festivals.", "/calendar",
                    loc=loc, cal=cal, lead=lead, first=first, pm=pm, nm=nm, today=t.isoformat())

    def _timing(request, kind):
        loc = loc_from(request); d = qdate(request)
        data = {"choghadiya": RP.choghadiya, "hora": RP.hora}[kind](d, L(loc))
        return loc, d, data

    @app.get("/choghadiya", response_class=HTMLResponse, include_in_schema=False)
    def chog(request: Request):
        loc, d, data = _timing(request, "choghadiya")
        return page(request, "choghadiya.html", f"Choghadiya {d.strftime('%d %b %Y')} – {loc['city']} | {BRAND}",
                    f"Day and night Choghadiya muhurat for {loc['city']}.", "/choghadiya", loc=loc, c=data, d=d,
                    prev=neighbor(d, -1), next=neighbor(d, 1))

    @app.get("/hora", response_class=HTMLResponse, include_in_schema=False)
    def hora(request: Request):
        loc, d, data = _timing(request, "hora")
        return page(request, "hora.html", f"Hora Timings {d.strftime('%d %b %Y')} – {loc['city']} | {BRAND}",
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
        types = ["festival", "ekadashi", "purnima", "amavasya", "sankranti", "pradosh", "sankashti", "shivaratri", "chaturthi", "eclipse"]
        return page(request, "festivals.html", f"Hindu Festivals & Vrat Calendar {y} – {loc['city']} | {BRAND}",
                    f"Complete {y} list of Hindu festivals, Ekadashi, Purnima, Amavasya, Pradosh, Sankranti and eclipses.", "/festivals",
                    loc=loc, months=months, year=y, typ=typ, types=types)

    @app.get("/kundli", response_class=HTMLResponse, include_in_schema=False)
    def kundli(request: Request):
        b = birth_from_query(request); k = None; charts = {}; style = request.query_params.get("style", "north")
        special_lagnas = None; av_suite = None; sudarshan_data = None; varshaphala_data = None; kp_data = None; holistic_reading = None; soul_guidance = None; remedies_corpus = None
        if b:
            req = KundliRequest(**{kk: v for kk, v in b.items() if kk != "city"})
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
                varshaphala_data = RV.varshaphala_endpoint(v_req)
            except Exception:
                varshaphala_data = None
            try:
                kp_req = KPRequest(**{kk: v for kk, v in b.items() if kk != "city"})
                kp_data = RV.kp_endpoint(kp_req)
            except Exception:
                kp_data = None

            try:
                from ..core.remedies_corpus import get_complete_remedies_for_chart
                remedies_corpus = get_complete_remedies_for_chart(k)
                soul_guidance = remedies_corpus.get("soul_guidance")
            except Exception:
                remedies_corpus = None
                soul_guidance = None

        return page(request, "kundli.html", f"Free Kundli (Janam Kundali) Online – {BRAND}",
                    "Free Vedic birth chart with North/South Indian charts, D1–D60 vargas, Vimshottari & Yogini dasha, ashtakavarga, doshas and yogas.",
                    "/kundli", b=b, k=k, charts=charts, style=style, qs=str(request.query_params),
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
        if b:
            req_dict = {kk: v for kk, v in b.items() if kk != "city"}
            req_dict["ayanamsa"] = ayan
            req = KundliRequest(**req_dict)
            vdata = RV.vargas(req)
            fn = {"north": north_indian, "south": south_indian, "east": east_indian}.get(style, north_indian)
            for vk, vinfo in vdata["vargas"].items():
                asc_s = ephem.SIGNS.index(vinfo["ascendant"]["sign_name"])
                pl = [{"name": p["name"], "sign": ephem.SIGNS.index(p["sign_name"]), "retrograde": False} for p in vinfo["planets"]]
                charts[vk] = fn(asc_s, pl, 320, vk)

            taj_res = RV.tajika_sahams_endpoint(req)
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
        if b:
            req_dict = {kk: v for kk, v in b.items() if kk != "city"}
            req_dict["ayanamsa"] = ayan
            req = KundliRequest(**req_dict)
            ydata = RV.comprehensive_yogas_endpoint(req)
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
        if b:
            req_dict = {kk: v for kk, v in b.items() if kk != "city"}
            req_dict["ayanamsa"] = ayan
            req = KundliRequest(**req_dict)
            rdata = RV.holistic_reading_endpoint(req)
            cur_dasha = RV.current_dasha_endpoint(req)
            karakas = RV.chara_karakas_endpoint(req)
            corpus_data = RV.planetary_placements_corpus(req)
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
        if b:
            v_req = VarshaphalaRequest(**{kk: v for kk, v in b.items() if kk != "city"}, year=year)
            vdata = RV.varshaphala_endpoint(v_req)
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
        if b:
            kp_req = KPRequest(**{kk: v for kk, v in b.items() if kk != "city"}, horary_number=horary_number)
            kp_data = RV.kp_endpoint(kp_req)
        return page(request, "kp.html", f"Krishnamurti Paddhati (KP System Astrology) | {BRAND}",
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
            pdata = RV.prashna_endpoint(p_req)

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
        if b:
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
        name = q.get("name") or (b.get("name") if b else "") or "Soul Seeker"
        dob_str = q.get("dob") or (b.get("date") if b else "") or "1990-05-15"
        system = q.get("system", "pythagorean")
        lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b else None)
        lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b else None)
        tm = q.get("time") or (b.get("time") if b else "12:00:00")
        tz = q.get("tz") or (b.get("timezone") if b else "Asia/Kolkata")
        if dob_str:
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
        name = q.get("name") or (b.get("name") if b else "") or "Aryabhata"
        dob_str = q.get("date") or q.get("dob") or (b.get("date") if b else "") or "1990-05-15"
        tm_str = q.get("time") or (b.get("time") if b else "08:30:00")
        if len(tm_str) == 5:
            tm_str += ":00"
        b_lat = float(q["lat"]) if q.get("lat") else (b.get("latitude") if b else 28.6139)
        b_lon = float(q["lon"]) if q.get("lon") else (b.get("longitude") if b else 77.2090)
        b_tz = q.get("tz") or (b.get("timezone") if b else "Asia/Kolkata")
        b_city = q.get("city") or (b.get("city") if b else "New Delhi, India")

        c_lat = float(q["cur_lat"]) if q.get("cur_lat") else loc["lat"]
        c_lon = float(q["cur_lon"]) if q.get("cur_lon") else loc["lon"]
        c_tz = q.get("cur_tz") or loc["tz"]
        c_city = q.get("cur_city") or loc["city"]
        scan_days = int(q.get("scan_days", 30)) if str(q.get("scan_days", "30")).isdigit() else 30

        dossier = None
        try:
            d_obj = Date.fromisoformat(dob_str)
            t_obj = datetime.strptime(tm_str, "%H:%M:%S").time()
            tz_b = ephem.make_tz(b_tz, None)
            dt_utc = datetime.combine(d_obj, t_obj).replace(tzinfo=tz_b).astimezone(timezone.utc)
            dossier = compute_master_destiny_dossier(
                dt_utc, b_lat, b_lon, b_tz, None, name=name,
                current_lat=c_lat, current_lon=c_lon, current_tz_name=c_tz,
                current_city=c_city, scan_days=min(max(scan_days, 7), 90)
            )
        except Exception:
            pass
        return page(
            request, "destiny.html",
            f"Master Destiny, Ravana Planetary Control, Lottery, Longevity & Past/Future Life – {BRAND}",
            "Cross-linked Vedic astrology oracle: diseases, longevity, accident dates & hours, lottery luck, marriage count, children & grandchildren, past/future life, and Ravana Samhita 9-planet control.",
            "/destiny", dossier=dossier, q=q, b=b,
            form={"name": name, "date": dob_str, "time": tm_str[:5], "lat": b_lat, "lon": b_lon, "tz": b_tz, "city": b_city,
                  "cur_lat": c_lat, "cur_lon": c_lon, "cur_tz": c_tz, "cur_city": c_city, "scan_days": scan_days}
        )

    @app.get("/tarot", response_class=HTMLResponse, include_in_schema=False)
    def tarot(request: Request):
        q = request.query_params; sp = q.get("spread", "three_card")
        t = RX.tarot(sp if sp in ("single", "yes_no", "three_card", "love", "celtic_cross") else "three_card", q.get("question"), q.get("seed"))
        return page(request, "tarot.html", f"Tarot Reading – {BRAND}", "Free tarot card reading.", "/tarot", t=t, sp=sp, q=q)

    @app.get("/human-design", response_class=HTMLResponse, include_in_schema=False)
    def human_design(request: Request):
        b = birth_from_query(request); hd = None
        if b: hd = RM.human_design(BirthData(**{kk: v for kk, v in b.items() if kk not in ("city", "name")}))
        return page(request, "humandesign.html", f"Human Design Chart Calculator – {BRAND}", "Free Human Design bodygraph: type, strategy, authority, profile, centers, channels and gates.",
                    "/human-design", b=b, hd=hd, CENTERS=list(HDM.CENTERS))

    @app.get("/vastu", response_class=HTMLResponse, include_in_schema=False)
    def vastu(request: Request):
        q = request.query_params
        layout = {r: q.get("room_" + r.replace(" ", "_")) for r in ESO.ROOM_BEST if q.get("room_" + r.replace(" ", "_"))}
        v = ESO.vastu(layout or None, q.get("facing"))
        return page(request, "vastu.html", f"Vastu Shastra Guide & Home Checker – {BRAND}", "Vastu directions, deities and elements with a room placement score.",
                    "/vastu", v=v, q=q, rooms=list(ESO.ROOM_BEST), dirs=list(ESO.VASTU))

    @app.get("/iching", response_class=HTMLResponse, include_in_schema=False)
    def iching(request: Request):
        q = request.query_params; c = ESO.iching_cast(q.get("question"), q.get("seed")) if (q.get("question") or q.get("cast")) else None
        return page(request, "iching.html", f"I-Ching Oracle – {BRAND}", "Cast an I-Ching hexagram with the three-coin method; all 64 hexagrams.",
                    "/iching", c=c, q=q, all=ESO.iching_all())

    @app.get("/palmistry", response_class=HTMLResponse, include_in_schema=False)
    def palmistry(request: Request):
        q = request.query_params
        r = ESO.palmistry(q.get("hand_shape"), q.get("heart"), q.get("head"), q.get("life"), q.get("fate"))
        return page(request, "palmistry.html", f"Palmistry Guide – {BRAND}", "Hand shapes, palm lines and mounts explained, with a reading from your features.",
                    "/palmistry", r=r, q=q)

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
        sid = q.get("siddhanta") if q.get("siddhanta") in ("surya", "vakya") else "drik"
        jn = int(q["janma_nakshatra"]) if q.get("janma_nakshatra", "").isdigit() else None
        ctx = {"r": RR.regional_calendar(d, loc["lat"], loc["lon"], loc["tz"], siddhanta=sid),
               "ny": RR.regional_new_years(d.year, loc["lat"], loc["lon"], loc["tz"], siddhanta=sid),
               "md": MDZ.day_doshas(d, loc["lat"], loc["lon"], loc["tz"], janma_nakshatra=jn), "fr": FRZ.RULES, "vk": __import__("app.core.vakya", fromlist=["x"]).vakya_panchang(d, loc["lat"], loc["lon"], loc["tz"]), "pk": __import__("app.core.punya_kaal", fromlist=["x"]).year_punya_kaal(d.year, loc["lat"], loc["lon"], loc["tz"]), "d": d, "sid": sid, "jn": jn, "loc": loc}
        return page(request, "regional.html", f"Regional Calendars, Panchaka & Muhurta Doshas – {BRAND}",
                    "Tamil, Malayalam, Bengali, Assamese, Odia, Gujarati and Marathi calendar dates, Vakya/Surya Siddhanta option, Panchaka, Bhadra and festival rules.",
                    "/regional", **ctx)

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
        urls = [p for p, _ in NAV] + ["/api/docs"]
        y = Date.today().year
        urls += [f"/festivals?year={yy}" for yy in (y - 1, y, y + 1)]
        body = "".join(f"<url><loc>{SITE}{u.replace('&', '&amp;')}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq></url>" for u in urls)
        return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>', media_type="application/xml")

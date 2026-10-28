"""Regional month grids, named calendars, guides, sky and remedy pages."""
from __future__ import annotations
from datetime import date as Date, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from ..core import ephem
from ..core.ephem import SIGNS, make_tz, moon_lon, calc, swe, local_midnight_jd, fmt
from ..core.panchang import day_events, RITUS
from ..core.regional_rules import regional_calendar, solar_date
from ..core.library_text import GUIDES, GEMS, MUKHI, LYRICS
from ..core import calendar as C

NEPALI = ["Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"]
PANJI = {
    "odia": "Odia Panji",
    "telugu": "Telugu Panchangam",
    "vinchudo": "Gujarati Vinchudo",
    "nepali": "Nepali Patro",
    "chandrabalam": "Chandrabalam",
}
OBSERVE = {
    "diwali": ("Diwali calendar", ("diwali", "narak", "kali", "govardhan", "bhai", "dhanteras", "lakshmi")),
    "durga": ("Durga Puja calendar", ("durga", "navami", "vijaya", "dussehra", "ashtami")),
    "navratri": ("Navratri calendar", ("navratri", "durga", "navami", "vijaya")),
}
GOOD = {1, 3, 6, 7, 10, 11}
ORBS = {"Mercury": 13, "Venus": 10, "Mars": 17, "Jupiter": 11, "Saturn": 15}


def _cell(kind, d, lat, lon, tz, janma):
    r = regional_calendar(d, lat, lon, tz)
    if kind == "odia":
        x = r["odia"]
        return f"{x['month']} {x['day']}", f"San {x['san']}"
    if kind == "telugu":
        x = r["telugu_kannada"]
        return x["month"], f"Shaka {x['shaka_samvat']}"
    if kind == "vinchudo":
        x = r["gujarati"]
        return x["month"], f"VS {x['vikram_samvat']}"
    if kind == "nepali":
        s, day, start, _ = solar_date(d, "odia", lat, lon, make_tz(tz))
        # Bikram Sambat: year flips at Mesha sankranti (Baisakh 1), about mid-April.
        ny = Date.fromisoformat(start) if s == 0 else None
        bs = d.year + 57 if (d.month, d.day) >= (4, 14) else d.year + 56
        if ny and d >= ny and s == 0:
            bs = d.year + 57
        return f"{NEPALI[s]} {day}", f"BS {bs}"
    ev = day_events(d, lat, lon, make_tz(tz))
    moon = int(moon_lon(ev["sunrise"]) // 30)
    if janma is None:
        return SIGNS[moon], "Moon’s rashi"
    house = (moon - janma) % 12 + 1
    return SIGNS[moon], ("Good" if house in GOOD else "Weak") + f" · house {house}"


def mount(app: FastAPI, page, loc_from, year_of, qdate, L):
    @app.get("/panji/{kind}", response_class=HTMLResponse, include_in_schema=False)
    def panji(request: Request, kind: str):
        if kind not in PANJI:
            kind = "odia"
        loc = loc_from(request)
        t = Date.today()
        y = year_of(request)
        m = int(request.query_params.get("month", t.month))
        if not 1 <= m <= 12:
            m = t.month
        first = Date(y, m, 1)
        nxt = Date(y + 1, 1, 1) if m == 12 else Date(y, m + 1, 1)
        prev = Date(y - 1, 12, 1) if m == 1 else Date(y, m - 1, 1)
        lead = (first.weekday() + 1) % 7
        jn = request.query_params.get("rashi")
        janma = int(jn) if jn and jn.isdigit() and 0 <= int(jn) < 12 else None
        days = []
        d = first
        while d < nxt:
            title, sub = _cell(kind, d, loc["lat"], loc["lon"], loc["tz"], janma)
            days.append({"date": d.isoformat(), "n": d.day, "title": title, "sub": sub, "today": d == t})
            d += timedelta(days=1)
        return page(request, "panji.html", f"{PANJI[kind]} – {first.strftime('%B %Y')} | PanchangHub",
                    f"{PANJI[kind]} for {loc['city']}.", f"/panji/{kind}",
                    loc=loc, kind=kind, label=PANJI[kind], first=first, prev=prev, nxt=nxt,
                    lead=lead, days=days, signs=list(enumerate(SIGNS)), janma=janma)

    @app.get("/observe/{slug}", response_class=HTMLResponse, include_in_schema=False)
    def observe(request: Request, slug: str):
        if slug not in OBSERVE:
            slug = "diwali"
        title, keys = OBSERVE[slug]
        loc = loc_from(request)
        y = year_of(request)
        ev = C.year_festivals(y, loc["lat"], loc["lon"], loc["tz"])["events"]
        rows = [e for e in ev if any(k in e["name"].lower() for k in keys)]
        return page(request, "observe.html", f"{title} {y} | PanchangHub", title, f"/observe/{slug}",
                    loc=loc, heading=title, year=y, rows=rows, slug=slug)

    @app.get("/guide/{slug}", response_class=HTMLResponse, include_in_schema=False)
    def guide(request: Request, slug: str):
        if slug not in GUIDES:
            slug = "dashavatara"
        title, blocks = GUIDES[slug]
        extra = None
        if slug == "pachchakkhan":
            loc = loc_from(request)
            ev = day_events(qdate(request), loc["lat"], loc["lon"], make_tz(loc["tz"]))
            extra = fmt(ev["sunset"], make_tz(loc["tz"]))
        else:
            loc = loc_from(request)
        return page(request, "guide.html", f"{title} | PanchangHub", title, f"/guide/{slug}",
                    loc=loc, heading=title, blocks=blocks, extra=extra)

    @app.get("/pachchakkhan", response_class=HTMLResponse, include_in_schema=False)
    def pachchakkhan(request: Request):
        return guide(request, "pachchakkhan")

    @app.get("/sky/{kind}", response_class=HTMLResponse, include_in_schema=False)
    def sky(request: Request, kind: str):
        loc = loc_from(request)
        tz = make_tz(loc["tz"])
        d = qdate(request)
        jd = local_midnight_jd(d, tz) + 0.5
        pos = {name: calc(jd, body, True) for name, body in ephem.PLANETS.items() if name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")}
        sun = pos["Sun"][0]
        rows = []
        if kind == "combust":
            title = "Planet combustion"
            for name, (lon, lat, sp) in pos.items():
                if name in ("Sun", "Moon"):
                    continue
                dist = abs((lon - sun + 180) % 360 - 180)
                rows.append({"name": name, "sign": SIGNS[int(lon // 30)], "note": f"{dist:.1f}° from the Sun", "flag": "Combust" if dist < ORBS[name] else "Clear"})
        elif kind == "retro":
            title = "Retrograde planets"
            for name, (lon, lat, sp) in pos.items():
                if name == "Sun":
                    continue
                rows.append({"name": name, "sign": SIGNS[int(lon // 30)], "note": f"speed {sp:.3f}°/day", "flag": "Retrograde" if sp < 0 else "Direct"})
        elif kind == "solstice":
            title = "Solstices and equinoxes"
            t0 = local_midnight_jd(Date(d.year, 1, 1), tz)
            marks = ((0, "March equinox"), (90, "June solstice"), (180, "September equinox"), (270, "December solstice"))
            prev = calc(t0, swe.SUN, False)[0]
            for i in range(1, 370):
                lon = calc(t0 + i, swe.SUN, False)[0]
                span = (lon - prev) % 360
                for ang, label in marks:
                    if ((ang - prev) % 360) <= span + 0.05:
                        rows.append({"name": label, "sign": "Tropical", "note": fmt(t0 + i, tz)[:16].replace("T", " "), "flag": "Sun"})
                prev = lon
            seen = set()
            rows = [r for r in rows if not (r["name"] in seen or seen.add(r["name"]))]
        else:
            kind = "seasons"
            title = "Indian seasons"
            sun_sign = int(sun // 30)
            ritu = RITUS[sun_sign // 2]
            pairs = [("Vasanta", "Mesha, Vrishabha"), ("Grishma", "Mithuna, Karka"), ("Varsha", "Simha, Kanya"),
                     ("Sharad", "Tula, Vrishchika"), ("Hemanta", "Dhanu, Makara"), ("Shishira", "Kumbha, Meena")]
            rows = [{"name": a, "sign": b, "note": "Sun is here" if a == ritu else "", "flag": "Now" if a == ritu else ""} for a, b in pairs]
        return page(request, "sky.html", f"{title} | PanchangHub", title, f"/sky/{kind}",
                    loc=loc, heading=title, rows=rows, day=d, kind=kind)

    @app.get("/gemstone", response_class=HTMLResponse, include_in_schema=False)
    def gemstone(request: Request):
        loc = loc_from(request)
        rashi = request.query_params.get("rashi")
        idx = int(rashi) if rashi and rashi.isdigit() and 0 <= int(rashi) < 12 else None
        if idx is None:
            ev = day_events(qdate(request), loc["lat"], loc["lon"], make_tz(loc["tz"]))
            idx = int(moon_lon(ev["sunrise"]) // 30)
            src = "today’s Moon"
        else:
            src = "the rashi you chose"
        g = GEMS[idx]
        return page(request, "remedy.html", f"Gemstone – {g[2]} | PanchangHub", "Navaratna by rashi.", "/gemstone",
                    loc=loc, kind="gem", signs=list(enumerate(SIGNS)), idx=idx, src=src, row=g, table=GEMS)

    @app.get("/rudraksha", response_class=HTMLResponse, include_in_schema=False)
    def rudraksha(request: Request):
        loc = loc_from(request)
        rashi = request.query_params.get("rashi")
        idx = int(rashi) if rashi and rashi.isdigit() and 0 <= int(rashi) < 12 else None
        if idx is None:
            ev = day_events(qdate(request), loc["lat"], loc["lon"], make_tz(loc["tz"]))
            idx = int(moon_lon(ev["sunrise"]) // 30)
            src = "today’s Moon"
        else:
            src = "the rashi you chose"
        return page(request, "remedy.html", "Rudraksha | PanchangHub", "A customary mukhi for each rashi.", "/rudraksha",
                    loc=loc, kind="rudraksha", signs=list(enumerate(SIGNS)), idx=idx, src=src, mukhi=MUKHI[idx], table=GEMS)

    @app.get("/sahasra", response_class=HTMLResponse, include_in_schema=False)
    def sahasra(request: Request):
        loc = loc_from(request)
        raw = request.query_params.get("birth")
        found = None
        if raw:
            try:
                b = Date.fromisoformat(raw)
            except ValueError:
                b = None
            if b:
                tz = make_tz(loc["tz"])
                n = 0
                d = b
                for _ in range(1100):
                    ev = day_events(d, loc["lat"], loc["lon"], tz)
                    mr = ev.get("moonrise")
                    if mr and ev["sunrise"] <= mr < ev["next_sunrise"]:
                        n += 1
                        if n == 1000:
                            found = {"date": d.isoformat(), "when": fmt(mr, tz), "count": n}
                            break
                    d += timedelta(days=1)
                    if d.year > ephem.YEAR_MAX:
                        break
        return page(request, "remedy.html", "Sahasra Chandrodaya | PanchangHub",
                    "The thousandth moonrise from a birth date.", "/sahasra",
                    loc=loc, kind="sahasra", found=found, birth=raw or "", signs=[], idx=0, src="", table=[])

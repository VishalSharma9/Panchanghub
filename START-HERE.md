# PanchangHub — start here

This zip is the whole running product. Nothing the site needs was left out: Python source, HTML, CSS, JavaScript, Swiss Ephemeris files, the 5.17 million place database, tests, accuracy notes, research notes, and both SDKs. The only thing not included is `.venv`. That folder is a local Python install. Recreate it with the commands below. `__pycache__` is also omitted. Python rebuilds it.

There are two folders. They are not two products. One process loads both.

```
api/        the calculation engine and the HTTP API
website/    the pages people see
```

## What is what

### `api/` — the engine and the REST API

Run this. It is a Python package named `app`.

| Path | What it is |
|---|---|
| `api/app/main.py` | Creates the FastAPI app, mounts every router under `/api`, then calls `register()` so the website routes exist on the same app. |
| `api/app/api/routers/` | One file per group of HTTP endpoints. These functions are the API. |
| `api/app/api/deps.py` | Shared request parsing: dates, timezones, birth bodies. |
| `api/app/api/__init__.py` | The list `ROUTERS`. Add a new router file and put its name here. |
| `api/app/core/` | The formulas. Routers and pages call this. Do not copy a formula into a template or into JavaScript. |
| `api/app/models.py` | JSON bodies for kundli, matching, charts. |
| `api/app/web/__init__.py` | The website’s Python. It lives on the API side because it imports the routers. It does not contain HTML. |
| `api/data/places.sqlite` | GeoNames populated places, about 5.17 million rows, plus an FTS5 search index. About 1.1 GB. Required. |
| `api/data/cities.json` | Small fallback used only if the sqlite file is missing. |
| `api/data/build_places.py` | Rebuilds `places.sqlite` from a GeoNames `allCountries.zip`. Do not run it unless the place set is wrong. |
| `api/ephe/` | Swiss Ephemeris files `sepl_18.se1`, `semo_18.se1`, `seas_18.se1` (about 1800–2399). Outside that span the code uses the built-in Moshier ephemeris so year 1 and year 3000 still answer. |
| `api/requirements.txt` | Python dependencies. |
| `api/tests/` | pytest. Run from `api/`. |
| `api/accuracy/` | Notes and rows from the Drik timing comparison. Read before changing `app/core/ephem.py`. |
| `api/research/` | Which texts the rules came from, and which commercial APIs were compared. |
| `api/sdk/` | Thin Python and JavaScript clients for the HTTP API. |
| `api/AGENT_REVIEW.md` | Deeper file-by-file map, accuracy rules, and the safe upgrade list. Read it before editing formulas. |
| `api/README.md` | Endpoint examples. |

### `website/` — what the browser renders

| Path | What it is |
|---|---|
| `website/templates/` | Jinja HTML. `base.html` is the header, location bar, and nav. Every other file is one page. |
| `website/static/style.css` | Kumkum / haldi / cream. Do not restyle the brand. |
| `website/static/app.js` | City search, geolocation, timezone fallback, language cookie, civil clock, Vedic clock. |
| `website/static/embed.js` | The snippet for `/widget/panchang`. |
| `website/static/logo.svg`, `favicon.svg` | Brand marks. |
| `website/PAGES.md` | One paragraph per page: the URL, the template, and which API function fills it. |

## How they are connected

One uvicorn process. One port. The website is not a second server and it does not recompute the planets.

```
Browser
  │
  ├─ GET /panchang          website page
  │     api/app/web/__init__.py
  │       calls RP.panchang(...)          ← the same function
  │             │
  │             ▼
  │     api/app/api/routers/panchang.py
  │             │
  │             ▼
  │     api/app/core/panchang.py          ← sunrise, tithi, Rahu, and the rest
  │             │
  │             ▼
  │     Jinja reads website/templates/panchang.html
  │
  └─ GET /api/panchang      same function, JSON instead of HTML
```

Pages that need a city name from the keyboard do not go through Jinja for that. `website/static/app.js` calls the public API:

| Browser call | API | Then |
|---|---|---|
| `GET /api/cities?q=` | `api/app/api/routers/geo.py` search | User picks a row. JS writes cookie `ph_loc` and reloads. |
| `GET /api/cities/nearest?lat&lon` | nearest populated place | Used after GPS permission. |
| `GET /api/cities/timezone?tz=` | largest place in that IANA timezone | Used when GPS is denied. The page must not stop on “Location blocked”. |
| `POST /api/kundli/pdf` | PDF bytes | The kundli page’s download button. |

`api/app/web/__init__.py` finds the HTML like this:

- If a sibling folder `website/templates` exists (this zip), it uses that.
- Otherwise it uses `web/templates` next to `app/` (the original single-folder tree).

City data and ephemeris stay inside `api/` because the routers look next to the `app` package: `api/data`, `api/ephe`.

## How to run

From the `api` folder, so Python can import `app`:

```bash
cd api
python3 -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# pyswisseph needs a C compiler and Python headers
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Then open `http://127.0.0.1:8080/`.

- Swagger: `http://127.0.0.1:8080/api/docs`
- Health: `http://127.0.0.1:8080/health`
- Tests, from `api/`: `pytest -q`

Do not start a second server for the website. If the HTML folder is missing, pages 500 and `/api/...` still works. If `places.sqlite` is missing, city search falls back to the short `cities.json` list.

Docker, from this zip’s root (the Dockerfile next to `api/` and `website/`, not `api/Dockerfile`):

```bash
docker build -t panchanghub .
docker run -p 8080:8000 panchanghub
```

`api/Dockerfile` is the older single-folder image. It is included so nothing was thrown away. Use the root Dockerfile for this layout.

## Cookies, not accounts

There is no login. Do not add passwords unless the product owner asks.

| Cookie | Meaning |
|---|---|
| `ph_loc` | Chosen place: city, lat, lon, IANA tz, and how it was chosen (`gps`, `search`, `timezone`). |
| `ph_janma` | Birth rashi 1–12 and birth nakshatra 1–27. |
| `ph_lang` | `en` or `hi mr gu bn ta te kn ml`. |
| `ph_loc2` | Second place on `/compare`. |

The website passes birth rashi and nakshatra as 1-based numbers into `RP.panchang`. The router subtracts 1. Do not subtract again in the page.

Until a place is chosen, calculations use New Delhi only as a numeric fallback. The header must not say the user is in New Delhi. GPS first, then the browser timezone’s largest city, then the search box.

## Pages and the functions they call

The full paragraph for each page is `website/PAGES.md`. Short version:

| URL | Template | Calls into the API |
|---|---|---|
| `/` | `home.html` | `RP.panchang`, `RP.choghadiya`, `RC.festivals` |
| `/panchang` | `panchang.html` | `RP.panchang`, `RX.regional` |
| `/mine` | `mine.html` | `RP.panchang`, `RP.choghadiya`, `for_you()` |
| `/week` | `week.html` | same, seven days |
| `/compare` | `compare.html` | `RP.panchang` twice |
| `/names` | `names.html` | `moon_syllable()` / `syllable()` |
| `/sade-sati` | `sade.html` | `kundli.sade_sati` |
| `/calendar` | `calendar.html` | `RC.month` |
| `/choghadiya` | `choghadiya.html` | `RP.choghadiya` |
| `/hora` | `hora.html` | `RP.hora` |
| `/rahu-kaal` | `rahu.html` | `RP.rahu_kaal` |
| `/lagna-table` | `lagna.html` | `RP.lagna`, `RP.gowri` |
| `/festivals` | `festivals.html` | `RC.festivals` |
| `/festivals.ics` | none | `RC.festivals` as a calendar file |
| `/kundli` | `kundli.html` | `RV.kundli` |
| `/matching` | `matching.html` | `RV.matching` |
| `/muhurat` | `muhurat.html` | `RC.muhurat` |
| `/transits` | `transits.html` | `RC.transits`, `RCore.planets`, `RX.moon_phases` |
| `/western` | `western.html` | `RCore.chart` |
| `/horoscope` | `horoscope.html` | `RX.horoscope` |
| `/numerology` | `numerology.html` | `RX.numerology` |
| `/tarot` | `tarot.html` | `RX.tarot_daily` |
| `/human-design` | `humandesign.html` | Human Design chart |
| `/vastu` | `vastu.html` | Vastu guide |
| `/iching` | `iching.html` | I Ching cast |
| `/palmistry` | `palmistry.html` | Palmistry reference |
| `/tools` | `tools.html` | Mayan, Chinese, Kabbalah, dreams, crystals |
| `/regional` | `regional.html` | regional, vakya, punya, dosha routers |
| `/widget/panchang` | `widget.html` | `RP.panchang` |

`for_you`, `syllable`, and `moon_syllable` live in `api/app/core/for_you.py`. They are not separate HTTP routes. The pages call them in-process. If you expose them, add a thin router that calls those same functions.

## API groups

All under `/api` except the five core paths, which also exist at the site root (`/health`, `/chart`, `/planets`, `/zodiac/{sign}`, `/nakshatra`).

| File | Routes it owns |
|---|---|
| `api/app/api/routers/core.py` | health, chart, planets, zodiac, nakshatra |
| `api/app/api/routers/panchang.py` | daily panchang, choghadiya, hora, gowri, lagna, Rahu |
| `api/app/api/routers/calendar.py` | festivals, month, eclipses, transits, muhurat search |
| `api/app/api/routers/geo.py` | city search, nearest, timezone, stats |
| `api/app/api/routers/vedic.py` | kundli, matching |
| `api/app/api/routers/regional.py` | regional calendars, vakya, punya kaal, doshas |
| `api/app/api/routers/extras.py` | KP, Jaimini, Lal Kitab, Varshaphal, SVG, PDF, horoscope, numerology, tarot, Chinese, Western relationships |
| `api/app/api/routers/more.py` | shadbala, interpretations, remedies, Human Design, Vastu, palmistry, I Ching, `POST /ask`, `POST /mcp` |

`POST /api/ask` matches keywords onto those endpoints. It is not a language model. Do not make it invent an answer the engines did not compute.

Swagger (`/api/docs`) is the parameter list. Do not keep a second list in a comment that will go stale.

## Rules for anyone improving this

1. Change a number in `api/app/core/`. Then expose it from a router. Then show it in `website/templates/` by calling that router. Three layers, one result.
2. Dates run from year 1 through year 3000. One muhurat search may cover 3660 days (10 years). Do not put the old “0..400 days” message back.
3. Sunrise is the upper limb with refraction. Moonrise is disc centre. That is the Drik match. Do not “correct” it.
4. Leave `PANCHANGHUB_STRICT_DT` unset. Setting it to `1` turns off the Drik time convention.
5. Do not invent Baana, Kumbha chakra, Lumbaka, Netrama, a Rahu-direction clock, baby-name lists, or an auspiciousness percentage. Those were looked up and no source checked out. A guessed table is worse than a missing row.
6. Keep the kumkum / haldi / cream colours.
7. After a Python change, restart uvicorn. After a CSS or JS change, bump the `?v=` on the stylesheet and script tags in `website/templates/base.html`.
8. The deep upgrade list (saved birth on the device, print stylesheet, timezone index, local eclipse circumstances, gochar on the home card) is in `api/AGENT_REVIEW.md`.

## This file list

`FILES.txt` at the root of this zip is every path that was packed and its size in bytes. If a tool shows this zip as a few dozen megabytes, it is showing compressed disk blocks, not the contents. The place database alone is about 1.1 GB uncompressed. After unzip, `api/data/places.sqlite` must be about 1,111,879,680 bytes.

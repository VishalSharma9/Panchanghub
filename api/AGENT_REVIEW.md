# PanchangHub — agent review guide

Read this before changing anything. It is the map of the running product: one FastAPI process that is both the public website and the REST API. They share the same calculation code. Do not fork a second copy of the astronomy.

Brand: **PanchangHub**. Sidereal Lahiri (Chitrapaksha), calibrated against canonical Drik Ganita astronomical standards. Dates from **1 CE through 3000 CE**. City search is the Global Gazetteer populated-place set (about 5.17 million), not a short city list.

## 1. How to run

From this folder (`panchanghub/`):

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # needs gcc and Python headers for pyswisseph
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

- Website: `http://127.0.0.1:8080/`
- Swagger: `http://127.0.0.1:8080/api/docs`
- ReDoc: `/api/redoc` · OpenAPI: `/api/openapi.json`
- Health: `GET /health` and `GET /api/health`
- Tests: `pytest -q`

The preview sandbox starts the same app with `/workspace/startup.sh` on port **8080**. After a Python change, restart that process. Jinja and static files are read from disk; `web/templates/base.html` loads `/static/app.js?v=16` and `/static/style.css?v=16`. **Bump that query string** when you edit `web/static/app.js` or `style.css`, or browsers keep the old file.

`places.sqlite` is about 1.1 GB. It is required for city search. `data/cities.json` is only a small fallback if the sqlite file is missing. Do not delete the sqlite file. Do not commit a second copy of it.

High-Precision Planetary Ephemeris files in `ephe/` cover roughly 1800–2399 (planets, Moon, asteroids). Outside that span the engine falls back to the built-in Moshier ephemeris. That is intentional so year 1 and year 3000 still answer.

## 2. How the API connects to the website

There is one app object: `app/main.py` builds FastAPI, mounts every router in `app/api/__init__.py` under `/api`, and then `app/web/__init__.py` `register()` adds the HTML routes.

```
Browser
  │
  ├─ HTML page (Jinja)  ──calls──►  app.api.routers.* functions directly
  │                                 (same Python the HTTP API uses)
  │
  └─ web/static/app.js  ──fetch──►  /api/cities, /api/cities/nearest, /api/cities/timezone
                                    /api/kundli/pdf  (download button)
```

Rules:

1. A website page must call the router function (`RP.panchang`, `RC.festivals`, `RV.kundli`, …), not reimplement tithi or sunrise in the template or in JavaScript.
2. Those router functions are also the HTTP handlers. `GET /api/panchang` and the home page run `compute_panchang` in `app/core/panchang.py`.
3. Routers listed in `ROOT_ALIASES` (`core` only) are mounted twice: `/health` and `/api/health`, `/chart` and `/api/chart`, and the same for `/planets`, `/zodiac/{sign}`, `/nakshatra`. Every other endpoint is **only** under `/api`.
4. HTML routes are `include_in_schema=False`. They do not appear in Swagger. The website-only feeds are `/festivals.ics` and `/widget/panchang`.
5. `?lang=hi|mr|gu|bn|ta|te|kn|ml` on a JSON endpoint is translated by `lang_middleware` in `app/main.py` via `app/core/i18n.py`. HTML pages do the same after render, in `localize_html()`, using the `ph_lang` cookie. Do not translate inside `<script>`, `<style>`, or form control values (the splitter already skips those).
6. Location, birth star, and language are cookies, not accounts. There is no login. Do not add passwords unless the product owner asks. See section 5.

Adding a feature the right way:

1. Put the formula in `app/core/<module>.py` with a comment naming the rule (which houses, which table).
2. Expose it from a router in `app/api/routers/`. Register the module name in `app/api/__init__.py` `ROUTERS` if it is a new file.
3. Add a Jinja page in `web/templates/` and a route in `register()` that calls that router function.
4. Add a nav entry in `NAV` and a link in `web/templates/base.html` (the top bar only shows `NAV[:13]`; the sidebar is handwritten).
5. Add a pytest that hits `/api/...` with a fixed lat/lon/date.

## 3. Request flow for one day

`GET /` and `GET /panchang` both end in `app.core.panchang.compute_panchang`.

Inputs: civil date, latitude, longitude, IANA timezone (or a numeric `utc_offset`), optional altitude, optional janma rashi **1–12** and janma nakshatra **1–27**.

The panchang router subtracts 1 before the core sees them. The website passes **1-based** values into `RP.panchang(...)`. **Do not subtract again in the website.** That bug already happened once and shifted Chandrabala by a sign.

The core:

- Builds a timezone with `ephem.make_tz`.
- Sunrise, sunset, moonrise, moonset from High-Precision Planetary Ephemeris (`day_events`). Sunrise is the upper limb with refraction. Moonrise is disc centre. This matches Drik, not “geometric centre of the Sun”.
- Tithi, nakshatra, yoga, karana, pada, moon sign are windows from one sunrise to the next sunrise, not midnight to midnight. A page can show two tithis.
- Muhurta windows (Rahu, Yamaganda, Gulika, durmuhurtam, varjyam, Abhijit, Brahma, Godhuli, Amrit) are in `compute_panchang` and `day_extras.py`.
- `day_extras.py` adds Pravishte/gate, Vedic ghati, Pancha Pakshi, Mantri Mandala, Agnivasa, Chandra vasa, Shivavasa, Homahuti, Tamil yoga, Aadal, do-ghati names.
- `personal` is Chandrabala (favourable houses 1, 3, 6, 7, 10, 11 from the birth sign) and Tarabala (nine-tara cycle). Favourable taras are the ones whose count mod 9 is in `{2, 4, 6, 8, 0}` (Sampat, Kshema, Sadhana, Mitra, Parama Mitra — the usual “good” set). Ashtama is the 8th from the birth sign.

Returned times are ISO-8601 with the local offset. Templates print them with the `hm` filter (`web/__init__.py`), which shows 12-hour time and adds the next day’s date when the instant is after midnight.

## 4. Location (read this before touching the header)

The user must not see a hardcoded “New Delhi” as if it were their city. `DEFAULT_LOC` in `app/web/__init__.py` is only the calculation fallback **before** the browser resolves a place. The label in that state is “Detecting your location…”, not “New Delhi”.

Resolution order in `loc_from()`:

1. Query `lat` and `lon` (plus optional `city`, `tz`) → source `query`.
2. Cookie `ph_loc` (JSON) → source `saved`, `gps`, `timezone`, or `search`.
3. Else `DEFAULT_LOC` with source `default`.

`web/static/app.js` then, only when `data-source="default"`:

1. If `localStorage.ph_loc` exists, reuse it and reload.
2. Else `navigator.geolocation`. On success, `GET /api/cities/nearest` and save cookie + localStorage with `src: "gps"`. The timezone saved is `Intl.DateTimeFormat().resolvedOptions().timeZone`, not the city’s zone from the database, so DST matches the device.
3. If permission is denied, missing, or times out: `GET /api/cities/timezone?tz=<browser IANA zone>`, which returns the **largest** populated place in that zone (`src: "timezone"`). The bar must say the place came from the timezone and that search can correct it. Do not leave the user on the text “Location blocked”.
4. If that lookup 404s (for example timezone `UTC`, which has no Global Gazetteer row), focus the search box and say so. The clock still runs, using the browser zone while the page is in the pending state.

Search box: `GET /api/cities?q=&limit=`. SQLite FTS5 (`places_fts`), then reranked so an exact city name beats a hamlet, with population as the tie-break. Picking a row writes `ph_loc` and reloads.

`Permissions-Policy: geolocation=(self)` is set in `app/main.py`. An embedded preview often still denies GPS. The timezone fallback is what makes that preview usable. Do not remove it.

Second place for `/compare` is cookie `ph_loc2`, query `lat2,lon2,tz2,city2`. Birth star is cookie `ph_janma` = `{"rashi": 1-12, "nak": 1-27}`. Language is `ph_lang`.

## 5. No accounts

Do not add email/password login for this almanac. Drik-style use is anonymous. Identity is the three cookies above. A later “save my birth on this device” should be another cookie (`ph_birth`), still not a password, and it should feed kundli, names, sade sati, and `ph_janma` from the Moon at that birth. Cross-device accounts are a separate product decision.

## 6. Every website page

Shared chrome is `web/templates/base.html`: sticky maroon header, live civil clock, language `<select>`, location bar, search, “Use my location”, sandal nav, left sidebar, cream page. Colours are CSS variables in `web/static/style.css` (`--kumkum`, `--haldi`, `--cream`). Keep them.

| Path | Template | Calls | What the page is |
|---|---|---|---|
| `/` | `home.html` | `RP.panchang`, `RP.choghadiya`, `RC.festivals` for this year | Today: sunrise strip, live Vedic clock (ghati/pala/vipala from sunrise to next sunrise), three feature cards, panchang glance, day choghadiya, upcoming festivals. Prev/next go to `/panchang`. |
| `/panchang` | `panchang.html` | `RP.panchang`, `RX.regional` | Full day. Five limbs with end times, both month systems, samvat, regional solar dates, ritu/ayana, Pravishte, ghati lengths, auspicious and inauspicious windows, Anandadi, Tamil yoga, Disha Shool plus the three open directions, Homahuti, Agnivasa, Chandra vasa, Shivavasa, Chandrabala/Tarabala lists, Pancha Pakshi table, 15+15 do-ghati muhurtas, Mantri Mandala. Janma selects write `ph_janma`. Live Vedic clock only when the date is today in that zone. |
| `/mine` | `mine.html` | `RP.panchang`, `RP.choghadiya`, `for_you()` | Personal day. Chandrabala and Tarabala for the current moon window. Next Amrit/Shubh/Labh outside Rahu (puja and new work). Next Char outside Rahu (travel). Next Labh outside Rahu (money). Abhijit and Rahu listed. Does not invent a score. |
| `/week` | `week.html` | same, seven days | One row per day: tithi, yes/no Chandrabala, yes/no Tarabala, next puja hour, Rahu start, Disha Shool. About 5 seconds. Do not call this on every home view. |
| `/compare` | `compare.html` | `RP.panchang` twice | Two places, one civil date. Shows when the sunrise tithi differs (a vrat can fall on another civil day). |
| `/names` | `names.html` | `moon_syllable()` / `syllable()` | Namakarana sound from the Moon’s nakshatra pada, or from a picked nakshatra+pada. Syllable table is `SYLLABLES` in `app/core/for_you.py` (Ashwini Chu…Revati Chi, with Devanagari). The family still chooses the name. Do not invent a baby-name database. |
| `/sade-sati` | `sade.html` | `kundli.sade_sati` | Saturn in 12th, 1st, 2nd from the natal Moon, plus 4th and 8th Panoti (Dhaiya). Input is a rashi **or** a birth (Moon sign computed). Scan starts 8 years before now so the current transit’s real start is included. |
| `/calendar` | `calendar.html` | `RC.month` | Month grid of tithi at sunrise. |
| `/choghadiya` | `choghadiya.html` | `RP.choghadiya` | Day and night, 8+8. Qualities: Amrit/Shubh Good, Labh Gain, Char Neutral, Udveg Bad, Kaal Loss, Rog Evil. |
| `/hora` | `hora.html` | `RP.hora` | 24 planetary hours, weekday lord first. |
| `/rahu-kaal` | `rahu.html` | `RP.rahu_kaal` over a span | Rahu table. Span cap is `SPAN_MAX_DAYS` (3660). |
| `/lagna-table` | `lagna.html` | `RP.lagna`, `RP.gowri` | Udaya lagna changes and Gowri nalla neram (`#gowri`). |
| `/festivals` | `festivals.html` | `RC.festivals` | Year list. Filters: festival, ekadashi, purnima, amavasya, sankranti, pradosh, sankashti, shivaratri, chaturthi, eclipse. “Add year to calendar” is `/festivals.ics` (VCALENDAR, all-day). |
| `/kundli` | `kundli.html` | `RV.kundli` | North/South/East SVG, D1–D60, Chandra chart, avakahada, doshas, yogas, Vimshottari. PDF via `POST /api/kundli/pdf` from the button, not from the HTML route. |
| `/matching` | `matching.html` | `RV.matching` | Ashtakoota 36 guna and 10 porutham. Query prefixes `b_` and `g_`. |
| `/muhurat` | `muhurat.html` | `RC.muhurat` | Types: marriage, griha_pravesh, vehicle, property, naming, mundan, annaprashan, business. Max window 3660 days. |
| `/transits` | `transits.html` | `RC.transits`, `RCore.planets`, `RX.moon_phases` | Sidereal ingresses and stations for a year, plus current planets. |
| `/western` | `western.html` | `RCore.chart`, `western_wheel` | Tropical chart. House system query `hs` (default placidus). |
| `/horoscope` | `horoscope.html` | `RX.horoscope` | Rashifal by period and sign. Template text, not a personal transit reading. |
| `/numerology` | `numerology.html` | `RX.numerology` | Name and date. |
| `/tarot` | `tarot.html` | `RX.tarot_daily` | Daily draw. |
| `/human-design` | `humandesign.html` | `HDM.chart` | Bodygraph from birth. Public mechanics only. |
| `/vastu` | `vastu.html` | `RM.vastu` | Direction guide and a layout score from posted rooms. |
| `/iching` | `iching.html` | `RM.iching_cast` | Three-coin cast. |
| `/palmistry` | `palmistry.html` | `RM.palmistry` | Reference plus a reading from described features. Not a photo reader. |
| `/tools` | `tools.html` | several `RM.*` | Mayan, Chinese forecast, Kabbalah, dreams, crystals. One page on purpose. |
| `/regional` | `regional.html` | regional + vakya + punya + dosha routers | Tamil/Malayalam/Bengali/Assamese/Odia solar dates, Gujarati/Marathi years, Vakya vs Drik, sankranti punya kaal, muhurta doshas, yoga catalog. |
| `/widget/panchang` | `widget.html` | `RP.panchang` | Embeddable fragment. `web/static/embed.js` is the snippet. |
| `/festivals.ics` | none | `RC.festivals` | `text/calendar` download. |
| `/robots.txt`, `/sitemap.xml` | none | `NAV` | Sitemap lists nav paths plus three festival years. |

`for_you()`, `syllable()`, and `moon_syllable()` live in `app/core/for_you.py`. They are not separate HTTP routes. The pages call them in-process. If you expose them, add a thin router that calls the same functions.

## 7. API surface (grouped)

All of these are under `/api` unless noted. Parameters and bodies are in Swagger; do not duplicate a second list that will drift. This is the map of which file owns the formula.

| Router file | Owns |
|---|---|
| `app/api/routers/core.py` | `/health`, `POST /chart`, `/planets`, `/zodiac/{sign}`, `/nakshatra`. Also at the site root. |
| `app/api/routers/panchang.py` | `/panchang`, `/muhurta/daily`, `/choghadiya`, `/hora`, `/gowri`, `/lagna-table`, `/rahu-kaal`. |
| `app/api/routers/calendar.py` | `/festivals`, `/calendar/month`, `/eclipses`, `/transits`, `/muhurat`. |
| `app/api/routers/geo.py` | `/cities`, `/cities/nearest`, `/cities/timezone`, `/cities/stats`. |
| `app/api/routers/vedic.py` | `POST /kundli`, `POST /matching`. |
| `app/api/routers/regional.py` | Regional v2, new-year festivals, festival rules, muhurta doshas, yoga catalog, Godhuli, Vakya panchang, Vakya sankranti, Chandravakyas, sankranti punya kaal. |
| `app/api/routers/extras.py` | KP, Jaimini, Lal Kitab, Varshaphal, kundli SVG/PDF/report, batch matching, nakshatra matching, regional v1, tithi/nakshatra/yoga search, moon phases, gochar, horoscope, numerology, biorhythm, angel numbers, tarot, Chinese, Western synastry/composite/Davison/progressions/returns/astrocartography. |
| `app/api/routers/more.py` | Shadbala, extra dashas, ghata chakra, written interpretation, remedies, Western transit interpretation, i18n glossary, manglik pair, matching PDF, varshaphal PDF, KP horary chart, transit search, Human Design, I Ching, Vastu, palmistry, Kabbalah, Mayan, dreams, crystals, Chinese forecast, `POST /ask` (rule keywords, **not** an LLM), `POST /mcp` (JSON-RPC tools). |

Location query on GET endpoints: `lat`, `lon`, and `tz` (IANA) or `utc_offset` (hours). Birth JSON: `date`, `time`, `latitude`, `longitude`, `timezone` or `utc_offset`, optional `name`. See `app/api/deps.py` and `app/models.py`.

`POST /api/ask` matches intents onto these endpoints. It must not invent an answer the engines did not compute.

## 8. Calculation modules (where to edit)

| File | Edit when you are changing |
|---|---|
| `app/core/ephem.py` | Swiss wrappers, ayanamsa, rise/set, Julian-day edges for year 1, `YEAR_MIN`, `YEAR_MAX`, `SPAN_MAX_DAYS`, Moshier fallback. `jd_from_utc` / `local_from_jd` must not build a `datetime` in year 0. |
| `app/core/panchang.py` | Daily limbs, choghadiya, hora, gowri, lagna, Rahu/Yamaganda/Gulika, personal Chandrabala/Tarabala. |
| `app/core/day_extras.py` | Drik day-page extras: gate, pakshi, mantri, agni, chandra vasa, shiva, tamil yoga, aadal, do-ghati. |
| `app/core/calendar.py` | Festivals, month grid, eclipses, transits, muhurat search. |
| `app/core/festival_rules.py` | Nirnayasindhu / Dharmasindhu festival tests, Smarta vs Vaishnava. |
| `app/core/regional_rules.py` | Solar-month rules (Tamil sunset, Malayalam 3/5, Bengali midnight, Odia civil). |
| `app/core/vakya.py` | Vararuci chandravakyas and Vakya sun. Side-by-side with Drik, not a replacement. |
| `app/core/punya_kaal.py` | Sankranti punya and maha punya. |
| `app/core/muhurta_doshas.py` | Panchaka, Bhadra vasa, dagdha tithi, tarabala detail. |
| `app/core/kundli.py` | Chart, vargas, dashas, doshas, yogas, `sade_sati`. |
| `app/core/advanced.py` | `current_vimshottari`, anandadi, special yogas. |
| `app/core/for_you.py` | Personal hour picker and naming syllables. |
| `app/core/shadbala.py` | Six-fold strength. |
| `app/core/yogas_classical.py`, `yogas_extra.py` | Yoga detectors. Cite the classical condition in the rule. Do not add a yoga you cannot state. |
| `app/core/matching.py`, `manglik_match.py` | Guna milan, porutham, manglik pair. |
| `app/core/charts_svg.py` | North, south, east, western wheel SVG. |
| `app/core/report_pdf.py` | Kundli PDF. |
| `app/core/i18n.py` | Glossary. Add the English string first, then each language. |
| `app/core/interpret.py` | Template sentences for planets, yogas, doshas. Not a substitute for the numbers. |
| `app/core/western.py`, `western_ext.py` | Tropical charts and the extra Western tools. |
| `app/core/horoscope.py`, `numerology.py`, `tarot.py`, `chinese.py`, `human_design.py`, `esoteric.py` | The non-panchang tools. |

`PANCHANGHUB_STRICT_DT=1` turns off the Drik-compatible ΔT double application (`DRIK_DT_SHIFT` in `ephem.py`). Leave it off unless you are comparing against a strict astronomical source. The published site matches Drik.

## 9. Design and front end

- Pages extend `base.html`. Snippets: `web/templates/_macros.html` (`elems`, `datebar`, `birthform`) and `_place.html` (one column of the compare page).
- `datebar` keeps city/lat/lon/tz across prev, next, and the date input. If a page has extra state (janma, second city), do not use the shared macro alone; put those fields in the form or in `locq`. `/mine`, `/week`, and `/compare` already do this.
- Birth place fields use `<input data-place="prefix">`. The script fills `prefixlat`, `prefixlon`, `prefixtz`. An empty prefix fills `lat`/`lon`/`tz`.
- Compare’s second city uses `data-compare`.
- Clock: `#liveClock`. If `data-pending="1"` it uses the browser timezone. Otherwise `data-tz` from the saved place.
- Vedic clock: `#vedicClock` with `data-sr` and `data-nsr` set to the sunrise ISO strings. 60 ghatis from sunrise to next sunrise. 1 ghati = 60 pala, 1 pala = 60 vipala.
- Do not add a new visual theme. Kumkum, haldi, and cream are the product.
- The top nav is `NAV[:13]` in `base.html`. If you insert an item at the front, something else falls out of the bar and must remain in the sidebar.

## 10. Data, range, and performance

- `data/places.sqlite`: table `places` plus FTS5 `places_fts`. Nearest-city uses a 0.25° cell column `cell`. Timezone lookup is `WHERE tz=? ORDER BY pop DESC LIMIT 1` and is a scan (about half a second). An index on `tz` would speed the GPS-denied fallback; build it with the file writable and expect a large rewrite.
- `data/build_places.py` rebuilds the sqlite from Global Gazetteer `allCountries.zip`. Only rerun if the place set is wrong.
- Festival and muhurat searches walk days. One muhurat request may cover at most 3660 days (`SPAN_MAX_DAYS`). Say “10 years” in errors, not “0..400”.
- `/week` is seven full panchangs. Acceptable for that page. Do not put it on `/`.
- Mantri Mandala finds the year’s Chaitra Shukla Pratipada by walking new moons. It is cached per place. Do not replace it with a 400-day scan.

## 11. Accuracy rules for anyone upgrading

Match Drik on astronomy. Do not “improve” sunrise by switching to disc centre. Do not change Lahiri unless a measured Drik diff says so (`accuracy/` has comparison scripts and cached Drik rows).

Published rules already implemented, with the source named in code or in `research/sources.md`:

- Muhurta Chintamani for Godhuli (seasonal), Panchaka, Bhadra residence, dagdha tithi.
- Nirnayasindhu / Dharmasindhu for festivals and sankranti punya kaal.
- Vararuci chandravakyas for the Vakya column (reconstructed; daily Vakya end times were not validated against a printed vakya almanac).
- Naming syllables: the 27×4 pada table in `for_you.py`.
- Sade Sati: Saturn transiting 12, 1, 2 from the natal Moon sign. Panoti: 4 and 8.

**Do not invent these.** They were looked up and no formula checked out against Drik, so they are absent on purpose:

- Baana
- Kumbha chakra
- Lumbaka and Netrama
- A Rahu “direction of the prahar” clock

If you add one, cite the page or verse and a Drik date where your output matches theirs. A guessed table is worse than a missing row.

Also do not:

- Invent baby names, lucky scores, or an “87% auspicious” meter.
- Present `/api/ask` as a model. It is keyword routing.
- Translate proper astronomy by editing numbers inside i18n. Translate labels only.
- Widen festival rules without a citation in `festival_rules.py`.

## 12. Tests and docs that already exist

- `pytest -q` from this folder. `tests/test_panchang_drik.py` is the Drik timing guard. `tests/test_day_extras.py` covers the extra day fields. Do not weaken these to make a change pass.
- `research/feature-matrix.md` — what commercial APIs sell. Status in `research/feature-checklist.csv` is “done” for that checklist; it is not a promise that every Drik ornament exists.
- `research/sources.md` — which public-domain texts were used, and which scans were deleted for copyright.
- `accuracy/` — how timings were compared. Read it before changing `ephem.py`.
- `README.md` — endpoint examples. Its sample port is 8000; the sandbox uses 8080. Behaviour is the same.
- `sdk/python` and `sdk/js` — thin clients. Update them if you change a public path.

## 13. Safe upgrade list (highest value first)

These are real gaps. They are not permission to invent yogas.

1. **One saved birth on this device.** Cookie `ph_birth` with name, date, time, lat, lon, tz, city. Derive Moon rashi and nakshatra once and write `ph_janma`. Prefill kundli, matching side A, names, and sade sati. Show current Vimshottari (`advanced.current_vimshottari`) on the home “For your birth star” card. Still no password.
2. **Print stylesheet** for `/panchang` so a priest can print one day. The data is already on the page.
3. **Index `places.tz`** so the timezone fallback is instant.
4. **Eclipse local circumstances** on `/festivals?type=eclipse`: the engine lists eclipses; visibility at the saved coordinates is the missing piece. Use Swiss local circumstances, do not guess magnitude.
5. **Gochar on the home card** when `ph_janma` is set, via the existing `/api/gochar` rules, not a new prediction voice.
6. **Keep Swagger and the website on one function.** Any new page that computes a number in JavaScript is a bug.

When you finish a change: run the relevant pytest, open the HTML route with a fixed `lat`, `lon`, and `tz` (do not trust the default city), and bump the static `?v=` if JavaScript or CSS changed.

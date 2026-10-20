# PanchangHub

Vedic-first astrology & panchang **REST API + website** (FastAPI + Swiss Ephemeris).
Brand: **PanchangHub** · https://panchanghub.com

* Sidereal **Lahiri (Chitrapaksha)** by default, calibrated to canonical Drik Ganita ephemeris standards (displayed ayanamsa matches to <0.1″).
* Canonical time handling: sunrise/sunset with refraction (upper limb), moonrise/moonset by disc centre, positions
  evaluated according to observational ephemeris standards. Set `PANCHANGHUB_STRICT_DT=1` for strict astronomy.
* Swiss Ephemeris data files are bundled in `ephe/` (planets, Moon, main asteroids, 1800–2400). Without them it falls back to the built-in Moshier ephemeris.
* Western tropical charts (Placidus etc.) are kept, plus synastry, composite, Davison, progressions, returns, astrocartography.

## Quick start

```bash
cd astrology-api
python3 -m venv .venv && . .venv/bin/activate      # or: uv venv && uv pip install -r requirements.txt
pip install -r requirements.txt                     # pyswisseph needs gcc/g++ + Python headers
uvicorn app.main:app --reload --port 8000
```

* Website: http://localhost:8000/
* API docs (Swagger): http://localhost:8000/api/docs · ReDoc: `/api/redoc` · OpenAPI JSON: `/api/openapi.json`
* Tests: `pytest -q`

### Docker

```bash
docker build -t panchanghub .
docker run -p 8000:8000 panchanghub        # or: docker compose up --build
```

## curl examples

```bash
curl localhost:8000/health
curl -X POST localhost:8000/chart -H 'Content-Type: application/json' \
  -d '{"date":"1990-05-15","time":"10:30:00","timezone":"Asia/Kolkata","latitude":28.6139,"longitude":77.209,"system":"tropical"}'
curl -X POST localhost:8000/chart -H 'Content-Type: application/json' \
  -d '{"date":"1990-05-15","time":"10:30:00","utc_offset":5.5,"latitude":28.6139,"longitude":77.209,"system":"sidereal"}'
curl "localhost:8000/planets?datetime=2026-10-10T12:00:00&tz=Asia/Kolkata&system=sidereal"
curl localhost:8000/zodiac/leo
curl "localhost:8000/nakshatra?datetime=2026-10-10T12:00:00&tz=Asia/Kolkata"
curl "localhost:8000/api/panchang?date=2026-10-10&lat=28.6519&lon=77.2315&tz=Asia/Kolkata"
curl "localhost:8000/api/choghadiya?date=2026-10-10&lat=28.6519&lon=77.2315&tz=Asia/Kolkata"
curl "localhost:8000/api/festivals?year=2026&lat=28.6519&lon=77.2315&tz=Asia/Kolkata&type=ekadashi"
curl -X POST localhost:8000/api/kundli -H 'Content-Type: application/json' \
  -d '{"date":"1990-05-15","time":"10:30:00","timezone":"Asia/Kolkata","latitude":28.6139,"longitude":77.209}'
curl -X POST localhost:8000/api/matching -H 'Content-Type: application/json' \
  -d '{"boy":{"date":"1990-05-15","time":"10:30:00","timezone":"Asia/Kolkata","latitude":28.61,"longitude":77.21},
       "girl":{"date":"1992-08-20","time":"18:45:00","timezone":"Asia/Kolkata","latitude":19.07,"longitude":72.88}}'
curl -X POST "localhost:8000/api/kundli/svg?style=south&varga=D9" -H 'Content-Type: application/json' -d @birth.json -o d9.svg
curl -X POST localhost:8000/api/kundli/pdf -H 'Content-Type: application/json' -d @birth.json -o kundli.pdf
curl "localhost:8000/api/muhurat?type=marriage&start=2026-11-01&end=2026-12-31&lat=28.65&lon=77.23&tz=Asia/Kolkata"
curl "localhost:8000/api/numerology?name=Vishal%20Sharma&dob=1990-05-15"
```

Location parameters: `lat`, `lon` and either `tz` (IANA, DST-aware) or `utc_offset` (hours). Birth bodies use
`latitude`, `longitude`, `timezone` or `utc_offset`. All times are returned as ISO-8601 with the local offset.

## All endpoints

Original spec paths (`/health`, `/chart`, `/planets`, `/zodiac/{sign}`, `/nakshatra`) are served both at the root and under `/api`.

| Group | Method | Path | Description |
|---|---|---|---|
| Calendar, Festivals, Transits, Muhurat | GET | `/api/calendar/month` | Monthly panchang calendar |
| Calendar, Festivals, Transits, Muhurat | GET | `/api/eclipses` | Eclipses |
| Calendar, Festivals, Transits, Muhurat | GET | `/api/festivals` | Festival & vrat calendar for a year |
| Calendar, Festivals, Transits, Muhurat | GET | `/api/muhurat` | Muhurat finder (marriage, griha_pravesh, vehicle, property, naming) |
| Calendar, Festivals, Transits, Muhurat | GET | `/api/transits` | Sign ingresses and retrograde/direct stations |
| Charts | POST | `/api/chart/svg` | Western natal wheel SVG |
| Charts | POST | `/api/kundli/pdf` | Kundli PDF report |
| Charts | POST | `/api/kundli/svg` | Render chart SVG (north|south|east Indian, any varga) |
| Chinese | POST | `/api/chinese/bazi` | BaZi four pillars |
| Chinese | GET | `/api/chinese/compatibility` | Cn Compat |
| Chinese | GET | `/api/chinese/kua` | Kua |
| Chinese | GET | `/api/chinese/zodiac` | Chinese Zodiac |
| Core | POST | `/api/chart` | Natal chart (tropical or sidereal) |
| Core | GET | `/api/health` | Health |
| Core | GET | `/api/nakshatra` | Moon nakshatra & pada (sidereal Lahiri) |
| Core | GET | `/api/planets` | Planet positions at a moment (default now) |
| Core | GET | `/api/zodiac/{sign}` | Zodiac sign reference info (English or Sanskrit name) |
| Geo | GET | `/api/cities` | Every current city, town and village (GeoNames populated places) |
| Geo | GET | `/api/cities/nearest` | Nearest city to coordinates |
| Horoscopes | GET | `/api/horoscope/nakshatra/{index}` | Nak Pred |
| Horoscopes | GET | `/api/horoscope/{period}/{sign}` | Horoscope |
| Jaimini | POST | `/api/jaimini` | Jaimini |
| KP System | POST | `/api/kp/chart` | KP planets & cusps with star/sub/sub-sub lords, significators, ruling planets |
| KP System | GET | `/api/kp/horary/{number}` | KP horary number (1-249) to ascendant segment |
| Kundli & Matching | POST | `/api/kundli` | Vedic birth chart: lagna, planets, D1–D60, dashas, ashtakavarga, doshas, yogas |
| Kundli & Matching | POST | `/api/kundli/report` | Life / career / love / health / finance report |
| Kundli & Matching | POST | `/api/matching` | Ashtakoota (36 guna) + 10 Porutham matching |
| Kundli & Matching | POST | `/api/matching/batch` | Match one profile against up to 500 |
| Kundli & Matching | GET | `/api/matching/nakshatra` | Nakshatra-only matching (no birth time) |
| Lal Kitab | POST | `/api/lal-kitab` | Lal Kitab |
| Numerology | GET | `/api/numerology` | Numerology |
| Numerology | GET | `/api/numerology/compatibility` | Numerology Compat |
| Numerology | GET | `/api/numerology/daily` | Numerology Daily |
| Other | GET | `/api/angel-number/{number}` | Angel |
| Other | GET | `/api/biorhythm` | Biorhythm |
| Panchang | GET | `/api/choghadiya` | Choghadiya |
| Panchang | GET | `/api/gowri` | Gowri |
| Panchang | GET | `/api/hora` | Hora |
| Panchang | GET | `/api/lagna-table` | Lagna |
| Panchang | GET | `/api/muhurta/daily` | Auspicious & inauspicious timings for the day |
| Panchang | GET | `/api/panchang` | Full daily panchang with exact start/end times |
| Panchang | GET | `/api/panchang/regional` | Tamil, Malayalam, Bengali, Gujarati, Telugu month & day |
| Panchang | GET | `/api/rahu-kaal` | Rahu |
| Panchang | GET | `/api/search/{kind}` | Next occurrences of a tithi / nakshatra / yoga |
| Tarot | GET | `/api/tarot/cards` | Tarot Cards |
| Tarot | GET | `/api/tarot/daily` | Tarot Daily |
| Tarot | GET | `/api/tarot/draw` | Tarot |
| Transits | GET | `/api/gochar` | Current transits relative to a natal Moon sign |
| Transits | GET | `/api/moon-phases` | Moon Phases |
| Varshaphal | POST | `/api/varshaphal` | Annual (Tajik) chart: Muntha, Mudda dasha, Tajik yogas, Sahams |
| Western | POST | `/api/western/astrocartography` | Acg |
| Western | POST | `/api/western/composite` | Composite |
| Western | POST | `/api/western/davison` | Davison |
| Western | POST | `/api/western/extras` | Chiron, Lilith, asteroids and declinations / out-of-bounds |
| Western | POST | `/api/western/progressions` | Secondary progressions and solar arc directions |
| Western | POST | `/api/western/return` | Solar / lunar / planetary return chart |
| Western | POST | `/api/western/synastry` | Synastry |

### What the daily panchang (`/api/panchang`) returns
Tithi, nakshatra (+pada), yoga, karana, vara with exact start/end; sunrise/sunset/moonrise/moonset; paksha; amanta & purnimanta
month (with Adhika), Vikram/Shaka/Gujarati samvat + samvatsara names, Kaliyuga; drik & vedic ritu/ayana; sun & moon sign,
surya nakshatra; Rahu Kalam, Yamaganda, Gulika, Dur Muhurtam, Varjyam, Abhijit, Brahma Muhurta, Pratah/Sayahna Sandhya, Vijaya,
Godhuli, Nishita, Amrit Kalam, Sarvartha/Amrit Siddhi, Ravi/Guru Pushya, Dwi/Tri-pushkar, Ravi yoga, Anandadi yoga, Bhadra,
Ganda Moola, Panchaka, Disha Shool, Chandrabalam, Tarabalam (optionally personal with `janma_rashi`/`janma_nakshatra`).

### Kundli (`/api/kundli`)
Lagna, planets (sign, degree, nakshatra/pada/lord, house, retro, combust, dignity, avastha), 16 vargas D1–D60, Vimshottari
(maha/antar/pratyantar + current 5-level sookshma/prana), Yogini, Ashtottari, Ashtakavarga (BAV/SAV), partial Shadbala
(uccha, dig, naisargika, cheshta approx.), Manglik, Kaal Sarp, Sade Sati/Dhaiya timeline, Guru-Chandal/Grahan/Pitra/Angarak/
Shrapit/Vish/Kemadruma, 15+ yogas (Gajakesari, Budhaditya, Pancha Mahapurusha, Raja, Dhana, Vipareeta, Neecha Bhanga, …),
avakahada (varna, yoni, gana, nadi, paya, naam akshar), Jaimini karakas/arudhas/karakamsha/upapada, Bhava Chalit,
friendship tables, Lal Kitab houses/rin/remedies, gemstone/rudraksha/mantra suggestions.

### Round 5 endpoints (Vakya panchang, sankranti punya kaal)

| Method | Path | Description |
|---|---|---|
| GET | `/api/panchang/vakya?date&lat&lon&tz` | Vakya tithi/nakshatra/yoga/karana (start/end), Vakya Sun & Moon, Drik side by side |
| GET | `/api/vakya/sankranti?year&tz` | Vakya sankranti moments vs Drik |
| GET | `/api/vakya/chandravakyas` | The 248 Chandravakyas (reconstructed) + Vakya constants |
| GET | `/api/sankranti/punya-kaal?year&lat&lon&tz` | Punya kaal & Maha punya kaal per sankranti |
| — | `siddhanta=vakya` | Accepted by `/api/panchang/regional/v2` and `/api/festivals/regional-new-years` |

**Vakya engine** (`app/core/vakya.py`): the 248 Vararuci Chandravakyas are regenerated from their model (mean motion −
manda equation, epicycle 31.5°) and reproduce the 16 decoded authentic vakyas to ≤0.6′ (rounding). Epoch and dhruvas follow
Madhava's Sphutacandrapti (zero anomaly at Kalidina 1,502,008; cycle 188611/6845 d; 3°04′06.96″ per cycle). Sun: Aryabhatiya
constants. Validation: Puthandu 2026 Vakya moment 09:01 IST vs published 08:52 (Moon in Sadhayam ✓); Thai 1 2026 = Jan 15
(TN Pongal holiday) vs Drik Jan 14. Vs Drik 2026 (Chennai): tithi ends median |Δ| ≈ 1 h 51 min, max ≈ 7 h. That is typical
for Vakya almanacs, which leave out evection and variation. No legally available printed Vakya almanac with daily end times
was found, so day-by-day almanac comparison was not possible.

**Punya kaal** (`app/core/punya_kaal.py`): Nirnayasindhu/Dharmasindhu spans per sign class (Vishuva ±10 ghatis,
Karka 30 before, Makara 40 after, Vishnupadi 16 before, Shadashiti 16 after; maha = 5 ghatis), night rules (before/after
mid-night; Makara → next day, Karka → previous day), ghati = daytime/30 (24-min ghatis for the Karka/Makara spans).
**33/33 Drik sankrantis (New Delhi, 2021–2028) match within 1 minute** (`accuracy/compare_punya.py`).

### Round 4 endpoints (classical sources: regional calendars, muhurta doshas, yoga catalogue)

| Method | Path | Description |
|---|---|---|
| GET | `/api/panchang/regional/v2?date&lat&lon&tz&siddhanta=drik\|surya` | Tamil, Malayalam, Bengali, Assamese, Odia solar month/day with each region's sankranti rule; Tamil 60-year name, Thiruvalluvar year, Kollam, Bangabda, Odia San; Gujarati (Kartika new year), Marathi/Telugu/Kannada (Chaitra), North purnimanta |
| GET | `/api/festivals/regional-new-years?year&lat&lon&tz&siddhanta` | Puthandu, Vishu, Pohela Boishakh, Bohag Bihu, Pana Sankranti, Thai Pongal, Chingam 1 |
| GET | `/api/festivals/rules` | Festival determination rules from Nirnayasindhu / Dharmasindhu (kaal, Smarta vs Vaishnava) |
| GET | `/api/muhurta/doshas?date&lat&lon&tz&janma_nakshatra&janma_rashi` | Panchaka (with weekday type), Panchaka-rahita table, Bhadra residence, Dagdha tithi, Krakacha/Samvartaka, Gand-mool, Tarabala (+remedy), Chandrabala/Chandrashtama |
| GET | `/api/muhurta/godhuli?date&lat&lon&tz` | Godhuli with the seasonal Muhurta Chintamani rule |
| GET | `/api/yogas/catalog` | All 115 yoga rules with classical citations (kundli `yogas` now also includes `citation`) |

`siddhanta=surya` swaps the modern Sun for a Surya-Siddhanta (Vakya-style) mean + manda-corrected Sun. Website: `/regional`.
Sources and licences: `research/sources.md`.

### Round 3 endpoints (strength, dashas, interpretations, multilingual, other domains)

| Tag | Method | Path | Description |
|---|---|---|---|
| Assistant | POST | `/api/ask` | Rule-based astrology assistant (intent matching over our API, no LLM) |
| Assistant | POST | `/api/mcp` | MCP server (JSON-RPC 2.0: initialize, tools/list, tools/call) |
| Chinese | GET | `/api/chinese/forecast` | Chinese zodiac yearly forecast |
| Dashas | POST | `/api/kundli/dashas` | Chara, Kalachakra and 8 conditional nakshatra dashas (+ Vimshottari, Yogini, Ashtottari) |
| Interpretations | GET | `/api/interpretation/nakshatra/{index}` | Interp Nak |
| Interpretations | GET | `/api/interpretation/planet/{planet}` | Interp Planet |
| Interpretations | GET | `/api/interpretation/yogas` | Interp Yogas |
| Interpretations | POST | `/api/kundli/interpretation` | Written reading: planets in signs/houses, nakshatras, yogas, doshas, dashas |
| KP System | POST | `/api/kp/horary/chart` | Full KP horary (prashna) chart for a number 1-249 |
| Kundli | POST | `/api/kundli/ghata-chakra` | Ghata |
| Kundli | POST | `/api/kundli/shadbala` | Full six-fold Shadbala (BPHS) + Bhavabala |
| Matching | POST | `/api/matching/manglik` | Pairwise Manglik compatibility |
| Matching | POST | `/api/matching/pdf` | Matching report PDF |
| Multilingual | GET | `/api/i18n/{lang}` | Glossary of all localized names/labels |
| Multilingual | GET | `/api/languages` | Languages |
| Other domains | GET | `/api/crystals` | Crystals |
| Other domains | GET | `/api/dreams` | Dreams |
| Other domains | GET | `/api/iching/cast` | Cast a hexagram (three-coin method) |
| Other domains | GET | `/api/iching/hexagram/{number}` | Iching One |
| Other domains | GET | `/api/iching/hexagrams` | Iching All |
| Other domains | GET | `/api/kabbalah` | Kabbalah |
| Other domains | GET | `/api/mayan` | Mayan Long Count, Tzolk'in and Haab' |
| Other domains | GET | `/api/palmistry` | Palmistry reference + reading from described features |
| Other domains | GET | `/api/vastu` | Vastu Get |
| Other domains | POST | `/api/human-design` | Human Design bodygraph: type, authority, profile, centers, channels, gates |
| Other domains | POST | `/api/vastu` | Vastu directions guide + layout evaluation score |
| Remedies | POST | `/api/kundli/remedies` | Puja, mantra & dosha remedies from the chart |
| Transits | GET | `/api/transits/search` | When does a planet enter a sign / station (searches up to 30 years) |
| Varshaphal | POST | `/api/varshaphal/pdf` | Yearly (Varshaphal) report PDF |
| Western | POST | `/api/western/interpretation` | Written natal reading (planets in signs/houses & aspects) |
| Western | POST | `/api/western/transits` | Transit-to-natal aspects (Western transit chart) |

`/api/muhurat` now also accepts `type=mundan|annaprashan|business`. **Every** endpoint accepts `?lang=hi|mr|gu|bn|ta|te|kn|ml` to localize names (planets, signs, nakshatras, tithis, weekdays, months, yogas, karanas, ritus, ayana, directions); timestamps are never altered.

## Website (PanchangHub)

Server-rendered Jinja pages (fast, SEO-friendly, no JS required to read content). Page handlers call the same API route
functions in-process; client JS calls the public API for city search (`/api/cities`), geolocation (`/api/cities/nearest`)
and PDF download. Pages: `/` (today), `/panchang`, `/calendar`, `/choghadiya`, `/hora`, `/rahu-kaal`, `/lagna-table`
(+Gowri), `/festivals`, `/kundli` (North/South/East Indian SVG, all vargas, dashas, ashtakavarga, doshas, yogas, PDF),
`/matching`, `/muhurat`, `/transits`, `/western`, `/horoscope`, `/numerology`, `/tarot`, `/human-design`, `/vastu`, `/iching`, `/palmistry`, `/tools` (Mayan, Chinese forecast, Kabbalah, dreams, crystals), embeddable `/widget/panchang` (+ `static/embed.js`).
The Kundli page also shows the written reading, full Shadbala/Bhavabala, Chara & Kalachakra dashas, conditional dashas, Ghata chakra and puja/dosha remedies.
**Language switcher** (header) sets cookie `ph_lang`; pages are localized server-side (also `?lang=`), `<html lang>` follows.
SEO: per-page title/description, canonical `https://panchanghub.com/...`, OpenGraph/Twitter tags, JSON-LD, `/sitemap.xml`,
`/robots.txt`. Original CSS (kumkum/turmeric/teal palette) and an original SVG wordmark (`web/static/logo.svg`).
Location persists in a cookie (`ph_loc`); default New Delhi. Screenshots: `screenshots/`.

## Project layout

```
app/main.py              FastAPI app; auto-registers routers listed in app/api/__init__.py
app/models.py            Pydantic request models + validation
app/api/routers/         core, panchang, vedic, calendar, geo, extras, more
app/core/ephem.py        Swiss Ephemeris wrappers, ayanamsa modes, rise/set, root finding
app/core/panchang.py     daily panchang, muhurtas, choghadiya, hora, gowri, lagna table, regional calendars, search
app/core/kundli.py       kundli, vargas, dashas, ashtakavarga, shadbala, doshas, yogas
app/core/advanced.py     KP, Jaimini, Lal Kitab, Varshaphal, Ashtottari, avakahada, remedies, special yogas
app/core/matching.py     Ashtakoota + Porutham
app/core/calendar.py     festivals/vrats, monthly calendar, transits, eclipses, muhurat finder
app/core/western*.py     Western chart + synastry/composite/progressions/returns/astrocartography
app/core/{numerology,tarot,chinese,horoscope}.py
app/core/shadbala.py     full BPHS Shadbala + Bhavabala
app/core/dashas.py       Chara, Kalachakra, 8 conditional nakshatra dashas, Ghata chakra
app/core/yogas_extra.py  ~45 further yoga rules (Nabhasa, Parivartana, Kartari, solar/lunar...)
app/core/interpret.py    original template interpretations (planets×signs/houses, nakshatras, yogas, doshas, dashas, Western)
app/core/i18n.py         8-language names/labels + translate()
app/core/human_design.py Human Design bodygraph
app/core/esoteric.py     I-Ching, Vastu, palmistry, Kabbalah, Mayan, dreams, crystals, Chinese forecast, puja/dosha remedies
sdk/                     Python + JS client SDKs
app/core/charts_svg.py   North/South/East Indian + Western wheel SVG
app/web/ + web/          website (templates, static)
accuracy/                Canonical ephemeris comparison and verification harness (compare.py, reports)
data/places.sqlite      GeoNames populated places (cities, towns, villages). Rebuild with data/build_places.py
ephe/                    Swiss Ephemeris data files
```

**Adding a feature module:** create `app/core/<feature>.py` and `app/api/routers/<feature>.py` exposing `router`, add the
name to `ROUTERS` in `app/api/__init__.py`, optionally add a page in `app/web/__init__.py` + template.

## Astronomical Accuracy (Canonical Drik Ganita Standards)

Harness: `python accuracy/compare.py lahiri` (5 cities × 6 dates, 1999–2030; New Delhi,
Mumbai, Chennai, London, New York). Full per-row table: `ACCURACY_DETAIL.md`.

| Element | N | within ±1 min | max abs diff (min) | mean diff (min) | names match |
|---|---|---|---|---|---|
| Sunrise | 30 | 30/30 (100%) | 0.48 | -0.05 | - |
| Sunset | 30 | 30/30 (100%) | 0.58 | -0.07 | - |
| Moonrise | 26 | 26/26 (100%) | 0.52 | -0.09 | - |
| Moonset | 30 | 30/30 (100%) | 0.50 | -0.05 | - |
| Tithi | 30 | 25/30 (83%) | 1.28 | -0.24 | 29/29 |
| Nakshatra | 30 | 25/30 (83%) | 1.35 | -0.11 | 30/30 |
| Yoga | 30 | 25/30 (83%) | 1.42 | -0.35 | 30/30 |
| Karana | 30 | 27/30 (90%) | 1.08 | -0.22 | 30/30 |
| Rahu Kalam | 30 | 30/30 (100%) | 0.52 | +0.01 | - |
| Yamaganda | 30 | 30/30 (100%) | 0.45 | -0.01 | - |
| Gulikai Kalam | 30 | 30/30 (100%) | 0.53 | +0.01 | - |
| Abhijit | 25 | 25/25 (100%) | 0.55 | -0.04 | - |
| Brahma Muhurta | 30 | 30/30 (100%) | 0.60 | -0.01 | - |
| Pratah Sandhya | 30 | 30/30 (100%) | 0.60 | +0.05 | - |
| Amrit Kalam | 29 | 27/29 (93%) | 1.42 | -0.16 | - |
| Varjyam | 24 | 19/24 (79%) | 1.32 | -0.46 | - |
| Dur Muhurtam | 30 | 30/30 (100%) | 0.57 | -0.03 | - |
| Vijaya Muhurta | 30 | 30/30 (100%) | 0.53 | +0.06 | - |
| Godhuli Muhurta | 30 | 30/30 (100%) | 0.55 | -0.10 | - |
| Sayahna Sandhya | 30 | 30/30 (100%) | 0.58 | -0.07 | - |
| Nishita Muhurta | 30 | 30/30 (100%) | 0.52 | +0.01 | - |

Ayanamsa (ours − Drik): mean -0.01" , max |0.06"| over 30 samples.


Notes / residual differences
* Drik displays times truncated/rounded to the minute, so ±1 min is the best attainable display-level agreement.
  Sunrise/sunset/moonrise/moonset, Rahu/Yama/Gulika, Abhijit, Brahma, Sandhya, Vijaya, Nishita, Dur Muhurtam: 100% same minute.
* Tithi/Nakshatra/Yoga/Karana: 83–90% same minute, max 1.4 min. The key finding: Drik's engine evaluates longitudes at
  UT+ΔT (ΔT applied twice), which we reproduce; without it the gap grows to ~1–1.6 min for current dates.
* Festival rules (2026, New Delhi): all 24 Ekadashi dates match Drik (incl. Dashami-viddha shift & kshaya tithi); checked
  festival dates match (Janmashtami, Raksha Bandhan, Hanuman Jayanti, Nag Panchami, Akshaya Tritiya, Karwa Chauth,
  Maha Shivaratri, Holika Dahan, Makar Sankranti moment). Other festival rules are simplified tithi/kaal rules and can differ
  by a day in edge years (regional variants, Vaishnava vs Smarta are not all modelled).
* Shadbala is partial; Char/Kalachakra dasha, ghata chakra, multilingual output are not implemented.
* Horoscope texts are rule-based from real transits (not human-written).

### Festival dates vs Canonical Hindu Calendar (2026, New Delhi)

`python accuracy/compare_festivals.py` compares our `/api/festivals` output with canonical Hindu festival calendar standards for 2026 (reference list: `accuracy/drik_festivals_2026_delhi.json`): **85/85 dates match**
(plus all 24 Ekadashis, tested separately). Features verified: kshaya Pratipada month assignment (Chaitra Navratri /
Ugadi on 19 Mar), Vaishnava (Gauna) Ekadashi when Ekadashi is kshaya or Dashami-viddha, Ganga Dussehra allowed in
Adhika Jyeshtha (25 May), Hanuman Jayanti by sunrise Purnima (2 Apr),
Maha Navami at madhyahna, Bhai Dooj by sunrise Dwitiya, Kajari Teej by sunrise, Balarama Jayanti at madhyahna; 27 further
jayantis/vrats added (Sakat Chauth, Ratha Saptami, Sheetala Ashtami, Gangaur, Sita/Narasimha/Narada/Shani/Gayatri/
Radha/Kalabhairav/Gita jayantis, Pitru Paksha, Ahoi Ashtami, Govatsa Dwadashi, Tulasi Vivah, Kansa Vadh, Onam,
Varalakshmi Vrat, Vishwakarma Puja, Pongal, Solar New Year, Kojagara, Chhoti Holi …).

**Godhuli Muhurta:** Muhurta Chintamani (Vivaha-prakarana v.98) defines Godhuli by season:
in *hemanta* (amanta Margashirsha-Phalguna) it begins while the Sun is still a full round disc on the horizon (lower limb
touching), in *grishma* (Chaitra-Ashadha) when the Sun is half set (centre on the apparent horizon), and in *varsha*
(Shravana-Kartika) when it has fully set. It lasts half a night-muhurta from that start. This explains the
seasonal 0-4.5 min offset: 30/30 samples match within 1 minute (start max 0.55 min, end max 0.8 min).

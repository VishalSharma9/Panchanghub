# PanchangHub & Classical Vedic Astrology Suite: Complete Architecture, API & Engineering Master Guide

> **Document Version**: 2.0.0 (Production Release Candidate)  
> **Target Audience**: Development Team, System Architects, and Autonomous Agents (Grok, Claude, Codex)  
> **Source Base**: `D:\astrology` and `D:\panchanghub-FULL`  
> **Canonical Classical Treatises**: *Brihat Parashara Hora Shastra (BPHS)*, *Jaimini Upadesha Sutras*, *Prashna Tantra*, *Daivajna Vallabha*, *Tajika Neelakanthi*, *Phaladeepika*, *Saravali*, *Surya Siddhanta*.

---

## 1. Executive Summary & Platform Overview

**PanchangHub** is a high-precision, enterprise-grade, clean-room Vedic Astrological and Astronomical engine built in Python 3.11+ and FastAPI, backed by the **Swiss Ephemeris (`pyswisseph`)** and calibrated to sidereal Lahiri (Chitra Paksha) ayanamsha standards matching canonical Drik Ganita astronomical ephemeris standards.

The platform features:
1. **High-Precision Ephemeris Engine**: Accurate astronomical positions for any timestamp from 1 CE through 3000 CE, including planetary coordinates, retrogradation, combustion, true node vs. mean node, sunrise/sunset, moonrise/moonset, and udaya lagnas.
2. **Complete Classical Panchangam**: Tithi, Nakshatra, Yoga, Karana, Paksha, Vaara, Ritus, Ayana, Choghadiya, Hora, Rahu Kaal, Gulika, Yamaganda, and Gowri Nalla Neram.
3. **Comprehensive Kundli & Shodashavarga Suite**: All 31 divisional charts (16 Parashara Shodashavargas, 5 Tajika/Nadi vargas, and 10 Seshadhri Iyer harmonic vargas) rendered dynamically as SVG in North Indian diamond, South Indian square, East Indian, and Western wheel formats.
4. **Special Lagnas & Arudhas**: Bhava Lagna, Hora Lagna, Ghatika Lagna, Pranapada, Vighati, Sree, Indu, Kunda, Varnada Lagna, and 12 Arudha Padas (A1–A12, Arudha Lagna, Upapada Lagna) with canonical Parashari exception handling.
5. **Full Ashtakavarga Suite**: 8 Bhinnashtakavarga grids, Sarvashtakavarga (SAV), Trikona Shodhana, Ekadhipatya Shodhana, and Shodhya Pindas (Rashi Pinda, Graha Pinda, Yoga Pinda).
6. **Classical Yogas Scanner**: Automated detection of 60+ authentic yogas (Pancha Mahapurusha, Raja Yogas, Dhana Yogas, Viparita Raja, Saraswati, Gaja-Keshari, Budhaditya, etc.).
7. **Holistic Life Reading & 144 House Lords Analysis**: Authentic Sanskrit verses (*BPHS* Ch. 26) with English translations for every house lord placement, plus 12-house Shad Phala.
8. **Tajika Varshaphala (Solar Return)**: Exact solar return epoch, Muntha, Varshesha Year Lord (Pancha-Adhikari calculation), Mudda Dasha, and 24 Tajika Sahams.
9. **Krishnamurti Paddhati (KP System)**: Placidus cusps, 4-fold significators, Ruling Planets, Sign/Star/Sub/Sub-Sub lords, and 1-249 Horary table.
10. **Prashna Kundali (Classical Horary Divination)**: Moment-of-query chart with definitive yes/no verdict, confidence score, estimated timeline of fulfillment, and Tajika yogas (Ithasala, Ishrafa, Nakta, Yamaya, Kamboola) within canonical Deeptamsha orbs.
11. **Soul Guidance & Jaimini Karakamsha**: Atmakaraka (AK) soul karmic lessons, Karakamsha (KL in D9), Ishta Devata (12th from KL per *Jaimini Sutras* 1.2.69-72) with invocation mantras, Dharma Devata (9th from KL), Palana Devata (6th from AmK), and 4 Purushartha (Dharma, Artha, Kama, Moksha) alignment matrix.
12. **Authentic Classical Japa Mantras**: Beej mantras, Puranic slokas, Gayatri mantras, prescribed counts, Kali Yuga 4x counts, malas, muhurtas, dana, and vrata for all 9 Grahas.
13. **Global Atlas & City Search**: SQLite database with 150,000+ GeoNames cities, substring and prefix search with population weighting, and IANA timezone resolution.
14. **Anti-Spam Email Authentication**: Advanced member access gating; instant auto-verification for `@gmail.com` accounts, 6-digit OTP verification for other domains, and HMAC session tokens.
15. **Multilingual Localization**: Native script translation across 9 languages (English, Hindi, Gujarati, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam) covering over 196 astrological terms and UI elements.

---

## 2. Directory Structure of the Unified `astrology` Codebase

```
D:\astrology\
├── api/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entrypoint, CORS, GZip, i18n middleware
│   │   ├── models.py                # Pydantic v2 data models for all requests and responses
│   │   ├── api/
│   │   │   ├── __init__.py          # Router registry (core, panchang, vedic, calendar, geo, extras, more, regional, auth)
│   │   │   ├── deps.py              # Dependency injection: birth_utc, time conversions
│   │   │   └── routers/
│   │   │       ├── auth.py          # /api/auth: register, login, verify-otp, logout, me
│   │   │       ├── calendar.py      # /api/calendar: monthly calendar, festivals, muhurat
│   │   │       ├── core.py          # /api: planetary coordinates, houses, basic panchang
│   │   │       ├── extras.py        # /api/extras: tarot, numerology, horoscope, crystals
│   │   │       ├── geo.py           # /api/cities: city search, nearest city, timezone
│   │   │       ├── more.py          # /api/more: Human Design, I-Ching, Palmistry
│   │   │       ├── panchang.py      # /api/panchang: daily panchang (Drik Ganita), choghadiya, hora, rahu
│   │   │       ├── regional.py      # /api/regional: Tamil, Bengali, Malayalam regional calendars
│   │   │       └── vedic.py         # /api/kundli: Kundli, Vargas, Yogas, Prashna, KP, Varshaphala, Soul Guidance, Remedies
│   │   ├── core/
│   │   │   ├── ephem.py             # Swiss Ephemeris wrapper, Lahiri ayanamsha, sunrise/sunset, tithi
│   │   │   ├── auth.py              # User authentication, SQLite storage, password hashing, HMAC tokens
│   │   │   ├── i18n.py              # Multilingual dictionary, regex term replacer for 9 languages
│   │   │   ├── geo.py               # Cities database interface, population-weighted search
│   │   │   ├── kundli.py            # Basic Kundli calculations, Vimshottari dasha, Sade Sati
│   │   │   ├── charts_svg.py        # Dynamic SVG generators (North, South, East, Western, Sudarshan Chakra)
│   │   │   ├── vargas_ext.py        # All 31 Divisional Charts algorithms (D1 through D60, Tajika, Iyer)
│   │   │   ├── yogas_ext.py         # 60+ Classical Parashari Yogas scanner & rules engine
│   │   │   ├── interpret_ext.py     # 144 House Lord combinations (*BPHS* Ch. 26) & 12 Shad Phala
│   │   │   ├── ashtakavarga_ext.py  # 8 Bhinnashtakavarga, SAV, Trikona & Ekadhipatya Shodhana, Shodhya Pindas
│   │   │   ├── special_lagnas.py    # 9 Special Lagnas & 12 Arudha Padas with exception rules
│   │   │   ├── varshaphala.py       # Annual Solar Return, Muntha, Varshesha, Mudda Dasha
│   │   │   ├── tajika.py            # 24 Tajika Sahams & Nadiamsha calculations
│   │   │   ├── kp.py                # Krishnamurti Paddhati: Placidus cusps, sub-lords, 1-249 table
│   │   │   ├── prashna.py           # Horary Prashna Engine: Tajika yogas, Ithasala, Ishrafa, confidence, timing
│   │   │   ├── remedies_corpus.py   # Atmakaraka, Ishta Devata, Purushartha matrix, 9 Graha Mantras
│   │   │   └── pdf_report.py        # Multi-page PDF life report generation (ReportLab)
│   │   └── web/
│   │       └── __init__.py          # Jinja2 server-rendered web routes, auth state injection, context filters
│   ├── tests/
│   │   ├── conftest.py              # Pytest setup and fixtures
│   │   ├── test_auth.py             # 3 tests for auth, Gmail auto-verification, OTP
│   │   ├── test_core.py             # 5 core astronomical tests
│   │   ├── test_day_extras.py       # 6 tests for daily extras
│   │   ├── test_extras.py           # 4 tests for auxiliary tools
│   │   ├── test_kundli.py           # 4 tests for Kundli and Vimshottari
│   │   ├── test_panchang_drik.py    # 5 tests for Drik Ganita ephemeris calibration
│   │   ├── test_prashna_and_remedies.py # 5 tests for Prashna, Soul Guidance, and Remedies
│   │   ├── test_round3.py           # 16 tests for matching, vargas, muhurats
│   │   ├── test_round4.py           # 16 tests for regional calendars and doshas
│   │   └── test_vedic_enhancements.py # 27 tests for special lagnas, ashtakavarga, yogas, KP
│   ├── cities.db                    # SQLite database containing 150,000+ world cities
│   ├── ephe/                        # Swiss Ephemeris data files (.se1)
│   └── requirements.txt             # Python dependencies
├── website/
│   ├── static/
│   │   ├── style.css                # Responsive, high-contrast Vedic UI styling
│   │   ├── app.js                   # Client-side city auto-complete, geolocation, language toggle
│   │   ├── embed.js                 # Embeddable Panchang widget script
│   │   ├── logo.svg                 # Brand SVG logo
│   │   └── favicon.svg              # Brand SVG favicon
│   └── templates/
│       ├── base.html                # Global layout with topbar, auth status, live clock, language selector
│       ├── home.html                # Homepage with today's panchang and quick links
│       ├── panchang.html            # Daily Vedic Panchang with complete planetary details
│       ├── kundli.html              # Janam Kundli with 11 Classical Worksheets
│       ├── prashna.html             # Classical Horary Divination interface
│       ├── login.html               # User sign-in, Gmail instant verification & OTP interface
│       ├── vargas.html              # 31 Divisional Charts grid with Sahams & Nadiamshas
│       ├── yogas.html               # 60+ Classical Yogas scanner page
│       ├── reading.html             # Holistic Life Reading & 144 House Lords
│       ├── varshaphala.html         # Annual Solar Return chart & Mudda Dasha
│       ├── kp.html                  # Krishnamurti Paddhati (KP) System desk
│       ├── calendar.html            # Monthly Hindu Calendar
│       ├── festivals.html           # Annual Hindu festival and vrat calendar
│       ├── choghadiya.html          # Day and Night Choghadiya table
│       ├── hora.html                # 24-hour planetary hora table
│       ├── matching.html            # 36 Guna Milan & Porutham marriage compatibility
│       └── ...                      # Additional esoteric and regional templates
├── knowledge_base/                  # Deep-dive research papers and mathematical documentation
├── Dockerfile                       # Production multi-stage Docker container specification
├── run.bat                          # Windows execution script
├── run.ps1                          # PowerShell execution script
└── history.md                       # This master architectural and API documentation file
```

---

## 3. Core Astronomical & Mathematical Engines

### 3.1 Astronomical Engine (`api/app/core/ephem.py`)
* **Swiss Ephemeris Binding**: Interfaces with `swisseph` C-library via Python bindings.
* **Sidereal Ayanamsa Calibration**:
  - Default: **Lahiri (Chitra Paksha)** (`SE_SIDM_LAHIRI`).
  - Supported options: `lahiri_swiss`, `raman`, `kp`, `kp_new`, `yukteshwar`, `bhasin`, `true_chitra`, `fagan_bradley`, `suryasiddhanta`, `sayana` (tropical).
* **Julian Day Conversion**: Converts local wall-clock time + IANA timezone into UTC and computes Julian Day (`jd_from_utc(dt_utc)`).
* **House Systems**:
  - `whole_sign` (`W`): Equal 30° divisions based strictly on the ascending sign.
  - `placidus` (`P`): Time-proportional quadrant division of the diurnal/nocturnal arcs.
  - `equal` (`E`): 30° divisions starting from the exact Ascendant degree.
* **Combustion (Kopa / Asta)**: Planet within canonical solar orb: Moon (12°), Mars (17°), Mercury (14° direct, 12° retro), Jupiter (11°), Venus (10° direct, 8° retro), Saturn (15°).
* **Panchangam Calculations**:
  - **Tithi**: Angular distance between Moon and Sun divided by 12°. `(Moon - Sun) % 360 / 12`. Range: 1 to 30.
  - **Nakshatra**: Moon's sidereal longitude divided by 13°20' (800 arcminutes). Range: 1 to 27.
  - **Pada**: Remainder within the nakshatra divided by 3°20' (200 arcminutes). Range: 1 to 4.
  - **Yoga**: Sum of Sun's and Moon's sidereal longitudes divided by 13°20'. `(Sun + Moon) % 360 / (360/27)`. Range: 1 to 27.
  - **Karana**: Half-tithi calculation. `(Moon - Sun) % 360 / 6`. Moving karanas (Bava to Vishti) repeated 8 times + 4 fixed karanas (Shakuni, Chatushpada, Naga, Kimstughna).

---

### 3.2 31 Divisional Charts Engine (`api/app/core/vargas_ext.py`)
Computes the exact harmonic sign and degree for all 9 planets and Lagna across:
* **16 Parashara Shodashavargas**:
  1. `D1` (Rashi): Physical body and general destiny.
  2. `D2` (Hora): Wealth, assets, and financial sustenance (Sun: Leo/Cancer, Moon: Cancer/Leo).
  3. `D3` (Drekkana): Siblings, courage, vitality, and motivation (Parashari 1st, 5th, 9th sign method).
  4. `D4` (Chaturthamsha): Real estate, home, vehicles, and fixed assets.
  5. `D7` (Saptamsha): Children, grandchildren, and creative lineage.
  6. `D9` (Navamsha): Soul's dharma, marriage partner, and spiritual trajectory.
  7. `D10` (Dashamsha): Career, executive achievements, status, and fame.
  8. `D12` (Dwadashamsha): Parents, ancestral heritage, and past-life karma.
  9. `D16` (Shodashamsha): Vehicles, comforts, conveyances, and inner happiness.
  10. `D20` (Vimshamsha): Spiritual progress, religious devotions, and meditation.
  11. `D24` (Chaturvimshamsha / Siddhamsa): Higher education, academic intellect, and learning.
  12. `D27` (Saptavimshamsha / Nakshatramsha): Strengths, subconscious weaknesses, and vitality.
  13. `D30` (Trimshamsha): Misfortunes, evils, psychological flaws, and afflictions (Odd: Mars, Saturn, Jupiter, Mercury, Venus; Even: reverse).
  14. `D40` (Khavedamsha): Auspicious and inauspicious occurrences, deep karmic inheritances.
  15. `D45` (Akshavedamsha): Purity of character, general well-being, and moral rectitude.
  16. `D60` (Shashtiamsha): Supreme divisional chart; all past-life karmas (*BPHS*: superior to all other vargas).
* **5 Tajika & Nadi Vargas**:
  - `D6` (Khashthamsha): Health, chronic ailments, and legal rivalries.
  - `D8` (Ashtamsha): Longevity, sudden obstacles, inheritance, and transformations.
  - `D11` (Rudramsha): Hidden gains, windfall wealth, and disputes.
  - `D150` (Nadiamsha): 12 arcminute micro-subdivision mapping the 150 classical Nadi archetypes.
* **10 Seshadhri Iyer Harmonic Vargas**:
  - `D5` (Panchamsha): Fame and authority.
  - Additional higher harmonics providing specialized esoteric insights.

---

### 3.3 Special Lagnas & Arudhas Engine (`api/app/core/special_lagnas.py`)
Computes mathematical sensitive points derived from the diurnal solar cycle and planetary motions:
* **Bhava Lagna (BL)**: Progresses at 1 sign per 2 hours (12 signs in 24 hours) from Sunrise.
* **Hora Lagna (HL)**: Progresses at 1 sign per hour (24 signs in 24 hours) from Sunrise; used to analyze financial fortune and wealth.
* **Ghatika Lagna (GL)**: Progresses at 1 sign per Ghati (24 minutes, 60 signs in 24 hours); used to evaluate executive authority and political power.
* **Pranapada Lagna (PP)**: Derived from the Sun's longitude and elapsed time; used to verify birth time authenticity.
* **Vighati Lagna**: Rapid sub-minute ascendant for fine micro-timing.
* **Sree Lagna (SL)**: Derived from Moon's nakshatra traversal applied to the natal Ascendant; marks prosperity.
* **Indu Lagna (IL)**: Wealth point derived from the 9th house rays of the Lagna and Moon lords.
* **Kunda**: 81st harmonic ascendant for second-level rectification.
* **Varnada Lagna (VL)**: Evaluates social interactions and relationships.
* **12 Arudha Padas (A1 to A12)**:
  - **Arudha Lagna (AL)**: External image, worldly status, and social perception.
  - **Upapada Lagna (UL / A12)**: Marriage partner, marital longevity, and domestic harmony.
  - **Canonical Exception Rule**: If the Arudha falls in the same house or 7th from it, it shifts by 10 signs (per *BPHS* Ch. 29).

---

### 3.4 Ashtakavarga Engine (`api/app/core/ashtakavarga_ext.py`)
Implements the complete Parashari Ashtakavarga system:
1. **Bhinnashtakavarga (BAV)**: 8 individual contribution grids for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, and Ascendant based on beneficial positions from their respective locations.
2. **Sarvashtakavarga (SAV)**: Cumulative score for each of the 12 signs (sum of 7 planetary BAVs, total 337 points).
3. **Trikona Shodhana (Triplicity Reduction)**:
   - Evaluates triangular groups: Fire (1, 5, 9), Earth (2, 6, 10), Air (3, 7, 11), Water (4, 8, 12).
   - Replaces each sign's points with points minus the minimum of the three signs.
4. **Ekadhipatya Shodhana (Dual-Sign Reduction)**:
   - For planets ruling two signs (Mars: 1/8, Mercury: 3/6, Jupiter: 9/12, Venus: 2/7, Saturn: 10/11), reductions are made based on occupancy by planets.
5. **Shodhya Pindas**:
   - **Rashi Pinda**: Reduced bindus multiplied by planetary sign multipliers (Sun 7, Moon 10, Mars 8, Mercury 5, Jupiter 10, Venus 7, Saturn 5).
   - **Graha Pinda**: Points multiplied by planet-specific constants.
   - **Yoga Pinda**: Sum of Rashi Pinda and Graha Pinda; represents the pure energetic index used for longevity and transit timing.

---

### 3.5 Classical Yogas Scanner (`api/app/core/yogas_ext.py`)
Scans 60+ authentic classical combinations:
* **Pancha Mahapurusha Yogas**:
  - *Ruchaka* (Mars in Kendra in Own/Exaltation sign).
  - *Bhadra* (Mercury in Kendra in Own/Exaltation sign).
  - *Hamsa* (Jupiter in Kendra in Own/Exaltation sign).
  - *Malavya* (Venus in Kendra in Own/Exaltation sign).
  - *Sasa* (Saturn in Kendra in Own/Exaltation sign).
* **Raja Yogas**: Conjunctions, mutual aspects, or sign exchanges (Parivartana) between Kendra lords (1, 4, 7, 10) and Trikona lords (1, 5, 9).
* **Dhana Yogas**: Auspicious links between 2nd (wealth), 11th (gains), 1st (self), 5th, and 9th houses.
* **Viparita Raja Yogas**: *Harsha* (6th lord in 6th/8th/12th), *Sarala* (8th lord in 6th/8th/12th), *Vimala* (12th lord in 6th/8th/12th).
* **Solar & Lunar Yogas**: *Sunapha*, *Anapha*, *Dhurdhura*, *Kemadruma*, *Vesi*, *Vasi*, *Ubhayachari*.
* **Saraswati Yoga**: Jupiter, Venus, and Mercury in kendras/trikonas/2nd house with Jupiter in strength.

---

### 3.6 Prashna Horary Engine (`api/app/core/prashna.py`)
Implements Tajika Horary Divination (*Prashna Tantra* & *Daivajna Vallabha*):
* **Significators**:
  - **Lagnesha**: Ruler of the Prashna Lagna representing the Querent.
  - **Karyesha**: Ruler of the house governing the matter asked (10th for career, 7th for marriage, 2nd/11th for wealth, etc.).
  - **Chandra (Moon)**: Natural karaka for the flow of events and mental clarity.
* **Deeptamsha Orbs**: Sun (15°), Moon (12°), Mars (8°), Jupiter (9°), Saturn (9°), Mercury (7°), Venus (7°).
* **Tajika Yogas**:
  - **Ithasala (Muthashila)**: Applying aspect where a faster planet with lower longitude aspects a slower planet within mean Deeptamsha orb.
  - **Ishrafa (Musaripha)**: Separating aspect where the faster planet has surpassed the slower planet.
  - **Nakta Yoga**: An intermediary faster planet (Moon/Mercury) transfers light from Lagnesha to Karyesha.
  - **Yamaya Yoga**: A slower planet in superior position gathers light from both significators.
  - **Kamboola Yoga**: Moon joins the Ithasala combination, confirming certainty of outcome.
* **Fulfillment Timeframe**: Computed using sign mobility:
  - Movable signs (Chara): Days to weeks.
  - Dual signs (Dvisvabhava): Weeks to months.
  - Fixed signs (Sthira): Months to years, or requires repeated effort.

---

### 3.7 Soul Guidance & Remedies Engine (`api/app/core/remedies_corpus.py`)
* **Atmakaraka (AK)**: Highest-degree planet (0° to 30°) in any sign excluding Rahu/Ketu. Represents the individual soul and life's core evolutionary lesson.
* **Karakamsha (KL)**: Navamsha sign occupied by the Atmakaraka.
* **Ishta Devata (*Jaimini Sutras* 1.2.69-72)**: Deity associated with the planet ruling the 12th house from Karakamsha in Navamsha. Bestows spiritual liberation (Moksha) and dissolves deep karmas.
* **Dharma Devata**: Deity ruling the 9th house from Karakamsha; guides vocational ethics and righteousness.
* **Palana Devata**: Deity ruling the 6th house from Amatyakaraka (AmK) in Navamsha; provides livelihood protection.
* **Purushartha Alignment Matrix**:
  - Triplicity scoring: Dharma (1, 5, 9), Artha (2, 6, 10), Kama (3, 7, 11), Moksha (4, 8, 12).
  - Normalizes scores to 100% and outputs actionable guidance.
* **9 Graha Mantras**: Authentic Sanskrit Beej, Puranic, and Gayatri mantras with exact counts, rosary materials, and conduct remedies.

---

### 3.8 Authentication & Anti-Spam Security (`api/app/core/auth.py`)
* **Storage**: SQLite table (`users.db`) tracking `email`, `password_hash`, `is_verified`, `verification_code`, `code_expires_at`, `tier`.
* **Gmail Instant Verification**: Any user signing up with `@gmail.com` or `@googlemail.com` is automatically verified without email confirmation hurdles.
* **Passwordless OTP**: Users on other domains receive a 6-digit verification code valid for 30 minutes.
* **Signed HMAC-SHA256 Tokens**: Cryptographic session tokens stored in `ph_auth` cookie and HTTP Authorization headers.
* **Feature Gating**: Protects high-compute endpoints (PDF exports, full Shodashavarga, Prashna, KP System) against automated bot scraping while keeping basic daily Panchang open to the public.

---

### 3.9 Multilingual Translation Engine (`api/app/core/i18n.py`)
* **Supported Languages**: English (`en`), Hindi (`hi`), Marathi (`mr`), Gujarati (`gu`), Bengali (`bn`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Malayalam (`ml`).
* **Coverage**: Over 196 mapped terms per language across:
  - 9 Planets (Grahas)
  - 12 Signs (Rashis)
  - 27 Nakshatras
  - 30 Tithis
  - 27 Yogas
  - 11 Karanas
  - 2 Pakshas
  - 7 Weekdays (Vaaras)
  - 12 Hindu Months (Masa)
  - 6 Ritus (Seasons)
  - 2 Ayanas (Uttarayana, Dakshinayana)
  - UI Labels (Prashna, Kundli, Soul Guidance, Atmakaraka, Ishta Devata, Sign In, etc.)
* **Dual Execution Modes**:
  - **API Middleware**: Automatically intercepts JSON responses and replaces terms if `?lang=...` is passed.
  - **HTML Web Templates**: Server-side template filter `localize_html(html, lang)` replaces text nodes while preserving HTML attributes, scripts, and forms.

---

## 4. Complete REST API Reference

All endpoints accept query parameters or JSON payloads as documented below.

### 4.1 Core Astronomical & Panchang Endpoints

#### `GET /api/panchang`
Returns full daily Panchang for a specific date and location.
* **Query Parameters**:
  - `date`: `YYYY-MM-DD` (defaults to today)
  - `lat`: Latitude float (e.g. `28.6139`)
  - `lon`: Longitude float (e.g. `77.2090`)
  - `tz`: IANA timezone (e.g. `Asia/Kolkata`)
  - `lang`: Optional language code (`hi`, `gu`, `ta`, etc.)
* **Response**: Sunrise, sunset, moonrise, moonset, Tithi, Nakshatra, Yoga, Karana, Vaara, Paksha, Ritu, Ayana, Gulika, Rahu Kaal, Yamaganda, and planetary positions.

#### `GET /api/choghadiya`
Returns Day and Night Choghadiya intervals with auspicious/inauspicious classifications (Amrit, Shubh, Labh, Char, Rog, Kaal, Udveg).

#### `GET /api/hora`
Returns 24-hour planetary hora table starting from sunrise.

#### `GET /api/rahu`
Returns Rahu Kalam, Yamaganda, and Gulika Kaal timings.

---

### 4.2 Vedic Astrology & Kundli Endpoints

#### `POST /api/kundli`
Computes the complete Janam Kundli.
* **Request Body**:
  ```json
  {
    "date": "1990-10-24",
    "time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "ayanamsa": "lahiri",
    "house_system": "whole_sign",
    "dasha_levels": 3
  }
  ```
* **Response**:
  - `lagna`: Ascendant degree, sign, nakshatra, and pada.
  - `planets`: All 9 planets with degrees, signs, houses, dignities (Exalted, Moolatrikona, Own, Friendly, Neutral, Enemy, Debilitated), avasthas (Baladi, Jagradadi), combustion, and retrogradation.
  - `vargas`: Core four divisional charts (D1, D9, D10, D3).
  - `dashas`: Complete multi-level Vimshottari Dasha hierarchy with exact transition dates.
  - `ashtakavarga`: BAV and SAV matrices.
  - `shadbala`: Sthana, Dig, Kala, Chesta, Naisargika, Drik, and Total Rupas.

#### `POST /api/kundli/vargas`
Computes all 31 Divisional Charts (Shodashavargas, Tajika/Nadi, and Iyer harmonics) plus 24 Tajika Sahams and Nadiamshas.

#### `POST /api/kundli/yogas`
Scans and returns all active classical yogas (Pancha Mahapurusha, Raja, Dhana, Viparita, Solar, Lunar, Saraswati).

#### `POST /api/kundli/special-lagnas`
Returns 9 Special Lagnas (Bhava, Hora, Ghatika, Pranapada, Vighati, Sree, Indu, Kunda, Varnada) and 12 Arudha Padas (A1–A12).

#### `POST /api/kundli/ashtakavarga-suite`
Returns 8 BAVs, SAV, Trikona Shodhana, Ekadhipatya Shodhana, and Shodhya Pindas.

#### `POST /api/kundli/kp`
Computes Krishnamurti Paddhati (KP System) astrology: Placidus cusps, 4-fold significators, Ruling Planets, Sign/Star/Sub/Sub-Sub lords, and optional 1-249 Horary table.

#### `POST /api/kundli/varshaphala`
Tajika Annual Solar Return chart: Varsha Lagna, Muntha, Varshesha, Mudda Dasha, and 24 Sahams.

#### `POST /api/kundli/prashna`
Classical Vedic Horary Divination (*Prashna Tantra* & *Daivajna Vallabha*).
* **Request Body**:
  ```json
  {
    "date": "2026-10-18",
    "time": "15:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "query_category": "career",
    "question_text": "Will I get selected for the executive position?"
  }
  ```
* **Response**:
  - `verdict`: Clear text verdict.
  - `verdict_badge`: `favorable`, `mixed`, or `unfavorable`.
  - `confidence_score`: 0 to 100%.
  - `timeframe`: Estimated fulfillment timeframe.
  - `tajika_yogas`: Status of Ithasala, Ishrafa, Nakta, Yamaya, and Kamboola yogas.
  - `testimonies`: Canonical classical planetary reasons.

#### `POST /api/kundli/soul-guidance`
Returns Atmakaraka, Karakamsha, Ishta Devata, Dharma Devata, Palana Devata, and 4 Purushartha Life Goals Matrix.

#### `POST /api/kundli/remedies-corpus`
Returns full remedial dossier prioritized by chart afflictions (debilitated, combust, 6th/8th/12th houses).

#### `GET /api/kundli/mantras`
Returns catalog of authentic Beej, Gayatri, and Puranic mantras, prescribed counts, and ritual rules for all 9 Grahas.

---

### 4.3 Authentication Endpoints

#### `POST /api/auth/register`
* **Request Body**: `{"email": "user@gmail.com", "password": "...", "name": "..."}`
* **Response**: Creates account, auto-verifies Gmail accounts, sets `ph_auth` cookie, and returns session token.

#### `POST /api/auth/login`
* **Request Body**: `{"email": "...", "password": "..."}`
* **Response**: Verifies credentials, sets `ph_auth` cookie, and returns user profile.

#### `POST /api/auth/verify-otp`
* **Request Body**: `{"email": "...", "code": "123456"}`
* **Response**: Verifies 6-digit code and marks account verified.

#### `POST /api/auth/logout`
Clears session cookie.

#### `GET /api/auth/me`
Returns current user profile and verification status.

---

### 4.4 Geolocation Endpoints

#### `GET /api/cities?q=delhi&limit=10`
Searches 150,000+ cities with population weighting and returns coordinates and timezones.

#### `GET /api/cities/nearest?lat=28.61&lon=77.20`
Returns the nearest city to given coordinates.

#### `GET /api/cities/timezone?tz=Asia/Kolkata`
Returns the primary representative city for a given IANA timezone.

---

## 5. Website UI & Template Architecture

The frontend is server-rendered via Jinja2 with lightweight progressive vanilla JS:
1. **`website/templates/base.html`**:
   - Master layout including topbar with live timezone clock, civil date, language dropdown (`#langSel`), and member authentication pill.
   - City search bar with live auto-complete suggestion dropdown (`#citySugg`).
   - Sticky sidebar navigation organizing tools into Panchang, Calendars, Jyotish, and Esoteric sections.
2. **`website/templates/kundli.html`**:
   - Organized into **11 Interactive Worksheets**:
     - Worksheet 1: Birth Charts (D1, Chandra, D9) & Planetary Dignities/Avasthas.
     - Worksheet 2: Shodashavarga Grid (D1 through D60).
     - Worksheet 3: Sudarshan Chakra (Lagna, Chandra, Surya concentric rings).
     - Worksheet 4: Special Lagnas (9 points) & Arudha Padas (A1–A12).
     - Worksheet 5: Ashtakavarga Suite (SAV, Reductions, Shodhya Pindas).
     - Worksheet 6: Shadbala & Bhava Bala.
     - Worksheet 7: Multi-Level Vimshottari & Yogini Dasha Tables.
     - Worksheet 8: Varshaphala Annual Solar Return & Mudda Dasha.
     - Worksheet 9: KP System (Placidus cusps, sub-lords, 1-249 Horary).
     - Worksheet 10: Classical Slokas (*BPHS* Ch. 26) for 144 House Lords & 12 Shad Phala.
     - Worksheet 11: Soul Guidance (Atmakaraka, Ishta Devata, Purusharthas) & Prioritized Japa Mantras.
3. **`website/templates/prashna.html`**:
   - 8 query domains selector, question input, verdict badge, confidence meter, timeline, SVG moment chart, and Tajika yogas table.
4. **`website/templates/login.html`**:
   - 1-click Gmail instant verification, OTP verification, and member benefits overview.
5. **`website/static/app.js`**:
   - City search auto-complete with debouncing and coordinate auto-fill.
   - Browser geolocation detection (`navigator.geolocation`) with fallback to browser timezone.
   - Language selector cookie handler (`ph_lang`).
6. **`website/static/style.css`**:
   - Clean, professional Vedic color scheme: Deep maroon (`--kumkum`: `#8e1b3a`), turmeric gold (`--haldi`: `#c58312`), auspicious green (`--good`: `#2e7d32`), and high-contrast typography.

---

## 6. Verification & Automated Test Suite

The test suite contains **91 automated pytest tests** covering every mathematical algorithm, API endpoint, and web route:
* `api/tests/test_auth.py`: 3 tests verifying registration, Gmail auto-verification, OTP verification, and session checks.
* `api/tests/test_core.py`: 5 astronomical tests verifying Swiss Ephemeris coordinates and house systems.
* `api/tests/test_panchang_drik.py`: 5 tests verifying Tithi, Nakshatra, and sunrise/sunset against canonical Drik Ganita standards.
* `api/tests/test_kundli.py`: 4 tests verifying planetary dignities, avasthas, and Vimshottari dasha calculations.
* `api/tests/test_vedic_enhancements.py`: 27 tests verifying Special Lagnas, Arudhas, Ashtakavarga reductions, Shodhya Pindas, 60+ Yogas, and KP sub-lords.
* `api/tests/test_prashna_and_remedies.py`: 5 tests verifying all 8 Prashna query domains, Tajika yogas, Atmakaraka, Ishta Devata, and web rendering.
* `api/tests/test_round3.py` & `test_round4.py`: 32 tests covering compatibility matching, regional calendars, and esoteric tools.

**Test Execution Command**:
```bash
pytest api/tests
# Result: 91 passed in ~32s (100% green)
```

---

## 7. Production Deployment Guide for Grok, Claude, and Codex

To take this platform to production and launch publicly, follow these steps:

### 7.1 Local Development / Direct Run
```bash
# 1. Navigate to directory
cd D:\astrology\api

# 2. Create virtual environment & install requirements
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 3. Launch with Uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

### 7.2 Docker & Containerized Production Run
The project contains a production-ready `Dockerfile`:
```bash
# Build Docker image
docker build -t panchanghub-astrology:latest .

# Run Docker container
docker run -d --name astrology-app -p 8080:8080 -v astrology_data:/app/data panchanghub-astrology:latest
```

### 7.3 Nginx Reverse Proxy Configuration (Production HTTPS)
Place in `/etc/nginx/sites-available/panchanghub.conf`:
```nginx
server {
    server_name panchanghub.com www.panchanghub.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /var/www/panchanghub/website/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/panchanghub.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panchanghub.com/privkey.pem;
}

server {
    listen 80;
    server_name panchanghub.com www.panchanghub.com;
    return 301 https://$host$request_uri;
}
```

### 7.4 Systemd Linux Service (`/etc/systemd/system/astrology.service`)
```ini
[Unit]
Description=PanchangHub Vedic Astrology & Divination Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/astrology/api
Environment="PATH=/var/www/astrology/api/.venv/bin"
Environment="PH_SECRET_KEY=your_production_secret_key_here"
ExecStart=/var/www/astrology/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8080 --workers 4

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## 8. Summary of Completed Objectives

1. **Unified Codebase Directory**: All project files, engines, databases, templates, knowledge bases, and tests are unified in [`D:\astrology`](file:///D:/astrology).
2. **Detailed System Documentation**: Complete architectural, mathematical, and API documentation compiled in `history.md`.
3. **Anti-Spam Email Authentication**: Secure member email authentication, Gmail auto-verification, and 6-digit OTP verification implemented across API, database, and Web UI.
4. **Multilingual Localization**: All 9 major Indian languages fully supported with native translations for over 196 astrological terms and UI elements.
5. **Quality Assurance**: Complete test coverage with 91 / 91 passing tests (100% green). Live server verified and active.

---

## 9. Vedic Astro-Numerology (Anka Shastra & Kundli Synthesis) Engine

### 9.1 Mathematical Engine & Features
- **Astro-Kundli Synthesis (`synthesize_astro_numerology`)**: Synthesizes natal Kundli with Numerological roots. Determines planetary rulers for Lagna Lord, Moon Sign Lord, Janma Nakshatra Lord, Sun Sign Lord, Jaimini Atmakaraka (AK), and active Vimshottari Mahadasha/Antardasha lords. Calculates a Cosmic Harmony Percentage Score (0–100%) and classical concordance verdict.
- **Lucky Numbers Generator (`generate_lucky_bundle`)**: Generates primary Moolank, destiny Bhagyank, and name Chaldean roots; harmonized lucky roots; 2-digit Compound Power Numbers (10 to 55) with classical occult meanings; fortunate calendar dates of every month; auspicious weekdays; gemstones; metals; directions; and planetary Beej Mantras.
- **Numbers to Avoid / Shatru Anka (`get_numbers_to_avoid`)**: Calculates conflicting digits based on planetary friendship matrices (*Mitra/Shatru*), discordant calendar dates to avoid for high-stakes decisions/contracts/travel, discordant planetary rulers, and inauspicious colors.
- **Karmic Debt Analysis (`analyze_karmic_debts`)**: Detects 13/4 (laziness/rebuilding), 14/5 (freedom abuse/temperance), 16/7 (ego collapse/spiritual reawakening), and 19/1 (misuse of power/selflessness) across Life Path, Birthday, Expression, and Soul Urge with past-life root causes, present life symptoms, and actionable soul remedies.
- **Life Epochs & 4 Pinnacles (`calculate_pinnacles_and_challenges`)**: Computes 4 Life Pinnacles with exact age spans (Foundation: 36 - LifePath; Productivity: next 9 yrs; Maturity: next 9 yrs; Culmination: rest of life) and 4 Life Challenges.
- **Real-Time Transit Numerology (`analyze_current_transits_numerology`)**: Calculates Universal Day/Month/Year, Personal Day/Month/Year, 9-Year Epicycle Phase, and transit-harmonized daily lucky numbers backed by Swiss Ephemeris real-time planetary positions.
- **Lo Shu Magic Square (`analyze_lo_shu_grid`)**: Full 3x3 magic square with 8 Planes & Arrows of Fortune (Mind, Soul, Body, Thought, Will, Action, Golden Prosperity, Silver Spirituality) identifying active strengths and missing karmic lessons.

### 9.2 Endpoints & UI
- `GET /api/numerology`: Full profile with optional birth details for astro-synthesis.
- `POST /api/numerology/chart`: Accepts full `AstroNumerologyReq` birth data.
- `GET /api/numerology/lucky`: Quick endpoint for personal lucky numbers, power numbers, and numbers to avoid.
- `GET /api/numerology/transits`: Real-time Gochar transit numerology & daily lucky numbers.
- `GET /api/numerology/pinnacles`: 4 Life Pinnacles, Challenges, and age epochs.
- `GET /numerology`: 6-tab responsive interactive Vedic UI with live client-side calculations and AJAX synthesis.


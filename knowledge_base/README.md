# Classical Astrological Knowledge Base & Computational Specification

This repository contains the comprehensive architectural synthesis, mathematical engines, classical rule systems, and non-plagiarized interpretive corpora derived from the reverse-engineering analysis of professional Vedic and mundane astrology software suites.

All materials in this directory are 100% vendor-agnostic, clean-room authored, free of proprietary identifiers, and mapped directly to classical Sanskrit texts (*Brihat Parashara Hora Shastra*, *Phaladeepika*, *Saravali*, *Jataka Parijata*, *Brihat Jataka*, *Suryasiddhanta*).

---

## Knowledge Base Catalog

| Module | Document | Scope & Technical Implementation |
|---|---|---|
| **01** | [`01_astronomical_and_calculation_engines.md`](./01_astronomical_and_calculation_engines.md) | High-precision ephemeris mathematics, Julian Day calculations, Delta-T approximations, LST, Ascendant equations, 11 Ayanamsha algorithms, complete mathematical formulas for all 16 Shodashavargas (D1 to D60), whole-sign vs quadrant house systems, and Shadbala/Ashtakavarga mathematical frameworks. |
| **02** | [`02_planetary_period_dasha_systems.md`](./02_planetary_period_dasha_systems.md) | Temporal timing engines: 5-level Vimshottari decomposition (Maha down to Prana), active running period resolution algorithms, 36-year Yogini Dasha with 8 sub-cycles, Jaimini Chara Dasha sign-progression algorithms, Kalachakra Dasha leap logic, and conditional nakshatra dashas. |
| **03** | [`03_classical_yoga_rules_and_dsl.md`](./03_classical_yoga_rules_and_dsl.md) | Domain Specific Language (DSL) and declarative evaluation grammar for 60+ classical Vedic combinations: Pancha Mahapurusha, Raja Yogas, Viparita Raja Yogas, Neechabhanga, Dhana Yogas, Solar/Lunar yogas, and Saraswati/Amala yogas. |
| **04** | [`04_vedic_interpretations_corpus.md`](./04_vedic_interpretations_corpus.md) | Non-plagiarized, professionally synthesized interpretive library covering: 12 Ascendant psychological and constitutional portraits, the 144 House Lord placement matrix (Lord 1–12 in Houses 1–12), and 12-house Shad Phala (favorable vs karmic growth potentials). |
| **05** | [`05_chart_styles_and_visualization.md`](./05_chart_styles_and_visualization.md) | Vector graphics rendering specifications: North Indian diamond chart geometry, South Indian fixed-sign square grid geometry, East Indian tetrahedral grid geometry, and Western 360° circular wheel geometry. |
| **06** | [`06_global_atlas_and_geolocation.md`](./06_global_atlas_and_geolocation.md) | High-performance compact global atlas architecture: 24-byte binary record encoding, $O(\log N)$ binary search lookup, timezone resolution, and integration with SQLite FTS5 for instant substring queries. |

---

## Active Platform Implementations

The specifications documented herein are actively integrated and running in the production API and website engines:

- **API Core Engines**:
  - `api/app/core/vargas_ext.py`: Full D1–D60 harmonic vargas, internal degrees, dignities, 60 Shastiamsa deities, and Vargottama detection.
  - `api/app/core/dashas_ext.py`: Deep 5-level Vimshottari, real-time target date resolution, Yogini dasha, and 7 Jaimini Chara Karakas.
  - `api/app/core/yogas_engine.py`: Classical rule scanner evaluating 60+ combinations with strength scoring.
  - `api/app/core/interpret_ext.py`: 12 Ascendant portraits, 144 Bhava Lord readings, and 12-house Shad Phala analysis.
  - `api/app/core/ephem.py`: 11 Ayanamsha modes (Lahiri, Raman, KP, KP New VP291, Sri Yukteshwar, JN Bhasin, True Chitra, Fagan-Bradley, Surya Siddhanta, Sayana).

- **REST API Endpoints**:
  - `POST /api/kundli/vargas`
  - `POST /api/kundli/dashas/current`
  - `POST /api/kundli/dashas/yogini`
  - `POST /api/kundli/dashas/chara`
  - `POST /api/kundli/reading`
  - `POST /api/kundli/yogas`
  - `POST /api/kundli/ayanamshas`

- **Interactive Web Pages**:
  - `/vargas`: Interactive Shodashavargas Explorer (North/South/East SVG charts, degrees, dignities, deities, Vargottama).
  - `/yogas`: Classical Yogas Scanner (Auspiciousness meter, category breakdown, conditions, manifestations).
  - `/reading`: Holistic Vedic Life Reading (Lagna portrait, current dasha timeline, Chara Karakas, 144 House Lord matrix, 12 Shad Phala).

"""
PanchangHub Detailed Text Reports, 22 Dasha Systems, 9-Menu Engine & Rectification Studio.
=========================================================================================
100% original clean-room implementation grounded in classical Jyotish treatises:
- Brihat Parashara Hora Shastra (BPHS)
- Saravali (Kalyana Varma)
- Phaladeepika (Mantreshwara)
- Brihat Jataka (Varahamihira)
- Jataka Parijata (Vaidyanatha Dikshita)
- Jaimini Upadesha Sutras
- Tajika Neelakanthi
- Garuda Purana & Mani Mala (Ratna Pariksha)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import math

from .ephem import (
    SIGNS, RASHIS, NAKSHATRAS, NAK_LORDS, SIGN_LORDS, VEDIC_PLANETS,
    all_positions, houses, sign_info, nakshatra_of, norm, angdiff, dms,
    jd_from_utc, local_from_jd, ayanamsa,
)
from .kundli import (
    YEAR_DAYS, VIM_ORDER, VIM_YEARS, YOGINIS, EXALT, EXALT_DEG, OWN, MOOLA,
    FRIENDS, relation, dignity, varga_sign, VARGAS, vimshottari, yogini,
    ashtakavarga, sade_sati, manglik, kaal_sarp, compute_kundli,
)
from . import dashas as _dashas_core
from . import advanced as _adv_core
from . import shadbala as _sb_core
from .interpret_ext import generate_holistic_reading
from .yogas_engine import evaluate_all_yogas
from .classical_corpus import generate_comprehensive_corpus_reading
from .tajika_sahams import compute_tajika_sahams
from .special_lagnas import compute_special_lagnas
from .ashtakavarga_ext import full_ashtakavarga_suite
from .remedies_corpus import get_complete_remedies_for_chart, GRAHA_REMEDIES


# ==============================================================================
# 1. CATALOG OF REPORT MODELS, 9 TOP-LEVEL MENUS & 68 WORKSHEETS
# ==============================================================================

REPORT_MODELS_CATALOG: List[Dict[str, Any]] = [
    {
        "code": "HC1",
        "category": "Horoscope Calculations",
        "title": "Horoscope Calculations — Essential (HC1)",
        "estimated_pages": 8,
        "description": "Essential Vedic birth calculations, Rashi/Moon/Navamsha/Sripati Bhava charts, Sudarshan Chakra, Shodashavarga summary, and Vimshottari Mahadasha/Antardasha tables.",
        "chapter_ids": ["314", "300", "304", "305", "307", "315", "376"],
    },
    {
        "code": "HC2",
        "category": "Horoscope Calculations",
        "title": "Horoscope Calculations — Standard (HC2)",
        "estimated_pages": 23,
        "description": "Includes HC1 plus 16 Divisional Charts, Panchadha Maitri Friendship, Full Shadbala & Bhava Bala, Graha/Rashi Drishti Aspects, Planetary Avasthas, Ashtakavarga (BAV/SAV/Reductions), Yogini & Ashtottari Dashas.",
        "chapter_ids": ["314", "300", "304", "302", "303", "305", "307", "306", "312", "310", "333", "330", "332", "338", "315", "325", "361", "345"],
    },
    {
        "code": "HC3",
        "category": "Horoscope Calculations",
        "title": "Horoscope Calculations — Comprehensive (HC3)",
        "estimated_pages": 43,
        "description": "Includes HC2 plus 11 Upagrahas & 15 Sphutas, Health/Ayurveda Physiology, Full 9-Planet Vimshottari AD/PD, Sookshma Dashas, Sadhesati & Kantaka Saturn, KP Significators, and Jaimini System with Chara Dasha.",
        "chapter_ids": ["314", "300", "337", "304", "302", "303", "395", "305", "307", "306", "312", "310", "333", "330", "332", "338", "346", "350", "315", "316", "373", "361", "345", "386", "391", "334", "335", "311", "369"],
    },
    {
        "code": "HC4",
        "category": "Horoscope Calculations",
        "title": "Horoscope Calculations — Archival Master (HC4)",
        "estimated_pages": 52,
        "description": "Complete mathematical compendium across all 16 Vargas, all 22 Dasha systems, Shadbala, Ashtakavarga Pindas, Upagrahas, Sphutas, Jaimini, and KP tables.",
        "chapter_ids": ["314", "300", "337", "304", "302", "303", "395", "305", "307", "306", "312", "310", "333", "330", "332", "338", "346", "350", "315", "316", "373", "361", "345", "363", "369", "386", "391", "334", "335", "311"],
    },
    {
        "code": "HP1",
        "category": "Horoscope Calculations & Interpretations",
        "title": "Horoscope Calculations & Interpretations — Concise (HP1)",
        "estimated_pages": 20,
        "description": "Includes HC1 plus Panchanga/Avakhada/Ghata Chakra, Nature & Temperament, Physical Constitution, Lucky Points, Birth Nakshatra & Pada Analysis, Mangala Dosha, Sadhesati Remedies, Gemstone Recommendations, and 5-Year Dasha Predictions.",
        "chapter_ids": ["200", "201", "314", "202", "203", "204", "300", "304", "305", "307", "205", "392", "315", "376", "386", "387", "397", "398", "701"],
    },
    {
        "code": "HP2",
        "category": "Horoscope Calculations & Interpretations",
        "title": "Horoscope Calculations & Interpretations — Standard (HP2)",
        "estimated_pages": 55,
        "description": "Includes HC2 + HP1 plus the 9-Planet Dispositions Treatise (Graha Phala: Sun through Ketu), 12 House Lords Treatise (Bhavesh Phala), Mangala Dosha Remedies, and 10-Year Dasha & Antardasha Predictions.",
        "chapter_ids": ["200", "201", "314", "202", "203", "204", "300", "304", "302", "303", "305", "307", "306", "312", "310", "333", "330", "332", "338", "205", "207", "216", "392", "393", "386", "387", "397", "398", "315", "325", "701", "361", "345"],
    },
    {
        "code": "HP3",
        "category": "Horoscope Calculations & Interpretations",
        "title": "Horoscope Calculations & Interpretations — Complete Dossier (HP3)",
        "estimated_pages": 105,
        "description": "Full flagship book-format treatise: HC3 + HP2 + Sadhesati/Dhayya/Kantaka Results + Classics in English (12 Houses, Planetary Yogas, Jaimini Karakamsha/Padas, Curses & Remedies) + Categorized Classical Yogas (Benefic, Malefic, Mixed) + Life Thematic Synthesis + 20-Year Dasha/Antardasha Predictions + Gochara Transit Interpretations.",
        "chapter_ids": ["200", "201", "314", "202", "203", "204", "300", "337", "304", "302", "303", "395", "305", "307", "306", "312", "310", "333", "330", "332", "338", "346", "350", "205", "207", "216", "802", "803", "804", "805", "806", "807", "808", "251", "392", "393", "386", "387", "388", "389", "390", "391", "397", "398", "315", "316", "373", "701", "275", "361", "345", "334", "335", "311", "369"],
    },
    {
        "code": "HP4",
        "category": "Horoscope Calculations & Interpretations",
        "title": "Horoscope Calculations & Interpretations — Grand Encyclopedia (HP4)",
        "estimated_pages": 125,
        "description": "Includes every chapter of HP3 plus all 22 Dasha Systems, Astronomical Planetary Profiles (Sun to Pluto), and Rectification/Relocation sensitivity tables.",
        "chapter_ids": ["200", "201", "314", "202", "203", "204", "300", "337", "304", "302", "303", "395", "305", "307", "306", "312", "310", "333", "330", "332", "338", "346", "350", "205", "207", "216", "802", "803", "804", "805", "806", "807", "808", "251", "392", "393", "386", "387", "388", "389", "390", "391", "397", "398", "315", "316", "373", "701", "275", "361", "345", "363", "369", "334", "335", "311", "394", "820"],
    },
    {
        "code": "KP1",
        "category": "KP Stellar Paddhati (KP)",
        "title": "KP Stellar Paddhati — Essential (KP1)",
        "estimated_pages": 8,
        "description": "KP Nirayana Bhava Chalit cusps, Star Lord / Sub Lord / Sub-Sub Lord table, 4-Step Planet & House Significators, Ruling Planets, and Vimshottari Dasha/Sub-Dasha tables.",
        "chapter_ids": ["314", "334", "335", "307", "315", "376", "373"],
    },
    {
        "code": "KP2",
        "category": "KP Stellar Paddhati (KP)",
        "title": "KP Stellar Paddhati — Complete Special (KP2)",
        "estimated_pages": 25,
        "description": "Complete KP dossier with Nirayana Cusps, 4-Fold Significators, Vargas, Panchadha Maitri, Shadbala, Aspects, Avasthas, Ashtakavarga, Sookshma Dashas, and Annual Varshaphala.",
        "chapter_ids": ["314", "300", "334", "335", "304", "302", "303", "305", "307", "306", "312", "310", "333", "330", "332", "315", "325", "373", "401", "402", "404"],
    },
    {
        "code": "VC1",
        "category": "Varshaphala (Annual Solar Return)",
        "title": "Varshaphala Calculations — Concise (VC1)",
        "estimated_pages": 6,
        "description": "Tajika Solar Return Basic Details, Muntha, Varsheshwara (Year Lord), Panchavargiya Bala, Dwadasavargiya Bala, Harsha Bala, and Annual Mudda Dasha.",
        "chapter_ids": ["401", "402", "403", "404", "410", "415", "373"],
    },
    {
        "code": "VC2",
        "category": "Varshaphala (Annual Solar Return)",
        "title": "Varshaphala Calculations — Detailed (VC2)",
        "estimated_pages": 25,
        "description": "Includes VC1 plus Tripataki Chakra, 36 Tajika Sahams (Sensitive Arabic Lots), 16 Tajika Yogas (Ithasala, Ishrafa, Nakta, Yamaya, Kamboola, etc.), and Multi-Year / Masaphala Monthly Charts.",
        "chapter_ids": ["401", "402", "403", "404", "406", "407", "405", "408", "409", "410", "415", "339", "425"],
    },
    {
        "code": "VP1",
        "category": "Varshaphala (Annual Solar Return)",
        "title": "Varshaphala Calculations & Interpretations — Standard (VP1)",
        "estimated_pages": 14,
        "description": "Includes VC1 plus Annual Chart Interpretations (Varsheshwara Year Lord, Muntha in Bhava, Munthesh Lord) and Mudda Dasha Period Predictions.",
        "chapter_ids": ["401", "402", "403", "404", "410", "415", "422", "423"],
    },
    {
        "code": "VP2",
        "category": "Varshaphala (Annual Solar Return)",
        "title": "Varshaphala Calculations & Interpretations — Complete (VP2)",
        "estimated_pages": 32,
        "description": "Complete Annual Solar Return Dossier: VC2 + Annual Varsheshwara/Muntha/Lord Interpretations + Annual Mudda Dasha Predictions + Tajika Sahams + Tripataki Chakra.",
        "chapter_ids": ["401", "402", "403", "404", "406", "407", "405", "408", "409", "410", "415", "422", "423", "339", "425"],
    },
    {
        "code": "HM1",
        "category": "Compatibility & Horoscope Matching",
        "title": "Horoscope Compatibility — Standard (HM1)",
        "estimated_pages": 6,
        "description": "Partner Birth Details, Dual Rashi/Moon/Navamsha Charts, 36-Point Ashtakoota Guna Milan Table, and Dual Mangala Dosha Consideration.",
        "chapter_ids": ["500", "501", "502", "503", "504", "505"],
    },
    {
        "code": "HM2",
        "category": "Compatibility & Horoscope Matching",
        "title": "Horoscope Compatibility — Complete North & South Indian (HM2)",
        "estimated_pages": 12,
        "description": "Includes HM1 plus Classical Mangala Dosha Cancellation Rules, South Indian 10-Porutham (Dashakoota) Matching Table, Koota-by-Koota Narrative, and Synastry Compatibility Report.",
        "chapter_ids": ["500", "501", "502", "503", "504", "505", "506", "507", "508"],
    },
    {
        "code": "PH1",
        "category": "Pocket Dossiers",
        "title": "Pocket Horoscope — Essential (PH1)",
        "estimated_pages": 12,
        "description": "Compact 12-section summary covering Birth Panchanga, Rashi/Navamsha, Lucky Points, Active Dashas, and Key Remedies.",
        "chapter_ids": ["200", "201", "314", "204", "300", "304", "315", "397", "701"],
    },
    {
        "code": "PH2",
        "category": "Pocket Dossiers",
        "title": "Pocket Horoscope — Extended (PH2)",
        "estimated_pages": 20,
        "description": "Extended 20-section pocket reference with Graha Phala highlights, Yogas, Sadhesati, Gemstones, and 10-Year Dashas.",
        "chapter_ids": ["200", "201", "314", "202", "204", "300", "304", "207", "806", "386", "392", "397", "315", "701"],
    },
    {
        "code": "PV",
        "category": "Pocket Dossiers",
        "title": "Pocket Varshaphala (PV)",
        "estimated_pages": 10,
        "description": "Compact Annual Solar Return summary with Muntha, Year Lord, Sahams, and Mudda Dasha predictions.",
        "chapter_ids": ["401", "402", "404", "407", "410", "422", "423"],
    },
    {
        "code": "MASTER_COMPLETE",
        "category": "Complete Master Compendium",
        "title": "PanchangHub Master Compendium — All 9 Menus, 22 Dashas & Complete Treatise",
        "estimated_pages": 140,
        "description": "Unabridged synthesis of every calculation, chart, Upagraha, Sphuta, Avastha, Maitri, Shadbala, Ashtakavarga, Graha Phala, Bhavesh Phala, Classics in English, Categorized Yogas, 22 Dashas, Varshaphala, Saturn Cycles, Gemstones, and Rectification/Relocation.",
        "chapter_ids": [
            "200", "201", "314", "202", "203", "204", "300", "337", "304", "302", "303", "395",
            "305", "307", "306", "312", "310", "333", "330", "332", "338", "346", "350", "205",
            "207", "216", "802", "803", "804", "805", "806", "807", "808", "251", "392", "393",
            "386", "387", "388", "389", "390", "391", "397", "398", "315", "316", "373", "701",
            "275", "361", "345", "363", "369", "334", "335", "311", "401", "402", "404", "406",
            "407", "405", "410", "422", "423", "394", "820", "900",
        ],
    },
]

MENUS_AND_SUBMENUS_CATALOG: List[Dict[str, Any]] = [
    {
        "menu_id": "menu_1_charts",
        "menu_number": 1,
        "title": "1. Charts & Divisional Vargas",
        "icon": "auto_awesome_mosaic",
        "submenus": [
            {"id": "300", "title": "1.1 Birth Chart (Rashi D-1) & Planetary Positions"},
            {"id": "337", "title": "1.2 11 Upagrahas (Sub-Planets) & 15 Mathematical Sphutas"},
            {"id": "304", "title": "1.3 Chandra (Moon), Navamsha (D-9) & Sripati Bhava Chalit"},
            {"id": "302", "title": "1.4 Shodashavarga Divisional Charts Suite I (D-1 to D-12)"},
            {"id": "303", "title": "1.5 Shodashavarga Divisional Charts Suite II (D-16 to D-60)"},
            {"id": "305", "title": "1.6 Sudarshan Chakra (Concentric Lagna, Moon & Sun Wheel)"},
            {"id": "309", "title": "1.7 Padanadhamsa & Karakamsha Chart"},
            {"id": "311", "title": "1.8 Jaimini System: 7 Chara Karakas, Arudha Padas (A1–A12) & Upapada"},
        ],
    },
    {
        "menu_id": "menu_2_calculations",
        "menu_number": 2,
        "title": "2. Mathematical Calculations & Bala",
        "icon": "calculate",
        "submenus": [
            {"id": "314", "title": "2.1 Basic Birth Calculations, Panchanga, 17-Item Avakhada & 8-Item Ghata Chakra"},
            {"id": "306", "title": "2.2 Panchadha Maitri Chakra (Natural, Temporal & 5-Fold Compound Friendship)"},
            {"id": "307", "title": "2.3 Shodashavarga Summary, Vaisheshikamsa Dignities & Vimshopaka Bala"},
            {"id": "312", "title": "2.4 Complete Six-Fold Shadbala, Ishta/Kashta Phala & 12-House Bhava Bala"},
            {"id": "310", "title": "2.5 Parashari Graha Sputa Drishti & Jaimini Rashi Drishti Aspects"},
            {"id": "333", "title": "2.6 4-System Planetary Avasthas (Jagradadi, Baladi, Deeptadi, Lajjitadi & Shayanadi)"},
            {"id": "330", "title": "2.7 Ashtakavarga Suite (7 Bhinnashtakavarga, Sarvashtakavarga, Trikona & Ekadhipatya Reductions, Rashi/Graha/Shodya Pindas)"},
            {"id": "350", "title": "2.8 Ayurvedic Tridosha, Dhatu & Drekkana Body-Part Physiology"},
            {"id": "334", "title": "2.9 KP Stellar Paddhati (KP) Cusps, Sub-Lords & 4-Fold Significators"},
        ],
    },
    {
        "menu_id": "menu_3_interpretations",
        "menu_number": 3,
        "title": "3. Detailed Text Interpretations",
        "icon": "menu_book",
        "submenus": [
            {"id": "200", "title": "3.1 Introduction, Panchanga & Birth Ascendant (Lagna) Treatise"},
            {"id": "202", "title": "3.2 Nature, Temperament, Shastric vs Modern Physical Appearance & Lucky Points"},
            {"id": "205", "title": "3.3 Birth Nakshatra & Exact Pada Deep Dive"},
            {"id": "207", "title": "3.4 9-Planet Dispositions Treatise — Graha Phala (Sun through Ketu)"},
            {"id": "216", "title": "3.5 12 House Lords Treatise — Bhavesh Phala (1st Lord through 12th Lord)"},
            {"id": "802", "title": "3.6 Classics in English: 12 Houses, Planetary Yogas, Jaimini Sutras & Curses/Remedies"},
            {"id": "806", "title": "3.7 Categorized Classical Yogas (Benefic, Malefic & Mixed Yogas with Rules)"},
            {"id": "251", "title": "3.8 Lifetime Thematic Synthesis (Personality, Wealth, Career, Marriage, Longevity)"},
            {"id": "701", "title": "3.9 Multi-Year Vimshottari Mahadasha & Antardasha Dated Predictions"},
            {"id": "275", "title": "3.10 Gochara Transit Interpretations & Vedha Obstruction Analysis"},
        ],
    },
    {
        "menu_id": "menu_4_dashas",
        "menu_number": 4,
        "title": "4. All 22 Dasha Systems",
        "icon": "schedule",
        "submenus": [
            {"id": "315", "title": "4.1 Vimshottari Dasha (120y) — 5-Level Mahadasha to Prana Dasha"},
            {"id": "345", "title": "4.2 Ashtottari Dasha (108y) — 8-Planet System"},
            {"id": "361", "title": "4.3 Yogini Dasha (36y) — 8-Yogini Tantric System"},
            {"id": "363", "title": "4.4 Kalachakra Dasha — Savya/Apasavya Navamsha Wheel"},
            {"id": "365", "title": "4.5 Tribhagi (80y) & Tribhagi-40 (40y) Dashas"},
            {"id": "369", "title": "4.6 8 Jaimini & Rashi Dashas (Chara, Sthira, Narayana, Shoola, Niryaana Shoola, Drig, Navamsha, Lagna Kendradi)"},
            {"id": "378", "title": "4.7 8 Conditional BPHS Nakshatra Dashas (Shodashottari 116y, Dwadashottari 112y, Panchottari 105y, Shatabdika 100y, Chaturshitisama 84y, Dwisaptatisama 72y, Shashtihayani 60y, Shattrimshatsama 36y)"},
        ],
    },
    {
        "menu_id": "menu_5_varshaphala",
        "menu_number": 5,
        "title": "5. Varshaphala (Annual Solar Return)",
        "icon": "wb_sunny",
        "submenus": [
            {"id": "401", "title": "5.1 Annual Solar Return Chart, Muntha & Varsheshwara (5-Officer Year Lord)"},
            {"id": "404", "title": "5.2 Panchavargiya Bala, Dwadasavargiya Bala & Harsha Bala"},
            {"id": "406", "title": "5.3 Tripataki Chakra (3-Banner Annual Progression Index)"},
            {"id": "407", "title": "5.4 36 Tajika Sahams (Punya, Vidya, Yashas, Mitra, Vivaha, Karya, Kali, etc.)"},
            {"id": "405", "title": "5.5 16 Tajika Yogas (Ikkavala, Induvara, Ithasala, Ishrafa, Nakta, Yamaya, Kamboola, etc.)"},
            {"id": "408", "title": "5.6 Annual Mudda (Vimshottari) & Patyayini Dashas"},
            {"id": "422", "title": "5.7 Detailed Annual Chart & Dasha Narrative Interpretations"},
        ],
    },
    {
        "menu_id": "menu_6_compatibility",
        "menu_number": 6,
        "title": "6. Compatibility & Horoscope Matching",
        "icon": "favorite",
        "submenus": [
            {"id": "500", "title": "6.1 Dual Partner Birth Charts, Moon Charts & Navamshas"},
            {"id": "503", "title": "6.2 36-Point Ashtakoota Guna Milan Table (Varna to Nadi)"},
            {"id": "504", "title": "6.3 Dual Mangala Dosha Consideration & 12 Cancellation Rules"},
            {"id": "507", "title": "6.4 South Indian 10-Porutham (Dashakoota) Matching Table"},
            {"id": "508", "title": "6.5 Comprehensive Koota-by-Koota & Synastry Compatibility Report"},
        ],
    },
    {
        "menu_id": "menu_7_astronomy",
        "menu_number": 7,
        "title": "7. Astronomical Details & Profiles",
        "icon": "public",
        "submenus": [
            {"id": "394", "title": "7.1 Heliocentric & Geocentric Astronomical Coordinates, Velocities & Latitudes"},
            {"id": "820", "title": "7.2 Physical & Astronomical Profiles of the Solar System (Sun to Pluto)"},
        ],
    },
    {
        "menu_id": "menu_8_remedies",
        "menu_number": 8,
        "title": "8. Saturn Cycles, Mangala Dosha & Gemstones",
        "icon": "diamond",
        "submenus": [
            {"id": "386", "title": "8.1 Saturn Sadhesati (3 Lifetime Cycles: Rising, Peak, Setting) & Paya Metal"},
            {"id": "388", "title": "8.2 Laghu Kalyani Dhayya (4th & 8th from Moon), Kantaka Saturn & Classical Remedies"},
            {"id": "392", "title": "8.3 Mangala (Kuja) Dosha Analysis from Lagna, Moon & Venus + Propitiation"},
            {"id": "397", "title": "8.4 Gemstone Recommendations I & II (Life Stone, Lucky Stone, Destiny Stone & Wearing Protocol)"},
        ],
    },
    {
        "menu_id": "menu_9_tools",
        "menu_number": 9,
        "title": "9. Rectification, Relocation & Research Tools",
        "icon": "build_circle",
        "submenus": [
            {"id": "901", "title": "9.1 Change Time / Birth Time Rectifier (Exact Lagna, D-9, D-10, D-60, Pranapada & Kunda Shift Boundaries)"},
            {"id": "902", "title": "9.2 Change Location / Astro-Relocation Tool (Relocated Ascendant, Cusps & House Shifts)"},
            {"id": "903", "title": "9.3 Special Point & Sphuta Calculator (Yogi, Avayogi, Sahayogi, Beeja, Kshetra, Trisphuta, Bhrigu Bindu)"},
            {"id": "904", "title": "9.4 Panch Pakshi (5-Bird Bio-Rhythm System), Navamsha Ages & SPICA Steps 1A–5 Worksheet"},
        ],
    },
]

WORKSHEETS_PRESETS_CATALOG: List[Dict[str, str]] = [
    {"id": "ws_600", "title": "Standard Parashari Dual View (Rashi D-1, Navamsha D-9, Vimshottari & Planetary Table)"},
    {"id": "ws_604", "title": "Ashtakavarga Master Worksheet (BAV, SAV, Shodya Pindas & Transit Bindus)"},
    {"id": "ws_609", "title": "Nakshatra & Avakhada Diagnostic Worksheet (27-Star Tarabala & Ghata Chakra)"},
    {"id": "ws_614", "title": "Shodashavarga 16-Chart Comparative Grid"},
    {"id": "ws_618", "title": "Shadbala, Bhava Bala & Panchadha Maitri Strength Matrix"},
    {"id": "ws_625", "title": "KP Stellar Paddhati (KP) 4-Step Significator & Ruling Planets Desk"},
    {"id": "ws_632", "title": "Jaimini Sutras Desk (Chara Karakas, Karakamsha, Arudha Padas A1–A12 & Chara Dasha)"},
    {"id": "ws_640", "title": "Varshaphala Tajika Desk (Annual Return, Muntha, 36 Sahams, 16 Tajika Yogas & Mudda Dasha)"},
    {"id": "ws_648", "title": "Upagrahas & 15 Sphutas Research Desk (Mandi, Gulika, Yogi/Avayogi, Beeja/Kshetra, Bhrigu Bindu)"},
    {"id": "ws_655", "title": "SPICA Auspiciousness & Rectification Desk (Steps 1A–5, Pranapada, Kunda & Navamsha Ages)"},
]


def get_reports_and_menus_catalog() -> Dict[str, Any]:
    return {
        "schema_version": "2026.10.27",
        "engine": "PanchangHub Detailed Reports & Complete 9-Menu Engine",
        "report_models_count": len(REPORT_MODELS_CATALOG),
        "report_models": REPORT_MODELS_CATALOG,
        "menus_count": len(MENUS_AND_SUBMENUS_CATALOG),
        "menus": MENUS_AND_SUBMENUS_CATALOG,
        "worksheet_presets": WORKSHEETS_PRESETS_CATALOG,
    }


# ==============================================================================
# 2. AVAKHADA CHAKRA (17 ITEMS) & GHATA CHAKRA (8 ITEMS) + 108 NAAMAKSHARAS
# ==============================================================================

# All 108 Nakshatra Pada syllables (27 Nakshatras x 4 Padas) per classical Avakhada Chakra
NAKSHATRA_PADA_SYLLABLES: List[List[str]] = [
    ["Chu", "Che", "Cho", "La"],      # 1. Ashwini
    ["Li", "Lu", "Le", "Lo"],         # 2. Bharani
    ["A", "Ee", "U", "Ea"],           # 3. Krittika
    ["O", "Va", "Vi", "Vu"],          # 4. Rohini
    ["Ve", "Vo", "Ka", "Ki"],         # 5. Mrigashira
    ["Ku", "Gha", "Ng", "Chha"],      # 6. Ardra
    ["Ke", "Ko", "Ha", "Hi"],         # 7. Punarvasu
    ["Hu", "He", "Ho", "Da"],         # 8. Pushya
    ["Di", "Du", "De", "Do"],         # 9. Ashlesha
    ["Ma", "Mi", "Mu", "Me"],         # 10. Magha
    ["Mo", "Ta", "Ti", "Tu"],         # 11. Purva Phalguni
    ["Te", "To", "Pa", "Pi"],         # 12. Uttara Phalguni
    ["Pu", "Sha", "Na", "Tha"],       # 13. Hasta
    ["Pe", "Po", "Ra", "Ri"],         # 14. Chitra
    ["Ru", "Re", "Ro", "Ta"],         # 15. Swati
    ["Ti", "Tu", "Te", "To"],         # 16. Vishakha
    ["Na", "Ni", "Nu", "Ne"],         # 17. Anuradha
    ["No", "Ya", "Yi", "Yu"],         # 18. Jyeshtha
    ["Ye", "Yo", "Bha", "Bhi"],       # 19. Moola
    ["Bhu", "Dha", "Pha", "Dha"],     # 20. Purva Ashadha
    ["Bhe", "Bho", "Ja", "Ji"],       # 21. Uttara Ashadha
    ["Ju", "Je", "Jo", "Gha"],        # 22. Shravana
    ["Ga", "Gi", "Gu", "Ge"],         # 23. Dhanishta
    ["Go", "Sa", "Si", "Su"],         # 24. Shatabhisha
    ["Se", "So", "Da", "Di"],         # 25. Purva Bhadrapada
    ["Du", "Tha", "Jha", "Da"],       # 26. Uttara Bhadrapada
    ["De", "Do", "Cha", "Chi"],       # 27. Revati
]

NAKSHATRA_DEITIES: List[str] = [
    "Ashwini Kumaras (Celestial Physicians)", "Yama (Lord of Dharma)", "Agni (Sacred Fire)",
    "Prajapati / Brahma (Creator)", "Soma (Chandra, Immortal Nectar)", "Rudra (Lord of Storms & Transformation)",
    "Aditi (Mother of Gods)", "Brihaspati (Sacred Wisdom)", "Nagas (Serpent Deities)",
    "Pitris (Ancestral Forefathers)", "Bhaga (Marital Bliss & Prosperity)", "Aryaman (Contracts & Patronage)",
    "Savitar (Creative Solar Force)", "Tvashtar / Vishwakarma (Celestial Architect)", "Vayu (Cosmic Life Wind)",
    "Indra-Agni (Sovereign Triumph)", "Mitra (Sacred Friendship & Covenant)", "Indra (King of Devas)",
    "Nirriti (Root Dissolution & Liberation)", "Apah (Cosmic Waters)", "Vishvadevas (Universal Deities)",
    "Vishnu (Preserver of Cosmos)", "Ashta Vasus (Eight Elemental Deities)", "Varuna (Cosmic Law & Healing)",
    "Aja Ekapada (One-Footed Cosmic Fire)", "Ahirbudhnya (Serpent of the Deep)", "Pushan (Nourisher & Safe Journeys)",
]

# Ghata Chakra complete 8-element table indexed by Janma Rashi (0=Aries..11=Pisces)
GHATA_COMPLETE_TABLE: List[Dict[str, str]] = [
    {"rashi": "Mesha (Aries)", "masa": "Kartika", "tithi": "1, 6, 11 (Nanda)", "vara": "Sunday", "nakshatra": "Magha", "yoga": "Vishkambha", "karana": "Bava", "prahara": "1st Prahara", "lagna": "Mesha (Aries)", "same_sex_moon": "Simha (Leo)", "opp_sex_moon": "Vrishabha (Taurus)"},
    {"rashi": "Vrishabha (Taurus)", "masa": "Margashirsha", "tithi": "5, 10, 15 (Purna)", "vara": "Saturday", "nakshatra": "Hasta", "yoga": "Atiganda", "karana": "Shakuni", "prahara": "4th Prahara", "lagna": "Vrishabha (Taurus)", "same_sex_moon": "Kanya (Virgo)", "opp_sex_moon": "Mithuna (Gemini)"},
    {"rashi": "Mithuna (Gemini)", "masa": "Ashadha", "tithi": "2, 7, 12 (Bhadra)", "vara": "Monday", "nakshatra": "Swati", "yoga": "Parigha", "karana": "Kaulava", "prahara": "3rd Prahara", "lagna": "Karka (Cancer)", "same_sex_moon": "Kumbha (Aquarius)", "opp_sex_moon": "Meena (Pisces)"},
    {"rashi": "Karka (Cancer)", "masa": "Pausha", "tithi": "2, 7, 12 (Bhadra)", "vara": "Wednesday", "nakshatra": "Anuradha", "yoga": "Shoola", "karana": "Nagava", "prahara": "1st Prahara", "lagna": "Tula (Libra)", "same_sex_moon": "Simha (Leo)", "opp_sex_moon": "Kanya (Virgo)"},
    {"rashi": "Simha (Leo)", "masa": "Jyeshtha", "tithi": "3, 8, 13 (Jaya)", "vara": "Saturday", "nakshatra": "Moola", "yoga": "Ganda", "karana": "Taitila", "prahara": "1st Prahara", "lagna": "Makara (Capricorn)", "same_sex_moon": "Karka (Cancer)", "opp_sex_moon": "Makara (Capricorn)"},
    {"rashi": "Kanya (Virgo)", "masa": "Bhadrapada", "tithi": "5, 10, 15 (Purna)", "vara": "Saturday", "nakshatra": "Shravana", "yoga": "Vyatipata", "karana": "Gara", "prahara": "1st Prahara", "lagna": "Meena (Pisces)", "same_sex_moon": "Vrishabha (Taurus)", "opp_sex_moon": "Mithuna (Gemini)"},
    {"rashi": "Tula (Libra)", "masa": "Magha", "tithi": "4, 9, 14 (Rikta)", "vara": "Thursday", "nakshatra": "Shatabhisha", "yoga": "Vajra", "karana": "Vanija", "prahara": "4th Prahara", "lagna": "Kanya (Virgo)", "same_sex_moon": "Dhanu (Sagittarius)", "opp_sex_moon": "Dhanu (Sagittarius)"},
    {"rashi": "Vrishchika (Scorpio)", "masa": "Ashvina", "tithi": "1, 6, 11 (Nanda)", "vara": "Friday", "nakshatra": "Revati", "yoga": "Vyaghata", "karana": "Vishti (Bhadra)", "prahara": "1st Prahara", "lagna": "Vrishchika (Scorpio)", "same_sex_moon": "Kanya (Virgo)", "opp_sex_moon": "Dhanu (Sagittarius)"},
    {"rashi": "Dhanu (Sagittarius)", "masa": "Shravana", "tithi": "3, 8, 13 (Jaya)", "vara": "Friday", "nakshatra": "Uttara Phalguni", "yoga": "Harshana", "karana": "Balava", "prahara": "1st Prahara", "lagna": "Dhanu (Sagittarius)", "same_sex_moon": "Meena (Pisces)", "opp_sex_moon": "Mithuna (Gemini)"},
    {"rashi": "Makara (Capricorn)", "masa": "Vaishakha", "tithi": "4, 9, 14 (Rikta)", "vara": "Tuesday", "nakshatra": "Rohini", "yoga": "Dhriti", "karana": "Chatushpada", "prahara": "4th Prahara", "lagna": "Kumbha (Aquarius)", "same_sex_moon": "Simha (Leo)", "opp_sex_moon": "Vrishchika (Scorpio)"},
    {"rashi": "Kumbha (Aquarius)", "masa": "Chaitra", "tithi": "3, 8, 13 (Jaya)", "vara": "Thursday", "nakshatra": "Ardra", "yoga": "Shoola", "karana": "Kinstughna", "prahara": "3rd Prahara", "lagna": "Mithuna (Gemini)", "same_sex_moon": "Mithuna (Gemini)", "opp_sex_moon": "Simha (Leo)"},
    {"rashi": "Meena (Pisces)", "masa": "Phalguna", "tithi": "5, 10, 15 (Purna)", "vara": "Friday", "nakshatra": "Ashlesha", "yoga": "Ganda", "karana": "Bava", "prahara": "4th Prahara", "lagna": "Simha (Leo)", "same_sex_moon": "Kumbha (Aquarius)", "opp_sex_moon": "Tula (Libra)"},
]


def compute_avakhada_and_ghata_chakra(
    pos: Dict[str, Any], asc_lon: float, birth_jd: float, lat: float, lon: float, tz: Any
) -> Dict[str, Any]:
    moon_lon = pos["Moon"]["longitude"]
    sun_lon = pos["Sun"]["longitude"]
    moon_sign = int(moon_lon // 30) % 12
    asc_sign = int(asc_lon // 30) % 12
    ni, pada = nakshatra_of(moon_lon)

    base_ava = _adv_core.avakahada(moon_lon, sun_lon, asc_lon)
    syllable = NAKSHATRA_PADA_SYLLABLES[ni][pada - 1]
    all_nak_syllables = ", ".join(NAKSHATRA_PADA_SYLLABLES[ni])

    # Rashi Paya (Gold, Silver, Copper, Iron) by Moon's house from Lagna
    moon_house_from_lagna = (moon_sign - asc_sign) % 12 + 1
    if moon_house_from_lagna in (1, 6, 11):
        rashi_paya = "Swarna (Gold Paya)"
    elif moon_house_from_lagna in (2, 5, 9):
        rashi_paya = "Rajata (Silver Paya)"
    elif moon_house_from_lagna in (3, 7, 10):
        rashi_paya = "Tamra (Copper Paya)"
    else:
        rashi_paya = "Loha (Iron Paya)"

    # Nakshatra Paya
    if ni in (0, 14, 21):
        nak_paya = "Swarna (Gold)"
    elif ni in (5, 6, 7, 8, 9, 10, 11, 12, 13):
        nak_paya = "Rajata (Silver)"
    elif ni in (15, 16, 17, 18, 19, 20, 22, 23, 24):
        nak_paya = "Tamra (Copper)"
    else:
        nak_paya = "Loha (Iron)"

    # Local Mean Time & Ishtakaal
    local_dt = local_from_jd(birth_jd, tz)
    std_offset_hours = (local_dt.utcoffset().total_seconds() / 3600.0) if local_dt.utcoffset() else 0.0
    std_meridian = std_offset_hours * 15.0
    lmt_correction_minutes = round((lon - std_meridian) * 4.0, 2)

    avakhada_17 = {
        "paya_rashi": rashi_paya,
        "paya_nakshatra": nak_paya,
        "varna": base_ava["varna"],
        "vashya": base_ava["vashya"],
        "yoni": base_ava["yoni"],
        "gana": base_ava["gana"],
        "nadi": base_ava["nadi"],
        "rashi": f"{RASHIS[moon_sign]} ({SIGNS[moon_sign]})",
        "rashi_lord": SIGN_LORDS[moon_sign],
        "nakshatra": NAKSHATRAS[ni],
        "nakshatra_pada": pada,
        "nakshatra_lord": NAK_LORDS[ni % 9],
        "nakshatra_deity": NAKSHATRA_DEITIES[ni],
        "naamakshara_pada_syllable": syllable,
        "nakshatra_all_syllables": all_nak_syllables,
        "tatva_element": base_ava["tatva"],
        "sun_sign_western": SIGNS[int((sun_lon + ayanamsa(birth_jd)) % 360 // 30)],
        "sun_sign_vedic": f"{RASHIS[int(sun_lon // 30)]} ({SIGNS[int(sun_lon // 30)]})",
        "lagna_sign": f"{RASHIS[asc_sign]} ({SIGNS[asc_sign]})",
        "lagna_lord": SIGN_LORDS[asc_sign],
        "ayanamsa_deg": round(ayanamsa(birth_jd), 6),
        "ayanamsa_dms": dms(ayanamsa(birth_jd)),
        "lmt_correction_minutes": lmt_correction_minutes,
    }

    ghata = GHATA_COMPLETE_TABLE[moon_sign]
    return {
        "avakhada_chakra": avakhada_17,
        "ghata_chakra": ghata,
        "guidance_note": (
            f"Born in {NAKSHATRAS[ni]} Pada {pada}, your classical Naamakshara (auspicious name syllable) is '{syllable}'. "
            f"Avoid initiating major ventures or surgery when the transiting Moon occupies {ghata['rashi']} on {ghata['vara']} "
            f"or during {ghata['tithi']} Tithi and {ghata['nakshatra']} Nakshatra."
        ),
    }


# ==============================================================================
# 3. 11 UPAGRAHAS, 15 SPHUTAS, 4 AVASTHA SYSTEMS & PANCHADHA MAITRI CHAKRA
# ==============================================================================

BALADI_ODD = ["Bala (Infant)", "Kumara (Youth)", "Yuva (Adult — Full Power)", "Vriddha (Old)", "Mrita (Inert)"]
BALADI_EVEN = list(reversed(BALADI_ODD))

SHAYANADI_12 = [
    ("Shayana", "Resting / Lying Down", "Reflective start; results mature after initial contemplation."),
    ("Upaveshana", "Sitting at Seat", "Steady command, administrative stability, and grounded authority."),
    ("Netrapani", "Hand on Eyes / Watchful", "High vigilance, foresight, artistic or diplomatic discernment."),
    ("Prakashana", "Shining / Illuminating", "Public recognition, eloquence, and visible achievements."),
    ("Gamana", "Moving / Travelling", "Dynamic mobility, expansion across regions, enterprise."),
    ("Agamana", "Returning / Consolidating", "Harvesting gains, returning to roots, asset consolidation."),
    ("Sabha", "In Royal Assembly", "Leadership in councils, advisory prestige, honors among peers."),
    ("Agama", "Acquiring Knowledge & Wealth", "Inflow of resources, scholarly mastery, institutional growth."),
    ("Bhojana", "Nourishing / Enjoyment", "Material comfort, culinary refinement, sensory fulfillment."),
    ("Nrityalipsa", "Creative / Artistic Zeal", "Rhythmic creativity, cultural patronage, magnetic charm."),
    ("Kautuka", "Curious / Celebratory", "Innovation, joyous auspicious events, scientific curiosity."),
    ("Nidra", "Deep Slumber / Introspection", "Mystical inward turn; requires conscious activation of the planet's house."),
]


def compute_upagrahas_sphutas_avasthas_maitri(
    pos: Dict[str, Any], asc_lon: float, birth_jd: float, lat: float, lon: float
) -> Dict[str, Any]:
    sun_lon = pos["Sun"]["longitude"]
    moon_lon = pos["Moon"]["longitude"]
    mars_lon = pos["Mars"]["longitude"]
    merc_lon = pos["Mercury"]["longitude"]
    jup_lon = pos["Jupiter"]["longitude"]
    ven_lon = pos["Venus"]["longitude"]
    sat_lon = pos["Saturn"]["longitude"]
    rahu_lon = pos["Rahu"]["longitude"]
    asc_sign = int(asc_lon // 30) % 12

    def _fmt_point(name: str, category: str, deg_val: float, formula: str, signification: str) -> Dict[str, Any]:
        L = norm(deg_val)
        s = int(L // 30) % 12
        ni, pada = nakshatra_of(L)
        return {
            "name": name,
            "category": category,
            "longitude": round(L, 6),
            "sign": SIGNS[s],
            "rashi": RASHIS[s],
            "degree_in_sign": round(L % 30, 4),
            "dms": dms(L % 30),
            "house": (s - asc_sign) % 12 + 1,
            "sign_lord": SIGN_LORDS[s],
            "nakshatra": NAKSHATRAS[ni],
            "pada": pada,
            "nakshatra_lord": NAK_LORDS[ni % 9],
            "navamsha_sign": SIGNS[varga_sign(L, 9)],
            "formula": formula,
            "signification": signification,
        }

    # --- A. 5 Aprakashika Upagrahas (Solar Non-Luminous Sub-Planets, BPHS Ch. 3) ---
    dhuma_lon = norm(sun_lon + 133.0 + 20.0 / 60.0)
    vyatipata_lon = norm(360.0 - dhuma_lon)
    parivesha_lon = norm(vyatipata_lon + 180.0)
    indrachapa_lon = norm(360.0 - parivesha_lon)
    upaketu_lon = norm(indrachapa_lon + 16.0 + 40.0 / 60.0)

    # --- B. 6 Kalavela Upagrahas (Planetary Portion Sub-Planets) ---
    # Using classic diurnal/nocturnal 8-fold planetary portion offsets from Lagna/Sun
    weekday = int((birth_jd + 1.5) % 7)  # 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
    # Saturn's portion (Gulika), Mandi, Sun's portion (Kala), Mars's portion (Mrityu),
    # Mercury's portion (Ardhaprahara), Jupiter's portion (Yamaghantaka)
    sat_portion_idx = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}[weekday]
    sun_portion_idx = {0: 0, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}[weekday]
    mars_portion_idx = {0: 2, 1: 1, 2: 0, 3: 6, 4: 5, 5: 4, 6: 3}[weekday]
    merc_portion_idx = {0: 3, 1: 2, 2: 1, 3: 0, 4: 6, 5: 5, 6: 4}[weekday]
    jup_portion_idx = {0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 6, 6: 5}[weekday]

    gulika_lon = norm(asc_lon + sat_portion_idx * 22.5)
    mandi_lon = norm(gulika_lon + 3.75)
    kala_lon = norm(asc_lon + sun_portion_idx * 22.5)
    mrityu_upagraha_lon = norm(asc_lon + mars_portion_idx * 22.5)
    ardhaprahara_lon = norm(asc_lon + merc_portion_idx * 22.5)
    yamaghantaka_lon = norm(asc_lon + jup_portion_idx * 22.5)

    upagrahas = [
        _fmt_point("Dhuma", "Aprakashika (Solar)", dhuma_lon, "Sun + 133°20'", "Thermal drive, intense ambition, and smoke-screen obstacles when afflicted."),
        _fmt_point("Vyatipata", "Aprakashika (Solar)", vyatipata_lon, "360° - Dhuma", "Sudden reversals, karmic crossroads, and transformative breakthroughs."),
        _fmt_point("Parivesha", "Aprakashika (Solar)", parivesha_lon, "Vyatipata + 180°", "Protective halo, diplomatic encirclement, and institutional sanctuary."),
        _fmt_point("Indrachapa (Kodanda)", "Aprakashika (Solar)", indrachapa_lon, "360° - Parivesha", "Bow of Indra; target precision, sudden fortune, and strategic victory."),
        _fmt_point("Upaketu (Sikhi)", "Aprakashika (Solar)", upaketu_lon, "Indrachapa + 16°40'", "Comet point; spiritual detachment, sudden insights, and compressed solar karma."),
        _fmt_point("Gulika", "Kalavela (Saturn Portion)", gulika_lon, "Cusp of Saturn's 1/8th Kalavela", "Karmic debt indicator; demands strict discipline and integrity in its house."),
        _fmt_point("Mandi", "Kalavela (Saturn Son)", mandi_lon, "Mid-cusp of Saturn's Kalavela", "Chronic karmic focus; reveals ancestral obligations and longevity checkpoints."),
        _fmt_point("Kala", "Kalavela (Sun Portion)", kala_lon, "Cusp of Sun's 1/8th Kalavela", "Temporal authority and stern paternal/administrative lessons."),
        _fmt_point("Mrityu (Upagraha)", "Kalavela (Mars Portion)", mrityu_upagraha_lon, "Cusp of Mars's 1/8th Kalavela", "Vitality vulnerability point; warns against haste or conflict in its bhava."),
        _fmt_point("Ardhaprahara", "Kalavela (Mercury Portion)", ardhaprahara_lon, "Cusp of Mercury's 1/8th Kalavela", "Commercial and analytical watch-point; sharpens tactical communication."),
        _fmt_point("Yamaghantaka", "Kalavela (Jupiter Portion)", yamaghantaka_lon, "Cusp of Jupiter's 1/8th Kalavela", "Benefic Kalavela; grants dharmic protection, scholarly grace, and counsel."),
    ]

    # --- C. 15 Mathematical Sphutas (Sensitive Points) ---
    prana_sphuta = norm(asc_lon * 5.0 + mandi_lon)
    deha_sphuta = norm(moon_lon * 8.0 + mandi_lon)
    mrityu_sphuta = norm(sat_lon * 7.0 + mandi_lon)
    trisphuta = norm(asc_lon + moon_lon + gulika_lon)
    chatusphuta = norm(trisphuta + sun_lon)
    panchasphuta = norm(chatusphuta + rahu_lon)
    beeja_sphuta = norm(sun_lon + ven_lon + jup_lon)
    kshetra_sphuta = norm(moon_lon + mars_lon + jup_lon)
    santana_tithi_sphuta = norm((moon_lon - sun_lon) * 5.0 + asc_lon)
    yogi_point = norm(sun_lon + moon_lon + 93.0 + 20.0 / 60.0)
    yogi_ni, _ = nakshatra_of(yogi_point)
    yogi_planet = NAK_LORDS[yogi_ni % 9]
    sahayogi_planet = SIGN_LORDS[int(yogi_point // 30) % 12]
    avayogi_point = norm(yogi_point + 186.0 + 40.0 / 60.0)
    avayogi_ni, _ = nakshatra_of(avayogi_point)
    avayogi_planet = NAK_LORDS[avayogi_ni % 9]
    bhrigu_bindu = norm((rahu_lon + moon_lon) / 2.0)
    fortuna_point = norm(asc_lon + moon_lon - sun_lon)
    kunda_point = norm(asc_lon * 81.0)

    sphutas = [
        _fmt_point("Prana Sphuta", "Vitality Trilogy", prana_sphuta, "(5 × Lagna) + Mandi", "Vital life-breath sensitivity; transits of benefics here revitalize prana."),
        _fmt_point("Deha Sphuta", "Vitality Trilogy", deha_sphuta, "(8 × Moon) + Mandi", "Somatic constitution and physical immunity anchor."),
        _fmt_point("Mrityu Sphuta", "Vitality Trilogy", mrityu_sphuta, "(7 × Saturn) + Mandi", "Longevity threshold; malefic transits require health vigilance."),
        _fmt_point("Trisphuta", "Parashari Composite", trisphuta, "Lagna + Moon + Gulika", "Triple confluence of body, mind, and karmic seed."),
        _fmt_point("Chatusphuta", "Parashari Composite", chatusphuta, "Trisphuta + Sun", "Four-fold integration adding the Atman (Soul)."),
        _fmt_point("Panchasphuta", "Parashari Composite", panchasphuta, "Chatusphuta + Rahu", "Five-fold karmic axis integrating past-life evolutionary vector."),
        _fmt_point("Beeja Sphuta", "Progeny & Creativity", beeja_sphuta, "Sun + Venus + Jupiter", "Paternal/creative virility and lineage continuity indicator (strong in odd signs/navamshas)."),
        _fmt_point("Kshetra Sphuta", "Progeny & Receptivity", kshetra_sphuta, "Moon + Mars + Jupiter", "Maternal/generative fertility field (strong in even signs/navamshas)."),
        _fmt_point("Santana Tithi Sphuta", "Progeny & Creativity", santana_tithi_sphuta, "5 × (Moon - Sun) + Lagna", "Lunar-solar progeny timing index."),
        _fmt_point("Yogi Point (Yoga Sphuta)", "Prosperity & Grace", yogi_point, "Sun + Moon + 93°20'", f"Supreme auspiciousness point; Yogi Planet is {yogi_planet}, Sahayogi (Duplicate Yogi) is {sahayogi_planet}."),
        _fmt_point("Avayogi Point", "Obstruction Watch", avayogi_point, "Yogi Point + 186°40'", f"Energy drain point; Avayogi Planet is {avayogi_planet} — guard against overextension in its periods."),
        _fmt_point("Bhrigu Bindu", "Nadi Destiny Axis", bhrigu_bindu, "(Rahu + Moon) / 2", "Karmic destiny trigger; Jupiter or Saturn transiting this degree always produces a milestone life event."),
        _fmt_point("Pars Fortuna (Punya Saham)", "Prosperity & Grace", fortuna_point, "Lagna + Moon - Sun", "Point of material fortune and effortless alignment."),
        _fmt_point("Kunda Lagna (81× Ascendant)", "Birth Time Rectification", kunda_point, "Lagna × 81 (mod 360°)", "Classical rectification point: Kunda sign should ideally be trine or 7th to Janma Nakshatra Rashi."),
    ]

    # --- D. 4-System Planetary Avasthas (Jagradadi, Baladi, Deeptadi, Lajjitadi & Shayanadi) ---
    sign_of = {p: int(pos[p]["longitude"] // 30) % 12 for p in VEDIC_PLANETS}
    house_of = {p: (sign_of[p] - asc_sign) % 12 + 1 for p in VEDIC_PLANETS}
    malefics_in_sign = {}
    for s in range(12):
        malefics_in_sign[s] = [p for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") if sign_of[p] == s]

    avasthas_table = []
    lagna_nav_idx = int(asc_lon // (10.0 / 3.0)) % 108

    for idx_p, p in enumerate(["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]):
        L = pos[p]["longitude"]
        s = sign_of[p]
        deg = L % 30.0
        ni, pada = nakshatra_of(L)
        dig = dignity(p, L)
        retro = pos[p]["speed"] < 0 if p not in ("Rahu", "Ketu") else True
        comb = abs(angdiff(L, sun_lon)) < 12.0 if p not in ("Sun", "Rahu", "Ketu") else False

        # 1. Baladi Avastha (5 age states by 6° slices, reversed in even signs)
        slice_idx = min(4, int(deg // 6.0))
        baladi = (BALADI_ODD if (s % 2 == 0) else BALADI_EVEN)[slice_idx]
        baladi_mult = {"Bala (Infant)": 0.25, "Kumara (Youth)": 0.50, "Yuva (Adult — Full Power)": 1.0, "Vriddha (Old)": 0.125, "Mrita (Inert)": 0.0}[baladi]

        # 2. Jagradadi Avastha (3 consciousness states)
        if dig in ("exalted", "own", "moolatrikona"):
            jagradadi = "Jagrat (Awake — 100% Expression)"
        elif dig in ("friendly", "neutral"):
            jagradadi = "Swapna (Dreaming — 50% Expression)"
        else:
            jagradadi = "Sushupti (Deep Sleep — 25% Expression)"

        # 3. Deeptadi Avastha (9 dignity/environment states)
        if dig == "exalted":
            deeptadi = "Deepta (Blazing / Radiant — Victory & Prestige)"
        elif dig in ("own", "moolatrikona"):
            deeptadi = "Swastha (Comfortable at Home — Stable Prosperity)"
        elif dig == "friendly":
            deeptadi = "Mudita (Delighted in Friend's House — Joy & Support)"
        elif comb:
            deeptadi = "Vikala (Eclipsed by Solar Rays — Needs Inner Focus)"
        elif dig == "debilitated":
            deeptadi = "Deena (Humbled in Debilitation — Builds Resilience)"
        elif dig == "enemy":
            deeptadi = "Dukhita (Distressed in Enemy Sign — Strategic Patience Needed)"
        elif any(m != p for m in malefics_in_sign[s]):
            deeptadi = "Khala (Agitated by Malefic Conjunction — Intense Drive)"
        else:
            deeptadi = "Shanta (Peaceful & Balanced — Steady Constructive Fruits)"

        # 4. Lajjitadi Avastha (6 psychological/relational states, BPHS Ch. 45)
        lajjitadi = "Sthira-Prasanna (Clear & Unafflicted)"
        if house_of[p] == 5 and any(m != p for m in malefics_in_sign[s]):
            lajjitadi = "Lajjita (Modest/Hesitant — in 5th with malefic)"
        elif dig in ("exalted", "moolatrikona"):
            lajjitadi = "Garvita (Proud & Regal — exalted/moolatrikona)"
        elif dig == "enemy" or any(m == "Saturn" and m != p for m in malefics_in_sign[s]):
            lajjitadi = "Kshudhita (Hungry for Transformation — enemy/Saturn link)"
        elif s in (3, 7, 11) and any(m != p for m in malefics_in_sign[s]):
            lajjitadi = "Trishita (Thirsty in Water Sign with malefic)"
        elif sign_of.get("Venus") == s and p != "Venus":
            lajjitadi = "Mudita-Sangama (Joyful with Benefic Venus)"
        elif comb and any(m != p for m in malefics_in_sign[s]):
            lajjitadi = "Kshobhita (Agitated by Sun & Malefic)"

        # 5. Shayanadi Avastha (12 behavioral states, BPHS Ch. 45 formula)
        star_num = ni + 1
        planet_num = idx_p + 1
        nav_num = int((deg // (10.0 / 3.0))) + 1
        shay_idx = ((star_num * planet_num * nav_num) + (ni + 1) + lagna_nav_idx) % 12
        sh_name, sh_meaning, sh_effect = SHAYANADI_12[shay_idx]

        avasthas_table.append({
            "planet": p,
            "sign": SIGNS[s],
            "degree": round(deg, 2),
            "house": house_of[p],
            "dignity": dig,
            "retrograde": retro,
            "combust": comb,
            "baladi_avastha": baladi,
            "baladi_strength_factor": baladi_mult,
            "jagradadi_avastha": jagradadi,
            "deeptadi_avastha": deeptadi,
            "lajjitadi_avastha": lajjitadi,
            "shayanadi_avastha": f"{sh_name} ({sh_meaning})",
            "shayanadi_effect": sh_effect,
        })

    # --- E. Panchadha Maitri Chakra (Naisargika, Tatkalika & 5-Fold Compound Relationship) ---
    seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    naisargika_matrix: Dict[str, Dict[str, str]] = {}
    tatkalika_matrix: Dict[str, Dict[str, str]] = {}
    panchadha_matrix: Dict[str, Dict[str, str]] = {}

    COMPOUND_MAP = {
        ("friend", "friend"): "Adhi Mitra (Intimate / Best Friend)",
        ("friend", "neutral"): "Mitra (Friend)",
        ("neutral", "friend"): "Mitra (Friend)",
        ("friend", "enemy"): "Sama (Neutral)",
        ("enemy", "friend"): "Sama (Neutral)",
        ("neutral", "neutral"): "Sama (Neutral)",
        ("neutral", "enemy"): "Shatru (Enemy)",
        ("enemy", "neutral"): "Shatru (Enemy)",
        ("enemy", "enemy"): "Adhi Shatru (Bitter Enemy)",
    }

    for p1 in seven_planets:
        naisargika_matrix[p1] = {}
        tatkalika_matrix[p1] = {}
        panchadha_matrix[p1] = {}
        for p2 in seven_planets:
            if p1 == p2:
                naisargika_matrix[p1][p2] = "—"
                tatkalika_matrix[p1][p2] = "—"
                panchadha_matrix[p1][p2] = "—"
                continue
            nat = relation(p1, p2)  # friend, neutral, enemy
            rel_house = (sign_of[p2] - sign_of[p1]) % 12 + 1
            temp = "friend" if rel_house in (2, 3, 4, 10, 11, 12) else "enemy"
            naisargika_matrix[p1][p2] = nat.capitalize()
            tatkalika_matrix[p1][p2] = temp.capitalize()
            panchadha_matrix[p1][p2] = COMPOUND_MAP[(nat, temp)]

    # --- F. 27-Nakshatra Tarabala & Latta (Planetary Kick) Matrix ---
    moon_ni, _ = nakshatra_of(moon_lon)
    TARA_NAMES = [
        "1. Janma (Body / Alertness)",
        "2. Sampat (Wealth & Prosperity)",
        "3. Vipat (Obstacles & Caution)",
        "4. Kshema (Safety & Well-Being)",
        "5. Pratyak (Resistance & Delay)",
        "6. Sadhana (Achievement & Success)",
        "7. Naidhana (Vulnerability — Avoid Risk)",
        "8. Mitra (Friendly Support)",
        "9. Parama Mitra (Supreme Alliance)",
    ]
    tarabala_27 = []
    for n_idx in range(27):
        dist = (n_idx - moon_ni) % 27
        tara_idx = dist % 9
        paryaya = dist // 9 + 1
        occupants = [p for p in VEDIC_PLANETS if nakshatra_of(pos[p]["longitude"])[0] == n_idx]
        tarabala_27.append({
            "nakshatra_number": n_idx + 1,
            "nakshatra": NAKSHATRAS[n_idx],
            "lord": NAK_LORDS[n_idx % 9],
            "tara_category": TARA_NAMES[tara_idx],
            "paryaya_cycle": paryaya,
            "is_auspicious": tara_idx in (1, 3, 5, 7, 8),
            "natal_occupants": occupants,
        })

    return {
        "upagrahas": upagrahas,
        "sphutas": sphutas,
        "yogi_avayogi_summary": {
            "yogi_point_deg": round(yogi_point, 4),
            "yogi_sign": SIGNS[int(yogi_point // 30) % 12],
            "yogi_nakshatra": NAKSHATRAS[yogi_ni],
            "yogi_planet": yogi_planet,
            "sahayogi_planet": sahayogi_planet,
            "avayogi_point_deg": round(avayogi_point, 4),
            "avayogi_nakshatra": NAKSHATRAS[avayogi_ni],
            "avayogi_planet": avayogi_planet,
        },
        "planetary_avasthas": avasthas_table,
        "panchadha_maitri_chakra": {
            "naisargika_natural": naisargika_matrix,
            "tatkalika_temporal": tatkalika_matrix,
            "panchadha_compound": panchadha_matrix,
        },
        "tarabala_27_nakshatras": tarabala_27,
    }


# ==============================================================================
# 4. ALL 22 DASHA SYSTEMS ENGINE (13 NAKSHATRA DASHAS + 9 RASHI DASHAS)
# ==============================================================================

def _fmt_jd_date(jd: float, tz: Any) -> str:
    return local_from_jd(jd, tz).date().isoformat()


def _rashi_dasha_from_sequence(
    name: str, method: str, seq: List[int], years_per_sign: List[float], birth_jd: float, tz: Any
) -> Dict[str, Any]:
    t = birth_jd
    periods = []
    for idx, s in enumerate(seq):
        y = years_per_sign[idx]
        e = t + y * YEAR_DAYS
        subs = []
        st = t
        for k in range(12):
            ss = (s + k) % 12
            se = st + (y * YEAR_DAYS / 12.0)
            subs.append({"sign": SIGNS[ss], "rashi": RASHIS[ss], "start": _fmt_jd_date(st, tz), "end": _fmt_jd_date(se, tz)})
            st = se
        periods.append({
            "sign": SIGNS[s],
            "rashi": RASHIS[s],
            "lord": SIGN_LORDS[s],
            "years": round(y, 2),
            "start": _fmt_jd_date(t, tz),
            "end": _fmt_jd_date(e, tz),
            "antardasha": subs,
        })
        t = e
    return {"system": name, "method": method, "total_years": round(sum(years_per_sign), 2), "periods": periods}


def compute_all_22_dasha_systems(
    pos: Dict[str, Any], asc_lon: float, birth_jd: float, tz: Any
) -> Dict[str, Any]:
    moon_lon = pos["Moon"]["longitude"]
    asc_sign = int(asc_lon // 30) % 12
    sign_of = {p: int(pos[p]["longitude"] // 30) % 12 for p in VEDIC_PLANETS}

    # 1. Vimshottari (120y)
    vim = vimshottari(moon_lon, birth_jd, tz, levels=3)

    # 2. Ashtottari (108y)
    ash = _adv_core.ashtottari(moon_lon, birth_jd, tz)

    # 3. Yogini (36y)
    yog = yogini(moon_lon, birth_jd, tz, cycles=2)

    # 4. Kalachakra
    kc = _dashas_core.kalachakra(moon_lon, birth_jd, tz)

    # 5 & 6. Tribhagi (80y = 2/3 Vimshottari) & Tribhagi-40 (40y = 1/3 Vimshottari)
    def _scaled_vimshottari(scale: float, label: str) -> Dict[str, Any]:
        span = 360.0 / 27.0
        ni = int(moon_lon // span)
        frac = (moon_lon - ni * span) / span
        lord0 = NAK_LORDS[ni % 9]
        i0 = VIM_ORDER.index(lord0)
        start = birth_jd - frac * (VIM_YEARS[lord0] * scale) * YEAR_DAYS
        t = start
        md = []
        for k in range(9):
            L = VIM_ORDER[(i0 + k) % 9]
            y = round(VIM_YEARS[L] * scale, 4)
            e = t + y * YEAR_DAYS
            subs = []
            st = t
            for sk in range(9):
                SL = VIM_ORDER[(i0 + k + sk) % 9]
                sy = y * VIM_YEARS[SL] / 120.0
                se = st + sy * YEAR_DAYS
                subs.append({"lord": SL, "start": _fmt_jd_date(st, tz), "end": _fmt_jd_date(se, tz)})
                st = se
            md.append({"lord": L, "years": round(y, 2), "start": _fmt_jd_date(t, tz), "end": _fmt_jd_date(e, tz), "antardasha": subs})
            t = e
        return {
            "system": label,
            "cycle_years": round(120.0 * scale, 1),
            "balance_at_birth": {"lord": lord0, "years_remaining": round((1.0 - frac) * VIM_YEARS[lord0] * scale, 4)},
            "periods": md,
        }

    tribhagi_80 = _scaled_vimshottari(2.0 / 3.0, "Tribhagi Dasha (80-Year Parashari Cycle)")
    tribhagi_40 = _scaled_vimshottari(1.0 / 3.0, "Tribhagi-40 Dasha (40-Year Condensed Cycle)")

    # 7..14. 8 Conditional Nakshatra Dashas (Shodashottari, Dwadashottari, Panchottari, Shatabdika, Chaturshitisama, Dwisaptatisama, Shashtihayani, Shattrimshatsama)
    conditional_nak_dashas = {}
    for kind in _dashas_core.NAK_DASHAS:
        d_obj = _dashas_core.nakshatra_dasha(kind, moon_lon, birth_jd, tz, cycles=1)
        # Add Antardashas to each conditional nakshatra dasha period
        lords, yrs, _, _, _ = _dashas_core.NAK_DASHAS[kind]
        total_y = sum(yrs)
        for p_idx, per in enumerate(d_obj["periods"]):
            st_jd = birth_jd if p_idx == 0 else (birth_jd + sum(x["years"] for x in d_obj["periods"][:p_idx]) * YEAR_DAYS)
            subs = []
            cur_t = st_jd
            l_start = lords.index(per["lord"])
            for sk in range(len(lords)):
                sl = lords[(l_start + sk) % len(lords)]
                sy = per["years"] * yrs[(l_start + sk) % len(lords)] / float(total_y)
                se = cur_t + sy * YEAR_DAYS
                subs.append({"lord": sl, "years": round(sy, 2), "start": _fmt_jd_date(cur_t, tz), "end": _fmt_jd_date(se, tz)})
                cur_t = se
            per["antardasha"] = subs
        conditional_nak_dashas[kind] = d_obj

    # 15. Jaimini Chara Dasha
    chara = _dashas_core.chara_dasha(pos, asc_lon, birth_jd, tz, cycles=1)

    # 16. Jaimini Sthira Dasha (Fixed 7/8/9 Years for Movable/Fixed/Dual Signs, starting from Brahma/Atmakaraka Rashi)
    sthira_seq = [(asc_sign + i) % 12 for i in range(12)]
    sthira_yrs = [7.0 if (s % 3 == 0) else (8.0 if (s % 3 == 1) else 9.0) for s in sthira_seq]
    sthira = _rashi_dasha_from_sequence(
        "Jaimini Sthira Dasha",
        "Fixed duration Rashi Dasha (Chara=7y, Sthira=8y, Dwiswabhava=9y; Total 96y)",
        sthira_seq, sthira_yrs, birth_jd, tz,
    )

    # 17. Narayana Dasha (Padakrama Rashi Dasha from Stronger of Lagna / 7th House)
    seventh_sign = (asc_sign + 6) % 12
    cnt_lag = sum(1 for p in VEDIC_PLANETS if sign_of[p] == asc_sign)
    cnt_sev = sum(1 for p in VEDIC_PLANETS if sign_of[p] == seventh_sign)
    narayana_start = asc_sign if cnt_lag >= cnt_sev else seventh_sign
    odd_footed = {0, 1, 2, 6, 7, 8}
    is_fwd = narayana_start in odd_footed
    narayana_seq = [(narayana_start + (i if is_fwd else -i)) % 12 for i in range(12)]
    narayana_yrs = []
    for s in narayana_seq:
        L = SIGN_LORDS[s]
        ls = sign_of[L]
        d = ((ls - s) % 12) if (s in odd_footed) else ((s - ls) % 12)
        y = 12 if d == 0 else d
        if L in EXALT and EXALT[L] == ls:
            y = min(12, y + 1)
        narayana_yrs.append(float(y))
    narayana = _rashi_dasha_from_sequence(
        "Narayana Dasha (Jaimini Padakrama)",
        f"Initiated from stronger of Lagna/7th ({SIGNS[narayana_start]}), {'Forward' if is_fwd else 'Reverse'} order",
        narayana_seq, narayana_yrs, birth_jd, tz,
    )

    # 18. Shoola Dasha (Trishoola Longevity & Health Dasha, 9 years per sign = 108y)
    shoola_start = asc_sign if cnt_lag >= cnt_sev else seventh_sign
    shoola_seq = [(shoola_start + i) % 12 for i in range(12)]
    shoola = _rashi_dasha_from_sequence(
        "Jaimini Shoola Dasha",
        "9 years per Rashi from stronger of 1st/7th house (108-year health & vitality cycle)",
        shoola_seq, [9.0] * 12, birth_jd, tz,
    )

    # 19. Niryaana Shoola Dasha (from 2nd or 8th house)
    second_sign = (asc_sign + 1) % 12
    eighth_sign = (asc_sign + 7) % 12
    cnt_2 = sum(1 for p in VEDIC_PLANETS if sign_of[p] == second_sign)
    cnt_8 = sum(1 for p in VEDIC_PLANETS if sign_of[p] == eighth_sign)
    nshoola_start = second_sign if cnt_2 >= cnt_8 else eighth_sign
    nshoola_seq = [(nshoola_start + i) % 12 for i in range(12)]
    niryaana_shoola = _rashi_dasha_from_sequence(
        "Niryaana Shoola Dasha",
        f"Initiated from stronger of 2nd/8th house ({SIGNS[nshoola_start]}), 9 years per sign",
        nshoola_seq, [9.0] * 12, birth_jd, tz,
    )

    # 20. Drig Dasha (Spiritual Awakening & Diksha Dasha from 9th House Aspecting Signs)
    ninth_sign = (asc_sign + 8) % 12
    drig_seq = [(ninth_sign + i) % 12 for i in range(12)]
    drig = _rashi_dasha_from_sequence(
        "Jaimini Drig Dasha",
        "Spiritual initiation & higher dharma progression from the 9th Bhava",
        drig_seq, narayana_yrs, birth_jd, tz,
    )

    # 21. Navamsha Dasha (9 years per Navamsha Rashi starting from Lagna/Navamsha Lagna)
    nav_lagna = varga_sign(asc_lon, 9)
    nav_seq = [(nav_lagna + i) % 12 for i in range(12)]
    nav_dasha = _rashi_dasha_from_sequence(
        "Navamsha Rashi Dasha",
        f"Initiated from Navamsha Lagna ({SIGNS[nav_lagna]}), 9 years per sign",
        nav_seq, [9.0] * 12, birth_jd, tz,
    )

    # 22. Lagna Kendradi Rashi Dasha (Kendra 1,4,7,10 -> Panapara 2,5,8,11 -> Apoklima 3,6,9,12)
    kendradi_offsets = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]
    kendradi_seq = [(asc_sign + off) % 12 for off in kendradi_offsets]
    kendradi = _rashi_dasha_from_sequence(
        "Lagna Kendradi Rashi Dasha",
        "Kendra (1,4,7,10) → Panapara (2,5,8,11) → Apoklima (3,6,9,12) sequence",
        kendradi_seq, narayana_yrs, birth_jd, tz,
    )

    return {
        "total_systems_computed": 22,
        "nakshatra_dashas": {
            "vimshottari_120y": vim,
            "ashtottari_108y": ash,
            "yogini_36y": yog,
            "kalachakra": kc,
            "tribhagi_80y": tribhagi_80,
            "tribhagi_40y": tribhagi_40,
            **conditional_nak_dashas,
        },
        "rashi_and_jaimini_dashas": {
            "chara_dasha": chara,
            "sthira_dasha": sthira,
            "narayana_dasha": narayana,
            "shoola_dasha": shoola,
            "niryaana_shoola_dasha": niryaana_shoola,
            "drig_dasha": drig,
            "navamsha_rashi_dasha": nav_dasha,
            "lagna_kendradi_rashi_dasha": kendradi,
        },
    }


# ==============================================================================
# 5. SATURN CYCLES (SADHESATI, DHAYYA, KANTAKA), MANGALA DOSHA & GEMSTONES
# ==============================================================================

GEMSTONE_SPECIFICATIONS: Dict[str, Dict[str, str]] = {
    "Sun": {
        "primary_gem": "Natural Burma Ruby (Manikya)",
        "substitute_gems": "Red Garnet (Tamda), Red Spinel (Laladi), Sunstone",
        "metal": "Gold (18K–22K) or Pure Copper",
        "weight_carats": "3 to 6 Carats (4 to 7 Rattis)",
        "finger": "Ring Finger (Anamika) of the Right Hand",
        "day_and_hora": "Sunday morning within 1 hour of Sunrise (Surya Hora)",
        "purification": "Immerse for 30 minutes in raw cow's milk, Ganga Jal, honey, and tulsi leaves",
        "mantra": "Om Hram Hreem Hroum Sah Suryaya Namah (7,000 recitations)",
        "scriptural_reference": "Garuda Purana (Ratna Pariksha Ch. 70): A pure ruby glows like the morning lotus and bestows royal authority, vitality, and longevity.",
    },
    "Moon": {
        "primary_gem": "Natural Basra / South Sea Pearl (Mukta / Moti)",
        "substitute_gems": "Natural Moonstone (Chandrakanta Mani), White Coral",
        "metal": "Pure Sterling Silver",
        "weight_carats": "4 to 7 Carats (5 to 8 Rattis)",
        "finger": "Little Finger (Kanishthika) or Ring Finger of the Right Hand",
        "day_and_hora": "Monday morning during Shukla Paksha (Chandra Hora)",
        "purification": "Immerse in unboiled milk and sacred water for 20 minutes",
        "mantra": "Om Shram Shreem Shroum Sah Chandraya Namah (11,000 recitations)",
        "scriptural_reference": "Brihat Samhita (Ch. 81): A lustrous spherical pearl calms mental agitation, strengthens ojas, and attracts fortune.",
    },
    "Mars": {
        "primary_gem": "Natural Italian / Mediterranean Red Coral (Moonga / Pravala)",
        "substitute_gems": "Carnelian, Red Jasper",
        "metal": "Gold or Pure Copper",
        "weight_carats": "5 to 8 Carats (6 to 9 Rattis)",
        "finger": "Ring Finger (Anamika) of the Right Hand",
        "day_and_hora": "Tuesday morning within 1 hour of Sunrise (Mangala Hora)",
        "purification": "Wash in raw milk and sacred water mixed with red sandalwood",
        "mantra": "Om Kram Kreem Kroum Sah Bhaumaya Namah (10,000 recitations)",
        "scriptural_reference": "Garuda Purana: Deep red coral free of perforations grants courage, victory over adversaries, and landed estate.",
    },
    "Mercury": {
        "primary_gem": "Natural Zambian / Colombian Emerald (Panna / Marakata)",
        "substitute_gems": "Green Tourmaline (Verdelite), Peridot, Green Jade",
        "metal": "Gold or Panchadhatu",
        "weight_carats": "3 to 6 Carats (4 to 7 Rattis)",
        "finger": "Little Finger (Kanishthika) of the Working Hand",
        "day_and_hora": "Wednesday morning within 2 hours of Sunrise (Budha Hora)",
        "purification": "Wash in raw milk and sacred water with tulsi leaves",
        "mantra": "Om Bram Breem Broum Sah Budhaya Namah (9,000 recitations)",
        "scriptural_reference": "Mani Mala: Emerald of velvety verdant hue sharpens intellect, eloquence, commercial mastery, and nervous resilience.",
    },
    "Jupiter": {
        "primary_gem": "Natural Ceylon Yellow Sapphire (Pukhraj / Pushparaga)",
        "substitute_gems": "Golden Topaz, Natural Citrine (Sunela)",
        "metal": "Yellow Gold",
        "weight_carats": "4 to 7 Carats (5 to 8 Rattis)",
        "finger": "Index Finger (Tarjani) of the Right Hand",
        "day_and_hora": "Thursday morning during Shukla Paksha (Guru Hora)",
        "purification": "Immerse in milk, honey, turmeric water, and Ganga Jal",
        "mantra": "Om Gram Greem Groum Sah Gurave Namah (19,000 recitations)",
        "scriptural_reference": "Garuda Purana: Flawless Pushparaga confers dharmic wisdom, progeny bliss, treasury expansion, and divine protection.",
    },
    "Venus": {
        "primary_gem": "Natural Diamond (Heera / Vajra) or Unheated White Sapphire (Safed Pukhraj)",
        "substitute_gems": "Natural White Zircon, Rock Crystal (Sphatika), Opal",
        "metal": "Platinum, White Gold, or Pure Silver",
        "weight_carats": "0.5 to 1.5 Carats (Diamond) or 4 to 6 Carats (White Sapphire)",
        "finger": "Middle Finger or Ring Finger of the Working Hand",
        "day_and_hora": "Friday morning after Sunrise (Shukra Hora)",
        "purification": "Wash in raw milk, rose water, and pure spring water",
        "mantra": "Om Dram Dreem Droum Sah Shukraya Namah (16,000 recitations)",
        "scriptural_reference": "Brihat Samhita (Ch. 80): Pure Vajra/White Sapphire bestows artistic brilliance, marital harmony, vehicles, and luxury.",
    },
    "Saturn": {
        "primary_gem": "Natural Ceylon Blue Sapphire (Neelam / Indraneela)",
        "substitute_gems": "Amethyst (Jamuniya), Iolite (Kaka-Neeli), Lapis Lazuli",
        "metal": "Panchadhatu, White Gold, Silver, or Iron",
        "weight_carats": "4 to 6 Carats (5 to 7 Rattis) — Always test for 72 hours before permanent setting",
        "finger": "Middle Finger (Madhyama) of the Right Hand",
        "day_and_hora": "Saturday evening 1 hour before Sunset (Shani Hora)",
        "purification": "Immerse in raw milk, black sesame water, and Ganga Jal",
        "mantra": "Om Pram Preem Proum Sah Shanaischaraya Namah (23,000 recitations)",
        "scriptural_reference": "Garuda Purana: Cornflower-blue Indraneela, when suiting the native, elevates discipline, endurance, and institutional authority.",
    },
}


def compute_saturn_cycles_mangala_and_gems(
    pos: Dict[str, Any], asc_lon: float, birth_jd: float, tz: Any
) -> Dict[str, Any]:
    asc_sign = int(asc_lon // 30) % 12
    moon_sign = int(pos["Moon"]["longitude"] // 30) % 12
    sign_of = {p: int(pos[p]["longitude"] // 30) % 12 for p in VEDIC_PLANETS}
    house_of = {p: (sign_of[p] - asc_sign) % 12 + 1 for p in VEDIC_PLANETS}

    # --- A. Saturn Sadhesati (3 Lifetime Cycles), Dhayya (4th/8th) & Kantaka (4th/7th/10th) ---
    raw_periods = sade_sati(moon_sign, birth_jd, years=95, tz=tz)
    sade_sati_cycles = []
    dhayya_periods = []
    cur_cycle = []

    PHASE_BODY_EFFECTS = {
        "Rising (12th)": {
            "dhayya_stage": "1st Dhayya (Rising — Head & Eyes)",
            "focus": "Mental restlessness, expenditure on restructuring, long-distance travel, and clearing outdated commitments.",
            "remedy": "Recite Dasharatha Shani Stotra on Saturdays and offer mustard oil lamp beneath a Peepal tree.",
        },
        "Peak (over Moon)": {
            "dhayya_stage": "2nd Dhayya (Peak — Heart, Chest & Core Identity)",
            "focus": "Deep emotional maturation, high responsibility in career and family, forging unshakeable inner character.",
            "remedy": "Perform Chhaya Dana (viewing your reflection in sesame/mustard oil in an iron bowl and donating it) on Saturdays.",
        },
        "Setting (2nd)": {
            "dhayya_stage": "3rd Dhayya (Setting — Feet, Speech & Treasury)",
            "focus": "Financial reorganization, family duties, and final consolidation of lessons before Saturn's departing reward.",
            "remedy": "Chant Vedic Shani Mantra ('Om Sham No Devir Abhishtaya...') and feed crows/stray animals on Saturdays.",
        },
    }

    for item in raw_periods:
        ph = item["phase"]
        if ph in PHASE_BODY_EFFECTS:
            info = PHASE_BODY_EFFECTS[ph]
            enriched = {
                **item,
                "dhayya_stage": info["dhayya_stage"],
                "classical_effect": info["focus"],
                "specific_remedy": info["remedy"],
            }
            cur_cycle.append(enriched)
            if ph == "Setting (2nd)":
                sade_sati_cycles.append({
                    "cycle_number": len(sade_sati_cycles) + 1,
                    "cycle_start": cur_cycle[0]["start"],
                    "cycle_end": cur_cycle[-1]["end"],
                    "phases": cur_cycle,
                })
                cur_cycle = []
        else:
            dhayya_periods.append({
                **item,
                "classical_name": "Laghu Kalyani Dhayya (Small Panoti — 2.5 Years)",
                "effect": (
                    "4th from Moon (Ardhashtama): Domestic/property reorganization and career pivot."
                    if "4th" in ph else
                    "8th from Moon (Ashtama Shani): Deep transformation, health vigilance, and disciplined patience."
                ),
            })
    if cur_cycle:
        sade_sati_cycles.append({
            "cycle_number": len(sade_sati_cycles) + 1,
            "cycle_start": cur_cycle[0]["start"],
            "cycle_end": cur_cycle[-1]["end"],
            "phases": cur_cycle,
        })

    # --- B. Comprehensive Mangala (Kuja) Dosha Analysis + 12 Classical Cancellation Rules ---
    mars_h_lagna = house_of["Mars"]
    mars_h_moon = (sign_of["Mars"] - sign_of["Moon"]) % 12 + 1
    mars_h_venus = (sign_of["Mars"] - sign_of["Venus"]) % 12 + 1
    mangala_houses = {1, 2, 4, 7, 8, 12}

    from_lagna = mars_h_lagna in mangala_houses
    from_moon = mars_h_moon in mangala_houses
    from_venus = mars_h_venus in mangala_houses

    cancellations: List[str] = []
    ms = sign_of["Mars"]
    if ms in (0, 7):
        cancellations.append(f"Mars occupies its Own Sign ({SIGNS[ms]}), neutralizing destructive Kuja Dosha.")
    if ms == 9:
        cancellations.append("Mars is Exalted in Capricorn (Makara), transmuting heat into disciplined protective strength.")
    if ms == 3:
        cancellations.append("Mars is in Cancer (Karka), where classical Manasagari texts state its fiery edge is cooled.")
    if asc_sign in (3, 4):
        cancellations.append(f"For {SIGNS[asc_sign]} Ascendant, Mars is a supreme Yogakaraka (ruling a Kendra and a Trikona), cancelling Kuja Dosha.")
    if mars_h_lagna == 1 and ms in (0, 4, 7, 8, 9):
        cancellations.append(f"Mars in the 1st house in {SIGNS[ms]} is exempted by Agastya Samhita.")
    if mars_h_lagna == 2 and ms in (2, 5):
        cancellations.append(f"Mars in the 2nd house in Mercury's sign ({SIGNS[ms]}) is exempted by BPHS.")
    if mars_h_lagna == 4 and ms in (0, 7):
        cancellations.append(f"Mars in the 4th house in {SIGNS[ms]} grants property without marital blemish.")
    if mars_h_lagna == 7 and ms in (3, 9):
        cancellations.append(f"Mars in the 7th house in {SIGNS[ms]} is exempted from Kuja Dosha.")
    if mars_h_lagna == 8 and ms in (3, 8, 11):
        cancellations.append(f"Mars in the 8th house in Jupiter/Moon sign ({SIGNS[ms]}) is exempted.")
    if mars_h_lagna == 12 and ms in (1, 6):
        cancellations.append(f"Mars in the 12th house in Venus's sign ({SIGNS[ms]}) is exempted.")
    if sign_of["Jupiter"] == ms or ((sign_of["Jupiter"] - ms) % 12 in (0, 4, 6, 8)):
        cancellations.append("Benevolent conjunction or aspect of Jupiter (Brihaspati) on Mars pacifies Kuja Dosha.")
    if sign_of["Saturn"] in (0, 3, 6, 7, 11) and mars_h_lagna in mangala_houses:
        cancellations.append("Strong placement of Saturn counterbalances Mars's thermal intensity.")

    active_count = sum([from_lagna, from_moon, from_venus])
    effective_manglik = (from_lagna or from_moon) and (len(cancellations) == 0)

    MANGALA_HOUSE_EFFECTS = {
        1: "Mars in the 1st Bhava grants dynamic leadership and physical vigor, but can create impatience or headstrong reactions in partnership unless channelled into athletics or enterprise.",
        2: "Mars in the 2nd Bhava gives direct, forceful speech and intense drive for family treasury; practicing gentle communication preserves domestic harmony.",
        4: "Mars in the 4th Bhava energizes real-estate acquisition and career ambition (aspecting 10th), requiring conscious emotional calm at home.",
        7: "Mars in the 7th Bhava brings passionate devotion and assertive partnership dynamics; mutual respect and shared active goals turn friction into synergy.",
        8: "Mars in the 8th Bhava intensifies research, longevity resilience, and shared financial accountability; transparency in joint assets is essential.",
        12: "Mars in the 12th Bhava channels energy into global ventures, spiritual kriyas, and charitable expenditure.",
    }

    mangala_report = {
        "from_lagna": from_lagna,
        "mars_house_from_lagna": mars_h_lagna,
        "from_moon": from_moon,
        "mars_house_from_moon": mars_h_moon,
        "from_venus": from_venus,
        "mars_house_from_venus": mars_h_venus,
        "triple_chart_score": f"{active_count}/3 reference charts show Mars in {sorted(mangala_houses)}",
        "cancellations_found": cancellations,
        "is_cancelled": len(cancellations) > 0 and (from_lagna or from_moon or from_venus),
        "effective_status": (
            "No Mangala Dosha Present"
            if not (from_lagna or from_moon or from_venus)
            else ("Mangala Dosha Present but Classically Cancelled (Shuddha)" if cancellations else f"Active Mangala Dosha ({'High' if active_count >= 2 else 'Moderate'})")
        ),
        "effective_manglik": effective_manglik,
        "house_effect_narrative": MANGALA_HOUSE_EFFECTS.get(
            mars_h_lagna,
            f"Mars occupies the {mars_h_lagna}th Bhava from Lagna in {SIGNS[ms]}, promoting constructive courage and initiative.",
        ),
        "classical_remedies": [
            "Recite Mangala Chandika Stotra or Hanuman Chalisa every Tuesday morning.",
            "Donate red masoor lentils, jaggery, or copper on Tuesdays during Shukla Paksha.",
            "Practice patience in speech and avoid impulsive agreements on Tuesday afternoons (Rahu Kaal).",
        ],
    }

    # --- C. Gemstone Recommendations #1 & #2 (Life Stone = 1st Lord, Lucky Stone = 5th Lord, Destiny Stone = 9th Lord) ---
    lord_1 = SIGN_LORDS[asc_sign]
    lord_5 = SIGN_LORDS[(asc_sign + 4) % 12]
    lord_9 = SIGN_LORDS[(asc_sign + 8) % 12]

    def _build_stone_rec(role_title: str, house_num: int, lord: str) -> Dict[str, Any]:
        spec = GEMSTONE_SPECIFICATIONS.get(lord, GEMSTONE_SPECIFICATIONS["Jupiter"])
        return {
            "role": role_title,
            "house_ruled": f"{house_num}th House ({SIGNS[(asc_sign + house_num - 1) % 12]})",
            "ruling_planet": lord,
            "natal_placement": f"{SIGNS[sign_of[lord]]} (House {house_of[lord]}, {dignity(lord, pos[lord]['longitude'])})",
            **spec,
        }

    # Avoid recommending stones of pure 6/8/12 dusthana lords unless they also rule 1, 5, or 9
    lords_6_8_12 = {SIGN_LORDS[(asc_sign + 5) % 12], SIGN_LORDS[(asc_sign + 7) % 12], SIGN_LORDS[(asc_sign + 11) % 12]}
    trine_lords = {lord_1, lord_5, lord_9}
    avoid_lords = sorted(lords_6_8_12 - trine_lords)

    return {
        "saturn_cycles": {
            "moon_rashi": f"{RASHIS[moon_sign]} ({SIGNS[moon_sign]})",
            "sade_sati_3_lifetime_cycles": sade_sati_cycles[:3],
            "laghu_kalyani_dhayya_periods": dhayya_periods[:10],
            "universal_saturn_remedies": [
                "Vedic Shani Mantra: 'Om Sham No Devir Abhishtaya Aapo Bhavantu Peetaye Sham Yor Abhi Sravantu Nah'",
                "Puranic Shani Stotra (Dasharatha Krita): 'Konatho Pingalo Babhruh Krishno Raudro Antako Yamah...'",
                "Mahamrityunjaya Mantra: 'Om Tryambakam Yajamahe Sugandhim Pushtivardhanam...'",
                "Charitable Seva: Support elderly, disabled, or laboring workers and offer black sesame and iron on Saturdays.",
            ],
        },
        "mangala_dosha_analysis": mangala_report,
        "gemstone_recommendations": {
            "lagna": f"{RASHIS[asc_sign]} ({SIGNS[asc_sign]})",
            "life_stone_lagnesh": _build_stone_rec("Life Stone (Jeevana Ratna — 1st Lord)", 1, lord_1),
            "lucky_stone_panchamesh": _build_stone_rec("Lucky & Intelligence Stone (Punya Ratna — 5th Lord)", 5, lord_5),
            "destiny_stone_bhagyesh": _build_stone_rec("Destiny & Fortune Stone (Bhagya Ratna — 9th Lord)", 9, lord_9),
            "gems_to_avoid_or_test_carefully": [
                {
                    "planet": pl,
                    "primary_gem": GEMSTONE_SPECIFICATIONS[pl]["primary_gem"],
                    "reason": f"Rules a Dusthana (6th/8th/12th) without owning a Trikona (1st/5th/9th) for {SIGNS[asc_sign]} Ascendant.",
                }
                for pl in avoid_lords if pl in GEMSTONE_SPECIFICATIONS
            ],
        },
    }


# ==============================================================================
# 6. BIRTH TIME RECTIFICATION, ASTRO-RELOCATION, PANCH PAKSHI & SPICA WORKSHEET
# ==============================================================================

PANCH_PAKSHI_BIRDS = ["Vulture (Gridhra)", "Owl (Uluka)", "Crow (Kaka)", "Cock (Kukkuta)", "Peacock (Mayura)"]
PANCH_PAKSHI_STATES = [
    ("Ruling (Arasu)", "100% Power — Supreme success, authority, and effortless accomplishment."),
    ("Eating (ishti / Bhajana)", "80% Power — Resource inflow, nourishment, and steady gains."),
    ("Walking (Gamana)", "50% Power — Moderate progress through movement and effort."),
    ("Sleeping (Nidra)", "25% Power — Better for rest, contemplation, and internal planning."),
    ("Dying (Marana)", "0% Power — Avoid launching critical high-risk ventures during this sub-window."),
]


def compute_rectification_and_relocation_tools(
    dt_utc: datetime,
    lat: float,
    lon: float,
    tz: Any,
    target_lat: Optional[float] = None,
    target_lon: Optional[float] = None,
    target_city: Optional[str] = None,
) -> Dict[str, Any]:
    birth_jd = jd_from_utc(dt_utc)
    pos = all_positions(birth_jd, sidereal=True, true_node=False)
    cusps, asc_lon, mc_lon = houses(birth_jd, lat, lon, "W", True)
    asc_sign = int(asc_lon // 30) % 12
    deg_in_sign = asc_lon % 30.0

    # Ascendant moves ~360° in 24 sidereal hours => ~1° every 4 minutes
    def _boundary_minutes(slice_deg: float, varga_label: str, cur_sign_idx: int) -> Dict[str, Any]:
        pos_in_slice = asc_lon % slice_deg
        mins_since_prev = round(pos_in_slice * 4.0, 2)
        mins_to_next = round((slice_deg - pos_in_slice) * 4.0, 2)
        prev_dt = local_from_jd(birth_jd - (mins_since_prev / 1440.0), tz)
        next_dt = local_from_jd(birth_jd + (mins_to_next / 1440.0), tz)
        return {
            "division": varga_label,
            "slice_span_deg": round(slice_deg, 4),
            "current_sign": SIGNS[cur_sign_idx],
            "current_rashi": RASHIS[cur_sign_idx],
            "minutes_since_previous_change": mins_since_prev,
            "previous_boundary_local_time": prev_dt.strftime("%H:%M:%S"),
            "minutes_until_next_change": mins_to_next,
            "next_boundary_local_time": next_dt.strftime("%H:%M:%S"),
        }

    rectification_boundaries = [
        _boundary_minutes(30.0, "Rashi Lagna (D-1 — 30°00')", asc_sign),
        _boundary_minutes(10.0, "Drekkana Lagna (D-3 — 10°00')", varga_sign(asc_lon, 3)),
        _boundary_minutes(10.0 / 3.0, "Navamsha Lagna (D-9 — 3°20')", varga_sign(asc_lon, 9)),
        _boundary_minutes(3.0, "Dashamsha Lagna (D-10 — 3°00')", varga_sign(asc_lon, 10)),
        _boundary_minutes(2.5, "Dwadashamsha Lagna (D-12 — 2°30')", varga_sign(asc_lon, 12)),
        _boundary_minutes(0.5, "Shashtiamsha Lagna (D-60 — 0°30')", varga_sign(asc_lon, 60)),
        _boundary_minutes(30.0 / 81.0, "Kunda Lagna (81× Ascendant — 0°22'13\")", int(norm(asc_lon * 81.0) // 30) % 12),
    ]

    # Classical Kunda & Pranapada Rectification Verification (BPHS)
    moon_lon = pos["Moon"]["longitude"]
    moon_ni, _ = nakshatra_of(moon_lon)
    moon_sign = int(moon_lon // 30) % 12
    kunda_lon = norm(asc_lon * 81.0)
    kunda_sign = int(kunda_lon // 30) % 12
    kunda_rel = (kunda_sign - moon_sign) % 12 + 1
    kunda_verified = kunda_rel in (1, 5, 7, 9)

    sun_lon = pos["Sun"]["longitude"]
    sun_sign = int(sun_lon // 30) % 12
    sun_anchor = sun_lon if (sun_sign % 3 == 0) else (norm(sun_lon + 240.0) if (sun_sign % 3 == 1) else norm(sun_lon + 120.0))
    pranapada_lon = norm((asc_lon - sun_lon) * 5.0 + sun_anchor)
    pranapada_sign = int(pranapada_lon // 30) % 12

    # --- Astro-Relocation (Change Location Tool) ---
    rel_lat = target_lat if target_lat is not None else 51.5074  # Default comparison: London if none passed
    rel_lon = target_lon if target_lon is not None else -0.1278
    rel_city = target_city or ("Custom Target Location" if target_lat is not None else "London, UK (Reference Relocation)")
    _, rel_asc, rel_mc = houses(birth_jd, rel_lat, rel_lon, "W", True)
    rel_asc_sign = int(rel_asc // 30) % 12

    relocated_planet_shifts = []
    for p in VEDIC_PLANETS:
        p_sign = int(pos[p]["longitude"] // 30) % 12
        natal_h = (p_sign - asc_sign) % 12 + 1
        rel_h = (p_sign - rel_asc_sign) % 12 + 1
        relocated_planet_shifts.append({
            "planet": p,
            "sign": SIGNS[p_sign],
            "natal_house": natal_h,
            "relocated_house": rel_h,
            "house_shift": rel_h - natal_h,
        })

    # --- Panch Pakshi (5-Bird Bio-Rhythm System) ---
    is_shukla = norm(moon_lon - sun_lon) < 180.0
    bird_idx = (moon_ni // 5) % 5
    if not is_shukla:
        bird_idx = (4 - bird_idx) % 5
    birth_bird = PANCH_PAKSHI_BIRDS[bird_idx]
    weekday = int((birth_jd + 1.5) % 7)
    state_idx = (bird_idx + weekday) % 5
    state_name, state_desc = PANCH_PAKSHI_STATES[state_idx]

    # --- Navamsha Ages & SPICA Steps 1A–5 Auspiciousness Worksheet ---
    navamsha_ages = []
    for n_step in range(1, 13):
        s_idx = (varga_sign(asc_lon, 9) + n_step - 1) % 12
        lord = SIGN_LORDS[s_idx]
        navamsha_ages.append({
            "cycle_step": n_step,
            "age_span": f"Age {(n_step - 1) * 9}–{n_step * 9}",
            "navamsha_sign": SIGNS[s_idx],
            "ruling_lord": lord,
            "lord_dignity": dignity(lord, pos[lord]["longitude"]),
        })

    spica_steps = []
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        L = pos[p]["longitude"]
        s = int(L // 30) % 12
        h = (s - asc_sign) % 12 + 1
        dig = dignity(p, L)
        step_1a = 20 if dig in ("exalted", "moolatrikona", "own") else (12 if dig == "friendly" else (8 if dig == "neutral" else 4))
        step_1b = 20 if h in (1, 4, 5, 7, 9, 10) else (14 if h in (2, 3, 11) else 6)
        nav_s = varga_sign(L, 9)
        nav_dig = dignity(p, nav_s * 30.0 + 15.0)
        step_2 = 20 if nav_dig in ("exalted", "own", "moolatrikona") else (14 if nav_dig == "friendly" else 8)
        step_3 = 20 if s == nav_s else 12  # Vargottama bonus
        step_4 = 15 if abs(angdiff(L, sun_lon)) > 12.0 or p == "Sun" else 6
        total_spica = step_1a + step_1b + step_2 + step_3 + step_4
        spica_steps.append({
            "planet": p,
            "step_1a_rashi_dignity": step_1a,
            "step_1b_bhava_placement": step_1b,
            "step_2_navamsha_disposition": step_2,
            "step_3_vargottama_harmony": step_3,
            "step_4_rays_clarity": step_4,
            "step_5_composite_auspiciousness": total_spica,
            "grade": "Uttama (Supreme)" if total_spica >= 80 else ("Madhyama (Strong)" if total_spica >= 60 else "ochita (Needs Support)"),
        })

    return {
        "birth_time_rectification": {
            "recorded_ascendant": f"{SIGNS[asc_sign]} {dms(deg_in_sign)} ({RASHIS[asc_sign]})",
            "division_shift_boundaries": rectification_boundaries,
            "kunda_verification": {
                "kunda_longitude": round(kunda_lon, 4),
                "kunda_sign": SIGNS[kunda_sign],
                "moon_sign": SIGNS[moon_sign],
                "house_from_moon": kunda_rel,
                "is_classically_rectified": kunda_verified,
                "rule": "BPHS Kunda Rule: Birth time is exact within ±44 seconds when Kunda Lagna (81 × Ascendant) falls in 1st, 5th, 7th, or 9th from Janma Rashi.",
            },
            "pranapada_verification": {
                "pranapada_longitude": round(pranapada_lon, 4),
                "pranapada_sign": SIGNS[pranapada_sign],
                "house_from_lagna": (pranapada_sign - asc_sign) % 12 + 1,
            },
        },
        "astro_relocation": {
            "natal_coordinates": {"latitude": lat, "longitude": lon, "ascendant": f"{SIGNS[asc_sign]} {dms(deg_in_sign)}"},
            "relocated_target": {
                "city": rel_city,
                "latitude": rel_lat,
                "longitude": rel_lon,
                "relocated_ascendant": f"{SIGNS[rel_asc_sign]} {dms(rel_asc % 30)}",
                "relocated_midheaven": f"{SIGNS[int(rel_mc // 30) % 12]} {dms(rel_mc % 30)}",
            },
            "planetary_house_shifts": relocated_planet_shifts,
        },
        "panch_pakshi_biorhythm": {
            "paksha": "Shukla Paksha (Waxing)" if is_shukla else "Krishna Paksha (Waning)",
            "birth_pakshi_bird": birth_bird,
            "natal_activity_state": state_name,
            "interpretation": state_desc,
            "all_5_states": [{"state": s[0], "effect": s[1]} for s in PANCH_PAKSHI_STATES],
        },
        "navamsha_life_ages": navamsha_ages,
        "spica_steps_1a_to_5_worksheet": spica_steps,
    }


# ==============================================================================
# 7. ASTRONOMICAL PROFILES & COMPLETE MULTI-CHAPTER REPORT GENERATOR
# ==============================================================================

ASTRONOMICAL_PROFILES: List[Dict[str, str]] = [
    {"body": "Sun (Surya)", "diameter_km": "1,392,700 km", "mass_earths": "332,946 × Earth", "rotation_period": "25.38 days (equator)", "orbital_period": "Galactic orbit ~225M years", "vedic_role": "Atmakaraka (Soul), Royal Authority, Vitality, Father, and Solar Dharma."},
    {"body": "Moon (Chandra)", "diameter_km": "3,474.8 km", "mass_earths": "0.0123 × Earth", "rotation_period": "27.32 days (tidally locked)", "orbital_period": "27.3217 days (Sidereal Month)", "vedic_role": "Manokaraka (Mind), Emotions, Mother, Soma Nourishment, and Public Popularity."},
    {"body": "Mars (Mangala / Kuja)", "diameter_km": "6,779 km", "mass_earths": "0.107 × Earth", "rotation_period": "24h 37m 22s", "orbital_period": "686.98 Earth days", "vedic_role": "Senapati (Commander), Courage, Landed Property,Siblings, and Technical Precision."},
    {"body": "Mercury (Budha)", "diameter_km": "4,879.4 km", "mass_earths": "0.0553 × Earth", "rotation_period": "58.65 Earth days", "orbital_period": "87.97 Earth days", "vedic_role": "Yuvaraja (Crown Prince), Analytical Intelligence, Speech, Commerce, and Adaptability."},
    {"body": "Jupiter (Brihaspati / Guru)", "diameter_km": "139,820 km", "mass_earths": "317.8 × Earth", "rotation_period": "9h 55m 30s", "orbital_period": "11.862 Earth years", "vedic_role": "Deva-Guru (Preceptor), Wisdom, Treasury, Progeny, Ethics, and Divine Grace."},
    {"body": "Venus (Shukra)", "diameter_km": "12,104 km", "mass_earths": "0.815 × Earth", "rotation_period": "243.02 Earth days (retrograde)", "orbital_period": "224.70 Earth days", "vedic_role": "Daitya-Guru (Preceptor), Marriage, Aesthetics, Vehicles, Diplomacy, and Sanjeevani Renewal."},
    {"body": "Saturn (Shani)", "diameter_km": "116,460 km", "mass_earths": "95.16 × Earth", "rotation_period": "10h 33m 38s", "orbital_period": "29.457 Earth years", "vedic_role": "Ayushkaraka (Longevity), Karmic Justice, Perseverance, Service, and Structural Mastery."},
    {"body": "Rahu & Ketu (Lunar Nodes)", "diameter_km": "Mathematical Ecliptic-Lunar Intersection", "mass_earths": "Gravitational Eclipse Axis", "rotation_period": "Retrograde Precession", "orbital_period": "18.61 Earth years (Nodal Cycle)", "vedic_role": "Karmic Evolution Axis: Rahu drives worldly expansion and innovation; Ketu grants moksha and intuitive mastery."},
]

LAGNA_TEMPERAMENT_TREATISE: Dict[str, Dict[str, str]] = {
    "Aries": {
        "nature": "Pioneering, dynamic, courageous, and decisive. Ruled by Mars in a Chara Agni (Movable Fire) sign, you possess natural executive initiative and refuse to stagnate.",
        "shastric_appearance": "Brihat Jataka & Saravali describe Mesha Lagna natives as having an athletic, energetic frame, expressive eyebrows, warm complexion, and a brisk, purposeful stride.",
        "modern_profile": "Natural entrepreneur, strategist, or crisis leader who thrives when given autonomy and clear milestones.",
        "lucky_days": "Tuesday, Sunday, Thursday",
        "lucky_numbers": "1, 9, 3",
        "lucky_colors": "Crimson Red, Saffron Gold, Coral Orange",
    },
    "Taurus": {
        "nature": "Steadfast, aesthetic, patient, and resource-wise. Ruled by Venus in a Sthira Prithvi (Fixed Earth) sign, you build enduring institutions, wealth, and harmonious relationships.",
        "shastric_appearance": "Classical texts note a magnetic countenance, serene eyes, strong shoulders, melodious voice, and graceful composure.",
        "modern_profile": "Financial steward, design/luxury innovator, or institutional builder valued for unshakeable reliability.",
        "lucky_days": "Friday, Saturday, Wednesday",
        "lucky_numbers": "6, 5, 8",
        "lucky_colors": "Pearl White, Emerald Green, Royal Blue",
    },
    "Gemini": {
        "nature": "Versatile, intellectually agile, articulate, and curious. Ruled by Mercury in a Dwiswabhava Vayu (Dual Air) sign, you synthesize diverse fields with effortless wit.",
        "shastric_appearance": "Saravali describes Mithuna Lagna natives with bright inquisitive eyes, expressive hands, youthful demeanor, and quick speech.",
        "modern_profile": "Polymath communicator, technologist, author, or strategist who bridges people and systems.",
        "lucky_days": "Wednesday, Friday",
        "lucky_numbers": "5, 6, 3",
        "lucky_colors": "Verdant Green, Sky Blue, Ivory",
    },
    "Cancer": {
        "nature": "Empathetic, protective, intuitive, and tenacious. Ruled by the Moon in a Chara Jala (Movable Water) sign, you combine deep emotional intelligence with public leadership.",
        "shastric_appearance": "Phaladeepika notes a luminous face, compassionate gaze, nurturing presence, and strong attachment to heritage and sanctuary.",
        "modern_profile": "Institutional caretaker, visionary leader, healer, or diplomat with strong public resonance.",
        "lucky_days": "Monday, Tuesday, Thursday",
        "lucky_numbers": "2, 7, 9",
        "lucky_colors": "Moonlight Silver, Sea Pearl, Saffron",
    },
    "Leo": {
        "nature": "Magnanimous, sovereign, principled, and dignified. Ruled by the Sun in a Sthira Agni (Fixed Fire) sign, you naturally command authority and uphold high ethical standards.",
        "shastric_appearance": "Brihat Jataka describes Simha Lagna natives with broad chest/shoulders, commanding gaze, regal posture, and an unmistakable aura of self-respect.",
        "modern_profile": "Executive statesperson, creative director, or civic pillar who inspires loyalty through noble vision.",
        "lucky_days": "Sunday, Tuesday, Thursday",
        "lucky_numbers": "1, 4, 9",
        "lucky_colors": "Solar Gold, Ruby Crimson, Amber",
    },
    "Virgo": {
        "nature": "Analytical, discerning, methodical, and service-oriented. Ruled by exalted Mercury in a Dwiswabhava Prithvi (Dual Earth) sign, you master complex systems and precision crafts.",
        "shastric_appearance": "Saravali highlights refined features, observant eyes, youthful vitality, and composed, articulate speech.",
        "modern_profile": "Researcher, physician, financial/data architect, or scholar prized for diagnostic brilliance.",
        "lucky_days": "Wednesday, Friday",
        "lucky_numbers": "5, 6",
        "lucky_colors": "Forest Green, Champagne White, Pastel Yellow",
    },
    "Libra": {
        "nature": "Diplomatic, just, refined, and strategically balanced. Ruled by Venus in its Moolatrikona Chara Vayu (Movable Air) sign, you excel in statesmanship, commerce, and alliance-building.",
        "shastric_appearance": "Phaladeepika notes symmetrical proportions, magnetic smile, refined attire, and a calm, persuasive demeanor.",
        "modern_profile": "Arbiter, legal/commercial leader, creative producer, or strategist who harmonizes competing forces.",
        "lucky_days": "Friday, Saturday, Wednesday",
        "lucky_numbers": "6, 8, 5",
        "lucky_colors": "Diamond White, Sapphire Blue, Turquoise",
    },
    "Scorpio": {
        "nature": "Penetrating, resilient, transformative, and fiercely loyal. Ruled by Mars in a Sthira Jala (Fixed Water) sign, you uncover hidden truths and thrive under high-stakes pressure.",
        "shastric_appearance": "Classical Hora texts describe intense, perceptive eyes, resolute jaw, magnetic reserve, and remarkable recuperative stamina.",
        "modern_profile": "Deep researcher, surgeon, investigator, or turnaround executive who masters crisis and renewal.",
        "lucky_days": "Tuesday, Thursday, Monday",
        "lucky_numbers": "9, 3, 2",
        "lucky_colors": "Deep Rust, Golden Yellow, Pearl White",
    },
    "Sagittarius": {
        "nature": "Philosophical, visionary, forthright, and dharmic. Ruled by Jupiter in a Dwiswabhava Agni (Dual Fire) sign, you aim toward higher purpose, education, and noble institutions.",
        "shastric_appearance": "Brihat Jataka describes Dhanu Lagna natives with a tall, dignified bearing, radiant forehead, candid gaze, and inspiring voice.",
        "modern_profile": "Mentor, jurist, global strategist, or visionary founder guided by principle and foresight.",
        "lucky_days": "Thursday, Sunday, Tuesday",
        "lucky_numbers": "3, 1, 9",
        "lucky_colors": "Turmeric Gold, Sunset Orange, Crimson",
    },
    "Capricorn": {
        "nature": "Pragmatic, disciplined, enduring, and architecturally minded. Ruled by Saturn in a Chara Prithvi (Movable Earth) sign, you play the long game and achieve lasting authority.",
        "shastric_appearance": "Saravali notes a composed, chiseled countenance, patient eyes, steady gait, and increasing vitality with maturity.",
        "modern_profile": "Chief administrator, infrastructure builder, or institutional steward whose peak authority blossoms steadily over time.",
        "lucky_days": "Saturday, Friday, Wednesday",
        "lucky_numbers": "8, 6, 5",
        "lucky_colors": "Indigo Blue, Emerald Green, Charcoal Silver",
    },
    "Aquarius": {
        "nature": "Humanitarian, original, systemic, and philosophically deep. Ruled by Saturn in its Moolatrikona Sthira Vayu (Fixed Air) sign, you innovate for collective upliftment.",
        "shastric_appearance": "Classical texts describe a thoughtful brow, noble stature, observant gaze, and an approachable yet independent presence.",
        "modern_profile": "Systems visionary, scientist, social reformer, or network architect ahead of conventional trends.",
        "lucky_days": "Saturday, Friday, Wednesday",
        "lucky_numbers": "8, 6, 5",
        "lucky_colors": "Electric Sapphire, Violet, Pearl White",
    },
    "Pisces": {
        "nature": "Intuitive, wise, compassionate, and transcendentally imaginative. Ruled by Jupiter in a Dwiswabhava Jala (Dual Water) sign, you unite scholarship with spiritual depth.",
        "shastric_appearance": "Phaladeepika notes luminous, expressive eyes, serene countenance, gentle voice, and an aura of grace and wisdom.",
        "modern_profile": "Counselor, creative visionary, scholar, or philanthropic leader guided by deep inner knowing.",
        "lucky_days": "Thursday, Monday, Tuesday",
        "lucky_numbers": "3, 2, 9",
        "lucky_colors": "Seafoam Gold, Saffron Yellow, Pearl White",
    },
}


def generate_detailed_text_report(
    dt_utc: datetime,
    lat: float,
    lon: float,
    tz: Any,
    name: str = "Native",
    gender: str = "male",
    model_code: str = "HP3",
    chapters: Optional[List[str]] = None,
    target_year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a complete, multi-chapter book-formatted Vedic Horoscope Dossier
    matching any of the 20 standard Report Models (HC1..HC4, HP1..HP4, KP1..KP2,
    VC1..VC2, VP1..VP2, HM1..HM2, PH1..PH2, PV, MASTER_COMPLETE).
    Strictly 100% original PanchangHub synthesis with zero third-party watermarks.
    """
    model_upper = (model_code or "HP3").upper()
    model_meta = next((m for m in REPORT_MODELS_CATALOG if m["code"] == model_upper), REPORT_MODELS_CATALOG[6])

    birth_jd = jd_from_utc(dt_utc)
    pos = all_positions(birth_jd, sidereal=True, true_node=False)
    cusps, asc_lon, mc_lon = houses(birth_jd, lat, lon, "W", True)
    asc_sign = int(asc_lon // 30) % 12
    moon_lon = pos["Moon"]["longitude"]
    moon_sign = int(moon_lon // 30) % 12
    m_ni, m_pada = nakshatra_of(moon_lon)

    # Core calculations
    k = compute_kundli(dt_utc, lat, lon, tz, False, 3, "W")
    ava_ghata = compute_avakhada_and_ghata_chakra(pos, asc_lon, birth_jd, lat, lon, tz)
    upa_sphuta = compute_upagrahas_sphutas_avasthas_maitri(pos, asc_lon, birth_jd, lat, lon)
    all_22_dashas = compute_all_22_dasha_systems(pos, asc_lon, birth_jd, tz)
    sat_mangala_gems = compute_saturn_cycles_mangala_and_gems(pos, asc_lon, birth_jd, tz)
    rect_reloc = compute_rectification_and_relocation_tools(dt_utc, lat, lon, tz)
    holistic = generate_holistic_reading(pos, asc_lon)
    yogas_eval = evaluate_all_yogas(pos, asc_lon)
    corpus = generate_comprehensive_corpus_reading(pos, asc_lon)
    sign_of_av = {p: int(pos[p]["longitude"] // 30) % 12 for p in VEDIC_PLANETS}
    sign_of_av["Lagna"] = asc_sign
    av_suite = full_ashtakavarga_suite(sign_of_av, pos, asc_lon)
    kp_data = _adv_core.kp_chart(dt_utc, lat, lon)

    yr = target_year or datetime.now(timezone.utc).year
    varsha_data = _adv_core.varshaphal(dt_utc, lat, lon, yr, tz)
    sahams_data = compute_tajika_sahams(pos, asc_lon)
    sahams_list = sahams_data.get("sahams", []) if isinstance(sahams_data, dict) else (sahams_data if isinstance(sahams_data, list) else [])

    lagna_name = SIGNS[asc_sign]
    temp_info = LAGNA_TEMPERAMENT_TREATISE.get(lagna_name, LAGNA_TEMPERAMENT_TREATISE["Aries"])

    # Build structured chapters
    structured_chapters: List[Dict[str, Any]] = []

    # Chapter 1: Birth Panchanga, 17-Item Avakhada & 8-Item Ghata Chakra (IDs 200, 201, 314)
    structured_chapters.append({
        "chapter_number": 1,
        "chapter_code": "201_314",
        "menu_category": "Menu 1 & 2: Birth Chart & Fundamental Calculations",
        "title": "Chapter I — Birth Panchanga, 17-Fold Avakhada Chakra & Ghata Chakra",
        "narrative_paragraphs": [
            f"This PanchangHub Master Horoscope Dossier is prepared for {name} (born {local_from_jd(birth_jd, tz).strftime('%Y-%m-%d %H:%M:%S')}, Latitude {lat:.4f}°, Longitude {lon:.4f}°, Sidereal Lahiri Ayanamsa {ava_ghata['avakhada_chakra']['ayanamsa_dms']}).",
            f"At the moment of birth, the Eastern Horizon (Udaya Lagna) rose at {k['lagna']['dms']} in {k['lagna']['rashi']} ({k['lagna']['sign']}), governed by {k['lagna']['sign_lord']}, within {k['lagna']['nakshatra']} Nakshatra Pada {k['lagna']['pada']}.",
            f"The natal Moon (Janma Rashi) occupies {RASHIS[moon_sign]} ({SIGNS[moon_sign]}) in {NAKSHATRAS[m_ni]} Nakshatra Pada {m_pada}, presided over by {NAKSHATRA_DEITIES[m_ni]} and planetary lord {NAK_LORDS[m_ni % 9]}.",
            ava_ghata["guidance_note"],
        ],
        "tables": {
            "avakhada_chakra": ava_ghata["avakhada_chakra"],
            "ghata_chakra": ava_ghata["ghata_chakra"],
            "planetary_positions": k["planets"],
        },
    })

    # Chapter 2: Nature, Temperament, Shastric vs Modern Appearance, Lucky Points & Nakshatra Pada (IDs 202, 203, 204, 205)
    structured_chapters.append({
        "chapter_number": 2,
        "chapter_code": "202_205",
        "menu_category": "Menu 3: General Interpretations & Nakshatra Treatise",
        "title": f"Chapter II — Ascendant Temperament ({lagna_name}), Lucky Points & {NAKSHATRAS[m_ni]} Pada {m_pada} Deep Dive",
        "narrative_paragraphs": [
            f"Nature & Temperament ({lagna_name} Ascendant): {temp_info['nature']}",
            f"Classical Shastric Portrayal (Brihat Jataka & Saravali): {temp_info['shastric_appearance']}",
            f"Modern Vocational Expression: {temp_info['modern_profile']}",
            f"Birth Nakshatra & Pada Analysis ({NAKSHATRAS[m_ni]} — Pada {m_pada}, Naamakshara '{ava_ghata['avakhada_chakra']['naamakshara_pada_syllable']}'): Ruled by {NAK_LORDS[m_ni % 9]} with Navamsha in {SIGNS[varga_sign(moon_lon, 9)]}, this lunar mansion endows deep emotional perception, dharmic resilience, and the capacity to channel {NAKSHATRA_DEITIES[m_ni]}'s archetype into tangible worldly achievement.",
        ],
        "tables": {
            "lucky_points": {
                "lucky_days": temp_info["lucky_days"],
                "lucky_numbers": temp_info["lucky_numbers"],
                "lucky_colors": temp_info["lucky_colors"],
                "yogi_planet_of_prosperity": upa_sphuta["yogi_avayogi_summary"]["yogi_planet"],
                "sahayogi_supporting_planet": upa_sphuta["yogi_avayogi_summary"]["sahayogi_planet"],
                "avayogi_caution_planet": upa_sphuta["yogi_avayogi_summary"]["avayogi_planet"],
            },
        },
    })

    # Chapter 3: 11 Upagrahas, 15 Mathematical Sphutas, 4 Avastha Systems & Panchadha Maitri (IDs 337, 306, 333, 312)
    structured_chapters.append({
        "chapter_number": 3,
        "chapter_code": "337_306_333",
        "menu_category": "Menu 1 & 2: Upagrahas, Sphutas, Avasthas, Maitri & Shadbala",
        "title": "Chapter III — 11 Upagrahas, 15 Mathematical Sphutas, 4-System Avasthas, Panchadha Maitri & Shadbala",
        "narrative_paragraphs": [
            "Beyond the nine primary Grahas, Brihat Parashara Hora Shastra (Chapters 3, 25, and 45) mandates the computation of the 5 Aprakashika (non-luminous solar) Upagrahas, 6 Kalavela (planetary portion) sub-planets led by Gulika and Mandi, and 15 sensitive mathematical Sphutas.",
            f"In this chart, the supreme Yogi Point falls at {upa_sphuta['yogi_avayogi_summary']['yogi_point_deg']}° ({upa_sphuta['yogi_avayogi_summary']['yogi_sign']} in {upa_sphuta['yogi_avayogi_summary']['yogi_nakshatra']}), making {upa_sphuta['yogi_avayogi_summary']['yogi_planet']} your primary Yogi Graha of prosperity and {upa_sphuta['yogi_avayogi_summary']['sahayogi_planet']} your Sahayogi.",
        ],
        "tables": {
            "upagrahas_11": upa_sphuta["upagrahas"],
            "sphutas_15": upa_sphuta["sphutas"],
            "planetary_avasthas": upa_sphuta["planetary_avasthas"],
            "panchadha_maitri": upa_sphuta["panchadha_maitri_chakra"]["panchadha_compound"],
            "shadbala": k["shadbala"],
            "bhavabala": k["bhavabala"],
        },
    })

    # Chapter 4: 9-Planet Dispositions Treatise — Graha Phala (IDs 207–215)
    graha_narratives = []
    avastha_by_planet = {a["planet"]: a for a in upa_sphuta["planetary_avasthas"]}
    for pl_obj in k["planets"][:9]:
        p_name = pl_obj["name"]
        av_row = avastha_by_planet.get(p_name, {})
        graha_narratives.append(
            f"{p_name} in {pl_obj['rashi']} ({pl_obj['sign']} {pl_obj['dms']}, House {pl_obj['house']}, {pl_obj['nakshatra']} Pada {pl_obj['pada']}, Dignity: {pl_obj['dignity']}): "
            f"Occupies {pl_obj['vargas']['D9']} in Navamsha (D-9) and {pl_obj['vargas']['D10']} in Dashamsha (D-10). "
            f"State of consciousness is {av_row.get('jagradadi_avastha', '')}, age state is {av_row.get('baladi_avastha', '')}, and environmental dignity is {av_row.get('deeptadi_avastha', '')}. "
            f"In Shayanadi Avastha, {p_name} is in {av_row.get('shayanadi_avastha', '')} — {av_row.get('shayanadi_effect', '')}"
        )

    structured_chapters.append({
        "chapter_number": 4,
        "chapter_code": "207_215",
        "menu_category": "Menu 3.4: 9-Planet Dispositions Treatise (Graha Phala)",
        "title": "Chapter IV — Nine-Planet Dispositions Treatise (Graha Phala: Sun through Ketu)",
        "narrative_paragraphs": graha_narratives,
        "tables": {"graha_shadbala_and_dignity": k["planets"][:9]},
    })

    # Chapter 5: 12 House Lords Treatise — Bhavesh Phala (IDs 216–224)
    bhavesh_list = holistic.get("bhavesh_phala_12_lords", [])
    bhavesh_paragraphs = [
        f"Lord of House {b.get('house_ruled', i+1)} ({b.get('sign_on_cusp', '')} — {b.get('lord', '')} placed in House {b.get('placed_in_house', '')} in {b.get('placed_in_sign', '')}): {b.get('interpretation', '')} Classical Sloka Reference: {b.get('classical_reference', 'BPHS Ch. 24')}."
        for i, b in enumerate(bhavesh_list)
    ]
    if not bhavesh_paragraphs:
        for h_num in range(1, 13):
            s_idx = (asc_sign + h_num - 1) % 12
            l_name = SIGN_LORDS[s_idx]
            l_pl = next(p for p in k["planets"] if p["name"] == l_name)
            bhavesh_paragraphs.append(
                f"Lord of the {h_num}th House ({SIGNS[s_idx]}) is {l_name}, positioned in the {l_pl['house']}th House in {l_pl['sign']} ({l_pl['dignity']}), linking the themes of Bhava {h_num} directly with Bhava {l_pl['house']} (BPHS Ch. 24 Bhava-Bhavesha Phala)."
            )

    structured_chapters.append({
        "chapter_number": 5,
        "chapter_code": "216_224",
        "menu_category": "Menu 3.5: 12 House Lords Treatise (Bhavesh Phala)",
        "title": "Chapter V — Twelve House Lords in Houses Treatise (Bhavesh Phala — BPHS Ch. 24)",
        "narrative_paragraphs": bhavesh_paragraphs,
        "tables": {"bhava_chalit": k["bhava_chalit"]},
    })

    # Chapter 6: Classics in English & Categorized Classical Yogas (IDs 802–808, 251)
    detected_yogas = yogas_eval.get("detected_yogas", k["yogas"])
    benefic_yogas = [y for y in detected_yogas if y.get("category", "") not in ("Arishta / Challenge", "Dosha")]
    challenging_yogas = [y for y in detected_yogas if y.get("category", "") in ("Arishta / Challenge", "Dosha")]

    ak_val = k["jaimini"].get("karakas", {}).get("Atmakaraka") or k["jaimini"].get("karakas", {}).get("AK") or "Sun"
    if isinstance(ak_val, dict):
        ak_val = ak_val.get("planet", "Sun")

    structured_chapters.append({
        "chapter_number": 6,
        "chapter_code": "802_808_251",
        "menu_category": "Menu 3.6 & 3.7: Classics in English & Categorized Yogas",
        "title": f"Chapter VI — Classics in English, Jaimini Karakamsha & {len(detected_yogas)} Applicable Classical Yogas",
        "narrative_paragraphs": [
            f"Across Brihat Parashara Hora Shastra, Saravali, Phaladeepika, and Jaimini Sutras, {len(detected_yogas)} classical combinations (Yogas) are active in this nativity ({len(benefic_yogas)} Raja/Dhana/Benefic Yogas and {len(challenging_yogas)} Parivartana/Transformative Yogas).",
            f"Jaimini Atmakaraka (Soul Significator): {ak_val} serves as the King of the Horoscope, guiding the soul's highest dharmic evolution through the Karakamsha.",
        ] + [
            f"• {y.get('name', 'Yoga')} ({y.get('category', 'Classical Yoga')}): {y.get('description', y.get('effects', ''))}"
            for y in detected_yogas[:18]
        ],
        "tables": {
            "benefic_yogas": benefic_yogas,
            "transformative_yogas": challenging_yogas,
            "jaimini_system": k["jaimini"],
            "ashtakavarga_summary": {
                "sarvashtakavarga": k["ashtakavarga"]["sarvashtakavarga"],
                "total_bindus": k["ashtakavarga"]["total"],
                "shodya_pindas": av_suite.get("pindas", {}) if isinstance(av_suite, dict) else {},
            },
        },
    })

    # Chapter 7: All 22 Dasha Systems & Multi-Year Dated Vimshottari Predictions (IDs 315, 701, 345, 361, 363, 369)
    vim_md = all_22_dashas["nakshatra_dashas"]["vimshottari_120y"]["mahadasha"]
    cd_raw = k.get("current_dasha", [])
    if isinstance(cd_raw, list) and cd_raw:
        active_seq_str = " → ".join(f"L{idx+1} {x.get('lord', '')}" for idx, x in enumerate(cd_raw[:3]) if isinstance(x, dict))
    elif isinstance(cd_raw, dict):
        active_seq_str = f"MD {cd_raw.get('mahadasha', {}).get('lord', '')} → AD {cd_raw.get('antardasha', {}).get('lord', '')}"
    else:
        active_seq_str = "Active Vimshottari Cycle"

    dasha_narratives = [
        f"Balance of Vimshottari Dasha at Birth: {all_22_dashas['nakshatra_dashas']['vimshottari_120y']['balance_at_birth']['lord']} Mahadasha ({all_22_dashas['nakshatra_dashas']['vimshottari_120y']['balance_at_birth']['years_remaining']} years remaining).",
        f"Currently Active Vimshottari Sequence: {active_seq_str}.",
    ]
    for md_item in vim_md:
        p_lord = md_item["lord"]
        pl_row = next((p for p in k["planets"] if p["name"] == p_lord), {"sign": "Aries", "house": 1, "dignity": "neutral"})
        dasha_narratives.append(
            f"{p_lord} Mahadasha ({md_item['start']} to {md_item['end']} — {md_item['years']} Years): "
            f"Because natal {p_lord} occupies House {pl_row['house']} in {pl_row['sign']} ({pl_row['dignity']}), this period activates the affairs of House {pl_row['house']} and the houses ruled by {p_lord}. "
            f"Sub-periods (Antardashas) of trine and kendra lords bring peak expansion, while sub-periods of 6th/8th/12th lords call for disciplined consolidation."
        )

    structured_chapters.append({
        "chapter_number": 7,
        "chapter_code": "315_701_ALL22",
        "menu_category": "Menu 4: Complete 22 Dasha Systems & Dated Predictions",
        "title": "Chapter VII — All 22 Dasha Systems & Multi-Year Vimshottari Mahadasha/Antardasha Predictions",
        "narrative_paragraphs": dasha_narratives,
        "tables": {
            "active_dasha_stack": k["current_dasha"],
            "vimshottari_mahadashas": vim_md,
            "all_22_dasha_systems_summary": {
                "nakshatra_systems": list(all_22_dashas["nakshatra_dashas"].keys()),
                "rashi_jaimini_systems": list(all_22_dashas["rashi_and_jaimini_dashas"].keys()),
            },
        },
    })

    # Chapter 8: Saturn Cycles (Sadhesati, Dhayya), Mangala Dosha & Gemstone Propitiation (IDs 386–398)
    gem_life = sat_mangala_gems["gemstone_recommendations"]["life_stone_lagnesh"]
    gem_lucky = sat_mangala_gems["gemstone_recommendations"]["lucky_stone_panchamesh"]
    gem_destiny = sat_mangala_gems["gemstone_recommendations"]["destiny_stone_bhagyesh"]

    structured_chapters.append({
        "chapter_number": 8,
        "chapter_code": "386_398",
        "menu_category": "Menu 8: Saturn Cycles, Mangala Dosha & Ratna Pariksha Gemstones",
        "title": "Chapter VIII — Saturn Sadhesati (3 Lifetime Cycles), Mangala Dosha & Classical Gemstone Protocol",
        "narrative_paragraphs": [
            f"Mangala (Kuja) Dosha Assessment: {sat_mangala_gems['mangala_dosha_analysis']['effective_status']} ({sat_mangala_gems['mangala_dosha_analysis']['triple_chart_score']}). {sat_mangala_gems['mangala_dosha_analysis']['house_effect_narrative']}",
            f"Life Stone (1st Lord — {gem_life['ruling_planet']}): Wear {gem_life['primary_gem']} ({gem_life['weight_carats']}) set in {gem_life['metal']} on the {gem_life['finger']} on {gem_life['day_and_hora']} after reciting '{gem_life['mantra']}'.",
            f"Lucky Stone (5th Lord — {gem_lucky['ruling_planet']}): Wear {gem_lucky['primary_gem']} ({gem_lucky['weight_carats']}) set in {gem_lucky['metal']} on the {gem_lucky['finger']}.",
            f"Destiny Stone (9th Lord — {gem_destiny['ruling_planet']}): Wear {gem_destiny['primary_gem']} ({gem_destiny['weight_carats']}) set in {gem_destiny['metal']} on the {gem_destiny['finger']}.",
        ],
        "tables": sat_mangala_gems,
    })

    # Chapter 9: Varshaphala (Annual Solar Return), KP Stellar Paddhati (KP) & Rectification/Relocation (IDs 401, 334, 901)
    m_raw = varsha_data.get("muntha", "") if isinstance(varsha_data, dict) else ""
    if isinstance(m_raw, dict):
        muntha_str = f"{m_raw.get('sign', '')} (House {m_raw.get('house_from_natal_lagna', m_raw.get('house', ''))})"
    else:
        muntha_str = str(m_raw)
    yr_lord_str = (varsha_data.get("year_lord") or varsha_data.get("varsheshwara") or "Sun") if isinstance(varsha_data, dict) else "Sun"

    structured_chapters.append({
        "chapter_number": 9,
        "chapter_code": "401_334_901",
        "menu_category": "Menu 5, 7 & 9: Varshaphala, KP Significators, Astronomy & Rectification Tools",
        "title": f"Chapter IX — Annual Solar Return ({yr} Varshaphala), KP Significators & Birth Time Rectification",
        "narrative_paragraphs": [
            f"Annual Varshaphala ({yr} Tajika Solar Return): Muntha falls in {muntha_str}, and the Varsheshwara (Year Lord) is {yr_lord_str}.",
            f"Birth Time Rectification Check: {rect_reloc['birth_time_rectification']['kunda_verification']['rule']} Current Kunda Sign is {rect_reloc['birth_time_rectification']['kunda_verification']['kunda_sign']} (House {rect_reloc['birth_time_rectification']['kunda_verification']['house_from_moon']} from Moon).",
            f"Panch Pakshi Bio-Rhythm: Your birth Pakshi is {rect_reloc['panch_pakshi_biorhythm']['birth_pakshi_bird']} in the '{rect_reloc['panch_pakshi_biorhythm']['natal_activity_state']}' state ({rect_reloc['panch_pakshi_biorhythm']['interpretation']}).",
        ],
        "tables": {
            "varshaphala_summary": varsha_data,
            "tajika_sahams_top12": sahams_list[:12],
            "kp_cusps": kp_data.get("cusps", []),
            "rectification_and_relocation": rect_reloc,
            "astronomical_profiles": ASTRONOMICAL_PROFILES,
        },
    })

    # Build clean, print-ready Book-Style HTML Dossier (100% original PanchangHub styling)
    html_parts = [
        f'<div class="ph-book-dossier" data-model="{model_meta["code"]}">',
        f'  <header class="ph-book-cover">',
        f'    <div class="ph-book-badge">PANCHANGHUB CLASSICAL JYOTISH ARCHIVE &bull; MODEL {model_meta["code"]}</div>',
        f'    <h1 class="ph-book-title">{model_meta["title"]}</h1>',
        f'    <p class="ph-book-subtitle">Prepared for <strong>{name}</strong> &bull; {local_from_jd(birth_jd, tz).strftime("%B %d, %Y at %H:%M:%S")} &bull; Lagna: {k["lagna"]["rashi"]} ({k["lagna"]["sign"]}) &bull; Moon: {RASHIS[moon_sign]} ({NAKSHATRAS[m_ni]} Pada {m_pada})</p>',
        f'  </header>',
    ]
    for ch in structured_chapters:
        html_parts.append(f'  <section class="ph-book-chapter" id="chapter-{ch["chapter_number"]}">')
        html_parts.append(f'    <div class="ph-chapter-kicker">{ch["menu_category"]}</div>')
        html_parts.append(f'    <h2 class="ph-chapter-heading">{ch["title"]}</h2>')
        for para in ch["narrative_paragraphs"]:
            html_parts.append(f'    <p class="ph-chapter-para">{para}</p>')
        html_parts.append(f'  </section>')
    html_parts.append('</div>')

    return {
        "schema_version": "2026.10.27",
        "brand": "PanchangHub Classical Jyotish Engine",
        "model_selected": model_meta,
        "native_summary": {
            "name": name,
            "gender": gender,
            "datetime_local": local_from_jd(birth_jd, tz).isoformat(),
            "latitude": lat,
            "longitude": lon,
            "ayanamsa_deg": ava_ghata["avakhada_chakra"]["ayanamsa_deg"],
            "lagna": k["lagna"],
            "moon": k["moon"],
            "naamakshara_syllable": ava_ghata["avakhada_chakra"]["naamakshara_pada_syllable"],
            "yogi_planet": upa_sphuta["yogi_avayogi_summary"]["yogi_planet"],
            "avayogi_planet": upa_sphuta["yogi_avayogi_summary"]["avayogi_planet"],
        },
        "chapters_count": len(structured_chapters),
        "chapters": structured_chapters,
        "complete_calculations": {
            "avakhada_and_ghata": ava_ghata,
            "upagrahas_sphutas_avasthas_maitri": upa_sphuta,
            "all_22_dasha_systems": all_22_dashas,
            "saturn_cycles_mangala_and_gems": sat_mangala_gems,
            "rectification_and_relocation": rect_reloc,
        },
        "printable_book_html": "\n".join(html_parts),
    }

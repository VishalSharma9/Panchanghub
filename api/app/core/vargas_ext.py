"""Comprehensive 31 Divisional Charts (Shodashavargas + Tajika/Nadi + Seshadhri Iyer) Engine.

Architected to match the complete classical Parashara and Tajika/Nadi/Iyer canon:
1. All 16 Parashara Shodashavargas (D1 to D60)
2. All 5 Tajika and Nadi Vargas (D5, D6, D8, D11, D150)
3. All 10 Seshadhri Iyer Harmonic Vargas (Hora Iyer, Hora III, D3..D30 Iyer)

Computes exact sign placements, internal degrees, houses from varga lagna,
dignities, deities (including 150 Deva Keralam Nadi deities and 60 Shastiamsa deities),
and Vargottama classifications.
"""
from __future__ import annotations
import math
from typing import Dict, List, Any, Union
from .ephem import SIGNS, RASHIS, SIGN_LORDS
from .kundli import dignity, relation, EXALT, OWN, MOOLA, FRIENDS
from .tajika_sahams import get_nadiamsha, get_drekkana_body_part

# Master 31 Classical Divisional Chart definitions (Brihat Parashara Hora Shastra, Tajika, Nadi & Seshadhri Iyer)
ALL_VARGAS: Dict[str, Dict[str, Any]] = {
    # === 1. PARASHARA SHODASHAVARGAS (16 Charts) ===
    "D1": {"code": "D1", "name": "Janma (all areas of life)", "short": "Rashi", "system": "Parashara", "division": 1, "domain": "Physical constitution, vitality and general destiny", "sanskrit": "जन्म (D1)"},
    "D2": {"code": "D2", "name": "Hora (wealth)", "short": "Hora", "system": "Parashara", "division": 2, "domain": "Wealth, liquid assets, speech tone and treasury", "sanskrit": "होरा (D2)"},
    "D3": {"code": "D3", "name": "Dreshkana (happiness siblings)", "short": "Drekkana", "system": "Parashara", "division": 3, "domain": "Siblings, courage, vitality, initiative and physical prowess", "sanskrit": "द्रेष्काण (D3)"},
    "D4": {"code": "D4", "name": "Chaturthamsha (destiny)", "short": "Chaturthamsa", "system": "Parashara", "division": 4, "domain": "Destiny, fixed property, real estate, conveyances and domestic peace", "sanskrit": "चतुर्थांश (D4)"},
    "D7": {"code": "D7", "name": "Saptamsha (children)", "short": "Saptamsa", "system": "Parashara", "division": 7, "domain": "Children, progeny, creative legacy and grandchildren", "sanskrit": "सप्तांश (D7)"},
    "D9": {"code": "D9", "name": "Navamsha (spouse)", "short": "Navamsa", "system": "Parashara", "division": 9, "domain": "Spouse, marriage, dharma, soul blueprint and inner potential", "sanskrit": "नवांश (D9)"},
    "D10": {"code": "D10", "name": "Dashamsha (great successes)", "short": "Dasamsa", "system": "Parashara", "division": 10, "domain": "Career eminence, public authority, professional status and leadership (Mahat Phala)", "sanskrit": "दशांश (D10)"},
    "D12": {"code": "D12", "name": "Dwadashamsha (parents)", "short": "Dwadasamsa", "system": "Parashara", "division": 12, "domain": "Parents, ancestral roots, genetic inheritance and past-life merits", "sanskrit": "द्वादशांश (D12)"},
    "D16": {"code": "D16", "name": "Shodashamsha (conveyances)", "short": "Shodasamsa", "system": "Parashara", "division": 16, "domain": "Vehicles, conveyances, luxuries and contentment", "sanskrit": "षोडशांश (D16)"},
    "D20": {"code": "D20", "name": "Vimshamsha (spiritual progress)", "short": "Vimsamsa", "system": "Parashara", "division": 20, "domain": "Spiritual progress, devotion, mantra siddhi and higher sadhana", "sanskrit": "विंशांश (D20)"},
    "D24": {"code": "D24", "name": "Chaturvimshamsha (knowledge)", "short": "Chaturvimsamsa", "system": "Parashara", "division": 24, "domain": "Knowledge, scholarship, intellectual discrimination and higher education", "sanskrit": "चतुर्विंशांश (D24)"},
    "D27": {"code": "D27", "name": "Saptavimshamsha (strength)", "short": "Saptavimsamsa", "system": "Parashara", "division": 27, "domain": "Subconscious strengths, physical vitality and resilience", "sanskrit": "सप्तविंशांश (D27)"},
    "D30": {"code": "D30", "name": "Trimshamsha (misfortunes)", "short": "Trimsamsa", "system": "Parashara", "division": 30, "domain": "Misfortunes, karmic obstacles, moral strength and acute trials", "sanskrit": "त्रिंशांश (D30)"},
    "D40": {"code": "D40", "name": "Khavedamsha (Ausp.Inausp.effects)", "short": "Khavedamsa", "system": "Parashara", "division": 40, "domain": "Auspicious & inauspicious portents, maternal ancestral merits", "sanskrit": "खवेदांश (D40)"},
    "D45": {"code": "D45", "name": "Akshavedamsha (All areas)", "short": "Akshavedamsa", "system": "Parashara", "division": 45, "domain": "Character purity, moral integrity and holistic karmic indications", "sanskrit": "अक्षवेदांश (D45)"},
    "D60": {"code": "D60", "name": "Shashtiamsha (All areas)", "short": "Shastiamsa", "system": "Parashara", "division": 60, "domain": "Past life karma and fine destiny (Sarvam Shashtiamshe)", "sanskrit": "षष्ट्यंश (D60)"},

    # === 2. TAJIKA & NADI VARGAS (5 Charts) ===
    "D5": {"code": "D5", "name": "Panchamsha 1/5 -", "short": "Panchamsha", "system": "Tajika/Nadi", "division": 5, "domain": "Fame, intellectual power, prowess, spiritual sadhana and creativity", "sanskrit": "पञ्चांश 1/5 (D5)"},
    "D6": {"code": "D6", "name": "Shashtamsha 1/6 Disease", "short": "Shashtamsha", "system": "Tajika/Nadi", "division": 6, "domain": "Disease, health vulnerability, litigations, debts and rivals", "sanskrit": "षष्ठांश 1/6 (D6)"},
    "D8": {"code": "D8", "name": "Ashtamsha 1/8 Accidents", "short": "Ashtamsha", "system": "Tajika/Nadi", "division": 8, "domain": "Accidents, chronic hazards, longevity, occult and unexpected transformations", "sanskrit": "अष्टांश 1/8 (D8)"},
    "D11": {"code": "D11", "name": "Ekadashamsha 1/11 Cure", "short": "Ekadashamsha", "system": "Tajika/Nadi", "division": 11, "domain": "Cure from diseases, financial gains, victory over obstacles and labha", "sanskrit": "एकादशांश 1/11 (D11)"},
    "D150": {"code": "D150", "name": "Nadiamsha 1/150 -", "short": "Nadiamsha", "system": "Tajika/Nadi", "division": 150, "domain": "Chandra Kala Nadi (Deva Keralam) micro-karmic destiny (12' arc)", "sanskrit": "नाड्यंश 1/150 (D150)"},

    # === 3. SESHADHRI IYER SYSTEM VARGAS (10 Charts) ===
    "D2_IYER": {"code": "D2_IYER", "name": "Hora Iyer (wealth)", "short": "Hora Iyer", "system": "Iyer", "division": 2, "domain": "Wealth & financial polarity (1st half sign, 2nd half 7th opposite sign)", "sanskrit": "होरा अय्यर (D2-Iyer)"},
    "D2_IYER3": {"code": "D2_IYER3", "name": "Hora III (7,1,2) (wealth)", "short": "Hora III", "system": "Iyer", "division": 2, "domain": "Wealth (Movable starts from 7th, Fixed from 1st, Dual from 2nd)", "sanskrit": "होरा III (7,1,2)"},
    "D3_IYER": {"code": "D3_IYER", "name": "Dreshkana Iyer (happiness siblings)", "short": "Drekkana Iyer", "system": "Iyer", "division": 3, "domain": "Happiness siblings (3 decanates cyclic from sign)", "sanskrit": "द्रेष्काण अय्यर (D3-Iyer)"},
    "D4_IYER": {"code": "D4_IYER", "name": "Chaturthamsha Iyer (destiny)", "short": "Chaturthamsa Iyer", "system": "Iyer", "division": 4, "domain": "Destiny & property (4 parts cyclic from sign)", "sanskrit": "चतुर्थांश अय्यर (D4-Iyer)"},
    "D10_IYER": {"code": "D10_IYER", "name": "Dashamsha Iyer (great successes)", "short": "Dasamsa Iyer", "system": "Iyer", "division": 10, "domain": "Great successes & career (10 parts cyclic)", "sanskrit": "दशांश अय्यर (D10-Iyer)"},
    "D12_IYER": {"code": "D12_IYER", "name": "Dwadashamsha Iyer (parents)", "short": "Dwadasamsa Iyer", "system": "Iyer", "division": 12, "domain": "Parents & lineage (12 parts cyclic from sign)", "sanskrit": "द्वादशांश अय्यर (D12-Iyer)"},
    "D30_IYER": {"code": "D30_IYER", "name": "Trimshamsha Iyer (misfortunes)", "short": "Trimsamsa Iyer", "system": "Iyer", "division": 30, "domain": "Misfortunes & challenges (30 equal 1° divisions cyclic)", "sanskrit": "त्रिंशांश अय्यर (D30-Iyer)"},
    "D5_IYER": {"code": "D5_IYER", "name": "Panchamsha 1/5 Iyer -", "short": "Panchamsha Iyer", "system": "Iyer", "division": 5, "domain": "Intellectual fame & learning (5 parts cyclic from sign)", "sanskrit": "पञ्चांश अय्यर (D5-Iyer)"},
    "D16_IYER": {"code": "D16_IYER", "name": "Shodashamsha Iyer (conveyances)", "short": "Shodasamsa Iyer", "system": "Iyer", "division": 16, "domain": "Conveyances & comforts (16 parts cyclic from sign)", "sanskrit": "षोडशांश अय्यर (D16-Iyer)"},
    "D11_IYER": {"code": "D11_IYER", "name": "Ekadashamsha 1/11 Iyer Cure", "short": "Ekadashamsha Iyer", "system": "Iyer", "division": 11, "domain": "Cure from disease & gains (11 parts cyclic from sign)", "sanskrit": "एकादशांश अय्यर (D11-Iyer)"},
}

# Backward compatible dictionary with division integers
VARGA_INFO = {v["division"]: {"name": v["short"], "division": v["division"], "domain": v["domain"], "sanskrit": v["code"]} for k, v in ALL_VARGAS.items() if v["system"] == "Parashara"}

# Classical 60 Shastiamsa Deities (Parashara Hora Shastra)
SHASTIAMSA_DEITIES = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulaghna",
    "Garala", "Vahni", "Maya", "Purishaka", "Apampathi", "Marutwan", "Kaala", "Sarpa",
    "Amrita", "Indu", "Mridu", "Komala", "Heramba", "Brahma", "Vishnu", "Maheshwara",
    "Deva", "Aardra", "Kalinasa", "Kshiteesa", "Kamalakara", "Gulika", "Mrityu", "Kaala",
    "Daavagni", "Ghora", "Yama", "Kantaka", "Suddha", "Amrita", "Poornachandra", "Vishadagdha",
    "Kulanasa", "Vamshakshaya", "Utpata", "Kaalarupa", "Saumya", "Dhumraketu", "Kulaanta",
    "Bhasitaka", "Yama", "Varuna", "Indra", "Pravina", "Kaalagni", "Dandabhritha", "Nirmala",
    "Subha", "Asubha", "Atisita", "Sudha", "Pramodana"
]

# Drekkana Deities: 0: Narada (Deva), 1: Agastya (Manushya), 2: Durvasa (Rakshasa)
DREKKANA_DEITIES = ["Narada", "Agastya", "Durvasa"]

def compute_varga_position(lon: float, v_code: Union[int, str]) -> tuple[int, float]:
    """Calculates both the varga sign index (0-11) and the degree within the varga sign (0.0-30.0).
    Supports all 31 Divisional charts: Parashara Shodashavargas, Tajika/Nadi Vargas, and Seshadhri Iyer Vargas.
    """
    lon = lon % 360.0
    sign = int(lon // 30) % 12
    deg = lon % 30.0
    is_odd = (sign % 2 == 0)  # Aries = 0 is odd
    modality = sign % 3       # 0 Movable, 1 Fixed, 2 Dual

    # Normalize code
    code = f"D{v_code}" if isinstance(v_code, int) else str(v_code).upper()

    # --- SESHADHRI IYER HARMONIC VARGAS ---
    if code == "D2_IYER":
        # Hora Iyer: 1st half sign itself, 2nd half opposite 7th sign
        v_sign = sign if deg < 15.0 else (sign + 6) % 12
        v_deg = (deg % 15.0) * 2.0
        return v_sign, v_deg

    elif code == "D2_IYER3":
        # Hora III (7,1,2): Movable from 7th, Fixed from 1st, Dual from 2nd
        start = (sign + 6) % 12 if modality == 0 else (sign if modality == 1 else (sign + 1) % 12)
        part = 0 if deg < 15.0 else 1
        v_sign = (start + part) % 12
        v_deg = (deg % 15.0) * 2.0
        return v_sign, v_deg

    elif code == "D3_IYER":
        part = int(deg // 10.0)
        v_sign = (sign + part) % 12
        v_deg = (deg % 10.0) * 3.0
        return v_sign, v_deg

    elif code == "D4_IYER":
        part = int(deg // 7.5)
        v_sign = (sign + part) % 12
        v_deg = (deg % 7.5) * 4.0
        return v_sign, v_deg

    elif code == "D5_IYER":
        part = int(deg // 6.0)
        v_sign = (sign + part) % 12
        v_deg = (deg % 6.0) * 5.0
        return v_sign, v_deg

    elif code == "D10_IYER":
        part = int(deg // 3.0)
        start = sign if modality == 0 else ((sign + 8) % 12 if modality == 1 else (sign + 4) % 12)
        v_sign = (start + part) % 12
        v_deg = (deg % 3.0) * 10.0
        return v_sign, v_deg

    elif code == "D11_IYER":
        part = int(deg // (30.0 / 11))
        v_sign = (sign + part) % 12
        v_deg = (deg % (30.0 / 11)) * 11.0
        return v_sign, v_deg

    elif code == "D12_IYER":
        part = int(deg // 2.5)
        v_sign = (sign + part) % 12
        v_deg = (deg % 2.5) * 12.0
        return v_sign, v_deg

    elif code == "D16_IYER":
        part = int(deg // 1.875)
        v_sign = (sign + part) % 12
        v_deg = (deg % 1.875) * 16.0
        return v_sign, v_deg

    elif code == "D30_IYER":
        part = int(deg // 1.0)
        v_sign = (sign + part) % 12
        v_deg = (deg % 1.0) * 30.0
        return v_sign, v_deg

    # --- TAJIKA & NADI VARGAS ---
    elif code == "D5":
        part = int(deg // 6.0)
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        v_sign = (start + part) % 12
        v_deg = (deg % 6.0) * 5.0
        return v_sign, v_deg

    elif code == "D6":
        part = int(deg // 5.0)
        start = 0 if is_odd else 6
        v_sign = (start + part) % 12
        v_deg = (deg % 5.0) * 6.0
        return v_sign, v_deg

    elif code == "D8":
        part = int(deg // 3.75)
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        v_sign = (start + part) % 12
        v_deg = (deg % 3.75) * 8.0
        return v_sign, v_deg

    elif code == "D11":
        part = int(deg // (30.0 / 11))
        v_sign = (0 + part) % 12 if is_odd else (11 - part) % 12
        v_deg = (deg % (30.0 / 11)) * 11.0
        return v_sign, v_deg

    elif code == "D150":
        part = int(deg // 0.2)
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        v_sign = (start + (part % 12)) % 12
        v_deg = (deg % 0.2) * 150.0
        return v_sign, v_deg

    # --- PARASHARA SHODASHAVARGAS ---
    if code in ("D1", "1"):
        return sign, deg

    elif code in ("D2", "2"):  # Hora (15° halves)
        v_sign = (4 if deg < 15 else 3) if is_odd else (3 if deg < 15 else 4)
        v_deg = (deg % 15.0) * 2.0
        return v_sign, v_deg

    elif code in ("D3", "3"):  # Drekkana (10° thirds)
        part = int(deg // 10.0)
        v_sign = (sign + 4 * part) % 12
        v_deg = (deg - part * 10.0) * 3.0
        return v_sign, v_deg

    elif code in ("D4", "4"):  # Chaturthamsa (7°30' quarters)
        part = int(deg // 7.5)
        v_sign = (sign + 3 * part) % 12
        v_deg = (deg - part * 7.5) * 4.0
        return v_sign, v_deg

    elif code in ("D7", "7"):  # Saptamsa (4°17' sevenths)
        part = int(deg // (30.0 / 7))
        start = sign if is_odd else (sign + 6)
        v_sign = (start + part) % 12
        v_deg = (deg - part * (30.0 / 7)) * 7.0
        return v_sign, v_deg

    elif code in ("D9", "9"):  # Navamsa (3°20' ninths)
        total_part = int(lon // (30.0 / 9))
        v_sign = total_part % 12
        v_deg = (deg % (30.0 / 9)) * 9.0
        return v_sign, v_deg

    elif code in ("D10", "10"):  # Dasamsa (3° tenths)
        part = int(deg // 3.0)
        start = sign if is_odd else (sign + 8)
        v_sign = (start + part) % 12
        v_deg = (deg - part * 3.0) * 10.0
        return v_sign, v_deg

    elif code in ("D12", "12"):  # Dwadasamsa (2°30' twelfths)
        part = int(deg // 2.5)
        v_sign = (sign + part) % 12
        v_deg = (deg - part * 2.5) * 12.0
        return v_sign, v_deg

    elif code in ("D16", "16"):  # Shodasamsa (1°52'30" sixteenths)
        part = int(deg // 1.875)
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        v_sign = (start + part) % 12
        v_deg = (deg - part * 1.875) * 16.0
        return v_sign, v_deg

    elif code in ("D20", "20"):  # Vimsamsa (1°30' twentieths)
        part = int(deg // 1.5)
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        v_sign = (start + part) % 12
        v_deg = (deg - part * 1.5) * 20.0
        return v_sign, v_deg

    elif code in ("D24", "24"):  # Chaturvimsamsa (1°15' twenty-fourths)
        part = int(deg // 1.25)
        start = 4 if is_odd else 3
        v_sign = (start + part) % 12
        v_deg = (deg - part * 1.25) * 24.0
        return v_sign, v_deg

    elif code in ("D27", "27"):  # Saptavimsamsa / Bhamsa
        part = int(deg // (30.0 / 27))
        start = [0, 3, 6, 9][sign % 4]
        v_sign = (start + part) % 12
        v_deg = (deg - part * (30.0 / 27)) * 27.0
        return v_sign, v_deg

    elif code in ("D30", "30"):  # Trimsamsa (Unequal degrees)
        if is_odd:
            if deg < 5:      v_sign, v_deg = 0, (deg / 5.0) * 30.0       # Mars (Aries)
            elif deg < 10:   v_sign, v_deg = 10, ((deg - 5) / 5.0) * 30.0   # Saturn (Aquarius)
            elif deg < 18:   v_sign, v_deg = 8, ((deg - 10) / 8.0) * 30.0   # Jupiter (Sagittarius)
            elif deg < 25:   v_sign, v_deg = 2, ((deg - 18) / 7.0) * 30.0   # Mercury (Gemini)
            else:            v_sign, v_deg = 1, ((deg - 25) / 5.0) * 30.0   # Venus (Taurus)
        else:
            if deg < 5:      v_sign, v_deg = 1, (deg / 5.0) * 30.0       # Venus (Taurus)
            elif deg < 12:   v_sign, v_deg = 5, ((deg - 5) / 7.0) * 30.0   # Mercury (Virgo)
            elif deg < 20:   v_sign, v_deg = 11, ((deg - 12) / 8.0) * 30.0 # Jupiter (Pisces)
            elif deg < 25:   v_sign, v_deg = 9, ((deg - 20) / 5.0) * 30.0  # Saturn (Capricorn)
            else:            v_sign, v_deg = 7, ((deg - 25) / 5.0) * 30.0  # Mars (Scorpio)
        return v_sign, v_deg

    elif code in ("D40", "40"):  # Khavedamsa (45' fortieths)
        part = int(deg // 0.75)
        start = 0 if is_odd else 6
        v_sign = (start + part) % 12
        v_deg = (deg - part * 0.75) * 40.0
        return v_sign, v_deg

    elif code in ("D45", "45"):  # Akshavedamsa (40' forty-fifths)
        part = int(deg // (30.0 / 45))
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        v_sign = (start + part) % 12
        v_deg = (deg - part * (30.0 / 45)) * 45.0
        return v_sign, v_deg

    elif code in ("D60", "60"):  # Shastiamsa (30' sixtieths)
        part = int(deg // 0.5)
        v_sign = (sign + part) % 12
        v_deg = (deg - part * 0.5) * 60.0
        return v_sign, v_deg

    raise ValueError(f"Unsupported varga division: {v_code}")

def format_dms(deg: float) -> str:
    d = int(deg)
    rem = (deg - d) * 60.0
    m = int(rem)
    s = round((rem - m) * 60.0, 1)
    return f"{d:02d}° {m:02d}' {s:04.1f}\""

def build_all_vargas(pos: Dict[str, Any], asc_lon: float) -> Dict[str, Any]:
    """Generates the full suite of all 31 Divisional Charts (Parashara, Tajika/Nadi, and Iyer)."""
    planets_list = [p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"] if p in pos]

    # Track signs across vargas for Vargottama and multi-varga strength calculation
    varga_signs_per_planet: Dict[str, Dict[str, int]] = {p: {} for p in planets_list}
    varga_signs_asc: Dict[str, int] = {}

    vargas_out: Dict[str, Any] = {}

    for vk, info in ALL_VARGAS.items():
        v_asc_sign, v_asc_deg = compute_varga_position(asc_lon, vk)
        varga_signs_asc[vk] = v_asc_sign

        bodies = []
        for p in planets_list:
            p_lon = pos[p]["longitude"]
            v_sign, v_deg = compute_varga_position(p_lon, vk)
            varga_signs_per_planet[p][vk] = v_sign

            # Calculate house from varga ascendant
            house_in_varga = (v_sign - v_asc_sign) % 12 + 1

            # Determine dignity in this varga
            v_dig = dignity(p, v_sign * 30.0 + v_deg)

            entry: Dict[str, Any] = {
                "name": p,
                "sign": v_sign,
                "sign_name": SIGNS[v_sign],
                "rashi": RASHIS[v_sign],
                "sign_lord": SIGN_LORDS[v_sign],
                "degree": round(v_deg, 4),
                "dms": format_dms(v_deg),
                "house": house_in_varga,
                "dignity": v_dig,
                "retrograde": pos[p].get("retrograde", False),
            }

            # Add specific deities/anatomies for D3, D60, and D150
            if vk == "D3":
                drekkana_idx = int((p_lon % 30.0) // 10.0) % 3
                entry["deity"] = DREKKANA_DEITIES[drekkana_idx]
            elif vk == "D60":
                shastiamsa_idx = int((p_lon % 30.0) // 0.5) % 60
                entry["deity"] = SHASTIAMSA_DEITIES[shastiamsa_idx]
            elif vk == "D150":
                nadi_info = get_nadiamsha(p_lon)
                entry["deity"] = nadi_info["deity"]

            bodies.append(entry)

        vargas_out[vk] = {
            "varga": vk,
            "name": info["name"],
            "short_name": info["short"],
            "sanskrit": info["sanskrit"],
            "system": info["system"],
            "division": info["division"],
            "domain": info["domain"],
            "ascendant": {
                "sign": v_asc_sign,
                "sign_name": SIGNS[v_asc_sign],
                "rashi": RASHIS[v_asc_sign],
                "sign_lord": SIGN_LORDS[v_asc_sign],
                "degree": round(v_asc_deg, 4),
                "dms": format_dms(v_asc_deg),
            },
            "planets": bodies,
        }

        if vk == "D150":
            asc_nadi = get_nadiamsha(asc_lon)
            vargas_out[vk]["ascendant"]["nadi_deity"] = asc_nadi["deity"]
            vargas_out[vk]["ascendant"]["nadi_number"] = asc_nadi["nadiamsha_number"]
            vargas_out[vk]["ascendant"]["nadi_span"] = asc_nadi["degree_span"]

    # Evaluate Vargottama (same sign in D1 and D9)
    vargottama_planets = []
    if varga_signs_asc.get("D1") == varga_signs_asc.get("D9"):
        vargottama_planets.append({"planet": "Ascendant", "sign": SIGNS[varga_signs_asc["D1"]], "type": "Ascendant Vargottama"})

    for p in planets_list:
        d1_s = varga_signs_per_planet[p].get("D1")
        d9_s = varga_signs_per_planet[p].get("D9")
        if d1_s is not None and d1_s == d9_s:
            vargottama_planets.append({"planet": p, "sign": SIGNS[d1_s], "rashi": RASHIS[d1_s], "type": "Navamsa Vargottama"})

    # Classical multi-varga strength grades (Shadvarga / Saptavarga / Dasavarga / Shodashavarga auspicious divisions)
    varga_strengths = {}
    shodasha_keys = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
    grade_names = {
        2: "Bhedaka", 3: "Vyanjana", 4: "Kimsuka", 5: "Vyanjana", 6: "Kimsuka",
        7: "Gopura", 8: "Simhasana", 9: "Paravata", 10: "Devaloka", 11: "Kairavali",
        12: "Iravata", 13: "Vaiseshikamsa", 14: "Kalanidhi", 15: "Mandara", 16: "Sri Vallabha"
    }

    for p in planets_list:
        good_count = 0
        for vn in shodasha_keys:
            v_sign = varga_signs_per_planet[p].get(vn, 0)
            if p in EXALT and EXALT[p] == v_sign:
                good_count += 1
            elif p in MOOLA and MOOLA[p] == v_sign:
                good_count += 1
            elif p in OWN and v_sign in OWN[p]:
                good_count += 1
        grade = grade_names.get(good_count, "Normal" if good_count < 2 else f"{good_count} Dignified Vargas")
        varga_strengths[p] = {"dignified_varga_count": good_count, "grade": grade}

    return {
        "vargas": vargas_out,
        "vargottama": vargottama_planets,
        "varga_strengths": varga_strengths,
    }

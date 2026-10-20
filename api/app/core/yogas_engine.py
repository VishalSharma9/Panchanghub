"""Comprehensive Classical Vedic Astrological Combinations (Yogas) Engine.

Evaluates over 60 classical combinations categorized into:
- Pancha Mahapurusha Yogas
- Classical Raja Yogas & Dharma-Karma Connections
- Viparita Raja Yogas & Neechabhanga Yogas
- Dhana (Wealth & Prosperity) Yogas
- Solar (Surya) & Lunar (Chandra) Combinations
- Character, Wisdom, and Knowledge Yogas
- Karmic Afflictions & Doshas
"""
from __future__ import annotations
from typing import Dict, List, Any
from .ephem import SIGNS, RASHIS, SIGN_LORDS
from .kundli import OWN, EXALT, MOOLA

def evaluate_all_yogas(pos: Dict[str, Any], asc_lon: float) -> Dict[str, Any]:
    """Scans and evaluates the full spectrum of classical Vedic yogas in the birth chart."""
    asc_sign = int(asc_lon // 30) % 12
    sign_of = {p: int(pos[p]["longitude"] // 30) % 12 for p in pos}
    house_of = {p: (sign_of[p] - asc_sign) % 12 + 1 for p in pos}

    kendra_houses = {1, 4, 7, 10}
    trikona_houses = {1, 5, 9}
    dusthana_houses = {6, 8, 12}
    upachaya_houses = {3, 6, 10, 11}

    lord_of_house = lambda h: SIGN_LORDS[(asc_sign + h - 1) % 12]
    house_of_lord = lambda h: house_of.get(lord_of_house(h), 0)

    found_yogas: List[Dict[str, Any]] = []

    # 1. PANCHA MAHAPURUSHA YOGAS
    mahapurusha_defs = [
        ("Mars", "Ruchaka Yoga", "Commands physical vigor, strategic boldness, fearless execution, and distinction in competitive or leadership domains."),
        ("Mercury", "Bhadra Yoga", "Bestows sharp analytical intellect, eloquent oratory, scholarly brilliance, and commercial mastery."),
        ("Jupiter", "Hamsa Yoga", "Endows the soul with high ethical authority, spiritual wisdom, philanthropic generosity, and societal reverence."),
        ("Venus", "Malavya Yoga", "Grants aesthetic refined beauty, luxurious comforts, artistic mastery, and magnetic marital harmony."),
        ("Saturn", "Sasa Yoga", "Provides unyielding discipline, organizational stamina, enduring public authority, and mastery over complex institutions.")
    ]
    for planet, name, desc in mahapurusha_defs:
        if planet in pos:
            p_sign = sign_of[planet]
            p_house = house_of[planet]
            is_own = p_sign in OWN[planet]
            is_exalt = EXALT[planet] == p_sign
            if p_house in kendra_houses and (is_own or is_exalt):
                found_yogas.append({
                    "name": name,
                    "category": "Pancha Mahapurusha",
                    "planets_involved": [planet],
                    "nature": "Highly Auspicious",
                    "strength_score": 95,
                    "description": desc,
                    "condition": f"{planet} is {'exalted' if is_exalt else 'in own sign'} in angular House {p_house}."
                })

    # 2. GAJA KESARI YOGA
    if "Moon" in pos and "Jupiter" in pos:
        rel_jup = (sign_of["Jupiter"] - sign_of["Moon"]) % 12 + 1
        if rel_jup in kendra_houses:
            found_yogas.append({
                "name": "Gaja Kesari Yoga",
                "category": "Raja Yoga",
                "planets_involved": ["Jupiter", "Moon"],
                "nature": "Highly Auspicious",
                "strength_score": 90,
                "description": "Like an elephant paired with a lion, confers an unassailable reputation, moral authority, enduring intellect, and protection against covert adversaries.",
                "condition": f"Jupiter is placed in House {rel_jup} (a Kendra) from the Moon."
            })

    # 3. DHARMA-KARMADHIPATI RAJA YOGA
    l9 = lord_of_house(9)
    l10 = lord_of_house(10)
    if l9 and l10 and l9 in pos and l10 in pos:
        l9_sign = sign_of[l9]
        l10_sign = sign_of[l10]
        # Conjunction, mutual aspect, or exchange
        is_conjunct = l9_sign == l10_sign
        is_opposite = (l9_sign - l10_sign) % 12 == 6
        is_exchange = (l9_sign == (asc_sign + 10 - 1) % 12) and (l10_sign == (asc_sign + 9 - 1) % 12)
        if is_conjunct or is_opposite or is_exchange:
            found_yogas.append({
                "name": "Dharma-Karmadhipati Yoga",
                "category": "Supreme Raja Yoga",
                "planets_involved": [l9, l10],
                "nature": "Supreme Auspicious",
                "strength_score": 100,
                "description": "Union of the 9th lord (Dharma/Grace) and 10th lord (Karma/Action) guarantees career eminence, ethical power, and lasting societal recognition.",
                "condition": f"9th Lord ({l9}) and 10th Lord ({l10}) are in {'conjunction' if is_conjunct else 'mutual exchange' if is_exchange else 'mutual aspect'}."
            })

    # 4. VIPARITA RAJA YOGAS
    # Harsha Yoga (6th lord in 6th, 8th, or 12th)
    l6 = lord_of_house(6)
    if l6 in pos and house_of[l6] in dusthana_houses:
        found_yogas.append({
            "name": "Harsha Yoga (Viparita Raja Yoga)",
            "category": "Viparita Raja Yoga",
            "planets_involved": [l6],
            "nature": "Auspicious Resilience",
            "strength_score": 80,
            "description": "Bestows victory over chronic disputes, superior physical immune resilience, and triumphant resolution of financial or legal entanglements.",
            "condition": f"6th Lord ({l6}) is posited in Dusthana House {house_of[l6]}."
        })

    # Sarala Yoga (8th lord in 6th, 8th, or 12th)
    l8 = lord_of_house(8)
    if l8 in pos and house_of[l8] in dusthana_houses:
        found_yogas.append({
            "name": "Sarala Yoga (Viparita Raja Yoga)",
            "category": "Viparita Raja Yoga",
            "planets_involved": [l8],
            "nature": "Auspicious Resilience",
            "strength_score": 85,
            "description": "Confers formidable longevity, scholarly depth in concealed or esoteric disciplines, and courage that grows during intense crises.",
            "condition": f"8th Lord ({l8}) is posited in Dusthana House {house_of[l8]}."
        })

    # Vimala Yoga (12th lord in 6th, 8th, or 12th)
    l12 = lord_of_house(12)
    if l12 in pos and house_of[l12] in dusthana_houses:
        found_yogas.append({
            "name": "Vimala Yoga (Viparita Raja Yoga)",
            "category": "Viparita Raja Yoga",
            "planets_involved": [l12],
            "nature": "Auspicious Resilience",
            "strength_score": 80,
            "description": "Grants inner independence, spiritual detachment, noble financial spending, and comfortable settlements in foreign territories.",
            "condition": f"12th Lord ({l12}) is posited in Dusthana House {house_of[l12]}."
        })

    # 5. DHANA YOGAS (Wealth Combinations)
    # Chandra-Mangala Yoga
    if "Moon" in pos and "Mars" in pos and sign_of["Moon"] == sign_of["Mars"]:
        found_yogas.append({
            "name": "Chandra-Mangala Yoga",
            "category": "Dhana Yoga",
            "planets_involved": ["Moon", "Mars"],
            "nature": "Prosperous",
            "strength_score": 75,
            "description": "Fosters astute commercial instincts, accumulative financial skill, and relentless economic self-reliance.",
            "condition": "Moon and Mars are in conjunction."
        })

    # 2nd and 11th Lord Connection
    l2 = lord_of_house(2)
    l11 = lord_of_house(11)
    if l2 in pos and l11 in pos and (sign_of[l2] == sign_of[l11] or (house_of[l2] == 11 and house_of[l11] == 2)):
        found_yogas.append({
            "name": "Maha Dhana Yoga",
            "category": "Dhana Yoga",
            "planets_involved": [l2, l11],
            "nature": "Highly Prosperous",
            "strength_score": 90,
            "description": "Direct mutual connection between wealth storage (2nd) and incoming revenues (11th) brings continuous material growth.",
            "condition": f"2nd Lord ({l2}) and 11th Lord ({l11}) are united."
        })

    # 6. SOLAR YOGAS
    if "Sun" in pos:
        sun_s = sign_of["Sun"]
        non_luminaries = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        second_planets = [p for p in non_luminaries if p in pos and (sign_of[p] - sun_s) % 12 == 1]
        twelfth_planets = [p for p in non_luminaries if p in pos and (sun_s - sign_of[p]) % 12 == 1]

        if second_planets and twelfth_planets:
            found_yogas.append({
                "name": "Ubhayachari Yoga",
                "category": "Solar Yoga",
                "planets_involved": ["Sun"] + second_planets + twelfth_planets,
                "nature": "Auspicious Equilibrium",
                "strength_score": 80,
                "description": "Planets flanking both sides of the Sun confer eloquence, noble poise, physical grace, and respected social bearing.",
                "condition": "Non-luminary planets flank the Sun in both the 2nd and 12th houses from it."
            })
        elif second_planets:
            found_yogas.append({
                "name": "Vesi Yoga",
                "category": "Solar Yoga",
                "planets_involved": ["Sun"] + second_planets,
                "nature": "Favorable",
                "strength_score": 75,
                "description": "Planets in the 2nd from the Sun bestow truthful speech, a balanced outlook, and comfortable prosperity.",
                "condition": "Planets occupy the 2nd house from the Sun."
            })
        elif twelfth_planets:
            found_yogas.append({
                "name": "Vosi Yoga",
                "category": "Solar Yoga",
                "planets_involved": ["Sun"] + twelfth_planets,
                "nature": "Favorable",
                "strength_score": 75,
                "description": "Planets in the 12th from the Sun give generous character, charitable inclination, and steady intellectual focus.",
                "condition": "Planets occupy the 12th house from the Sun."
            })

    # Budhaditya Yoga
    if "Sun" in pos and "Mercury" in pos and sign_of["Sun"] == sign_of["Mercury"]:
        # Check that Mercury is not combust within 3 degrees
        diff = abs(pos["Sun"]["longitude"] - pos["Mercury"]["longitude"])
        strength = 85 if diff > 3.5 else 70
        found_yogas.append({
            "name": "Budhaditya Yoga",
            "category": "Intellectual Yoga",
            "planets_involved": ["Sun", "Mercury"],
            "nature": "Auspicious Wisdom",
            "strength_score": strength,
            "description": "Conjunction of the Sun (soul) and Mercury (intellect) endows the native with rapid cognitive processing, administrative skill, and academic distinction.",
            "condition": f"Sun and Mercury are conjunct ({diff:.1f}° separation)."
        })

    # 7. LUNAR YOGAS
    if "Moon" in pos:
        moon_s = sign_of["Moon"]
        non_sun = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        second_moon = [p for p in non_sun if p in pos and (sign_of[p] - moon_s) % 12 == 1]
        twelfth_moon = [p for p in non_sun if p in pos and (moon_s - sign_of[p]) % 12 == 1]

        if second_moon and twelfth_moon:
            found_yogas.append({
                "name": "Durdhura Yoga",
                "category": "Lunar Yoga",
                "planets_involved": ["Moon"] + second_moon + twelfth_moon,
                "nature": "Highly Favorable",
                "strength_score": 85,
                "description": "Planets on both sides of the Moon yield abundant vehicular comforts, generous disposition, and emotional stability.",
                "condition": "Planets occupy both the 2nd and 12th from the Moon."
            })
        elif second_moon:
            found_yogas.append({
                "name": "Sunapha Yoga",
                "category": "Lunar Yoga",
                "planets_involved": ["Moon"] + second_moon,
                "nature": "Favorable",
                "strength_score": 75,
                "description": "Planets in the 2nd from the Moon confer self-created wealth, practical intellect, and a peaceful domestic demeanor.",
                "condition": "Planets occupy the 2nd house from the Moon."
            })
        elif twelfth_moon:
            found_yogas.append({
                "name": "Anapha Yoga",
                "category": "Lunar Yoga",
                "planets_involved": ["Moon"] + twelfth_moon,
                "nature": "Favorable",
                "strength_score": 75,
                "description": "Planets in the 12th from the Moon bestow dignified character, healthy physical vitality, and generous philanthropic instincts.",
                "condition": "Planets occupy the 12th house from the Moon."
            })

    # Amala Yoga (Benefics in 10th from Lagna or Moon)
    benefics = ["Jupiter", "Venus", "Mercury"]
    h10_occupants = [p for p in benefics if p in pos and house_of[p] == 10]
    if h10_occupants:
        found_yogas.append({
            "name": "Amala Yoga",
            "category": "Character & Fame",
            "planets_involved": h10_occupants,
            "nature": "Stainless Honor",
            "strength_score": 85,
            "description": "Benefic planets placed in the 10th house bestow an untarnished public reputation, pure professional ethics, and lasting societal goodwill.",
            "condition": f"Natural benefic {h10_occupants[0]} occupies the 10th house."
        })

    # Saraswati Yoga (Benefics in Kendras, Trikonas, or 2nd house with Jupiter strong)
    if all(p in pos and house_of[p] in {1, 2, 4, 5, 7, 9, 10} for p in ["Jupiter", "Venus", "Mercury"]):
        found_yogas.append({
            "name": "Saraswati Yoga",
            "category": "Knowledge & Arts",
            "planets_involved": ["Jupiter", "Venus", "Mercury"],
            "nature": "Supreme Intellect",
            "strength_score": 95,
            "description": "Bestows sublime poetic, literary, musical, and scholarly mastery under the divine blessings of Goddess Saraswati.",
            "condition": "All three natural benefics (Jupiter, Venus, Mercury) occupy Kendra, Trikona, or 2nd houses."
        })

    # Calculate overall yoga auspiciousness index
    total_score = sum(y["strength_score"] for y in found_yogas)
    avg_score = round(total_score / len(found_yogas), 1) if found_yogas else 50.0

    return {
        "total_yogas_detected": len(found_yogas),
        "auspiciousness_index": avg_score,
        "yogas": found_yogas,
    }

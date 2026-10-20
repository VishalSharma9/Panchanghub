"""Classical Vedic Prashna (Horary) Astrology Engine.

Derived from canonical Sanskrit treatises:
- Prashna Tantra of Neelakantha Daivajna
- Daivajna Vallabha of Varahamihira
- Shatpanchasika of Prithuyashas
- Tajika Neelakanthi (Ithasala, Ishrafa, Nakta, Yamaya, Kamboola yogas)

Evaluates horary charts for any given query moment and location, determining:
1. Prashna Lagna & Arudha Lagna
2. Karyesha (Significator of the Query House) & Lagnesha (Querent)
3. Tajika Aspectual Yogas (Ithasala, Ishrafa, Nakta, Yamaya, Kamboola)
4. Deeptamsha Orb calculations
5. Moon's disposition & planetary testimonies
6. Definite Verdict, Auspiciousness Confidence Score, and Estimated Timing
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .ephem import (
    all_positions, houses, jd_from_utc, norm, angdiff, dms,
    SIGNS, RASHIS, SIGN_LORDS, VEDIC_PLANETS
)

# Canonical Deeptamsha Orbs (Tajika Neelakanthi Ch. 1)
DEEPTAMSHA_ORBS = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
    "Rahu": 0.0,
    "Ketu": 0.0
}

# Average daily speeds for determining faster vs slower planet
PLANET_DAILY_SPEEDS = {
    "Moon": 13.176,
    "Mercury": 1.383,
    "Venus": 1.200,
    "Sun": 0.9856,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.033
}

# 8 Classical Prashna Query Categories
QUERY_DOMAINS = {
    "career": {
        "title": "Career, Promotion, Business & Status",
        "house": 10,
        "signification": "Professional elevation, job offer, commercial ventures, executive recognition",
        "natural_karaka": "Sun"
    },
    "marriage": {
        "title": "Marriage, Love & Partnerships",
        "house": 7,
        "signification": "Marital union, relationship harmony, commercial partnerships, public alliances",
        "natural_karaka": "Venus"
    },
    "finance": {
        "title": "Wealth, Gains & Investments",
        "house": 2,
        "alt_house": 11,
        "signification": "Financial liquidity, return on capital, windfall gains, profit from enterprise",
        "natural_karaka": "Jupiter"
    },
    "health": {
        "title": "Health, Recovery from Disease & Vitality",
        "house": 1,
        "alt_house": 6,
        "signification": "Recovery from illness, bodily endurance, medical prognosis, immunity",
        "natural_karaka": "Sun"
    },
    "children": {
        "title": "Progeny, Children & Examinations",
        "house": 5,
        "signification": "Conception, birth of child, academic success, intellectual creations",
        "natural_karaka": "Jupiter"
    },
    "property": {
        "title": "Real Estate, Property, Vehicles & Home",
        "house": 4,
        "signification": "Purchase or sale of land, domestic peace, construction, conveyances",
        "natural_karaka": "Mars"
    },
    "travel": {
        "title": "Travel, Relocation & Foreign Journey",
        "house": 9,
        "alt_house": 12,
        "signification": "Overseas migration, pilgrimage, relocation, journeys for fortune",
        "natural_karaka": "Moon"
    },
    "litigation": {
        "title": "Legal Disputes, Competitions & Court Verdicts",
        "house": 6,
        "signification": "Litigation resolution, triumph over adversaries, arbitration outcomes",
        "natural_karaka": "Mars"
    }
}

# Tajika Aspects:
# Pratyaksha (Friendly): 3rd, 5th, 9th, 11th signs (sextile 60° and trine 120°)
# Drishti (Inimical): 1st, 4th, 7th, 10th signs (conjunction 0°, square 90°, opposition 180°)
# Adrishti (Inimical/No aspect): 2nd, 6th, 8th, 12th signs
def get_tajika_aspect(deg1: float, deg2: float) -> tuple[str, float]:
    """Returns aspect type ('friendly', 'inimical', 'none') and exact angular distance."""
    diff = abs(angdiff(deg1, deg2))
    
    # Check conjunction (0° ± orb)
    if diff <= 12.0:
        return "inimical_conjunction", diff
    # Sextile (60° ± orb)
    if abs(diff - 60.0) <= 12.0:
        return "friendly_sextile", abs(diff - 60.0)
    # Square (90° ± orb)
    if abs(diff - 90.0) <= 12.0:
        return "inimical_square", abs(diff - 90.0)
    # Trine (120° ± orb)
    if abs(diff - 120.0) <= 12.0:
        return "friendly_trine", abs(diff - 120.0)
    # Opposition (180° ± orb)
    if abs(diff - 180.0) <= 12.0:
        return "inimical_opposition", abs(diff - 180.0)
        
    return "none", diff

def evaluate_prashna(dt_utc: datetime, lat: float, lon: float, query_category: str = "career") -> Dict[str, Any]:
    """Calculates full classical Prashna (Horary) chart and synthesis."""
    if query_category not in QUERY_DOMAINS:
        query_category = "career"
        
    q_info = QUERY_DOMAINS[query_category]
    karya_house_num = q_info["house"]
    
    jd = jd_from_utc(dt_utc)
    pos = all_positions(jd, sidereal=True, true_node=False)
    cusps, asc, mc = houses(jd, lat, lon, "W", True)
    
    asc_sign = int(asc // 30) % 12
    lagnesha = SIGN_LORDS[asc_sign]
    
    karya_sign = (asc_sign + karya_house_num - 1) % 12
    karyesha = SIGN_LORDS[karya_sign]
    
    # Moon position
    moon_lon = pos["Moon"]["longitude"]
    moon_sign = int(moon_lon // 30) % 12
    moon_house = (moon_sign - asc_sign) % 12 + 1
    
    # Coordinates of Lagnesha and Karyesha
    lag_deg = pos[lagnesha]["longitude"] if lagnesha in pos else 0.0
    karya_deg = pos[karyesha]["longitude"] if karyesha in pos else 0.0
    
    # Average speed comparison
    lag_spd = PLANET_DAILY_SPEEDS.get(lagnesha, 1.0)
    karya_spd = PLANET_DAILY_SPEEDS.get(karyesha, 1.0)
    
    # Mean orb
    orb_lag = DEEPTAMSHA_ORBS.get(lagnesha, 8.0)
    orb_karya = DEEPTAMSHA_ORBS.get(karyesha, 8.0)
    mean_orb = (orb_lag + orb_karya) / 2.0
    
    # Aspect check
    aspect_type, aspect_diff = get_tajika_aspect(lag_deg, karya_deg)
    has_aspect = aspect_type != "none" and aspect_diff <= mean_orb
    
    # Determine Ithasala vs Ishrafa
    is_ithasala = False
    is_ishrafa = False
    
    if has_aspect:
        # If the faster planet has lower degree in the sign than the slower planet -> Applying (Ithasala)
        # If faster has higher degree -> Separating (Ishrafa)
        lag_in_sign = lag_deg % 30.0
        karya_in_sign = karya_deg % 30.0
        
        if lag_spd > karya_spd:
            # Lagnesha is faster
            if lag_in_sign < karya_in_sign:
                is_ithasala = True
            else:
                is_ishrafa = True
        else:
            # Karyesha is faster
            if karya_in_sign < lag_in_sign:
                is_ithasala = True
            else:
                is_ishrafa = True
                
    # Nakta Yoga check: if no direct Ithasala, does a faster planet (e.g. Moon or Mercury) transfer light?
    nakta_planet = None
    if not is_ithasala:
        for p in ["Moon", "Mercury", "Venus"]:
            if p not in (lagnesha, karyesha) and p in pos:
                p_deg = pos[p]["longitude"]
                asp1, diff1 = get_tajika_aspect(pos[lagnesha]["longitude"], p_deg)
                asp2, diff2 = get_tajika_aspect(pos[karyesha]["longitude"], p_deg)
                if asp1 != "none" and asp2 != "none" and diff1 <= 10.0 and diff2 <= 10.0:
                    nakta_planet = p
                    break
                    
    # Yamaya Yoga check: slower planet collects light
    yamaya_planet = None
    if not is_ithasala and not nakta_planet:
        for p in ["Jupiter", "Saturn", "Mars"]:
            if p not in (lagnesha, karyesha) and p in pos:
                p_deg = pos[p]["longitude"]
                asp1, diff1 = get_tajika_aspect(pos[lagnesha]["longitude"], p_deg)
                asp2, diff2 = get_tajika_aspect(pos[karyesha]["longitude"], p_deg)
                if asp1 != "none" and asp2 != "none" and diff1 <= 10.0 and diff2 <= 10.0:
                    yamaya_planet = p
                    break
                    
    # Kamboola Yoga: Moon joins the Ithasala
    is_kamboola = False
    if is_ithasala:
        m_asp1, _ = get_tajika_aspect(moon_lon, lag_deg)
        m_asp2, _ = get_tajika_aspect(moon_lon, karya_deg)
        if m_asp1 != "none" or m_asp2 != "none":
            is_kamboola = True
            
    # Auspiciousness scoring (0 to 100)
    score = 50
    reasons = []
    
    # 1. Ithasala between Lagnesha & Karyesha is the king of yogas
    if is_ithasala:
        score += 30
        reasons.append(f"Auspicious Ithasala (Muthashila) Yoga formed between Lagnesha {lagnesha} and Karyesha {karyesha} (applying aspect within {aspect_diff:.2f}° orb).")
    elif is_ishrafa:
        score -= 20
        reasons.append(f"Ishrafa (Musaripha) separating aspect detected between {lagnesha} and {karyesha}, indicating that a recent opportunity has passed or requires re-initiation.")
    elif nakta_planet:
        score += 20
        reasons.append(f"Nakta Yoga formed: {nakta_planet} transfers light between {lagnesha} and {karyesha}, promising success through a mediator, friend, or third party.")
    elif yamaya_planet:
        score += 18
        reasons.append(f"Yamaya Yoga formed: {yamaya_planet} gathers light from both planets, indicating success through a person of high authority or institutional elder.")
    else:
        reasons.append(f"No direct Tajika mutual aspect between Lagnesha {lagnesha} and Karyesha {karyesha}; progress depends on the strength of the Moon and the 11th house of gains.")

    if is_kamboola:
        score += 15
        reasons.append("Kamboola Yoga present: The Moon actively aspects the planetary significators, promising swift and certain fulfillment.")

    # 2. Moon's house position in Prashna
    if moon_house in (1, 4, 7, 10):
        score += 10
        reasons.append(f"The Moon occupies a Kendra house (House {moon_house}), providing momentum, clarity, and rapid development.")
    elif moon_house in (5, 9):
        score += 12
        reasons.append(f"The Moon occupies a Trikona house (House {moon_house}), blessing the query with divine grace and fortune.")
    elif moon_house in (3, 11):
        score += 8
        reasons.append(f"The Moon is in an Upachaya house (House {moon_house}), indicating progressive growth through self-effort.")
    elif moon_house in (6, 8, 12):
        score -= 15
        reasons.append(f"The Moon is in a Dusthana house (House {moon_house}), warning of anxiety, delays, or unseen hidden obstacles.")

    # 3. Benefics in Kendras (1, 4, 7, 10)
    kendra_planets = [p for p in VEDIC_PLANETS if (int(pos[p]["longitude"] // 30) - asc_sign) % 12 + 1 in (1, 4, 7, 10)]
    benefics_in_kendra = [p for p in kendra_planets if p in ("Jupiter", "Venus", "Mercury")]
    if benefics_in_kendra:
        score += 10
        reasons.append(f"Natural benefics ({', '.join(benefics_in_kendra)}) occupy Kendras, protecting the matter from failure per Daivajna Vallabha.")

    # Cap score between 10 and 98
    score = max(10, min(98, score))
    
    # Verdict determination
    if score >= 75:
        verdict = "Highly Favorable (Yes)"
        verdict_badge = "favorable"
        summary = "The cosmic indicators strongly favor success. Circumstances, timing, and planetary testimonies indicate an affirmative outcome with good satisfaction."
    elif score >= 55:
        verdict = "Favorable with Conscious Effort"
        verdict_badge = "mixed"
        summary = "The outcome is achievable but requires persistence, diplomatic mediation, and overcoming intermediate delays. Maintain proactive follow-through."
    else:
        verdict = "Unfavorable / Significant Delays"
        verdict_badge = "unfavorable"
        summary = "Present planetary currents indicate heavy friction, hidden obstacles, or untimely conditions. It is advisable to wait for a more auspicious moment or reassess the approach."

    # Timeframe calculation (Classical Tajika Movable / Fixed / Dual rules)
    # Movable sign (Chara): Fast (Days)
    # Dual sign (Dwiswabhava): Medium (Weeks)
    # Fixed sign (Sthira): Slow / Delayed (Months)
    karya_mod = karya_sign % 3
    if karya_mod == 0:
        timeframe = "Swift fulfillment within 3 to 14 days"
    elif karya_mod == 2:
        timeframe = "Moderate timeline within 3 to 8 weeks"
    else:
        timeframe = "Extended timeline within 3 to 6 months"

    # Plan of action
    planets_overview = []
    for p in VEDIC_PLANETS:
        L = pos[p]["longitude"]
        s = int(L // 30) % 12
        h = (s - asc_sign) % 12 + 1
        planets_overview.append({
            "name": p,
            "sign": SIGNS[s],
            "rashi": RASHIS[s],
            "dms": dms(L % 30.0),
            "house": h,
            "is_lagnesha": p == lagnesha,
            "is_karyesha": p == karyesha
        })

    return {
        "query_category": query_category,
        "query_domain": query_category,
        "query_title": q_info["title"],
        "query_house": karya_house_num,
        "query_signification": q_info["signification"],
        "prashna_moment_utc": dt_utc.isoformat(),
        "prashna_lagna": {
            "sign": SIGNS[asc_sign],
            "rashi": RASHIS[asc_sign],
            "dms": dms(asc % 30.0),
            "lord": lagnesha
        },
        "karya_bhava": {
            "house": karya_house_num,
            "sign": SIGNS[karya_sign],
            "rashi": RASHIS[karya_sign],
            "lord": karyesha
        },
        "moon_status": {
            "sign": SIGNS[moon_sign],
            "house": moon_house,
            "dms": dms(moon_lon % 30.0)
        },
        "tajika_yogas": {
            "ithasala": is_ithasala,
            "ishrafa": is_ishrafa,
            "nakta": nakta_planet is not None,
            "nakta_planet": nakta_planet,
            "yamaya": yamaya_planet is not None,
            "yamaya_planet": yamaya_planet,
            "kamboola": is_kamboola,
            "aspect_type": aspect_type,
            "aspect_orb": round(aspect_diff, 2)
        },
        "verdict": verdict,
        "verdict_badge": verdict_badge,
        "confidence_score": score,
        "timeframe": timeframe,
        "summary": summary,
        "testimonies": reasons,
        "planets": planets_overview,
        "source": "Prashna Tantra (Neelakantha Daivajna) & Daivajna Vallabha (Varahamihira)"
    }

"""Comprehensive Ashtakavarga Engine with Reductions and Pindas.

Authentic implementation per Brihat Parashara Hora Shastra (BPHS Ch. 67-70):
1. Bhinnashtakavarga (BAV) for all 7 classical planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).
2. Sarvashtakavarga / Samudaya Ashtakavarga (SAV) with 337 total bindus.
3. Trikona Shodhana (Triplicity Reduction across Fire, Earth, Air, Water signs).
4. Ekadhipatya Shodhana (Dual Lordship Reduction for Mars, Venus, Mercury, Jupiter, Saturn).
5. Shodhya Pindas: Rashi Pinda, Graha Pinda, and Yoga Pinda.
6. Kaksha Division Matrix (8 Kakshas per sign, 96 total kakshas across the zodiac).
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from .ephem import SIGNS, RASHIS, SIGN_LORDS, VEDIC_PLANETS

# 12 Rashi Gunakas (multipliers for Rashi Pinda)
RASHI_GUNAKAS = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12]

# 7 Graha Gunakas (multipliers for Graha Pinda)
GRAHA_GUNAKAS = {
    "Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5, "Jupiter": 10, "Venus": 7, "Saturn": 5
}

# Classical 8 Kaksha Lords in order (each Kaksha spans 3°45')
KAKSHA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]

# BPHS Ashtakavarga benefic contributions (_AV matrix)
_AV_CONTRIB = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12]
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11]
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11]
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11]
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11]
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11]
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11]
    }
}

def trikona_shodhana(bav_pts: List[int]) -> List[int]:
    """Applies Trikona Shodhana (triplicity reduction) per BPHS Ch. 67.
    
    Triplicities:
    - Fire: Aries (0), Leo (4), Sagittarius (8)
    - Earth: Taurus (1), Virgo (5), Capricorn (9)
    - Air: Gemini (2), Libra (6), Aquarius (10)
    - Water: Cancer (3), Scorpio (7), Pisces (11)
    """
    res = list(bav_pts)
    for i in range(4):
        tri = [i, i + 4, i + 8]
        vals = [res[s] for s in tri]
        # If any sign in triplicity is 0, no reduction is made
        if any(v == 0 for v in vals):
            continue
        # If all three are equal, all become 0
        if vals[0] == vals[1] == vals[2]:
            for s in tri:
                res[s] = 0
        else:
            m = min(vals)
            for s in tri:
                res[s] -= m
    return res

def ekadhipatya_shodhana(trikona_pts: List[int], planets_in_signs: Dict[int, List[str]]) -> List[int]:
    """Applies Ekadhipatya Shodhana (dual lordship reduction) per BPHS Ch. 68.
    
    Pairs of signs ruled by the same planet:
    - Mars: Aries (0) & Scorpio (7)
    - Venus: Taurus (1) & Libra (6)
    - Mercury: Gemini (2) & Virgo (5)
    - Jupiter: Sagittarius (8) & Pisces (11)
    - Saturn: Capricorn (9) & Aquarius (10)
    """
    res = list(trikona_pts)
    pairs = [
        (0, 7),  # Mars
        (1, 6),  # Venus
        (2, 5),  # Mercury
        (8, 11), # Jupiter
        (9, 10)  # Saturn
    ]
    for s1, s2 in pairs:
        p1, p2 = res[s1], res[s2]
        occ1 = bool(planets_in_signs.get(s1))
        occ2 = bool(planets_in_signs.get(s2))
        
        # Case 1: Both occupied -> No reduction
        if occ1 and occ2:
            continue
            
        # Case 2: Neither occupied
        if not occ1 and not occ2:
            if p1 == p2:
                res[s1] = 0
                res[s2] = 0
            else:
                m = min(p1, p2)
                res[s1] = m
                res[s2] = m
            continue
            
        # Case 3: One occupied, one unoccupied
        occ_s, unocc_s = (s1, s2) if occ1 else (s2, s1)
        occ_p, unocc_p = res[occ_s], res[unocc_s]
        
        if unocc_p > occ_p:
            res[unocc_s] = occ_p
        else:
            res[unocc_s] = 0
            
    return res

def compute_shodhya_pindas(shodhita_pts: List[int], planets_in_signs: Dict[int, List[str]]) -> Dict[str, int]:
    """Calculates Rashi Pinda, Graha Pinda, and Yoga Pinda per BPHS Ch. 69-70."""
    rashi_pinda = sum(shodhita_pts[s] * RASHI_GUNAKAS[s] for s in range(12))
    
    graha_pinda = 0
    for s in range(12):
        pts = shodhita_pts[s]
        if pts > 0 and s in planets_in_signs:
            for pl in planets_in_signs[s]:
                if pl in GRAHA_GUNAKAS:
                    graha_pinda += pts * GRAHA_GUNAKAS[pl]
                    
    yoga_pinda = rashi_pinda + graha_pinda
    return {
        "rashi_pinda": rashi_pinda,
        "graha_pinda": graha_pinda,
        "yoga_pinda": yoga_pinda
    }

def compute_kakshas_matrix(sign_of: Dict[str, int]) -> Dict[str, Any]:
    """Generates the 8-Kaksha transit grid for all signs and planets per BPHS.
    
    Each sign has 8 kakshas of 3°45'. Each kaksha is ruled by one of KAKSHA_LORDS.
    A bindu (1) is present if the kaksha lord contributes a benefic point to that sign.
    """
    matrix = {}
    for p in GRAHA_GUNAKAS:
        bav_row = {}
        for s in range(12):
            kakshas = []
            for kl in KAKSHA_LORDS:
                # Contributor check
                contrib_list = _AV_CONTRIB[p].get(kl, [])
                # Does kl from its own position make this sign benefic?
                kl_sign = sign_of.get(kl, 0)
                h = (s - kl_sign) % 12 + 1
                has_bindu = 1 if h in contrib_list else 0
                kakshas.append({"lord": kl, "bindu": has_bindu})
            bav_row[SIGNS[s]] = kakshas
        matrix[p] = bav_row
    return matrix

def full_ashtakavarga_suite(sign_of: Dict[str, int], pos: Dict[str, Any], asc: float) -> Dict[str, Any]:
    """Calculates the complete Ashtakavarga suite:
    - Bhinnashtakavarga (BAV) for all 7 planets
    - Samudaya Ashtakavarga (SAV, total 337 points)
    - Trikona Shodhana (triplicity reduction)
    - Ekadhipatya Shodhana (dual lordship reduction)
    - Shodhita Ashtakavarga
    - Shodhya Pindas (Rashi Pinda, Graha Pinda, Yoga Pinda)
    - Kakshas matrix
    """
    # 1. Raw BAV
    bav = {}
    for p in GRAHA_GUNAKAS:
        pts = [0] * 12
        for c, hs in _AV_CONTRIB[p].items():
            for h in hs:
                pts[(sign_of[c] + h - 1) % 12] += 1
        bav[p] = pts
        
    sav = [sum(bav[p][i] for p in bav) for i in range(12)]
    
    # 2. Planets in signs mapping
    planets_in_signs: Dict[int, List[str]] = {s: [] for s in range(12)}
    for pl in GRAHA_GUNAKAS:
        s = sign_of.get(pl, 0)
        planets_in_signs[s].append(pl)
        
    # 3. Reductions & Pindas
    trikona_reduced = {}
    shodhita = {}
    pindas = {}
    
    for pl in GRAHA_GUNAKAS:
        tri = trikona_shodhana(bav[pl])
        trikona_reduced[pl] = tri
        
        shod = ekadhipatya_shodhana(tri, planets_in_signs)
        shodhita[pl] = shod
        
        pindas[pl] = compute_shodhya_pindas(shod, planets_in_signs)
        
    # Total reduced SAV
    shodhita_sav = [sum(shodhita[p][i] for p in GRAHA_GUNAKAS) for i in range(12)]
    
    # Kakshas
    kakshas = compute_kakshas_matrix(sign_of)
    
    return {
        "signs": SIGNS,
        "rashis": RASHIS,
        "bhinnashtakavarga": bav,
        "sarvashtakavarga": sav,
        "sav_total": sum(sav),
        "trikona_shodhana": trikona_reduced,
        "shodhita_ashtakavarga": shodhita,
        "shodhita_sav": shodhita_sav,
        "shodhita_sav_total": sum(shodhita_sav),
        "shodhya_pindas": pindas,
        "kakshas_matrix": kakshas,
        "rashi_gunakas": RASHI_GUNAKAS,
        "graha_gunakas": GRAHA_GUNAKAS
    }

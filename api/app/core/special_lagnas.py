"""Special Lagnas, Alternate Reference Frames, and Arudha Padas.

Authentic implementation per Brihat Parashara Hora Shastra (BPHS Ch. 5, 29, 30) and Jaimini Sutras:
- Bhava Lagna (BL): Moves 1 sign every 5 ghatis (2 hours) from sunrise.
- Hora Lagna (HL): Moves 1 sign every 2.5 ghatis (1 hour) from sunrise (Seat of Wealth & Resources).
- Ghati Lagna (GL): Moves 1 sign every 1 ghati (24 minutes) from sunrise (Seat of Power & Authority).
- Sree Lagna (SL): Moon's nakshatra traversal projected onto Lagna (Seat of Prosperity & Lakshmi).
- Pranapada Lagna (PP): Life-breath ascendant used for birth time rectification.
- Indu Lagna: Moon-ray wealth ascendant based on Kalas of 9th lords from Lagna and Moon.
- Paka Lagna: Sign occupied by Lagna Lord.
- Karka Lagna: Cancer sign reference frame.
- Arudha Padas A1 to A12 (including AL - Arudha Lagna and UL - Upapada Lagna) with classical exceptions.
"""
from __future__ import annotations
import math
import swisseph as swe
from typing import Dict, List, Any
from .ephem import (
    calc, norm, angdiff, SIGNS, RASHIS, SIGN_LORDS, VEDIC_PLANETS,
    nakshatra_of, dms
)

# Planetary Kalas (Rays) for Indu Lagna per Brihat Jataka & BPHS
INDU_KALAS = {
    "Sun": 30,
    "Moon": 16,
    "Mars": 6,
    "Mercury": 8,
    "Jupiter": 10,
    "Venus": 12,
    "Saturn": 1
}

ARUDHA_NAMES = {
    1: ("A1", "Arudha Lagna (AL)", "Public image, outer manifestation, persona, and worldly status"),
    2: ("A2", "Dhana Pada (A2)", "Accumulated financial assets, liquid wealth, and family reputation"),
    3: ("A3", "Bhratru Pada (A3)", "Courage, prowess, enterprise, initiatives, and younger siblings"),
    4: ("A4", "Matru / Sukha Pada (A4)", "Vehicles, conveyances, fixed properties, real estate, and inner contentment"),
    5: ("A5", "Mantra / Putra Pada (A5)", "Creative intelligence, investments, speculation, mantra siddhi, and progeny"),
    6: ("A6", "Shatru / Roga Pada (A6)", "Enemies, litigations, debts, acute obstacles, and competitive prowess"),
    7: ("A7", "Dara Pada (A7)", "Spouse, physical partnership, business trade, and commercial associates"),
    8: ("A8", "Mrityu / Randhra Pada (A8)", "Longevity, sudden transformations, vulnerabilities, and occult secrets"),
    9: ("A9", "Dharma / Pitru Pada (A9)", "Righteousness, fortune, father, pilgrimage, preceptors, and grace"),
    10: ("A10", "Rajya / Karma Pada (A10)", "Career achievements, executive authority, leadership, and public legacy"),
    11: ("A11", "Labha Pada (A11)", "Gains, revenues, friends, network circles, and realization of desires"),
    12: ("A12", "Upapada Lagna (UL)", "Marriage partner, marital longevity, spouse's heritage, and expenditure")
}

def compute_special_lagnas(
    birth_jd: float,
    lat: float,
    lon: float,
    asc_lon: float,
    sun_lon: float,
    moon_lon: float,
    pos: Dict[str, Any]
) -> Dict[str, Any]:
    """Computes all classical BPHS Special Lagnas, Alternate Lagnas, and Arudha Padas."""
    asc_sign = int(asc_lon // 30)
    moon_sign = int(moon_lon // 30)
    sun_sign = int(sun_lon // 30)
    
    # 1. Sunrise determination
    from .ephem import rise_set
    sr = rise_set(birth_jd, swe.SUN, lat, lon, 0.0, True)
    if sr is None or sr > birth_jd:
        # Check previous day's sunrise
        sr = rise_set(birth_jd - 1.0, swe.SUN, lat, lon, 0.0, True)
    
    if sr is not None:
        delta_days = max(0.0, birth_jd - sr)
    else:
        # Fallback if polar or failed rise
        delta_days = 0.25
        
    ghatis = delta_days * 60.0  # 1 day = 60 ghatis = 24 hours
    vighatis = ghatis * 60.0    # 1 ghati = 60 vighatis
    
    # Sun at sunrise approximation
    sun_sr_lon = sun_lon - (delta_days * 0.9856)
    
    # 2. Bhava Lagna (BL): 1 sign per 5 ghatis -> 6 degrees per ghati
    bl_lon = norm(sun_sr_lon + ghatis * 6.0)
    bl_sign = int(bl_lon // 30)
    
    # 3. Hora Lagna (HL): 1 sign per 2.5 ghatis -> 12 degrees per ghati (1 hour = 1 sign)
    hl_lon = norm(sun_sr_lon + ghatis * 12.0)
    hl_sign = int(hl_lon // 30)
    
    # 4. Ghati Lagna (GL): 1 sign per 1 ghati -> 30 degrees per ghati
    gl_lon = norm(sun_sr_lon + ghatis * 30.0)
    gl_sign = int(gl_lon // 30)
    
    # 5. Sree Lagna (SL): Moon nakshatra traversed fraction * 360 added to Janma Lagna
    span = 360.0 / 27.0
    nak_idx = int(moon_lon // span)
    nak_frac = (moon_lon - nak_idx * span) / span
    sl_lon = norm(asc_lon + nak_frac * 360.0)
    sl_sign = int(sl_lon // 30)
    
    # 6. Pranapada Lagna (PP):
    # Vighatis divided by 15 gives signs. Added to Sun with movable/fixed/dual sign adjustment
    pp_movement = (vighatis / 15.0) * 30.0
    sign_type = sun_sign % 3  # 0: movable, 1: fixed, 2: dual
    offset = 0.0 if sign_type == 0 else (240.0 if sign_type == 1 else 120.0)
    pp_lon = norm(sun_lon + pp_movement + offset)
    pp_sign = int(pp_lon // 30)
    
    # 7. Indu Lagna (Wealth Ascendant):
    # 9th lord from Lagna + 9th lord from Moon
    ninth_from_asc = (asc_sign + 8) % 12
    lord1 = SIGN_LORDS[ninth_from_asc]
    kalas1 = INDU_KALAS.get(lord1, 10)
    
    ninth_from_moon = (moon_sign + 8) % 12
    lord2 = SIGN_LORDS[ninth_from_moon]
    kalas2 = INDU_KALAS.get(lord2, 10)
    
    kala_sum = kalas1 + kalas2
    rem = kala_sum % 12
    if rem == 0:
        rem = 12
        
    # Count rem signs from Moon sign
    indu_sign = (moon_sign + rem - 1) % 12
    indu_lon = indu_sign * 30.0 + 15.0  # Center of sign
    
    # Evaluate planets in Indu Lagna
    planets_in_indu = [p for p in VEDIC_PLANETS if int(pos[p]["longitude"] // 30) == indu_sign]
    indu_benefics = [p for p in planets_in_indu if p in ("Jupiter", "Venus", "Mercury", "Moon")]
    indu_malefics = [p for p in planets_in_indu if p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")]
    
    if indu_benefics:
        indu_reading = f"Strong Dhana Yoga: Auspicious benefics ({', '.join(indu_benefics)}) occupy Indu Lagna, conferring great wealth, financial stability, and effortless material prosperity."
    elif indu_malefics:
        indu_reading = f"Moderate Wealth Yoga: Malefic grahas ({', '.join(indu_malefics)}) occupy Indu Lagna; financial gains are attained through strenuous effort, discipline, and persistent labor."
    else:
        indu_reading = "Unoccupied Indu Lagna; financial fortune is mediated by the strength, dignity, and aspects received by the sign lord (" + SIGN_LORDS[indu_sign] + ")."
        
    # 8. Paka Lagna (Sign of the Lagna Lord)
    lagna_lord = SIGN_LORDS[asc_sign]
    paka_sign = int(pos[lagna_lord]["longitude"] // 30)
    
    # 9. Arudha Padas (A1 to A12)
    sign_of = {p: int(pos[p]["longitude"] // 30) for p in VEDIC_PLANETS}
    sign_of["Lagna"] = asc_sign
    
    arudhas = {}
    for h in range(1, 13):
        h_sign = (asc_sign + h - 1) % 12
        lord = SIGN_LORDS[h_sign]
        ls = sign_of[lord]
        dist = (ls - h_sign) % 12
        pada = (ls + dist) % 12
        # Classical exceptions (if pada falls in house itself -> 10th; if 7th -> 4th)
        if pada == h_sign:
            pada = (h_sign + 9) % 12
        elif pada == (h_sign + 6) % 12:
            pada = (h_sign + 3) % 12
            
        code, label, meaning = ARUDHA_NAMES[h]
        planets_in_pada = [p for p in VEDIC_PLANETS if sign_of[p] == pada]
        arudhas[code] = {
            "house": h,
            "code": code,
            "label": label,
            "sign": SIGNS[pada],
            "rashi": RASHIS[pada],
            "sign_index": pada,
            "house_from_lagna": (pada - asc_sign) % 12 + 1,
            "planets": planets_in_pada,
            "signification": meaning
        }
        
    def _pack_special(lon, sign, name, label, description):
        deg = lon % 30.0
        ni, pada = nakshatra_of(lon)
        from .ephem import NAKSHATRAS, NAK_LORDS
        return {
            "name": name,
            "label": label,
            "longitude": round(lon, 6),
            "sign": SIGNS[sign],
            "rashi": RASHIS[sign],
            "degree": round(deg, 6),
            "dms": dms(deg),
            "nakshatra": NAKSHATRAS[ni],
            "pada": pada,
            "nakshatra_lord": NAK_LORDS[ni % 9],
            "sign_lord": SIGN_LORDS[sign],
            "house_from_lagna": (sign - asc_sign) % 12 + 1,
            "description": description
        }

    return {
        "bhava_lagna": _pack_special(bl_lon, bl_sign, "BL", "Bhava Lagna", "Advances 1 sign every 5 ghatis (2 hours) from sunrise; reveals vitality and constitutional strength."),
        "hora_lagna": _pack_special(hl_lon, hl_sign, "HL", "Hora Lagna", "Advances 1 sign every 2.5 ghatis (1 hour) from sunrise; paramount indicator of wealth and monetary assets."),
        "ghati_lagna": _pack_special(gl_lon, gl_sign, "GL", "Ghati Lagna", "Advances 1 sign every 1 ghati (24 minutes) from sunrise; primary seat of royal power, authority, and high status."),
        "sree_lagna": _pack_special(sl_lon, sl_sign, "SL", "Sree Lagna", "Special fortune lagna of Goddess Lakshmi; reveals ease of financial acquisition and prosperity."),
        "pranapada_lagna": _pack_special(pp_lon, pp_sign, "PP", "Pranapada Lagna", "The life-breath ascendant; classical reference point for verifying and rectifying birth time."),
        "indu_lagna": {
            "sign": SIGNS[indu_sign],
            "rashi": RASHIS[indu_sign],
            "sign_index": indu_sign,
            "house_from_lagna": (indu_sign - asc_sign) % 12 + 1,
            "sign_lord": SIGN_LORDS[indu_sign],
            "lord_kalas": {"9th_from_asc": {"lord": lord1, "kalas": kalas1}, "9th_from_moon": {"lord": lord2, "kalas": kalas2}, "sum": kala_sum, "remainder": rem},
            "planets_occupying": planets_in_indu,
            "interpretation": indu_reading
        },
        "paka_lagna": {
            "sign": SIGNS[paka_sign],
            "rashi": RASHIS[paka_sign],
            "sign_index": paka_sign,
            "house_from_lagna": (paka_sign - asc_sign) % 12 + 1,
            "lagna_lord": lagna_lord,
            "description": f"Sign occupied by Lagna Lord ({lagna_lord}); indicates the physical focus and operational sphere of the soul's incarnation."
        },
        "karka_lagna": {
            "sign": "Cancer",
            "rashi": "Karka",
            "sign_index": 3,
            "house_from_lagna": (3 - asc_sign) % 12 + 1,
            "description": "Cancer as universal cosmic mother lagna and heart center."
        },
        "arudha_padas": arudhas,
        "arudha_lagna": arudhas["A1"],
        "upapada_lagna": arudhas["A12"]
    }

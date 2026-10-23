"""Comprehensive Planetary Period (Dasha) Systems Engine.

Includes:
- Deep 5-level Vimshottari decomposition (Maha, Antar, Pratyantar, Sookshma, Prana)
- Active current dasha resolver for any target date
- Complete Yogini Dasha with Antar-Yoginis
- Jaimini Chara Karakas (AK, AmK, BK, MK, PK, GK, DK) and Karakamsha analysis
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from .ephem import NAK_LORDS, SIGNS, RASHIS, SIGN_LORDS, local_from_jd
from .kundli import YEAR_DAYS, VIM_ORDER, VIM_YEARS, YOGINIS

def _add_days(jd: float, days: float) -> float:
    return jd + days

def _add_years(jd: float, years: float) -> float:
    return jd + years * YEAR_DAYS

def _fmt_date(jd: float, tz) -> str:
    return local_from_jd(jd, tz).date().isoformat()

def get_vimshottari_balance(moon_lon: float, birth_jd: float) -> tuple[str, float, float]:
    """Calculates initial dasha ruler, years remaining, and the precise cycle start JD."""
    span = 360.0 / 27.0  # 13°20'
    nak_idx = int((moon_lon % 360.0) // span)
    frac = ((moon_lon % 360.0) - nak_idx * span) / span
    ruler0 = NAK_LORDS[nak_idx % 9]
    ruler_years = VIM_YEARS[ruler0]
    years_remaining = (1.0 - frac) * ruler_years
    cycle_start_jd = birth_jd - frac * ruler_years * YEAR_DAYS
    return ruler0, years_remaining, cycle_start_jd

def compute_deep_vimshottari(moon_lon: float, birth_jd: float, tz, max_levels: int = 3, cycles: int = 1) -> Dict[str, Any]:
    """Computes Vimshottari Dasha up to 5 levels (Maha, Antar, Pratyantar, Sookshma, Prana)."""
    ruler0, years_rem, cycle_start = get_vimshottari_balance(moon_lon, birth_jd)
    idx0 = VIM_ORDER.index(ruler0)

    def generate_subperiods(parent_lord: str, start_jd: float, total_years: float, current_level: int) -> List[Dict[str, Any]]:
        subs = []
        p_idx = VIM_ORDER.index(parent_lord)
        t = start_jd
        level_names = {2: "antardasha", 3: "pratyantardasha", 4: "sookshmadasha", 5: "pranadasha"}
        key_name = level_names.get(current_level, "sub")

        for k in range(9):
            sub_lord = VIM_ORDER[(p_idx + k) % 9]
            sub_years = total_years * VIM_YEARS[sub_lord] / 120.0
            sub_end = _add_years(t, sub_years)

            entry: Dict[str, Any] = {
                "lord": sub_lord,
                "years": round(sub_years, 5),
                "start": _fmt_date(t, tz),
                "end": _fmt_date(sub_end, tz),
            }

            if current_level < max_levels:
                entry[level_names.get(current_level + 1, "sub")] = generate_subperiods(sub_lord, t, sub_years, current_level + 1)

            subs.append(entry)
            t = sub_end
        return subs

    mahadashas = []
    curr_t = cycle_start
    total_mahas = 9 * cycles

    for k in range(total_mahas):
        maha_lord = VIM_ORDER[(idx0 + k) % 9]
        m_years = VIM_YEARS[maha_lord]
        m_end = _add_years(curr_t, m_years)

        # Include only if the period ends after birth
        if m_end > birth_jd:
            maha_entry: Dict[str, Any] = {
                "lord": maha_lord,
                "years": m_years,
                "start": _fmt_date(curr_t, tz),
                "end": _fmt_date(m_end, tz),
            }
            if max_levels >= 2:
                maha_entry["antardashas"] = generate_subperiods(maha_lord, curr_t, m_years, 2)
            mahadashas.append(maha_entry)

        curr_t = m_end

    return {
        "system": "Vimshottari (120 Years)",
        "birth_balance": {
            "ruler": ruler0,
            "years_remaining": round(years_rem, 4),
        },
        "mahadashas": mahadashas,
    }

def get_current_dasha(moon_lon: float, birth_jd: float, target_jd: float, tz) -> Dict[str, Any]:
    """Finds the exact operative Mahadasha, Antardasha, Pratyantardasha, and Sookshmadasha for any target JD."""
    ruler0, _, cycle_start = get_vimshottari_balance(moon_lon, birth_jd)
    idx0 = VIM_ORDER.index(ruler0)

    # 1. Find Mahadasha
    curr_t = cycle_start
    active_maha = None
    for k in range(18):  # Check up to 2 full cycles (240 years)
        lord = VIM_ORDER[(idx0 + k) % 9]
        dur = VIM_YEARS[lord] * YEAR_DAYS
        end_t = curr_t + dur
        if curr_t <= target_jd < end_t:
            active_maha = (lord, curr_t, end_t, VIM_YEARS[lord])
            break
        curr_t = end_t

    if not active_maha:
        return {"error": "Target date is outside calculation range"}

    m_lord, m_start, m_end, m_yrs = active_maha

    # 2. Find Antardasha
    m_idx = VIM_ORDER.index(m_lord)
    curr_t = m_start
    active_antar = None
    for k in range(9):
        lord = VIM_ORDER[(m_idx + k) % 9]
        sub_yrs = m_yrs * VIM_YEARS[lord] / 120.0
        dur = sub_yrs * YEAR_DAYS
        end_t = curr_t + dur
        if curr_t <= target_jd < end_t:
            active_antar = (lord, curr_t, end_t, sub_yrs)
            break
        curr_t = end_t

    a_lord, a_start, a_end, a_yrs = active_antar

    # 3. Find Pratyantardasha
    a_idx = VIM_ORDER.index(a_lord)
    curr_t = a_start
    active_prat = None
    for k in range(9):
        lord = VIM_ORDER[(a_idx + k) % 9]
        sub_yrs = a_yrs * VIM_YEARS[lord] / 120.0
        dur = sub_yrs * YEAR_DAYS
        end_t = curr_t + dur
        if curr_t <= target_jd < end_t:
            active_prat = (lord, curr_t, end_t, sub_yrs)
            break
        curr_t = end_t

    p_lord, p_start, p_end, p_yrs = active_prat

    # 4. Find Sookshmadasha
    p_idx = VIM_ORDER.index(p_lord)
    curr_t = p_start
    active_sook = None
    for k in range(9):
        lord = VIM_ORDER[(p_idx + k) % 9]
        sub_yrs = p_yrs * VIM_YEARS[lord] / 120.0
        dur = sub_yrs * YEAR_DAYS
        end_t = curr_t + dur
        if curr_t <= target_jd < end_t:
            active_sook = (lord, curr_t, end_t, sub_yrs)
            break
        curr_t = end_t

    s_lord, s_start, s_end, s_yrs = active_sook

    # Calculate percentage elapsed of current Mahadasha
    m_total_days = m_end - m_start
    m_elapsed_days = target_jd - m_start
    m_pct = min(100.0, max(0.0, (m_elapsed_days / m_total_days) * 100.0))

    # Classical summary interpretation of combined period
    theme = f"Operating under the major influence of {m_lord}, with secondary direction from {a_lord} and fine focus from {p_lord}."

    return {
        "target_date": _fmt_date(target_jd, tz),
        "mahadasha": {
            "lord": m_lord,
            "start": _fmt_date(m_start, tz),
            "end": _fmt_date(m_end, tz),
            "percent_elapsed": round(m_pct, 1),
            "days_remaining": int(m_end - target_jd),
        },
        "antardasha": {
            "lord": a_lord,
            "start": _fmt_date(a_start, tz),
            "end": _fmt_date(a_end, tz),
            "days_remaining": int(a_end - target_jd),
        },
        "pratyantardasha": {
            "lord": p_lord,
            "start": _fmt_date(p_start, tz),
            "end": _fmt_date(p_end, tz),
        },
        "sookshmadasha": {
            "lord": s_lord,
            "start": _fmt_date(s_start, tz),
            "end": _fmt_date(s_end, tz),
        },
        "sookshma": {
            "lord": s_lord,
            "start": _fmt_date(s_start, tz),
            "end": _fmt_date(s_end, tz),
        },
        "summary": f"{m_lord}-{a_lord}-{p_lord}-{s_lord}",
        "theme": theme,
    }

def compute_full_yogini(moon_lon: float, birth_jd: float, tz, cycles: int = 2) -> Dict[str, Any]:
    """Generates complete Yogini Dasha including all Antar-Yoginis."""
    span = 360.0 / 27.0
    nak_idx = int((moon_lon % 360.0) // span)
    frac = ((moon_lon % 360.0) - nak_idx * span) / span

    # Yogini index formula: (Nakshatra + 3) mod 8
    k0 = (nak_idx + 1 + 3) % 8
    k0 = 8 if k0 == 0 else k0
    start_idx = k0 - 1

    yrs0 = YOGINIS[start_idx][2]
    curr_t = birth_jd - frac * yrs0 * YEAR_DAYS

    periods = []
    total_periods = 8 * cycles

    for c in range(total_periods):
        y_name, y_lord, y_dur = YOGINIS[(start_idx + c) % 8]
        end_t = _add_years(curr_t, y_dur)

        # Generate 8 Antar-Yoginis
        subs = []
        sub_t = curr_t
        for sc in range(8):
            s_name, s_lord, s_dur = YOGINIS[(start_idx + c + sc) % 8]
            sub_span_years = y_dur * s_dur / 36.0
            sub_end = _add_years(sub_t, sub_span_years)
            subs.append({
                "yogini": s_name,
                "lord": s_lord,
                "years": round(sub_span_years, 4),
                "start": _fmt_date(sub_t, tz),
                "end": _fmt_date(sub_end, tz),
            })
            sub_t = sub_end

        if end_t > birth_jd:
            periods.append({
                "yogini": y_name,
                "lord": y_lord,
                "years": y_dur,
                "start": _fmt_date(curr_t, tz),
                "end": _fmt_date(end_t, tz),
                "antardashas": subs,
            })
        curr_t = end_t

    return {
        "system": "Yogini Dasha (36 Years)",
        "birth_balance": {
            "yogini": YOGINIS[start_idx][0],
            "lord": YOGINIS[start_idx][1],
            "years_remaining": round((1.0 - frac) * yrs0, 4),
        },
        "periods": periods,
    }

def compute_jaimini_karakas(pos: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates the 7 Chara Karakas (Atmakaraka to Darakaraka) based on planetary degrees in sign."""
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    candidates = []

    for p in planets:
        if p in pos:
            deg_in_sign = pos[p]["longitude"] % 30.0
            candidates.append({"planet": p, "deg_in_sign": deg_in_sign, "longitude": pos[p]["longitude"]})

    # Sort descending by degree within sign
    candidates.sort(key=lambda x: x["deg_in_sign"], reverse=True)

    karaka_roles = [
        ("Atmakaraka (AK)", "The Soul indicator and prime significator of life trajectory"),
        ("Amatyakaraka (AmK)", "The Minister, career, professional intellect and execution"),
        ("Bhratrukaraka (BK)", "Siblings, comrades, courageous efforts and mentors"),
        ("Matrukaraka (MK)", "Mother, domestic peace, vehicles and emotional roots"),
        ("Putrakaraka (PK)", "Children, creative intelligence, scholarship and legacy"),
        ("Gnatikaraka (GK)", "Obstacles, competition, litigation, health and spiritual tests"),
        ("Darakaraka (DK)", "Spouse, partnership, contracts and public harmony"),
    ]

    assigned = []
    for i, (role, desc) in enumerate(karaka_roles):
        if i < len(candidates):
            c = candidates[i]
            assigned.append({
                "role": role,
                "planet": c["planet"],
                "degree_in_sign": round(c["deg_in_sign"], 4),
                "sign": SIGNS[int(c["longitude"] // 30) % 12],
                "rashi": RASHIS[int(c["longitude"] // 30) % 12],
                "description": desc,
            })

    # Atmakaraka's Navamsa position gives the Karakamsha
    ak_planet = assigned[0]["planet"]
    ak_lon = pos[ak_planet]["longitude"]
    ak_navamsa_sign = int(ak_lon // (30.0 / 9)) % 12

    return {
        "karakas": assigned,
        "atmakaraka": ak_planet,
        "karakamsha_sign": SIGNS[ak_navamsa_sign],
        "karakamsha_sign_idx": ak_navamsa_sign,
        "karakamsha_rashi": RASHIS[ak_navamsa_sign],
        "karakamsha_lord": SIGN_LORDS[ak_navamsa_sign],
    }

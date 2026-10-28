from datetime import datetime as _dt, timezone as _tz
from fastapi import APIRouter, HTTPException
from ...models import (
    KundliRequest, MatchRequest, VarshaphalaRequest, KPRequest,
    PrashnaRequest, DestinyRequest, TraditionsReportRequest, PalmistryPhotoRequest,
    VisualVastuLayoutRequest, DetailedReportRequest, RectifyRelocateRequest,
)
from ...core import ephem
from ...core.destiny_engine import compute_master_destiny_dossier
from ...core.kundli import compute_kundli
from ...core.matching import ashtakoota, porutham
from ...core.panchang import moon_sid
from ...core.vargas_ext import build_all_vargas
from ...core.dashas_ext import get_current_dasha, compute_full_yogini, compute_jaimini_karakas, compute_deep_vimshottari
from ...core.interpret_ext import generate_holistic_reading
from ...core.yogas_engine import evaluate_all_yogas
from ...core.classical_corpus import generate_comprehensive_corpus_reading
from ...core.classical_interpretations import get_varga_comprehensive_reading
from ...core.tajika_sahams import compute_tajika_sahams, get_nadiamsha, get_drekkana_body_part
from ...core.special_lagnas import compute_special_lagnas
from ...core.ashtakavarga_ext import full_ashtakavarga_suite
from ...core.charts_svg import sudarshan_chakra_svg, north_indian, south_indian, east_indian
from ...core.advanced import varshaphal, kp_chart, kp_horary_chart
from ...core.prashna import evaluate_prashna
from ...core.remedies_corpus import compute_soul_guidance, get_complete_remedies_for_chart, GRAHA_REMEDIES
from ..deps import birth_utc, wrap


router = APIRouter(tags=["Studio"])
HS = {"whole_sign": "W", "placidus": "P", "equal": "E"}

@router.post("/kundli/vargas", summary="All 16 Shodashavargas (D1 to D60) with Ascendant, degrees, and Vargottama")
def vargas(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(jd, sidereal=True, true_node=req.true_node)
    cusps, asc, mc = ephem.houses(jd, req.latitude, req.longitude, HS[req.house_system], True)
    res = build_all_vargas(pos, asc)
    res["name"] = req.name
    res["ayanamsa"] = req.ayanamsa

    # Enrich each varga with classical scriptural interpretations and slokas
    karakas = compute_jaimini_karakas(pos)
    k_ctx = {"lagna": {"longitude": asc}, "karakas": karakas}
    for vk, vinfo in res.get("vargas", {}).items():
        vinfo["classical_interpretation"] = get_varga_comprehensive_reading(vk, res, k_ctx)

    return res

@router.post("/kundli/dashas/current", summary="Active running Vimshottari Dasha down to Sookshma level")
def current_dasha_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    moon_lon = pos["Moon"]["longitude"]

    target_dt = req.target_date or _dt.now(_tz.utc).date()
    target_jd = ephem.jd_from_utc(_dt.combine(target_dt, _dt.min.time(), tzinfo=_tz.utc))
    return get_current_dasha(moon_lon, birth_jd, target_jd, tz)

@router.post("/kundli/dashas/yogini", summary="Complete Yogini Dasha (36-year cycle) with Antar-Yoginis")
def yogini_dasha_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    moon_lon = pos["Moon"]["longitude"]
    return compute_full_yogini(moon_lon, birth_jd, tz, cycles=2)

@router.post("/kundli/dashas/chara", summary="Jaimini Chara Karakas (AK..DK) and Karakamsha analysis")
def chara_karakas_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    return compute_jaimini_karakas(pos)

@router.post("/kundli/reading", summary="Holistic Vedic life reading: Lagna, 144 House Lords, and Shad Phala")
def holistic_reading_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    reading = generate_holistic_reading(pos, asc)
    reading["name"] = req.name
    return reading

@router.post("/kundli/yogas", summary="Comprehensive scan of 60+ classical Vedic Yogas with effects and remedies")
def comprehensive_yogas_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    yogas = evaluate_all_yogas(pos, asc)
    yogas["name"] = req.name
    return yogas

@router.post("/kundli/ayanamshas", summary="Planetary coordinates comparison across all 8 supported Ayanamshas")
def ayanamshas_comparison(req: KundliRequest):
    dt_utc = birth_utc(req)
    jd = ephem.jd_from_utc(dt_utc)
    saved_mode = ephem._ayan_mode.get()
    results = {}
    planets_to_check = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for mode in ephem.AYANAMSAS:
        ephem.set_ayanamsa_mode(mode)
        pos = ephem.all_positions(jd, sidereal=True, true_node=req.true_node)
        cusps, asc, mc = ephem.houses(jd, req.latitude, req.longitude, HS[req.house_system], True)
        results[mode] = {
            "ayanamsa_value": round(ephem.ayanamsa(jd), 5),
            "ascendant": round(asc, 4),
            "ascendant_sign": ephem.SIGNS[int(asc // 30) % 12],
            "planets": {p: {"longitude": round(pos[p]["longitude"], 4), "sign": ephem.SIGNS[int(pos[p]["longitude"] // 30) % 12]} for p in planets_to_check if p in pos}
        }

    ephem.set_ayanamsa_mode(saved_mode)
    return {"julian_day": jd, "modes": results}

@router.post("/kundli/corpus/planetary-placements", summary="In-depth Graha Rashi and Drekkana decanate readings for all planets")
def planetary_placements_corpus(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    corpus_res = generate_comprehensive_corpus_reading(pos, asc)
    corpus_res["name"] = req.name
    return corpus_res

@router.post("/kundli/corpus/comprehensive-life", summary="Exhaustive classical life report combining Ascendant, Graha Rashi, 144 Lords, 12 Shad Phala, and Yogas")
def comprehensive_life_corpus(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    
    corpus_res = generate_comprehensive_corpus_reading(pos, asc)
    reading = generate_holistic_reading(pos, asc)
    yogas = evaluate_all_yogas(pos, asc)
    karakas = compute_jaimini_karakas(pos)
    vargas = build_all_vargas(pos, asc)
    
    target_dt = req.target_date or _dt.now(_tz.utc).date()
    target_jd = ephem.jd_from_utc(_dt.combine(target_dt, _dt.min.time(), tzinfo=_tz.utc))
    current_dasha = get_current_dasha(pos["Moon"]["longitude"], birth_jd, target_jd, tz)
    
    return {
        "name": req.name,
        "ayanamsa": req.ayanamsa,
        "ascendant_portfolio": corpus_res["ascendant_portfolio"],
        "ascendant_drekkana": corpus_res["ascendant_drekkana"],
        "graha_rashi_readings": corpus_res["graha_rashi_readings"],
        "house_lords": reading["house_lords"],
        "shad_phala": reading["shad_phala"],
        "navamsha_synthesis": reading.get("navamsha_synthesis"),
        "kharesh_diagnostic": reading.get("kharesh_diagnostic"),
        "yogas": yogas,
        "karakas": karakas,
        "vargottama": vargas["vargottama"],
        "varga_strengths": vargas["varga_strengths"],
        "current_dasha": current_dasha,
    }

@router.post("/kundli/tajika/sahams", summary="All 24 Classical Tajika Sahams, 150 Nadiamshas, and Medical Drekkana Body Parts")
def tajika_sahams_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc_lon, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    sun_lon = pos.get("Sun", {}).get("longitude", 0.0)
    sun_house = (int(sun_lon // 30) - int(asc_lon // 30)) % 12 + 1
    is_day = sun_house in (7, 8, 9, 10, 11, 12)
    
    sahams = compute_tajika_sahams(pos, asc_lon, is_day_birth=is_day)
    nadi = get_nadiamsha(asc_lon)
    drekk = get_drekkana_body_part(asc_lon)
    return {
        "name": req.name,
        "is_day_birth": is_day,
        "sahams": sahams,
        "ascendant_nadiamsha": nadi,
        "ascendant_drekkana_body_part": drekk
    }

@router.post("/kundli/special-lagnas", summary="All Classical Special Lagnas (Hora, Ghati, Bhava, Sree, Indu, Pranapada, Paka) and 12 Arudha Padas")
def special_lagnas_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc_lon, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    sun_lon = pos.get("Sun", {}).get("longitude", 0.0)
    moon_lon = pos.get("Moon", {}).get("longitude", 0.0)
    
    res = compute_special_lagnas(birth_jd, req.latitude, req.longitude, asc_lon, sun_lon, moon_lon, pos)
    res["name"] = req.name
    res["ayanamsa"] = req.ayanamsa
    return res

@router.post("/kundli/ashtakavarga/reductions", summary="Ashtakavarga Suite: BAV, SAV, Trikona Shodhana, Ekadhipatya Shodhana, Shodhya Pindas, and Kakshas")
def ashtakavarga_reductions_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc_lon, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    
    sign_of = {p: int(pos[p]["longitude"] // 30) for p in ephem.VEDIC_PLANETS}
    sign_of["Lagna"] = int(asc_lon // 30)
    
    res = full_ashtakavarga_suite(sign_of, pos, asc_lon)
    res["name"] = req.name
    res["ayanamsa"] = req.ayanamsa
    return res

@router.post("/kundli/sudarshan", summary="Sudarshan Chakra 3-ring concentric wheel (Lagna, Chandra, Surya) SVG and House Analysis")
def sudarshan_chakra_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc_lon, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    
    asc_s = int(asc_lon // 30)
    moon_s = int(pos["Moon"]["longitude"] // 30)
    sun_s = int(pos["Sun"]["longitude"] // 30)
    
    pls = []
    for p in ephem.VEDIC_PLANETS:
        L = pos[p]["longitude"]
        s = int(L // 30)
        retro = pos[p]["speed"] < 0 if p not in ("Rahu", "Ketu") else True
        pls.append({"name": p, "sign": s, "longitude": L, "retrograde": retro})
        
    svg = sudarshan_chakra_svg(asc_s, moon_s, sun_s, pls, size=560, title=f"Sudarshan Chakra - {req.name or 'Native'}")
    
    sectors = []
    for h in range(12):
        s_lagna = (asc_s + h) % 12
        s_moon = (moon_s + h) % 12
        s_sun = (sun_s + h) % 12
        p_lagna = [p["name"] for p in pls if p["sign"] == s_lagna]
        p_moon = [p["name"] for p in pls if p["sign"] == s_moon]
        p_sun = [p["name"] for p in pls if p["sign"] == s_sun]
        sectors.append({
            "house": h + 1,
            "lagna_sign": ephem.SIGNS[s_lagna],
            "lagna_planets": p_lagna,
            "moon_sign": ephem.SIGNS[s_moon],
            "moon_planets": p_moon,
            "sun_sign": ephem.SIGNS[s_sun],
            "sun_planets": p_sun,
        })
        
    return {
        "name": req.name,
        "ayanamsa": req.ayanamsa,
        "lagna_sign": ephem.SIGNS[asc_s],
        "moon_sign": ephem.SIGNS[moon_s],
        "sun_sign": ephem.SIGNS[sun_s],
        "svg": svg,
        "sectors": sectors
    }

@router.post("/kundli/varshaphala", summary="Varshaphala Annual Solar Return: Muntha, Varshesha Year Lord, Mudda Dasha, Sahams, Tajika Yogas")
def varshaphala_endpoint(req: VarshaphalaRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    y = req.year or _dt.now(tz).year
    
    res = varshaphal(dt_utc, req.latitude, req.longitude, y, tz)
    res["name"] = req.name
    res["ayanamsa"] = req.ayanamsa
    
    # Calculate all 24 classical Tajika Sahams for the Varsha Pravesha moment
    varsha_utc = _dt.fromisoformat(res["solar_return_moment"].replace("Z", "+00:00")) if "T" in res["solar_return_moment"] else dt_utc
    varsha_jd = ephem.jd_from_utc(varsha_utc)
    v_pos = ephem.all_positions(varsha_jd, sidereal=True, true_node=req.true_node)
    v_cusps, v_asc, v_mc = ephem.houses(varsha_jd, req.latitude, req.longitude, HS[req.house_system], True)
    
    full_sahams = compute_tajika_sahams(v_pos, v_asc, is_day_birth=res["birth_in_day"])
    res["sahams_full_24"] = full_sahams
    return res

@router.post("/kundli/kp", summary="KP System: Placidus cusps, four-level lords, significators and ruling planets")
def kp_endpoint(req: KPRequest):
    dt_utc = birth_utc(req)
    if req.horary_number:
        res = kp_horary_chart(req.horary_number, dt_utc, req.latitude, req.longitude)
    else:
        res = kp_chart(dt_utc, req.latitude, req.longitude)
    res["name"] = req.name
    return res

@router.post("/kundli/worksheets", summary="Synchronized multi-chart layout presets matching classical astrological worksheets")
def worksheets_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    
    k = compute_kundli(dt_utc, req.latitude, req.longitude, tz, req.true_node, req.dasha_levels, HS[req.house_system])
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    cusps, asc_lon, mc = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    vargas = build_all_vargas(pos, asc_lon)
    
    sun_lon = pos.get("Sun", {}).get("longitude", 0.0)
    moon_lon = pos.get("Moon", {}).get("longitude", 0.0)
    special_lagnas = compute_special_lagnas(birth_jd, req.latitude, req.longitude, asc_lon, sun_lon, moon_lon, pos)
    
    sign_of = {p: int(pos[p]["longitude"] // 30) for p in ephem.VEDIC_PLANETS}
    sign_of["Lagna"] = int(asc_lon // 30)
    av_suite = full_ashtakavarga_suite(sign_of, pos, asc_lon)
    
    now_jd = ephem.jd_from_utc(_dt.now(_tz.utc))
    curr_dasha = get_current_dasha(moon_lon, birth_jd, now_jd, tz)
    
    pls = [{"name": p, "sign": int(pos[p]["longitude"] // 30), "longitude": pos[p]["longitude"], "retrograde": pos[p]["speed"] < 0} for p in ephem.VEDIC_PLANETS]
    sudarshan_svg = sudarshan_chakra_svg(int(asc_lon // 30), int(moon_lon // 30), int(sun_lon // 30), pls, size=480)
    
    return {
        "name": req.name,
        "ayanamsa": req.ayanamsa,
        "birth_chart": {
            "lagna": k["lagna"],
            "moon": k["moon"],
            "planets": k["planets"],
            "current_dasha": curr_dasha
        },
        "vargas_core_four": {
            "D1": vargas["vargas"]["D1"],
            "D9": vargas["vargas"]["D9"],
            "D10": vargas["vargas"]["D10"],
            "D3": vargas["vargas"]["D3"]
        },
        "sudarshan": {
            "svg": sudarshan_svg,
            "lagna_sign": ephem.SIGNS[int(asc_lon // 30)],
            "moon_sign": ephem.SIGNS[int(moon_lon // 30)],
            "sun_sign": ephem.SIGNS[int(sun_lon // 30)]
        },
        "special_lagnas": special_lagnas,
        "ashtakavarga": {
            "sav": av_suite["sarvashtakavarga"],
            "sav_total": av_suite["sav_total"],
            "shodhita_sav": av_suite["shodhita_sav"],
            "shodhita_sav_total": av_suite["shodhita_sav_total"],
            "shodhya_pindas": av_suite["shodhya_pindas"]
        },
        "shadbala": k.get("shadbala", {})
    }

@router.post("/kundli/prashna", summary="Classical Vedic Prashna (Horary): Tajika Yogas, Karyesha, verdict & timing")
def prashna_endpoint(req: PrashnaRequest):
    if req.date and req.time:
        from datetime import datetime as _dt_cls
        dt_local = _dt_cls.combine(req.date, req.time)
        tz = ephem.make_tz(req.timezone, req.utc_offset)
        dt_utc = dt_local.replace(tzinfo=tz).astimezone(_tz.utc)
    else:
        dt_utc = _dt.now(_tz.utc)
    return evaluate_prashna(dt_utc, req.latitude, req.longitude, req.query_category)

@router.post("/kundli/soul-guidance", summary="Soul's Desires (Atmakaraka), Ishta Devata & Purushartha Life Goals Matrix")
def soul_guidance_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    jd = ephem.jd_from_utc(dt_utc)
    pos = ephem.all_positions(jd, sidereal=True, true_node=req.true_node)
    cusps, asc, mc = ephem.houses(jd, req.latitude, req.longitude, HS[req.house_system], True)
    return compute_soul_guidance(pos, asc)

@router.post("/kundli/remedies-corpus", summary="Exhaustive Classical Remedial Dossier: Japa Mantras, counts, malas, & soul guidance")
def remedies_corpus_endpoint(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    k = wrap(compute_kundli, birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
             req.true_node, req.dasha_levels, HS[req.house_system])
    return get_complete_remedies_for_chart(k)

@router.get("/kundli/mantras", summary="Classical Japa Mantras, Beej, Puranic, Gayatri, & counts for all 9 Grahas")
def mantras_catalog():
    return {"grahas": GRAHA_REMEDIES}



def _run_destiny(req: DestinyRequest):
    return wrap(
        compute_master_destiny_dossier,
        birth_utc(req),
        req.latitude,
        req.longitude,
        req.timezone,
        req.utc_offset,
        req.name,
        req.current_latitude,
        req.current_longitude,
        req.current_timezone,
        req.current_utc_offset,
        req.current_city,
        req.target_date,
        req.scan_days,
        req.ayanamsa,
    )

@router.post("/kundli/destiny-dossier", summary="Master Cross-Linked Destiny Dossier: Diseases, Longevity, Accidents, Lottery, Marriage, Progeny/Grandkids, Past/Future Life & 9-Planet Mastery")
def destiny_dossier_endpoint(req: DestinyRequest):
    return _run_destiny(req)

@router.post("/kundli/medical-longevity", summary="Ayurvedic Tridosha, Organ & Disease Vulnerabilities, BPHS Ayurdaya Longevity, Marakas & Mrityu Bhaga")
def medical_longevity_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
        "medical_diseases_and_longevity": res["medical_diseases_and_longevity"],
    }

@router.post("/kundli/accidents-safety", summary="Natal D1/D8 Accident Susceptibility & Location-Calibrated Exact Danger/Safe Dates & Horas")
def accidents_safety_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "current_location_anchor": res["current_location_anchor"],
        "accidents_and_safety_windows": res["accidents_and_safety_windows"],
    }

@router.post("/kundli/destiny-dates", summary="Lifelong Bhrigu Turning Ages, Dasha Junctions, Location-Calibrated Good/Bad Dates & Chronic Bad-Luck Reset")
def destiny_dates_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "current_location_anchor": res["current_location_anchor"],
        "destiny_turning_points_and_dates": res["destiny_turning_points_and_dates"],
    }

@router.post("/kundli/lottery-windfall", summary="Indu Lagna, 5th/8th/11th Windfall Yogas, Location-Calibrated Golden Lottery Dates, Horas & Lucky Numbers")
def lottery_windfall_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "current_location_anchor": res["current_location_anchor"],
        "lottery_and_windfall_oracle": res["lottery_and_windfall_oracle"],
    }

@router.post("/kundli/marriage-analysis", summary="Number of Marriages/Unions Estimator, Upapada Lagna, Darakaraka, Timing & Ways to Fix Marriage")
def marriage_analysis_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
        "marriage_count_and_remedies": res["marriage_count_and_remedies"],
    }

@router.post("/kundli/progeny-lineage", summary="Fertility (Beeja/Kshetra Sphuta), D-7 Saptamsha Number of Children & Grandchildren's Future Destiny")
def progeny_lineage_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
        "progeny_children_and_grandchildren": res["progeny_children_and_grandchildren"],
    }

@router.post("/kundli/past-future-life", summary="Past Life (D-60 & Ketu), Active Past-Life Rinas & Fixes, This Life's Purpose & Future Life/Moksha Trajectory")
def past_future_life_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
        "past_life_future_life_and_purpose": res["past_life_future_life_and_purpose"],
    }

@router.post("/kundli/planetary-mastery", summary="Samhita 9-Planet Control Matrix: Gemstones, Shlokas, Deity Worship Schedule & Keep-Close vs Avoid Guide")
@router.post("/kundli/ravana-mastery", include_in_schema=False)
def planetary_mastery_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
        "samhita_planetary_mastery": res["ravana_samhita_planetary_mastery"],
        "ravana_samhita_planetary_mastery": res["ravana_samhita_planetary_mastery"],
    }



@router.post("/kundli/astro-vastu", summary="Personalized Birth-Chart Astro-Vastu Synthesis, 9-Zone Map, Do's/Don'ts & Plain-English Glossary")
def astro_vastu_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
        "astro_vastu_guide": res["astro_vastu_guide"],
        "plain_english_glossary": res["plain_english_glossary"],
    }


@router.get("/meta", tags=["Core"], summary="Contract versions and the enums an SDK should generate from")
def api_meta():
    from ...core.astro_vastu_engine import ITEM_RULES, GATE_MECHANISM_RULES
    return {
        "schema_version": "2026.10.23",
        "engine": "panchanghub",
        "vastu_item_types": sorted(ITEM_RULES),
        "gate_mechanisms": sorted(GATE_MECHANISM_RULES),
        "directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        "palm_detection_methods": ["explicit", "byte-hash"],
        "palm_note": "A photo without landmarks is labeled byte-hash. An empty palm body is rejected.",
    }


@router.get("/vastu/catalog", tags=["Vastu, Astro-Vastu & Feng Shui"], summary="Complete Catalog of 45+ Vastu & Feng Shui Items, Gate Sliding/Swing Mechanics, Photo/TV Wall Sides, Trench Flow & 9 Zones")
def vastu_catalog_endpoint():
    from ...core.astro_vastu_engine import (
        ITEM_RULES, GATE_MECHANISM_RULES, WALL_SIDE_LABELS,
        DIRECTION_META, FENG_SHUI_BAGUA_SECTORS,
    )
    return {
        "total_items": len(ITEM_RULES),
        "items_catalog": ITEM_RULES,
        "gate_opening_and_sliding_mechanisms": GATE_MECHANISM_RULES,
        "wall_mounting_sides": WALL_SIDE_LABELS,
        "trench_drainage_directions": ["NE", "N", "E", "NW", "SE", "W", "S", "SW", "stagnant"],
        "placement_scopes": ["indoor", "outdoor", "outside_boundary"],
        "house_shapes": ["square", "wide_rectangle", "deep_rectangle"],
        "vastu_nine_zones": DIRECTION_META,
        "feng_shui_bagua_nine_sectors": FENG_SHUI_BAGUA_SECTORS,
    }


@router.post("/vastu/personalized-preset", tags=["Vastu, Astro-Vastu & Feng Shui"], summary="Generate Personalized Birth-Chart Ideal Vastu & Feng Shui Arrangement (Items, Walls, Fence Loop) + Baseline Evaluation")
def vastu_personalized_preset_endpoint(req: TraditionsReportRequest):
    from ...core.astro_vastu_engine import (
        compute_personalized_astro_vastu, compute_classical_feng_shui,
        evaluate_visual_vastu_layout,
    )
    ephem.set_ayanamsa_mode(req.ayanamsa)
    jd = ephem.jd_from_utc(birth_utc(req))
    pos = ephem.all_positions(jd, sidereal=True, true_node=req.true_node)
    _, asc_lon, _ = ephem.houses(jd, req.latitude, req.longitude, HS[req.house_system], True)
    av = compute_personalized_astro_vastu(pos, asc_lon)
    fs = compute_classical_feng_shui(req.date.year, req.date.month, req.date.day, req.gender or "male", pos=pos, asc_lon=asc_lon)
    preset = av["personalized_chart_preset"]
    baseline_eval = evaluate_visual_vastu_layout(
        items=preset["items"],
        house_shape="square",
        has_outer_lot=True,
        compass_rotation=0.0,
        pos=pos,
        asc_lon=asc_lon,
        walls=preset["walls"],
        fences=preset["fences"],
    )
    return {
        "personalized_chart_preset": preset,
        "astro_vastu_guide": av,
        "classical_feng_shui": fs,
        "baseline_evaluation": baseline_eval,
    }


@router.post("/vastu/analyze-layout", tags=["Vastu, Astro-Vastu & Feng Shui"], summary="Evaluate Interactive Visual House & Outer-Lot Vastu + Feng Shui Layout with Birth-Chart & Uploaded Palm Synergy")
@router.post("/vastu/evaluate", include_in_schema=False)
def analyze_visual_vastu_layout_endpoint(req: VisualVastuLayoutRequest):
    from ...core.astro_vastu_engine import (
        evaluate_visual_vastu_layout, compute_personalized_astro_vastu,
        compute_classical_feng_shui, build_personalized_chart_preset, ITEM_RULES,
    )
    from ...core.palmistry_vision import analyze_palm_photo, PalmInputError

    payload = req.model_dump()
    warnings: list = []
    raw_items = payload.get("items") or []
    items = [it if isinstance(it, dict) else dict(it) for it in raw_items]
    unknown = sorted({str(it.get("type", "")).lower() for it in items if str(it.get("type", "")).lower() not in ITEM_RULES})
    if unknown:
        raise HTTPException(422, detail={"code": "UNKNOWN_ITEM_TYPE", "unknown": unknown, "allowed": sorted(ITEM_RULES)})
    raw_walls = payload.get("walls")
    walls = [w if isinstance(w, dict) else dict(w) for w in raw_walls] if raw_walls is not None else None
    raw_fences = payload.get("fences")
    fences = [f if isinstance(f, dict) else dict(f) for f in raw_fences] if raw_fences is not None else None

    house_shape = payload.get("house_shape", "square")
    has_outer_lot = bool(payload.get("has_outer_lot", True))
    compass_rotation = float(payload.get("compass_rotation", 0.0))

    pos = None
    asc_lon = None
    astro_vastu_guide = None
    classical_feng_shui = None
    b_date = payload.get("date") or payload.get("birth_date")
    b_lat = payload.get("latitude") if payload.get("latitude") is not None else (payload.get("lat") if payload.get("lat") is not None else payload.get("birth_latitude"))
    b_lon = payload.get("longitude") if payload.get("longitude") is not None else (payload.get("lon") if payload.get("lon") is not None else payload.get("birth_longitude"))
    b_time = payload.get("time") or payload.get("birth_time") or "10:30:00"
    b_tz = payload.get("timezone") if payload.get("timezone") is not None else (payload.get("tz") if payload.get("tz") is not None else payload.get("birth_timezone", "Asia/Kolkata"))
    b_gender = payload.get("gender") or "male"

    if b_date and b_lat is not None and b_lon is not None:
        try:
            try:
                tz_name, utc_off = None, float(b_tz)
            except (ValueError, TypeError):
                tz_name, utc_off = str(b_tz), None
            b_req = DestinyRequest(
                date=b_date,
                time=b_time,
                latitude=float(b_lat),
                longitude=float(b_lon),
                timezone=tz_name,
                utc_offset=utc_off,
            )
            ephem.set_ayanamsa_mode(b_req.ayanamsa)
            jd = ephem.jd_from_utc(birth_utc(b_req))
            pos = ephem.all_positions(jd, sidereal=True, true_node=False)
            _, asc_lon, _ = ephem.houses(jd, b_req.latitude, b_req.longitude, "W", True)
            astro_vastu_guide = compute_personalized_astro_vastu(pos, asc_lon)
            classical_feng_shui = compute_classical_feng_shui(
                b_req.date.year, b_req.date.month, b_req.date.day, b_gender,
                pos=pos, asc_lon=asc_lon,
                sitting=payload.get("sitting"), facing=payload.get("facing"),
            )
        except Exception:
            warnings.append({"code": "CHART_FAILED", "message": "Birth chart was not applied. Check date, time, latitude, longitude, and timezone."})

    if not items and payload.get("use_chart_ideal_preset_if_empty"):
        preset = build_personalized_chart_preset(pos, asc_lon)
        items = preset["items"]
        if walls is None:
            walls = preset["walls"]
        if fences is None:
            fences = preset["fences"]

    # Resolve optional palm photo or palm feature parameters via Computer-Vision Palmistry Engine
    palm_data = payload.get("palm_data")
    full_palm_report = None
    palm_img = payload.get("palm_image_base64") or (palm_data.get("image_base64") if isinstance(palm_data, dict) else None)
    has_direct_palm_overrides = any(payload.get(k) for k in ("hand_shape", "life_line", "head_line", "heart_line", "fate_line", "thumbprint_type"))
    if palm_img or has_direct_palm_overrides:
        try:
            p_src = palm_data if isinstance(palm_data, dict) else {}
            full_palm_report = analyze_palm_photo(
                image_base64=palm_img,
                thumb_image_base64=payload.get("thumb_image_base64") or p_src.get("thumb_image_base64"),
                hand_side=p_src.get("hand_side") or "right",
                hand_shape=payload.get("hand_shape") or p_src.get("hand_shape"),
                heart_line=payload.get("heart_line") or p_src.get("heart_line"),
                head_line=payload.get("head_line") or p_src.get("head_line"),
                life_line=payload.get("life_line") or p_src.get("life_line"),
                fate_line=payload.get("fate_line") or p_src.get("fate_line"),
                thumbprint_type=payload.get("thumbprint_type") or p_src.get("thumbprint_type"),
                birth_date=str(b_date) if b_date else None,
                birth_time=str(b_time or "10:30:00"),
                latitude=float(b_lat) if b_lat is not None else None,
                longitude=float(b_lon) if b_lon is not None else None,
                timezone_str=str(b_tz or "Asia/Kolkata"),
            )
            palm_data = full_palm_report["extracted_palm_profile"]
        except PalmInputError as exc:
            warnings.append({"code": "PALM_INPUT", "message": str(exc)})
        except Exception:
            warnings.append({"code": "PALM_FAILED", "message": "The palm photo could not be read."})

    res = evaluate_visual_vastu_layout(
        items=items,
        house_shape=house_shape,
        has_outer_lot=has_outer_lot,
        compass_rotation=compass_rotation,
        pos=pos,
        asc_lon=asc_lon,
        walls=walls,
        fences=fences,
        palm_data=palm_data,
        auspicious_dirs=list((classical_feng_shui or {}).get("four_auspicious_directions", {}).values()) if classical_feng_shui else None,
        land_high=payload.get("land_high"),
        roads=payload.get("roads"),
        plot_cuts=payload.get("plot_cuts"),
        plot_extensions=payload.get("plot_extensions"),
    )
    res["warnings"] = warnings
    res["schema_version"] = "2026.10.23"
    if astro_vastu_guide is not None:
        res["astro_vastu_guide"] = astro_vastu_guide
    if classical_feng_shui is not None:
        res["classical_feng_shui"] = classical_feng_shui
    if full_palm_report is not None:
        res["full_palmistry_and_astrology_report"] = {
            "extracted_palm_profile": full_palm_report["extracted_palm_profile"],
            "palm_and_astrology_synthesis": full_palm_report["palm_and_astrology_synthesis"],
            "palm_and_vastu_synthesis": full_palm_report["palm_and_vastu_synthesis"],
        }
    return res


@router.post("/vastu/feng-shui", summary="Classical Feng Shui: Personal Kua (Ming Gua), Eight Mansions (Ba Zhai), Bagua 9-Grid & Period 9 Flying Stars")
def vastu_feng_shui_endpoint(req: TraditionsReportRequest):
    from ...core.astro_vastu_engine import compute_classical_feng_shui
    ephem.set_ayanamsa_mode(req.ayanamsa)
    jd = ephem.jd_from_utc(birth_utc(req))
    pos = ephem.all_positions(jd, sidereal=True, true_node=req.true_node)
    _, asc_lon, _ = ephem.houses(jd, req.latitude, req.longitude, HS[req.house_system], True)
    return compute_classical_feng_shui(
        req.date.year, req.date.month, req.date.day, req.gender or "male",
        pos=pos, asc_lon=asc_lon, sitting=getattr(req, "sitting", None), facing=getattr(req, "facing", None),
    )


# ==============================================================================
# GLOBAL & CLASSICAL ASTROLOGICAL TRADITIONS + DOSHA / FIVE ELEMENTS API
# ==============================================================================

@router.get("/traditions/catalog", tags=["Global Traditions & Doshas"], summary="Catalog of all 14 Eastern/Vedic, Western & Global astrological traditions, goals, and schools")
def traditions_catalog_endpoint():
    from ...core.traditions_engine import get_traditions_catalog
    return get_traditions_catalog()


@router.post("/traditions/report", tags=["Global Traditions & Doshas"], summary="Customizable Multi-Tradition Astrological Report with Vata-Pitta-Kapha & Chinese Five Elements Balance")
def traditions_report_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    ephem.set_ayanamsa_mode(req.ayanamsa)
    return wrap(
        compute_traditions_report,
        birth_utc(req),
        req.latitude,
        req.longitude,
        ephem.make_tz(req.timezone, req.utc_offset),
        req.name or "Native",
        req.gender or "male",
        req.selected_traditions or req.traditions,
        req.goal or req.focus_mode or "all",
        req.approach or req.school_preference or "all",
    )


@router.post("/traditions/dosha-element-balance", tags=["Global Traditions & Doshas"], summary="Ayurvedic Tridosha (Vata, Pitta, Kapha) × Chinese Five Elements (Wood, Fire, Earth, Metal, Water) Constitutional Balance")
def traditions_dosha_element_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req),
        req.latitude,
        req.longitude,
        ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native",
        gender=req.gender,
        selected_traditions=["dosha_and_elements"],
    )
    return res["traditions"]["dosha_and_elements"]


@router.post("/traditions/lal-kitab", tags=["Global Traditions & Doshas"], summary="Detailed Lal Kitab Report: Fixed Aries Ascendant (Pakka Ghar), SVG Chart, Sleeping Planets, Rinas, Palmistry Links & 43-Day Upayas")
def traditions_lal_kitab_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["lal_kitab"],
    )
    return res["traditions"]["lal_kitab"]


@router.post("/traditions/jaimini", tags=["Global Traditions & Doshas"], summary="Detailed Jaimini Sutras Report: 7 Chara Karakas, Karakamsha, Arudha Padas (AL, UL, A7, A10), Rashi Drishti & Chara Dasha")
def traditions_jaimini_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["jaimini"],
    )
    return res["traditions"]["jaimini"]


@router.post("/traditions/nadi", tags=["Global Traditions & Doshas"], summary="Detailed Nadi Astrology Report: 150 Nadi Amshas, Thumbprint Archetypes, Bhrigu Nandi Nadi Circuits & 14 Kandams")
def traditions_nadi_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["nadi"],
    )
    return res["traditions"]["nadi"]


@router.post("/traditions/hellenistic", tags=["Global Traditions & Doshas"], summary="Detailed Hellenistic Astrology Report: Sect (Day/Night), Whole-Sign Houses, Lots of Fortune & Spirit, Annual Profections")
def traditions_hellenistic_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["hellenistic"],
    )
    return res["traditions"]["hellenistic"]


@router.post("/traditions/evolutionary", tags=["Global Traditions & Doshas"], summary="Modern Psychological & Evolutionary Astrology: Jungian Archetypes, Pluto Soul Evolution, PPP & Lunar Nodes")
def traditions_evolutionary_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["psychological_evolutionary"],
    )
    return res["traditions"]["psychological_evolutionary"]


@router.post("/traditions/uranian", tags=["Global Traditions & Doshas"], summary="Uranian / Hamburg School Astrology: 8 Trans-Neptunian Planets (Cupido..Poseidon), 90° Dial & Planetary Midpoints")
def traditions_uranian_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["uranian_hamburg"],
    )
    return res["traditions"]["uranian_hamburg"]


@router.post("/traditions/feng-shui", tags=["Global Traditions & Doshas"], summary="Classical Feng Shui Report: Kua Number, Eight Mansions, Bagua 9-Grid, Period 9 Flying Stars & Form School")
def traditions_feng_shui_endpoint(req: TraditionsReportRequest):
    from ...core.traditions_engine import compute_traditions_report
    res = compute_traditions_report(
        birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native", gender=req.gender, selected_traditions=["feng_shui"],
    )
    return res["traditions"]["feng_shui"]


# ==============================================================================
# MULTI-SPECTRUM COMPUTER-VISION PALMISTRY & NADI THUMBPRINT API
# ==============================================================================

@router.get("/palmistry/spectrum-modes", tags=["Palmistry Vision"], summary="List all 10 color & spectral imaging modes for palm line, mount, and Nadi thumbprint inspection")
def palmistry_spectrum_modes_endpoint():
    from ...core.palmistry_vision import get_spectrum_modes_catalog
    return get_spectrum_modes_catalog()


@router.post("/palmistry/analyze-photo", tags=["Palmistry Vision"], summary="Analyze palm & thumbprint photo across 10 spectral modes + Vedic birth-chart mount, Lal Kitab & Vastu synthesis")
def palmistry_analyze_photo_endpoint(req: PalmistryPhotoRequest):
    from ...core.palmistry_vision import analyze_palm_photo, PalmInputError
    try:
        return analyze_palm_photo(
            image_base64=req.image_base64,
            thumb_image_base64=req.thumb_image_base64,
            hand_side=req.hand_side or "right",
            active_spectrum=req.active_spectrum or "ridge_enhance",
            hand_shape=req.hand_shape,
            heart_line=req.heart_line,
            head_line=req.head_line,
            life_line=req.life_line,
            fate_line=req.fate_line,
            thumbprint_type=req.thumbprint_type,
            birth_date=req.birth_date or req.date,
            birth_time=req.birth_time or req.time or "12:00:00",
            latitude=req.latitude,
            longitude=req.longitude,
            timezone_str=req.timezone or "UTC",
        )
    except PalmInputError as exc:
        raise HTTPException(400, detail={"code": "PALM_INPUT", "message": str(exc)})


@router.post("/palmistry/combine-astrology", tags=["Palmistry Vision"], summary="Combine Uploaded Palm/Thumbprint Photo (or Palm Features) with Vedic Birth Chart, Lal Kitab & Nadi Astrology")
def palmistry_combine_astrology_endpoint(req: PalmistryPhotoRequest):
    from ...core.palmistry_vision import analyze_palm_photo, PalmInputError
    try:
        res = analyze_palm_photo(
            image_base64=req.image_base64,
            thumb_image_base64=req.thumb_image_base64,
            hand_side=req.hand_side or "right",
            active_spectrum=req.active_spectrum or "ridge_enhance",
            hand_shape=req.hand_shape,
            heart_line=req.heart_line,
            head_line=req.head_line,
            life_line=req.life_line,
            fate_line=req.fate_line,
            thumbprint_type=req.thumbprint_type,
            birth_date=req.birth_date or req.date,
            birth_time=req.birth_time or req.time or "12:00:00",
            latitude=req.latitude,
            longitude=req.longitude,
            timezone_str=req.timezone or "UTC",
        )
    except PalmInputError as exc:
        raise HTTPException(400, detail={"code": "PALM_INPUT", "message": str(exc)})
    return {
        "schema_version": "2026.10.23",
        "warnings": res.get("warnings") or [],
        "extracted_palm_profile": res["extracted_palm_profile"],
        "nadi_thumbprint_analysis": res["nadi_thumbprint_analysis"],
        "ayurvedic_tridosha_hand_signature": res["ayurvedic_tridosha_hand_signature"],
        "birth_chart_and_lal_kitab_mount_links": res["birth_chart_and_lal_kitab_mount_links"],
        "palm_and_astrology_synthesis": res["palm_and_astrology_synthesis"],
        "palm_and_vastu_synthesis": res["palm_and_vastu_synthesis"],
    }


@router.post("/palmistry/combine-vastu", tags=["Palmistry Vision", "Vastu, Astro-Vastu & Feng Shui"], summary="Combine Uploaded Palm/Thumbprint Photo + Birth Chart + Vastu & Feng Shui Layout Evaluation")
def palmistry_combine_vastu_endpoint(req: VisualVastuLayoutRequest):
    # If caller didn't pass floorplan items, automatically evaluate against their Birth-Chart Ideal Vastu Preset
    if not req.items:
        req.use_chart_ideal_preset_if_empty = True
    return analyze_visual_vastu_layout_endpoint(req)




# ==============================================================================
# DETAILED MULTI-CHAPTER TEXT REPORTS, 22 DASHAS, 9 MENUS & RECTIFICATION STUDIO
# ==============================================================================

@router.get("/reports/catalog", tags=["Detailed Text Reports & 9 Menus"], summary="Complete catalog of all 20 Report Models (HC1..HC4, HP1..HP4, KP1..KP2, VC1..VC2, VP1..VP2, HM1..HM2, PH1..PH2, PV, MASTER_COMPLETE), 9 Top-Level Menus & Submenus, and 10 Research Worksheet Presets")
def reports_catalog_endpoint():
    from ...core.detailed_reports_engine import get_reports_and_menus_catalog
    return get_reports_and_menus_catalog()


@router.post("/reports/generate", tags=["Detailed Text Reports & 9 Menus"], summary="Generate a multi-chapter book-formatted Vedic Horoscope Dossier & Printable HTML for any Report Model (HP3, HC3, KP2, VP2, MASTER_COMPLETE, etc.)")
def reports_generate_endpoint(req: DetailedReportRequest):
    from ...core.detailed_reports_engine import generate_detailed_text_report
    ephem.set_ayanamsa_mode(req.ayanamsa)
    return generate_detailed_text_report(
        dt_utc=birth_utc(req),
        lat=req.latitude,
        lon=req.longitude,
        tz=ephem.make_tz(req.timezone, req.utc_offset),
        name=req.name or "Native",
        gender=req.gender or "male",
        model_code=req.model_code or "HP3",
        chapters=req.chapters,
        target_year=req.target_year,
    )


@router.post("/kundli/dashas/all-systems", tags=["Detailed Text Reports & 9 Menus"], summary="All 22 Classical Dasha Systems: 13 Nakshatra Dashas (Vimshottari, Ashtottari, Yogini, Kalachakra, Tribhagi, 8 Conditional) + 8 Jaimini & Rashi Dashas (Chara, Sthira, Narayana, Shoola, Niryaana Shoola, Drig, Navamsha, Lagna Kendradi)")
def all_22_dashas_endpoint(req: KundliRequest):
    from ...core.detailed_reports_engine import compute_all_22_dasha_systems
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    _, asc, _ = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    return compute_all_22_dasha_systems(pos, asc, birth_jd, tz)


@router.post("/kundli/upagrahas-and-sphutas", tags=["Detailed Text Reports & 9 Menus"], summary="11 Upagrahas (Dhuma..Yamaghantaka), 15 Mathematical Sphutas (Prana, Deha, Mrityu, Trisphuta, Beeja, Kshetra, Yogi/Avayogi, Bhrigu Bindu, Kunda), 4-System Avasthas, Panchadha Maitri & 27-Star Tarabala")
def upagrahas_and_sphutas_endpoint(req: KundliRequest):
    from ...core.detailed_reports_engine import (
        compute_avakhada_and_ghata_chakra,
        compute_upagrahas_sphutas_avasthas_maitri,
    )
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    _, asc, _ = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    ava = compute_avakhada_and_ghata_chakra(pos, asc, birth_jd, req.latitude, req.longitude, tz)
    upa = compute_upagrahas_sphutas_avasthas_maitri(pos, asc, birth_jd, req.latitude, req.longitude)
    return {**ava, **upa}


@router.post("/kundli/saturn-cycles-and-doshas", tags=["Detailed Text Reports & 9 Menus"], summary="3 Lifetime Cycles of Saturn Sadhesati, Laghu Kalyani Dhayya, Mangala Dosha (from Lagna/Moon/Venus + 12 Cancellations), and Gemstone Recommendations I & II (Life, Lucky & Destiny Stones)")
def saturn_cycles_and_doshas_endpoint(req: KundliRequest):
    from ...core.detailed_reports_engine import compute_saturn_cycles_mangala_and_gems
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    birth_jd = ephem.jd_from_utc(dt_utc)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=req.true_node)
    _, asc, _ = ephem.houses(birth_jd, req.latitude, req.longitude, HS[req.house_system], True)
    return compute_saturn_cycles_mangala_and_gems(pos, asc, birth_jd, tz)


@router.post("/tools/rectify-and-relocate", tags=["Detailed Text Reports & 9 Menus"], summary="Birth Time Rectifier (Lagna, D-9, D-10, D-60, Kunda & Pranapada exact shift boundaries), Astro-Relocation Tool, Panch Pakshi 5-Bird Bio-Rhythm, Navamsha Ages & SPICA Steps 1A–5 Worksheet")
def rectify_and_relocate_endpoint(req: RectifyRelocateRequest):
    from ...core.detailed_reports_engine import compute_rectification_and_relocation_tools
    ephem.set_ayanamsa_mode(req.ayanamsa)
    dt_utc = birth_utc(req)
    tz = ephem.make_tz(req.timezone, req.utc_offset)
    return compute_rectification_and_relocation_tools(
        dt_utc=dt_utc,
        lat=req.latitude,
        lon=req.longitude,
        tz=tz,
        target_lat=req.target_latitude,
        target_lon=req.target_longitude,
        target_city=req.target_city,
    )


@router.post("/tools/rectify-time", tags=["Detailed Text Reports & 9 Menus"], summary="Birth Time Rectifier: Exact minute/second boundary shifts for Rashi, Drekkana, Navamsha, Dashamsha, Shashtiamsha, Kunda & Pranapada")
def rectify_time_endpoint(req: RectifyRelocateRequest):
    res = rectify_and_relocate_endpoint(req)
    return res["birth_time_rectification"]


@router.post("/tools/relocate-chart", tags=["Detailed Text Reports & 9 Menus"], summary="Change Location / Astro-Relocation Tool: Compare Natal vs Relocated Ascendant, Midheaven & Planetary House Shifts")
def relocate_chart_endpoint(req: RectifyRelocateRequest):
    res = rectify_and_relocate_endpoint(req)
    return res["astro_relocation"]

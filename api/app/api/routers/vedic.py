from datetime import datetime as _dt, timezone as _tz
from fastapi import APIRouter
from ...models import KundliRequest, MatchRequest, VarshaphalaRequest, KPRequest, PrashnaRequest, DestinyRequest
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


router = APIRouter(tags=["Kundli & Matching"])
HS = {"whole_sign": "W", "placidus": "P", "equal": "E"}

@router.post("/kundli", summary="Vedic birth chart: lagna, planets, D1–D60, dashas, ashtakavarga, doshas, yogas")
def kundli(req: KundliRequest):
    ephem.set_ayanamsa_mode(req.ayanamsa)
    k = wrap(compute_kundli, birth_utc(req), req.latitude, req.longitude, ephem.make_tz(req.timezone, req.utc_offset),
             req.true_node, req.dasha_levels, HS[req.house_system])
    k["name"] = req.name
    k["cross_linked_features"] = {
        "master_destiny_dossier": "/api/kundli/destiny-dossier",
        "medical_diseases_and_longevity": "/api/kundli/medical-longevity",
        "accidents_and_safety_windows": "/api/kundli/accidents-safety",
        "destiny_turning_dates_and_bad_luck_fix": "/api/kundli/destiny-dates",
        "lottery_and_windfall_oracle": "/api/kundli/lottery-windfall",
        "marriage_count_and_remedies": "/api/kundli/marriage-analysis",
        "progeny_children_and_grandchildren": "/api/kundli/progeny-lineage",
        "past_future_life_and_rinas": "/api/kundli/past-future-life",
        "ravana_samhita_planetary_mastery": "/api/kundli/ravana-mastery",
        "astro_numerology_synthesis": "/api/numerology/chart",
        "web_portal": "/destiny",
    }
    return k

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

@router.post("/matching", summary="Ashtakoota (36 guna) + 10 Porutham matching")
def matching(req: MatchRequest):
    b = moon_sid(ephem.jd_from_utc(birth_utc(req.boy))); g = moon_sid(ephem.jd_from_utc(birth_utc(req.girl)))
    return {"ashtakoota": ashtakoota(b, g), "porutham": porutham(b, g)}

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

@router.post("/kundli/kp", summary="Krishnamurti Paddhati (KP System): Placidus Cusps, 4-Level Lords, 4-Fold Significators, Ruling Planets")
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

@router.post("/kundli/destiny-dossier", summary="Master Cross-Linked Destiny Dossier: Diseases, Longevity, Accidents, Lottery, Marriage, Progeny/Grandkids, Past/Future Life & Ravana Mastery")
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

@router.post("/kundli/ravana-mastery", summary="Ravana Samhita 9-Planet Control Matrix: Gemstones, Shlokas, Deity Worship Schedule & Keep-Close vs Avoid Guide")
def ravana_mastery_endpoint(req: DestinyRequest):
    res = _run_destiny(req)
    return {
        "name": res["name"],
        "birth_chart_anchor": res["birth_chart_anchor"],
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


@router.post("/vastu/analyze-layout", summary="Evaluate Interactive Visual House (Square/Rectangle) & Outer-Lot Vastu Layout with Birth-Chart Synergy")
def analyze_visual_vastu_layout_endpoint(payload: dict):
    from ...core.astro_vastu_engine import evaluate_visual_vastu_layout
    items = payload.get("items") or []
    house_shape = payload.get("house_shape", "square")
    has_outer_lot = bool(payload.get("has_outer_lot", True))
    compass_rotation = float(payload.get("compass_rotation", 0.0))

    pos = None
    asc_lon = None
    b_date = payload.get("date") or payload.get("birth_date")
    b_lat = payload.get("latitude") if payload.get("latitude") is not None else payload.get("birth_latitude")
    b_lon = payload.get("longitude") if payload.get("longitude") is not None else payload.get("birth_longitude")
    if b_date and b_lat is not None and b_lon is not None:
        try:
            b_time = payload.get("time") or payload.get("birth_time") or "10:30:00"
            b_tz = payload.get("timezone") if payload.get("timezone") is not None else payload.get("birth_timezone", "Asia/Kolkata")
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
        except Exception:
            pass

    return evaluate_visual_vastu_layout(
        items=items,
        house_shape=house_shape,
        has_outer_lot=has_outer_lot,
        compass_rotation=compass_rotation,
        pos=pos,
        asc_lon=asc_lon,
    )

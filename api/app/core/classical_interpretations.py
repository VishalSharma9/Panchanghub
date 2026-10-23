"""Comprehensive Classical Astrological Interpretations with Scriptural Slokas.

Authentic, vendor-agnostic synthesis derived from:
- Brihat Parashara Hora Shastra (BPHS): Chapters 7, 8, 23, 26, 35
- Saravali of Kalyana Varma: Chapters 24, 30, 33, 49, 50, 51
- Brihat Jataka of Varahamihira & Jataka Parijata
- 16 Divisional Harmonic Charts (Shodashavargas: D1 to D60)
"""
from __future__ import annotations
import json, os
from typing import Dict, List, Any, Optional
from .ephem import SIGNS, RASHIS, SIGN_LORDS

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "classical_slokas.json")

_SLOKAS_CACHE = None
def _load_slokas() -> dict:
    global _SLOKAS_CACHE
    if _SLOKAS_CACHE is None:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _SLOKAS_CACHE = json.load(f)
        else:
            _SLOKAS_CACHE = {}
    return _SLOKAS_CACHE

def get_house_lord_sloka(lord_house: int, pos_house: int) -> Dict[str, str]:
    """Returns classical BPHS Chapter 26 verse and citation for Lord of House L in House P."""
    data = _load_slokas().get("bphs_house_lords", {})
    key = f"{lord_house}_{pos_house}"
    sloka_text = data.get(key, "")
    return {
        "verse": sloka_text,
        "source": "Brihat Parashara Hora Shastra, Ch. 26",
        "title": f"Lord of House {lord_house} in House {pos_house}"
    }

def get_navamsha_interpretation(d1_asc_sign: int, d1_asc_deg: float, moon_sign: int = None, moon_deg: float = None, ak_planet: str = None, ak_nav_sign: int = None) -> Dict[str, Any]:
    """Returns deep Navamsha (D9) interpretation with Saravali Ch. 51 slokas and Karakamsha."""
    corpus = _load_slokas()
    sara_navs = corpus.get("saravali_navamshas", {})
    bphs_kk = corpus.get("bphs_karakamsha", {})
    
    # Calculate D9 Lagna
    # 1 Navamsha = 3° 20' = 3.333333°
    nav_index = int(d1_asc_deg // (30.0 / 9.0))
    nav_index = min(max(nav_index, 0), 8)
    pada = nav_index + 1
    
    # Starting sign for Navamsha:
    # Fire signs (0, 4, 8) start from Aries (0)
    # Earth signs (1, 5, 9) start from Capricorn (9)
    # Air signs (2, 6, 10) start from Libra (6)
    # Water signs (3, 7, 11) start from Cancer (3)
    mod4 = d1_asc_sign % 4
    if mod4 == 0: start_sign = 0
    elif mod4 == 1: start_sign = 9
    elif mod4 == 2: start_sign = 6
    else: start_sign = 3
    
    d9_sign_idx = (start_sign + nav_index) % 12
    d9_sign = SIGNS[d9_sign_idx]
    d9_rashi = RASHIS[d9_sign_idx]
    d9_lord = SIGN_LORDS[d9_sign_idx]
    
    # Saravali Ch 51 key: (d1_asc_sign+1)_(d9_sign_idx+1)
    sara_key = f"{d1_asc_sign + 1}_{d9_sign_idx + 1}"
    sloka_text = sara_navs.get(sara_key, "")
    
    # Karakamsha
    kk_text = ""
    if ak_nav_sign is not None:
        kk_key = str(ak_nav_sign + 1)
        kk_text = bphs_kk.get(kk_key, "")
        
    # Vargottama check
    is_vargottama = (d1_asc_sign == d9_sign_idx)
    
    # Pushkara Navamsha check
    # Specific degree ranges are Pushkara
    pushkara_padas = {
        0: [3, 7], 1: [5, 7], 2: [6, 8], 3: [1, 3],
        4: [3, 7], 5: [5, 7], 6: [6, 8], 7: [1, 3],
        8: [3, 7], 9: [5, 7], 10: [6, 8], 11: [1, 3]
    }
    is_pushkara = pada in pushkara_padas.get(d1_asc_sign, [])
    
    # Deities of Navamshas: Deva, Nara, Rakshasa
    deities = ["Deva (Divine)", "Nara (Human)", "Rakshasa (Demonic)"]
    nav_deity = deities[nav_index % 3]

    return {
        "varga": "D9",
        "name": "Navamsha",
        "sanskrit": "नवांश",
        "domain": "Dharma, Soul Blueprint, Marriage & Inner Potential",
        "d9_lagna_sign": d9_sign,
        "d9_lagna_rashi": d9_rashi,
        "d9_lagna_lord": d9_lord,
        "navamsha_pada": pada,
        "deity": nav_deity,
        "is_vargottama": is_vargottama,
        "is_pushkara": is_pushkara,
        "saravali_sloka": sloka_text,
        "source": f"Saravali Ch. 51 & BPHS Ch. 35 (Navamsha {pada} of {SIGNS[d1_asc_sign]})",
        "saravali_source": f"Saravali of Kalyana Varma, Ch. 51 (Navamsha {pada} of {SIGNS[d1_asc_sign]})",
        "karakamsha_reading": kk_text,
        "karakamsha_source": f"Brihat Parashara Hora Shastra, Ch. 35 (Karakamsha in {SIGNS[ak_nav_sign] if ak_nav_sign is not None else ''})" if kk_text else "",
        "synthesis": (
            f"The rising Navamsha in {d9_sign} ({d9_rashi}) governed by {d9_lord} represents your subtle spiritual core and post-maturity dharma. "
            f"Occupying the {pada}{'st' if pada==1 else ('nd' if pada==2 else ('rd' if pada==3 else 'th'))} Pada under the {nav_deity} deity, "
            f"it reveals how your character and marital life unfold over time. "
            + ("Being Vargottama, your Ascendant gains immense potency and unshakeable resilience. " if is_vargottama else "")
            + ("Positioned in an auspicious Pushkara Navamsha, this confers divine protection, good fortune, and inner grace." if is_pushkara else "")
        )
    }

def get_22nd_drekkana_interpretation(asc_lon: float) -> Dict[str, Any]:
    """Calculates the 22nd Drekkana (Kharesh, 8th house cusp decanate from Lagna) with Saravali slokas."""
    corpus = _load_slokas()
    d22_data = corpus.get("drekkana_22_kharesh", {})
    
    # 22nd Drekkana is exactly 21 decanates ahead of Lagna decanate (7 signs = 210 degrees)
    # Lagna decanate index 0-35
    lag_drekk_idx = int(asc_lon // 10.0) % 36
    d22_idx = (lag_drekk_idx + 21) % 36 # 0-indexed
    d22_number = d22_idx + 1 # 1-indexed (1 to 36)
    
    sign_idx = d22_idx // 3
    decanate_in_sign = d22_idx % 3
    deg_start = decanate_in_sign * 10
    deg_end = deg_start + 10
    
    sign_name = SIGNS[sign_idx]
    rashi_name = RASHIS[sign_idx]
    
    # Drekkana Lord
    # 1st decanate owned by sign lord, 2nd by 5th lord, 3rd by 9th lord
    lord_sign = (sign_idx + (decanate_in_sign * 4)) % 12
    drekkana_lord = SIGN_LORDS[lord_sign]
    
    text = d22_data.get(str(d22_number), "")
    
    return {
        "varga": "D3",
        "name": "22nd Drekkana (Kharesh)",
        "sanskrit": "द्वाविंश द्वेष्काण",
        "decanate_number": d22_number,
        "sign": sign_name,
        "rashi": rashi_name,
        "degree_range": f"{deg_start}°–{deg_end}° {sign_name}",
        "drekkana_lord": drekkana_lord,
        "classical_text": text,
        "source": "Saravali Ch. 50 & Brihat Jataka Ch. 27",
        "guidance": (
            f"The 22nd Drekkana (Kharesh) falls in {deg_start}°–{deg_end}° {sign_name} ruled by {drekkana_lord}. "
            f"In classical Jyotish, planets transiting this point or owning this decanate require mindful health vigilance and spiritual remedies. "
            f"Benefic aspects from Jupiter or strong Lagna lord placement neutralize adverse implications."
        )
    }

def get_dashamsha_interpretation(d10_varga: dict, d1_10th_lord: str = "") -> Dict[str, Any]:
    """Returns Dashamsha (D10) professional and career authority interpretation."""
    asc = d10_varga.get("ascendant", {})
    sign = asc.get("sign_name", "Aries")
    rashi = asc.get("rashi", "Mesha")
    lord = asc.get("sign_lord", "Mars")
    
    # Count occupants of 10th house in D10
    planets = d10_varga.get("planets", [])
    h10_planets = [p["name"] for p in planets if p.get("house_from_varga_lagna") == 10]
    lag_planets = [p["name"] for p in planets if p.get("house_from_varga_lagna") == 1]
    
    career_focus = {
        "Aries": "Pioneering leadership, defense, surgery, sports, technology, and independent entrepreneurship.",
        "Taurus": "Finance, luxury assets, commerce, agriculture, banking, and high-end arts.",
        "Gemini": "Media, journalism, data communication, negotiation, IT, and marketing.",
        "Cancer": "Public relations, maritime trade, hospitality, healthcare, and administrative governance.",
        "Leo": "Executive authority, political administration, corporate leadership, and prestigious public roles.",
        "Virgo": "Diagnostics, analytical research, engineering auditing, medicine, and operational management.",
        "Libra": "Jurisprudence, diplomacy, commerce, arbitration, fashion, and public alliances.",
        "Scorpio": "Investigative research, crisis strategy, surgery, intelligence, and high-stakes transformation.",
        "Sagittarius": "Higher education, jurisprudence, advisory roles, institutional leadership, and publishing.",
        "Capricorn": "Corporate governance, heavy industry, public administration, and strategic infrastructure.",
        "Aquarius": "Scientific research, global NGOs, technology systems, aviation, and progressive reforms.",
        "Pisces": "Philanthropy, spiritual counseling, artistic creativity, international commerce, and healing."
    }.get(sign, "Distinguished executive capability and professional achievement.")
    
    return {
        "varga": "D10",
        "name": "Dashamsha",
        "sanskrit": "दशांश",
        "domain": "Career, Power, Profession, Status & Public Eminence (Mahat Phala)",
        "d10_lagna": f"{sign} ({rashi})",
        "d10_lagna_lord": lord,
        "career_sphere": career_focus,
        "tenth_house_occupants": h10_planets,
        "lagna_occupants": lag_planets,
        "source": "Brihat Parashara Hora Shastra, Ch. 8, Sloka 6 & Saravali Ch. 33",
        "classical_sloka": (
            "दशांशे महतोत्कर्षात् सर्वं कर्म विलोकयेत्। (Dashāṃśe mahatotkarṣāt sarvaṃ karma vilokayet - BPHS 8.6)\n"
            "Translation: 'From the Dashamsha chart, all matters of great authority, status, professional eminence, and the fruits of actions should be judged.' "
            "If the lord of Dashamsha Lagna and the 10th house are dignified and aspected by benefics, the native rises to esteemed leadership and commands lasting respect."
        )
    }

def get_varga_comprehensive_reading(varga_key: str, vdata: dict, k: dict = None) -> Dict[str, Any]:
    """Returns a rich, multi-paragraph classical reading for ANY of the 16 divisional charts."""
    vinfo = vdata.get("vargas", {}).get(varga_key, {})
    if not vinfo:
        return {}
        
    asc = vinfo.get("ascendant", {})
    sign = asc.get("sign_name", "Aries")
    rashi = asc.get("rashi", "Mesha")
    lord = asc.get("sign_lord", "Mars")
    
    if varga_key == "D9":
        # Compute D9 Navamsha
        d1_asc_sign = int(k["lagna"]["longitude"] // 30) if k else 0
        d1_asc_deg = (k["lagna"]["longitude"] % 30.0) if k else 0.0
        ak_sign = None
        if k and "karakas" in k:
            ak_sign = k["karakas"].get("karakamsha_sign_idx")
        return get_navamsha_interpretation(d1_asc_sign, d1_asc_deg, ak_nav_sign=ak_sign)
        
    elif varga_key == "D10":
        return get_dashamsha_interpretation(vinfo)
        
    elif varga_key == "D3":
        asc_lon = k["lagna"]["longitude"] if k else 0.0
        d22 = get_22nd_drekkana_interpretation(asc_lon)
        return {
            "varga": "D3",
            "name": "Drekkana",
            "sanskrit": "द्रेष्काण",
            "domain": "Siblings, Courage, Vitality, Energy & Co-borns",
            "d3_lagna": f"{sign} ({rashi})",
            "d3_lord": lord,
            "22nd_drekkana": d22,
            "classical_sloka": "द्रेष्काणे भ्रातृजं सौख्यम् (Dreshkāṇe bhrātṛjaṃ saukhyam - BPHS 8.2): 'From Drekkana, analyze brothers, sisters, courage, and bodily prowess.'",
            "source": "Brihat Parashara Hora Shastra Ch. 8 & Saravali Ch. 50"
        }
        
    elif varga_key == "D2":
        # Hora
        planets = vinfo.get("planets", [])
        sun_hora = [p["name"] for p in planets if p.get("sign_name") == "Leo"]
        moon_hora = [p["name"] for p in planets if p.get("sign_name") == "Cancer"]
        return {
            "varga": "D2",
            "name": "Hora",
            "sanskrit": "होरा",
            "domain": "Wealth, Treasury, Financial Resources & Sustenance",
            "d2_lagna": f"{sign} ({rashi})",
            "sun_hora_planets": sun_hora,
            "moon_hora_planets": moon_hora,
            "classical_sloka": "होरायां सम्पदादिकम् (Horāyāṃ sampadādikam - BPHS 8.2): 'From Hora, judge wealth, treasury, and prosperity.' Jupiter, Sun, and Mars thrive in Sun's Hora; Moon, Venus, and Saturn thrive in Moon's Hora; Mercury flourishes in both.",
            "source": "Brihat Parashara Hora Shastra Ch. 7-8 & Saravali Ch. 49"
        }
        
    elif varga_key == "D7":
        return {
            "varga": "D7",
            "name": "Saptamsha",
            "sanskrit": "सप्तांश",
            "domain": "Children, Progeny, Grandchildren & Creative Legacy",
            "d7_lagna": f"{sign} ({rashi})",
            "classical_sloka": "सप्तांशे पुत्रपौत्रादीन् (Saptāṃśe putra-pautrādīn - BPHS 8.3): 'From Saptamsha, assess sons, daughters, grandchildren, and ancestral succession.' Jupiter and the 5th house in D7 determine the flourishing of family lineage.",
            "source": "Brihat Parashara Hora Shastra Ch. 8, Sloka 3"
        }
        
    elif varga_key == "D12":
        return {
            "varga": "D12",
            "name": "Dwadashamsha",
            "sanskrit": "द्वादशांश",
            "domain": "Parents, Paternal & Maternal Heritage, Ancestral Merits",
            "d12_lagna": f"{sign} ({rashi})",
            "classical_sloka": "द्वादशांशे तथा पित्रोः (Dvādaśāṃśe tathā pitroḥ - BPHS 8.4): 'From Dwadashamsha, judge father, mother, and ancestral lineage.' Sun in D12 signifies paternal blessings; Moon signifies maternal care.",
            "source": "Brihat Parashara Hora Shastra Ch. 8, Sloka 4"
        }
        
    elif varga_key == "D30":
        return {
            "varga": "D30",
            "name": "Trimshamsha",
            "sanskrit": "त्रिंशांश",
            "domain": "Karmic Obstacles, Subconscious Challenges & Moral Strength",
            "d30_lagna": f"{sign} ({rashi})",
            "classical_sloka": "त्रिंशांशे चारिष्टादिकम् (Triṃśāṃśe cāriṣṭādikam - BPHS 8.5): 'From Trimshamsha, assess misfortunes, inner moral trials, and karmic afflictions.' Benefic placements in D30 confer moral immunity and spiritual rectitude.",
            "source": "Brihat Parashara Hora Shastra Ch. 8, Sloka 5"
        }
        
    elif varga_key == "D60":
        return {
            "varga": "D60",
            "name": "Shashtiamsha",
            "sanskrit": "षष्ट्यंश",
            "domain": "Past-Life Karma & Ultimate Cosmic Arbiter (Sarvam Shashtiamshe)",
            "d60_lagna": f"{sign} ({rashi})",
            "classical_sloka": "षष्ट्यंशेऽपि च सर्वज्ञैर्विज्ञेयं सकलं फलम् (Ṣaṣṭyaṃśe'pi ca sarvajñair vijñeyaṃ sakalaṃ phalam - BPHS 8.6-8): 'By the omniscient sages, all auspicious and inauspicious results of a birth must be ultimately confirmed through Shashtiamsha.' The bhava whose lord occupies a malefic Shashtiamsha diminishes; the bhava whose lord occupies a benefic Shashtiamsha flourishes.",
            "source": "Brihat Parashara Hora Shastra Ch. 8, Slokas 6-8"
        }
        
    elif varga_key == "D5":
        return {
            "varga": "D5",
            "name": "Panchamsha (1/5)",
            "sanskrit": "पञ्चांश",
            "domain": "Spiritual Sadhana, Fame, Power of Intellect & Learning",
            "d5_lagna": f"{sign} ({rashi})",
            "classical_sloka": "पञ्चांशे कीर्तिविद्योपासनादिकम् (Pañcāṃśe kīrtividyopāsanādikam): 'From Panchamsha, analyze spiritual devotion, fame, scholarly intelligence, and mastery of mantras.' The 5th division unveils the subtle brilliance of the mind.",
            "source": "Tajika Neelakanthi & Jaimini Sutras"
        }

    elif varga_key == "D6":
        return {
            "varga": "D6",
            "name": "Shashtamsha (1/6)",
            "sanskrit": "षष्ठांश",
            "domain": "Disease, Debts, Litigations & Physical Obstacles",
            "d6_lagna": f"{sign} ({rashi})",
            "classical_sloka": "षष्ठांशे रोगरिपुऋणादिकम् (Ṣaṣṭhāṃśe rogaripuṛṇādikam): 'From Shashtamsha, judge bodily diseases, enemies, financial encumbrances, and litigation.' Benefic presence here shields against chronic afflictions.",
            "source": "Tajika Shastra & Classical Nadi"
        }

    elif varga_key == "D8":
        return {
            "varga": "D8",
            "name": "Ashtamsha (1/8)",
            "sanskrit": "अष्टांश",
            "domain": "Accidents, Chronic Hazards, Longevity & Unexpected Events",
            "d8_lagna": f"{sign} ({rashi})",
            "classical_sloka": "अष्टांशे चायुर्विनाशसंकटम् (Aṣṭāṃśe cāyurvināśasaṃkaṭam): 'From Ashtamsha, evaluate longevity, sudden physical hazards, and unalterable karmic turning points.'",
            "source": "Tajika Canons & Rudramsha Shastra"
        }

    elif varga_key == "D11":
        return {
            "varga": "D11",
            "name": "Ekadashamsha (1/11 Rudramsha)",
            "sanskrit": "एकादशांश (रुद्रांश)",
            "domain": "Cure from Disease, Victory over Obstacles & Extraordinary Gains",
            "d11_lagna": f"{sign} ({rashi})",
            "classical_sloka": "एकादशांशे सर्वलाभं रोगमुक्तिं च (Ekādaśāṃśe sarvalābhaṃ rogamuktiṃ ca): 'From Ekadashamsha (Rudramsha), discern recovery from diseases, defeat of adversaries, and influx of wealth (Labha).'",
            "source": "Tajika Nilakanthi & Rudramsha Tantra"
        }

    elif varga_key == "D150":
        asc_nadi = vinfo.get("ascendant", {}).get("nadi_deity", "Vasudha")
        nadi_num = vinfo.get("ascendant", {}).get("nadi_number", 1)
        return {
            "varga": "D150",
            "name": "Nadiamsha (1/150)",
            "sanskrit": "नाड्यंश (चन्द्रकला नाडी)",
            "domain": "Ultra-Fine Karmic Blueprint & Individual Uniqueness (12' arc)",
            "d150_lagna": f"{sign} ({rashi})",
            "nadi_deity": asc_nadi,
            "nadi_number": nadi_num,
            "classical_sloka": f"नाड्यंशे सूक्ष्मकर्मफलं विलोकयेत्। The native's Ascendant rises in Nadiamsha #{nadi_num} governed by the divine deity '{asc_nadi}' according to Maharishi Satyacharya and Chandra Kala Nadi. This 12-minute arc reveals the unique karmic impulse of the incarnation.",
            "source": "Chandra Kala Nadi (Deva Keralam) & Satyacharya"
        }

    elif "IYER" in varga_key:
        return {
            "varga": varga_key,
            "name": vinfo.get("name", varga_key),
            "sanskrit": vinfo.get("sanskrit", ""),
            "domain": vinfo.get("domain", "Seshadhri Iyer Harmonic System"),
            "lagna": f"{sign} ({rashi})",
            "lagna_lord": lord,
            "classical_sloka": f"Evaluated according to the Seshadhri Iyer continuous cyclic harmonic methodology ({vinfo.get('domain', '')}). Unlike standard static partitions, the Iyer system projects dynamic polarity across all 12 signs.",
            "source": "Seshadhri Iyer (New Techniques of Prediction)"
        }
        
    else:
        # Generic harmonic varga
        return {
            "varga": varga_key,
            "name": vinfo.get("name", varga_key),
            "sanskrit": vinfo.get("sanskrit", ""),
            "domain": vinfo.get("domain", "Harmonic Divination"),
            "lagna": f"{sign} ({rashi})",
            "lagna_lord": lord,
            "classical_sloka": f"Evaluated according to the classical Shodashavarga canons of Maharishi Parashara for the harmonic domain of {vinfo.get('domain', '')}.",
            "source": "Brihat Parashara Hora Shastra Ch. 7 & 8"
        }

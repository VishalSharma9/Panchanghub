"""Comprehensive Classical Vedic Japa Mantras, Remedial Measures & Soul Guidance.

Derived from canonical treatises:
- Brihat Parashara Hora Shastra (BPHS: Chapters 84-90 on Graha Shanti, Japa, Dana)
- Jaimini Upadesha Sutras (Chapter 1, Pada 2 on Karakamsha & Ishta Devata)
- Agni Purana & Garuda Purana (Planetary Beej & Puranic Mantras)
- Parashari Purushartha Philosophy (Dharma, Artha, Kama, Moksha alignment)
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional

# Exhaustive Classical Mantra & Remedial Database for 9 Vedic Grahas
GRAHA_REMEDIES = {
    "Sun": {
        "sanskrit": "सूर्य (Surya)",
        "beej_mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः",
        "beej_transliteration": "Om Hraam Hreem Hroum Sah Sooryaaya Namah",
        "puranic_mantra": "जपाकुसुमसंकाशं काश्यपेयं महाद्युतिम्। तमोऽरिं सर्वपापघ्नं प्रणतोऽस्मि दिवाकरम्॥",
        "puranic_transliteration": "Japaakusuma samkaasham kaashyapeyam mahaadyutim, tamo'rim sarvapaapaghnam pranatosmi divaakaram.",
        "puranic_meaning": "I bow down to the Sun, who is radiant like the hibiscus flower, son of Kashyapa, of immense brilliance, the destroyer of darkness and expeller of all sins.",
        "gayatri_mantra": "ॐ आदित्याय विद्महे मार्तण्डाय धीमहि तन्नः सूर्यः प्रचोदयात्॥",
        "prescribed_japa_count": 7000,
        "kaliyuga_recommended_count": 28000,
        "rosary_mala": "Rudraksha or Red Sandalwood (Rakta Chandana)",
        "best_muhurta": "Sunday at Sunrise (Surya Hora) during Shukla Paksha",
        "deity": "Lord Shiva, Lord Rama, Surya Narayana",
        "charitable_dana": "Wheat, ruby, jaggery (gur), copper vessel, red cloth, saffron",
        "fasting_vrata": "Sunday fast; abstain from salt; consume wheat and milk",
        "conduct_remedy": "Offer water (Arghya) to the rising Sun daily from a copper vessel; respect father and government authority"
    },
    "Moon": {
        "sanskrit": "चन्द्र (Chandra)",
        "beej_mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः",
        "beej_transliteration": "Om Shraam Shreem Shroum Sah Chandramase Namah",
        "puranic_mantra": "दधिशंखतुषाराभं क्षीरोदार्णवसंभवम्। नमामि शशिनं सोमं शम्भोर्मुकुटभूषणम्॥",
        "puranic_transliteration": "Dadhishankhatushaaraabham ksheerodaarnavasambhavam, namaami shashinam somam shambhormukutabhooshanam.",
        "puranic_meaning": "I bow to the Moon, shining like curd, conch and snow, born from the Ocean of Milk, who adorns the crown of Lord Shiva.",
        "gayatri_mantra": "ॐ क्षीरपुत्राय विद्महे अमृतत्त्वाय धीमहि तन्नो चन्द्रः प्रचोदयात्॥",
        "prescribed_japa_count": 11000,
        "kaliyuga_recommended_count": 44000,
        "rosary_mala": "Sphatika (Quartz Crystal), Pearl, or White Sandalwood",
        "best_muhurta": "Monday evening or night (Chandra Hora) during waxing Moon (Shukla Paksha)",
        "deity": "Goddess Parvati, Gauri, Lord Shiva, Lord Krishna",
        "charitable_dana": "Rice, white pearl, silver, milk, curd, white clothes, camphor, sugar",
        "fasting_vrata": "Monday fast or Purnima (Full Moon) fast; consume milk products only",
        "conduct_remedy": "Drink water from a silver cup; serve and seek blessings from mother and maternal elders; practice evening meditation"
    },
    "Mars": {
        "sanskrit": "मङ्गल (Mangala)",
        "beej_mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः",
        "beej_transliteration": "Om Kraam Kreem Kroum Sah Bhoumaaya Namah",
        "puranic_mantra": "धरणीगर्भसंभूतं विद्युत्कान्तिसमप्रभम्। कुमारं शक्तिहस्तं च मङ्गलं प्रणमाम्यहम्॥",
        "puranic_transliteration": "Dharaneegarbhasambhootam vidyutkaantisamaprabham, kumaaram shaktihastam cha mangalam pranamaamyaham.",
        "puranic_meaning": "I bow down to Mangala, born of the womb of Mother Earth, shining with the splendor of lightning, youthful prince holding the divine spear (Shakti).",
        "gayatri_mantra": "ॐ अङ्गारकाय विद्महे शक्तिहस्ताय धीमहि तन्नो भौमः प्रचोदयात्॥",
        "prescribed_japa_count": 10000,
        "kaliyuga_recommended_count": 40000,
        "rosary_mala": "Red Coral (Moonga) or Red Sandalwood",
        "best_muhurta": "Tuesday morning (Mangala Hora)",
        "deity": "Lord Hanuman, Lord Kartikeya (Subrahmanya), Lord Narasimha",
        "charitable_dana": "Red lentils (masoor dal), copper, red flowers, jaggery, red coral, sweet wheat bread (roti)",
        "fasting_vrata": "Tuesday fast; take food once in the evening without salt",
        "conduct_remedy": "Recite Hanuman Chalisa or Sundarkand on Tuesdays; support younger siblings; donate blood voluntarily"
    },
    "Mercury": {
        "sanskrit": "बुध (Budha)",
        "beej_mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः",
        "beej_transliteration": "Om Braam Breem Broum Sah Budhaaya Namah",
        "puranic_mantra": "प्रियंगुकलिकाश्यामं रूपेणाप्रतिमं बुधम्। सौम्यं सौम्यगुणोपेतं तं बुधं प्रणमाम्यहम्॥",
        "puranic_transliteration": "Priyangu-kalikaa-shyaamam roopenaapratimam budham, soumyam soumyagunopetam tam budham pranamaamyaham.",
        "puranic_meaning": "I bow to Budha, dark like the tender bud of the Priyangu plant, of peerless form, gentle nature, and endowed with all benign qualities.",
        "gayatri_mantra": "ॐ सौम्यरूपाय विद्महे वाणेशाय धीमहि तन्नो सौम्यः प्रचोदयात्॥",
        "prescribed_japa_count": 9000,
        "kaliyuga_recommended_count": 36000,
        "rosary_mala": "Tulsi mala or Emerald bead mala",
        "best_muhurta": "Wednesday morning (Budha Hora)",
        "deity": "Lord Vishnu, Lord Ganesha, Narayana",
        "charitable_dana": "Whole green gram (moong dal), bronze, green clothes, emerald, ivory, green vegetables, books",
        "fasting_vrata": "Wednesday fast; consume green fruits and moong dal",
        "conduct_remedy": "Recite Vishnu Sahasranama; feed green grass or spinach to cows; plant flowering or medicinal green trees"
    },
    "Jupiter": {
        "sanskrit": "गुरु / बृहस्पति (Guru / Brihaspati)",
        "beej_mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः",
        "beej_transliteration": "Om Graam Greem Groum Sah Gurave Namah",
        "puranic_mantra": "देवानां च ऋषीणां च गुरुं काञ्चनसंनिभम्। बुद्धिभूतं त्रिलोकेशं तं नमामि बृहस्पतिम्॥",
        "puranic_transliteration": "Devaanaam cha risheenaam cha gurum kaanchanasannibham, buddhibhootam trilokesham tam namaami brihaspatim.",
        "puranic_meaning": "I bow to Brihaspati, preceptor of gods and sages, resplendent like molten gold, the very embodiment of supreme intellect and lord of the three worlds.",
        "gayatri_mantra": "ॐ गुरुदेवाय विद्महे परब्रह्मणे धीमहि तन्नो गुरुः प्रचोदयात्॥",
        "prescribed_japa_count": 19000,
        "kaliyuga_recommended_count": 76000,
        "rosary_mala": "Turmeric-dyed wood (Haldi mala), Yellow Sandalwood, or Rudraksha (Five-Mukhi)",
        "best_muhurta": "Thursday morning (Guru Hora) during Shukla Paksha",
        "deity": "Lord Shiva, Lord Dakshinamurthy, Lord Dattatreya, Lord Brihaspati",
        "charitable_dana": "Yellow split gram (chana dal), turmeric, yellow topaz/sapphire, gold, yellow cloth, religious scriptures",
        "fasting_vrata": "Thursday fast; take yellow foods (besan, chana dal); avoid applying oil or soap",
        "conduct_remedy": "Revere and serve spiritual mentors, teachers, and Brahmins; read philosophical scriptures daily"
    },
    "Venus": {
        "sanskrit": "शुक्र (Shukra)",
        "beej_mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः",
        "beej_transliteration": "Om Draam Dreem Droum Sah Shukraaya Namah",
        "puranic_mantra": "हिमकुन्दमृणालाभं दैत्यानां परमं गुरुम्। सर्वशास्त्रप्रवक्तारं भार्गवं प्रणमाम्यहम्॥",
        "puranic_transliteration": "Himakundamrinaalaabham daityaanaam paramam gurum, sarvashaastrapravaktaaram bhaargavam pranamaamyaham.",
        "puranic_meaning": "I bow to Bhaargava (Shukra), white like snow, the jasmine blossom and lotus fiber, the supreme guru of the Daityas, master expounder of all sciences.",
        "gayatri_mantra": "ॐ भार्गवाय विद्महे दैत्यगुरवे धीमहि तन्नो शुक्रः प्रचोदयात्॥",
        "prescribed_japa_count": 16000,
        "kaliyuga_recommended_count": 64000,
        "rosary_mala": "Sphatika (Crystal), White Lotus Seed (Kamal Gatta), or Silver beads",
        "best_muhurta": "Friday morning (Shukra Hora) or evening twilight",
        "deity": "Goddess Mahalakshmi, Lalita Tripurasundari, Goddess Radha",
        "charitable_dana": "Ghee, white silk, diamond/zircon, white sweets, silver, curd, fragrant perfumes",
        "fasting_vrata": "Friday fast; worship Goddess Lakshmi; consume sweet kheer/milk dishes",
        "conduct_remedy": "Recite Sri Suktam or Kanakadhara Stotram; treat women, spouse, and artists with utmost dignity and honor"
    },
    "Saturn": {
        "sanskrit": "शनि (Shani)",
        "beej_mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः",
        "beej_transliteration": "Om Praam Preem Proum Sah Shanaishcharaaya Namah",
        "puranic_mantra": "नीलांजनसमाभासं रविपुत्रं यमाग्रजम्। छायामार्तण्डसंभूतं तं नमामि शनैश्चरम्॥",
        "puranic_transliteration": "Neelaanjanasamaabhaasam raviputram yamaagrajam, chhaayaamaartandasambhootam tam namaami shanaishcharam.",
        "puranic_meaning": "I bow to Shanaishchara, radiant like dark blue collyrium, son of the Sun, elder brother of Yama, born of Chhaya and the Sun.",
        "gayatri_mantra": "ॐ काकध्वजाय विद्महे खड्गहस्ताय धीमहि तन्नो मन्दः प्रचोदयात्॥",
        "prescribed_japa_count": 23000,
        "kaliyuga_recommended_count": 92000,
        "rosary_mala": "Rudraksha (Seven-Mukhi) or Blue Sapphire/Amethyst beads",
        "best_muhurta": "Saturday evening after Sunset (Shani Hora)",
        "deity": "Lord Hanuman, Lord Shiva, Lord Yama, Lord Shani",
        "charitable_dana": "Black sesame seeds (til), mustard oil, iron utensils, blue sapphire, black cloth, whole urad dal, leather shoes",
        "fasting_vrata": "Saturday fast; consume food once after sunset containing sesame or urad dal",
        "conduct_remedy": "Light a sesame oil or mustard oil lamp beneath a Peepal tree on Saturdays; serve and assist laborers, disabled persons, and elders"
    },
    "Rahu": {
        "sanskrit": "राहु (Rahu)",
        "beej_mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः",
        "beej_transliteration": "Om Bhraam Bhreem Bhroum Sah Raahave Namah",
        "puranic_mantra": "अर्धकायं महावीर्यं चन्द्रादित्यविमर्दनम्। सिंहिकागर्भसंभूतं तं राहुं प्रणमाम्यहम्॥",
        "puranic_transliteration": "Ardhakaayam mahaaveeryam chandraadityavimardanam, simhikaagarbhasambhootam tam raahum pranamaamyaham.",
        "puranic_meaning": "I bow to Rahu, of half body, endowed with formidable power, the eclipsing oppressor of the Sun and Moon, born of Simhika.",
        "gayatri_mantra": "ॐ नागध्वजाय विद्महे पद्महस्ताय धीमहि तन्नो राहुः प्रचोदयात्॥",
        "prescribed_japa_count": 18000,
        "kaliyuga_recommended_count": 72000,
        "rosary_mala": "Gomedha (Hessonite Garnet) or Sandalwood beads",
        "best_muhurta": "Saturday or Wednesday at night / twilight during Rahu Kaal",
        "deity": "Goddess Durga, Goddess Bhairavi, Lord Shiva, Lord Varaha",
        "charitable_dana": "Seven grains (satnaja), lead (sheesha), hessonite, dark blankets, mustard, coconut immersed in flowing river",
        "fasting_vrata": "Saturday fast or fasting during solar/lunar eclipses",
        "conduct_remedy": "Recite Durga Saptashati or Kalabhairava Ashtakam; avoid wearing stale/dark unwashed garments; maintain cleanliness in bathroom"
    },
    "Ketu": {
        "sanskrit": "केतु (Ketu)",
        "beej_mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः",
        "beej_transliteration": "Om Sraam Sreem Sroum Sah Ketave Namah",
        "puranic_mantra": "पलाशपुष्पसंकाशं तारकाग्रहमस्तकम्। रौद्रं रौद्रात्मकं घोरं तं केतुं प्रणमाम्यहम्॥",
        "puranic_transliteration": "Palaashapushpasamkaasham taarakaagrahamastakam, roudram roudraatmakam ghoram tam ketum pranamaamyaham.",
        "puranic_meaning": "I bow down to Ketu, having the appearance of the fiery Palasha blossom, foremost among starry planetary bodies, fierce, of Rudra's divine essence, and awe-inspiring.",
        "gayatri_mantra": "ॐ अश्मध्वजाय विद्महे शूलहस्ताय धीमहि तन्नो केतुः प्रचोदयात्॥",
        "prescribed_japa_count": 17000,
        "kaliyuga_recommended_count": 68000,
        "rosary_mala": "Cat's Eye (Vaidurya) or Rudraksha (Nine-Mukhi)",
        "best_muhurta": "Tuesday or Thursday at dawn or late night",
        "deity": "Lord Ganesha, Lord Matsya, Goddess Chhinnamasta",
        "charitable_dana": "Two-colored blanket, sesame, oil, iron knife, cat's eye stone, mustard, food for street dogs",
        "fasting_vrata": "Tuesday or Ganesh Chaturthi fast",
        "conduct_remedy": "Recite Ganesha Atharvashirsha daily; feed stray dogs; practice non-attachment and Vipassana / Vedanta meditation"
    }
}

# Jaimini Deities assigned to planets in Navamsha (Jaimini Sutras 1.2.69-72)
JAIMINI_DEITIES = {
    "Sun": {"ishta": "Lord Shiva / Lord Rama", "mantra": "ॐ नमः शिवाय (Om Namah Shivaaya)"},
    "Moon": {"ishta": "Goddess Gauri / Lalita / Krishna", "mantra": "ॐ क्लीं कृष्णाय नमः (Om Kleem Krishnaaya Namah)"},
    "Mars": {"ishta": "Lord Kartikeya / Hanuman / Narasimha", "mantra": "ॐ हं हनुमते नमः (Om Ham Hanumate Namah)"},
    "Mercury": {"ishta": "Lord Maha Vishnu / Narayana", "mantra": "ॐ नमो भगवते वासुदेवाय (Om Namo Bhagavate Vaasudevaaya)"},
    "Jupiter": {"ishta": "Lord Dakshinamurthy / Dattatreya", "mantra": "ॐ दक्षिणामूर्तये नमः (Om Dakshinaamoortaye Namah)"},
    "Venus": {"ishta": "Goddess Mahalakshmi / Radha", "mantra": "ॐ श्रीं महालक्ष्म्यै नमः (Om Shreem Mahaalakshmyai Namah)"},
    "Saturn": {"ishta": "Lord Kurma / Lord Shiva / Brahma", "mantra": "ॐ शं शनैश्चराय नमः (Om Sham Shanaishcharaaya Namah)"},
    "Rahu": {"ishta": "Goddess Durga / Lord Varaha", "mantra": "ॐ दुं दुर्गायै नमः (Om Dum Durgaayai Namah)"},
    "Ketu": {"ishta": "Lord Ganesha / Lord Matsya", "mantra": "ॐ गं गणपतये नमः (Om Gam Ganapataye Namah)"}
}

def compute_soul_guidance(pos: Dict[str, Any], asc_lon: float, d9_pos: Dict[str, Any] = None) -> Dict[str, Any]:
    """Calculates Atmakaraka, Karakamsha, Ishta Devata, Dharma Devata, Palana Devata, and Purushartha Matrix."""
    from .dashas_ext import compute_jaimini_karakas
    from .ephem import SIGNS, RASHIS, SIGN_LORDS
    
    # 1. Chara Karakas
    jk = compute_jaimini_karakas(pos)
    ak_planet = jk.get("atmakaraka", "Sun")
    amk_planet = jk.get("amatyakaraka", "Jupiter")
    
    # Navamsha sign of Atmakaraka (Karakamsha)
    ak_lon = pos[ak_planet]["longitude"] if ak_planet in pos else 0.0
    ak_nav_idx = int(ak_lon // (30.0 / 9.0)) % 12
    # Standard Navamsha calculation:
    ak_sign = int(ak_lon // 30.0) % 12
    ak_deg = ak_lon % 30.0
    nav_pada = int(ak_deg // (30.0 / 9.0))
    mod4 = ak_sign % 4
    if mod4 == 0: start_sign = 0
    elif mod4 == 1: start_sign = 9
    elif mod4 == 2: start_sign = 6
    else: start_sign = 3
    karakamsha_sign_idx = (start_sign + nav_pada) % 12
    
    karakamsha_sign = SIGNS[karakamsha_sign_idx]
    karakamsha_rashi = RASHIS[karakamsha_sign_idx]
    karakamsha_lord = SIGN_LORDS[karakamsha_sign_idx]
    
    # 2. Ishta Devata (12th from Karakamsha in Navamsha)
    ishta_house_sign_idx = (karakamsha_sign_idx + 11) % 12
    ishta_lord = SIGN_LORDS[ishta_house_sign_idx]
    ishta_info = JAIMINI_DEITIES.get(ishta_lord, JAIMINI_DEITIES["Sun"])
    
    # 3. Dharma Devata (9th from Karakamsha in Navamsha)
    dharma_house_sign_idx = (karakamsha_sign_idx + 8) % 12
    dharma_lord = SIGN_LORDS[dharma_house_sign_idx]
    dharma_info = JAIMINI_DEITIES.get(dharma_lord, JAIMINI_DEITIES["Jupiter"])
    
    # 4. Palana Devata (6th from Amatyakaraka in Navamsha)
    amk_lon = pos[amk_planet]["longitude"] if amk_planet in pos else 0.0
    amk_sign = int(amk_lon // 30.0) % 12
    amk_deg = amk_lon % 30.0
    amk_nav_pada = int(amk_deg // (30.0 / 9.0))
    amk_mod4 = amk_sign % 4
    if amk_mod4 == 0: a_start = 0
    elif amk_mod4 == 1: a_start = 9
    elif amk_mod4 == 2: a_start = 6
    else: a_start = 3
    amk_nav_idx = (a_start + amk_nav_pada) % 12
    palana_house_sign_idx = (amk_nav_idx + 5) % 12
    palana_lord = SIGN_LORDS[palana_house_sign_idx]
    palana_info = JAIMINI_DEITIES.get(palana_lord, JAIMINI_DEITIES["Mercury"])
    
    # 5. Purushartha Matrix (Dharma, Artha, Kama, Moksha)
    # Count occupants and house lords in each triplicity from Lagna
    asc_sign = int(asc_lon // 30.0) % 12
    
    dharma_houses = [1, 5, 9]
    artha_houses = [2, 6, 10]
    kama_houses = [3, 7, 11]
    moksha_houses = [4, 8, 12]
    
    scores = {"Dharma": 0, "Artha": 0, "Kama": 0, "Moksha": 0}
    planets_in_purushartha = {"Dharma": [], "Artha": [], "Kama": [], "Moksha": []}
    
    for p, pdata in pos.items():
        if p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            h = (int(pdata["longitude"] // 30.0) - asc_sign) % 12 + 1
            pts = 2 if p in ("Sun", "Jupiter") else (1.5 if p in ("Moon", "Mars", "Venus") else 1)
            if h in dharma_houses:
                scores["Dharma"] += pts
                planets_in_purushartha["Dharma"].append(p)
            elif h in artha_houses:
                scores["Artha"] += pts
                planets_in_purushartha["Artha"].append(p)
            elif h in kama_houses:
                scores["Kama"] += pts
                planets_in_purushartha["Kama"].append(p)
            elif h in moksha_houses:
                scores["Moksha"] += pts
                planets_in_purushartha["Moksha"].append(p)
                
    # Normalize scores to 100%
    total_pts = sum(scores.values()) or 1.0
    pct = {k: round((v / total_pts) * 100, 1) for k, v in scores.items()}
    primary_purushartha = max(scores, key=scores.get)
    
    guidance_map = {
        "Dharma": "Your soul's highest fulfillment arises through moral leadership, intellectual/spiritual teaching, ethical creativity, and upholding truth. Align your daily decisions with higher principles.",
        "Artha": "Your primary vehicle for worldly success and inner contentment is structured productivity, financial acumen, institutional competence, and tangible service to society.",
        "Kama": "You thrive through creative partnerships, social networks, artistic enterprise, and the ambitious pursuit of goals. Channel desires into constructive collective achievements.",
        "Moksha": "Your inner nature seeks deep peace, introspection, meditation, and detachment from worldly storms. Cultivate daily solitude, charity, and contemplative practices."
    }
    
    ak_lessons = {
        "Sun": "Lesson of humility: Surrendering personal ego, cultivating genuine selfless service, and leading without pride.",
        "Moon": "Lesson of emotional balance: Transcending mood fluctuations, extending unconditional compassion without needy attachment.",
        "Mars": "Lesson of non-violence (Ahimsa): Channeling formidable vitality into disciplined protection rather than conflict or anger.",
        "Mercury": "Lesson of truthful speech (Satya): Mastering the mind and tongue, using communication to heal, clarify, and educate.",
        "Jupiter": "Lesson of wisdom and respect: Honoring mentors, staying receptive to truth, and avoiding dogmatism or moral superiority.",
        "Venus": "Lesson of purity in relationship: Transcending sensual fixation, appreciating divine beauty in all souls, and practicing fidelity.",
        "Saturn": "Lesson of patient endurance (Titiksha): Embracing hard labor without bitterness, accepting solitude, and serving the underprivileged.",
        "Rahu": "Lesson of unmasking illusions: Freeing oneself from worldly obsessions, deception, and sudden craving for exotic acclaim."
    }.get(ak_planet, "Pursue self-mastery through adherence to truth.")
    
    return {
        "atmakaraka": {
            "planet": ak_planet,
            "degree_in_sign": f"{ak_deg:.2f}°",
            "sign": SIGNS[ak_sign],
            "rashi": RASHIS[ak_sign],
            "soul_lesson": ak_lessons
        },
        "karakamsha": {
            "sign": karakamsha_sign,
            "rashi": karakamsha_rashi,
            "lord": karakamsha_lord,
            "description": f"The Atmakaraka occupies {karakamsha_sign} ({karakamsha_rashi}) in Navamsha, indicating your subtle spiritual blueprint and post-maturity inner path."
        },
        "ishta_devata": {
            "house": "12th from Karakamsha in Navamsha",
            "sign": SIGNS[ishta_house_sign_idx],
            "governing_lord": ishta_lord,
            "deity_archetype": ishta_info["ishta"],
            "primary_mantra": ishta_info["mantra"],
            "significance": "According to Jaimini Upadesha Sutras 1.2.69-72, the deity indicated by the 12th house from Karakamsha is the Ishta Devata who bestows spiritual liberation (Moksha) and dissolves deep-seated karmas."
        },
        "dharma_devata": {
            "house": "9th from Karakamsha in Navamsha",
            "sign": SIGNS[dharma_house_sign_idx],
            "governing_lord": dharma_lord,
            "deity_archetype": dharma_info["ishta"],
            "significance": "Guiding deity for righteous conduct, vocational integrity, moral prosperity, and higher wisdom."
        },
        "palana_devata": {
            "house": "6th from Amatyakaraka in Navamsha",
            "sign": SIGNS[palana_house_sign_idx],
            "governing_lord": palana_lord,
            "deity_archetype": palana_info["ishta"],
            "significance": "Presiding deity for worldly sustenance, steady income, career stability, and defense against professional ruin."
        },
        "purushartha_matrix": {
            "primary_focus": primary_purushartha,
            "distribution_percentages": pct,
            "planets_in_domains": planets_in_purushartha,
            "strategic_guidance": guidance_map[primary_purushartha]
        },
        "canonical_source": "Brihat Parashara Hora Shastra Ch. 35 & Maharishi Jaimini Upadesha Sutras"
    }

def get_complete_remedies_for_chart(k: dict) -> Dict[str, Any]:
    """Generates an exhaustive remedial dossier with Japa Mantras, counts, rituals, and soul guidance."""
    pos = {p["name"]: {"longitude": p["longitude"], "speed": p.get("speed", 0.0)} for p in k.get("planets", [])}
    asc_lon = k.get("lagna", {}).get("longitude", 0.0)
    
    # Calculate Soul Guidance & Ishta Devata
    soul_guidance = compute_soul_guidance(pos, asc_lon)
    
    # Identify planets needing remedial attention:
    # 1. Debilitated planets
    # 2. Planets in 6th, 8th, 12th houses
    # 3. Combust planets
    # 4. Running dasha lords
    remedial_grahas = []
    for p in k.get("planets", []):
        name = p["name"]
        if name in GRAHA_REMEDIES:
            needs_remedy = False
            reasons = []
            if "Debil" in p.get("dignity", ""):
                needs_remedy = True
                reasons.append("Debilitated dignity in Rashi chart")
            if p.get("combust"):
                needs_remedy = True
                reasons.append("Combust by close proximity to the Sun")
            if p.get("house") in (6, 8, 12):
                needs_remedy = True
                reasons.append(f"Placed in Dusthana (House {p['house']})")
                
            rem_entry = dict(GRAHA_REMEDIES[name])
            rem_entry["planet_name"] = name
            rem_entry["priority"] = "High" if len(reasons) >= 2 else ("Medium" if needs_remedy else "Supplementary")
            rem_entry["affliction_reasons"] = reasons
            remedial_grahas.append(rem_entry)
            
    # Sort by priority
    order_val = {"High": 0, "Medium": 1, "Supplementary": 2}
    remedial_grahas.sort(key=lambda x: order_val.get(x["priority"], 3))
    
    return {
        "soul_guidance": soul_guidance,
        "graha_remedies_catalogue": remedial_grahas,
        "all_nine_grahas": GRAHA_REMEDIES,
        "general_ethical_guidance": (
            "Classical remedies in Maharishi Parashara's canons are not commercial transactions, "
            "but conscious realignment of the inner psyche with cosmic laws. Regular japa with devotion, "
            "truthful speech (Satya), non-violence (Ahimsa), and unselfish service to the disadvantaged "
            "provide enduring protection and transmute karmic afflictions."
        )
    }

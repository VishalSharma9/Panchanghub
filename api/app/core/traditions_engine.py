"""Global & Classical Astrological Traditions + Ayurvedic Tridosha (Vata, Pitta, Kapha)
& Chinese Five Elements (Wood, Fire, Earth, Metal, Water) Holistic Chart Engine.

Covers in full mathematical and interpretive depth:
1. Indian (Vedic / Jyotish) Astrology Systems:
   - Lal Kitab (Fixed Aries Ascendant / Pakka Ghar, Sleeping Planets, Karmic Rinas, Palmistry Links, 43-Day Upayas)
   - Parashari Astrology (BPHS Sidereal Zodiac, 27 Nakshatras, Vimshottari Dasha, Vargas D1/D9/D10, Shadbala, Yogas)
   - Jaimini Astrology (7 Chara Karakas, Karakamsha Lagna, Arudha Padas AL/UL/A7/A10, Rashi Drishti, Chara Dasha)
   - Krishnamurti Paddhati / KP System (Placidus Cusps, 249 Sub-Lords, 4-Fold Significators, Event Timing Verdicts)
   - Nadi Astrology (150 Nadi Amshas, Thumbprint Archetypes Shankha/Chakra/Padma, Bhrigu Nandi Nadi Circuits, Parihara)
2. Western Astrology Systems:
   - Western Tropical Astrology (Equinox/Solstice Zodiac, Big Three Archetypes, Elements/Modalities, Ptolemaic Aspects)
   - Hellenistic Astrology (Sect Day/Night, Benefic/Malefic of Sect, Whole-Sign Houses, Lots of Fortune/Spirit, Annual Profections)
   - Modern Psychological & Evolutionary Astrology (Pluto Soul Evolution Axis, Pluto Polarity Point, Lunar Nodes, Jungian Archetypes)
   - Uranian / Hamburg School (8 Trans-Neptunian Planets: Cupido..Poseidon, 90° Cosmobiology Dial, Planetary Midpoints A/B=C)
3. Global & Cultural Systems:
   - Chinese Astrology (12 Animal Signs, BaZi Four Pillars of Destiny: Year/Month/Day Master/Hour, Yin/Yang, Five Elements)
   - Classical Feng Shui (Personal Kua / Ming Gua, Eight Mansions Ba Zhai, Bagua 9-Grid, Period 9 Flying Stars, 4 Celestial Animals)
   - Mayan Astrology (Sacred 260-Day Tzolk'in, 20 Nawales × 13 Galactic Tones, Mayan Tree-of-Life Cross, Wavespell)
   - Celtic (Druidic) Tree Astrology (13-Moon Ogham Tree Calendar, Ogham Stave, Power Animal, Druidic Wisdom)
4. Native Chart Constitutional Balance (Ayurvedic Vata-Pitta-Kapha × Chinese Wood-Fire-Earth-Metal-Water):
   - Natal Prakriti (Vata %, Pitta %, Kapha %) + Current Dasha Vikriti
   - Natal Chinese Five Elements (Wood %, Fire %, Earth %, Metal %, Water %) + Yin/Yang Balance
   - Complete Diet, Herbs, Dinacharya, Pranayama, Organ Meridian & Space Balancing Protocol
5. Customizable Report Filter (by focus_mode, school_preference, and selected_traditions).
"""
from __future__ import annotations
from datetime import date as Date, datetime, timezone
import math
from typing import Any, Dict, List, Optional

from . import ephem, kundli as K, dashas as D, dashas_ext as DExt, advanced as ADV
from . import chinese as CH, esoteric as ESO, western as W, western_ext as WExt
from . import charts_svg as SVG
from .astro_vastu_engine import compute_personalized_astro_vastu, compute_classical_feng_shui
from .ephem import SIGNS, RASHIS, SIGN_LORDS, NAKSHATRAS, NAK_LORDS, VEDIC_PLANETS


# ---------------------------------------------------------------------------
# CATALOG OF ALL TRADITIONS & FILTER CATEGORIES
# ---------------------------------------------------------------------------
TRADITIONS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "lal_kitab",
        "title": "Lal Kitab (Red Book Remedial & Palmistry Jyotish)",
        "school": "eastern_vedic",
        "focus_tags": ["remedies_and_healing", "event_prediction", "personal_insight"],
        "founder_or_root": "Pandit Roop Chand Joshi (1939–1952, rooted in Vedic & Persian/Uttara Kalamrita traditions)",
        "summary": "Uses a Fixed Aries Ascendant (Pakka Ghar) chart regardless of birth time, maps each planet to a palm mount/line, detects Karmic Debts (Rinas) & Sleeping Planets, and prescribes simple, low-cost daily remedies (Upayas).",
    },
    {
        "id": "parashari",
        "title": "Parashari Astrology (Classical Brihat Parashara Hora Shastra)",
        "school": "eastern_vedic",
        "focus_tags": ["personal_insight", "event_prediction", "remedies_and_healing"],
        "founder_or_root": "Maharishi Parashara (Brihat Parashara Hora Shastra)",
        "summary": "The foundational pillar of Vedic Jyotish: Sidereal Lahiri zodiac, 27 Nakshatras, 16 Shodashavarga divisional charts (D1, D9 Navamsha, D10), Vimshottari Dasha, Shadbala, Ashtakavarga, and Classical Raja/Dhana Yogas.",
    },
    {
        "id": "jaimini",
        "title": "Jaimini Sutras (Chara Karakas, Arudha Padas & Chara Dasha)",
        "school": "eastern_vedic",
        "focus_tags": ["personal_insight", "event_prediction"],
        "founder_or_root": "Maharishi Jaimini (Upadesha Sutras)",
        "summary": "Uses degree-based variable soul significators (7 Chara Karakas led by Atmakaraka), Sign Aspects (Rashi Drishti), Arudha Padas (AL & Upapada UL), Karakamsha Lagna, and sign-based Chara Dasha.",
    },
    {
        "id": "kp",
        "title": "Krishnamurti Paddhati (KP Stellar Sub-Lord System)",
        "school": "eastern_vedic",
        "focus_tags": ["event_prediction"],
        "founder_or_root": "Prof. K.S. Krishnamurti (20th Century Stellar Astrology)",
        "summary": "Divides the 27 Nakshatras into 249 unequal Sub-Lord divisions in Vimshottari proportion with Placidus house cusps for razor-sharp 'Yes/No' promise and event timing.",
    },
    {
        "id": "nadi",
        "title": "Nadi Astrology (Agastya, Bhrigu & Bhrigu Nandi Nadi Palm-Leaf System)",
        "school": "eastern_vedic",
        "focus_tags": ["event_prediction", "personal_insight", "remedies_and_healing"],
        "founder_or_root": "Sages Agastya, Bhrigu & Tamil Siddha Palm-Leaf Tradition",
        "summary": "Matches thumbprint ridge archetypes (Shankha, Chakra, Padma) and 150 Nadi Amshas with Bhrigu Nandi Nadi planetary circuits (Jupiter=Jeeva, Saturn=Karma) to decode past-life karma and destined life chapters (Kandams).",
    },
    {
        "id": "western_tropical",
        "title": "Western Tropical Astrology (Seasonal Equinox & Archetypal Chart)",
        "school": "western",
        "focus_tags": ["personal_insight"],
        "founder_or_root": "Ptolemaic & Modern Western Tropical Tradition",
        "summary": "Aligns 0° Aries with the Vernal Equinox, emphasizing Sun-Moon-Rising psychological archetypes, Elemental/Modality balance, outer planets (Uranus, Neptune, Pluto), and geometric aspects.",
    },
    {
        "id": "hellenistic",
        "title": "Hellenistic Astrology (Ancient Greco-Roman Fate & Time-Lord System)",
        "school": "western",
        "focus_tags": ["event_prediction", "personal_insight"],
        "founder_or_root": "Vettius Valens, Dorotheus of Sidon, Claudius Ptolemy (1st c. BCE – 2nd c. CE)",
        "summary": "Built on Sect (Day vs. Night charts), Benefic/Malefic of Sect, Whole-Sign Houses (Topoi), Arabic/Hellenistic Lots (Lot of Fortune & Lot of Spirit), and Annual Profections (Time Lord of the Year).",
    },
    {
        "id": "psychological_evolutionary",
        "title": "Modern Psychological & Evolutionary Astrology (Jungian & Pluto Soul Axis)",
        "school": "western",
        "focus_tags": ["personal_insight", "remedies_and_healing"],
        "founder_or_root": "Carl Jung, Dane Rudhyar, Liz Greene & Jeffrey Wolf Green",
        "summary": "Maps the psyche's Persona, Ego, Anima/Animus, and Shadow alongside the Pluto Soul Evolution Axis (Pluto + Pluto Polarity Point + South/North Lunar Nodes) for deep unconscious healing.",
    },
    {
        "id": "uranian",
        "title": "Uranian / Hamburg School (Midpoints, 90° Dial & 8 Trans-Neptunian Planets)",
        "school": "western",
        "focus_tags": ["event_prediction"],
        "founder_or_root": "Alfred Witte, Friedrich Sieggrün & Reinhold Ebertin (Cosmobiology)",
        "summary": "Mathematical event forecasting using Planetary Midpoints (A/B = C), the 90-Degree Dial, and 8 hypothetical Trans-Neptunian Planets (Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon).",
    },
    {
        "id": "chinese_bazi",
        "title": "Chinese Astrology (BaZi Four Pillars of Destiny, 12 Animals & Wu Xing)",
        "school": "global_cultural",
        "focus_tags": ["personal_insight", "event_prediction", "remedies_and_healing"],
        "founder_or_root": "Classical Imperial Chinese BaZi (Ming Li) & Sheng Xiao Tradition",
        "summary": "Combines the 12 Animal Signs with the Four Pillars of Destiny (Year, Month, Day Master, Hour Stems & Branches), Yin/Yang polarity, and Five Elements (Wood, Fire, Earth, Metal, Water).",
    },
    {
        "id": "feng_shui",
        "title": "Classical Feng Shui (Ming Gua Kua, Eight Mansions, Bagua & Flying Stars)",
        "school": "global_cultural",
        "focus_tags": ["remedies_and_healing", "personal_insight"],
        "founder_or_root": "Classical Compass School (Ba Zhai & Xuan Kong Fei Xing) & Form School",
        "summary": "Aligns your Personal Kua Number, 4 Auspicious Directions (Sheng Qi, Tian Yi, Yan Nian, Fu Wei), Bagua 9-Sector Map, Period 9 Flying Stars, and Four Celestial Landscape Guardians.",
    },
    {
        "id": "mayan",
        "title": "Mayan Astrology (Sacred 260-Day Tzolk'in, 20 Nawales & Mayan Cross)",
        "school": "global_cultural",
        "focus_tags": ["personal_insight"],
        "founder_or_root": "Mesoamerican Mayan Daykeeper (Ajq'ij) Sacred Calendar Tradition",
        "summary": "Computes your Galactic Signature (Kin 1–260), Day Sign (Nawal 1–20), Galactic Tone (1–13), and the 5-position Mayan Tree-of-Life Cross.",
    },
    {
        "id": "celtic_tree",
        "title": "Celtic (Druidic) Tree Astrology (13-Moon Ogham Sacred Grove)",
        "school": "global_cultural",
        "focus_tags": ["personal_insight", "remedies_and_healing"],
        "founder_or_root": "Celtic Ogham Alphabet & Reconstructed 13-Luna Druidic Seasonal Lore",
        "summary": "Maps your birth date to the 13 Lunar Tree Archetypes (Birch to Elder), Ogham stave letter, sacred animal guide, and seasonal earth wisdom.",
    },
    {
        "id": "holistic_dosha_elements",
        "title": "Ayurvedic Tridosha (Vata, Pitta, Kapha) × Chinese Five Elements Chart Balance",
        "school": "holistic_balance",
        "focus_tags": ["remedies_and_healing", "personal_insight"],
        "founder_or_root": "Ayurvedic Jyotish (Charaka / BPHS) × Chinese Wu Xing Bio-Constitutional Synthesis",
        "summary": "Calculates your exact Vata, Pitta, and Kapha percentages from your Vedic birth chart + current Dasha AND your Wood, Fire, Earth, Metal, and Water balance from your Chinese pillars, with a personalized diet, herb, breathwork, and home regimen.",
    },
]


# ---------------------------------------------------------------------------
# 1. LAL KITAB ENGINE (FIXED ARIES ASCENDANT, PAKKA GHAR, RINAS, PALMISTRY & UPAYAS)
# ---------------------------------------------------------------------------
LAL_KITAB_PAKKA_GHAR: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "pakka_ghar": "House 1 (Aries — Throne of Soul)",
        "exalted_house": 1, "debilitated_house": 7,
        "palm_mount": "Mount of Apollo (Sun Mount — beneath Ring Finger) & Sun Line (Vidya/Yash Rekha)",
        "karaka": "Father, Government, Vitality, Bones, Right Eye, Self-Respect, Heart",
        "benefic_signs": "Strong radiant vitality, government honor, leadership, self-earned authority.",
        "malefic_signs": "Ego clashes, bone/eye/heart strain, tax/government hurdles, strained bond with father.",
        "upaya_43_days": "Offer water mixed with jaggery (Gud) and red flowers to the rising Sun for 43 days; swallow a tiny piece of jaggery with water before starting important work; never accept anything for free.",
    },
    "Moon": {
        "pakka_ghar": "House 4 (Cancer — Throne of Mother & Peace)",
        "exalted_house": 2, "debilitated_house": 8,
        "palm_mount": "Mount of Luna (Moon Mount — outer lower edge of palm) & Intuition/Travel Lines",
        "karaka": "Mother, Liquid Cash, Emotional Peace, Mind, Left Eye, Horses, Fresh Water",
        "benefic_signs": "Deep mental serenity, strong maternal blessings, steady liquid cash, real estate comfort.",
        "malefic_signs": "Emotional anxiety, insomnia, fluctuating savings, sinus/cold sensitivity.",
        "upaya_43_days": "Touch your mother's feet daily; drink water/milk in a pure silver glass; keep a solid silver square (4 grams) in your wallet; never sell milk or exploit maternal figures.",
    },
    "Mars": {
        "pakka_ghar": "House 1 & House 8 (Aries/Scorpio — Courage & Shield)",
        "exalted_house": 10, "debilitated_house": 4,
        "palm_mount": "Upper Mars (below Mercury/Heart line), Lower Mars (above Thumb/Life line) & Plain of Mars",
        "karaka": "Brothers, Courage, Blood, Muscular Strength, Land/Property, Armed Forces, Surgery",
        "benefic_signs": "Fearless protector (*Mangal Nek*), loyal siblings, victory over enemies, land ownership.",
        "malefic_signs": "Impulsive anger (*Mangal Bad*), blood pressure/cuts, sibling disputes, property delays.",
        "upaya_43_days": "Float sweet Tandoori rotis or Rewari (sesame-jaggery sweets) in flowing water on Tuesdays; distribute sweet Boondi/Laddoos at a Hanuman temple; keep cordial harmony with brothers.",
    },
    "Mercury": {
        "pakka_ghar": "House 7 (Commercial & Intellectual Axis)",
        "exalted_house": 6, "debilitated_house": 12,
        "palm_mount": "Mount of Mercury (beneath Little Finger) & Line of Mercury (Business/Health Line)",
        "karaka": "Speech, Intellect, Trade, Nervous System, Sister, Daughter, Maternal Aunt (Bua), Teeth",
        "benefic_signs": "Razor-sharp business acumen, persuasive speech, diplomatic mastery, mathematical skill.",
        "malefic_signs": "Nervous restlessness, skin/allergy issues, commercial contract misunderstandings, dental sensitivity.",
        "upaya_43_days": "Clean your teeth with alum (Fitkari) water on Wednesdays; pierce nose/ear or wear a copper coin with a hole on a white thread; gift green bangles/sweets to sisters or young girls (Kanyas).",
    },
    "Jupiter": {
        "pakka_ghar": "Houses 2, 5, 9, 12 (Dharma, Lineage & Wisdom Pillars)",
        "exalted_house": 4, "debilitated_house": 10,
        "palm_mount": "Mount of Jupiter (beneath Index Finger) & Ring of Solomon (Guru Valaya)",
        "karaka": "Gold, Wisdom, Guru, Grandfather, Progeny, Liver, Breath/Prana, Peepal Tree",
        "benefic_signs": "Divine protection, respected counsel, thriving children, gold/treasury growth, spiritual authority.",
        "malefic_signs": "Weight/liver sluggishness, interrupted higher education, ancestral (Pitru) restlessness.",
        "upaya_43_days": "Apply a Tilak of pure saffron (Kesar) or turmeric on your forehead, tongue, and navel daily for 43 days; water a Peepal tree on Thursdays without touching it; offer Chana Dal & yellow cloth at a temple.",
    },
    "Venus": {
        "pakka_ghar": "House 7 (Marriage, Spouse & Worldly Comfort)",
        "exalted_house": 12, "debilitated_house": 6,
        "palm_mount": "Mount of Venus (fleshy base of the Thumb encircled by the Life Line) & Girdle of Venus",
        "karaka": "Spouse, Marriage, Vehicles, Luxury, Perfume, Skin, Reproductive Vitality, White Cow",
        "benefic_signs": "Loving marriage, artistic magnetism, luxury vehicles, radiant skin, effortless material grace.",
        "malefic_signs": "Marital friction, hormonal/reproductive strain, vehicle expenses, vanity blocks.",
        "upaya_43_days": "Feed green fodder or Jowar (sorghum) to a white/mother cow on Fridays; apply natural alcohol-free rose/mogra attar; keep your clothes clean and pressed; donate curd (yogurt) or camphor at a place of worship.",
    },
    "Saturn": {
        "pakka_ghar": "Houses 8, 10, 11 (Longevity, Karma & Mass Gains)",
        "exalted_house": 7, "debilitated_house": 1,
        "palm_mount": "Mount of Saturn (beneath Middle Finger) & Fate Line (Bhagya/Shani Rekha)",
        "karaka": "Machinery, Iron, Real Estate Construction, Laborers, Paternal Uncle (Chacha), Knees/Joints, Justice",
        "benefic_signs": "Enduring empire builder, loyal workforce, multiple properties, deep focus, long life.",
        "malefic_signs": "Chronic delays, joint/nerve pain, machinery breakdowns, legal/labor friction.",
        "upaya_43_days": "Perform Chhaya Dana (look at your reflection in mustard oil and donate it) on 7 Saturdays; feed oiled roti to black dogs and crows; bury a small clay pot filled with honey or surma (antimony) in an open field if Saturn is afflicted.",
    },
    "Rahu": {
        "pakka_ghar": "House 12 (Imagination, Foreign Realms & Thoughts)",
        "exalted_house": 3, "debilitated_house": 9,
        "palm_mount": "Central Upper Plain of Rahu (between Head Line and Heart Line) & Sudden Windfall Branches",
        "karaka": "Sudden Windfalls, Technology, Foreign Lands, In-Laws, Elephants, Barley, Blue/Smoke Color",
        "benefic_signs": "Brilliant out-of-the-box strategist, sudden wealth breakthroughs, mastery of modern technology.",
        "malefic_signs": "Overthinking, sudden misunderstandings, electronic failures, insomnia, phantom fears.",
        "upaya_43_days": "Keep a solid silver elephant (min 25g) in your living/work area; keep a small pouch of fennel (Saunf) under your pillow; wash 400g of barley in milk and flow it in running water on a Saturday; keep your staircase and roof spotless.",
    },
    "Ketu": {
        "pakka_ghar": "House 6 (Service, Intuition & Liberation)",
        "exalted_house": 9, "debilitated_house": 3,
        "palm_mount": "Mount of Ketu (base of palm above wrist bracelets / Manibandha between Venus & Moon)",
        "karaka": "Son, Maternal Uncle (Mama), Spine, Feet, Dogs, Two-Colored Blanket, Spiritual Intuition",
        "benefic_signs": "Unerring gut intuition, spiritual liberation, protective shield for children, victory in hidden matters.",
        "malefic_signs": "Spine/foot/urinary sensitivity, sudden detachments, maternal family worries.",
        "upaya_43_days": "Feed a two-colored (black-and-white) street dog daily; apply saffron tilak behind both earlobes; donate a black-and-white blanket at a sacred shrine on a Tuesday or Saturday.",
    },
}


def compute_lal_kitab_system(pos: Dict[str, Any], asc_lon: float) -> Dict[str, Any]:
    """Computes the complete Lal Kitab Kundli (Fixed Aries Ascendant where planets are
    placed by their natal house offset into Signs 1..12), Pakka Ghar status, Sleeping Planets,
    Lal Kitab Karmic Rinas, Palmistry Mount/Line correlations, and 43-Day Upayas."""
    lagna_idx = int(asc_lon // 30) % 12
    house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
    planet_houses: Dict[str, int] = {}

    # Build synthetic positions for the Fixed Aries Ascendant Lal Kitab SVG chart:
    # In Lal Kitab, House 1 is always Aries (0°..30°), House 2 is Taurus (30°..60°), etc.
    lk_pos_for_svg: Dict[str, Dict[str, Any]] = {}
    for idx_p, p in enumerate(VEDIC_PLANETS):
        p_lon = pos[p]["longitude"]
        p_sign = int(p_lon // 30) % 12
        natal_house = (p_sign - lagna_idx) % 12 + 1
        planet_houses[p] = natal_house
        house_occupants[natal_house].append(p)
        lk_pos_for_svg[p] = {
            "longitude": (natal_house - 1) * 30.0 + (p_lon % 30.0),
            "retrograde": pos[p].get("retrograde", False),
        }

    lk_pls_for_svg = [
        {"name": p, "sign": planet_houses[p] - 1, "retrograde": pos[p].get("retrograde", False)}
        for p in VEDIC_PLANETS
    ]
    lk_svg = SVG.north_indian(0, lk_pls_for_svg, 340, "Lal Kitab (Fixed Aries H1)")

    # Evaluate each planet in Lal Kitab
    planet_evaluations = []
    sleeping_planets = []
    for p in VEDIC_PLANETS:
        h = planet_houses[p]
        meta = LAL_KITAB_PAKKA_GHAR[p]
        # Lal Kitab aspect rule: 1staspects 7th, 2->6/8, 3->9/11, 4->10, 5->9, 6->12, 8->2, 9->3/5, 11->3
        is_exalted = (h == meta["exalted_house"])
        is_debilitated = (h == meta["debilitated_house"])
        is_pakka = str(h) in meta["pakka_ghar"]
        if is_exalted or is_pakka or h in (1, 2, 4, 5, 9, 11):
            status = "Nek (Benefic / Awakened)"
        elif is_debilitated or h in (6, 8, 12):
            status = "Mand (Challenged — Apply Upaya)"
        else:
            status = "Mixed / Conditional"

        # Sleeping planet check: if a house receives no planetary aspect in Lal Kitab
        # (Houses 7, 10, 8, 12 checked against their drishti senders 1, 4, 2, 6)
        sender_map = {7: [1], 10: [4], 8: [2], 12: [6], 9: [3, 5], 11: [3]}
        senders = sender_map.get(h, [])
        is_sleeping = bool(senders and all(len(house_occupants[s]) == 0 for s in senders) and len(house_occupants[h]) == 1)
        if is_sleeping:
            sleeping_planets.append({
                "planet": p,
                "house": h,
                "explanation": f"{p} in House {h} is a 'Sleeping Planet' (Soya Hua Graha) because its activating house ({', '.join('House ' + str(s) for s in senders)}) is empty.",
                "how_to_awaken": f"Activate House {senders[0]} by keeping the sacred item of {LAL_KITAB_PAKKA_GHAR[SIGN_LORDS[senders[0]-1]]['karaka'].split(',')[0]} or performing {p}'s 43-day Upaya.",
            })

        planet_evaluations.append({
            "planet": p,
            "lal_kitab_house": h,
            "kalpurush_fixed_sign": SIGNS[h - 1],
            "pakka_ghar_permanent_home": meta["pakka_ghar"],
            "lal_kitab_status": status,
            "palmistry_mount_and_line_link": meta["palm_mount"],
            "life_significations": meta["karaka"],
            "manifestation_in_your_chart": meta["benefic_signs"] if "Nek" in status else meta["malefic_signs"],
            "lal_kitab_43_day_upaya": meta["upaya_43_days"],
        })

    # Lal Kitab Karmic Debts (Rinas)
    rinas = []
    if any(planet_houses[p] in (2, 5, 9, 12) for p in ("Rahu", "Ketu", "Saturn")):
        rinas.append({
            "rina_name": "Pitru Rina (Ancestral / Forefathers' Debt)",
            "cause_in_chart": "Presence of Rahu, Ketu, or Saturn in Jupiter's houses (2, 5, 9, or 12).",
            "life_effect": "Sudden reputation tests, delays in higher education or career promotion despite hard work.",
            "lal_kitab_remedy": "Collect a small coin from every family member and donate the combined sum at a temple on a Thursday, or water a Peepal tree for 43 days.",
        })
    if planet_houses["Sun"] == 5 or planet_houses["Venus"] == 5:
        rinas.append({
            "rina_name": "Swa-Rina (Self / Past-Life Ego Debt)",
            "cause_in_chart": "Sun or Venus placed in the 5th house of Purva Punya.",
            "life_effect": "Taking on others' burdens without appreciation, acid/heartburn, or financial fluctuations.",
            "lal_kitab_remedy": "Perform a small Havan/Agni offering or feed jaggery and wheat to a reddish-brown cow.",
        })
    if planet_houses["Ketu"] == 4 or planet_houses["Moon"] in (6, 8, 12):
        rinas.append({
            "rina_name": "Matru Rina (Mother's / Nurturing Debt)",
            "cause_in_chart": "Ketu in the 4th house or Moon in 6th/8th/12th.",
            "life_effect": "Restless sleep, domestic shifts, or emotional worry.",
            "lal_kitab_remedy": "Flow equal weights of silver coins or rice in a clean river on a Monday and serve your mother/elderly women.",
        })
    if planet_houses["Sun"] in (2, 7) or planet_houses["Rahu"] in (2, 7):
        rinas.append({
            "rina_name": "Stree Rina (Spouse / Feminine Lineage Debt)",
            "cause_in_chart": "Sun or Rahu in the 2nd or 7th house (Venus's domain).",
            "life_effect": "Relationship misunderstandings or unexpected household expenses.",
            "lal_kitab_remedy": "Feed green grass/fodder to 11 cows on a Friday and always treat women in the family with utmost respect.",
        })
    if not rinas:
        rinas.append({
            "rina_name": "Clear Rina Ledger (No Major Lal Kitab Rina Affliction)",
            "cause_in_chart": "Jupiter, Moon, and Venus houses are free of severe nodal Rina triggers.",
            "life_effect": "Strong ancestral and domestic protection.",
            "lal_kitab_remedy": "Maintain daily gratitude, offer the first roti of the kitchen to a cow, and the last roti to a dog.",
        })

    # Blind Chart (Andhe Graha) check: 2+ inimical planets in House 10
    is_blind_chart = len(house_occupants[10]) >= 3
    return {
        "tradition_name": "Lal Kitab (Pandit Roop Chand Joshi)",
        "methodology_explained": (
            "Unlike classical Parashari astrology, Lal Kitab fixes the 1st House as Aries (Kalpurush Ascendant) for every human being, "
            "placing your natal planets into the exact houses (1 to 12) they occupy from your birth Lagna. It skips complex divisional charts "
            "and links every house directly to a Mount on your palm and practical, low-cost 43-day daily remedies (Upayas)."
        ),
        "lal_kitab_fixed_aries_svg": lk_svg,
        "blind_chart_andhe_graha_check": (
            "Active (3+ planets in 10th house — feed 10 visually impaired people to unlock career sight)"
            if is_blind_chart
            else "Clear (Your 10th house of Karma has clear vision; planets act openly)"
        ),
        "sleeping_planets_soye_hue_graha": sleeping_planets or [
            {"planet": "None", "house": 0, "explanation": "All occupied houses in your chart are actively aspected or self-awakened.", "how_to_awaken": "Continue regular morning sunlight and daily gratitude."}
        ],
        "karmic_rinas_and_remedies": rinas,
        "nine_planet_pakka_ghar_and_palmistry_table": planet_evaluations,
    }


# ---------------------------------------------------------------------------
# 2. JAIMINI SUTRAS ENGINE (7 CHARA KARAKAS, ARUDHA PADAS, RASHI DRISHTI & CHARA DASHA)
# ---------------------------------------------------------------------------
def compute_jaimini_system(pos: Dict[str, Any], asc_lon: float, birth_dt_utc: datetime) -> Dict[str, Any]:
    """Computes Sage Jaimini's Upadesha Sutra system: 7 Chara Karakas, Karakamsha Lagna,
    Arudha Padas (AL, UL, A7, A10), Rashi Drishti (Sign Aspects), and Chara Dasha."""
    lagna_idx = int(asc_lon // 30) % 12
    seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    sorted_p = sorted(seven_planets, key=lambda p: pos[p]["longitude"] % 30.0, reverse=True)
    karaka_titles = [
        ("Atmakaraka (AK)", "Supreme King of the Chart — Soul's deepest desire, spiritual evolution & inner truth"),
        ("Amatyakaraka (AmK)", "Prime Minister — Career direction, professional counsel & mind's execution"),
        ("Bhratrukaraka (BK)", "Siblings, Guru, mentors, courage & sacred guidance"),
        ("Matrukaraka (MK)", "Mother, homeland, emotional nourishment, real estate & inner peace"),
        ("Putrakaraka (PK)", "Children, creative intelligence, followers, authorship & future legacy"),
        ("Gnatikaraka (GK)", "Competitors, obstacles, health resilience & karmic cousins"),
        ("Darakaraka (DK)", "Spouse, marriage partner, business partnerships & heart magnetism"),
    ]
    chara_karakas = []
    for idx, p in enumerate(sorted_p):
        lon = pos[p]["longitude"]
        s_idx = int(lon // 30) % 12
        deg_in_sign = lon % 30.0
        nav_idx = int(lon / (30.0 / 9.0)) % 12
        title, meaning = karaka_titles[idx]
        chara_karakas.append({
            "karaka_rank": idx + 1,
            "karaka_name": title,
            "planet": p,
            "degree_in_sign": f"{int(deg_in_sign):02d}°{int((deg_in_sign % 1) * 60):02d}'",
            "rashi_sign": f"{SIGNS[s_idx]} ({RASHIS[s_idx]})",
            "navamsha_d9_sign": f"{SIGNS[nav_idx]} ({RASHIS[nav_idx]})",
            "soul_signification": meaning,
        })

    ak_planet = sorted_p[0]
    ak_nav_idx = int(pos[ak_planet]["longitude"] / (30.0 / 9.0)) % 12
    karakamsha_sign = SIGNS[ak_nav_idx]
    karakamsha_house_from_lagna = (ak_nav_idx - lagna_idx) % 12 + 1

    # Arudha Padas (AL = Arudha of 1st, UL = Upapada Arudha of 12th, A7 = Darapada, A10 = Rajyapada)
    def _calc_arudha(house_num: int) -> Dict[str, Any]:
        h_sign = (lagna_idx + house_num - 1) % 12
        lord = SIGN_LORDS[h_sign]
        lord_sign = int(pos[lord]["longitude"] // 30) % 12
        diff = (lord_sign - h_sign) % 12
        pada_sign = (lord_sign + diff) % 12
        # Jaimini Sutra exception: if Arudha falls in 1st or 7th from the house itself, move 10 signs forward
        rel = (pada_sign - h_sign) % 12 + 1
        if rel in (1, 7):
            pada_sign = (pada_sign + 9) % 12
        return {
            "sign": SIGNS[pada_sign],
            "rashi": RASHIS[pada_sign],
            "lord": SIGN_LORDS[pada_sign],
            "house_from_lagna": (pada_sign - lagna_idx) % 12 + 1,
        }

    al = _calc_arudha(1)
    ul = _calc_arudha(12)
    a7 = _calc_arudha(7)
    a10 = _calc_arudha(10)

    # Jaimini Rashi Drishti (Sign Aspects) from Lagna & Atmakaraka Sign
    def _rashi_drishti(s_idx: int) -> List[str]:
        # Movable (0,3,6,9) aspect Fixed (1,4,7,10) except adjacent; Fixed aspect Movable except adjacent; Dual (2,5,8,11) aspect other Duals
        mod = s_idx % 3
        aspected = []
        for other in range(12):
            if other == s_idx:
                continue
            if mod == 0 and (other % 3 == 1) and ((other - s_idx) % 12 != 1):
                aspected.append(SIGNS[other])
            elif mod == 1 and (other % 3 == 0) and ((s_idx - other) % 12 != 1):
                aspected.append(SIGNS[other])
            elif mod == 2 and (other % 3 == 2):
                aspected.append(SIGNS[other])
        return aspected

    chara_dasha = D.chara_dasha(pos, asc_lon, ephem.jd_from_utc(birth_dt_utc), timezone.utc, cycles=1)
    return {
        "tradition_name": "Jaimini Sutras (Maharishi Jaimini)",
        "methodology_explained": (
            "Sage Jaimini's system differs from Parashari by using 7 degree-ranked Chara Karakas (excluding Rahu/Ketu in primary Karaka assignment), "
            "Sign-to-Sign Aspects (Rashi Drishti), Arudha Padas (showing how the material world perceives you vs. your inner reality), "
            "Karakamsha Lagna (the Navamsha sign of your Atmakaraka), and Sign-based Chara Dasha periods."
        ),
        "seven_chara_karakas": chara_karakas,
        "karakamsha_lagna": {
            "atmakaraka_planet": ak_planet,
            "karakamsha_sign": karakamsha_sign,
            "house_in_d1": karakamsha_house_from_lagna,
            "interpretation": (
                f"Your Atmakaraka ({ak_planet}) falls in {karakamsha_sign} in the Navamsha (D9), placing your Karakamsha in House {karakamsha_house_from_lagna} "
                f"of your birth chart. In Jaimini Sutras, this reveals your deepest soul vocation and spiritual liberation (Moksha) path."
            ),
        },
        "arudha_padas": {
            "arudha_lagna_AL": {**al, "meaning": "Public Image, Status & Maya (how society perceives your authority)"},
            "upapada_lagna_UL": {**ul, "meaning": "Marriage, Spouse's Lineage & Long-Term Domestic Bond"},
            "darapada_A7": {**a7, "meaning": "Business Partnerships, Charisma & Romantic Attraction"},
            "rajyapada_A10": {**a10, "meaning": "Executive Power, Career Throne & Public Recognition"},
        },
        "jaimini_rashi_drishti_from_lagna": _rashi_drishti(lagna_idx),
        "chara_dasha_periods": chara_dasha[:12] if isinstance(chara_dasha, list) else chara_dasha,
    }


# ---------------------------------------------------------------------------
# 3. NADI ASTROLOGY ENGINE (150 NADI AMSHAS, THUMBPRINT ARCHETYPES & BHRIGU NANDI NADI)
# ---------------------------------------------------------------------------
NADI_NAMES_15 = [
    "Vasudha", "Vaishnavi", "Brahmi", "Kalakoota", "Shankari",
    "Sudhakara", "Sama", "Saumya", "Sura", "Maya",
    "Manohara", "Madhavi", "Manjuswana", "Ghora", "Kumbhini",
]


def compute_nadi_system(pos: Dict[str, Any], asc_lon: float) -> Dict[str, Any]:
    """Computes Tamil Nadi & Bhrigu Nandi Nadi palm-leaf astrology:
    150 Nadi Amsha division, Thumbprint ridge archetype (Shankha/Chakra/Padma),
    Bhrigu Nandi Nadi (BNN) planetary circuits (Jupiter=Jeeva, Saturn=Karma),
    14 Kandams (Palm-Leaf Chapters) summary, and Nadi Parihara."""
    lagna_idx = int(asc_lon // 30) % 12
    deg_in_sign = asc_lon % 30.0
    nadi_amsha_num = int(deg_in_sign * 5.0) + 1  # 1..150 (each 12 arc-minutes)
    nadi_name = NADI_NAMES_15[(nadi_amsha_num - 1) % 15]

    # Thumbprint archetype linked to Lagna modality + Moon/Jupiter/Saturn signature
    mod = lagna_idx % 3
    if mod == 0:
        thumb = {
            "sanskrit_class": "Chakra Rekha (Concentric Whorl / Spiral Disc)",
            "english_type": "Whorl Pattern (1–2 Deltas with Central Spiral)",
            "meaning": "Associated with self-made pioneers, strong karmic autonomy, leadership destiny, and Dharmic authority.",
        }
    elif mod == 1:
        thumb = {
            "sanskrit_class": "Shankha Rekha (Sacred Conch Loop)",
            "english_type": "Ulnar / Radial Loop Pattern (Flowing Curved Ridges)",
            "meaning": "Associated with adaptability, wealth accumulation, diplomatic grace, and protective ancestral blessings.",
        }
    else:
        thumb = {
            "sanskrit_class": "Padma / Kodanda Rekha (Lotus Arch & Twin-Loop)",
            "english_type": "Tented Arch / Composite Twin-Loop Pattern",
            "meaning": "Associated with multi-disciplinary intellect, spiritual teaching, intuitive healing, and bridge-building across cultures.",
        }

    # Bhrigu Nandi Nadi (BNN) Trinal (1-5-9) & Directional (2, 12, 7) links for Jupiter (Jeeva) and Saturn (Karma)
    sign_planets: Dict[int, List[str]] = {i: [] for i in range(12)}
    for p in VEDIC_PLANETS:
        s = int(pos[p]["longitude"] // 30) % 12
        sign_planets[s].append(p)

    def _bnn_circuit(base_planet: str) -> Dict[str, Any]:
        b_sign = int(pos[base_planet]["longitude"] // 30) % 12
        trine_planets = []
        for offset in (0, 4, 8):
            for p in sign_planets[(b_sign + offset) % 12]:
                if p != base_planet:
                    trine_planets.append(p)
        opp_planets = sign_planets[(b_sign + 6) % 12]
        next_planets = sign_planets[(b_sign + 1) % 12]
        prev_planets = sign_planets[(b_sign - 1) % 12]
        return {
            "sign": SIGNS[b_sign],
            "trine_1_5_9_partners": trine_planets,
            "seventh_opposition_partners": opp_planets,
            "second_house_ahead_planets": next_planets,
            "twelfth_house_behind_planets": prev_planets,
        }

    jeeva_circuit = _bnn_circuit("Jupiter")
    karma_circuit = _bnn_circuit("Saturn")

    kandams = [
        {"kandam": "Kandam 1 (General Life & Thumbprint Leaf Match)", "reading": f"Born under {SIGNS[lagna_idx]} Lagna, Nadi Amsha #{nadi_amsha_num} ({nadi_name} Nadi). Jeeva Karaka Jupiter resides in {jeeva_circuit['sign']} connected with {', '.join(jeeva_circuit['trine_1_5_9_partners']) or 'pure self-effort'}."},
        {"kandam": "Kandam 2 (Wealth, Speech, Family & Education)", "reading": f"Mercury ({SIGNS[int(pos['Mercury']['longitude']//30)%12]}) and Venus ({SIGNS[int(pos['Venus']['longitude']//30)%12]}) govern your intellectual and financial treasury."},
        {"kandam": "Kandam 7 (Marriage & Life Partner Leaf)", "reading": f"Venus and Mars form your marital axis; harmonious fulfillment blooms when honoring your Upapada and 7th lord."},
        {"kandam": "Kandam 10 (Career, Destiny & Karma Circuit)", "reading": f"Karma Karaka Saturn in {karma_circuit['sign']} links with {', '.join(karma_circuit['trine_1_5_9_partners'] + karma_circuit['seventh_opposition_partners']) or 'independent mastery'}, giving rise through structured perseverance, technology/administration, and dharmic service."},
        {"kandam": "Kandam 13 & 14 (Shanthi / Past-Life Karma & Mantra कवच)", "reading": f"Ketu in {SIGNS[int(pos['Ketu']['longitude']//30)%12]} and Rahu in {SIGNS[int(pos['Rahu']['longitude']//30)%12]} indicate past-life vows completed through lighting sesame/ghee lamps at an ancient Shiva/Vishnu shrine and feeding the needy on birth-star (Janma Nakshatra) days."},
    ]

    return {
        "tradition_name": "Nadi Astrology (Agastya, Bhrigu & Bhrigu Nandi Nadi)",
        "methodology_explained": (
            "Originating in the ancient palm-leaf libraries of Tamil Nadu (Vaitheeswaran Koil) and Sages Agastya & Bhrigu, "
            "Nadi astrology identifies a seeker's bundle via thumbprint ridge patterns (Rekha Shastra), divides each zodiac sign into "
            "150 micro-divisions (Nadi Amshas of 12 arc-minutes each), and reads planetary energy circuits around Jupiter (Jeeva/Soul) and Saturn (Karma/Action)."
        ),
        "nadi_amsha_signature": {
            "nadi_amsha_number_1_to_150": nadi_amsha_num,
            "nadi_name": f"{nadi_name} Nadi",
            "ascendant_degree": f"{SIGNS[lagna_idx]} {int(deg_in_sign):02d}°{int((deg_in_sign % 1)*60):02d}'",
        },
        "thumbprint_palm_leaf_classification": thumb,
        "bhrigu_nandi_nadi_circuits": {
            "jeeva_karaka_jupiter_circuit": jeeva_circuit,
            "karma_karaka_saturn_circuit": karma_circuit,
        },
        "palm_leaf_kandams_reading": kandams,
    }


# ---------------------------------------------------------------------------
# 4. HELLENISTIC ASTROLOGY ENGINE (SECT, LOTS, WHOLE-SIGN HOUSES & ANNUAL PROFECTIONS)
# ---------------------------------------------------------------------------
def compute_hellenistic_system(
    jd: float,
    birth_dt_utc: datetime,
    lat: float,
    lon: float,
) -> Dict[str, Any]:
    """Computes Ancient Greco-Roman Hellenistic Astrology (1st c. BCE – 2nd c. CE):
    Sect (Diurnal vs Nocturnal), Sect Light, Benefic/Malefic of Sect, Whole-Sign Houses,
    Lot of Fortune & Lot of Spirit (with Day/Night reversal), and Annual Profections."""
    trop_pos = ephem.all_positions(jd, sidereal=False)
    _, asc_trop, mc_trop = ephem.houses(jd, lat, lon, "W", sidereal=False)
    sun_lon = trop_pos["Sun"]["longitude"]
    moon_lon = trop_pos["Moon"]["longitude"]

    # Day chart if Sun is above the Ascendant-Descendant horizon (i.e. within 180° clockwise from Descendant to Ascendant -> sin(asc - sun) > 0)
    diff_asc_sun = (asc_trop - sun_lon) % 360.0
    is_day_chart = 0.0 <= diff_asc_sun < 180.0

    if is_day_chart:
        sect_info = {
            "sect": "Diurnal (Day Chart — Sun Above the Horizon)",
            "sect_light": "Sun (Leo/Solar Luminary)",
            "most_constructive_benefic_of_sect": "Jupiter (Greater Benefic in Sect — brings maximum protection, mentorship & elevation)",
            "secondary_benefic": "Venus (Out-of-Sect Benefic)",
            "constructive_malefic_of_sect": "Saturn (Malefic in Sect — teaches discipline, mastery, endurance & long-term structure)",
            "contrary_to_sect_malefic": "Mars (Out-of-Sect Malefic — primary source of acute friction, heat, or impulsive haste; needs conscious channeling)",
        }
        lot_fortune = (asc_trop + moon_lon - sun_lon) % 360.0
        lot_spirit = (asc_trop + sun_lon - moon_lon) % 360.0
    else:
        sect_info = {
            "sect": "Nocturnal (Night Chart — Sun Below the Horizon)",
            "sect_light": "Moon (Lunar Luminary)",
            "most_constructive_benefic_of_sect": "Venus (Benefic in Sect — brings grace, harmony, relationship blessings & artistic fortune)",
            "secondary_benefic": "Jupiter (Out-of-Sect Benefic)",
            "constructive_malefic_of_sect": "Mars (Malefic in Sect — provides decisive courage, drive, athletic/executive stamina)",
            "contrary_to_sect_malefic": "Saturn (Out-of-Sect Malefic — primary source of delays, coldness, or heavy burdens; needs warmth & patience)",
        }
        lot_fortune = (asc_trop + sun_lon - moon_lon) % 360.0
        lot_spirit = (asc_trop + moon_lon - sun_lon) % 360.0

    asc_sign_idx = int(asc_trop // 30) % 12
    f_sign = int(lot_fortune // 30) % 12
    s_sign = int(lot_spirit // 30) % 12

    # Annual Profections for current age
    today = Date.today()
    b_date = birth_dt_utc.date()
    age = max(0, today.year - b_date.year - ((today.month, today.day) < (b_date.month, b_date.day)))
    profected_house = (age % 12) + 1
    profected_sign_idx = (asc_sign_idx + profected_house - 1) % 12
    time_lord = SIGN_LORDS[profected_sign_idx]

    return {
        "tradition_name": "Hellenistic Astrology (Greco-Roman Classical Tradition)",
        "methodology_explained": (
            "Developed in Alexandria and the Greco-Roman world (1st c. BCE – 2nd c. CE by Vettius Valens, Dorotheus & Ptolemy), "
            "Hellenistic astrology first evaluates Sect (whether you were born by Day or Night) to identify your most helpful Benefic "
            "and most challenging Malefic, uses Whole-Sign Houses (Topoi), casts the Lots of Fortune and Spirit, and activates one house per year via Annual Profections."
        ),
        "sect_analysis": sect_info,
        "whole_sign_ascendant": f"{SIGNS[asc_sign_idx]} ({asc_trop % 30.0:.2f}°)",
        "hellenistic_lots": {
            "lot_of_fortune_pars_fortunae": {
                "sign": SIGNS[f_sign],
                "degree": f"{lot_fortune % 30.0:.2f}°",
                "whole_sign_house": (f_sign - asc_sign_idx) % 12 + 1,
                "ruler": SIGN_LORDS[f_sign],
                "meaning": "Governs the physical body, material fortune, health, and events that happen to you through circumstance.",
            },
            "lot_of_spirit_pars_spiritus": {
                "sign": SIGNS[s_sign],
                "degree": f"{lot_spirit % 30.0:.2f}°",
                "whole_sign_house": (s_sign - asc_sign_idx) % 12 + 1,
                "ruler": SIGN_LORDS[s_sign],
                "meaning": "Governs deliberate willpower, career vocation, soul agency, and what you actively initiate in the world.",
            },
        },
        "annual_profection_current_year": {
            "current_age": age,
            "activated_whole_sign_house": profected_house,
            "profected_sign": SIGNS[profected_sign_idx],
            "lord_of_the_year_chronocrator": time_lord,
            "yearly_forecast": (
                f"At age {age}, your Annual Profection activates your {profected_house}th Whole-Sign House ({SIGNS[profected_sign_idx]}), "
                f"making {time_lord} your supreme Time Lord (Chronocrator) for this entire birthday year! Transits to and by {time_lord} set the timing of major events."
            ),
        },
    }


# ---------------------------------------------------------------------------
# 5. MODERN PSYCHOLOGICAL & EVOLUTIONARY ASTROLOGY ENGINE (JUNGIAN & PLUTO AXIS)
# ---------------------------------------------------------------------------
def compute_psychological_evolutionary_system(jd: float, lat: float, lon: float) -> Dict[str, Any]:
    """Computes Jungian Psychological & Jeffrey Wolf Green Evolutionary Astrology:
    Pluto Soul Evolution Axis, Pluto Polarity Point (PPP), North/South Lunar Nodes,
    and Jungian Archetypes (Persona, Ego, Anima/Animus, Shadow, Self)."""
    trop = ephem.all_positions(jd, sidereal=False)
    _, asc_lon, mc_lon = ephem.houses(jd, lat, lon, "P", sidereal=False)
    asc_idx = int(asc_lon // 30) % 12

    pluto_lon = trop["Pluto"]["longitude"]
    pluto_sign_idx = int(pluto_lon // 30) % 12
    pluto_house = (pluto_sign_idx - asc_idx) % 12 + 1

    ppp_lon = (pluto_lon + 180.0) % 360.0
    ppp_sign_idx = int(ppp_lon // 30) % 12
    ppp_house = (ppp_sign_idx - asc_idx) % 12 + 1

    nn_lon = trop["Rahu"]["longitude"]
    sn_lon = trop["Ketu"]["longitude"]
    nn_sign = SIGNS[int(nn_lon // 30) % 12]
    sn_sign = SIGNS[int(sn_lon // 30) % 12]
    nn_house = (int(nn_lon // 30) % 12 - asc_idx) % 12 + 1
    sn_house = (int(sn_lon // 30) % 12 - asc_idx) % 12 + 1

    sun_sign = SIGNS[int(trop["Sun"]["longitude"] // 30) % 12]
    moon_sign = SIGNS[int(trop["Moon"]["longitude"] // 30) % 12]
    saturn_sign = SIGNS[int(trop["Saturn"]["longitude"] // 30) % 12]

    return {
        "tradition_name": "Modern Psychological & Evolutionary Astrology (Jungian & Pluto Paradigm)",
        "methodology_explained": (
            "Inspired by Carl Jung's depth psychology (Dane Rudhyar, Liz Greene) and Evolutionary Astrology (Jeffrey Wolf Green), "
            "this tradition views the birth chart as a blueprint of the psyche, unconscious complexes, and soul evolution across lifetimes — "
            "anchored by Pluto (deepest soul desire), the Pluto Polarity Point (evolutionary leap), and the Lunar Nodes."
        ),
        "evolutionary_pluto_axis": {
            "natal_pluto_soul_memory": f"{SIGNS[pluto_sign_idx]} (House {pluto_house})",
            "past_life_compulsion_and_security": (
                f"With Natal Pluto in {SIGNS[pluto_sign_idx]} (House {pluto_house}), your soul enters this life with deep mastery — "
                f"and unconscious attachment — to the themes of House {pluto_house} and {SIGNS[pluto_sign_idx]}."
            ),
            "pluto_polarity_point_PPP_growth_edge": f"{SIGNS[ppp_sign_idx]} (House {ppp_house})",
            "present_life_evolutionary_intention": (
                f"Your Pluto Polarity Point lies in {SIGNS[ppp_sign_idx]} (House {ppp_house}): your soul's primary evolutionary breakthrough "
                f"happens when you step out of {SIGNS[pluto_sign_idx]} control patterns and embrace the open polarity of {SIGNS[ppp_sign_idx]}."
            ),
            "south_node_karmic_habit": f"{sn_sign} (House {sn_house})",
            "north_node_destiny_compass": f"{nn_sign} (House {nn_house})",
        },
        "jungian_psyche_archetypes": [
            {"archetype": "The Persona (Outer Social Mask — Ascendant)", "placement": f"{SIGNS[asc_idx]} Rising", "psychological_dynamic": f"You greet the world through the lens of {SIGNS[asc_idx]}, projecting its natural instincts as your protective social interface."},
            {"archetype": "The Conscious Hero / Ego (Sun)", "placement": f"Sun in {sun_sign}", "psychological_dynamic": f"Your conscious identity and creative vitality individuate by embodying the highest qualities of {sun_sign}."},
            {"archetype": "The Inner Child & Emotional Soul (Moon / Anima-Animus)", "placement": f"Moon in {moon_sign}", "psychological_dynamic": f"At an instinctive cellular level, you require {moon_sign} nourishment to feel emotionally safe and whole."},
            {"archetype": "The Shadow & Inner Critic (Saturn & Pluto)", "placement": f"Saturn in {saturn_sign} / Pluto in {SIGNS[pluto_sign_idx]}", "psychological_dynamic": f"Where you initially feel fear, inhibition, or over-control ({saturn_sign} & {SIGNS[pluto_sign_idx]}) holds your greatest reservoir of integrated mastery once owned consciously."},
        ],
    }


# ---------------------------------------------------------------------------
# 6. URANIAN / HAMBURG SCHOOL ENGINE (90° DIAL, MIDPOINTS & 8 TRANS-NEPTUNIANS)
# ---------------------------------------------------------------------------
# Classical Witte/Sieggrün mean orbital elements (J2000 epoch 2451545.0) for the 8 Uranian TNPs
URANIAN_TNPS = [
    ("Cupido",   265.0, 0.003753, "Marriage, family bonds, art, social synthesis, corporations & community"),
    ("Hades",     75.8, 0.002735, "Antiquity, deep research, occult secrets, medicine, recycling & hidden history"),
    ("Zeus",     168.6, 0.002165, "Directed fire, engineering, machinery, leadership, procreation & decisive creation"),
    ("Kronos",    84.2, 0.001891, "Supreme authority, government, mastery, high altitude, bureaucracy & excellence"),
    ("Apollon",  192.4, 0.001715, "Science, global commerce, peace, wide expansion, wisdom & multiplied success"),
    ("Admetos",   58.9, 0.001580, "Deep roots, real estate, raw materials, unshakeable endurance & condensation"),
    ("Vulkanus", 112.5, 0.001485, "Mighty dynamic power, volcanic energy, momentum & unstoppable triumph"),
    ("Poseidon", 218.2, 0.001334, "Enlightenment, higher spirit, philosophy, media illumination & universal truth"),
]


def compute_uranian_hamburg_system(jd: float, lat: float, lon: float) -> Dict[str, Any]:
    """Computes the 20th-century Uranian / Hamburg School & Ebertin Cosmobiology system:
    8 Hypothetical Trans-Neptunian Planets (TNPs), 90° Cosmobiology Dial positions,
    and core Planetary Midpoints (A/B = C) with sharp event-based interpretations."""
    trop = ephem.all_positions(jd, sidereal=False)
    _, asc_lon, mc_lon = ephem.houses(jd, lat, lon, "P", sidereal=False)

    days_since_j2000 = jd - 2451545.0
    tnp_table = []
    all_points_360: Dict[str, float] = {
        "Sun": trop["Sun"]["longitude"],
        "Moon": trop["Moon"]["longitude"],
        "Mercury": trop["Mercury"]["longitude"],
        "Venus": trop["Venus"]["longitude"],
        "Mars": trop["Mars"]["longitude"],
        "Jupiter": trop["Jupiter"]["longitude"],
        "Saturn": trop["Saturn"]["longitude"],
        "Uranus": trop["Uranus"]["longitude"],
        "Neptune": trop["Neptune"]["longitude"],
        "Pluto": trop["Pluto"]["longitude"],
        "Node": trop["Rahu"]["longitude"],
        "Asc": asc_lon,
        "MC": mc_lon,
    }

    for name, lon0, daily_motion, meaning in URANIAN_TNPS:
        lon = (lon0 + daily_motion * days_since_j2000) % 360.0
        all_points_360[name] = lon
        s_idx = int(lon // 30) % 12
        tnp_table.append({
            "tnp_name": name,
            "longitude_360": round(lon, 2),
            "sign_position": f"{SIGNS[s_idx]} {lon % 30.0:.2f}°",
            "dial_90_modulus": round(lon % 90.0, 2),
            "witte_signification": meaning,
        })

    # Core Cosmobiology / Uranian Midpoints on the 90° Dial
    midpoint_specs = [
        ("Sun", "Moon", "Core Vitality, Marriage Harmony & Inner-Outer Integration Axis"),
        ("Asc", "MC", "Personal Identity, Vocation & Immediate Environment Axis"),
        ("Sun", "Jupiter", "Health, Wealth, Recognition & Karma-Free Success Axis"),
        ("Venus", "Mars", "Passion, Creative Magnetism, Romance & Biological Drive Axis"),
        ("Mercury", "Uranus", "Inventive Genius, Computing, Sudden Insight & Lightning Reflexes Axis"),
        ("Jupiter", "Uranus", "Sudden Windfall, Breakthrough Luck & Fortunate Turning-Point Axis (Thank-God Axis)"),
        ("Saturn", "Pluto", "Extreme Endurance, Monumental Effort & Deep Structural Transformation Axis"),
    ]

    midpoints_evaluated = []
    for p1, p2, desc in midpoint_specs:
        l1, l2 = all_points_360[p1], all_points_360[p2]
        diff = ((l2 - l1 + 540.0) % 360.0) - 180.0
        mp_360 = (l1 + diff / 2.0) % 360.0
        mp_90 = mp_360 % 90.0
        # Find any planet or TNP within 2.0° on the 90° dial (hard aspect 0°, 45°, 90°, 135°, 180°)
        hits = []
        for k, v in all_points_360.items():
            if k in (p1, p2):
                continue
            v90 = v % 90.0
            d90 = min(abs(v90 - mp_90), 90.0 - abs(v90 - mp_90))
            if d90 <= 2.2:
                hits.append(f"{k} (orb {d90:.2f}°)")
        midpoints_evaluated.append({
            "midpoint_formula": f"{p1}/{p2}",
            "midpoint_360": f"{SIGNS[int(mp_360 // 30) % 12]} {mp_360 % 30.0:.2f}°",
            "dial_90_degree": f"{mp_90:.2f}°",
            "activated_by_planets_or_tnps": hits or ["Unoccupied direct axis (activated during transits/solar arc)"],
            "planetary_picture_meaning": desc,
        })

    return {
        "tradition_name": "Uranian / Hamburg School & Cosmobiology (Witte / Ebertin)",
        "methodology_explained": (
            "Founded by Alfred Witte in Hamburg and expanded by Reinhold Ebertin's Cosmobiology, the Uranian system dispenses with traditional "
            "houses in favor of symmetrical Planetary Pictures (A + B - C), Midpoints (A/B = C), the 90-Degree Dial (which groups 0°, 45°, 90°, 135°, 180° "
            "hard event-producing angles together), and 8 hypothetical Trans-Neptunian Planets (Cupido through Poseidon)."
        ),
        "trans_neptunian_planets_8": tnp_table,
        "planetary_midpoints_90_dial": midpoints_evaluated,
    }


# ---------------------------------------------------------------------------
# 7. CHINESE BAZI (FOUR PILLARS OF DESTINY, 12 ANIMALS & FIVE ELEMENTS WU XING)
# ---------------------------------------------------------------------------
HEAVENLY_STEMS = [
    ("Jia (甲)", "Yang", "Wood"), ("Yi (乙)", "Yin", "Wood"),
    ("Bing (丙)", "Yang", "Fire"), ("Ding (丁)", "Yin", "Fire"),
    ("Wu (戊)", "Yang", "Earth"), ("Ji (己)", "Yin", "Earth"),
    ("Geng (庚)", "Yang", "Metal"), ("Xin (辛)", "Yin", "Metal"),
    ("Ren (壬)", "Yang", "Water"), ("Gui (癸)", "Yin", "Water"),
]

EARTHLY_BRANCHES = [
    ("Zi (子)", "Rat", "Water", "Yang"),
    ("Chou (丑)", "Ox", "Earth", "Yin"),
    ("Yin (寅)", "Tiger", "Wood", "Yang"),
    ("Mao (卯)", "Rabbit", "Wood", "Yin"),
    ("Chen (辰)", "Dragon", "Earth", "Yang"),
    ("Si (巳)", "Snake", "Fire", "Yin"),
    ("Wu (午)", "Horse", "Fire", "Yang"),
    ("Wei (未)", "Goat", "Earth", "Yin"),
    ("Shen (申)", "Monkey", "Metal", "Yang"),
    ("You (酉)", "Rooster", "Metal", "Yin"),
    ("Xu (戌)", "Dog", "Earth", "Yang"),
    ("Hai (亥)", "Pig", "Water", "Yin"),
]


def compute_chinese_bazi_system(birth_dt_local: datetime, jd: float) -> Dict[str, Any]:
    """Computes Chinese Astrology: 12 Animal Sign, BaZi Four Pillars of Destiny
    (Year, Month, Day Master, Hour Pillars), Yin/Yang Polarity, and Five Elements (Wu Xing)."""
    base_ch = CH.zodiac_year(birth_dt_local)
    y = birth_dt_local.year
    m = birth_dt_local.month
    d = birth_dt_local.day
    hr = birth_dt_local.hour

    # Adjust solar year for Lichun (~Feb 4)
    solar_y = y - 1 if (m == 1 or (m == 2 and d < 4)) else y
    y_stem_idx = (solar_y - 4) % 10
    y_branch_idx = (solar_y - 4) % 12

    # Month Pillar (Tiger month starts Feb)
    m_branch_idx = (m + 12) % 12
    m_stem_idx = ((y_stem_idx % 5) * 2 + (m - 1)) % 10

    # Day Pillar (Sexagenary cycle from Julian Day Number)
    jdn = int(jd + 0.5)
    d_stem_idx = (jdn + 9) % 10
    d_branch_idx = (jdn + 1) % 12

    # Hour Pillar (2-hour Chinese Shichen)
    hr_branch_idx = ((hr + 1) // 2) % 12
    hr_stem_idx = ((d_stem_idx % 5) * 2 + hr_branch_idx) % 10

    pillars = []
    elem_counts = {"Wood": 0.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0}
    polarity_counts = {"Yang": 0, "Yin": 0}

    pillar_defs = [
        ("Year Pillar (Ancestors, Outer Social Mask & Early Youth)", y_stem_idx, y_branch_idx, 1.0),
        ("Month Pillar (Parents, Career Environment & Young Adulthood)", m_stem_idx, m_branch_idx, 1.5),
        ("Day Pillar / Day Master (Core Self, Body & Marriage Partner)", d_stem_idx, d_branch_idx, 2.0),
        ("Hour Pillar (Children, Ambition, Inner Legacy & Later Life)", hr_stem_idx, hr_branch_idx, 1.0),
    ]

    for p_name, s_i, b_i, weight in pillar_defs:
        s_name, s_pol, s_el = HEAVENLY_STEMS[s_i]
        b_name, b_anim, b_el, b_pol = EARTHLY_BRANCHES[b_i]
        elem_counts[s_el] += weight
        elem_counts[b_el] += weight
        polarity_counts[s_pol] += 1
        polarity_counts[b_pol] += 1
        pillars.append({
            "pillar": p_name,
            "heavenly_stem": f"{s_name} ({s_pol} {s_el})",
            "earthly_branch": f"{b_name} — {b_anim} ({b_pol} {b_el})",
            "animal": b_anim,
            "stem_element": s_el,
            "branch_element": b_el,
        })

    total_w = sum(elem_counts.values()) or 1.0
    elem_pct = {k: round((v / total_w) * 100.0, 1) for k, v in elem_counts.items()}
    dominant_el = max(elem_pct, key=elem_pct.get)
    deficient_el = min(elem_pct, key=elem_pct.get)

    day_master_stem, day_master_pol, day_master_el = HEAVENLY_STEMS[d_stem_idx]

    return {
        "tradition_name": "Chinese Astrology (BaZi Four Pillars of Destiny & 12 Animals)",
        "methodology_explained": (
            "Chinese astrology unites the 12 Animal Signs (Sheng Xiao) with the Four Pillars of Destiny (BaZi), "
            "mapping the Heavenly Stems (Tian Gan) and Earthly Branches (Di Zhi) of your Birth Year, Month, Day (Day Master), "
            "and Birth Hour across the Five Elements (Wood, Fire, Earth, Metal, Water) and Yin/Yang polarity."
        ),
        "year_animal_profile": base_ch,
        "day_master_core_identity": f"{day_master_stem} ({day_master_pol} {day_master_el})",
        "four_pillars_of_destiny_bazi": pillars,
        "five_elements_wu_xing_percentages": elem_pct,
        "dominant_element": dominant_el,
        "deficient_or_needed_balancing_element_yong_shen": deficient_el,
        "yin_yang_balance": {
            "yang_percent": round((polarity_counts["Yang"] / 8.0) * 100.0, 1),
            "yin_percent": round((polarity_counts["Yin"] / 8.0) * 100.0, 1),
        },
    }


# ---------------------------------------------------------------------------
# 8. MAYAN ASTROLOGY ENGINE (260-DAY TZOLK'IN & MAYAN TREE-OF-LIFE CROSS)
# ---------------------------------------------------------------------------
def compute_mayan_system(dob: Date) -> Dict[str, Any]:
    """Computes Sacred 260-Day Mayan Tzolk'in astrology + 5-Point Mayan Cross."""
    base_m = ESO.mayan(dob)
    from datetime import timedelta
    past_m = ESO.mayan(dob - timedelta(days=8))
    future_m = ESO.mayan(dob + timedelta(days=8))
    left_m = ESO.mayan(dob - timedelta(days=6))
    right_m = ESO.mayan(dob + timedelta(days=6))

    return {
        "tradition_name": "Mayan Astrology (Sacred 260-Day Tzolk'in & Mayan Cross)",
        "methodology_explained": (
            "The Mayan Sacred Calendar (Tzolk'in) interweaves 20 Solar Day Signs (Nawales) with 13 Galactic Numbers (Tones) "
            "to create a 260-day spiritual matrix. The Mayan Cross places your birth Nawal at the center, flanked by your "
            "Conception sign (-8 days), Destiny maturity sign (+8 days), Spiritual left-hand helper (-6 days), and Material right-hand helper (+6 days)."
        ),
        "core_galactic_signature": base_m,
        "mayan_tree_of_life_cross": {
            "center_core_destiny_nawal": f"{base_m['tone']} {base_m['day_sign']} ({base_m['meaning']})",
            "top_conception_and_youth_sign": f"{past_m['tone']} {past_m['day_sign']} ({past_m['meaning']})",
            "bottom_future_and_elder_fulfilled_sign": f"{future_m['tone']} {future_m['day_sign']} ({future_m['meaning']})",
            "left_feminine_spiritual_ally": f"{left_m['tone']} {left_m['day_sign']} ({left_m['meaning']})",
            "right_masculine_practical_ally": f"{right_m['tone']} {right_m['day_sign']} ({right_m['meaning']})",
        },
    }


# ---------------------------------------------------------------------------
# 9. CELTIC (DRUIDIC) TREE ASTROLOGY ENGINE (13-MOON OGHAM CALENDAR)
# ---------------------------------------------------------------------------
CELTIC_TREES = [
    ((12, 24), (1, 20), "Birch (Beith — The Achiever)", "ᚁ (Beith)", "Sun", "White Stag & Golden Eagle", "Rock Crystal", "Renewal, pioneering ambition, purity of purpose, and resilient new beginnings after winter darkness."),
    ((1, 21), (2, 17), "Rowan (Luis — The Thinker & Visionary)", "ᚂ (Luis)", "Uranus / Mercury", "Green Dragon & Crane", "Peridot / Tourmaline", "Philosophical originality, protective spiritual vision, and ability to transform setbacks into wisdom."),
    ((2, 18), (3, 17), "Ash (Nion — The Enchanter & World Tree)", "ᚃ (Nion)", "Neptune / Jupiter", "Seahorse & Adder", "Coral / Aquamarine", "Imaginative depth, poetic intuition, bridge between inner mystic worlds and practical reality."),
    ((3, 18), (4, 14), "Alder (Fearn — The Trailblazer)", "ᚄ (Fearn)", "Mars", "Fox, Hawk & Raven", "Ruby / Garnet", "Courageous pathfinder, noble confidence, warrior spirit, and unshakeable loyalty to family and allies."),
    ((4, 15), (5, 12), "Willow (Saille — The Intuitive Observer)", "ᚅ (Saille)", "Moon", "Hare & Sea Serpent", "Moonstone / Pearl", "Deep lunar cyclic wisdom, emotional empathy, healing memory, and quiet tenacity that bends without breaking."),
    ((5, 13), (6, 9), "Hawthorn (Huath — The Illusionist & Harmonizer)", "ᚆ (Huath)", "Vulcan / Venus", "Bee & Owl", "Topaz / Carnelian", "Creative versatility, magnetic wit, ability to hold paradoxes, and keen insight into human psychology."),
    ((6, 10), (7, 7), "Oak (Duir — The Stabilizer & Sovereign King)", "ᚇ (Duir)", "Jupiter / Sun", "Wren, Otter & White Horse", "Diamond / Amber", "Royal generosity, protective shelter for others, unshakeable optimism, and enduring moral strength."),
    ((7, 8), (8, 4), "Holly (Tinne — The Ruler & Strategist)", "ᚈ (Tinne)", "Mars / Saturn", "Unicorn & Boar", "Carnelian / Bloodstone", "High-minded noble leadership, competitive excellence, strategic patience, and steadfast devotion."),
    ((8, 5), (9, 1), "Hazel (Coll — The Knower & Scholar)", "ᚉ (Coll)", "Mercury", "Salmon of Wisdom & Crane", "Amethyst / Amber", "concentrated analytical brilliance, encyclopedic memory, poetic eloquence, and mastery of sacred arts."),
    ((9, 2), (9, 29), "Vine (Muin — The Equalizer & Connoisseur)", "ᚊ (Muin)", "Venus", "White Swan & Lizard", "Emerald", "Refined aesthetic sensitivity, diplomatic balance, capacity to see both sides of every truth, and autumn harvest abundance."),
    ((9, 30), (10, 27), "Ivy (Gort — The Survivor & Soul Guide)", "ᚌ (Gort)", "Pluto / Moon", "Boar & Butterfly", "Opal", "Phenomenal spiritual endurance, compassionate loyalty, and ability to climb toward light through any obstacle."),
    ((10, 28), (11, 24), "Reed (Ngetal — The Inquisitor & Truth-Seeker)", "ᚍ (Ngetal)", "Pluto / Mars", "Hound & Owl", "Jasper", "Fearless detective of hidden truth, magnetic storytelling, and deep ancestral sovereignty."),
    ((11, 25), (12, 23), "Elder (Ruis — The Seeker & Philosopher)", "ᚏ (Ruis)", "Saturn / Jupiter", "Black Horse & Badger", "Lapis Lazuli / Jet", "Freedom-loving philosophical depth, regeneration, completion of karmic cycles, and wise counsel."),
]


def compute_celtic_tree_system(dob: Date) -> Dict[str, Any]:
    """Maps a birth date to the 13-Lunar-Month Celtic (Druidic) Ogham Tree Calendar."""
    md = (dob.month, dob.day)
    picked = CELTIC_TREES[0]
    for start_md, end_md, tree_name, ogham, planet, animal, gem, meaning in CELTIC_TREES:
        if start_md[0] == 12:
            if md >= start_md or md <= end_md:
                picked = (start_md, end_md, tree_name, ogham, planet, animal, gem, meaning)
                break
        elif start_md <= md <= end_md:
            picked = (start_md, end_md, tree_name, ogham, planet, animal, gem, meaning)
            break

    _, _, tree_name, ogham, planet, animal, gem, meaning = picked
    return {
        "tradition_name": "Celtic (Druidic) 13-Moon Ogham Tree Astrology",
        "methodology_explained": (
            "Rooted in the ancient Irish/Celtic Ogham tree alphabet ('Beth-Luis-Nion') and seasonal lunar cycles, "
            "Druidic Tree Astrology divides the solar year into 13 lunar-month archetypes, each governed by a sacred tree, "
            "Ogham stave symbol, animal guide, and seasonal earth medicine."
        ),
        "celtic_tree_sign": tree_name,
        "ogham_letter_and_stave": ogham,
        "planetary_correspondence": planet,
        "sacred_animal_guides": animal,
        "druidic_gemstone": gem,
        "archetypal_personality_and_gift": meaning,
    }


# ---------------------------------------------------------------------------
# 10. HOLISTIC AYURVEDIC TRIDOSHA (VATA, PITTA, KAPHA) × CHINESE FIVE ELEMENTS ENGINE
# ---------------------------------------------------------------------------
PLANET_DOSHA_MAP: Dict[str, Dict[str, float]] = {
    "Sun":     {"Vata": 0.0, "Pitta": 1.0, "Kapha": 0.0},
    "Moon":    {"Vata": 0.2, "Pitta": 0.0, "Kapha": 0.8},
    "Mars":    {"Vata": 0.0, "Pitta": 1.0, "Kapha": 0.0},
    "Mercury": {"Vata": 0.5, "Pitta": 0.25, "Kapha": 0.25},
    "Jupiter": {"Vata": 0.0, "Pitta": 0.1, "Kapha": 0.9},
    "Venus":   {"Vata": 0.3, "Pitta": 0.0, "Kapha": 0.7},
    "Saturn":  {"Vata": 1.0, "Pitta": 0.0, "Kapha": 0.0},
    "Rahu":    {"Vata": 0.9, "Pitta": 0.1, "Kapha": 0.0},
    "Ketu":    {"Vata": 0.2, "Pitta": 0.8, "Kapha": 0.0},
}

SIGN_DOSHA_MAP: Dict[int, Dict[str, float]] = {
    0:  {"Vata": 0.1, "Pitta": 0.9, "Kapha": 0.0},  # Aries (Fire)
    1:  {"Vata": 0.2, "Pitta": 0.0, "Kapha": 0.8},  # Taurus (Earth)
    2:  {"Vata": 0.8, "Pitta": 0.1, "Kapha": 0.1},  # Gemini (Air)
    3:  {"Vata": 0.1, "Pitta": 0.0, "Kapha": 0.9},  # Cancer (Water)
    4:  {"Vata": 0.0, "Pitta": 0.95, "Kapha": 0.05},# Leo (Fire)
    5:  {"Vata": 0.75, "Pitta": 0.1, "Kapha": 0.15},# Virgo (Earth/Vata)
    6:  {"Vata": 0.8, "Pitta": 0.1, "Kapha": 0.1},  # Libra (Air)
    7:  {"Vata": 0.0, "Pitta": 0.65, "Kapha": 0.35},# Scorpio (Water/Mars)
    8:  {"Vata": 0.1, "Pitta": 0.75, "Kapha": 0.15},# Sagittarius (Fire/Jupiter)
    9:  {"Vata": 0.7, "Pitta": 0.0, "Kapha": 0.3},  # Capricorn (Earth/Saturn)
    10: {"Vata": 0.85, "Pitta": 0.1, "Kapha": 0.05},# Aquarius (Air/Saturn)
    11: {"Vata": 0.0, "Pitta": 0.1, "Kapha": 0.9},  # Pisces (Water/Jupiter)
}

DOSHA_BALANCING_GUIDES: Dict[str, Dict[str, Any]] = {
    "Vata": {
        "elements": "Vayu (Air) + Akasha (Ether)",
        "sanskrit_elements": "Vayu (Air) + Akasha (Ether) — Kinetic & Nervous Energy",
        "qualities": "Dry (Ruksha), Light (Laghu), Cold (Sheeta), Subtle (Sukshma), Mobile (Chala), Clear (Vishada)",
        "ruling_planets": "Saturn, Rahu & Mercury (Air signs Gemini, Libra, Aquarius & Capricorn/Virgo)",
        "when_in_balance": "Quick comprehension, creative enthusiasm, agile body, clear intuition, joyful adaptability.",
        "when_balanced": "Quick comprehension, creative enthusiasm, agile body, clear intuition, joyful adaptability.",
        "when_in_excess": "Anxiety, racing thoughts, insomnia, dry skin, bloating/gas, cracking joints, irregular appetite, cold hands/feet.",
        "when_imbalanced": "Anxiety, racing thoughts, insomnia, dry skin, bloating/gas, cracking joints, irregular appetite, cold hands/feet.",
        "tastes_to_favor": "Sweet (Madhura — whole grains, dates, ghee, milk), Sour (Amla — lemon, fermented warm foods), Salty (Lavana — mineral/rock salt).",
        "tastes_to_reduce": "Bitter, Pungent (excess raw chili), and Astringent (cold dry salads, raw beans, iced drinks, excess caffeine).",
        "foods_to_favor": "Warm, freshly cooked, unctuous meals with pure cow ghee, sesame oil, soups, stews, kitchari, basmati rice, cooked root vegetables, soaked almonds, and warm spiced milk.",
        "foods_to_reduce": "Cold raw salads, dry crackers, iced beverages, excess caffeine, unripe fruits, and skipping meals or eating late at night.",
        "herbs_and_oils": "Ashwagandha, Brahmi, Shatavari, Dashamoola, Triphala with warm water, Ginger-Cardamom-Cinnamon tea, and daily warm Sesame Oil (Tila Taila) Abhyanga.",
        "pranayama_and_lifestyle": "Daily warm sesame oil self-massage (Abhyanga), sleep by 10:00 PM, regular meal times, Nadi Shodhana (Alternate Nostril Breathing) & Bhramari (10 mins daily).",
        "diet_and_foods": [
            "Eat warm, freshly cooked, lightly spiced, unctuous meals with pure cow ghee, sesame oil, soups, stews, kitchari, basmati rice, cooked root vegetables, soaked almonds, and warm spiced milk.",
            "Avoid skipping meals, eating late at night, cold raw salads in winter, dry crackers, and iced beverages.",
        ],
        "herbs_and_rasayanas": ["Ashwagandha (Withania somnifera — grounds nervous system)", "Brahmi / Gotu Kola (calms racing mind)", "Shatavari (nourishes tissues)", "Dashamoola & Triphala with warm water at bedtime", "Ginger, Cardamom, Cinnamon & Fennel tea"],
        "dinacharya_daily_routine": [
            "Perform daily warm sesame oil self-massage (Abhyanga) before showering — the #1 classical remedy for Vata.",
            "Maintain consistent sleep (by 10:00 PM) and meal times to anchor Saturn/Rahu rhythms.",
            "Practice Nadi Shodhana (Alternate Nostril Breathing) and Bhramari (Humming Bee Breath) for 10 minutes daily.",
        ],
        "vastu_and_home_alignment": "Sleep with your head toward the South (Earth grounding); keep the North-West (Vayu/Air zone) calm and uncluttered; use warm earthy ochre, cream, and soft gold tones.",
    },
    "Pitta": {
        "elements": "Agni (Fire) + Jala (Water)",
        "sanskrit_elements": "Agni (Fire) + Jala (Water) — Metabolic, Enzymatic & Intellectual Energy",
        "qualities": "Hot (Ushna), Sharp/Penetrating (Tikshna), Light (Laghu), Liquid (Drava), Slightly Oily (Sasneha)",
        "ruling_planets": "Sun, Mars & Ketu (Fire signs Aries, Leo, Sagittarius & Scorpio)",
        "when_in_balance": "Sharp intellect, decisive leadership, strong digestion (Jatharagni), radiant complexion, warm courage.",
        "when_balanced": "Sharp intellect, decisive leadership, strong digestion (Jatharagni), radiant complexion, warm courage.",
        "when_in_excess": "Acid reflux/heartburn, irritability, impatience, skin inflammation/rashes, burning eyes, premature greying, perfectionism.",
        "when_imbalanced": "Acid reflux/heartburn, irritability, impatience, skin inflammation/rashes, burning eyes, premature greying, perfectionism.",
        "tastes_to_favor": "Sweet (cooling grains, coconut, sweet fruits), Bitter (leafy greens, turmeric, aloe), Astringent (pomegranate, mung beans, cucumber).",
        "tastes_to_reduce": "Pungent (hot chili, cayenne, raw garlic/onion), Sour (vinegar, aged cheese, alcohol), and Excess Salty/Fried foods.",
        "foods_to_favor": "Cooling, hydrating foods: coconut water, sweet melons, pomegranates, basmati rice, green mung dal, cucumber, cilantro, mint, fennel, and pure cow ghee.",
        "foods_to_reduce": "Deep-fried foods, heavy red meat, fiery chilies, raw garlic/onions, fermented alcohol, sour vinegar, and skipping midday lunch.",
        "herbs_and_oils": "Amalaki (Amla), Shatavari, Guduchi (Giloy), Aloe Vera, Coriander-Fennel-Rose cooling infusion, and cooling Coconut Oil or Sandalwood/Brahmi oil.",
        "pranayama_and_lifestyle": "Sheetali / Sheetkari (Cooling Breath), Chandra Bhedana (Left-Nostril Lunar Breathing), evening moonlight/garden walks, and avoiding midday heat.",
        "diet_and_foods": [
            "Favor cooling, hydrating foods: coconut water, sweet melons, pomegranates, basmati rice, green mung dal, cucumber, cilantro, mint, fennel, and pure cow ghee.",
            "Avoid deep-fried foods, heavy red meat, fiery chilies, fermented alcohol, and skipping lunch when the Sun is at peak (12:00 PM – 1:00 PM).",
        ],
        "herbs_and_rasayanas": ["Amalaki (Indian Gooseberry — cools Pitta & rejuvenates blood/eyes)", "Shatavari", "Guduchi (Giloy)", "Aloe Vera juice", "Coriander, Fennel & Rose petal cooling infusion", "Brahmi in coconut oil"],
        "dinacharya_daily_routine": [
            "Practice Sheetali or Sheetkari (Cooling Breath) and Chandra Bhedana (Left-Nostril Lunar Breathing).",
            "Take evening walks under moonlight or near water/gardens; avoid overheating in midday sun.",
            "Apply cooling coconut oil or sandalwood/rose water before bath.",
        ],
        "vastu_and_home_alignment": "Ensure your bedroom is NOT in the South-East (Agni/Fire corner); keep the North-East (Water/Ishanya zone) serene and cool; use soothing pastel blues, greens, and pearl white.",
    },
    "Kapha": {
        "elements": "Prithvi (Earth) + Jala (Water)",
        "sanskrit_elements": "Prithvi (Earth) + Jala (Water) — Structural, Immune & Lubricating Energy",
        "qualities": "Heavy (Guru), Slow/Steady (Manda), Cool (Sheeta), Oily/Unctuous (Snigdha), Smooth (Slakshna), Dense/Stable (Sthira)",
        "ruling_planets": "Jupiter, Moon & Venus (Water & Earth signs Cancer, Pisces, Taurus)",
        "when_in_balance": "Immense stamina, calm emotional stability, strong immunity (Ojas), compassionate loyalty, deep restful sleep.",
        "when_balanced": "Immense stamina, calm emotional stability, strong immunity (Ojas), compassionate loyalty, deep restful sleep.",
        "when_in_excess": "Lethargy, slow metabolism, weight gain, sinus/chest congestion, water retention, oversleeping, resistance to change.",
        "when_imbalanced": "Lethargy, slow metabolism, weight gain, sinus/chest congestion, water retention, oversleeping, resistance to change.",
        "tastes_to_favor": "Pungent (ginger, black pepper, turmeric, cinnamon), Bitter (fenugreek, leafy greens), Astringent (legumes, apples, berries, warm herbal teas).",
        "tastes_to_reduce": "Sweet (refined sugar, heavy dairy, wheat pastries), Salty (excess sodium), and Sour (heavy creamy/cheesy foods).",
        "foods_to_favor": "Light, warm, dry, spiced meals: barley, millet, quinoa, steamed greens, spiced lentil soups, warm water with raw honey & lemon, ginger, and black pepper.",
        "foods_to_reduce": "Cold dairy, ice cream, heavy fried sweets, refined sugar/wheat pastries, daytime naps after meals, and overeating at dinner.",
        "herbs_and_oils": "Trikatu (Ginger, Black Pepper, Pippali), Triphala, Punarnava, Tulsi-Ginger-Turmeric tea, and dry brushing (Garshana) with warm Mustard/Sesame oil.",
        "pranayama_and_lifestyle": "Wake before Sunrise (Brahma Muhurta ~05:30 AM), vigorous daily exercise, Surya Namaskar, and energizing Kapalabhati / Bhastrika Pranayama.",
        "diet_and_foods": [
            "Favor light, warm, dry, and spiced meals: barley, millet, quinoa, steamed greens, spiced lentil soups, warm water with raw honey and lemon, ginger, and black pepper.",
            "Avoid cold dairy, ice cream, heavy fried sweets, daytime naps after meals, and overeating at dinner.",
        ],
        "herbs_and_rasayanas": ["Trikatu (Ginger, Black Pepper, Long Pepper — kindles digestive Agni)", "Triphala", "Punarnava (clears fluid retention)", "Tulsi (Holy Basil) & Ginger tea", "Turmeric & Cinnamon"],
        "dinacharya_daily_routine": [
            "Wake up before Sunrise (Brahma Muhurta ~05:30 AM) — sleeping past sunrise increases Kapha sluggishness.",
            "Engage in vigorous daily exercise, Surya Namaskar (Sun Salutations), and Kapalabhati / Bhastrika Pranayama.",
            "Use dry brushing (Garshana) or warm mustard/sesame oil massage.",
        ],
        "vastu_and_home_alignment": "Let bright morning sunlight flood the East and North windows; declutter heavy storage in the North-East and East; use energizing warm coral, gold, and bright citrus accents.",
    },
}

CHINESE_ELEMENT_BALANCING_GUIDES: Dict[str, Dict[str, Any]] = {
    "Wood": {
        "organ_meridian": "Liver (Yin) & Gallbladder (Yang) — Governs Tendons, Eyes, Planning & Vision",
        "ayurvedic_bridge": "Bridges Pitta-Vata (upward-rising growth force, wind/movement + metabolic heat)",
        "when_balanced": "Visionary leadership, benevolence, flexibility, smooth emotional flow.",
        "when_imbalanced": "Frustration, tight neck/shoulders, eye strain, headaches, rigid impatience.",
        "how_to_balance": "Spend time among tall green trees (East sector), eat fresh leafy greens and sprouts, practice gentle stretching/Tai Chi/Yoga twists, and nurture your Controlling/Generating elements (Water nourishes Wood; Fire channels excess Wood into joy).",
    },
    "Fire": {
        "organ_meridian": "Heart (Yin), Small Intestine (Yang), Pericardium & Triple Burner — Governs Blood Vessels, Tongue, Joy & Spirit (Shen)",
        "ayurvedic_bridge": "Directly parallels Ayurvedic Pitta Dosha (Sadhaka & Ranjaka Pitta)",
        "when_balanced": "Radiant warmth, charisma, clear speech, joyful enthusiasm, peaceful sleep.",
        "when_imbalanced": "Restless mind (agitated Shen), palpitations, burnout, impulsiveness, heat sensations.",
        "how_to_balance": "Balance with cooling Water (quiet reflection, hydration) and grounding Earth (mindful meals, nature walks); favor bitter greens and red berries; keep the South sector of your home uncluttered.",
    },
    "Earth": {
        "organ_meridian": "Spleen/Pancreas (Yin) & Stomach (Yang) — Governs Muscles, Digestion, Empathy & Grounded Thought",
        "ayurvedic_bridge": "Directly parallels Ayurvedic Kapha Dosha & Kledaka Kapha / Samana Vata digestion",
        "when_balanced": "Deep stability, nurturing reliability, strong digestion, centered focus.",
        "when_imbalanced": "Overthinking/worry, sluggish digestion, dampness/heaviness, feeling stuck.",
        "how_to_balance": "Eat warm cooked root vegetables (sweet potato, pumpkin, ginger, millet), avoid cold damp foods, walk barefoot on grass/earth, and activate Metal (breathwork, decluttering) to move stagnant Earth.",
    },
    "Metal": {
        "organ_meridian": "Lungs (Yin) & Large Intestine (Yang) — Governs Respiration, Skin, Boundaries, Order & Letting Go",
        "ayurvedic_bridge": "Bridges Prana Vata & Udana Vata (respiratory vitality, skin lustre, and cellular release)",
        "when_balanced": "Integrity, crisp organization, strong immunity, ability to let go of the past.",
        "when_imbalanced": "Grief/melancholy, respiratory or skin sensitivity, overly rigid perfectionism.",
        "how_to_balance": "Practice deep rhythmic Pranayama breathwork at dawn, eat white/pungent nourishing foods (pear, radish, ginger, lotus root, oats), and keep the West and North-West sectors of your home bright and airy.",
    },
    "Water": {
        "organ_meridian": "Kidneys (Yin) & Urinary Bladder (Yang) — Governs Bones, Marrow, Brain, Ears, Willpower (Zhi) & Longevity Essence (Jing)",
        "ayurvedic_bridge": "Parallels Ayurvedic Ojas, Tarpaka Kapha & Apana Vata (reproductive & foundational vitality)",
        "when_balanced": "Deep wisdom, calm resilience, strong bones/lower back, enduring willpower.",
        "when_imbalanced": "Fear/timidity, adrenal exhaustion, lower back/knee weakness, cold extremities.",
        "how_to_balance": "Protect Kidney Jing with restorative sleep, black sesame seeds, walnuts, dark berries, bone/mineral broths, and warm foot baths; harmonize the North sector of your home.",
    },
}


def compute_dosha_and_element_balance(
    pos: Dict[str, Any],
    asc_lon: float,
    birth_dt_local: datetime,
    jd: float,
) -> Dict[str, Any]:
    """Computes the native's exact Ayurvedic Tridosha (Vata, Pitta, Kapha) from their
    Vedic birth chart (Prakriti) + current Vimshottari Dasha (Vikriti), AND their
    Chinese Five Elements (Wood, Fire, Earth, Metal, Water) from their Four Pillars,
    synthesizing a complete holistic balancing protocol."""
    lagna_idx = int(asc_lon // 30) % 12
    lagna_lord = SIGN_LORDS[lagna_idx]
    moon_idx = int(pos["Moon"]["longitude"] // 30) % 12
    sun_idx = int(pos["Sun"]["longitude"] // 30) % 12

    scores = {"Vata": 0.0, "Pitta": 0.0, "Kapha": 0.0}
    factors = []

    def _add_dosha(label: str, d_map: Dict[str, float], weight: float):
        for k in ("Vata", "Pitta", "Kapha"):
            scores[k] += d_map[k] * weight
        dom = max(d_map, key=d_map.get)
        factors.append({"chart_factor": label, "dominant_dosha": dom, "weight": weight})

    # 1. Lagna Sign (30%)
    _add_dosha(f"Ascendant (Lagna) Sign: {SIGNS[lagna_idx]}", SIGN_DOSHA_MAP[lagna_idx], 3.0)
    # 2. Lagna Lord Planet & its Sign (20%)
    ll_sign = int(pos[lagna_lord]["longitude"] // 30) % 12
    _add_dosha(f"Lagna Lord ({lagna_lord} in {SIGNS[ll_sign]})", PLANET_DOSHA_MAP[lagna_lord], 1.3)
    _add_dosha(f"Lagna Lord Sign ({SIGNS[ll_sign]})", SIGN_DOSHA_MAP[ll_sign], 0.7)
    # 3. Moon & Moon Sign (20%)
    _add_dosha(f"Moon Sign (Chandra Rashi): {SIGNS[moon_idx]}", SIGN_DOSHA_MAP[moon_idx], 1.4)
    _add_dosha("Moon (Manas/Fluids)", PLANET_DOSHA_MAP["Moon"], 0.6)
    # 4. Sun & Sun Sign (15%)
    _add_dosha(f"Sun Sign (Atma/Agni): {SIGNS[sun_idx]}", SIGN_DOSHA_MAP[sun_idx], 0.9)
    _add_dosha("Sun (Digestive & Vital Fire)", PLANET_DOSHA_MAP["Sun"], 0.6)
    # 5. Planets in 1st House (Body) & 6th House (Health) (15%)
    for p in VEDIC_PLANETS:
        p_s = int(pos[p]["longitude"] // 30) % 12
        h = (p_s - lagna_idx) % 12 + 1
        if h == 1:
            _add_dosha(f"{p} occupying 1st House (Physical Body)", PLANET_DOSHA_MAP[p], 1.2)
        elif h == 6:
            _add_dosha(f"{p} occupying 6th House (Metabolic/Health Axis)", PLANET_DOSHA_MAP[p], 0.8)

    total_d = sum(scores.values()) or 1.0
    dosha_pct = {k: round((v / total_d) * 100.0, 1) for k, v in scores.items()}
    ordered_doshas = sorted(dosha_pct.keys(), key=lambda k: dosha_pct[k], reverse=True)
    primary_dosha, secondary_dosha = ordered_doshas[0], ordered_doshas[1]
    if dosha_pct[primary_dosha] - dosha_pct[secondary_dosha] <= 12.0:
        prakriti_type = f"{primary_dosha}-{secondary_dosha} Dual Constitution (Dwandwaja Prakriti)"
    else:
        prakriti_type = f"{primary_dosha}-Dominant Constitution ({primary_dosha} Prakriti)"

    # Current Dasha Vikriti (Dynamic seasonal/period shift)
    now_jd = ephem.jd_from_utc(datetime.now(timezone.utc))
    cur_d = DExt.get_current_dasha(pos["Moon"]["longitude"], jd, now_jd, timezone.utc)
    cur_md = cur_d.get("mahadasha", {}).get("lord", lagna_lord)
    cur_ad = cur_d.get("antardasha", {}).get("lord", lagna_lord)
    md_dosha = max(PLANET_DOSHA_MAP.get(cur_md, PLANET_DOSHA_MAP["Sun"]), key=PLANET_DOSHA_MAP.get(cur_md, PLANET_DOSHA_MAP["Sun"]).get)
    ad_dosha = max(PLANET_DOSHA_MAP.get(cur_ad, PLANET_DOSHA_MAP["Moon"]), key=PLANET_DOSHA_MAP.get(cur_ad, PLANET_DOSHA_MAP["Moon"]).get)

    # Chinese Five Elements from BaZi
    bazi = compute_chinese_bazi_system(birth_dt_local, jd)
    elem_pct = bazi["five_elements_wu_xing_percentages"]
    dom_elem = bazi["dominant_element"]
    def_elem = bazi["deficient_or_needed_balancing_element_yong_shen"]

    return {
        "ayurvedic_jyotish_tridosha_profile": {
            "natal_prakriti_type": prakriti_type,
            "dosha_percentages": dosha_pct,
            "primary_dosha_to_pacify": primary_dosha,
            "secondary_dosha": secondary_dosha,
            "current_dasha_vikriti": {
                "active_mahadasha": cur_md,
                "active_antardasha": cur_ad,
                "active_dasha_dosha_push": f"{cur_md} ({md_dosha}) / {cur_ad} ({ad_dosha})",
                "explanation": (
                    f"While your lifelong birth constitution (Prakriti) is {prakriti_type}, your current running planetary period "
                    f"({cur_md} Mahadasha – {cur_ad} Antardasha) elevates {md_dosha} and {ad_dosha} energy (Vikriti). "
                    f"Pay extra attention to balancing {primary_dosha} and {md_dosha} in your daily diet and routine right now."
                ),
            },
            "chart_contributors": factors,
            "primary_dosha_balancing_protocol": DOSHA_BALANCING_GUIDES[primary_dosha],
            "secondary_dosha_balancing_protocol": DOSHA_BALANCING_GUIDES[secondary_dosha],
            "all_three_dosha_reference": DOSHA_BALANCING_GUIDES,
        },
        "chinese_five_elements_wu_xing_profile": {
            "day_master": bazi["day_master_core_identity"],
            "element_percentages": elem_pct,
            "dominant_excess_element": dom_elem,
            "deficient_element_to_strengthen": def_elem,
            "yin_yang_balance": bazi["yin_yang_balance"],
            "dominant_element_guide": CHINESE_ELEMENT_BALANCING_GUIDES[dom_elem],
            "deficient_element_guide": CHINESE_ELEMENT_BALANCING_GUIDES[def_elem],
            "all_five_elements_reference": CHINESE_ELEMENT_BALANCING_GUIDES,
        },
        "east_meets_east_unified_synthesis": {
            "headline": f"Unified {primary_dosha}-{secondary_dosha} (Ayurveda) + {dom_elem}/{def_elem} (Chinese Wu Xing) Master Plan",
            "core_connection": (
                f"Your Vedic chart shows a {prakriti_type} ({dosha_pct['Vata']}% Vata, {dosha_pct['Pitta']}% Pitta, {dosha_pct['Kapha']}% Kapha), "
                f"while your Chinese Four Pillars show abundant {dom_elem} ({elem_pct[dom_elem]}%) and a need to nourish {def_elem} ({elem_pct[def_elem]}%). "
                f"By calming excess {primary_dosha} ({DOSHA_BALANCING_GUIDES[primary_dosha]['tastes_to_favor']}) while strengthening your Chinese {def_elem} meridian "
                f"({CHINESE_ELEMENT_BALANCING_GUIDES[def_elem]['organ_meridian']}), both your Vedic planetary houses and your Chinese Five Elements come into complete bio-energetic harmony."
            ),
        },
    }


# ---------------------------------------------------------------------------
# 11. MASTER MULTI-TRADITION REPORT GENERATOR WITH FILTERING
# ---------------------------------------------------------------------------
def generate_multi_tradition_report(
    birth_dt_utc: datetime,
    birth_dt_local: datetime,
    lat: float,
    lon: float,
    tz_name: str = "Asia/Kolkata",
    name: str = "Seeker",
    gender: str = "male",
    focus_mode: str = "all",
    school_preference: str = "all",
    selected_traditions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Computes and filters the complete Multi-Tradition Astrology, Vastu, Feng Shui,
    Ayurvedic Tridosha (Vata/Pitta/Kapha) & Chinese Five Elements Dossier."""
    jd = ephem.jd_from_utc(birth_dt_utc)
    pos = ephem.all_positions(jd, sidereal=True)
    _, asc_lon, mc_lon = ephem.houses(jd, lat, lon, "W", sidereal=True)
    lagna_idx = int(asc_lon // 30) % 12
    moon_idx = int(pos["Moon"]["longitude"] // 30) % 12

    # Determine which traditions are active based on filters
    all_ids = [t["id"] for t in TRADITIONS_CATALOG]
    if selected_traditions:
        # Normalize aliases
        alias_map = {
            "ayurveda_dosha": "holistic_dosha_elements",
            "chinese_elements": "holistic_dosha_elements",
            "dosha": "holistic_dosha_elements",
            "elements": "holistic_dosha_elements",
            "dosha_and_elements": "holistic_dosha_elements",
            "kp_system": "kp",
            "uranian_hamburg": "uranian",
            "chinese": "chinese_bazi",
        }
        norm_sel = set()
        for s in selected_traditions:
            s_low = s.strip().lower()
            norm_sel.add(alias_map.get(s_low, s_low))
        active_ids = [tid for tid in all_ids if tid in norm_sel]
        if not active_ids:
            active_ids = all_ids
    else:
        active_ids = []
        for t in TRADITIONS_CATALOG:
            if school_preference != "all" and t["school"] != school_preference:
                # Always include holistic_dosha_elements if eastern_vedic or global_cultural or holistic_balance
                if not (t["id"] == "holistic_dosha_elements" and school_preference in ("holistic_balance", "eastern_vedic", "global_cultural")):
                    continue
            if focus_mode != "all" and focus_mode not in t["focus_tags"]:
                continue
            active_ids.append(t["id"])
        if not active_ids:
            active_ids = all_ids

    sections: Dict[str, Any] = {}

    if "lal_kitab" in active_ids:
        sections["lal_kitab"] = compute_lal_kitab_system(pos, asc_lon)

    if "parashari" in active_ids:
        from .destiny_engine import classify_functional_planets
        roles = classify_functional_planets(lagna_idx)
        now_jd = ephem.jd_from_utc(datetime.now(timezone.utc))
        cur_dasha_info = DExt.get_current_dasha(pos["Moon"]["longitude"], jd, now_jd, timezone.utc)
        nak_idx = int(pos["Moon"]["longitude"] / (360.0 / 27.0)) % 27
        pada = int((pos["Moon"]["longitude"] % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
        d9_planets = {}
        for p in VEDIC_PLANETS:
            nav_s = int(pos[p]["longitude"] / (30.0 / 9.0)) % 12
            d9_planets[p] = f"{SIGNS[nav_s]} ({RASHIS[nav_s]})"
        sections["parashari"] = {
            "tradition_name": "Parashari Astrology (Brihat Parashara Hora Shastra)",
            "methodology_explained": (
                "The classical mainstream system of Vedic Jyotish taught by Maharishi Parashara. It uses the Sidereal (Nirayana) "
                "zodiac anchored to fixed stars (Lahiri Chitrapaksha), 27 Nakshatras, 16 Divisional Charts (Shodashavargas), "
                "functional house lordships from the Ascendant, and the 120-year Vimshottari Dasha."
            ),
            "sidereal_ascendant": f"{SIGNS[lagna_idx]} ({RASHIS[lagna_idx]}) — Lord: {SIGN_LORDS[lagna_idx]}",
            "janma_rashi_and_nakshatra": f"{SIGNS[moon_idx]} ({RASHIS[moon_idx]}) · {NAKSHATRAS[nak_idx]} Pada {pada} (Lord: {NAK_LORDS[nak_idx % 9]})",
            "functional_benefics": roles["functional_benefics"],
            "functional_malefics": roles["functional_malefics"],
            "maraka_and_badhaka": {"marakas": roles["maraka_lords"], "badhaka_lord": roles["badhaka_lord"]},
            "navamsha_d9_positions": d9_planets,
            "current_vimshottari_dasha": cur_dasha_info,
        }

    if "jaimini" in active_ids:
        sections["jaimini"] = compute_jaimini_system(pos, asc_lon, birth_dt_utc)

    if "kp" in active_ids:
        kp_data = ADV.kp_chart(birth_dt_utc, lat, lon)
        sections["kp"] = {
            "tradition_name": "Krishnamurti Paddhati (KP Stellar Sub-Lord System)",
            "methodology_explained": (
                "Developed by Prof. K.S. Krishnamurti, KP refines Parashari astrology using Placidus house cusps and dividing each of the "
                "27 Nakshatras into 9 unequal Sub-Lord zones (249 total sub-divisions). A planet gives the results of its Star Lord (Nakshatra Lord), "
                "while the Sub-Lord decides whether the promised event is favorable or denied."
            ),
            "planets_sign_star_sub_lords": kp_data.get("planets", []),
            "cuspal_sub_lords": kp_data.get("cusps", []),
            "ruling_planets": kp_data.get("ruling_planets", {}),
        }

    if "nadi" in active_ids:
        sections["nadi"] = compute_nadi_system(pos, asc_lon)

    if "western_tropical" in active_ids:
        w_chart = W.natal_chart(birth_dt_utc, lat, lon, system="tropical", house_system="placidus")
        sections["western_tropical"] = {
            "tradition_name": "Western Tropical Astrology (Seasonal Equinox Zodiac)",
            "methodology_explained": (
                "Aligns 0° Aries with the Earth's Vernal Equinox rather than background constellations, emphasizing the psychological "
                "interplay of the Tropical Sun (core identity), Moon (emotional responses), Ascendant (persona), outer planets (Uranus, Neptune, Pluto), "
                "and Ptolemaic aspect geometry."
            ),
            "tropical_ascendant": w_chart["ascendant"],
            "tropical_midheaven_mc": w_chart["midheaven"],
            "tropical_planets": w_chart["planets"][:10],
            "elements_and_modalities": w_chart.get("elements", {}),
            "major_aspects": w_chart["aspects"][:12],
        }

    if "hellenistic" in active_ids:
        sections["hellenistic"] = compute_hellenistic_system(jd, birth_dt_utc, lat, lon)

    if "psychological_evolutionary" in active_ids:
        sections["psychological_evolutionary"] = compute_psychological_evolutionary_system(jd, lat, lon)

    if "uranian" in active_ids:
        sections["uranian"] = compute_uranian_hamburg_system(jd, lat, lon)

    if "chinese_bazi" in active_ids:
        sections["chinese_bazi"] = compute_chinese_bazi_system(birth_dt_local, jd)

    if "feng_shui" in active_ids:
        sections["feng_shui"] = compute_classical_feng_shui(
            birth_dt_local.year, birth_dt_local.month, birth_dt_local.day, gender=gender
        )

    if "mayan" in active_ids:
        sections["mayan"] = compute_mayan_system(birth_dt_local.date())

    if "celtic_tree" in active_ids:
        sections["celtic_tree"] = compute_celtic_tree_system(birth_dt_local.date())

    if "holistic_dosha_elements" in active_ids:
        sections["holistic_dosha_elements"] = compute_dosha_and_element_balance(
            pos, asc_lon, birth_dt_local, jd
        )

    if "astro_vastu" in selected_traditions if selected_traditions else True:
        sections["astro_vastu"] = compute_personalized_astro_vastu(pos, asc_lon)

    # Provide convenient alias keys in sections as well
    if "holistic_dosha_elements" in sections:
        hd = sections["holistic_dosha_elements"]
        hd["ayurvedic_tridosha"] = {
            "prakriti_type": hd["ayurvedic_jyotish_tridosha_profile"]["natal_prakriti_type"],
            "natal_prakriti_pct": hd["ayurvedic_jyotish_tridosha_profile"]["dosha_percentages"],
            "dominant_dosha": hd["ayurvedic_jyotish_tridosha_profile"]["primary_dosha_to_pacify"],
            "secondary_dosha": hd["ayurvedic_jyotish_tridosha_profile"]["secondary_dosha"],
            "active_mahadasha": hd["ayurvedic_jyotish_tridosha_profile"]["current_dasha_vikriti"]["active_mahadasha"],
            "active_dasha_dosha_push": hd["ayurvedic_jyotish_tridosha_profile"]["current_dasha_vikriti"]["active_dasha_dosha_push"],
            "vikriti_note": hd["ayurvedic_jyotish_tridosha_profile"]["current_dasha_vikriti"]["explanation"],
        }
        hd["chinese_five_elements"] = {
            "day_master_element": hd["chinese_five_elements_wu_xing_profile"]["day_master"],
            "element_distribution_pct": hd["chinese_five_elements_wu_xing_profile"]["element_percentages"],
            "dominant_element": hd["chinese_five_elements_wu_xing_profile"]["dominant_excess_element"],
            "deficient_element": hd["chinese_five_elements_wu_xing_profile"]["deficient_element_to_strengthen"],
            "yin_yang_balance": hd["chinese_five_elements_wu_xing_profile"]["yin_yang_balance"],
        }
        sections["dosha_and_elements"] = hd
    if "kp" in sections:
        sections["kp_system"] = sections["kp"]
    if "uranian" in sections:
        sections["uranian_hamburg"] = sections["uranian"]
    if "chinese_bazi" in sections:
        sections["chinese"] = sections["chinese_bazi"]

    return {
        "name": name,
        "birth_details": {
            "date": birth_dt_local.date().isoformat(),
            "time_ampm": birth_dt_local.strftime("%I:%M %p"),
            "latitude": lat,
            "longitude": lon,
            "timezone": str(tz_name),
            "gender": gender,
        },
        "applied_filters": {
            "focus_mode": focus_mode,
            "school_preference": school_preference,
            "active_traditions_count": len(active_ids),
            "active_tradition_ids": active_ids,
        },
        "selected_traditions": active_ids,
        "available_traditions_catalog": TRADITIONS_CATALOG,
        "traditions_dossier": sections,
        "traditions": sections,
    }


def get_traditions_catalog() -> Dict[str, Any]:
    """Returns the catalog of all 14 traditions, goals, and schools."""
    return {
        "total_traditions": len(TRADITIONS_CATALOG),
        "traditions": [
            {**t, "name": t["title"]} for t in TRADITIONS_CATALOG
        ],
        "focus_modes": ["all", "personal_insight", "event_prediction", "remedies_and_healing"],
        "school_preferences": ["all", "eastern_vedic", "western", "global_cultural", "holistic_balance"],
    }


def compute_traditions_report(
    birth_dt_utc: datetime,
    lat: float,
    lon: float,
    tz_obj: Any,
    name: str = "Native",
    gender: str = "male",
    selected_traditions: Optional[List[str]] = None,
    goal_filter: str = "all",
    approach_filter: str = "all",
) -> Dict[str, Any]:
    """Wrapper around generate_multi_tradition_report accepting UTC datetime + tzinfo object."""
    birth_dt_local = birth_dt_utc.astimezone(tz_obj)
    return generate_multi_tradition_report(
        birth_dt_utc=birth_dt_utc,
        birth_dt_local=birth_dt_local,
        lat=lat,
        lon=lon,
        tz_name=str(tz_obj),
        name=name,
        gender=gender,
        focus_mode=goal_filter or "all",
        school_preference=approach_filter or "all",
        selected_traditions=selected_traditions,
    )


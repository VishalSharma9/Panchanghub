"""Comprehensive Plain-English Astrological Glossary, Deep Narrative Explainer,
Personalized Birth-Chart Astro-Vastu Engine, and Interactive House + Outer-Lot
Visual Vastu Layout Analyzer.

Covers:
1. Plain-English Dictionary of every Vedic Astrology & Vastu term (Maraka, Badhaka,
   Yogakaraka, Dusthana, Indu Lagna, Upapada, Darakaraka, Atmakaraka, Karakamsha,
   Beeja/Kshetra Sphuta, D-7, D-8, D-9, D-60, Mrityu Bhaga, Chandrashtama, Rinas,
   Brahmasthan, Agneya, Ishanya, Nairutya, Vayavya, etc.).
2. Deep, plain-English explanations attached to every module of the Master Destiny Dossier.
3. Personalized Astro-Vastu synthesis from the native's Birth Chart to double positive effects.
4. Full multi-item Visual House (Square/Rectangle) + Outer Lot/Yard Vastu Layout Evaluator
   supporting indoor rooms (entrance, back_door, master_bedroom, bedroom, guest_room,
   living_room, kitchen, bathroom, storage, balcony, dining_room, puja_room, study_room,
   staircase, safe_locker) and outdoor lot features (fence, gate, parking_gate, trees,
   flowers, bushes, fireplace, garden, grass, water_body, septic_trash).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from . import ephem
from .ephem import SIGNS, RASHIS
from .kundli import SIGN_LORDS, dignity


# ---------------------------------------------------------------------------
# 1. PLAIN-ENGLISH ASTROLOGICAL & VASTU GLOSSARY (EVERY TERM IN SIMPLE WORDS)
# ---------------------------------------------------------------------------
PLAIN_ENGLISH_GLOSSARY: List[Dict[str, str]] = [
    {
        "term": "Lagna (Ascendant / Rising Sign)",
        "simple_meaning": "The zodiac sign rising on the eastern horizon at the exact minute you were born.",
        "why_it_matters": "It is House #1 of your chart — it governs your physical body, immunity, appearance, self-confidence, and how your life unfolds.",
    },
    {
        "term": "Rashi (Moon Sign)",
        "simple_meaning": "The zodiac sign where the Moon was located when you were born.",
        "why_it_matters": "In Vedic astrology, the Moon governs your mind, emotions, gut instinct, and daily transit luck (Gochar).",
    },
    {
        "term": "Nakshatra (Birth Star / Lunar Mansion)",
        "simple_meaning": "One of the 27 star constellations the Moon passes through each month (each is 13°20' wide).",
        "why_it_matters": "Your birth Nakshatra determines your life's Dasha timeline (which planet rules which years of your life) and your daily Tara Bala (star luck).",
    },
    {
        "term": "Maraka (Health-Testing & Life-Boundary Planet)",
        "simple_meaning": "Literals means 'terminator' or 'vitality tester' — specifically the planets that rule House 2 and House 7 from your Ascendant.",
        "why_it_matters": "Because Houses 8 and 3 are the longevity houses, Houses 2 and 7 sit opposite them (12th from 3rd and 8th). During a Maraka planet's period (Dasha), you can experience high financial/relationship activity, but also physical exhaustion, illness, or medical crises if you don't protect your health.",
    },
    {
        "term": "Badhaka / Badhakadhipati (Hidden Roadblock Planet)",
        "simple_meaning": "The planet that creates unexpected last-minute delays, red tape, or invisible obstacles.",
        "why_it_matters": "For Movable signs (Aries, Cancer, Libra, Capricorn) it is the 11th house lord; for Fixed signs (Taurus, Leo, Scorpio, Aquarius) it is the 9th lord; for Dual signs (Gemini, Virgo, Sagittarius, Pisces) it is the 7th lord. Knowing your Badhaka planet lets you clear sudden blocks using its specific charity and Vastu fix.",
    },
    {
        "term": "Yogakaraka (Supreme Power & Kingmaker Planet)",
        "simple_meaning": "A single planet that simultaneously rules both a Pillar House (Kendra: 1, 4, 7, 10) and a Luck House (Trikona: 1, 5, 9).",
        "why_it_matters": "It is your chart's #1 most beneficial planet — wearing its gemstone or working during its Hora brings rapid promotion, wealth, and protection.",
    },
    {
        "term": "Functional Benefic vs. Functional Malefic",
        "simple_meaning": "Friendly helper planets for your specific Ascendant vs. troublemaker planets for your Ascendant.",
        "why_it_matters": "Planets ruling houses 1, 5, and 9 are your true friends (Functional Benefics — amplify them with gemstones). Planets ruling houses 6, 8, and 12 are Functional Malefics — never wear their gemstones; instead, calm them down with charity (Dana) and mantras.",
    },
    {
        "term": "Dusthana (Challenging Houses: 6th, 8th, and 12th)",
        "simple_meaning": "The three tough houses of the birth chart: 6th (debts, enemies, acute illness), 8th (sudden shocks, surgeries, chronic issues, unearned windfalls), and 12th (expenses, sleep, foreign lands, spiritual liberation).",
        "why_it_matters": "Planets placed here or ruling these houses require careful timing, Vastu alignment, and preventive remedies.",
    },
    {
        "term": "Indu Lagna (Sudden Wealth & Jackpot Point)",
        "simple_meaning": "A special mathematical wealth point calculated by adding the energy units (Kalas) of the 9th lord from Ascendant and 9th lord from Moon.",
        "why_it_matters": "Indu Lagna shows where and when sudden multi-fold money, lottery wins, windfalls, or booming investments can enter your life.",
    },
    {
        "term": "Hora (Planetary Hour)",
        "simple_meaning": "Each day from local Sunrise to the next Sunrise is divided into 24 planetary hours (12 daytime Horas, 12 nighttime Horas), each ruled by one of the 7 visible planets.",
        "why_it_matters": "Taking action during the Hora of your Lucky/Wealth planet at your current location multiplies success; avoiding Mars/Saturn Hora on risky days prevents accidents.",
    },
    {
        "term": "Rahu Kaal & Yamaganda (Daily Shadow Windows)",
        "simple_meaning": "Two 90-minute windows every day (calculated from your current city's exact Sunrise and Sunset) ruled by Rahu (confusion/obstruction) and Yama (loss/finality).",
        "why_it_matters": "Never sign new contracts, buy lottery tickets, start surgery, or begin a major trip during Rahu Kaal or Yamaganda.",
    },
    {
        "term": "Tara Bala (9-Fold Star Harmony)",
        "simple_meaning": "A daily score comparing today's Moon Nakshatra with your Birth Nakshatra across 9 categories.",
        "why_it_matters": "Sampat (Wealth #2), Kshema (Safety #4), Sadhaka (Achievement #6), Mitra (Friend #8), and Parama Mitra (Best Friend #9) days bring smooth success. Vipat (Danger #3), Pratyak (Obstacle #5), and Vadha/Naidhana (Destruction #7) days require caution.",
    },
    {
        "term": "Chandrashtama (2.5-Day Moon Caution Period)",
        "simple_meaning": "The 2.5 days every month when the transiting Moon passes through the 8th zodiac sign counted from your birth Moon sign.",
        "why_it_matters": "During Chandrashtama, emotions run high, focus drops, and minor mistakes can turn into accidents or arguments. Lay low and avoid risky decisions on these days.",
    },
    {
        "term": "Mrityu Bhaga (Fateful / Sensitive Degree)",
        "simple_meaning": "A specific single degree inside each zodiac sign where a planet becomes hyper-sensitive or fragile.",
        "why_it_matters": "If a planet sits within ~1° of its Mrityu Bhaga degree at birth, the body part and life area ruled by that planet need extra care.",
    },
    {
        "term": "Upapada Lagna (UL) & Darakaraka (DK)",
        "simple_meaning": "Upapada Lagna is the marriage manifestation point (calculated from the 12th house), and Darakaraka is the planet with the lowest degree in your chart (representing your spouse).",
        "why_it_matters": "Together with the 7th house and D-9 Navamsha chart, UL and DK reveal how many marriages you will have, your spouse's nature, and how to save a troubled marriage.",
    },
    {
        "term": "Beeja Sphuta & Kshetra Sphuta (Fertility Points)",
        "simple_meaning": "Mathematical points created by adding Sun + Venus + Jupiter (Beeja = seed/sperm vitality) and Moon + Mars + Jupiter (Kshetra = womb/receptive vitality).",
        "why_it_matters": "They show biological and energetic ability to conceive children and whether medical or mantra support is helpful.",
    },
    {
        "term": "D-7 Saptamsha, D-8 Ashtamsha, D-9 Navamsha & D-60 Shashtiamsha",
        "simple_meaning": "Microscopic zoom-in charts created by dividing each 30° zodiac sign into 7 parts (D-7 for children/grandchildren), 8 parts (D-8 for accidents), 9 parts (D-9 for marriage & soul strength), and 60 parts (D-60 for past-life karma).",
        "why_it_matters": "Two people born 5 minutes apart have the same main chart (D-1), but their D-7, D-9, and D-60 charts change — giving pinpoint accuracy for kids, marriage, and past lives.",
    },
    {
        "term": "Atmakaraka (AK) & Karakamsha (KL)",
        "simple_meaning": "Atmakaraka is the planet at the highest degree in your birth chart (the 'King of Your Soul'). Karakamsha is the sign that planet occupies in the D-9 Navamsha chart.",
        "why_it_matters": "They reveal why your soul incarnated in this life, your core spiritual lesson, your Ishta Devata (personal guiding deity), and your destination after this life.",
    },
    {
        "term": "Rina (Karmic Debt from Past Lives)",
        "simple_meaning": "Unpaid energetic obligations carried over from previous incarnations — toward ancestors (Pitru Rina), mother/nurturers (Matru Rina), sages/teachers (Deva/Guru Rina), partners (Stri Rina), or living beings (Jeeva Rina).",
        "why_it_matters": "When a Rina is active, you feel 'stuck' in that area of life until you perform the simple compensatory act of service/remedy to clear the ledger.",
    },
    {
        "term": "Brahmasthan, Ishanya (NE), Agneya (SE), Nairutya (SW) & Vayavya (NW)",
        "simple_meaning": "The 5 key Vastu zones of any home or lot: Brahmasthan = exact center (Space element); Ishanya = North-East (Water/Divine wisdom); Agneya = South-East (Fire/Kitchen/Cash flow); Nairutya = South-West (Earth/Master stability); Vayavya = North-West (Air/Movement).",
        "why_it_matters": "Aligning your rooms and outdoor yard with these 5 elemental zones turns your home into a 24/7 battery that boosts your birth chart.",
    },
]


# ---------------------------------------------------------------------------
# 2. DIRECTIONAL VASTU & PLANETARY MAPPING
# ---------------------------------------------------------------------------
DIRECTION_META: Dict[str, Dict[str, Any]] = {
    "N": {
        "name": "North (Uttara — Kubera Zone)",
        "planet": "Mercury",
        "deity": "Lord Kubera (Treasurer of the Gods)",
        "element": "Water / Earth Transition",
        "life_domain": "Liquid money, career opportunities, business growth, intellect, and trade",
        "best_rooms": ["Entrance", "Living Room", "Safe / Locker (opening North)", "Study / Office", "Balcony", "Garden / Lawn"],
        "avoid_rooms": ["Heavy Storage", "Kitchen Stove", "Toilet / Septic Tank", "Tall Heavy Trees blocking light"],
        "color_palette": "Light Green, Mint, White, Soft Blue",
    },
    "NE": {
        "name": "North-East (Ishanya — Sacred Wisdom & Blessings Zone)",
        "planet": "Jupiter",
        "secondary_planet": "Ketu",
        "deity": "Lord Shiva / Ishana",
        "element": "Water (Jala) & Divine Ether",
        "life_domain": "Divine grace, mental peace, intuition, children & grandchildren's fortune, immunity, and spiritual clarity",
        "best_rooms": ["Puja / Meditation Room", "Main Entrance", "Living Room", "Balcony / Veranda", "Underground Water / Fountain", "Small Flowers / Lawn"],
        "avoid_rooms": ["Bathroom / Toilet (Major Dosha!)", "Kitchen / Fireplace", "Master Bedroom", "Heavy Storage", "Staircase", "Septic Tank", "Tall Dense Trees"],
        "color_palette": "Cream, Soft Yellow, Off-White, Sky Blue",
    },
    "E": {
        "name": "East (Purva — Solar Vitality & Social Authority Zone)",
        "planet": "Sun",
        "deity": "Lord Surya & Indra",
        "element": "Air / Fire (Rising Prana)",
        "life_domain": "Health, vitality, government/leadership recognition, father's wellbeing, and new beginnings",
        "best_rooms": ["Main Entrance", "Living Room", "Study Room", "Balcony", "Bathroom (clean/ventilated)", "Garden / Flowers / Lawn"],
        "avoid_rooms": ["Heavy Storage / Junk", "Staircase", "Tall Trees or High Wall blocking morning sun", "Garage / Parking Shed"],
        "color_palette": "Warm White, Peach, Soft Orange, Light Gold",
    },
    "SE": {
        "name": "South-East (Agneya — Fire, Cash Flow & Energy Zone)",
        "planet": "Venus",
        "deity": "Agni Deva (Lord of Fire)",
        "element": "Fire (Agni)",
        "life_domain": "Daily cash flow, digestion, metabolic health, passion, luxury, and active kitchen energy",
        "best_rooms": ["Kitchen (Ideal #1)", "Outdoor Fireplace / BBQ", "Electrical Panel / Generator", "Workout / Gym"],
        "avoid_rooms": ["Master Bedroom (causes arguments)", "Bathroom / Toilet", "Underground Water / Pool", "Main Entrance (unless remedied)", "Safe / Locker"],
        "color_palette": "Soft Pink, Coral, Pastel Orange, Silver-White",
    },
    "S": {
        "name": "South (Dakshina — Stamina, Discipline & Recognition Zone)",
        "planet": "Mars",
        "deity": "Lord Yama (Lord of Dharma & Discipline)",
        "element": "Earth / Fire",
        "life_domain": "Courage, legal victory, property strength, deep relaxation, and fame",
        "best_rooms": ["Bedroom", "Dining Room", "Storage", "Staircase", "High Boundary Wall / Fence", "Tall Trees"],
        "avoid_rooms": ["Main Entrance (unless Pada 4/Grihakshat)", "Underground Water / Borewell", "Open Low Balcony"],
        "color_palette": "Warm Beige, Terracotta, Coral, Earthy Cream",
    },
    "SW": {
        "name": "South-West (Nairutya — Master Stability, Ancestors & Wealth Retention Zone)",
        "planet": "Rahu",
        "deity": "Nirriti & Pitris (Ancestors)",
        "element": "Earth (Prithvi — Heaviest Zone)",
        "life_domain": "Long-term stability, command/leadership, marriage durability, savings retention, and ancestral protection",
        "best_rooms": ["Master Bedroom (Ideal #1)", "Heavy Storage / Wardrobe", "Safe / Locker (placed in SW facing North)", "Staircase", "High Fence", "Tall Heavy Trees"],
        "avoid_rooms": ["Main Entrance (drains wealth)", "Kitchen", "Bathroom / Toilet", "Underground Water / Pool", "Puja Room"],
        "color_palette": "Earthy Sand, Beige, Soft Ochre, Warm Taupe",
    },
    "W": {
        "name": "West (Paschima — Gains, Profits & Fulfillment Zone)",
        "planet": "Saturn",
        "deity": "Lord Varuna (Lord of Cosmic Order & Oceans)",
        "element": "Water / Earth Stability",
        "life_domain": "Business profits, return on effort, real estate gains, dining satisfaction, and steady maturity",
        "best_rooms": ["Dining Room", "Children's Bedroom", "Study Room", "Storage", "Staircase", "Overhead Water Tank", "Trees / Fence"],
        "avoid_rooms": ["Underground Water / Pool", "Low Depression in Lot"],
        "color_palette": "White, Soft Grey, Light Blue, Cream",
    },
    "NW": {
        "name": "North-West (Vayavya — Movement, Helpful People & Support Zone)",
        "planet": "Moon",
        "deity": "Vayu Deva (Lord of Wind)",
        "element": "Air (Vayu)",
        "life_domain": "Helpful social/banking contacts, travel, emotional flow, marriage proposals, and quick turnover",
        "best_rooms": ["Guest Room (Ideal #1)", "Bathroom / Toilet", "Finished Goods Storage", "Parking Gate / Garage", "Kitchen (Alternative #2)", "Bushes / Fragrant Flowers"],
        "avoid_rooms": ["Master Bedroom (causes restlessness)", "Safe / Cash Locker (money flies away)", "Heavy South-West style weight"],
        "color_palette": "Pure White, Pearl, Cream, Light Silver",
    },
    "Center": {
        "name": "Center (Brahmasthan — Cosmic Heart of the Home)",
        "planet": "Jupiter",
        "deity": "Lord Brahma (The Creator)",
        "element": "Space / Ether (Akasha)",
        "life_domain": "Overall harmony, family unity, pranic circulation, and health of the head of the family",
        "best_rooms": ["Open Courtyard", "Central Living Hall (light & clutter-free)", "Open Lawn (if courtyard)"],
        "avoid_rooms": ["Bathroom / Toilet (Severe Dosha!)", "Kitchen / Fireplace", "Heavy Storage", "Staircase", "Heavy Pillars"],
        "color_palette": "White, Light Ivory, Marble, Pale Gold",
    },
}


# ---------------------------------------------------------------------------
# 3. PERSONALIZED BIRTH-CHART ASTRO-VASTU SYNTHESIS
# ---------------------------------------------------------------------------
def compute_personalized_astro_vastu(
    pos: Dict[str, Any],
    asc_lon: float,
) -> Dict[str, Any]:
    """Cross-links the native's Birth Chart (Lagna, Moon, 4th House of Home,
    9th Bhagya Lord, 2nd/11th Wealth Lords, and Weak/Afflicted Planets) with
    directional Vastu Shastra to double positive astrological effects."""
    lagna_idx = int(asc_lon // 30) % 12
    moon_idx = int(pos["Moon"]["longitude"] // 30) % 12
    h4_idx = (lagna_idx + 3) % 12  # 4th house of home, land, and domestic peace
    h9_idx = (lagna_idx + 8) % 12  # 9th house of luck/fortune
    h11_idx = (lagna_idx + 10) % 12  # 11th house of gains
    h2_idx = (lagna_idx + 1) % 12  # 2nd house of savings
    h8_idx = (lagna_idx + 7) % 12  # 8th house of sudden obstacles

    lagna_lord = SIGN_LORDS[lagna_idx]
    moon_lord = SIGN_LORDS[moon_idx]
    h4_lord = SIGN_LORDS[h4_idx]
    h9_lord = SIGN_LORDS[h9_idx]
    h11_lord = SIGN_LORDS[h11_idx]
    h2_lord = SIGN_LORDS[h2_idx]
    h8_lord = SIGN_LORDS[h8_idx]

    planet_to_dir = {
        "Sun": ("E", "East"),
        "Moon": ("NW", "North-West"),
        "Mars": ("S", "South"),
        "Mercury": ("N", "North"),
        "Jupiter": ("NE", "North-East"),
        "Venus": ("SE", "South-East"),
        "Saturn": ("W", "West"),
        "Rahu": ("SW", "South-West"),
        "Ketu": ("NE", "North-East"),
    }

    lagna_dir_code, lagna_dir_name = planet_to_dir[lagna_lord]
    h4_dir_code, h4_dir_name = planet_to_dir[h4_lord]
    h9_dir_code, h9_dir_name = planet_to_dir[h9_lord]
    wealth_dir_code, wealth_dir_name = planet_to_dir[h11_lord]
    caution_dir_code, caution_dir_name = planet_to_dir[h8_lord]

    # Analyze each of the 8 compass zones specifically through the lens of the native's chart
    personalized_zone_guide = []
    for code in ("NE", "E", "SE", "S", "SW", "W", "NW", "N", "Center"):
        meta = DIRECTION_META[code]
        ruler = meta["planet"]
        p_lon = pos[ruler]["longitude"]
        p_sign_idx = int(p_lon // 30) % 12
        p_house = (p_sign_idx - lagna_idx) % 12 + 1
        dig = dignity(ruler, p_lon) if ruler not in ("Rahu", "Ketu") else "shadow"

        if p_house in (6, 8, 12) or dig == "debilitated":
            chart_status = f"Sensitive Zone in Your Chart ({ruler} is in House {p_house}, {SIGNS[p_sign_idx]})"
            double_effect_tip = (
                f"Because {ruler} sits in a challenging position (House {p_house}) in your birth chart, keeping the "
                f"{meta['name']} of your home/lot spotless, clutter-free, and balanced with {meta['color_palette'].split(',')[0]} "
                f"acts as a 24/7 physical remedy that heals {ruler}'s obstacles automatically!"
            )
        elif ruler in (lagna_lord, h4_lord, h9_lord, h11_lord):
            chart_status = f"Power Multiplier Zone ({ruler} rules your Key Fortune/Home/Self Axis in House {p_house})"
            double_effect_tip = (
                f"{ruler} is one of your prime chart benefactors (placed in House {p_house}, {SIGNS[p_sign_idx]}). "
                f"Activating the {meta['name']} with {', '.join(meta['best_rooms'][:2])} and {meta['color_palette'].split(',')[0]} "
                f"accents DOUBLES the positive results of your mantras and gemstones!"
            )
        else:
            chart_status = f"Supportive Zone ({ruler} in House {p_house}, {SIGNS[p_sign_idx]})"
            double_effect_tip = (
                f"Maintain classical Vastu balance in the {meta['name']} (use for {', '.join(meta['best_rooms'][:2])}; "
                f"avoid {', '.join(meta['avoid_rooms'][:2])}) to keep {ruler}'s energy flowing smoothly."
            )

        personalized_zone_guide.append({
            "direction_code": code,
            "direction_name": meta["name"],
            "ruling_planet": ruler,
            "deity_and_element": f"{meta['deity']} | {meta['element']}",
            "your_chart_planet_placement": f"{ruler} in {SIGNS[p_sign_idx]} (House {p_house})",
            "chart_zone_status": chart_status,
            "best_uses": meta["best_rooms"],
            "strictly_avoid": meta["avoid_rooms"],
            "lucky_wall_and_decor_colors": meta["color_palette"],
            "double_positive_effect_secret": double_effect_tip,
        })

    dos_list = [
        f"1. Power Entrance & Window Rule: Keep the {lagna_dir_name} ({lagna_lord}, your Ascendant Lord) and {h9_dir_name} ({h9_lord}, your 9th Luck Lord) sectors of your home bright, ventilated, and open every morning.",
        f"2. Best Sleeping Head Direction: Sleep with your head pointing toward the South (for deep cellular recovery and Mars/Earth magnetic alignment) or {h4_dir_name} (aligned with your 4th Home Lord {h4_lord}). Never sleep with your head pointing Due North.",
        f"3. Double-Wealth Safe & Desk Rule: Place your cash locker, safe, or primary investment computer in the South-West or {wealth_dir_name} ({h11_lord}) room, positioning it so that you face North (Kubera) or North-East (Jupiter) while working or opening the safe.",
        "4. Sacred North-East (Ishanya) Rule: Keep the North-East corner of both your house and your outer lot lighter, lower, and cleaner than every other corner. A small bowl of clean water with fresh flowers or a fountain in the North-East multiplies Jupiter's blessings for children and wisdom.",
        "5. Kitchen Fire Rule: Ensure the kitchen stove is in the South-East (Agneya) or North-West, and orient the stove so the person cooking faces East.",
        "6. Outer Lot & Yard Greenery Rule: Plant tall, heavy shade or fruit trees in the South, South-West, or West of the outer lot to block harsh afternoon radiation and anchor Earth energy, while keeping low grass lawn, tulsi, jasmine, and small flowers in the North, East, and North-East.",
    ]

    donts_list = [
        f"1. Protect Your Sensitive Sector ({caution_dir_name} — Ruled by 8th Lord {h8_lord}): Never accumulate broken electronics, rusted iron, dead plants, or leaking pipes in the {caution_dir_name} of your house or yard, as that immediately triggers 8th-house sudden stress.",
        "2. Never Block the Center (Brahmasthan): Keep the exact center of your house open and free from bathrooms, heavy storage closets, fireplaces, or load-bearing clutter.",
        "3. No Toilet or Kitchen in North-East: A bathroom or fireplace/kitchen in the North-East (Ishanya) clashes with Jupiter's water/ether element, blocking financial growth and family health. If one already exists there, place a bowl of natural sea salt (changed weekly) and hang a Vastu copper strip outside the door.",
        "4. No Mirror Facing the Bed: Never place a mirror or reflective wardrobe door where it reflects your body while sleeping — according to Vastu, it doubles fatigue and disturbs marital peace.",
        "5. No Heavy Trees or Trash in Front of the Main Entrance: Never plant a large tree, pole, or trash bin directly facing the Main Entrance or Main Gate (Vedha Dosha).",
        "6. Avoid Dark/Heavy South-West Excavations: Never put an underground swimming pool, borewell, or deep pit in the South-West corner of the lot.",
    ]

    return {
        "native_home_signature": {
            "lagna_sign": SIGNS[lagna_idx],
            "lagna_lord": f"{lagna_lord} ( Governs {lagna_dir_name} )",
            "fourth_house_of_home_sign": SIGNS[h4_idx],
            "fourth_house_lord": f"{h4_lord} ( Governs {h4_dir_name} )",
            "ninth_house_luck_lord": f"{h9_lord} ( Governs {h9_dir_name} )",
            "eleventh_house_gains_lord": f"{h11_lord} ( Governs {wealth_dir_name} )",
            "ideal_house_or_lot_facing_directions": list(dict.fromkeys([lagna_dir_name, h4_dir_name, h9_dir_name, "East", "North", "North-East"]))[:4],
            "best_sleeping_head_directions": ["South (Universal Longevity & Deep Rest)", f"{h4_dir_name} (Your 4th Home Lord {h4_lord} Harmony)", "East (Memory, Wisdom & Solar Vitality)"],
            "best_work_and_wealth_facing_directions": ["North (Lord Kubera Treasury)", "North-East (Ishanya Divine Clarity)", f"{h9_dir_name} (Your 9th Bhagya Lord {h9_lord})"],
        },
        "personalized_nine_zone_astro_vastu_map": personalized_zone_guide,
        "astro_vastu_dos_to_double_positive_effect": dos_list,
        "astro_vastu_donts_to_prevent_bad_luck": donts_list,
        "personalized_chart_preset": build_personalized_chart_preset(pos, asc_lon),
    }


# ---------------------------------------------------------------------------
# 4. INTERACTIVE VISUAL HOUSE (SQUARE/RECTANGLE) & OUTER-LOT VASTU + FENG SHUI EVALUATOR
# ---------------------------------------------------------------------------
GATE_MECHANISM_RULES: Dict[str, Dict[str, Any]] = {
    "swing_in_cw": {
        "label": "Swings Inward — Clockwise (Pradakshina)",
        "score_delta": 1,
        "verdict": "SUPREME IDEAL: Door/Gate swings inward clockwise (Pradakshina), smoothly drawing auspicious Prana & Sheng Qi into the property.",
        "remedy": "Keep hinges well-oiled so the gate/door never creaks (creaking hinges cause Swara Vedha).",
    },
    "double_in": {
        "label": "Double-Leaf Gate — Swings Inward from Center",
        "score_delta": 1,
        "verdict": "ROYAL SIMHADWARA: Double-leaf inward-opening gate/door welcomes balanced bilateral Qi and dignity.",
        "remedy": "Ensure both leaves open symmetrically without obstruction.",
    },
    "swing_in_ccw": {
        "label": "Swings Inward — Counter-Clockwise (Left-Hand)",
        "score_delta": 0,
        "verdict": "ACCEPTABLE: Opens inward (good), though counter-clockwise (Vama) flow is slightly less auspicious than clockwise.",
        "remedy": "Place a small brass or copper pyramid on the hinge-side lintel to harmonize inward vortex flow.",
    },
    "swing_out": {
        "label": "Swings Outward (Toward Street / Outside)",
        "score_delta": -2,
        "verdict": "VASTU & FENG SHUI WARNING: Outward-swinging gate/door pushes incoming Lakshmi / Sheng Qi away from the house.",
        "remedy": "Zero-demolition fix: Place two inward-curving planters or pillar lamps flanking the gate and install a brass/copper threshold strip.",
    },
    "slide_ne": {
        "label": "Sliding Gate / Door — Slides Open Toward North or East",
        "score_delta": 1,
        "verdict": "AUSPICIOUS SLIDING MECHANISM: Sliding gate opens toward the positive Solar/Magnetic pole (North/East), inviting unobstructed flow.",
        "remedy": "Keep the sliding track clean and smooth so it never jams.",
    },
    "slide_sw": {
        "label": "Sliding Gate / Door — Slides Open Toward South or West",
        "score_delta": -1,
        "verdict": "CAUTION (SLIDING TOWARD S/W): Gate slides toward the heavy South/West sector, pulling kinetic motion toward Nirriti/Yama.",
        "remedy": "Attach a copper Vastu strip along the track and place a heavy yellow stone or brass pyramid at the South/West stopper post.",
    },
    "rollup": {
        "label": "Overhead Roll-Up / Vertical Lift Gate",
        "score_delta": 0,
        "verdict": "NEUTRAL / MODERN: Vertical roll-up gate is neutral in Vastu & Feng Shui provided it is well-lit and silent.",
        "remedy": "Keep a warm overhead light above the gate lintel.",
    },
}

WALL_SIDE_LABELS: Dict[str, str] = {
    "N": "North Wall (Facing South)",
    "E": "East Wall (Facing West)",
    "S": "South Wall (Facing North)",
    "W": "West Wall (Facing East)",
    "NE": "North-East Wall",
    "SE": "South-East Wall",
    "SW": "South-West Wall",
    "NW": "North-West Wall",
}

ITEM_RULES: Dict[str, Dict[str, Any]] = {
    # ---------------- INDOOR ROOMS, DOORS & SACRED SPACES ----------------
    "entrance": {
        "label": "Main Entrance Door",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["W", "NW"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "ideal_door_facing": ["NE", "E", "N"],
        "why_simple": "The Main Entrance (Simhadwara / Mouth of Qi) is where cosmic energy (Prana) and wealth enter. North-East (Jupiter), East (Sun), and North (Mercury/Kubera) bring health, fame, and steady prosperity. It should ideally swing inward clockwise.",
        "fix_if_wrong": "If your entrance is in South, South-West, or South-East, place a bright warm light above the door, install a copper/lead Vastu strip along the threshold, place two auspicious plants on either side, and hang a Panchamukhi Hanuman or Ganesha emblem above the lintel.",
    },
    "back_door": {
        "label": "Back Door / Patio Sliding Exit",
        "category": "indoor",
        "ideal_zones": ["NW", "W", "E", "N"],
        "acceptable_zones": ["SE", "NE"],
        "bad_zones": ["SW", "S", "Center"],
        "ideal_door_facing": ["N", "E", "NW", "W"],
        "why_simple": "The Back Door or Patio Sliding Door allows air circulation without draining stored wealth. Avoid placing the back door in a direct straight line with the Main Entrance (Feng Shui 'Chuan Tang Sha' wealth-tunnel drain) and avoid South-West.",
        "fix_if_wrong": "Keep a South-West or South back door closed when not in use, place a heavy earth-toned rug inside, and if it aligns straight with the front door, place a screen, plant, or table between them.",
    },
    "puja_room": {
        "label": "Temple / Prayer Hall / Puja Altar",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["W", "Center"],
        "bad_zones": ["S", "SW", "SE", "NW"],
        "ideal_door_facing": ["E", "N", "NE", "W"],
        "why_simple": "The North-East (Ishanya) is the supreme spiritual receptor of the home (Jupiter & Shiva), and in Feng Shui it is the Gen (Mountain/Wisdom) sector. Worshippers should face East or North; idols should face West or East.",
        "fix_if_wrong": "Never place the Temple/Prayer Hall under a staircase or sharing a wall with a bathroom/toilet. Keep a copper Kalash of clean water in the NE corner of the altar, light a ghee lamp daily, and never mix deceased ancestors' photos on the Puja altar.",
    },
    "meditation_hall": {
        "label": "Meditation / Yoga / Dhyana Space",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["Center", "W"],
        "bad_zones": ["SE", "S", "SW", "NW"],
        "ideal_door_facing": ["E", "NE", "N"],
        "why_simple": "Meditation and Pranayama require calm Sattvic Ether/Water vibration in the North-East or rising Solar Prana in the East. Facing East or North-East aligns the pineal gland with Earth's magnetic field.",
        "fix_if_wrong": "Use a natural Kusha grass, wool, or cotton mat, face North-East or East while meditating, and burn pure sandalwood or loban incense.",
    },
    "medication_cabinet": {
        "label": "Medicine / Medication & First-Aid Storage",
        "category": "indoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW", "W"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "why_simple": "Per Vastu Shastra, medicines kept in the North-East (Dhanvantari / Divine Healer zone) or North (Soma) infuse remedies with rapid healing energy so illness resolves quickly. Keeping medicines in the South-West (stability/permanence) or South-East (Fire/Kitchen) makes diseases drag on chronically!",
        "fix_if_wrong": "Immediately move daily medicines and pill boxes out of the Kitchen (SE), South, or Master Bedroom (SW) into a clean white/wooden box in the North-East or North-East-North (NNE) zone, and discard expired medications every Amavasya.",
    },
    "gym_room": {
        "label": "Gym / Workout / Fitness Equipment",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "W", "SE"],
        "acceptable_zones": ["NW", "E"],
        "bad_zones": ["NE", "Center", "N"],
        "ideal_door_facing": ["E", "N"],
        "why_simple": "Gym dumbbells, treadmills, and weight racks are heavy physical masses governed by Mars (South/SE strength & sweat) and Saturn/Rahu (West/SW Earth stability). Placing heavy gym weights in the North-East crushes the sacred head of the Vastu Purusha!",
        "fix_if_wrong": "If your workout area is in the North-East or North, move all heavy iron dumbbells/machines to the South or West corner of that room, place rubber shock-absorbing mats underneath, and face East while exercising.",
    },
    "storage": {
        "label": "Heavy Storage / Store Room / Closet",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "W", "NW"],
        "acceptable_zones": ["SE"],
        "bad_zones": ["NE", "E", "N", "Center"],
        "why_simple": "Heavy storage, trunks, tools, and seasonal boxes add dense Earth mass — ideal in South-West, South, or West to anchor the home, but harmful in North-East, North, East, or Center where they block financial & mental clarity.",
        "fix_if_wrong": "Declutter North/East/NE storage immediately, keep the top shelf lighter than the bottom shelf, paint the inside white, and keep a bright LED light inside.",
    },
    "grain_pantry": {
        "label": "Food & Grain Pantry (Anna Bhandar)",
        "category": "indoor",
        "ideal_zones": ["NW", "SW", "W", "S"],
        "acceptable_zones": ["SE"],
        "bad_zones": ["NE", "Center", "N"],
        "why_simple": "Classical Vastu places the granary/pantry (Anna Bhandar) in the North-West (Vayavya — continuous replenishment of food) or South-West (Earth abundance) so the household never experiences food scarcity.",
        "fix_if_wrong": "Keep a small silver coin or turmeric root inside the rice/grain container to invoke Maa Annapurna's blessings.",
    },
    "washer_dryer": {
        "label": "Washer & Dryer / Laundry Machine",
        "category": "indoor",
        "ideal_zones": ["NW", "SE", "W"],
        "acceptable_zones": ["E", "S"],
        "bad_zones": ["NE", "SW", "Center", "N"],
        "why_simple": "A Washer & Dryer combines vigorous mechanical churning (Vayu/Air), dirty water drainage, and high electrical heat (Dryer = Agni). North-West (Vayavya movement), East-South-East (churning), and South-East (Agni) are ideal. Placing a washer/dryer in North-East churns the mind with anxiety; in South-West it destabilizes career/marriage.",
        "fix_if_wrong": "Place a thick anti-vibration rubber pad under the washer/dryer, keep the laundry lid/door closed when not running, and place a green plant or wooden board nearby if located in NE/SW.",
    },
    "kitchen": {
        "label": "Kitchen Room",
        "category": "indoor",
        "ideal_zones": ["SE", "NW"],
        "acceptable_zones": ["E", "S"],
        "bad_zones": ["NE", "SW", "N", "W", "Center"],
        "why_simple": "The Kitchen is governed by Agni (Fire) and belongs in the South-East (Agneya) or secondarily North-West (Vayavya). A kitchen in North-East clashes with sacred Water, and in South-West destabilizes family health and savings.",
        "fix_if_wrong": "Keep the cooking stove in the South-East corner of the kitchen so the cook faces East, place a yellow Jaisalmer stone or green marble slab under the stove if in NE/SW, and separate the stove from the sink.",
    },
    "kitchen_stove": {
        "label": "Kitchen Stove / Cooktop / Range (Agni)",
        "category": "indoor",
        "ideal_zones": ["SE", "S", "E"],
        "acceptable_zones": ["NW"],
        "bad_zones": ["NE", "N", "SW", "W", "Center"],
        "ideal_door_facing": ["E", "N"],
        "why_simple": "The Kitchen Stove (Chulha / Range) is the primary Fire altar of the home and Feng Shui's #1 wealth generator (Zao Jun). It belongs in the South-East with the cook facing East. In both Vastu and Feng Shui, the stove must NEVER touch or directly face the kitchen sink/taps (Fire-Water clash) or sit directly in line with the kitchen/bathroom door.",
        "fix_if_wrong": "Orient the stove or your standing position toward East; if the stove is close to the water sink/taps, place a vertical wooden chopping board, green herb pot (basil/mint), or green tape strip between the stove and sink to bridge Water-Fire.",
    },
    "indoor_taps": {
        "label": "Indoor Water Taps / Kitchen Sink / Faucets",
        "category": "indoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW", "W"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "why_simple": "Water taps, kitchen sinks, and drinking water filters belong in the North-East, North, or East (Jala/Water zones). Taps in the South-West or South weaken Earth stability, and taps right next to the SE stove create Fire-Water friction. A dripping tap anywhere drains liquid wealth!",
        "fix_if_wrong": "Repair any dripping tap immediately; if taps are in the South-East or South-West, place a green plant or wooden coaster beside the sink and ensure drain pipes exit toward North or East.",
    },
    "master_bedroom": {
        "label": "Master Bedroom",
        "category": "indoor",
        "ideal_zones": ["SW", "S"],
        "acceptable_zones": ["W"],
        "bad_zones": ["NE", "SE", "NW", "Center", "E", "N"],
        "ideal_door_facing": ["S", "E", "W"],
        "why_simple": "The Master Bedroom belongs in the South-West (Nairutya Earth element / Feng Shui Kun Marriage sector) or South so the head of the household enjoys deep sleep, authority, and marital harmony. Sleep with the bed head toward South or East (never North).",
        "fix_if_wrong": "Place the bed in the South-West corner of the room with the headboard against a solid South or West wall, use earthy beige/terracotta tones, and keep a pair of rose quartz crystals on the nightstand.",
    },
    "bedroom": {
        "label": "Bedroom (Family / Children)",
        "category": "indoor",
        "ideal_zones": ["W", "S", "E", "NW"],
        "acceptable_zones": ["N", "SW"],
        "bad_zones": ["NE", "SE", "Center"],
        "ideal_door_facing": ["S", "E", "W"],
        "why_simple": "West (Feng Shui Dui Children sector), East (rising Sun growth), South, and North-West provide restful sleep, study focus, and vitality for children and family members.",
        "fix_if_wrong": "Ensure the sleeper's head points South or East (never North), avoid overhead ceiling beams above the bed, and keep electronics/TV covered at night.",
    },
    "guest_room": {
        "label": "Guest Bedroom",
        "category": "indoor",
        "ideal_zones": ["NW", "E", "N"],
        "acceptable_zones": ["W", "SE"],
        "bad_zones": ["SW", "Center", "NE"],
        "why_simple": "North-West (Vayavya Air / Feng Shui Qian Helpful People) is ideal for guests — welcoming and supportive without letting guests dominate the homeowner's South-West authority.",
        "fix_if_wrong": "If the Guest Room is in the South-West, keep heavy owner wardrobes or a locked owner safe in that room so the homeowner retains primary Earth-zone command.",
    },
    "living_room": {
        "label": "Living Room / Family Lounge",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N", "NW", "Center"],
        "acceptable_zones": ["W", "S"],
        "bad_zones": ["SW", "SE"],
        "why_simple": "The Living Room thrives in the bright, open, social sectors (North, East, North-East, or North-West) where welcoming Qi and family harmony circulate freely.",
        "fix_if_wrong": "Anchor heavy sofas and cabinets against the South and West walls of the living room while keeping the North and East sides bright and open.",
    },
    "dining_room": {
        "label": "Dining Room",
        "category": "indoor",
        "ideal_zones": ["W", "E", "S", "N"],
        "acceptable_zones": ["SE", "NW"],
        "bad_zones": ["SW", "NE", "Center"],
        "why_simple": "West (Varuna/Saturn nourishment) and East promote healthy digestion, gratitude, and family bonding over meals.",
        "fix_if_wrong": "Face East, North, or West while eating (avoid facing South during meals), and keep a bowl of fresh fruit on the table.",
    },
    "study_room": {
        "label": "Study / Home Office Desk",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N", "W"],
        "acceptable_zones": ["SW", "NW"],
        "bad_zones": ["SE", "Center"],
        "ideal_door_facing": ["NE", "E", "N"],
        "why_simple": "East (Sun), North (Mercury intellect), North-East (Jupiter wisdom), and West (Saturn focus) sharpen concentration and career output. Always sit with a solid wall behind your back (Feng Shui Black Tortoise support).",
        "fix_if_wrong": "Orient your chair so you face East, North, or North-East while working, and place a clear quartz crystal or globe on the North-East corner of the desk.",
    },
    "bathroom": {
        "label": "Bathroom / Toilet / WC",
        "category": "indoor",
        "ideal_zones": ["NW", "W", "S"],
        "acceptable_zones": ["SE", "E"],
        "bad_zones": ["NE", "SW", "Center", "N"],
        "why_simple": "Bathrooms and toilets handle waste elimination and belong in North-West (Vayavya), West, or South-South-West. A toilet in North-East, Center (Brahmasthan), or South-West is a severe Vastu & Feng Shui drain.",
        "fix_if_wrong": "Keep the toilet lid down and bathroom door closed at all times, place a glass bowl of crushed sea salt / rock salt inside (replace weekly), install a copper strip outside the door threshold, and keep an air-purifying plant inside.",
    },
    "balcony": {
        "label": "Balcony / Veranda / Deck",
        "category": "indoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW"],
        "bad_zones": ["SW", "S", "W", "SE", "Center"],
        "why_simple": "Balconies open the home to light and air — ideal in North, East, and North-East to invite morning solar Prana and Kubera wealth.",
        "fix_if_wrong": "If your balcony is in South or South-West, add heavy terracotta planters, thick curtains/blinds, or glass enclosures to increase weight in the SW.",
    },
    "staircase": {
        "label": "Staircase",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "W"],
        "acceptable_zones": ["NW", "SE"],
        "bad_zones": ["NE", "Center", "N", "E"],
        "why_simple": "A staircase is a heavy vertical mass that belongs in South-West, South, or West and should ascend clockwise (turning right as you go up).",
        "fix_if_wrong": "Never put a Puja altar, kitchen stove, or cash safe directly under a staircase; place a pair of copper pyramids under the first and last step.",
    },
    "safe_locker": {
        "label": "Safe / Cash Locker / Tijori",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "N"],
        "acceptable_zones": ["W"],
        "bad_zones": ["SE", "NW", "NE", "Center", "E"],
        "ideal_door_facing": ["N", "NE", "E"],
        "why_simple": "Place the Cash Safe in the South-West or South against the South wall so its door opens toward the North (the direction of Lord Kubera, Treasurer of the Gods) or North-East.",
        "fix_if_wrong": "Line the inside of the safe with red/yellow cloth, keep a Shree Yantra and Citrine/Pyrite crystal inside, and ensure the safe never opens toward a bathroom or main exit door.",
    },
    "shoe_rack": {
        "label": "Shoe Rack / Footwear Stand",
        "category": "indoor",
        "ideal_zones": ["W", "NW", "SW", "S"],
        "acceptable_zones": ["SE"],
        "bad_zones": ["NE", "N", "E", "Center"],
        "why_simple": "Shoes carry outside dust and Saturn/Rahu Tamasic energy. Keep shoe racks in a closed cabinet in the West, North-West, or South-West foyer — never in the sacred North-East, Puja room, or Kitchen, and never piled loosely across the main threshold.",
        "fix_if_wrong": "Use a closed-door shoe cabinet (so shoes are not visible), keep it slightly off the main door threshold, and wipe it clean weekly.",
    },
    "electrical_inverter": {
        "label": "Electrical Panel / Inverter / Water Heater",
        "category": "indoor",
        "ideal_zones": ["SE", "S", "NW"],
        "acceptable_zones": ["W", "E"],
        "bad_zones": ["NE", "Center", "SW", "N"],
        "why_simple": "Main electrical panels, inverters, boilers, and furnaces generate intense electromagnetic heat (Agni) and belong in the South-East (Agneya).",
        "fix_if_wrong": "Keep electrical meters/inverters enclosed in a non-conductive cabinet and never place a bed headboard directly on the opposite side of a high-voltage panel wall.",
    },
    "aquarium_indoor_water": {
        "label": "Indoor Aquarium / Tabletop Fountain",
        "category": "indoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["SE"],
        "bad_zones": ["SW", "S", "W", "NW", "Center"],
        "why_simple": "Moving water indoors (aquariums, tabletop fountains) activates Kubera wealth (North), Ishanya clarity (North-East), and Feng Shui Sheng Qi. Never place an aquarium or water fountain inside a Bedroom or in the South Fire sector!",
        "fix_if_wrong": "Ensure water is always aerated, crystal-clear, and flowing inward toward the center of the house (never pointing out the door).",
    },
    "indoor_plants_tulsi": {
        "label": "Tulsi Vrindavan / Sacred Indoor Plants",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["NW", "SE"],
        "bad_zones": ["SW", "S", "Center"],
        "why_simple": "Holy Basil (Tulsi), Lucky Bamboo, Money Plant, and oxygenating green plants belong in the North-East, East, or North where they purify Prana and strengthen Mercury & Jupiter.",
        "fix_if_wrong": "Avoid thorny cacti, bonsai (stunted growth), or artificial dusty plastic plants inside the house; water Tulsi daily except Sundays/Ekadashi.",
    },

    # ---------------- WALL HANGINGS: PHOTO FRAMES, TV, MIRROR & CLOCK ----------------
    "photo_living": {
        "label": "Photo Frame: Living Family / Couple / Kids",
        "category": "indoor",
        "ideal_zones": ["SW", "W", "E", "N", "NE"],
        "acceptable_zones": ["NW", "Center"],
        "bad_zones": ["S", "SE"],
        "ideal_wall_sides": ["SW", "W", "E", "N"],
        "why_simple": "Photos of living family members, married couples, and children belong in the South-West (bonds marriage stability & family unity), West (Feng Shui Dui Children/Joy sector), East (family health), or North. NEVER hang living family members' photos on the South Pitru Wall alongside deceased ancestors!",
        "fix_if_wrong": "Use wooden or gold/brass frames in SW/E/N; keep couple photos in the SW of the bedroom/living room, and never hang living family photos next to deceased ancestors or facing a toilet door.",
    },
    "photo_deceased": {
        "label": "Photo Frame: Deceased Ancestors (Pitru / Late Members)",
        "category": "indoor",
        "ideal_zones": ["S", "SW"],
        "acceptable_zones": ["W"],
        "bad_zones": ["NE", "N", "E", "SE", "NW", "Center"],
        "ideal_wall_sides": ["S", "SW"],
        "ideal_door_facing": ["N"],
        "why_simple": "STRICT CLASSICAL VASTU RULE: Photos of deceased ancestors / late family members (Pitru) MUST be hung ONLY on the South Wall (so the photo faces North) or in the South / South-West zone. NEVER place deceased ancestors' photos inside the Temple / Puja Room (NE) or mix them with Gods' photos (causes Pitru-Deva Dosha), and NEVER hang them in a Bedroom, Kitchen, or directly facing the Main Entrance!",
        "fix_if_wrong": "Respectfully move all photos of deceased family members out of the Puja Room / NE / Bedroom and hang them exclusively on a clean South wall in the living/dining hall (facing North), adorned with a sandalwood garland.",
    },
    "photo_gods": {
        "label": "Photo Frame: Gods / Deities / Sacred Yantras",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["W", "Center"],
        "bad_zones": ["S", "SW", "SE", "NW"],
        "ideal_wall_sides": ["E", "N", "NE"],
        "ideal_door_facing": ["W", "S", "E"],
        "why_simple": "Sacred photos of Gods, Deities, and Yantras belong on the North-East, East, or North walls (so the Deity faces West or South, and the person viewing/praying faces East or North). Never hang Gods' photos on a wall shared with a Bathroom/Toilet, at the foot of a bed, under stairs, or on the South wall facing North (and never mix with deceased ancestor photos).",
        "fix_if_wrong": "Relocate Deity frames to the East or North-East wall, choose serene sitting/blessing postures (Shanta Swarupa) for the home, and never hang them on a bathroom wall.",
    },
    "tv_screen": {
        "label": "TV / Television / Home Theater Wall",
        "category": "indoor",
        "ideal_zones": ["SE", "E", "N", "NW"],
        "acceptable_zones": ["S", "W"],
        "bad_zones": ["NE", "SW", "Center"],
        "ideal_wall_sides": ["S", "E", "N"],
        "ideal_door_facing": ["N", "W", "S", "E"],
        "why_simple": "Televisions and large monitors are Fire/Electronic emitters (Agni + Rahu media). They work best in the South-East, East, North, or North-West, mounted on the South or East wall so viewers face South, East, or North. In a Bedroom, a TV screen directly facing the bed acts as a dark Feng Shui mirror reflecting sleeping bodies — causing insomnia, restless dreams, and marital arguments!",
        "fix_if_wrong": "If a TV is in the North-East, keep it switched off when not watching and avoid loud aggressive media; if a TV is in a Bedroom facing the bed, drape a clean fabric cover/runner over the screen before going to sleep.",
    },
    "wall_mirror": {
        "label": "Wall Mirror / Dressing Table Mirror",
        "category": "indoor",
        "ideal_zones": ["N", "E", "NE"],
        "acceptable_zones": ["NW", "W"],
        "bad_zones": ["S", "SW", "SE", "Center"],
        "ideal_wall_sides": ["N", "E"],
        "ideal_door_facing": ["S", "W", "E", "N"],
        "why_simple": "Mirrors represent the Water element and optical expansion. Hanging mirrors on the North or East wall expands Kubera/Surya light, whereas mirrors on the South or South-West wall reflect heavy Mars/Rahu energy back into the room. Never place a mirror directly facing the Bed or directly facing the Main Entrance Door!",
        "fix_if_wrong": "Move mirrors to the North or East wall; if a wardrobe mirror faces the bed and cannot be moved, cover it with an opaque curtain or frosted film at night.",
    },
    "wall_clock": {
        "label": "Wall Clock / Pendulum Clock",
        "category": "indoor",
        "ideal_zones": ["N", "E", "NE"],
        "acceptable_zones": ["W", "NW"],
        "bad_zones": ["S", "SW", "SE"],
        "ideal_wall_sides": ["N", "E", "NE"],
        "why_simple": "Clocks govern the flow of Kaala (Time) and momentum. Hang wall clocks on the North, East, or North-East wall so you look North or East when checking the time. Never hang a clock on the South wall (Yama's direction — stagnates progress), above a doorway, or let a stopped/broken clock remain on any wall!",
        "fix_if_wrong": "Replace batteries immediately if a clock stops, move South-wall clocks to the North or East wall, and favor round or octagonal metallic/wooden frames.",
    },

    # ---------------- OUTDOOR LOT, PERIMETER, DRAINAGE, PLAY & GATES ----------------
    "gate": {
        "label": "Main Property Gate (Compound Entrance)",
        "category": "outdoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["NW", "W"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "ideal_door_facing": ["NE", "E", "N"],
        "why_simple": "The Main Compound Gate governs how cosmic and financial Qi enters the entire land parcel. Gates in North-East, East, or North that swing inward clockwise (or slide open toward North/East) bring protection and prosperity.",
        "fix_if_wrong": "If the property gate is in South or South-West, or swings outward, install bright lamps on both gate pillars, embed a copper rod/strip under the gate sill, and keep the NE gate/corner well-lit.",
    },
    "parking_gate": {
        "label": "Parking / Driveway Gate / Garage Door",
        "category": "outdoor",
        "ideal_zones": ["NW", "SE", "E", "N"],
        "acceptable_zones": ["W"],
        "bad_zones": ["SW", "NE", "Center", "S"],
        "ideal_door_facing": ["N", "E", "NW", "W"],
        "why_simple": "Vehicles represent movement (Vayu/Air) and engine heat (Agni). North-West and South-East are the prime Vastu zones for a driveway gate or garage. If using a sliding gate, sliding open toward North or East is most auspicious.",
        "fix_if_wrong": "Park vehicles facing East or North whenever possible, keep the driveway free of oil stains, and ensure the gate slides/swings smoothly without grinding noise.",
    },
    "side_pedestrian_gate": {
        "label": "Side / Back Yard Gate (Wicket Gate)",
        "category": "outdoor",
        "ideal_zones": ["N", "E", "NE", "NW"],
        "acceptable_zones": ["W", "SE"],
        "bad_zones": ["SW", "S", "Center"],
        "ideal_door_facing": ["N", "E", "NE", "NW"],
        "why_simple": "Secondary pedestrian or garden gates work best on the North, East, North-East, or North-West sides and should always be smaller than the Main Gate and swing inward.",
        "fix_if_wrong": "Keep a South or South-West side gate locked when not in active use and plant dense shrubs inside to prevent Qi leakage.",
    },
    "fence": {
        "label": "Outer Fence / Compound Boundary Wall",
        "category": "outdoor",
        "ideal_zones": ["SW", "S", "W", "N", "E", "NE", "NW", "SE"],
        "acceptable_zones": ["Center"],
        "bad_zones": [],
        "why_simple": "A boundary fence (Prakara) defines and protects the property's energy field (Kshetra). In Vastu & Form School Feng Shui, the South, South-West (Black Tortoise), and West (White Tiger) fences should be solid, slightly higher, and unbroken, while the North, North-East, and East fences should be slightly lower or allow light/air.",
        "fix_if_wrong": "Ensure there are no broken gaps or missing fence panels in the South-West or South; keep the North-East fence clean and painted in a bright tone.",
    },
    "trench_ditch": {
        "label": "Trench / Ditch / Drainage Channel / Pit",
        "category": "outdoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW"],
        "bad_zones": ["SW", "S", "W", "SE", "Center"],
        "why_simple": "CLASSICAL VASTU & FENG SHUI TOPOGRAPHY RULE: A trench, ditch, canal, drainage channel, or ground depression (inside OR outside the property boundary) lowers the earth level of that sector. In North, North-East, or East, a clean trench draining toward NE/E is AUSPICIOUS (Uttara/Ishanya Nimna — attracts wealth). In South, South-West, West, or South-East, a trench or ditch is a SEVERE DEFECT (Nairutya/Dakshina Pallam) that drains wealth, health, and stability!",
        "fix_if_wrong": "Zero-demolition fix for a South, South-West, or West trench/ditch: (1) Cover the trench with heavy concrete/stone slabs so it is not an open pit; (2) Build a solid, slightly taller boundary wall/curb between your house and the SW/S trench; (3) Place 3 heavy yellow earth boulders or a lead/brass Vastu helix along the SW boundary; and (4) Ensure water inside the trench flows toward North or East (never stagnating in SW).",
    },
    "water_hose": {
        "label": "Water Hose / Outdoor Garden Tap / Spigot",
        "category": "outdoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW", "W"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "why_simple": "Outdoor water hoses, garden taps, and sprinkler valves represent active Jala (Water element). They belong in the North-East, North, or East of the yard/exterior wall. A leaking water hose or outdoor tap in the South-West softens the Earth foundation and drains savings; in the South-East it clashes with Agni.",
        "fix_if_wrong": "Keep the outdoor hose neatly coiled on a wall reel (never tangled on the ground like a serpent), fix any dripping spigot washer immediately, and if the tap is in SW/SE, place a terracotta or yellow stone slab beneath the spigot.",
    },
    "kids_slide": {
        "label": "Kids Slide / Swing / Outdoor Play Set",
        "category": "outdoor",
        "ideal_zones": ["W", "NW", "N", "E"],
        "acceptable_zones": ["NE", "SE"],
        "bad_zones": ["SW", "S", "Center"],
        "ideal_door_facing": ["N", "E", "NE"],
        "why_simple": "In Classical Feng Shui, West (Dui Trigram) is the supreme sector of Children & Joy, while in Vastu, North-West (Vayu movement), East (vitality), and West are ideal for children's play equipment. Orient the kids' slide so children slide down facing North or East! Avoid placing tall play structures in the South-West (where kids either get minor falls or become overly stubborn toward parents) or South-East.",
        "fix_if_wrong": "Point the slide chute toward North or East, place soft green turf or rubber safety mats underneath, and keep play sets out of the extreme South-West corner.",
    },
    "overhead_tank": {
        "label": "Overhead Water Tank (Elevated Heavy Tank)",
        "category": "outdoor",
        "ideal_zones": ["SW", "W", "S"],
        "acceptable_zones": ["NW"],
        "bad_zones": ["NE", "N", "E", "SE", "Center"],
        "why_simple": "Unlike underground water (which belongs in NE), an Overhead Water Tank represents massive elevated weight (Earth element) and belongs on the West or South-West roof/tower — never in the North-East or Center!",
        "fix_if_wrong": "Raise the tank on a 1–2 foot platform so there is air space beneath it, paint it white or light beige, and avoid plastic black tanks in the NE.",
    },
    "trees": {
        "label": "Tall / Heavy Shade Trees",
        "category": "outdoor",
        "ideal_zones": ["SW", "S", "W"],
        "acceptable_zones": ["NW", "SE"],
        "bad_zones": ["NE", "N", "E", "Center"],
        "why_simple": "Per Brihat Samhita (Vrikshayurveda), tall, dense trees belong in the South-West, South, and West of the lot where they block harsh afternoon heat and anchor Earth stability. Tall trees in the North-East or East block sacred morning sunlight!",
        "fix_if_wrong": "Trim lower/overhanging branches of any NE/E/N trees so morning sunlight reaches the house unobstructed, and never allow a tree trunk to stand directly in front of the Main Entrance (Vriksha Vedha).",
    },
    "flowers": {
        "label": "Flower Beds / Flowering Plants",
        "category": "outdoor",
        "ideal_zones": ["NE", "E", "N", "NW", "SE"],
        "acceptable_zones": ["W", "S", "SW"],
        "bad_zones": ["Center"],
        "why_simple": "Fragrant and vibrant flowers activate Venus, Mercury, and Jupiter energies. Placing flower beds in the North, East, North-East, or North-West uplifts mental peace, social charm, and positive Prana.",
        "fix_if_wrong": "Remove wilted flowers promptly; use white/yellow/jasmine flowers in NE/E/NW and red/rose/hibiscus flowers in SE/S.",
    },
    "bushes": {
        "label": "Bushes / Ornamental Shrubs",
        "category": "outdoor",
        "ideal_zones": ["NW", "W", "S", "SE", "SW"],
        "acceptable_zones": ["N", "E"],
        "bad_zones": ["NE", "Center"],
        "why_simple": "Medium-height bushes and hedges work wonderfully along the West, North-West, South, and South-East lot borders. Keep the North-East corner free of thorny or dense bushes.",
        "fix_if_wrong": "Never plant thorny cacti or milk-oozing shrubs inside the lot boundary (except roses); keep any bushes in the North or East trimmed below window height.",
    },
    "fireplace": {
        "label": "Outdoor Fireplace / Fire Pit / BBQ",
        "category": "outdoor",
        "ideal_zones": ["SE", "S", "NW"],
        "acceptable_zones": ["E"],
        "bad_zones": ["NE", "N", "SW", "W", "Center"],
        "why_simple": "An outdoor fireplace, fire pit, or BBQ grill is pure Agni (Fire element). Placing it in the South-East (Agneya) or North-West harmonizes with natural elemental laws, whereas a fire pit in the North-East (Water element) creates a severe Water-Fire clash.",
        "fix_if_wrong": "If a fixed fire pit or BBQ is in the North, North-East, or South-West, keep it covered when not in use and place 4 natural yellow jasper / earth stones or terracotta pots around its base to insulate the fire element.",
    },
    "garden": {
        "label": "Garden / Herbal & Vegetable Patch",
        "category": "outdoor",
        "ideal_zones": ["N", "E", "NE", "NW"],
        "acceptable_zones": ["W", "SE", "S", "SW"],
        "bad_zones": ["Center"],
        "why_simple": "The North (ruled by Mercury, planet of greenery) and East (ruled by the life-giving Sun) are the supreme Vastu zones for a lush garden, Tulsi plant, and herbal patch.",
        "fix_if_wrong": "If your garden is in the South or West, use raised wooden or stone planter beds (which adds beneficial Earth elevation in South/West!).",
    },
    "grass": {
        "label": "Grass Lawn / Open Green Turf",
        "category": "outdoor",
        "ideal_zones": ["NE", "N", "E", "NW"],
        "acceptable_zones": ["W", "SE", "S", "SW", "Center"],
        "bad_zones": [],
        "why_simple": "Low, soft green grass in the North, East, and North-East keeps those sacred zones open, cool, and receptive to cosmic and solar energy.",
        "fix_if_wrong": "Keep the lawn well-mowed and ensure rainwater drains gently toward the North-East or East rather than pooling in the South-West.",
    },
    "water_body": {
        "label": "Pool / Fountain / Pond / Borewell",
        "category": "outdoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW"],
        "bad_zones": ["SW", "S", "SE", "W", "Center"],
        "why_simple": "Water elements (fountains, pools, ponds, underground tanks) multiply wealth and peace when placed in the North-East, North, or East — and cause severe Vastu defects if placed in the South-West (Earth) or South-East (Fire).",
        "fix_if_wrong": "If a pool or water feature is in the South, South-West, or South-East, border it with heavy natural rock/stone planters and warm lighting to buffer the water element.",
    },
    "septic_trash": {
        "label": "Septic Tank / Trash Bins / Compost",
        "category": "outdoor",
        "ideal_zones": ["NW", "W"],
        "acceptable_zones": ["S", "SE"],
        "bad_zones": ["NE", "N", "E", "SW", "Center"],
        "why_simple": "Trash bins, compost, and septic tanks must be kept in the North-West (Vayavya elimination zone) or West — never in the sacred North-East, East, North, or South-West.",
        "fix_if_wrong": "Move portable trash bins immediately to the North-West or West side of the yard and keep them lidded and screened behind a wooden/green divider.",
    },
}


def build_personalized_chart_preset(
    pos: Optional[Dict[str, Any]] = None,
    asc_lon: Optional[float] = None,
) -> Dict[str, Any]:
    """Builds a complete, chart-calibrated Ideal Vastu & Feng Shui layout preset
    including rooms, temple, meditation, medication, gym, storage, washer/dryer,
    kitchen stove, taps, water hose, kids slide, NE drainage trench, gates with
    clockwise/sliding mechanics, photo frames (living, deceased, gods), TV wall,
    interior walls, and a perimeter fence loop."""
    lagna_idx = int(asc_lon // 30) % 12 if asc_lon is not None else 0
    lagna_sign = SIGNS[lagna_idx]
    lagna_lord = SIGN_LORDS[lagna_idx]
    h4_lord = SIGN_LORDS[(lagna_idx + 3) % 12]
    h9_lord = SIGN_LORDS[(lagna_idx + 8) % 12]

    # Calibrate primary entrance / gate facing based on Lagna/9th/4th auspiciousness
    best_door = "NE" if lagna_lord in ("Jupiter", "Sun", "Mars") else ("N" if lagna_lord in ("Mercury", "Venus", "Saturn") else "E")

    items = [
        # Sacred, Entrance & Healing (NE / N / E)
        {"id": 1,  "type": "entrance",           "label": f"Main Entrance ({best_door} Simhadwara)", "x": 66, "y": 16, "w": 13, "h": 6,  "door_dir": best_door, "gate_mech": "swing_in_cw", "wall_side": "NE", "scope": "indoor"},
        {"id": 2,  "type": "puja_room",          "label": "Temple / Prayer Hall (Ishanya)",          "x": 70, "y": 23, "w": 12, "h": 10, "door_dir": "E",       "gate_mech": "double_in",   "wall_side": "NE", "scope": "indoor"},
        {"id": 3,  "type": "photo_gods",         "label": "Gods / Deities Frame (NE East Wall)",     "x": 73, "y": 34, "w": 9,  "h": 6,  "door_dir": "W",       "gate_mech": "",            "wall_side": "E",  "scope": "indoor"},
        {"id": 4,  "type": "meditation_hall",    "label": "Meditation & Yoga Space",                 "x": 57, "y": 23, "w": 12, "h": 10, "door_dir": "NE",      "gate_mech": "",            "wall_side": "NE", "scope": "indoor"},
        {"id": 5,  "type": "medication_cabinet", "label": "Medication / First-Aid (NNE Dhanvantari)","x": 56, "y": 16, "w": 9,  "h": 6,  "door_dir": "N",       "gate_mech": "",            "wall_side": "N",  "scope": "indoor"},
        {"id": 6,  "type": "living_room",        "label": f"Living Room ({lagna_sign} Lagna Lounge)","x": 38, "y": 17, "w": 17, "h": 15, "door_dir": "N",       "gate_mech": "",            "wall_side": "N",  "scope": "indoor"},
        {"id": 7,  "type": "tv_screen",          "label": "TV Wall (Living East Wall)",              "x": 72, "y": 42, "w": 10, "h": 6,  "door_dir": "W",       "gate_mech": "",            "wall_side": "E",  "scope": "indoor"},
        {"id": 8,  "type": "indoor_taps",        "label": "Kitchen Sink & Water Taps (NE/E)",        "x": 73, "y": 55, "w": 9,  "h": 6,  "door_dir": "N",       "gate_mech": "",            "wall_side": "E",  "scope": "indoor"},
        # Fire / Kitchen / Appliances (SE)
        {"id": 9,  "type": "kitchen",            "label": "Kitchen (SE Agneya)",                     "x": 63, "y": 62, "w": 19, "h": 18, "door_dir": "N",       "gate_mech": "swing_in_cw", "wall_side": "SE", "scope": "indoor"},
        {"id": 10, "type": "kitchen_stove",      "label": "Kitchen Stove (SE — Cook Faces East)",    "x": 71, "y": 71, "w": 10, "h": 7,  "door_dir": "E",       "gate_mech": "",            "wall_side": "E",  "scope": "indoor"},
        # Master Stability, Safe, Storage, Gym & Ancestor Frame (SW / S / W)
        {"id": 11, "type": "master_bedroom",     "label": f"Master Bedroom (SW — {h4_lord} Peace)",  "x": 18, "y": 62, "w": 21, "h": 19, "door_dir": "N",       "gate_mech": "swing_in_cw", "wall_side": "SW", "scope": "indoor"},
        {"id": 12, "type": "photo_living",       "label": "Living Family / Couple Frame (SW)",       "x": 20, "y": 74, "w": 10, "h": 5,  "door_dir": "N",       "gate_mech": "",            "wall_side": "SW", "scope": "indoor"},
        {"id": 13, "type": "safe_locker",        "label": f"Cash Safe / Tijori (Opens North)",       "x": 40, "y": 72, "w": 9,  "h": 8,  "door_dir": "N",       "gate_mech": "swing_in_cw", "wall_side": "S",  "scope": "indoor"},
        {"id": 14, "type": "photo_deceased",     "label": "Deceased Ancestors Frame (South Wall → N)","x": 50, "y": 74, "w": 11, "h": 6, "door_dir": "N",       "gate_mech": "",            "wall_side": "S",  "scope": "indoor"},
        {"id": 15, "type": "gym_room",           "label": "Home Gym & Weights (South Mars Zone)",    "x": 46, "y": 61, "w": 15, "h": 11, "door_dir": "N",       "gate_mech": "",            "wall_side": "S",  "scope": "indoor"},
        {"id": 16, "type": "storage",            "label": "Heavy Storage Room (West Saturn)",        "x": 18, "y": 48, "w": 12, "h": 12, "door_dir": "E",       "gate_mech": "",            "wall_side": "W",  "scope": "indoor"},
        {"id": 17, "type": "dining_room",        "label": "Dining Hall (West Nourishment)",          "x": 31, "y": 46, "w": 14, "h": 13, "door_dir": "E",       "gate_mech": "",            "wall_side": "W",  "scope": "indoor"},
        {"id": 18, "type": "study_room",         "label": f"Study / Office ({h9_lord} Focus)",       "x": 60, "y": 43, "w": 11, "h": 11, "door_dir": "NE",      "gate_mech": "",            "wall_side": "E",  "scope": "indoor"},
        # Air / Movement / Laundry / Bathroom / Guest (NW)
        {"id": 19, "type": "washer_dryer",       "label": "Washer & Dryer (NW Vayavya)",             "x": 18, "y": 33, "w": 11, "h": 9,  "door_dir": "E",       "gate_mech": "",            "wall_side": "NW", "scope": "indoor"},
        {"id": 20, "type": "bathroom",           "label": "Bathroom / WC (NW)",                      "x": 30, "y": 33, "w": 10, "h": 10, "door_dir": "E",       "gate_mech": "swing_in_cw", "wall_side": "NW", "scope": "indoor"},
        {"id": 21, "type": "guest_room",         "label": "Guest Bedroom (NW)",                      "x": 18, "y": 17, "w": 15, "h": 14, "door_dir": "E",       "gate_mech": "swing_in_cw", "wall_side": "NW", "scope": "indoor"},
        # Outdoor Lot, Gates, Sliding Gate, Water Hose, Kids Slide, Trench & Trees
        {"id": 22, "type": "gate",               "label": "Main Compound Gate (Inward Clockwise)",   "x": 65, "y": 2,  "w": 15, "h": 6,  "door_dir": best_door, "gate_mech": "swing_in_cw", "wall_side": "N",  "scope": "outdoor"},
        {"id": 23, "type": "parking_gate",       "label": "Driveway Sliding Gate (Slides → East)",   "x": 16, "y": 2,  "w": 18, "h": 6,  "door_dir": "N",       "gate_mech": "slide_ne",    "wall_side": "NW", "scope": "outdoor"},
        {"id": 24, "type": "water_hose",         "label": "Garden Water Hose & Tap (NE)",            "x": 85, "y": 14, "w": 11, "h": 7,  "door_dir": "NE",      "gate_mech": "",            "wall_side": "NE", "scope": "outdoor"},
        {"id": 25, "type": "trench_ditch",       "label": "NE Drainage Trench (Flows W→NE)",         "x": 83, "y": 3,  "w": 14, "h": 6,  "door_dir": "NE",      "flow_dir": "NE",           "wall_side": "NE", "scope": "outdoor"},
        {"id": 26, "type": "kids_slide",         "label": "Kids Slide & Play Set (Chute → N)",       "x": 3,  "y": 42, "w": 11, "h": 14, "door_dir": "N",       "gate_mech": "",            "wall_side": "W",  "scope": "outdoor"},
        {"id": 27, "type": "trees",              "label": "SW Heavy Shade Trees",                    "x": 3,  "y": 78, "w": 12, "h": 16, "door_dir": "",        "gate_mech": "",            "wall_side": "SW", "scope": "outdoor"},
        {"id": 28, "type": "garden",             "label": "North Herbal & Tulsi Garden",             "x": 38, "y": 3,  "w": 22, "h": 7,  "door_dir": "N",       "gate_mech": "",            "wall_side": "N",  "scope": "outdoor"},
        {"id": 29, "type": "fireplace",          "label": "SE Outdoor Fire Pit / BBQ",               "x": 85, "y": 78, "w": 11, "h": 12, "door_dir": "E",       "gate_mech": "",            "wall_side": "SE", "scope": "outdoor"},
    ]

    walls = [
        {"id": 201, "x1": 16, "y1": 45, "x2": 39, "y2": 45, "wall_type": "partition", "label": "West Interior Partition Wall"},
        {"id": 202, "x1": 39, "y1": 60, "x2": 84, "y2": 60, "wall_type": "load_bearing", "label": "South-West / South-East Thick Wall"},
        {"id": 203, "x1": 62, "y1": 60, "x2": 62, "y2": 84, "wall_type": "partition", "label": "Kitchen Partition Wall"},
    ]

    fences = [
        {
            "id": 301,
            "label": "Property Perimeter Fence (Closed Loop with NE/NW Gate Openings)",
            "closed": True,
            "open_side": "NONE",
            "points": [
                {"x": 2, "y": 2},
                {"x": 98, "y": 2},
                {"x": 98, "y": 98},
                {"x": 2, "y": 98},
            ],
        }
    ]

    return {
        "preset_title": f"Personalized Ideal Layout for {lagna_sign} Ascendant ({lagna_lord}) & Home Lord {h4_lord}",
        "items": items,
        "walls": walls,
        "fences": fences,
    }


def _coord_to_zone(cx: float, cy: float, compass_deg: float = 0.0) -> str:
    """Given normalized center coordinates (cx, cy) in [0..100] where (50, 50) is
    the center of the house/lot and top (y=0) is North when compass_deg=0,
    returns the Vastu zone: 'Center', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'."""
    dx = cx - 50.0
    dy = cy - 50.0
    dist = math.hypot(dx, dy)
    if dist < 11.5:
        return "Center"

    angle_cw_from_top = (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0
    rel_angle = (angle_cw_from_top - compass_deg + 360.0) % 360.0
    sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int(((rel_angle + 22.5) % 360.0) // 45.0)
    return sectors[idx]


def _point_to_segment_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def evaluate_visual_vastu_layout(
    items: List[Dict[str, Any]],
    house_shape: str = "square",
    has_outer_lot: bool = True,
    compass_rotation: float = 0.0,
    pos: Optional[Dict[str, Any]] = None,
    asc_lon: Optional[float] = None,
    walls: Optional[List[Dict[str, Any]]] = None,
    fences: Optional[List[Dict[str, Any]]] = None,
    palm_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluates a complete visual House + Outer-Lot Vastu & Feng Shui diagram with:
    - All 45+ indoor rooms, appliances (washer/dryer, stove, taps), sacred spaces (temple, meditation, medication),
      photo frames (living, deceased, gods), TV wall, and outdoor features (trench, water hose, kids slide, gates)
    - Gate & door opening mechanisms (swing inward clockwise/counter-clockwise, outward, double-leaf, sliding N/E vs S/W)
    - Trench / ditch inside vs outside property & water flow slope direction
    - Custom drawn wall lines (checking Brahmasthan center cut & SW vs NE wall density)
    - Continuous perimeter fence loops (closed loop vs open loop directionality)
    - Cross-item relational Vastu & Feng Shui diagnostics."""
    shape_info = {
        "square": {
            "name": "Square Footprint (Chaturasra — Classical 1:1 Proportion)",
            "vastu_rating": "Supreme (100/100)",
            "explanation": "In Mayamata and Manasara Vastu Shastra, the Square (Chaturasra) is the most balanced geometric form because all 8 directional energies and the central Brahmasthan distribute symmetrically.",
        },
        "wide_rectangle": {
            "name": "Wide Rectangle Footprint (Ayatasra — East-West Extended)",
            "vastu_rating": "Auspicious (92/100 — keep length:width ratio within 1:1.5)",
            "explanation": "A rectangular house or lot is highly auspicious in Vastu provided its corners are 90° and the North/East sides remain well-lit and unobstructed.",
        },
        "deep_rectangle": {
            "name": "Deep Rectangle Footprint (Ayatasra — North-South Extended)",
            "vastu_rating": "Very Good (94/100 — Classical North-South Axis Alignment)",
            "explanation": "A rectangle aligned along the North-South magnetic axis channels Earth's geomagnetic flow smoothly from North to South.",
        },
    }.get(house_shape, {
        "name": "Custom Rectangular Footprint",
        "vastu_rating": "Good (90/100)",
        "explanation": "Maintain clean 90° corners and keep the center (Brahmasthan) clutter-free.",
    })

    lagna_idx = int(asc_lon // 30) % 12 if asc_lon is not None else None
    lagna_lord = SIGN_LORDS[lagna_idx] if lagna_idx is not None else None
    h9_lord = SIGN_LORDS[(lagna_idx + 8) % 12] if lagna_idx is not None else None

    evaluated_items: List[Dict[str, Any]] = []
    total_pts = 0
    max_pts = 0
    critical_doshas: List[str] = []
    auspicious_highlights: List[str] = []

    # Track placed items by type for relational cross-checks
    by_type: Dict[str, List[Dict[str, Any]]] = {}

    for idx, raw in enumerate(items, start=1):
        itype = str(raw.get("type", "living_room")).lower()
        rule = ITEM_RULES.get(itype, ITEM_RULES["living_room"])
        custom_label = raw.get("label") or rule["label"]
        cx = float(raw.get("x", 50.0)) + float(raw.get("w", 12.0)) / 2.0
        cy = float(raw.get("y", 50.0)) + float(raw.get("h", 12.0)) / 2.0
        door_dir = str(raw.get("door_dir") or "").upper()
        gate_mech = str(raw.get("gate_mech") or "").lower()
        wall_side = str(raw.get("wall_side") or "").upper()
        flow_dir = str(raw.get("flow_dir") or "").upper()
        area_scope = raw.get("scope") or rule["category"]  # 'indoor', 'outdoor', or 'outside_boundary'

        zone = _coord_to_zone(cx, cy, compass_rotation)
        zone_meta = DIRECTION_META[zone]
        zone_planet = zone_meta["planet"]

        by_type.setdefault(itype, []).append({
            "label": custom_label, "zone": zone, "cx": cx, "cy": cy,
            "door_dir": door_dir, "wall_side": wall_side, "gate_mech": gate_mech,
            "flow_dir": flow_dir, "scope": area_scope,
        })

        # 1. Base Zone Score (out of 10)
        if zone in rule["ideal_zones"]:
            pts = 10
            status = "IDEAL / AUSPICIOUS"
            badge_color = "good"
            verdict_summary = f"Excellent! {custom_label} in the {zone_meta['name']} harmonizes with {zone_meta['element']} and {zone_planet}."
        elif zone in rule["acceptable_zones"]:
            pts = 7
            status = "ACCEPTABLE / BALANCED"
            badge_color = "neutral"
            verdict_summary = f"Balanced placement: {custom_label} in {zone_meta['name']} works well with minor elemental support."
        else:
            pts = 3
            status = "VASTU DOSHA (NEEDS REMEDY)"
            badge_color = "bad"
            verdict_summary = (
                f"Elemental Clash: {custom_label} is placed in {zone_meta['name']} ({zone_meta['element']}), "
                f"whereas it belongs in {', '.join(rule['ideal_zones'])}."
            )

        # 2. Door / Facing Direction Check
        extra_notes: List[str] = []
        if door_dir and "ideal_door_facing" in rule:
            if door_dir in rule["ideal_door_facing"]:
                pts = min(10, pts + 1)
                extra_notes.append(f"Facing {door_dir} is highly auspicious.")
            elif door_dir in ("SW", "S") and itype not in ("photo_deceased", "wall_mirror"):
                pts = max(2, pts - 2)
                if status == "IDEAL / AUSPICIOUS":
                    status = "ACCEPTABLE (CHECK FACING DIRECTION)"
                    badge_color = "neutral"
                extra_notes.append(f"Facing {door_dir} needs a threshold copper strip / bright lamp.")
            else:
                extra_notes.append(f"Facing {door_dir} is balanced.")

        # 3. Gate / Door Swing & Sliding Mechanism Check
        mech_label = ""
        if gate_mech and gate_mech in GATE_MECHANISM_RULES:
            m_rule = GATE_MECHANISM_RULES[gate_mech]
            mech_label = m_rule["label"]
            pts = max(1, min(10, pts + m_rule["score_delta"]))
            extra_notes.append(m_rule["verdict"])
            if m_rule["score_delta"] < 0:
                if badge_color == "good":
                    badge_color = "neutral"
                    status = "CHECK GATE/DOOR OPENING MECHANISM"
                critical_doshas.append(f"{custom_label} ({m_rule['label']}): {m_rule['remedy']}")

        # 4. Wall Side Check (for Photo Frames, TV, Mirror, Clock, Taps)
        if wall_side:
            w_lbl = WALL_SIDE_LABELS.get(wall_side, f"{wall_side} Wall")
            if "ideal_wall_sides" in rule:
                if wall_side in rule["ideal_wall_sides"]:
                    extra_notes.append(f"Mounted on {w_lbl} — ideal wall alignment!")
                else:
                    pts = max(2, pts - 2)
                    if badge_color == "good":
                        badge_color = "neutral"
                        status = "WALL ORIENTATION NEEDS ADJUSTMENT"
                    extra_notes.append(
                        f"Mounted on {w_lbl}, whereas classical Vastu recommends mounting on {', '.join(rule['ideal_wall_sides'])} wall."
                    )
            else:
                extra_notes.append(f"Wall: {w_lbl}.")

        # 5. Special Trench / Ditch Inside vs Outside Property & Flow Check
        if itype == "trench_ditch":
            loc_str = "Outside Property Boundary" if area_scope == "outside_boundary" else ("Inside House" if area_scope == "indoor" else "Inside Property Yard")
            extra_notes.append(f"Trench Location: {loc_str}.")
            if flow_dir:
                if flow_dir in ("NE", "E", "N"):
                    pts = min(10, pts + 1)
                    extra_notes.append(f"Drainage/Slope flows toward {flow_dir} (Auspicious Pradakshina water flow!).")
                elif flow_dir in ("SW", "S", "W", "STAGNANT"):
                    pts = max(1, pts - 3)
                    badge_color = "bad"
                    status = "TRENCH DRAINAGE DOSHA"
                    extra_notes.append(f"WARNING: Trench water drains/stagnates toward {flow_dir}, which drains wealth and stability!")
                    critical_doshas.append(
                        f"{custom_label} ({loc_str} in {zone} draining toward {flow_dir}): Re-grade or channel drainage toward North-East/East and cover SW/S trench segments with heavy stone slabs."
                    )

        # Birth Chart Synergy Note
        chart_synergy = ""
        if pos and lagna_idx is not None:
            p_lon = pos[zone_planet]["longitude"]
            p_house = (int(p_lon // 30) % 12 - lagna_idx) % 12 + 1
            if zone_planet in (lagna_lord, h9_lord):
                chart_synergy = (
                    f"Birth-Chart Double Boost: This {zone} sector is ruled by {zone_planet} (your natal "
                    f"{'Ascendant' if zone_planet == lagna_lord else '9th Luck'} Lord in House {p_house}) — "
                    f"keeping this {custom_label} harmonious directly amplifies your personal luck!"
                )
            else:
                chart_synergy = (
                    f"Birth-Chart Link: {zone} is governed by {zone_planet} (placed in House {p_house} of your birth chart)."
                )

        detail_suffix = (" " + " ".join(extra_notes)) if extra_notes else ""
        if pts >= 9:
            auspicious_highlights.append(f"{custom_label} in {zone} ({zone_meta['name']}){detail_suffix}")
        elif pts <= 4:
            critical_doshas.append(f"{custom_label} in {zone}: {rule['fix_if_wrong']}")

        total_pts += pts
        max_pts += 10

        fs_bagua = FENG_SHUI_BAGUA_SECTORS.get(zone, FENG_SHUI_BAGUA_SECTORS["Center"])
        fs_note = (
            f"Feng Shui Bagua ({fs_bagua['trigram']} · {fs_bagua['life_area']} · {fs_bagua['element']}): "
            f"{fs_bagua['enhancer']}"
        )

        scope_display = (
            "Outside Property Boundary" if area_scope == "outside_boundary"
            else ("Outer Lot / Yard" if area_scope == "outdoor" else "Inside House")
        )
        door_display_parts = []
        if door_dir:
            door_display_parts.append(f"Faces {door_dir}")
        if mech_label:
            door_display_parts.append(mech_label)
        if wall_side:
            door_display_parts.append(f"On {wall_side} Wall")
        if flow_dir:
            door_display_parts.append(f"Flows → {flow_dir}")
        door_display = " · ".join(door_display_parts) if door_display_parts else "N/A"

        evaluated_items.append({
            "index": idx,
            "type": itype,
            "label": custom_label,
            "scope": scope_display,
            "detected_zone": zone,
            "zone_full_name": zone_meta["name"],
            "zone_planet_and_element": f"{zone_planet} | {zone_meta['element']} | Feng Shui: {fs_bagua['element']} ({fs_bagua['life_area']})",
            "door_or_gate_facing": door_display,
            "score_out_of_10": pts,
            "status": status,
            "badge_color": badge_color,
            "verdict_in_simple_words": verdict_summary + detail_suffix,
            "why_this_rule_exists": rule["why_simple"],
            "ideal_zones_for_this_item": rule["ideal_zones"],
            "birth_chart_synergy": chart_synergy,
            "feng_shui_bagua_harmony": fs_note,
            "zero_demolition_remedy": "No remedy needed — keep clean, bright, and clutter-free!" if pts >= 9 else rule["fix_if_wrong"],
        })

    # -----------------------------------------------------------------------
    # 6. RELATIONAL CROSS-ITEM CHECKS (Stove vs Taps, Photos, TV in Bedroom)
    # -----------------------------------------------------------------------
    relational_findings: List[Dict[str, str]] = []

    # Check 6A: Kitchen Stove vs Indoor Taps / Sink proximity (Fire-Water Sha Qi)
    for st in by_type.get("kitchen_stove", []):
        for tp in by_type.get("indoor_taps", []):
            dist = math.hypot(st["cx"] - tp["cx"], st["cy"] - tp["cy"])
            if dist < 14.0:
                msg = (
                    f"🔥💧 Fire-Water Clash Detected: '{st['label']}' and '{tp['label']}' are placed very close together ({round(dist, 1)}% span). "
                    "In both Vastu and Classical Feng Shui, a stove touching or facing a water sink causes digestive & marital friction. "
                    "Fix: Place a green herb plant, wooden cutting board, or green crystal between the stove and taps."
                )
                critical_doshas.append(msg)
                relational_findings.append({"type": "warning", "title": "Stove vs. Water Taps Clash", "detail": msg})

    # Check 6B: Deceased Ancestors Photo mixed with Gods Photo or Puja Room
    for dec in by_type.get("photo_deceased", []):
        for sacred in (by_type.get("puja_room", []) + by_type.get("photo_gods", [])):
            if dec["zone"] == sacred["zone"] or math.hypot(dec["cx"] - sacred["cx"], dec["cy"] - sacred["cy"]) < 18.0:
                msg = (
                    f"🖼️⚠️ Pitru-Deva Photo Clash: '{dec['label']}' is placed in the same zone ({dec['zone']}) or near '{sacred['label']}'. "
                    "Classical Vastu strictly forbids keeping deceased ancestors' photos in the Puja altar or alongside Gods' photos. "
                    "Fix: Hang deceased ancestors' photos exclusively on the South wall (facing North) in the living/dining hall."
                )
                critical_doshas.append(msg)
                relational_findings.append({"type": "warning", "title": "Deceased Ancestors vs. Gods Photo Clash", "detail": msg})

    # Check 6C: Living Family Photo alongside Deceased Ancestors Photo
    for liv in by_type.get("photo_living", []):
        for dec in by_type.get("photo_deceased", []):
            if liv["zone"] == dec["zone"] and (not liv["wall_side"] or liv["wall_side"] == dec["wall_side"]):
                msg = (
                    f"🖼️⚠️ Living vs. Deceased Photo Rule: '{liv['label']}' and '{dec['label']}' are in the same {liv['zone']} sector/wall. "
                    "Never hang photos of living family members on the same wall alongside deceased ancestors. "
                    "Fix: Move living family photos to the South-West, West, East, or North wall."
                )
                critical_doshas.append(msg)
                relational_findings.append({"type": "warning", "title": "Living vs. Deceased Family Photo Separation", "detail": msg})

    # Check 6D: TV Screen or Wall Mirror inside Bedroom facing Bed
    for bed in (by_type.get("master_bedroom", []) + by_type.get("bedroom", [])):
        for refl in (by_type.get("tv_screen", []) + by_type.get("wall_mirror", [])):
            if math.hypot(bed["cx"] - refl["cx"], bed["cy"] - refl["cy"]) < 18.0:
                msg = (
                    f"📺🛏️ Bedroom Dark-Mirror Warning: '{refl['label']}' is inside or adjacent to '{bed['label']}'. "
                    "In Vastu & Feng Shui, a TV screen or mirror reflecting the sleeping body drains vitality and disturbs marital harmony. "
                    "Fix: Cover the TV screen or mirror with a cloth runner before sleeping, or mount it on a side wall that does not reflect the bed."
                )
                relational_findings.append({"type": "caution", "title": "TV / Mirror Near Bed Check", "detail": msg})

    # -----------------------------------------------------------------------
    # 7. DRAWN WALL LINES EVALUATION (Brahmasthan Cut & SW vs NE Density)
    # -----------------------------------------------------------------------
    wall_evaluations: List[Dict[str, Any]] = []
    sw_wall_len = 0.0
    ne_wall_len = 0.0
    for w_idx, w in enumerate(walls or [], start=1):
        x1, y1 = float(w.get("x1", 20)), float(w.get("y1", 20))
        x2, y2 = float(w.get("x2", 40)), float(w.get("y2", 20))
        w_type = str(w.get("wall_type") or "partition")
        w_label = w.get("label") or f"Wall Line #{w_idx}"
        seg_len = round(math.hypot(x2 - x1, y2 - y1), 1)
        mid_zone = _coord_to_zone((x1 + x2) / 2.0, (y1 + y2) / 2.0, compass_rotation)
        dist_center = _point_to_segment_dist(50.0, 50.0, x1, y1, x2, y2)

        if mid_zone in ("SW", "S", "W"):
            sw_wall_len += seg_len * (1.5 if w_type == "load_bearing" else 1.0)
        elif mid_zone in ("NE", "N", "E"):
            ne_wall_len += seg_len

        if dist_center < 8.5:
            w_status = "BRAHMASTHAN WALL DOSHA"
            w_badge = "bad"
            w_advice = (
                f"{w_label} cuts directly through the central Brahmasthan / Tai Qi heart of the house! "
                "A wall bisecting the exact center blocks pranic circulation and causes spine/digestive pressure. "
                "Zero-demolition fix: Paint this central wall pure white/ivory, hang a bright warm light or nature tapestry on it, "
                "and place 2 brass Vastu pyramids at the base of the wall."
            )
            critical_doshas.append(w_advice)
            total_pts += 3
        else:
            w_status = "HARMONIOUS PARTITION"
            w_badge = "good"
            w_advice = (
                f"{w_label} ({w_type.replace('_', ' ')}, length {seg_len}%) in {mid_zone} zone respects the open Brahmasthan center."
            )
            total_pts += 9
        max_pts += 10

        wall_evaluations.append({
            "index": w_idx,
            "label": w_label,
            "wall_type": w_type,
            "zone": mid_zone,
            "length_percent": seg_len,
            "cuts_brahmasthan": dist_center < 8.5,
            "status": w_status,
            "badge_color": w_badge,
            "advice": w_advice,
        })

    # -----------------------------------------------------------------------
    # 8. PERIMETER FENCE LOOPS EVALUATION (Closed vs Open Loop)
    # -----------------------------------------------------------------------
    fence_evaluations: List[Dict[str, Any]] = []
    for f_idx, fn in enumerate(fences or [], start=1):
        pts_list = fn.get("points") or []
        is_closed = bool(fn.get("closed", True))
        open_side = str(fn.get("open_side") or ("NONE" if is_closed else "NE")).upper()
        f_label = fn.get("label") or f"Perimeter Fence #{f_idx}"

        if is_closed:
            f_status = "CLOSED LOOP PERIMETER (PROTECTED KSHETRA)"
            f_badge = "good"
            f_advice = (
                f"{f_label}: Complete Closed-Loop Fence around the property creates a sealed, auspicious Vastu Kshetra & Feng Shui guardian boundary. "
                "Ensure the South-West and South fence segments are solid and slightly taller, while keeping the North-East and East segments lighter/airy with an inward-opening Gate."
            )
            auspicious_highlights.append(f"{f_label} (Closed Loop Perimeter Protection)")
            total_pts += 10
        else:
            if open_side in ("NE", "N", "E"):
                f_status = f"OPEN LOOP FENCE (OPEN TOWARD {open_side} — AUSPICIOUS PRANA MUKHA)"
                f_badge = "good"
                f_advice = (
                    f"{f_label}: Open-Loop Fence enclosed on the heavy back/sides and open toward {open_side}. "
                    f"In Vastu & Form School Feng Shui, an open {open_side} front (Red Phoenix / Solar opening) with solid SW/S/W backing (Black Tortoise support) is highly auspicious!"
                )
                auspicious_highlights.append(f"{f_label} (Open Loop facing auspicious {open_side})")
                total_pts += 9
            elif open_side in ("SW", "S"):
                f_status = f"OPEN LOOP FENCE WARNING (UNPROTECTED {open_side} BOUNDARY)"
                f_badge = "bad"
                f_advice = (
                    f"{f_label}: Open-Loop Fence is left open on the {open_side} side! "
                    "In both Vastu (Nairutya Prakara Dosha) and Feng Shui (missing Black Tortoise backing), leaving the South or South-West boundary unfenced while fencing the North/East leaks wealth and stability. "
                    "Fix: Close the fence loop along the South/South-West or plant a dense row of tall trees/shrubs along the SW boundary."
                )
                critical_doshas.append(f_advice)
                total_pts += 3
            else:
                f_status = f"OPEN LOOP FENCE (OPEN ON {open_side})"
                f_badge = "neutral"
                f_advice = (
                    f"{f_label}: Open-Loop Fence with opening toward {open_side} ({len(pts_list)} vertices). "
                    "Keep the South-West corner of the fence solidly anchored and well-defined."
                )
                total_pts += 7
        max_pts += 10

        fence_evaluations.append({
            "index": f_idx,
            "label": f_label,
            "loop_type": "Closed Loop (360° Enclosure)" if is_closed else f"Open Loop (Open on {open_side})",
            "closed": is_closed,
            "open_side": open_side,
            "vertex_count": len(pts_list),
            "status": f_status,
            "badge_color": f_badge,
            "advice": f_advice,
        })

    overall_score = round((total_pts / max_pts) * 100) if max_pts > 0 else 85
    if overall_score >= 82:
        overall_grade = "A+ (Vastu & Feng Shui Siddha — High-Energy Prosperous Layout)"
    elif overall_score >= 68:
        overall_grade = "B+ (Harmonious Layout — Apply Simple Remedies to Reach 95%+)"
    else:
        overall_grade = "C (Multiple Elemental Clashes — Apply the Zero-Demolition Remedies Below)"

    # -----------------------------------------------------------------------
    # 5. PALM + BIRTH CHART + VASTU & FENG SHUI TRI-SYNTHESIS
    # -----------------------------------------------------------------------
    palm_vastu_chart_synthesis: Optional[Dict[str, Any]] = None
    if palm_data and isinstance(palm_data, dict):
        h_shape = str(palm_data.get("hand_shape") or "fire").lower()
        l_life = str(palm_data.get("life_line") or "deep").lower()
        l_head = str(palm_data.get("head_line") or "long").lower()
        l_heart = str(palm_data.get("heart_line") or "curved").lower()
        l_fate = str(palm_data.get("fate_line") or "clear").lower()
        t_type = str(palm_data.get("thumbprint_type") or "chakra_whorl").lower()
        t_name = str(palm_data.get("thumbprint_name") or t_type.replace("_", " ").title())
        has_photo = bool(palm_data.get("has_uploaded_photo"))

        lagna_sign = SIGNS[lagna_idx] if lagna_idx is not None else "Aries"
        h4_lord_name = SIGN_LORDS[(lagna_idx + 3) % 12] if lagna_idx is not None else "Moon"
        h9_lord_name = h9_lord or "Jupiter"

        placed_zones_by_type = {k: [x["zone"] for x in v] for k, v in by_type.items()}
        puja_zones = placed_zones_by_type.get("puja_room", []) + placed_zones_by_type.get("meditation_hall", [])
        med_zones = placed_zones_by_type.get("medication_cabinet", [])
        stove_zones = placed_zones_by_type.get("kitchen_stove", []) + placed_zones_by_type.get("kitchen", [])
        bed_zones = placed_zones_by_type.get("master_bedroom", [])
        safe_zones = placed_zones_by_type.get("safe_locker", [])
        gate_zones = placed_zones_by_type.get("entrance", []) + placed_zones_by_type.get("gate", [])

        tri_checks = [
            {
                "palm_feature": f"Hand Element: {h_shape.title()} Hand" + (" (Uploaded Photo Verified)" if has_photo else ""),
                "birth_chart_factor": f"Ascendant: {lagna_sign} (Lord: {lagna_lord or 'Mars'}) · 4th Home Lord: {h4_lord_name}",
                "floorplan_alignment_status": (
                    "Harmonized" if (("SE" in stove_zones and "NE" in puja_zones) if h_shape == "fire" else ("SW" in bed_zones)) else "Needs Elemental Balancing"
                ),
                "combined_palm_chart_vastu_insight": {
                    "fire": f"Your {h_shape.title()} Palm (strong Sun/Mars mount) + {lagna_sign} Ascendant generates high Agni drive. Your floorplan's Kitchen/Stove in {', '.join(stove_zones) or 'unplaced'} and Temple/Meditation in {', '.join(puja_zones) or 'unplaced'} directly regulate your Pitta thermal balance.",
                    "earth": f"Your {h_shape.title()} Palm (strong Saturn/Venus mount) + {lagna_sign} Ascendant seeks grounded permanence. Anchoring your Master Bedroom in {', '.join(bed_zones) or 'SW'} and maintaining a 360° Closed-Loop Fence locks in your earthly stability.",
                    "air": f"Your {h_shape.title()} Palm (Mercury/Jupiter intellectual current) + {lagna_sign} Ascendant needs Vata grounding. Sleeping in {', '.join(bed_zones) or 'SW'} with head South and keeping the central Brahmasthan open calms mental overdrive.",
                    "water": f"Your {h_shape.title()} Palm (Moon/Venus intuitive sensitivity) + {lagna_sign} Ascendant is highly sensitive to water flow. Ensure all Water Taps, Garden Hose, and Trenches drain toward North-East and never stagnate in South-West.",
                }.get(h_shape, f"Your {h_shape.title()} Palm and {lagna_sign} Ascendant work together through the NE–SW axis."),
                "actionable_remedy": "Massage the center of your palm (Brahmasthan / Plain of Mars) with a drop of sandalwood or sesame oil before sleep and keep the house center clutter-free.",
            },
            {
                "palm_feature": f"Life Line ({l_life.title()}) & Mount of Mars / Venus",
                "birth_chart_factor": f"Lagna Lord {lagna_lord or 'Mars'} & 8th House Vitality",
                "floorplan_alignment_status": (
                    "Optimal Healing Zone" if any(z in ("NE", "N", "E") for z in med_zones) else "Place Medicine Cabinet in NE/N"
                ),
                "combined_palm_chart_vastu_insight": (
                    f"Your {l_life.title()} Life Line governs physical immunity and cellular recovery. "
                    f"On your floorplan, your Medication Cabinet is in {', '.join(med_zones) if med_zones else 'not yet placed (add in NE/N)'}. "
                    "When the Medication Cabinet sits in North-East (Dhanvantari zone) and the East zone admits morning sunlight, your Life Line's vitality is doubled."
                ),
                "actionable_remedy": "Keep medicines in North-East/North (never in SW or Kitchen) and practice Prana Mudra (thumb + ring + little finger) for 10 minutes facing East.",
            },
            {
                "palm_feature": f"Head Line ({l_head.title()}) & Mount of Jupiter (Index Base)",
                "birth_chart_factor": f"5th House Intellect & 9th Wisdom Lord ({h9_lord_name})",
                "floorplan_alignment_status": (
                    "Optimal Wisdom Zone" if any(z in ("NE", "E", "N") for z in puja_zones) else "Activate NE Temple / Meditation"
                ),
                "combined_palm_chart_vastu_insight": (
                    f"Your {l_head.title()} Head Line and Mount of Jupiter correspond directly to the North-East (Ishanya) sector of your home. "
                    f"Your Temple / Meditation space is placed in {', '.join(puja_zones) if puja_zones else 'unplaced'}. "
                    "Keeping North-East sacred, free of heavy storage or toilets, and free of Deceased Ancestors' photos keeps your Head Line decision-making razor-sharp."
                ),
                "actionable_remedy": "Practice Gyan Mudra in your NE Meditation/Temple corner and place Gods/Deities photos on the NE or East wall facing West/South.",
            },
            {
                "palm_feature": f"Heart Line ({l_heart.title()}) & Mount of Venus / Marriage Lines",
                "birth_chart_factor": f"4th Home Lord ({h4_lord_name}) & 7th House Partnership",
                "floorplan_alignment_status": (
                    "Optimal Relationship Zone" if "SW" in bed_zones else "Anchor Master Bedroom in SW"
                ),
                "combined_palm_chart_vastu_insight": (
                    f"Your {l_heart.title()} Heart Line governs emotional peace and marital harmony. "
                    f"Your Master Bedroom is placed in {', '.join(bed_zones) if bed_zones else 'unplaced'}. "
                    "Placing the Master Bedroom in South-West, hanging Living Family/Couple Photos on the SW wall, and keeping TV/Mirrors from facing the bed protects your Heart Line from emotional turbulence."
                ),
                "actionable_remedy": "Keep a pair of Rose Quartz crystals in the SW Master Bedroom and never mix Deceased Ancestors' photos with Living Family photos.",
            },
            {
                "palm_feature": f"Fate Line ({l_fate.title()}) & Nadi Thumbprint ({t_name})",
                "birth_chart_factor": f"9th Luck Lord ({h9_lord_name}) & 10th/11th Wealth Axis",
                "floorplan_alignment_status": (
                    "Optimal Wealth & Gate Flow" if (any(z in ("N", "SW", "S") for z in safe_zones) or any(z in ("NE", "N", "E") for z in gate_zones)) else "Align Safe (N/SW) & Gate (NE/E)"
                ),
                "combined_palm_chart_vastu_insight": (
                    f"Your {l_fate.title()} Fate Line rising toward the Mount of Saturn and your {t_name} thumbprint govern career rise and wealth retention. "
                    f"Your Main Entrance/Gate is in {', '.join(gate_zones) if gate_zones else 'NE/E'} and Cash Safe is in {', '.join(safe_zones) if safe_zones else 'N/SW'}. "
                    "Having your Gate/Door swing inward clockwise (or slide toward North/East) and your Safe open toward North activates your Fate Line's full financial potential."
                ),
                "actionable_remedy": "Keep a silver coin or Shree Yantra inside your North-opening Safe and light a cow-ghee lamp in the NE Temple on Thursdays.",
            },
        ]

        palm_vastu_chart_synthesis = {
            "active": True,
            "has_uploaded_photo": has_photo,
            "headline": f"🖐️ Palm ({h_shape.title()} Hand · {t_name}) + 🌟 Birth Chart ({lagna_sign} Lagna) + 🏡 Vastu Layout Synthesis",
            "summary": (
                f"Combined analysis of your {'uploaded palm photo' if has_photo else 'selected palm profile'} "
                f"({h_shape.title()} Hand, {l_life} Life Line, {l_head} Head Line, {l_heart} Heart Line, {l_fate} Fate Line, {t_name}) "
                f"with your {lagna_sign} Ascendant birth chart and your {len(evaluated_items)} placed Vastu/Feng Shui floorplan items."
            ),
            "tri_system_checks": tri_checks,
        }

    return {
        "overall_vastu_score_percent": overall_score,
        "overall_score": overall_score,
        "overall_grade": overall_grade,
        "house_shape_analysis": shape_info,
        "has_outer_lot": has_outer_lot,
        "compass_rotation_degrees": compass_rotation,
        "total_items_evaluated": len(evaluated_items),
        "total_walls_evaluated": len(wall_evaluations),
        "total_fences_evaluated": len(fence_evaluations),
        "auspicious_strengths": auspicious_highlights or ["Add rooms and lot features on the visual canvas to see strengths."],
        "critical_doshas_and_fixes": critical_doshas or ["Zero critical Vastu/Feng Shui defects detected in the current placement!"],
        "relational_cross_checks": relational_findings,
        "wall_line_evaluations": wall_evaluations,
        "fence_loop_evaluations": fence_evaluations,
        "item_by_item_breakdown": evaluated_items,
        "palm_vastu_chart_synthesis": palm_vastu_chart_synthesis,
        "feng_shui_bagua_reference": FENG_SHUI_BAGUA_SECTORS,
        "feng_shui": FENG_SHUI_BAGUA_SECTORS,
    }


# ---------------------------------------------------------------------------
# 4B. CLASSICAL FENG SHUI ENGINE (BAGUA, PERSONAL KUA / EIGHT MANSIONS & FLYING STARS)
# ---------------------------------------------------------------------------
FENG_SHUI_BAGUA_SECTORS: Dict[str, Dict[str, Any]] = {
    "N": {
        "sector": "North", "trigram": "Kan (☵)", "lo_shu_number": 1, "element": "Water",
        "life_area": "Career, Life Path & Cash Flow", "celestial_guardian": "Red Phoenix / Black Tortoise Axis",
        "period_9_star": "Star #5 (Yellow Earth — Neutralize with 6-Rod Metal Windchime or Brass Wu Lou)",
        "colors": "Deep Blue, Black, Charcoal, White/Metallic accents",
        "enhancer": "Keep pathways open; use gentle moving water, aquarium, or metallic/glass decor to stimulate career flow.",
        "avoid": "Heavy Earth boulders, yellow clay clutter, or fire features in the North.",
    },
    "NE": {
        "sector": "North-East", "trigram": "Gen (☶)", "lo_shu_number": 8, "element": "Small Earth (Mountain)",
        "life_area": "Knowledge, Spiritual Wisdom, Study & Self-Cultivation", "celestial_guardian": "Outer Gate of Wisdom",
        "period_9_star": "Star #3 (Jade Wood — Add a touch of Red/Warm Light to calm wood-earth tension)",
        "colors": "Sandy Beige, Terracotta, Warm Yellow, Cream",
        "enhancer": "Ideal for meditation, Puja altar, library, and natural quartz/amethyst crystals.",
        "avoid": "Toilets, septic tanks, trash bins, or noisy machinery.",
    },
    "E": {
        "sector": "East", "trigram": "Zhen (☳)", "lo_shu_number": 3, "element": "Big Wood (Thunder)",
        "life_area": "Family Harmony, Physical Health, Vitality & Elders", "celestial_guardian": "Green Dragon (Qing Long — Keep Slightly Higher & Lush)",
        "period_9_star": "Star #7 (Red Metal — Place lush green bamboo or water-grown plants to absorb metal)",
        "colors": "Emerald Green, Forest Green, Teal, Aqua",
        "enhancer": "Healthy lush green plants, Lucky Bamboo (3 stalks), wooden furniture, and morning sunlight.",
        "avoid": "Sharp metal blades, dead/dried plants, or heavy metallic clutter.",
    },
    "SE": {
        "sector": "South-East", "trigram": "Xun (☴)", "lo_shu_number": 4, "element": "Soft Wood (Wind)",
        "life_area": "Wealth, Prosperity, Abundance & Fortunate Blessings", "celestial_guardian": "Sunlit Dragon Wing",
        "period_9_star": "Star #8 (White Wealth Star — Secondary Prosperity Star in Period 9!)",
        "colors": "Green, Jade, Purple, Lavender, Gold accents",
        "enhancer": "Jade plant / Money tree, citrine cluster, wooden wealth bowl, or clean kitchen warmth.",
        "avoid": "Withering plants, garbage, or dark stagnant corners.",
    },
    "S": {
        "sector": "South", "trigram": "Li (☲)", "lo_shu_number": 9, "element": "Fire",
        "life_area": "Fame, Reputation, Recognition & Social Illumination", "celestial_guardian": "Red Phoenix / Vermilion Bird (Keep Open & Bright)",
        "period_9_star": "Star #4 (Green Wood Academic & Romance Star — Feeds Fire naturally!)",
        "colors": "Crimson Red, Coral, Orange, Magenta, Bright Gold",
        "enhancer": "Bright lighting, awards/diplomas, fireplace/hearth, or 9-stalk upward-growing plants.",
        "avoid": "Large water tanks, swimming pools, or dark mirrors extinguishing South Fire.",
    },
    "SW": {
        "sector": "South-West", "trigram": "Kun (☷)", "lo_shu_number": 2, "element": "Big Earth (Receptive Mother)",
        "life_area": "Love, Marriage, Devoted Partnerships & Maternal Stability", "celestial_guardian": "Black Tortoise Support Wing",
        "period_9_star": "Star #6 (White Metal Heavenly Authority Star — Harmonious Earth-Metal bond)",
        "colors": "Rose Pink, Terracotta, Earthy Ochre, Soft Peach, Warm Beige",
        "enhancer": "Master Bedroom, paired rose quartz crystals, pairs of lamps/cushions, and heavy grounding furniture.",
        "avoid": "Single/lonely imagery, thorny cacti, water pools, or toilets.",
    },
    "W": {
        "sector": "West", "trigram": "Dui (☱)", "lo_shu_number": 7, "element": "Small Metal (Lake / Joy)",
        "life_area": "Children, Creativity, Descendants, Joy & Artistic Expression", "celestial_guardian": "White Tiger (Bai Hu — Keep Calmer & Lower than East)",
        "period_9_star": "Star #2 (Black Earth — Hang a Brass Wu Lou gourd to transmute illness energy into Metal)",
        "colors": "White, Silver, Metallic Gold, Pastel Grey",
        "enhancer": "Creative studio, children's bedroom, round metallic frames, and joyful family artwork.",
        "avoid": "Excessive open fire or chaotic clutter.",
    },
    "NW": {
        "sector": "North-West", "trigram": "Qian (☰)", "lo_shu_number": 6, "element": "Big Metal (Heaven / Mentor)",
        "life_area": "Helpful People, Mentors, Global Travel, Benefactors & Patriarch", "celestial_guardian": "Heavenly Gate (Qian)",
        "period_9_star": "Star #1 (White Water Future Prosperity & Nobleman Star — Highly Auspicious!)",
        "colors": "Metallic Gold, Silver, Pearl White, Platinum",
        "enhancer": "Guest room, travel globes, brass/silver bells (6-rod metal chime), and images of mentors/benefactors.",
        "avoid": "Heavy fire/kitchen stoves ('Fire at Heaven\\'s Gate' in Feng Shui — cure with yellow ceramic/earth crystal if kitchen is NW).",
    },
    "Center": {
        "sector": "Center (Tai Qi / Heart of Home)", "trigram": "Tai Qi (☯)", "lo_shu_number": 5, "element": "Central Earth",
        "life_area": "Overall Health, Unity, Spiritual Grounding & Qi Distribution", "celestial_guardian": "Supreme Axis (Brahmasthan / Tai Qi)",
        "period_9_star": "Star #9 (Purple Fire Supreme Period-9 reigning Star 2024–2043!)",
        "colors": "Cream, Ivory, Light Gold, Earthy Neutral",
        "enhancer": "Keep completely open, airy, well-lit, and unencumbered so Qi and Prana circulate to all 8 outer sectors.",
        "avoid": "Pillars, heavy staircases, bathrooms, or storage closets in the exact center.",
    },
}


def compute_classical_feng_shui(
    birth_year: int = 1990,
    birth_month: int | str = 5,
    birth_day: int = 15,
    gender: str = "male",
    pos: Dict[str, Any] | None = None,
    asc_lon: float | None = None,
) -> Dict[str, Any]:
    """Computes Personal Kua Number (Ming Gua), Eight Mansions (Ba Zhai) 4 Auspicious
    & 4 Inauspicious Directions, Bagua 9-Grid, Period 9 Flying Stars, and Form School Landscape rules."""
    if isinstance(birth_month, str):
        gender = birth_month
        birth_month = 5
    # Adjust solar year for Lichun (approx Feb 4)
    solar_year = birth_year - 1 if (birth_month == 1 or (birth_month == 2 and birth_day < 4)) else birth_year
    last_two = solar_year % 100
    s = (last_two // 10) + (last_two % 10)
    while s >= 10:
        s = (s // 10) + (s % 10)

    is_female = str(gender or "male").lower().startswith("f")
    if solar_year < 2000:
        kua = (s + 4) if is_female else (10 - s)
    else:
        kua = (s + 6) if is_female else (9 - s)
    while kua >= 10:
        kua = (kua // 10) + (kua % 10)
    if kua <= 0:
        kua += 9
    if kua == 5:
        kua = 8 if is_female else 2

    KUA_DATA = {
        1: {
            "trigram": "Kan (☵ Water)", "element": "Water", "group": "East Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "SE",
                "Tian Yi (Heavenly Doctor & Health)": "E",
                "Yan Nian (Harmony, Love & Longevity)": "S",
                "Fu Wei (Stability, Study & Peace)": "N",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "W",
                "Wu Gui (Five Ghosts / Conflict)": "NE",
                "Liu Sha (Six Killings / Drain)": "NW",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "SW",
            },
        },
        2: {
            "trigram": "Kun (☷ Earth)", "element": "Earth", "group": "West Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "NE",
                "Tian Yi (Heavenly Doctor & Health)": "W",
                "Yan Nian (Harmony, Love & Longevity)": "NW",
                "Fu Wei (Stability, Study & Peace)": "SW",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "E",
                "Wu Gui (Five Ghosts / Conflict)": "SE",
                "Liu Sha (Six Killings / Drain)": "S",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "N",
            },
        },
        3: {
            "trigram": "Zhen (☳ Wood)", "element": "Wood", "group": "East Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "S",
                "Tian Yi (Heavenly Doctor & Health)": "N",
                "Yan Nian (Harmony, Love & Longevity)": "SE",
                "Fu Wei (Stability, Study & Peace)": "E",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "SW",
                "Wu Gui (Five Ghosts / Conflict)": "NW",
                "Liu Sha (Six Killings / Drain)": "NE",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "W",
            },
        },
        4: {
            "trigram": "Xun (☴ Wood)", "element": "Soft Wood", "group": "East Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "N",
                "Tian Yi (Heavenly Doctor & Health)": "S",
                "Yan Nian (Harmony, Love & Longevity)": "E",
                "Fu Wei (Stability, Study & Peace)": "SE",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "NW",
                "Wu Gui (Five Ghosts / Conflict)": "SW",
                "Liu Sha (Six Killings / Drain)": "W",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "NE",
            },
        },
        6: {
            "trigram": "Qian (☰ Metal)", "element": "Metal", "group": "West Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "W",
                "Tian Yi (Heavenly Doctor & Health)": "NE",
                "Yan Nian (Harmony, Love & Longevity)": "SW",
                "Fu Wei (Stability, Study & Peace)": "NW",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "SE",
                "Wu Gui (Five Ghosts / Conflict)": "E",
                "Liu Sha (Six Killings / Drain)": "N",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "S",
            },
        },
        7: {
            "trigram": "Dui (☱ Metal)", "element": "Small Metal", "group": "West Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "NW",
                "Tian Yi (Heavenly Doctor & Health)": "SW",
                "Yan Nian (Harmony, Love & Longevity)": "NE",
                "Fu Wei (Stability, Study & Peace)": "W",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "N",
                "Wu Gui (Five Ghosts / Conflict)": "S",
                "Liu Sha (Six Killings / Drain)": "SE",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "E",
            },
        },
        8: {
            "trigram": "Gen (☶ Earth)", "element": "Mountain Earth", "group": "West Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "SW",
                "Tian Yi (Heavenly Doctor & Health)": "NW",
                "Yan Nian (Harmony, Love & Longevity)": "W",
                "Fu Wei (Stability, Study & Peace)": "NE",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "S",
                "Wu Gui (Five Ghosts / Conflict)": "N",
                "Liu Sha (Six Killings / Drain)": "E",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "SE",
            },
        },
        9: {
            "trigram": "Li (☲ Fire)", "element": "Fire", "group": "East Group",
            "auspicious": {
                "Sheng Qi (Supreme Wealth & Vitality)": "E",
                "Tian Yi (Heavenly Doctor & Health)": "SE",
                "Yan Nian (Harmony, Love & Longevity)": "N",
                "Fu Wei (Stability, Study & Peace)": "S",
            },
            "inauspicious": {
                "Huo Hai (Minor Mishaps)": "NE",
                "Wu Gui (Five Ghosts / Conflict)": "W",
                "Liu Sha (Six Killings / Drain)": "SW",
                "Jue Ming (Total Loss — Suppress with Bathroom/Storage)": "NW",
            },
        },
    }
    kd = KUA_DATA[kua]
    ausp_list = [
        {"star": k.split(" (")[0], "title": k.split(" (")[1].rstrip(")") if "(" in k else k, "direction": v, "use": "Front door, desk orientation, bed headboard, or wealth activation"}
        for k, v in kd["auspicious"].items()
    ]
    inausp_list = [
        {"star": k.split(" (")[0], "title": k.split(" (")[1].rstrip(")") if "(" in k else k, "direction": v, "remedy": "Place bathrooms, closets, storerooms, or elemental cures here to suppress negative Qi"}
        for k, v in kd["inauspicious"].items()
    ]
    return {
        "solar_birth_year": solar_year,
        "gender_calibrated": "female" if is_female else "male",
        "kua_number": kua,
        "trigram": kd["trigram"],
        "personal_element": kd["element"],
        "eight_mansions_group": kd["group"],
        "personal_kua": {
            "kua_number": kua,
            "trigram_name": kd["trigram"],
            "element": kd["element"],
            "group": kd["group"],
        },
        "four_auspicious_directions": kd["auspicious"],
        "four_inauspicious_directions": kd["inauspicious"],
        "auspicious_directions": ausp_list,
        "inauspicious_directions": inausp_list,
        "bagua_nine_sectors": list(FENG_SHUI_BAGUA_SECTORS.values()),
        "bagua_9_grid": FENG_SHUI_BAGUA_SECTORS,
        "form_school_four_celestial_animals": [
            {"guardian": "Black Tortoise (Xuan Wu — Back / South-West Support)", "rule": "Keep the back of the house/lot supported by higher ground, a solid fence/wall, or tall shade trees for career and family backing."},
            {"guardian": "Red Phoenix (Zhu Que — Front / Ming Tang Bright Hall)", "rule": "Keep the front entrance lawn/yard open, bright, and welcoming (grass, low flowers, or gentle water feature) so opportunities gather."},
            {"guardian": "Green Dragon (Qing Long — Left / East Side looking out)", "rule": "Plant vibrant green trees/garden slightly higher on the East/Left side to activate Yang growth and noble mentors."},
            {"guardian": "White Tiger (Bai Hu — Right / West Side looking out)", "rule": "Keep the West/Right side tidy with lower bushes and calm pathway lighting so White Tiger energy stays protective and peaceful."},
        ],
        "period_9_fire_era_summary": (
            "We are currently in the 20-year Xuan Kong Period 9 (2024–2043), ruled by the #9 Purple Fire Star (Li Trigram). "
            "Homes with open, bright North/South axes, thriving Southeast (#8 Wealth Star) and Northwest (#1 Nobleman Star) sectors, "
            "and a clutter-free Center (#9 Supreme Star) experience maximum prosperity."
        ),
    }


# ---------------------------------------------------------------------------
# 5. DEEP PLAIN-ENGLISH ENRICHMENT FOR MASTER DESTINY DOSSIER
# ---------------------------------------------------------------------------
def enrich_destiny_with_deep_simple_explanations(
    dossier: Dict[str, Any],
    pos: Dict[str, Any],
    asc_lon: float,
) -> Dict[str, Any]:
    """Attaches:
    1. `plain_english_glossary` (every technical term explained in simple words)
    2. `simple_step_by_step_explanations` (deep, jargon-free breakdown of every tab)
    3. `astro_vastu_guide` (personalized Birth-Chart + Vastu synthesis & Do's/Don'ts)
    4. `default_visual_vastu_report` (sample pre-evaluated house + lot Vastu layout)
    into the Master Destiny Dossier."""
    lagna_idx = int(asc_lon // 30) % 12
    lagna_sign = SIGNS[lagna_idx]
    lagna_lord = SIGN_LORDS[lagna_idx]

    rm = dossier.get("ravana_samhita_planetary_mastery", {})
    fh = rm.get("functional_planet_hierarchy", {})
    lot = dossier.get("lottery_and_windfall_oracle", {})
    dt = dossier.get("destiny_turning_points_and_dates", {})
    acc = dossier.get("accidents_and_safety_windows", {})
    med = dossier.get("medical_diseases_and_longevity", {})
    mar = dossier.get("marriage_count_and_remedies", {})
    prog = dossier.get("progeny_children_and_grandchildren", {})
    pl = dossier.get("past_life_future_life_and_purpose", {})

    simple_explanations = {
        "ravana_mastery_in_simple_words": {
            "headline": f"How to Command All 9 Planets for Your {lagna_sign} Ascendant (In Plain English)",
            "what_it_means": (
                f"When you were born, the zodiac sign {lagna_sign} was rising on the eastern horizon. That makes {lagna_lord} your "
                f"'Captain Planet' (Lagna Lord — ruler of your body, health, and life path). Think of the 9 planets like a cabinet of ministers: "
                f"your friendly helper planets (Functional Benefics: {', '.join(fh.get('functional_benefics', []))}) rule the good houses of luck, "
                f"intelligence, and career growth. You should STRENGTHEN these helper planets by wearing their gemstones, using their colors, "
                f"and facing their directions. By contrast, {', '.join(fh.get('functional_malefics', []))} rule the tough houses (6th house of debt/illness, "
                f"8th house of sudden shocks, or 12th house of loss) for a {lagna_sign} native. You must NEVER wear the gemstone of a Functional Malefic, "
                f"because making a troublemaker planet stronger increases obstacles! Instead, you command and pacify them through charity (Dana), "
                f"feeding specific animals, and chanting their peace mantras during their planetary hour (Hora)."
            ),
            "maraka_and_badhaka_explained_simply": (
                f"• What is a Maraka Planet? ({', '.join(fh.get('maraka_lords', []))}): 'Maraka' literally means 'vitality-drainer' or 'health-tester'. "
                f"In Vedic astrology, House 8 and House 3 govern your longevity. The houses right behind them — House 2 (family/savings) and House 7 "
                f"(marriage/business partners) — are the Maraka houses. Their planetary lords ({', '.join(fh.get('maraka_lords', []))}) bring money and relationships, "
                f"but during their time periods (Dashas), they also test your physical body and stamina.\n"
                f"• What is a Badhaka Planet? ({fh.get('badhaka_lord', '')}): 'Badhaka' means 'hidden roadblock' or 'invisible saboteur'. "
                f"Whenever a deal, visa, promotion, or relationship is 99% done and suddenly gets stuck at the very last minute for no logical reason, "
                f"your Badhaka planet ({fh.get('badhaka_lord', '')}) is causing it. Performing its specific charity (Dana) and keeping its Vastu direction clean immediately removes that invisible wall."
            ),
            "key_terms_in_this_section": [
                {"term": "Functional Benefic", "meaning": "A planet that rules lucky houses (1st, 5th, 9th) for your specific rising sign — safe and powerful to boost with gemstones."},
                {"term": "Functional Malefic", "meaning": "A planet that rules difficult houses (6th, 8th, 12th) for your rising sign — never wear its gem; calm it down with charity (Dana) and mantras."},
                {"term": "Maraka (2nd & 7th Lords)", "meaning": "Planets that rule family/wealth (2nd) and marriage (7th), which also test physical health and stamina during their Dasha periods."},
                {"term": "Badhaka (Obstruction Lord)", "meaning": "The planet responsible for sudden, unexplained last-minute delays and red tape. Appeasing it clears stuck work."},
                {"term": "Beej Mantra & Prana Pratishtha", "meaning": "Beej Mantra is the acoustic seed-sound frequency of a planet; Prana Pratishtha is the energizing verse spoken before wearing a ring so it bonds with your aura."},
                {"term": "Dana (Targeted Charity)", "meaning": "Giving away the physical item ruled by a harsh planet (such as black sesame for Saturn or red lentils for Mars) so its heavy energy leaves your body."},
            ],
            "step_by_step_how_to_use": [
                f"1. Wear only the prescribed Life/Luck/Destiny gemstones for {', '.join(fh.get('functional_benefics', []))} in the exact metal, finger, and morning Hora listed below.",
                f"2. Carry the Sacred Wallet/Desk items and wear your Power Colors ({', '.join(rm.get('things_to_keep_close_master_guide', {}).get('power_colors_to_wear', [])[:4])}) whenever attending high-stakes meetings.",
                f"3. Whenever you feel blocked or drained, donate the Dana item of your Badhaka planet ({fh.get('badhaka_lord', '')}) or Functional Malefics ({', '.join(fh.get('functional_malefics', []))}) on their weekday.",
            ],
            "vastu_double_boost_tip": (
                f"Double the Positive Effect with Vastu: Keep the home direction ruled by your Captain Planet ({lagna_lord}) and 9th Luck Lord "
                f"bright, clean, and well-lit every morning, and place a copper/brass emblem or fresh plant there."
            ),
        },
        "lottery_and_windfall_in_simple_words": {
            "headline": "How Your Sudden Wealth, Speculation & Lottery Luck Actually Works",
            "what_it_means": (
                f"Regular monthly salary comes from your 10th house (career) and 6th house (daily work). Sudden windfalls, jackpots, "
                f"booming stock/crypto trades, and lottery luck come from a completely different circuit of four wealth points: "
                f"(1) Indu Lagna ({lot.get('indu_lagna_wealth_ascendant', {}).get('sign', '')}, ruled by {lot.get('indu_lagna_wealth_ascendant', {}).get('lord', '')}) — your special 'Wealth Ascendant', "
                f"(2) the 5th House of Speculation & Intuition (ruled by {lot.get('key_wealth_and_speculation_lords', {}).get('5th_lord_speculation_intuition', '')}), "
                f"(3) the 8th House of Sudden Unearned Money (ruled by {lot.get('key_wealth_and_speculation_lords', {}).get('8th_lord_sudden_unearned_windfall', '')}), and "
                f"(4) the 11th House of Massive Gains (ruled by {lot.get('key_wealth_and_speculation_lords', {}).get('11th_lord_massive_gains', '')}). "
                f"The table below scans every upcoming day at your CURRENT location and finds the exact dates and 15-minute windows when the local Moon and Planetary Hora activate these four wealth triggers simultaneously!"
            ),
            "key_terms_in_this_section": [
                {"term": "Indu Lagna (Wealth Ascendant)", "meaning": "A special mathematical wealth point discovered by sage Parashara by combining the 9th lords from your Ascendant and Moon. When activated, it brings multi-fold money."},
                {"term": "5th, 8th & 11th Lords", "meaning": "5th Lord = market/game intuition; 8th Lord = sudden unearned windfall/jackpot; 11th Lord = big financial payouts and fulfilled desires."},
                {"term": "Sampat / Sadhaka / Kshema Tara", "meaning": "Favorable daily star alignments between today's Moon and your birth star: Sampat = Wealth Day, Sadhaka = Achievement Day, Kshema = Prosperity Day."},
                {"term": "Golden Hora & 15-Min Lakshmi Sub-Window", "meaning": "The 1-hour planetary window (and its peak 15-minute core) calculated from your current city's exact Sunrise when your wealth planet rules the sky."},
            ],
            "step_by_step_how_to_use": [
                "1. Never speculate or buy tickets on random days or during Rahu Kaal — wait for the dates listed in the table below.",
                "2. Act during the 15-minute Peak Lakshmi Sub-Window while facing the recommended compass direction.",
                "3. Use the 6-Pick Harmonic Numbers and Power Root Digit generated for that specific date (linked to your birth numerology + day's wealth planet).",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Keep the North (Lord Kubera's treasury) and North-East (Jupiter's abundance) of your home/lot completely free of heavy shoes, trash, or clutter, and keep your safe/wallet in the South-West opening toward the North."
            ),
        },
        "turning_points_and_bad_luck_in_simple_words": {
            "headline": "Why Your Luck Changes at Specific Ages & How to Break a Chronic Bad-Luck Streak",
            "what_it_means": (
                "Have you ever wondered why certain years of your life change everything overnight? That happens through two cosmic clocks: "
                "(1) Bhrigu Chakra Rotation — every year of your life activates the next house of your birth chart in a 12-year cycle (and planets have natural maturity ages like 22, 24, 28, 30, 36, 42, 48), and "
                "(2) Vimshottari Mahadasha — the multi-year planetary chapter ruling your life. "
                "When you hit a streak of 'chronic bad luck' where everything goes wrong one after another, it is not random: it means your 9th Luck Lord is temporarily blocked by transit Saturn/Rahu or your Badhaka (obstruction) planet is active. "
                "The 4-Step Durbhagya Nashaka (Bad-Luck Reset) protocol below physically and energetically clears that block."
            ),
            "key_terms_in_this_section": [
                {"term": "Bhrigu Chakra Paddhati", "meaning": "An ancient age-progression technique where Age 1 activates House 1, Age 2 activates House 2, and so on around your chart, showing exact milestone years."},
                {"term": "Vimshottari Mahadasha", "meaning": "The 120-year master timeline of Vedic astrology that tells which planet is the 'CEO of your life' during any given decade."},
                {"term": "Abhijit Muhurta", "meaning": "The ~48-minute midday victory window around local solar noon when Lord Vishnu's energy neutralizes nearly all planetary defects."},
                {"term": "Durbhagya Nashaka", "meaning": "Classical Vedic & Tantric remedy protocol to dissolve a streak of repeated bad luck and re-awaken the 9th house of fortune (Bhagya)."},
            ],
            "step_by_step_how_to_use": [
                "1. Schedule major launches, interviews, property purchases, and agreements on the green 'Upcoming Auspicious Destiny Dates' during the Power Hora or Abhijit window.",
                "2. On the red 'Upcoming Adverse / Bad-Luck Dates', avoid starting risky ventures during the Avoid Hora and Local Rahu Kaal, and apply the listed 1-minute Instant Neutralizer.",
                "3. If you have been facing months of stuck luck, perform the 4-Step Chronic Bad-Luck Fix Protocol starting this Saturday evening.",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Mop your home floors once a week on Saturday with water mixed with a pinch of natural sea salt and turmeric, and light a ghee lamp near the Main Entrance or North-East corner at dusk."
            ),
        },
        "accidents_and_safety_in_simple_words": {
            "headline": "Why Accidents & Mishaps Happen in Specific Hours & How to Stay 100% Protected",
            "what_it_means": (
                "Physical accidents, falls, burns, vehicle collisions, or sudden surgeries rarely happen out of nowhere — in Vedic astrology they occur when three triggers line up on the same day: "
                "(1) your birth chart's D-8 Ashtamsha (the microscopic 1/8th divisional chart of sudden shocks) has Mars, Saturn, or Rahu in sensitive zones, "
                "(2) the Moon in the sky is passing through an unfavorable star (Vipat/Vadha Tara) or the 8th sign from your birth Moon (Chandrashtama), and "
                "(3) you drive fast or handle sharp/fiery equipment during a local Mars/Saturn Hora, Rahu Kaal, or Yamaganda window. "
                "By simply checking the red 'Danger & Caution Windows' below for your current city, you know the exact hours to slow down and stay protected."
            ),
            "key_terms_in_this_section": [
                {"term": "D-8 Ashtamsha Chart", "meaning": "A specialized divisional chart (dividing each sign into 8 parts) used exclusively to inspect sudden physical shocks, accidents, surgeries, and hidden longevity support."},
                {"term": "Chandrashtama", "meaning": "The 2.5 days each month when the Moon transits the 8th sign from your natal Moon — causing mental fatigue, distraction, and delayed reflexes."},
                {"term": "Vipat & Vadha Tara", "meaning": "Vipat = 'Danger Star' (3rd from birth star) and Vadha = 'Destruction/Impact Star' (7th from birth star). Avoid high-risk physical activities on these days."},
                {"term": "Disha Shool (Directional Thorn)", "meaning": "Each day of the week has one compass direction where energy flows against travelers. If you must travel that way, eat the day's neutralizer first."},
            ],
            "step_by_step_how_to_use": [
                "1. Before long highway drives, flights, or medical procedures, check the red Caution Windows and green Safe Travel Windows for your current city.",
                "2. Avoid starting a journey during the listed Peak Danger Hora, Rahu Kaal, or Yamaganda.",
                "3. Recite the 1-line Narasimha Raksha Kavacha Shloka before turning the ignition key on high-risk days.",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Keep your Parking Gate / Garage in the North-West or South-East, never leave broken glass or rusted iron in the South or South-West of your yard, and keep the South-East kitchen fire away from water leaks."
            ),
        },
        "medical_and_longevity_in_simple_words": {
            "headline": "Your Body Constitution (Tridosha), Organ Vulnerabilities & Lifespan Potential (Ayurdaya)",
            "what_it_means": (
                f"Medical Astrology (Ayur-Jyotish) maps the 12 zodiac signs and 9 planets directly to the organs and tissues of your body. "
                f"Your chart shows an Ayurvedic constitution (Prakriti) of {med.get('ayurvedic_constitution', {}).get('dominant_prakriti', 'Balanced')}. "
                f"For lifespan and vitality (Ayurdaya), sage Parashara's Three-Pairs Method compares the placement of (1) your Ascendant Lord & 8th Lord, "
                f"(2) your Moon & Saturn, and (3) your Ascendant & Hora Lagna, indicating '{med.get('longevity_ayurdaya', {}).get('estimated_lifespan_potential', 'Full Span')}'. "
                f"Most importantly, the table of 'Critical Maraka & Health-Vigilance Windows' below is an early-warning calendar: during those specific planetary sub-periods, "
                f"your body's immunity dips and you should proactively schedule checkups, eat clean, and practice the listed Ayurvedic & mantra remedies."
            ),
            "key_terms_in_this_section": [
                {"term": "Tridosha (Vata, Pitta, Kapha)", "meaning": "The three biological humors in Ayurveda: Vata = Air/Nervous system; Pitta = Fire/Metabolism & Digestion; Kapha = Water-Earth/Immunity & Joints."},
                {"term": "Ayurdaya (Longevity Calculation)", "meaning": "Classical Vedic mathematical assessment of physical vitality and lifespan category (Alpayu, Madhyayu, Purnayu/Dirghayu) along with Bhanga (protective cancellations)."},
                {"term": "6th, 8th & 12th Houses in Health", "meaning": "6th House = acute infections, digestion, daily immunity; 8th House = chronic/long-term conditions & surgeries; 12th House = hospitalization & sleep."},
                {"term": "Mrityu Bhaga (Sensitive Degree)", "meaning": "A specific degree in a sign where a planet becomes medically sensitive — indicating which organ needs lifelong preventive care."},
            ],
            "step_by_step_how_to_use": [
                "1. Review the Organ & Disease Vulnerability Matrix below to see which specific organs your 6th, 8th, and weak planets sensitize.",
                "2. Adopt the daily Ayurvedic herb/diet remedy listed for your primary vulnerable planet.",
                "3. During any 'HIGH (Double Maraka)' or 'ELEVATED' Dasha window at the bottom of this tab, prioritize rest, routine bloodwork, and Maha Mrityunjaya japa.",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Never sleep with your head pointing North (it fights Earth's magnetic pole and raises blood pressure/insomnia); always sleep with your head pointing South or East, and keep the North-East corner of your home clean and airy."
            ),
        },
        "marriage_in_simple_words": {
            "headline": "How Astrology Predicts Marriage Count, Spouse Personality & Ways to Save/Harmonize Marriage",
            "what_it_means": (
                f"Many people ask: 'Will I have one lifelong marriage, or is there a risk of separation / second marriage, and how do I fix it?' "
                f"To answer this accurately, we cross-check four pillars: (1) your 7th House of Marriage and its ruling planet, "
                f"(2) your D-9 Navamsha chart (the sacred microscopic marriage chart), (3) Jaimini Upapada Lagna ({mar.get('key_marital_pillars', {}).get('upapada_lagna_ul', '')} — "
                f"which shows the actual physical stability of the marriage bond), and (4) your Darakaraka planet ({mar.get('key_marital_pillars', {}).get('jaimini_darakaraka_spouse_indicator', '')} — "
                f"the planet at the lowest degree, representing your spouse's soul nature). "
                f"Your chart's synthesis shows: {mar.get('estimated_number_of_marriages', '')} ({mar.get('marriage_count_verdict', '')}). "
                f"Even when a chart has heavy tension (like Mars/Rahu/Saturn pressure or dual-sign multiplicity), applying the targeted Vedic Upayas and bedroom Vastu fixes on the right side of this tab protects and heals the union."
            ),
            "key_terms_in_this_section": [
                {"term": "7th House & D-9 Navamsha", "meaning": "The 7th house in your birth chart shows who attracts you; the D-9 Navamsha chart shows how the marriage actually feels and lasts over decades."},
                {"term": "Upapada Lagna (UL) & 2nd from UL", "meaning": "Jaimini astrology's marriage point. If the 2nd house from Upapada Lagna is strong, the marriage endures every storm; if afflicted, targeted Upapada fasting is required."},
                {"term": "Darakaraka (DK)", "meaning": "The planet with the lowest degree (0°–30°) in your birth chart — it describes your spouse's personality, appearance, and temperament."},
                {"term": "Manglik / Kuja Dosha", "meaning": "Placement of fiery Mars in the 1st, 2nd, 4th, 7th, 8th, or 12th house, which can cause impatience or heated arguments in marriage if not channeled or neutralized."},
            ],
            "step_by_step_how_to_use": [
                "1. Check your Spouse Character & Meeting Direction (from Darakaraka) and your Manglik status.",
                "2. Use the 'Favorable Marriage / Relationship Renewal Windows' for weddings, engagements, vow renewals, or important relationship talks.",
                "3. Follow the 5 custom 'Ways to Fix, Save & Harmonize Marriage' step-by-step if you want to remove delays or heal friction.",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Always use the South-West (Nairutya) room as the Master Bedroom for the couple (never the North-West, which causes restlessness/separation), use a single mattress on the marital bed, and remove any mirror reflecting the bed."
            ),
        },
        "progeny_and_grandchildren_in_simple_words": {
            "headline": "Ability to Have Children, Exact Child Count (D-7 Saptamsha) & Your Grandchildren's Future",
            "what_it_means": (
                f"To see everything about children and grandchildren, Vedic astrology uses three layers of precision: "
                f"First, we calculate your biological & energetic fertility score using Beeja Sphuta (Sun + Venus + Jupiter) and Kshetra Sphuta (Moon + Mars + Jupiter) — "
                f"your score is {prog.get('fertility_and_conception_capacity', {}).get('fertility_vitality_score', 85)}/100 ({prog.get('fertility_and_conception_capacity', {}).get('verdict', '')}). "
                f"Second, we open your D-7 Saptamsha chart (the 1/7th divisional chart of progeny): the 5th house of D-7 reveals your 1st child, the 7th house reveals your 2nd child, and the 9th house reveals your 3rd child, including their temperament and future destiny. "
                f"Third, how do we see your GRANDCHILDREN? By the rule of Bhavat Bhavam ('5th from the 5th'), your 5th house is your child, so 5 houses from the 5th is your 9th House! "
                f"Your 9th house and D-7 9th axis reveal: {prog.get('grandchildren_and_lineage_future', {}).get('estimated_grandchildren_blessing', '')}."
            ),
            "key_terms_in_this_section": [
                {"term": "Beeja Sphuta & Kshetra Sphuta", "meaning": "Classical mathematical fertility points (Sun+Venus+Jupiter and Moon+Mars+Jupiter). When placed in odd/even harmonious signs free of Saturn/Rahu, conception is smooth."},
                {"term": "D-7 Saptamsha Chart", "meaning": "The 1/7th divisional chart dedicated solely to children, grandchildren, creative legacy, and lineage continuation."},
                {"term": "Oja (Odd) & Yugma (Even) Rashi Rule", "meaning": "Sage Parashara's rule in D-7 where odd signs/exalted Sun-Mars-Jupiter-Lagnesh indicate male-inclined energy and even signs/Moon-Venus-Mercury indicate female-inclined energy."},
                {"term": "Bhavat Bhavam (9th House = Grandchildren)", "meaning": "Because the 5th house represents your children, counting 5 houses forward from the 5th lands on the 9th house — the house of grandchildren (Pautra/Pautri)."},
            ],
            "step_by_step_how_to_use": [
                "1. Check your Fertility Vitality Score and Beeja/Kshetra Sphuta signs to see if any planetary remediation is needed before conception.",
                "2. Read the Child-by-Child D-7 profile to understand each child's natural talent, personality, and how best to guide them.",
                "3. Read the 3-Generation Grandchildren & Lineage section to see how your grandchildren will prosper and what ancestral blessing to leave them.",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Keep the North-East (Jupiter — natural significator of children) and East (Sun — vitality) of your home completely open, bright, and free of heavy storage or toilets; children's bedrooms thrive in the East, North, or West."
            ),
        },
        "past_and_future_life_in_simple_words": {
            "headline": "Your Past Life (D-60 & Ketu), Past-Life Mistakes to Fix, This Life's Purpose & Your Next Life",
            "what_it_means": (
                "In Vedic astrology, your birth chart is a snapshot of your soul's long journey across incarnations: "
                "• PAST LIFE: Ketu (the South Node) and the ultra-fine D-60 Shashtiamsha chart (which divides every sign into 60 tiny 0.5° slices) show where your soul came from, what status/skills you already mastered, and what 'Rinas' (karmic debts or mistakes from past lives) you brought with you. Retrograde (Vakri) planets show unfinished promises you swore to complete. "
                "• THIS LIFE'S PURPOSE: Rahu (the North Node), your Atmakaraka (the planet at the highest degree — your Soul King), and your Amatyakaraka (second-highest degree — your Career Minister) show why you took birth now and the exact daily life you should live. "
                "• FUTURE LIFE: The 12th house from your Karakamsha (your Atmakaraka's position in D-9) shows where your soul is headed after this life and how to consciously elevate your next birth or attain liberation (Moksha)."
            ),
            "key_terms_in_this_section": [
                {"term": "D-60 Shashtiamsha Chart", "meaning": "The finest divisional chart in Vedic astrology (each division is just half a degree), used by sages to read past-life karma (Purva Punya) and root destiny."},
                {"term": "Ketu vs. Rahu Axis", "meaning": "Ketu = what you already did in past lives (natural talent & detachment); Rahu = the new frontier you must master in this life."},
                {"term": "Vakri (Retrograde Planet)", "meaning": "A planet appearing to move backward in the sky at birth — it represents an unfinished duty or relationship carried over from a previous life."},
                {"term": "Rina (Past-Life Karmic Debt)", "meaning": "Specific unpaid soul obligations (to ancestors, mother, teachers, partners, or nature) that cause recurring blocks until cleared with the listed remedy."},
                {"term": "Atmakaraka (AK) & Karakamsha", "meaning": "Atmakaraka is the highest-degree planet (your Soul's King); Karakamsha is its sign in D-9, revealing your spiritual calling and post-life trajectory."},
            ],
            "step_by_step_how_to_use": [
                "1. Read your Past-Life Archetype and Retrograde Unfinished Promises to understand why certain people and situations feel deeply familiar.",
                "2. Perform the simple, practical remedies under 'Bad Things Done / Karmic Debts (Rinas) from Past Lives' to dissolve old karmic blocks.",
                "3. Align your daily routine (Dinacharya), career ethics, and spiritual practice with your Atmakaraka and Karakamsha guide.",
            ],
            "vastu_double_boost_tip": (
                "Double the Positive Effect with Vastu: Dedicate a clean, peaceful Puja / Meditation shelf in the North-East (Ishanya) for Deva/Guru blessings, and keep the South-West (Pitru/Ancestral stability zone) respectful and orderly to clear ancestral Rina."
            ),
        },
    }

    astro_vastu = compute_personalized_astro_vastu(pos, asc_lon)

    default_sample_items = [
        {"type": "entrance", "label": "Main Entrance", "x": 72, "y": 20, "w": 12, "h": 7, "door_dir": "NE", "scope": "indoor"},
        {"type": "living_room", "label": "Living Room", "x": 52, "y": 24, "w": 22, "h": 18, "door_dir": "", "scope": "indoor"},
        {"type": "kitchen", "label": "Kitchen", "x": 64, "y": 60, "w": 18, "h": 16, "door_dir": "E", "scope": "indoor"},
        {"type": "master_bedroom", "label": "Master Bedroom", "x": 20, "y": 58, "w": 22, "h": 18, "door_dir": "N", "scope": "indoor"},
        {"type": "bedroom", "label": "Kids Bedroom", "x": 20, "y": 38, "w": 18, "h": 16, "door_dir": "E", "scope": "indoor"},
        {"type": "guest_room", "label": "Guest Room", "x": 20, "y": 20, "w": 18, "h": 15, "door_dir": "E", "scope": "indoor"},
        {"type": "bathroom", "label": "Bathroom", "x": 40, "y": 20, "w": 10, "h": 12, "door_dir": "", "scope": "indoor"},
        {"type": "storage", "label": "Storage Closet", "x": 44, "y": 64, "w": 14, "h": 12, "door_dir": "", "scope": "indoor"},
        {"type": "balcony", "label": "Balcony", "x": 58, "y": 14, "w": 14, "h": 6, "door_dir": "N", "scope": "indoor"},
        {"type": "back_door", "label": "Back Door", "x": 22, "y": 14, "w": 10, "h": 6, "door_dir": "NW", "scope": "indoor"},
        {"type": "gate", "label": "Main Lot Gate", "x": 70, "y": 3, "w": 14, "h": 6, "door_dir": "NE", "scope": "outdoor"},
        {"type": "parking_gate", "label": "Parking Gate & Driveway", "x": 14, "y": 3, "w": 18, "h": 7, "door_dir": "NW", "scope": "outdoor"},
        {"type": "trees", "label": "Tall Shade Trees", "x": 6, "y": 76, "w": 16, "h": 16, "door_dir": "", "scope": "outdoor"},
        {"type": "flowers", "label": "Flower Bed", "x": 84, "y": 14, "w": 11, "h": 14, "door_dir": "", "scope": "outdoor"},
        {"type": "bushes", "label": "Ornamental Bushes", "x": 4, "y": 32, "w": 9, "h": 20, "door_dir": "", "scope": "outdoor"},
        {"type": "fireplace", "label": "Outdoor Fireplace / BBQ", "x": 84, "y": 76, "w": 12, "h": 12, "door_dir": "", "scope": "outdoor"},
        {"type": "garden", "label": "Herbal & Veggie Garden", "x": 44, "y": 3, "w": 22, "h": 8, "door_dir": "", "scope": "outdoor"},
        {"type": "grass", "label": "Front Grass Lawn", "x": 84, "y": 32, "w": 11, "h": 28, "door_dir": "", "scope": "outdoor"},
    ]
    default_layout_eval = evaluate_visual_vastu_layout(
        default_sample_items, house_shape="square", has_outer_lot=True, compass_rotation=0.0, pos=pos, asc_lon=asc_lon
    )

    dossier["plain_english_glossary"] = PLAIN_ENGLISH_GLOSSARY
    dossier["simple_step_by_step_explanations"] = simple_explanations
    dossier["astro_vastu_guide"] = astro_vastu
    dossier["default_visual_vastu_report"] = default_layout_eval
    return dossier

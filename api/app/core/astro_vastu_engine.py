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
    }


# ---------------------------------------------------------------------------
# 4. INTERACTIVE VISUAL HOUSE (SQUARE/RECTANGLE) & OUTER-LOT VASTU EVALUATOR
# ---------------------------------------------------------------------------
ITEM_RULES: Dict[str, Dict[str, Any]] = {
    # ---------------- INDOOR HOUSE ITEMS ----------------
    "entrance": {
        "label": "Main Entrance Door",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["W", "NW"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "ideal_door_facing": ["NE", "E", "N"],
        "why_simple": "The Main Entrance (Simhadwara) is the mouth of the house where cosmic energy (Prana) and luck enter. North-East (Jupiter), East (Sun), and North (Mercury/Kubera) bring health, fame, and steady wealth.",
        "fix_if_wrong": "If your entrance is in South, South-West, or South-East, place a bright warm light above the door, install a copper Vastu strip along the threshold, place two auspicious plants on either side, and hang a Panchamukhi Hanuman or Ganesha emblem above the lintel.",
    },
    "back_door": {
        "label": "Back Door / Patio Exit",
        "category": "indoor",
        "ideal_zones": ["NW", "W", "E", "N"],
        "acceptable_zones": ["SE", "NE"],
        "bad_zones": ["SW", "S", "Center"],
        "ideal_door_facing": ["N", "E", "NW", "W"],
        "why_simple": "The Back Door should allow air circulation without draining the stored wealth of the house. Keeping the Back Door slightly smaller than the Main Entrance and avoiding the South-West prevents money leakage.",
        "fix_if_wrong": "Keep a South-West or South back door closed when not in use, place a heavy earth-toned doormat inside, and ensure the Main Entrance is larger and brighter than the back door.",
    },
    "master_bedroom": {
        "label": "Master Bedroom",
        "category": "indoor",
        "ideal_zones": ["SW", "S"],
        "acceptable_zones": ["W"],
        "bad_zones": ["NE", "SE", "NW", "Center", "E", "N"],
        "why_simple": "The Master Bedroom belongs in the South-West (Earth element) or South so the head of the family enjoys grounded stability, deep sleep, command, and lasting marriage harmony.",
        "fix_if_wrong": "If the Master Bedroom is in North-East (causes health/clarity drain), South-East (Fire zone — causes couple arguments), or North-West (Air zone — causes restlessness), place the bed in the South-West corner of that room, sleep with your head South, use earthy beige bedsheets, and keep a pair of rose quartz or brass elephants on the side table.",
    },
    "bedroom": {
        "label": "Bedroom (Family / Children)",
        "category": "indoor",
        "ideal_zones": ["W", "S", "E", "NW"],
        "acceptable_zones": ["N", "SW"],
        "bad_zones": ["NE", "SE", "Center"],
        "why_simple": "West, South, East, and North-West provide restful sleep, study focus, and growth for family members and children.",
        "fix_if_wrong": "Position the bed so the sleeper's head points South or East (never North), avoid placing the bed directly under a beam, and use calming pastel colors.",
    },
    "guest_room": {
        "label": "Guest Bedroom",
        "category_type": "indoor",
        "category": "indoor",
        "ideal_zones": ["NW", "E", "N"],
        "acceptable_zones": ["W", "SE"],
        "bad_zones": ["SW", "Center", "NE"],
        "why_simple": "North-West is ruled by Vayu (Air/Movement) — it ensures guests feel warmly welcomed and comfortable, while never usurping the house owner's authority (which happens if guests sleep in the South-West).",
        "fix_if_wrong": "If the Guest Room is in the South-West, the house owner should occasionally use or store heavy personal items in that room so the owner retains primary Earth-zone authority.",
    },
    "living_room": {
        "label": "Living Room / Family Lounge",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N", "NW", "Center"],
        "acceptable_zones": ["W", "S"],
        "bad_zones": ["SW", "SE"],
        "why_simple": "The Living Room thrives in the bright, open, social zones (North, East, North-East, or North-West) where welcoming energy and conversation flow naturally.",
        "fix_if_wrong": "Place heavy sofas and entertainment cabinets against the South or West walls of the living room, leaving the North and East sides of the room more open, bright, and airy.",
    },
    "kitchen": {
        "label": "Kitchen",
        "category": "indoor",
        "ideal_zones": ["SE", "NW"],
        "acceptable_zones": ["E", "S"],
        "bad_zones": ["NE", "SW", "N", "W", "Center"],
        "why_simple": "The Kitchen is governed by Agni (Fire) and belongs in the South-East (Agneya) or secondarily the North-West (Vayavya). A kitchen in North-East clashes with Water, and in South-West destabilizes family health/finances.",
        "fix_if_wrong": "Without moving the kitchen: place the cooking stove in the South-East corner of the kitchen so the cook faces East; place a green marble slab or yellow stone under the stove if the kitchen is in NE/SW; and keep the kitchen sink (Water) as far from the stove (Fire) as possible.",
    },
    "bathroom": {
        "label": "Bathroom / Toilet",
        "category": "indoor",
        "ideal_zones": ["NW", "W", "S"],
        "acceptable_zones": ["SE", "E"],
        "bad_zones": ["NE", "SW", "Center", "N"],
        "why_simple": "Bathrooms and toilets handle waste disposal and belong in the North-West (Air/elimination) or West/South. A toilet in the North-East (Sacred Water/Jupiter) or Center (Brahmasthan) or South-West is a major Vastu defect.",
        "fix_if_wrong": "Zero-demolition fix: Keep the bathroom door shut at all times, keep a glass or ceramic bowl filled with natural crushed sea salt / rock salt on the tank or shelf (replace every Saturday), use an exhaust fan + green spider plant inside, and place a brass/copper Vastu strip outside the bathroom threshold.",
    },
    "storage": {
        "label": "Storage / Closet / Pantry",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "W", "NW"],
        "acceptable_zones": ["SE"],
        "bad_zones": ["NE", "E", "N", "Center"],
        "why_simple": "Heavy storage, closets, and pantries add physical weight — in Vastu, weight in the South-West, South, or West anchors stability, whereas clutter/weight in the North-East, North, or Center chokes prosperity.",
        "fix_if_wrong": "If a storage room is in the North, East, or North-East, keep the shelves light and neatly organized, remove all broken/unused items, and install a bright white LED light inside.",
    },
    "balcony": {
        "label": "Balcony / Veranda / Deck",
        "category": "indoor",
        "ideal_zones": ["NE", "N", "E"],
        "acceptable_zones": ["NW"],
        "bad_zones": ["SW", "S", "W", "SE", "Center"],
        "why_simple": "Balconies create open space and light. Having balconies in the North, East, or North-East invites morning solar prana and Kubera wealth energy.",
        "fix_if_wrong": "If your balcony is in the South or South-West, place heavy terracotta plant pots, bamboo blinds, or glass enclosures there to add weight and filter harsh afternoon rays.",
    },
    "dining_room": {
        "label": "Dining Room",
        "category": "indoor",
        "ideal_zones": ["W", "E", "S", "N"],
        "acceptable_zones": ["SE", "NW"],
        "bad_zones": ["SW", "NE", "Center"],
        "why_simple": "The West zone (ruled by Varuna/Saturn) and East zone promote nourishment, digestion, and family bonding over meals.",
        "fix_if_wrong": "Face East, North, or West while eating (avoid facing South while dining), and place a bowl of fresh fruit on the dining table to symbolize abundance.",
    },
    "puja_room": {
        "label": "Puja / Meditation / Sacred Altar",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["W", "Center"],
        "bad_zones": ["S", "SW", "SE", "NW"],
        "why_simple": "The North-East (Ishanya) is the supreme spiritual receptor of the home, ruled by Jupiter and Lord Shiva.",
        "fix_if_wrong": "Ensure you face East or North while praying, never place the altar against a shared bathroom wall, and keep a small copper kalash of water on the NE side of the altar.",
    },
    "study_room": {
        "label": "Study / Home Office",
        "category": "indoor",
        "ideal_zones": ["NE", "E", "N", "W"],
        "acceptable_zones": ["SW", "NW"],
        "bad_zones": ["SE", "Center"],
        "why_simple": "East (Sun), North (Mercury), North-East (Jupiter), and West (focused Saturn) sharpen memory, concentration, and career output.",
        "fix_if_wrong": "Position the desk so you face East, North, or North-East while working, with a solid wall behind your chair for support.",
    },
    "staircase": {
        "label": "Staircase",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "W"],
        "acceptable_zones": ["NW", "SE"],
        "bad_zones": ["NE", "Center", "N", "E"],
        "why_simple": "A staircase is a heavy structural element that belongs in the heavy Earth/West/South zones and should ideally ascend clockwise.",
        "fix_if_wrong": "Keep the area under the stairs clean (never put a toilet, kitchen, or altar under a staircase) and place a pair of copper pyramids at the base and top step.",
    },
    "safe_locker": {
        "label": "Safe / Cash Locker / Treasury",
        "category": "indoor",
        "ideal_zones": ["SW", "S", "N"],
        "acceptable_zones": ["W"],
        "bad_zones": ["SE", "NW", "NE", "Center", "E"],
        "why_simple": "A safe placed in the South-West (against the South wall so its door opens toward the North — Kubera's direction) locks in wealth and prevents unplanned expenses.",
        "fix_if_wrong": "Place a red cloth and a energized Shree Yantra / Gomti Chakra inside the safe, and place a small mirror inside so it reflects the cash/valuables.",
    },

    # ---------------- OUTDOOR LOT / YARD ITEMS ----------------
    "fence": {
        "label": "Outer Fence / Boundary Wall",
        "category": "outdoor",
        "ideal_zones": ["SW", "S", "W", "N", "E", "NE", "NW", "SE"],
        "acceptable_zones": ["Center"],
        "bad_zones": [],
        "why_simple": "A boundary fence protects the lot's energy field (Kshetra). In Vastu, the South and West boundary walls/fences should be slightly thicker, higher, or more solid, while the North, East, and North-East fences should allow more light and air.",
        "fix_if_wrong": "Keep the North-East and East fence clean, painted in light colors, or slightly more open/see-through, while making the South-West and South fence sturdy and privacy-shielded.",
    },
    "gate": {
        "label": "Main Lot Gate (Compound Entrance)",
        "category": "outdoor",
        "ideal_zones": ["NE", "E", "N"],
        "acceptable_zones": ["NW", "W"],
        "bad_zones": ["SW", "S", "SE", "Center"],
        "ideal_door_facing": ["NE", "E", "N"],
        "why_simple": "The Main Compound Gate determines how external opportunities enter the entire property lot. Gates in the North-East, East, or North bring prosperity and protection.",
        "fix_if_wrong": "If the lot gate is in the South or South-West, paint it in an earthy metallic or bronze tone, install two bright pillar lamps on both gateposts (lit every evening at sunset), and embed a copper rod/wire beneath the gate threshold.",
    },
    "parking_gate": {
        "label": "Parking Gate / Driveway / Garage",
        "category": "outdoor",
        "ideal_zones": ["NW", "SE", "E", "N"],
        "acceptable_zones": ["W"],
        "bad_zones": ["SW", "NE", "Center"],
        "ideal_door_facing": ["N", "E", "NW", "W"],
        "why_simple": "Vehicles represent movement (Vayu/Air) and heat/engine energy (Agni/Fire). North-West and South-East are the two best Vastu zones for a parking gate, driveway, or garage.",
        "fix_if_wrong": "If parking is in the North-East, keep the porch roof light/open so it doesn't block morning sunlight to the house; if in the South-West, park vehicles facing East or North and keep the driveway spotless.",
    },
    "trees": {
        "label": "Tall / Heavy Trees",
        "category": "outdoor",
        "ideal_zones": ["SW", "S", "W"],
        "acceptable_zones": ["NW", "SE"],
        "bad_zones": ["NE", "N", "E", "Center"],
        "why_simple": "Per Brihat Samhita (Vrikshayurveda), tall, dense, heavy-trunk trees belong in the South-West, South, and West of the lot where they block harsh afternoon heat and anchor Earth stability. Tall trees in the North-East or East block sacred morning sunlight!",
        "fix_if_wrong": "If you have tall trees in the North-East, East, or North of the lot, trim their lower/overhanging branches regularly so morning sunlight reaches the house unobstructed, and plant at least 2 heavier trees or tall bamboo/fencing in the South-West to balance the weight.",
    },
    "flowers": {
        "label": "Flower Beds / Flowering Plants",
        "category": "outdoor",
        "ideal_zones": ["NE", "E", "N", "NW", "SE"],
        "acceptable_zones": ["W", "S", "SW"],
        "bad_zones": ["Center"],
        "why_simple": "Fragrant and vibrant flowers activate Venus, Mercury, and Jupiter energies. Placing flower beds in the North, East, North-East, or North-West uplifts mental peace, social charm, and positive prana.",
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


def _coord_to_zone(cx: float, cy: float, compass_deg: float = 0.0) -> str:
    """Given normalized center coordinates (cx, cy) in [0..100] where (50, 50) is
    the center of the house/lot and top (y=0) is North when compass_deg=0,
    returns the Vastu zone: 'Center', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'."""
    dx = cx - 50.0
    dy = cy - 50.0
    dist = math.hypot(dx, dy)
    if dist < 11.5:
        return "Center"

    # Angle clockwise from Top (0° = top = North before rotation)
    angle_cw_from_top = (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0
    # Adjust for compass rotation (if North is rotated by compass_deg clockwise)
    rel_angle = (angle_cw_from_top - compass_deg + 360.0) % 360.0

    # 8 compass sectors of 45° each:
    # N: 337.5..22.5, NE: 22.5..67.5, E: 67.5..112.5, SE: 112.5..157.5,
    # S: 157.5..202.5, SW: 202.5..247.5, W: 247.5..292.5, NW: 292.5..337.5
    sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int(((rel_angle + 22.5) % 360.0) // 45.0)
    return sectors[idx]


def evaluate_visual_vastu_layout(
    items: List[Dict[str, Any]],
    house_shape: str = "square",
    has_outer_lot: bool = True,
    compass_rotation: float = 0.0,
    pos: Optional[Dict[str, Any]] = None,
    asc_lon: Optional[float] = None,
) -> Dict[str, Any]:
    """Evaluates a complete visual House + Outer-Lot Vastu diagram with any number
    of indoor rooms and outdoor yard items, returning a detailed Vastu score,
    shape analysis, item-by-item diagnostics, birth-chart synergy, and remedies."""
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

    # Optional birth chart cross-link
    lagna_idx = int(asc_lon // 30) % 12 if asc_lon is not None else None
    lagna_lord = SIGN_LORDS[lagna_idx] if lagna_idx is not None else None
    h9_lord = SIGN_LORDS[(lagna_idx + 8) % 12] if lagna_idx is not None else None

    evaluated_items: List[Dict[str, Any]] = []
    total_pts = 0
    max_pts = 0
    critical_doshas: List[str] = []
    auspicious_highlights: List[str] = []

    for idx, raw in enumerate(items, start=1):
        itype = str(raw.get("type", "living_room")).lower()
        rule = ITEM_RULES.get(itype, ITEM_RULES["living_room"])
        custom_label = raw.get("label") or rule["label"]
        cx = float(raw.get("x", 50.0)) + float(raw.get("w", 12.0)) / 2.0
        cy = float(raw.get("y", 50.0)) + float(raw.get("h", 12.0)) / 2.0
        door_dir = raw.get("door_dir") or ""
        area_scope = raw.get("scope") or rule["category"]  # 'indoor' or 'outdoor'

        zone = _coord_to_zone(cx, cy, compass_rotation)
        zone_meta = DIRECTION_META[zone]
        zone_planet = zone_meta["planet"]

        # Score the placement (out of 10)
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

        # Check Door / Gate Facing Direction if applicable
        door_note = ""
        if door_dir and "ideal_door_facing" in rule:
            if door_dir in rule["ideal_door_facing"]:
                pts = min(10, pts + 1)
                door_note = f" Door/Gate facing {door_dir} is highly auspicious (invites positive Prana)."
            elif door_dir in ("SW", "S"):
                pts = max(2, pts - 2)
                if status == "IDEAL / AUSPICIOUS":
                    status = "ACCEPTABLE (CHECK DOOR DIRECTION)"
                    badge_color = "neutral"
                door_note = f" Note: Door/Gate facing {door_dir} needs a threshold copper strip and bright overhead lamp."
            else:
                door_note = f" Door/Gate facing {door_dir} is moderate/balanced."

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

        if pts >= 9:
            auspicious_highlights.append(f"{custom_label} in {zone} ({zone_meta['name']}){door_note}")
        elif pts <= 4:
            critical_doshas.append(f"{custom_label} in {zone}: {rule['fix_if_wrong']}")

        total_pts += pts
        max_pts += 10

        evaluated_items.append({
            "index": idx,
            "type": itype,
            "label": custom_label,
            "scope": "Outer Lot / Yard" if area_scope == "outdoor" else "Inside House",
            "detected_zone": zone,
            "zone_full_name": zone_meta["name"],
            "zone_planet_and_element": f"{zone_planet} | {zone_meta['element']}",
            "door_or_gate_facing": door_dir or "N/A",
            "score_out_of_10": pts,
            "status": status,
            "badge_color": badge_color,
            "verdict_in_simple_words": verdict_summary + door_note,
            "why_this_rule_exists": rule["why_simple"],
            "ideal_zones_for_this_item": rule["ideal_zones"],
            "birth_chart_synergy": chart_synergy,
            "zero_demolition_remedy": "No remedy needed — keep clean, bright, and clutter-free!" if pts >= 9 else rule["fix_if_wrong"],
        })

    overall_score = round((total_pts / max_pts) * 100) if max_pts > 0 else 85
    if overall_score >= 82:
        overall_grade = "A+ (Vastu Siddha — High-Energy Prosperous Layout)"
    elif overall_score >= 68:
        overall_grade = "B+ (Harmonious Layout — Apply Simple Remedies to Reach 95%+)"
    else:
        overall_grade = "C (Multiple Elemental Clashes — Apply the Zero-Demolition Remedies Below)"

    return {
        "overall_vastu_score_percent": overall_score,
        "overall_grade": overall_grade,
        "house_shape_analysis": shape_info,
        "has_outer_lot": has_outer_lot,
        "compass_rotation_degrees": compass_rotation,
        "total_items_evaluated": len(evaluated_items),
        "auspicious_strengths": auspicious_highlights or ["Add rooms and lot features on the visual canvas to see strengths."],
        "critical_doshas_and_fixes": critical_doshas or ["Zero critical Vastu defects detected in the current placement!"],
        "item_by_item_breakdown": evaluated_items,
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

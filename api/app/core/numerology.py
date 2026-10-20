"""Numerology (Pythagorean & Chaldean), Lo Shu grid, Astro-Numerology Kundli synthesis,
Pinnacles, Challenges, Karmic Debts, Numbers to Avoid, Compound Vibrations, and Transit Harmonics."""
from __future__ import annotations
import math
from datetime import date as Date, datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

try:
    from . import ephem
    from .ephem import make_tz
    from .kundli import compute_kundli
except (ImportError, ValueError):
    from app.core import ephem
    from app.core.ephem import make_tz
    from app.core.kundli import compute_kundli

PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
CHALD = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [1,2,3,4,5,8,3,5,1,1,2,3,4,5,7,8,1,2,3,4,6,6,6,5,1,7]))
VOWELS = set("AEIOU")
MASTER = {11, 22, 33}

MEANING = {
    1: "Leader, independent, pioneering, ambitious, original",
    2: "Diplomat, cooperative, sensitive, intuitive, peaceful",
    3: "Creative, expressive, optimistic, joyful, inspiring",
    4: "Builder, disciplined, practical, orderly, steadfast",
    5: "Adventurer, freedom-loving, versatile, progressive, magnetic",
    6: "Nurturer, responsible, harmonious, loving, balanced",
    7: "Seeker, analytical, spiritual, introspective, wise",
    8: "Achiever, authoritative, material success, karmic balance, executive",
    9: "Humanitarian, compassionate, selfless, idealistic, global consciousness",
    11: "Master intuitive, visionary illumination, spiritual catalyst",
    22: "Master builder, practical idealist, architect of global systems",
    33: "Master teacher, universal compassion, selfless divine service"
}

PLANET = {
    1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu",
    5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"
}

PLANET_NUMBERS = {
    "Sun": 1, "Moon": 2, "Jupiter": 3, "Rahu": 4,
    "Mercury": 5, "Venus": 6, "Ketu": 7, "Saturn": 8, "Mars": 9
}

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

COLORS = {
    1: ["Gold", "Orange", "Bright Yellow"],
    2: ["White", "Silver", "Sea Green"],
    3: ["Yellow", "Saffron", "Golden Yellow"],
    4: ["Electric Blue", "Grey", "Smoky Blue"],
    5: ["Emerald Green", "Light Green", "Teal"],
    6: ["Pink", "Light Blue", "Sparkling White"],
    7: ["Smoky Grey", "Multi-colour", "Pastel Shades"],
    8: ["Dark Blue", "Black", "Dark Violet"],
    9: ["Crimson Red", "Scarlet", "Coral Pink"]
}

METALS = {
    1: "Gold", 2: "Silver", 3: "Gold / Brass", 4: "Alloy (Ashtadhatu)",
    5: "Bronze / Brass", 6: "Silver / Platinum", 7: "Alloy (Panchadhatu)", 8: "Iron / Lead", 9: "Copper / Gold"
}

GEMSTONES = {
    1: "Ruby (Manikya)", 2: "Pearl (Moti) / Moonstone", 3: "Yellow Sapphire (Pukhraj)",
    4: "Hessonite (Gomed)", 5: "Emerald (Panna)", 6: "Diamond (Heera) / White Zircon",
    7: "Cat's Eye (Lehsuniya)", 8: "Blue Sapphire (Neelam) / Amethyst", 9: "Red Coral (Moonga)"
}

DIRECTIONS = {
    1: "East", 2: "Northwest", 3: "Northeast", 4: "Southwest",
    5: "North", 6: "Southeast", 7: "South / Northwest", 8: "West", 9: "South"
}

MANTRAS = {
    1: "Om Hram Hreem Hroum Sah Suryaya Namah (ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः)",
    2: "Om Shram Shreem Shroum Sah Chandraya Namah (ॐ श्रां श्रीं श्रौं सः चन्द्राय नमः)",
    3: "Om Gram Greem Groum Sah Gurave Namah (ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः)",
    4: "Om Bhram Bhreem Bhroum Sah Rahave Namah (ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः)",
    5: "Om Bram Breem Broum Sah Budhaya Namah (ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः)",
    6: "Om Dram Dreem Droum Sah Shukraya Namah (ॐ द्रां द्रीं द्रौं सः शुक्राय नमः)",
    7: "Om Stram Streem Stroum Sah Ketave Namah (ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः)",
    8: "Om Pram Preem Proum Sah Shanaishcharaya Namah (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः)",
    9: "Om Kram Kreem Kroum Sah Bhaumaya Namah (ॐ क्रां क्रीं क्रौं सः भौमाय नमः)"
}

DAYS_OF_WEEK = {
    1: ["Sunday"], 2: ["Monday"], 3: ["Thursday"], 4: ["Saturday", "Wednesday"],
    5: ["Wednesday"], 6: ["Friday"], 7: ["Tuesday", "Thursday"], 8: ["Saturday"], 9: ["Tuesday"]
}

# Classical Anka Shastra Friendship & Enmity
FRIENDLY = {
    1: [1, 2, 3, 9],
    2: [1, 2, 3, 5],
    3: [1, 2, 3, 6, 9],
    4: [1, 5, 6, 7, 8],
    5: [1, 4, 5, 6],
    6: [3, 4, 5, 6, 9],
    7: [1, 4, 5, 6],
    8: [4, 5, 6, 8],
    9: [1, 2, 3, 6, 9]
}

# Inimical Numbers to strictly avoid (Shatru Anka)
INIMICAL = {
    1: [6, 8],
    2: [4, 7, 8],
    3: [6],
    4: [2, 9],
    5: [],
    6: [1, 2],
    7: [2],
    8: [1, 2, 9],
    9: [4, 5, 6]
}

# Neutral Numbers (Sama Anka)
NEUTRAL = {
    1: [4, 5, 7],
    2: [6, 9],
    3: [5, 7, 8],
    4: [3],
    5: [2, 3, 7, 8, 9],
    6: [7, 8],
    7: [3, 8, 9],
    8: [3, 7],
    9: [7, 8]
}

# Famous Compound Occult Vibrations (Cheiro & Vedic Tradition)
COMPOUND_VIBRATIONS = {
    10: {"title": "The Wheel of Fortune", "vibe": 1, "description": "Rise and fall, honor, faith, success in ambition and creative enterprise."},
    11: {"title": "The Clenched Hand", "vibe": 2, "description": "Master intuitive vibration; spiritual trials, visionary capacity, inspiration through adversity."},
    12: {"title": "The Sacrifice", "vibe": 3, "description": "Intellectual anxiety; spiritual devotion, learning self-mastery through surrender of personal pride."},
    13: {"title": "The Scepter of Transformation", "vibe": 4, "description": "Karmic Debt 13/4: Power achieved through meticulous discipline and relentless work ethic."},
    14: {"title": "The Magnetic Movement", "vibe": 5, "description": "Karmic Debt 14/5: Restless energy, financial caution; success through moderation and adaptable wisdom."},
    15: {"title": "The Magician / Alchemist", "vibe": 6, "description": "Magnetic eloquence, artistic charm, eloquence, mastery over material abundance and public goodwill."},
    16: {"title": "The Shattered Citadel", "vibe": 7, "description": "Karmic Debt 16/7: Destruction of the false ego; spiritual rebirth, supreme inner illumination after material illusion collapses."},
    17: {"title": "The Star of the Magi", "vibe": 8, "description": "Immense spiritual protection; rising above earthly trials, enduring immortality of name and deeds."},
    18: {"title": "Spiritual Conflict", "vibe": 9, "description": "Inner conflict between matter and spirit; warning against deceptive alliances, triumph through steadfast truth."},
    19: {"title": "The Prince of Heaven", "vibe": 1, "description": "Karmic Debt 19/1: One of the most fortunate vibrations; victory, radiant happiness, universal success and divine favor."},
    20: {"title": "The Awakening", "vibe": 2, "description": "Spiritual call to purpose; revival of higher consciousness, awakening of latent psychic and healing abilities."},
    21: {"title": "The Crown of the Magi", "vibe": 3, "description": "Total victory after prolonged endurance; advancement, honor, and triumphant realization of soul goals."},
    22: {"title": "The Master Architect", "vibe": 4, "description": "Master builder; capacity to materialize grand spiritual ideals into permanent earthly institutions."},
    23: {"title": "The Royal Star of the Lion", "vibe": 5, "description": "Supreme royal fortune, magnetic charisma, powerful protection from high authorities and effortless triumph over competitors."},
    24: {"title": "Venusian Harmony", "vibe": 6, "description": "Prosperous alliances, magnetic affection, domestic peace, and steady accumulation of enduring wealth."},
    25: {"title": "Strength Through Wisdom", "vibe": 7, "description": "Discrimination and spiritual victory achieved through trials, meditation, and keen observation."},
    26: {"title": "Partnership of Karma", "vibe": 8, "description": "Financial success through disciplined partnership; caution against reckless speculation and litigation."},
    27: {"title": "The Scepter of Command", "vibe": 9, "description": "Commanding intellect, creative brilliance, authority in leadership, and mastery over public assemblies."},
    28: {"title": "The Trusting Lamb", "vibe": 1, "description": "Great original talent; warning to exercise caution in partnerships and contracts."},
    29: {"title": "Spiritual Awakening Through Trials", "vibe": 2, "description": "Deeply spiritual and intuitive; tests in relationships that awaken profound emotional maturity."},
    30: {"title": "The Scholar / Philosopher", "vibe": 3, "description": "Philosophical contemplation, literary genius, and spiritual reflection; transcendent intellect."},
    31: {"title": "The Isolated Thinker", "vibe": 4, "description": "Independent intellect, self-reliant builder; overcoming isolation through collaborative devotion."},
    32: {"title": "The Star of Mercury", "vibe": 5, "description": "Dynamic commerce, eloquence, public acclaim, magnetic persuasion, and thriving commercial ventures."},
    33: {"title": "The Universal Avatar / Teacher", "vibe": 6, "description": "Master teacher of humanity; selfless compassion, healing presence, and devotion to the welfare of all beings."},
    37: {"title": "Good Fortune & Divine Love", "vibe": 1, "description": "Highly auspicious partnerships, sincere friends, fortunate domestic life, and profound spiritual joy."},
    41: {"title": "Dynamic Enterprise", "vibe": 5, "description": "Pioneering business leadership, inventive mind, rapid material advancement, and sharp executive acumen."},
    46: {"title": "Wisdom of the Sages", "vibe": 1, "description": "Sovereign knowledge, executive leadership, enduring wealth, and profound spiritual stature."},
    51: {"title": "The Warrior King", "vibe": 6, "description": "Extraordinary courage, decisive victory over obstacles, magnetic leadership, and pioneering breakthrough."},
    55: {"title": "Divine Alchemy", "vibe": 1, "description": "Profound intuition, supreme mental agility, breakthrough innovation, and transformative soul insight."}
}

KARMIC_DEBTS_INFO = {
    13: {
        "debt_number": "13/4",
        "title": "Karmic Debt of Discipline & Focused Labor",
        "past_life_cause": "Abuse of effort, laziness, shifting burdens onto others, or evading necessary duties in a prior incarnation.",
        "present_symptoms": "Feeling that one has to work twice as hard for ordinary recognition, obstacles appearing right before success, feeling trapped by rigid circumstances.",
        "soul_remedy": "Commit to uncompromising integrity, routine, and discipline. Never take shortcuts. Embrace systematic labor as divine worship."
    },
    14: {
        "debt_number": "14/5",
        "title": "Karmic Debt of Temperance & Sensory Freedom",
        "past_life_cause": "Misuse of personal freedom, sensory overindulgence, escapism, or violating the liberty of others.",
        "present_symptoms": "Extreme swings between strict rigidity and wild indulgence, restlessness, rapid loss of focus, temptations to escape through substances or erratic changes.",
        "soul_remedy": "Practice moderation, mindful self-control, and emotional constancy. Dedicate your versatile gifts to a high spiritual purpose."
    },
    16: {
        "debt_number": "16/7",
        "title": "Karmic Debt of Love, Humility & False Ego (The Tower)",
        "past_life_cause": "Vanity, intellectual arrogance, or deceit in matters of the heart and interpersonal love in past lifetimes.",
        "present_symptoms": "Sudden, dramatic collapses of material plans or relationships whenever arrogance takes root. The soul is forced into deep introspection.",
        "soul_remedy": "Cultivate genuine spiritual humility. Surrender the personal ego to divine will. Choose unconditional love over superficial validation."
    },
    19: {
        "debt_number": "19/1",
        "title": "Karmic Debt of Selfless Leadership & Compassion",
        "past_life_cause": "Tyrannical dominance, stubborn pride, and refusing to help or listen to others when in positions of power.",
        "present_symptoms": "Feeling isolated, having to solve problems completely alone, struggling with asking for support, resentment toward perceived helplessness.",
        "soul_remedy": "Learn to receive assistance with gratitude. Lead through humble service and selfless empowerment of others rather than solitary dominance."
    }
}

PINNACLE_INTERPRETATIONS = {
    1: "Pinnacle of Independence: Era of self-reliance, leadership, pioneering original ventures, and building self-confidence.",
    2: "Pinnacle of Partnership: Era of diplomacy, cooperation, patience, developing deep intuitive and relationship wisdom.",
    3: "Pinnacle of Creative Expression: Era of artistic breakthrough, optimism, communication, writing, and social joy.",
    4: "Pinnacle of Practical Foundation: Era of hard discipline, constructing enduring institutions, and financial consolidation.",
    5: "Pinnacle of Dynamic Freedom: Era of major travel, rapid changes, expanding horizons, adventure, and versatile enterprise.",
    6: "Pinnacle of Family & Service: Era of domestic fulfillment, community responsibility, unconditional love, and healing others.",
    7: "Pinnacle of Spiritual Wisdom: Era of deep study, meditation, specialization, philosophy, and metaphysical mastery.",
    8: "Pinnacle of Material Harvest: Era of executive authority, large-scale financial management, commercial triumph, and karmic justice.",
    9: "Pinnacle of Universal Humanitarianism: Era of global compassion, letting go of outdated attachments, and selfless service to humanity.",
    11: "Master Pinnacle of Vision: Era of heightened spiritual intuition, illuminating others, and channeling higher inspirations.",
    22: "Master Pinnacle of Architecture: Era of manifesting large-scale systems, visionary enterprise, and world-changing contributions."
}

CHALLENGE_INTERPRETATIONS = {
    0: "Challenge of Free Choice: The soul is tested in mastering all areas of life with supreme freedom; avoid apathy and aim high.",
    1: "Challenge of Self-Will: Overcoming feelings of dominance or inferiority; developing healthy self-worth without selfish aggression.",
    2: "Challenge of Over-Sensitivity: Overcoming hypersensitivity to criticism, fear of rejection, and learning emotional resilience in partnerships.",
    3: "Challenge of Self-Expression: Overcoming self-doubt, scattered energies, and superficiality; focusing creative expression with substance.",
    4: "Challenge of Practical Discipline: Overcoming resistance to routine, disorganization, or dogmatic rigidity; cultivating patient craftsmanship.",
    5: "Challenge of Freedom & Restlessness: Overcoming cravings for sensory escapism and fear of commitment; learning true inner liberty through self-mastery.",
    6: "Challenge of Ideals & Relationships: Overcoming perfectionism, possessiveness, or meddling; accepting loved ones as they are with compassionate grace.",
    7: "Challenge of Faith & Skepticism: Overcoming cynical intellectual pride, emotional aloofness, or spiritual melancholy; cultivating open-hearted faith.",
    8: "Challenge of Material Power: Overcoming greed, obsession with status, or fear of poverty; balancing spiritual values with ethical material stewardship."
}

LO_SHU_ARROWS_INFO = {
    "thought": {"name": "Arrow of Thought (4-3-8)", "numbers": [4, 3, 8], "positive": "Excellent analytical intellect, strategic planning, intellectual clarity.", "negative": "Arrow of Poor Memory / Hesitation: Struggle with systematic planning."},
    "will": {"name": "Arrow of Will (9-5-1)", "numbers": [9, 5, 1], "positive": "Tenacious perseverance, indomitable willpower, supreme resilience.", "negative": "Arrow of Frustration: Easily discouraged when immediate outcomes stall."},
    "action": {"name": "Arrow of Action (2-7-6)", "numbers": [2, 7, 6], "positive": "Dynamic execution, physical vitality, prompt decision-making.", "negative": "Arrow of Inactivity / Procrastination: Hesitation to put ideas into tangible action."},
    "intellect": {"name": "Arrow of Intellect (4-9-2)", "numbers": [4, 9, 2], "positive": "Superior memory, mental brilliance, quick retention of intricate details.", "negative": "Arrow of Forgetfulness: Struggle with retaining minutiae."},
    "spirituality": {"name": "Arrow of Soul & Emotion (3-5-7)", "numbers": [3, 5, 7], "positive": "Profound spiritual perception, deep empathy, inner serenity and compassion.", "negative": "Arrow of Skepticism / Emotional Turmoil: Vulnerability to melancholy or emotional doubt."},
    "practicality": {"name": "Arrow of Practicality (8-1-6)", "numbers": [8, 1, 6], "positive": "Exceptional business acumen, organizational craft, material discipline.", "negative": "Arrow of Disorder / Impracticality: Difficulty with financial or physical grounding."},
    "golden_success": {"name": "Arrow of Golden Prosperity (4-5-6)", "numbers": [4, 5, 6], "positive": "Extraordinary material and emotional fulfillment, balance of intellect, heart, and wealth.", "negative": "Missing Golden Arrow: Requires deliberate cultivation of harmony between heart and enterprise."},
    "silver_spirituality": {"name": "Arrow of Silver Spirituality (2-5-8)", "numbers": [2, 5, 8], "positive": "Fortunate in real estate, unwavering spiritual devotion, profound patience.", "negative": "Missing Silver Arrow: Requires conscious cultivation of emotional equilibrium."}
}

def reduce(n: int, keep_master: bool = True) -> int:
    """Reduce integer to single digit or master number (11, 22, 33)."""
    while n > 9 and not (keep_master and n in MASTER):
        n = sum(int(c) for c in str(n))
    return n

def reduce_single(n: int) -> int:
    """Strictly reduce to a single digit 1-9."""
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n

def name_sum(name: str, table: dict, which: str = "all") -> int:
    """Calculate raw numerical sum of letters using specified alphabet conversion table."""
    s = 0
    for c in name.upper():
        if c not in table:
            continue
        if which == "vowels" and c not in VOWELS:
            continue
        if which == "consonants" and c in VOWELS:
            continue
        s += table[c]
    return s

def check_karmic_debt(raw_val: int) -> Optional[int]:
    """Check if a raw sub-sum equals a classic Karmic Debt vibration (13, 14, 16, 19)."""
    if raw_val in {13, 14, 16, 19}:
        return raw_val
    while raw_val > 99:
        raw_val = sum(int(c) for c in str(raw_val))
    if raw_val in {13, 14, 16, 19}:
        return raw_val
    return None

def analyze_karmic_debts(dob: Date, name: str, table: dict) -> List[Dict[str, Any]]:
    """Detect and return detailed information on all Karmic Debt numbers present in the chart."""
    detected = []
    seen = set()

    if dob.day in {13, 14, 16, 19}:
        seen.add(dob.day)
        info = KARMIC_DEBTS_INFO[dob.day].copy()
        info["location"] = f"Birthday ({dob.day}th)"
        detected.append(info)

    y_sum = sum(int(c) for c in str(dob.year))
    m_sum = sum(int(c) for c in str(dob.month))
    d_sum = sum(int(c) for c in str(dob.day))
    combined_lp = reduce(y_sum) + reduce(m_sum) + reduce(d_sum)
    kd_lp = check_karmic_debt(combined_lp) or check_karmic_debt(sum(int(c) for c in dob.strftime("%Y%m%d")))
    if kd_lp and kd_lp not in seen:
        seen.add(kd_lp)
        info = KARMIC_DEBTS_INFO[kd_lp].copy()
        info["location"] = f"Life Path Number ({kd_lp})"
        detected.append(info)

    raw_expr = name_sum(name, table, "all")
    kd_expr = check_karmic_debt(raw_expr)
    if kd_expr and kd_expr not in seen:
        seen.add(kd_expr)
        info = KARMIC_DEBTS_INFO[kd_expr].copy()
        info["location"] = f"Expression Number ({kd_expr})"
        detected.append(info)

    raw_soul = name_sum(name, table, "vowels")
    kd_soul = check_karmic_debt(raw_soul)
    if kd_soul and kd_soul not in seen:
        seen.add(kd_soul)
        info = KARMIC_DEBTS_INFO[kd_soul].copy()
        info["location"] = f"Soul Urge Number ({kd_soul})"
        detected.append(info)

    return detected

def calculate_pinnacles_and_challenges(dob: Date, life_path_single: int) -> Dict[str, Any]:
    """Calculate the 4 major life Pinnacles and 4 Challenges with exact age milestones."""
    m_single = reduce_single(dob.month)
    d_single = reduce_single(dob.day)
    y_single = reduce_single(dob.year)

    p1 = reduce(m_single + d_single)
    p2 = reduce(d_single + y_single)
    p3 = reduce(p1 + p2)
    p4 = reduce(m_single + y_single)

    age_end_p1 = 36 - life_path_single
    age_end_p2 = age_end_p1 + 9
    age_end_p3 = age_end_p2 + 9

    c1 = abs(m_single - d_single)
    c2 = abs(d_single - y_single)
    c3 = abs(c1 - c2)
    c4 = abs(m_single - y_single)

    return {
        "pinnacles": [
            {"period": "1st Pinnacle (Foundation)", "age_span": f"Birth to age {age_end_p1}", "number": p1, "interpretation": PINNACLE_INTERPRETATIONS.get(reduce_single(p1), "")},
            {"period": "2nd Pinnacle (Productivity)", "age_span": f"Age {age_end_p1 + 1} to {age_end_p2}", "number": p2, "interpretation": PINNACLE_INTERPRETATIONS.get(reduce_single(p2), "")},
            {"period": "3rd Pinnacle (Maturity)", "age_span": f"Age {age_end_p2 + 1} to {age_end_p3}", "number": p3, "interpretation": PINNACLE_INTERPRETATIONS.get(reduce_single(p3), "")},
            {"period": "4th Pinnacle (Culmination)", "age_span": f"Age {age_end_p3 + 1} and beyond", "number": p4, "interpretation": PINNACLE_INTERPRETATIONS.get(reduce_single(p4), "")}
        ],
        "challenges": [
            {"period": "1st Challenge", "timing": f"Active during 1st Pinnacle (up to age {age_end_p1})", "number": c1, "interpretation": CHALLENGE_INTERPRETATIONS.get(c1, "")},
            {"period": "2nd Challenge", "timing": f"Active during 2nd Pinnacle (age {age_end_p1 + 1} to {age_end_p2})", "number": c2, "interpretation": CHALLENGE_INTERPRETATIONS.get(c2, "")},
            {"period": "Main / 3rd Challenge", "timing": "Lifelong core challenge", "number": c3, "interpretation": CHALLENGE_INTERPRETATIONS.get(c3, "")},
            {"period": "4th Challenge", "timing": f"Active during final Pinnacle (age {age_end_p3 + 1}+)", "number": c4, "interpretation": CHALLENGE_INTERPRETATIONS.get(c4, "")}
        ]
    }

def analyze_lo_shu_grid(dob: Date) -> Dict[str, Any]:
    """Analyze the complete 3x3 Lo Shu Magic Square with all 8 Planes & Arrows of Fortune."""
    digits = dob.strftime("%d%m%Y")
    counts = {str(i): digits.count(str(i)) for i in range(1, 10)}
    layout = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    missing = [i for i in range(1, 10) if counts[str(i)] == 0]

    arrows_present = []
    arrows_missing = []

    for k, v in LO_SHU_ARROWS_INFO.items():
        all_present = all(counts[str(num)] > 0 for num in v["numbers"])
        all_absent = all(counts[str(num)] == 0 for num in v["numbers"])
        if all_present:
            arrows_present.append({"arrow": v["name"], "status": "Active Strength", "description": v["positive"]})
        elif all_absent:
            arrows_missing.append({"arrow": v["name"], "status": "Karmic Lesson", "description": v["negative"]})

    return {
        "counts": counts,
        "layout": layout,
        "missing_numbers": missing,
        "arrows_present": arrows_present,
        "arrows_missing": arrows_missing
    }

def generate_compound_numbers(root_number: int) -> List[Dict[str, Any]]:
    """Return all double-digit compound vibrations that reduce to the given root number."""
    r = reduce_single(root_number)
    results = []
    for comp in sorted(COMPOUND_VIBRATIONS.keys()):
        if reduce_single(comp) == r:
            info = COMPOUND_VIBRATIONS[comp].copy()
            info["compound"] = comp
            results.append(info)
    return results

def get_numbers_to_avoid(moolank: int, bhagyank: int) -> Dict[str, Any]:
    """Identify inimical numbers, unfavorable dates, and discordant days/colors to avoid."""
    m_avoid = INIMICAL.get(moolank, [])
    b_avoid = INIMICAL.get(bhagyank, [])
    combined_avoid = sorted(list(set(m_avoid + b_avoid)))

    dates_to_avoid = []
    for day in range(1, 32):
        if reduce_single(day) in combined_avoid:
            dates_to_avoid.append(day)

    avoid_planets = [PLANET.get(num, "") for num in combined_avoid]
    avoid_colors = []
    for num in combined_avoid:
        avoid_colors.extend(COLORS.get(num, []))

    return {
        "inimical_numbers": combined_avoid,
        "dates_of_month_to_avoid": dates_to_avoid,
        "inimical_planetary_rulers": avoid_planets,
        "colors_to_avoid": list(dict.fromkeys(avoid_colors)),
        "guidance": "Avoid commencing major contracts, wedding registrations, property purchases, long travel, or medical surgeries on dates governed by these numbers."
    }

def generate_lucky_bundle(moolank: int, bhagyank: int, name_number: int) -> Dict[str, Any]:
    """Generate the full lucky numbers portfolio including power dates, days, gemstones, and mantras."""
    m_friends = FRIENDLY.get(moolank, [])
    b_friends = FRIENDLY.get(bhagyank, [])
    core_lucky = sorted(list(set(m_friends).intersection(set(b_friends))))
    if not core_lucky:
        core_lucky = sorted(list(set([moolank, bhagyank])))

    lucky_dates = []
    for day in range(1, 32):
        if reduce_single(day) in core_lucky:
            lucky_dates.append(day)

    lucky_days = []
    for num in core_lucky:
        lucky_days.extend(DAYS_OF_WEEK.get(num, []))
    lucky_days = list(dict.fromkeys(lucky_days))

    compound_lucky = []
    for num in core_lucky:
        compound_lucky.extend(generate_compound_numbers(num))

    ruler = PLANET.get(moolank, "Sun")

    return {
        "primary_lucky_number": moolank,
        "destiny_lucky_number": bhagyank,
        "name_lucky_number": name_number,
        "harmonized_lucky_roots": core_lucky,
        "lucky_calendar_dates": lucky_dates,
        "lucky_days_of_week": lucky_days,
        "compound_power_numbers": compound_lucky,
        "ruling_planet": ruler,
        "lucky_colors": COLORS.get(moolank, []),
        "lucky_gemstone": GEMSTONES.get(moolank, ""),
        "lucky_metal": METALS.get(moolank, ""),
        "auspicious_direction": DIRECTIONS.get(moolank, ""),
        "vedic_beej_mantra": MANTRAS.get(moolank, "")
    }

def analyze_current_transits_numerology(dob: Date, transit_date: Optional[Date] = None) -> Dict[str, Any]:
    """Calculate real-time Gochar transit numerology, personal day/month/year, and today's lucky numbers."""
    t_date = transit_date or Date.today()

    univ_year = reduce_single(t_date.year)
    univ_month = reduce_single(t_date.month + univ_year)
    univ_day = reduce_single(t_date.day + univ_month)

    pers_year = reduce_single(reduce_single(dob.month) + reduce_single(dob.day) + reduce_single(t_date.year))
    pers_month = reduce_single(pers_year + t_date.month)
    pers_day = reduce_single(pers_month + t_date.day)

    transit_planet_strengths = []
    try:
        dt_utc = datetime(t_date.year, t_date.month, t_date.day, 12, 0, tzinfo=timezone.utc)
        jd = ephem.jd_from_utc(dt_utc)
        all_pos = ephem.all_positions(jd, sidereal=True)
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if p_name in all_pos:
                lon = all_pos[p_name]["longitude"]
                s_idx = int(lon / 30) % 12
                s_name = ephem.SIGNS[s_idx]
                p_num = PLANET_NUMBERS.get(p_name, 1)
                transit_planet_strengths.append({
                    "planet": p_name,
                    "number": p_num,
                    "current_sign": s_name,
                    "degree": round(lon % 30, 2)
                })
    except Exception:
        pass

    moolank = reduce_single(dob.day)

    day_friends = FRIENDLY.get(pers_day, [pers_day])
    today_lucky = sorted(list(set(day_friends).intersection(set(FRIENDLY.get(moolank, [moolank])))))
    if not today_lucky:
        today_lucky = [pers_day, moolank]

    nine_year_cycle_meaning = {
        1: "Year of Fresh Beginnings: Plant new seeds, initiate ambitious projects, take bold leadership.",
        2: "Year of Patience & Cooperation: Cultivate relationships, practice diplomacy, allow foundations to take root.",
        3: "Year of Creative Expansion: Social growth, self-expression, joyful networking, and creative breakthroughs.",
        4: "Year of Solid Foundations: Discipline, relentless focus, hard work, and organizing long-term security.",
        5: "Year of Freedom & Dynamic Change: Unexpected travel, expansion of horizons, adaptability, and shedding old ruts.",
        6: "Year of Love & Domestic Responsibility: Home, family, community duty, marriage, healing, and nurturing others.",
        7: "Year of Spiritual Introspection: Solitude, deep study, soul-searching, meditation, and inner revelation.",
        8: "Year of Material Harvest & Executive Power: Commercial triumph, financial expansion, leadership, and karmic rewards.",
        9: "Year of Completion & Humanitarian Release: Forgiveness, wrapping up outdated cycles, charity, and preparing for rebirth."
    }

    return {
        "transit_date": t_date.isoformat(),
        "universal_cycle": {"year": univ_year, "month": univ_month, "day": univ_day},
        "personal_cycle": {
            "personal_year": pers_year,
            "personal_month": pers_month,
            "personal_day": pers_day,
            "nine_year_cycle_phase": f"Year {pers_year} of 9",
            "personal_year_theme": nine_year_cycle_meaning.get(pers_year, ""),
            "today_energy_theme": MEANING.get(pers_day, "")
        },
        "transit_harmonized_lucky_numbers": today_lucky,
        "today_lucky_color": COLORS.get(pers_day, ["White"])[0],
        "planetary_transits": transit_planet_strengths
    }

def synthesize_astro_numerology(k: Dict[str, Any], moolank: int, bhagyank: int, namank: int) -> Dict[str, Any]:
    """Synthesize the Vedic astrological chart (Kundli) with Numerology (Anka Vidya)."""
    lagna_sign = k["lagna"]["sign"]
    lagna_lord = k["lagna"].get("sign_lord", SIGN_LORDS.get(lagna_sign, "Moon"))
    lagna_num = PLANET_NUMBERS.get(lagna_lord, 1)

    moon_p = next((p for p in k["planets"] if p["name"] == "Moon"), None)
    moon_sign = moon_p["sign"] if moon_p else "Aries"
    moon_lord = moon_p.get("sign_lord", SIGN_LORDS.get(moon_sign, "Moon"))
    moon_num = PLANET_NUMBERS.get(moon_lord, 2)

    nak_name = moon_p["nakshatra"] if moon_p else "Ashwini"
    nak_lord = moon_p.get("nakshatra_lord", "Ketu")
    nak_num = PLANET_NUMBERS.get(nak_lord, 7)

    sun_p = next((p for p in k["planets"] if p["name"] == "Sun"), None)
    sun_sign = sun_p["sign"] if sun_p else "Aries"
    sun_lord = sun_p.get("sign_lord", SIGN_LORDS.get(sun_sign, "Sun"))
    sun_num = PLANET_NUMBERS.get(sun_lord, 1)

    ak_name = k.get("jaimini", {}).get("chara_karakas", {}).get("Atmakaraka", "Sun")
    ak_num = PLANET_NUMBERS.get(ak_name, 1)

    active_dasha_lord = "Jupiter"
    active_antar_lord = "Sun"
    if k.get("current_dasha"):
        active_dasha_lord = k["current_dasha"][0].get("lord", "Jupiter")
        if len(k["current_dasha"]) > 1:
            active_antar_lord = k["current_dasha"][1].get("lord", "Sun")
    dasha_num = PLANET_NUMBERS.get(active_dasha_lord, 3)
    antar_num = PLANET_NUMBERS.get(active_antar_lord, 1)

    harmony_pts = 0
    if moolank in FRIENDLY.get(lagna_num, []):
        harmony_pts += 30
    elif moolank not in INIMICAL.get(lagna_num, []):
        harmony_pts += 18
    else:
        harmony_pts += 8

    if moolank in FRIENDLY.get(moon_num, []):
        harmony_pts += 25
    elif moolank not in INIMICAL.get(moon_num, []):
        harmony_pts += 15
    else:
        harmony_pts += 5

    if bhagyank in FRIENDLY.get(lagna_num, []):
        harmony_pts += 25
    elif bhagyank not in INIMICAL.get(lagna_num, []):
        harmony_pts += 15
    else:
        harmony_pts += 5

    if namank in FRIENDLY.get(lagna_num, []) or namank in FRIENDLY.get(moon_num, []):
        harmony_pts += 20
    else:
        harmony_pts += 10

    harmony_pct = min(harmony_pts, 100)

    if harmony_pct >= 85:
        verdict = "Divine Cosmic Harmony: Your physical, mental, and numerical vibrations resonate in extraordinary alignment with your planetary chart."
    elif harmony_pct >= 70:
        verdict = "Strong Auspicious Resonance: Favorable alignment between your planetary lords and core numbers. Fosters steady progress and spiritual resilience."
    elif harmony_pct >= 55:
        verdict = "Moderate Dynamic Alignment: Certain planetary energies require conscious harmonization through lucky gemstones and prescribed japa mantras."
    else:
        verdict = "Karmic Friction: Discordant vibrations between your psychic number and chart rulers. Strictly practice planetary remedies and avoid inimical numbers."

    return {
        "lagna": {"sign": lagna_sign, "lord": lagna_lord, "number": lagna_num},
        "chandra_rashi": {"sign": moon_sign, "lord": moon_lord, "number": moon_num},
        "janma_nakshatra": {"name": nak_name, "lord": nak_lord, "number": nak_num},
        "surya_rashi": {"sign": sun_sign, "lord": sun_lord, "number": sun_num},
        "atmakaraka": {"planet": ak_name, "number": ak_num},
        "active_mahadasha_lord": {"planet": active_dasha_lord, "number": dasha_num},
        "active_antardasha_lord": {"planet": active_antar_lord, "number": antar_num},
        "cosmic_harmony_score_percent": harmony_pct,
        "concordance_verdict": verdict,
        "astro_lucky_numbers": sorted(list(set([moolank, bhagyank, lagna_num, moon_num, ak_num]))),
        "astro_remedy": {
            "primary_deity_mantra": MANTRAS.get(lagna_num, ""),
            "primary_gemstone": GEMSTONES.get(lagna_num, ""),
            "favorable_metal": METALS.get(lagna_num, "")
        }
    }

def profile(name: str, dob: Date, system: str = "pythagorean", birth_details: Optional[Dict[str, Any]] = None, transit_date: Optional[Date] = None) -> Dict[str, Any]:
    """Compute the master Numerology profile, combining core vibrations, Lo Shu grid,
    karmic analysis, 4 pinnacles/challenges, numbers to avoid, lucky numbers generator,
    and optional full Vedic Kundli Astro-Numerology synthesis."""
    t = PYTH if system == "pythagorean" else CHALD
    life = reduce(reduce(dob.year) + reduce(dob.month) + reduce(dob.day))
    expr = reduce(name_sum(name, t))
    soul = reduce(name_sum(name, t, "vowels"))
    pers = reduce(name_sum(name, t, "consonants"))
    birthday = reduce(dob.day)

    psychic = reduce_single(dob.day)
    destiny_vedic = reduce_single(sum(int(c) for c in dob.strftime("%d%m%Y")))
    name_num_chaldean = reduce_single(name_sum(name, CHALD))
    maturity = reduce(life + expr)

    letter_counts = {i: 0 for i in range(1, 10)}
    for c in name.upper():
        if c in t:
            letter_counts[t[c]] += 1
    karmic_lessons = [num for num, cnt in letter_counts.items() if cnt == 0]
    hidden_passion = max(letter_counts, key=letter_counts.get) if any(letter_counts.values()) else psychic

    karmic_debts = analyze_karmic_debts(dob, name, t)
    pinnacles_challenges = calculate_pinnacles_and_challenges(dob, reduce_single(life))
    lo_shu = analyze_lo_shu_grid(dob)
    lucky_bundle = generate_lucky_bundle(psychic, destiny_vedic, name_num_chaldean)
    avoid_bundle = get_numbers_to_avoid(psychic, destiny_vedic)
    transits = analyze_current_transits_numerology(dob, transit_date)

    astro_synthesis = None
    if birth_details and birth_details.get("latitude") and birth_details.get("longitude"):
        try:
            tz_obj = make_tz(birth_details.get("timezone", "Asia/Kolkata"), birth_details.get("utc_offset", 5.5))
            tm_str = birth_details.get("time", "12:00:00")
            if len(tm_str) == 5:
                tm_str += ":00"
            t_obj = datetime.strptime(tm_str, "%H:%M:%S").time()
            dt_loc = datetime.combine(dob, t_obj)
            dt_utc = dt_loc.replace(tzinfo=tz_obj).astimezone(timezone.utc)
            k = compute_kundli(dt_utc, birth_details["latitude"], birth_details["longitude"], tz_obj, dasha_levels=1)
            astro_synthesis = synthesize_astro_numerology(k, psychic, destiny_vedic, name_num_chaldean)
        except Exception:
            pass

    return {
        "name": name,
        "date_of_birth": dob.isoformat(),
        "system": system,
        "life_path": {"number": life, "meaning": MEANING.get(life)},
        "expression_destiny": {"number": expr, "meaning": MEANING.get(expr)},
        "soul_urge": {"number": soul, "meaning": MEANING.get(soul)},
        "personality": {"number": pers, "meaning": MEANING.get(pers)},
        "birthday": birthday,
        "maturity": maturity,
        "vedic": {
            "psychic_number_moolank": psychic,
            "destiny_number_bhagyank": destiny_vedic,
            "ruling_planet": PLANET[psychic],
            "name_number_chaldean": name_num_chaldean
        },
        "lucky": {
            "numbers": FRIENDLY[psychic],
            "colors": COLORS[psychic],
            "planet": PLANET[psychic]
        },
        "lo_shu_grid": lo_shu,
        "karmic_debts": karmic_debts,
        "karmic_lessons": karmic_lessons,
        "hidden_passion_number": hidden_passion,
        "life_epochs": pinnacles_challenges,
        "numbers_to_avoid": avoid_bundle,
        "lucky_numbers_generator": lucky_bundle,
        "transits_numerology": transits,
        "astro_numerology": astro_synthesis
    }

def daily(dob: Date, on: Date) -> Dict[str, Any]:
    """Daily numerological forecast."""
    personal_year = reduce(reduce(dob.month) + reduce(dob.day) + reduce(on.year), False)
    pm = reduce(personal_year + on.month, False)
    pd = reduce(pm + on.day, False)
    return {
        "date": on.isoformat(),
        "personal_year": personal_year,
        "personal_month": pm,
        "personal_day": pd,
        "theme": MEANING[pd],
        "lucky_color": COLORS[pd][0]
    }

def compatibility(n1: str, d1: Date, n2: str, d2: Date) -> Dict[str, Any]:
    """Numerological compatibility analysis."""
    a, b = profile(n1, d1), profile(n2, d2)
    la, lb = a["vedic"]["psychic_number_moolank"], b["vedic"]["psychic_number_moolank"]
    score = 0
    score += 40 if lb in FRIENDLY[la] else 15
    score += 30 if la in FRIENDLY[lb] else 10
    score += 30 if a["life_path"]["number"] % 9 == b["life_path"]["number"] % 9 or b["life_path"]["number"] in FRIENDLY.get(reduce(a["life_path"]["number"], False), []) else 10
    return {
        "person1": {"name": n1, "moolank": la, "life_path": a["life_path"]["number"]},
        "person2": {"name": n2, "moolank": lb, "life_path": b["life_path"]["number"]},
        "score_percent": min(score, 100)
    }

def biorhythm(dob: Date, on: Date, days: int = 1) -> List[Dict[str, Any]]:
    """Biorhythm calculations for physical, emotional, intellectual, intuitive cycles."""
    out = []
    for k in range(days):
        n = (on - dob).days + k
        out.append({
            "day_offset": k,
            "days_alive": n,
            "physical": round(math.sin(2 * math.pi * n / 23), 4),
            "emotional": round(math.sin(2 * math.pi * n / 28), 4),
            "intellectual": round(math.sin(2 * math.pi * n / 33), 4),
            "intuitive": round(math.sin(2 * math.pi * n / 38), 4)
        })
    return out

ANGEL = {
    "0": "Infinite potential and new beginnings",
    "1": "Manifest your thoughts; new start",
    "2": "Balance, trust, partnership",
    "3": "Creativity and encouragement",
    "4": "Stability and protection",
    "5": "Change is coming",
    "6": "Home, family, care",
    "7": "Spiritual awakening, luck",
    "8": "Abundance and karma",
    "9": "Completion and service"
}

def angel_number(num: str) -> Dict[str, Any]:
    """Angel number analysis and message."""
    if not num.isdigit():
        raise ValueError("digits only")
    return {
        "number": num,
        "core": ANGEL.get(num[0], ""),
        "digit_root": reduce(int(num), False),
        "message": "; ".join(dict.fromkeys(ANGEL[c] for c in num if c in ANGEL))
    }

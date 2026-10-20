"""Comprehensive Classical Astrological Interpretations Corpus.

Contains non-plagiarized, professionally synthesized Vedic readings for:
- 144 House Lord Combinations (Lord 1 to 12 in Houses 1 to 12)
- 12 Houses Shad Phala (Auspicious vs Inauspicious House Balance)
- 12 Ascendant Profiles
- Holistic Astrological Report Assembler
"""
from __future__ import annotations
from typing import Dict, List, Any
from .ephem import SIGNS, RASHIS, SIGN_LORDS
from .classical_interpretations import (
    get_house_lord_sloka,
    get_navamsha_interpretation,
    get_22nd_drekkana_interpretation
)

# 12 Ascendants
ASCENDANTS = {
    0: {
        "name": "Mesha", "sign": "Aries", "ruler": "Mars", "element": "Cardinal Fire",
        "portrait": "A dynamic, pioneering individual with sharp initiative, moral courage, and executive drive. Thrives in competitive or leadership environments where independence is valued.",
        "key_strengths": "Fearless leadership, rapid problem solving, physical resilience, straightforward honesty.",
        "growth_areas": "Patience with slower paced collaborators, avoiding rash decisions, temper balance."
    },
    1: {
        "name": "Vrishabha", "sign": "Taurus", "ruler": "Venus", "element": "Fixed Earth",
        "portrait": "An enduring, practical, and aesthetically refined personality with immense perseverance and determination. Attuned to beauty, material security, and family stability.",
        "key_strengths": "Steady loyalty, financial prudence, sensory appreciation, reliable productivity.",
        "growth_areas": "Adaptability to sudden shifts, releasing prolonged resentments, avoiding complacency."
    },
    2: {
        "name": "Mithuna", "sign": "Gemini", "ruler": "Mercury", "element": "Dual Air",
        "portrait": "An intellectually versatile, inquisitive, and eloquent communicator. Possesses a multifaceted mind that readily synthesizes diverse streams of knowledge and media.",
        "key_strengths": "Exceptional communication, rapid learning, commercial acumen, witty social charm.",
        "growth_areas": "Sustained focus on single long-term goals, calming nervous energy, mental grounding."
    },
    3: {
        "name": "Karka", "sign": "Cancer", "ruler": "Moon", "element": "Cardinal Water",
        "portrait": "A deeply empathetic, protective, and emotionally intuitive individual anchored by strong domestic roots, ancestral memory, and nurturing devotion to loved ones.",
        "key_strengths": "Emotional intelligence, deep loyalty, protective instincts, strong cultural memory.",
        "growth_areas": "Shielding against emotional fluctuations, letting go of past wounds, boundary setting."
    },
    4: {
        "name": "Simha", "sign": "Leo", "ruler": "Sun", "element": "Fixed Fire",
        "portrait": "A dignified, honorable, and magnanimous personality possessing natural regal authority, creative warmth, and inspiring executive leadership.",
        "key_strengths": "Natural authority, generous warmth, high ethical standards, magnetic charisma.",
        "growth_areas": "Humility when receiving counsel, moderating pride, sharing the spotlight."
    },
    5: {
        "name": "Kanya", "sign": "Virgo", "ruler": "Mercury", "element": "Dual Earth",
        "portrait": "A meticulous, analytical, and service-oriented mind dedicated to craftsmanship, diagnostic precision, organizational efficiency, and practical problem solving.",
        "key_strengths": "Diagnostic acuity, organizational mastery, practical wisdom, thorough diligence.",
        "growth_areas": "Overcoming excessive self-criticism, accepting imperfect outcomes, avoiding worry."
    },
    6: {
        "name": "Tula", "sign": "Libra", "ruler": "Venus", "element": "Cardinal Air",
        "portrait": "A judicious, charming, and harmony-seeking diplomat committed to fair partnerships, aesthetic balance, strategic mediation, and equitable collaboration.",
        "key_strengths": "Strategic negotiation, refined aesthetic taste, partnership harmony, objective fairness.",
        "growth_areas": "Decisive firmness without prolonged vacillation, confronting necessary conflicts."
    },
    7: {
        "name": "Vrishchika", "sign": "Scorpio", "ruler": "Mars & Ketu", "element": "Fixed Water",
        "portrait": "An intensely perceptive, resilient, and transformative personality with penetrating insight, profound loyalty, and an unyielding will in times of crisis.",
        "key_strengths": "Psychological depth, crisis endurance, unwavering focus, transformative renewal.",
        "growth_areas": "Willingness to trust, releasing suspicion, practicing open vulnerability."
    },
    8: {
        "name": "Dhanu", "sign": "Sagittarius", "ruler": "Jupiter", "element": "Dual Fire",
        "portrait": "An optimistic, principled, and visionary seeker guided by philosophical wisdom, higher ethics, love of truth, and broad exploratory enthusiasm.",
        "key_strengths": "Philosophical optimism, inspiring mentorship, ethical integrity, expansive vision.",
        "growth_areas": "Attention to fine administrative details, diplomatic restraint in speech."
    },
    9: {
        "name": "Makara", "sign": "Capricorn", "ruler": "Saturn", "element": "Cardinal Earth",
        "portrait": "A disciplined, prudent, and patient builder with exceptional strategic endurance. Steadily constructs enduring achievements through hard work and responsibility.",
        "key_strengths": "Formidable endurance, institutional competence, mature patience, long-term mastery.",
        "growth_areas": "Allowing joy and play into the schedule, avoiding emotional austerity."
    },
    10: {
        "name": "Kumbha", "sign": "Aquarius", "ruler": "Saturn & Rahu", "element": "Fixed Air",
        "portrait": "A forward-thinking, humanitarian, and intellectually original reformer dedicated to collective progress, scientific systems, and progressive social ideals.",
        "key_strengths": "Broad visionary perspective, egalitarian values, innovative problem solving.",
        "growth_areas": "Connecting on intimate one-on-one emotional levels, avoiding cold detachment."
    },
    11: {
        "name": "Meena", "sign": "Pisces", "ruler": "Jupiter", "element": "Dual Water",
        "portrait": "A compassionate, imaginative, and spiritually receptive soul possessing deep artistic sensibility, transcendental intuition, and gentle philosophical benevolence.",
        "key_strengths": "Profound empathy, creative imagination, intuitive wisdom, spiritual selflessness.",
        "growth_areas": "Practical boundary enforcement, financial realism, maintaining daily discipline."
    }
}

# 12 Houses Shad Phala Significations & Interpretations
HOUSE_PHALA = {
    1: {
        "title": "1st House: Tanu Bhava (Vitality & Self)",
        "favorable": "Strong bodily constitution, radiant presence, high confidence, dignified reputation, and energetic self-direction.",
        "challenging": "Physical fatigue, fluctuating vitality, self-doubt, or wandering aimlessly without grounded direction."
    },
    2: {
        "title": "2nd House: Dhana Bhava (Wealth & Heritage)",
        "favorable": "Steady financial accumulation, persuasive and melodious speech, domestic harmony, and wholesome nourishment.",
        "challenging": "Financial volatility, sharp or contentious speech, family misunderstandings, and dietary imbalances."
    },
    3: {
        "title": "3rd House: Sahaja Bhava (Courage & Enterprise)",
        "favorable": "Bold initiatives, supportive siblings, literary and media skill, effective communication, and muscular vitality.",
        "challenging": "Hesitation in critical moments, strained sibling relationships, fruitless travel, or shoulder/ear discomforts."
    },
    4: {
        "title": "4th House: Bandhu Bhava (Home & Emotional Peace)",
        "favorable": "Landed property acquisition, vehicular comfort, maternal blessings, deep emotional contentment, and academic success.",
        "challenging": "Domestic discord, maternal health concerns, property litigations, and lingering emotional unrest."
    },
    5: {
        "title": "5th House: Putra Bhava (Intellect & Legacy)",
        "favorable": "Brilliant analytical intellect, virtuous and accomplished children, creative mastery, intuitive wisdom, and good counsel.",
        "challenging": "Speculative losses, anxieties regarding children, interrupted higher studies, or ethical wavering."
    },
    6: {
        "title": "6th House: Ari Bhava (Service & Overcoming Adversity)",
        "favorable": "Triumph over competitors, resilient immune defense, efficient conflict resolution, and excellence in professional service.",
        "challenging": "Susceptibility to chronic ailments, debt obligations, workplace friction, or unnecessary disputes."
    },
    7: {
        "title": "7th House: Yuvati Bhava (Partnerships & Trade)",
        "favorable": "Devoted and capable spouse, harmonious business alliances, profitable public dealings, and beneficial foreign travel.",
        "challenging": "Marital discord, partnership mistrust, contractual misunderstandings, or reproductive imbalances."
    },
    8: {
        "title": "8th House: Randhra Bhava (Transformation & Longevity)",
        "favorable": "Long life expectancy, unexpected inheritances, deep esoteric insight, and triumphant emergence from major life transitions.",
        "challenging": "Susceptibility to sudden crises, chronic psychological stress, hidden obstructions, or inheritance disputes."
    },
    9: {
        "title": "9th House: Dharma Bhava (Fortune & Higher Truth)",
        "favorable": "Divine protective grace, esteemed mentors and teachers, righteous wealth, successful pilgrimages, and honorable fatherly blessings.",
        "challenging": "Philosophical confusion, distance from father or mentors, ethical doubts, or delayed travel fortunes."
    },
    10: {
        "title": "10th House: Karma Bhava (Career & Public Eminence)",
        "favorable": "Executive authority, professional distinction, public respect, ethical leadership, and enduring societal contributions.",
        "challenging": "Career instability, friction with institutional superiors, reputational challenges, or vocational disillusionment."
    },
    11: {
        "title": "11th House: Labha Bhava (Gains & Social Networks)",
        "favorable": "Abundant income streams, influential social network, realization of major aspirations, and affectionate elder siblings.",
        "challenging": "Delayed gains, unreliable friends, frustrated desires, or economic dependency on fluctuating networks."
    },
    12: {
        "title": "12th House: Vyaya Bhava (Liberation & Global Horizons)",
        "favorable": "Peaceful sleep, spiritual detachment, charitable generosity, profitable overseas settlements, and meditative illumination.",
        "challenging": "Unavoidable expenditures, sleep disturbances, feelings of isolation, or excessive material loss."
    }
}

# 144 House Lord Placements Matrix: { (lord_house, pos_house): "interpretation" }
# Generates concise, non-plagiarized classical summaries
def get_house_lord_reading(lord_house: int, pos_house: int) -> str:
    """Returns the classical interpretation for the lord of house L placed in house P."""
    # Classical archetypes from Parashari & Jaimini principles
    if lord_house == pos_house:
        return f"Lord of House {lord_house} in its own house establishes a robust foundation for all significations of this house, granting stability, dignity, and natural self-reliance in this domain."

    # Specific key combinations
    special_cases = {
        (1, 2): "The Lagna lord in the 2nd house makes the native focused on financial accumulation, family lineage, and articulate speech, generating self-earned wealth.",
        (1, 4): "The Lagna lord in the 4th house grants strong domestic happiness, vehicular comforts, property gains, and deep devotion to maternal heritage.",
        (1, 5): "The Lagna lord in the 5th house confers high intelligence, creative distinction, purva punya blessings, and prosperity through children or scholarship.",
        (1, 7): "The Lagna lord in the 7th house directs vitality toward relationships, public commerce, and foreign voyages, with a strong focus on marriage partners.",
        (1, 9): "The Lagna lord in the 9th house creates a fortunate soul (Bhagyavanta), blessed with divine protection, virtuous elders, and honorable world travel.",
        (1, 10): "The Lagna lord in the 10th house bestows executive drive, career eminence, public acclaim, and natural authority in professional life.",
        (1, 11): "The Lagna lord in the 11th house creates immense enterprise for financial gains, supportive network circles, and regular fulfillment of desires.",
        (2, 11): "The 2nd lord in the 11th house forms an auspicious Dhana Yoga, indicating continuous financial inflows, commercial success, and wealth growth.",
        (9, 10): "The 9th lord in the 10th house forms the highest Dharma-Karmadhipati Raja Yoga, bringing royal honor, high ethical leadership, and lasting legacy.",
        (10, 9): "The 10th lord in the 9th house aligns career with higher principles, bringing success in education, law, advisory roles, and noble business ventures.",
        (5, 9): "The 5th lord in the 9th house combines creativity with divine grace, producing profound philosophical insights, scholarly publishing, and virtuous progeny.",
        (6, 6): "The 6th lord in the 6th house establishes Harsha Yoga, granting mastery over diseases, victory over legal opponents, and high workplace resilience.",
        (8, 8): "The 8th lord in the 8th house forms Sarala Yoga, granting longevity, fearlessness during crises, and breakthrough discoveries in hidden sciences.",
        (12, 12): "The 12th lord in the 12th house forms Vimala Yoga, indicating spiritual independence, charitable honor, and comfortable overseas engagements."
    }

    if (lord_house, pos_house) in special_cases:
        return special_cases[(lord_house, pos_house)]

    # General algorithmic synthesis
    is_kendra = pos_house in [1, 4, 7, 10]
    is_trikona = pos_house in [1, 5, 9]
    is_dusthana = pos_house in [6, 8, 12]
    is_upachaya = pos_house in [3, 6, 10, 11]

    if is_dusthana:
        return f"Lord of House {lord_house} in the {pos_house}th house calls for conscious attention to transformational lessons, overcoming friction, and managing unexpected shifts in life matters ruled by the {lord_house}th house."
    elif is_trikona:
        return f"Lord of House {lord_house} in the {pos_house}th house is highly fortunate, infusing wisdom, creative grace, and natural dharmic protection into all undertakings governed by the {lord_house}th house."
    elif is_kendra:
        return f"Lord of House {lord_house} in the {pos_house}th house actively projects its energies into concrete worldly achievements, relationships, and leadership structures."
    elif is_upachaya:
        return f"Lord of House {lord_house} in the {pos_house}th house is an Upachaya placement, indicating that results in this area improve steadily through conscious effort, maturity, and perseverance over time."
    else:
        return f"Lord of House {lord_house} posited in the {pos_house}th house connects the foundational nature of the {lord_house}th house with the resources and developmental themes of the {pos_house}th house."

def generate_holistic_reading(pos: Dict[str, Any], asc_lon: float) -> Dict[str, Any]:
    """Assembles a complete, multi-layered Vedic astrological interpretation."""
    asc_sign = int(asc_lon // 30) % 12
    asc_info = ASCENDANTS.get(asc_sign, ASCENDANTS[0])

    # 1. House Lords analysis (144 combinations)
    house_lords_analysis = []
    for h in range(1, 13):
        # Determine sign of this house
        h_sign = (asc_sign + h - 1) % 12
        ruler_planet = SIGN_LORDS[h_sign]

        # Locate where ruler_planet sits in the chart
        if ruler_planet in pos:
            ruler_lon = pos[ruler_planet]["longitude"]
            ruler_sign = int(ruler_lon // 30) % 12
            placement_house = (ruler_sign - asc_sign) % 12 + 1

            reading = get_house_lord_reading(h, placement_house)
            sloka = get_house_lord_sloka(h, placement_house)
            house_lords_analysis.append({
                "house": h,
                "ruler": ruler_planet,
                "placed_in_house": placement_house,
                "placed_in_sign": SIGNS[ruler_sign],
                "rashi": RASHIS[ruler_sign],
                "interpretation": reading,
                "bphs_sloka": sloka,
            })

    # 2. Shad Phala analysis
    shad_phala = []
    for h in range(1, 13):
        info = HOUSE_PHALA[h]
        # Count planets occupying this house
        occupants = [p for p in pos if (int(pos[p]["longitude"] // 30) - asc_sign) % 12 + 1 == h]
        shad_phala.append({
            "house": h,
            "title": info["title"],
            "occupants": occupants,
            "favorable_potential": info["favorable"],
            "growth_considerations": info["challenging"],
        })

    # 3. Divisional Chart Classical Syntheses (D9 Navamsha & 22nd Drekkana)
    navamsha_synthesis = get_navamsha_interpretation(asc_sign, asc_lon % 30.0)
    kharesh_diagnostic = get_22nd_drekkana_interpretation(asc_lon)

    return {
        "ascendant_profile": {
            "sign": SIGNS[asc_sign],
            "rashi": RASHIS[asc_sign],
            "ruler": asc_info["ruler"],
            "element": asc_info["element"],
            "portrait": asc_info["portrait"],
            "strengths": asc_info["key_strengths"],
            "growth_areas": asc_info["growth_areas"],
        },
        "house_lords": house_lords_analysis,
        "shad_phala": shad_phala,
        "navamsha_synthesis": navamsha_synthesis,
        "kharesh_diagnostic": kharesh_diagnostic,
    }

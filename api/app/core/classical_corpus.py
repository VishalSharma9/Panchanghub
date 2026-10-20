"""Classical Astrological Corpus & Deep Interpretive Engine.

Synthesizes classical principles from Brihat Parashara Hora Shastra, Saravali, 
and classical Jyotish tradition into clean-room, vendor-agnostic interpretations:
- 12 Ascendant Complete Portfolios (Physical, Mental, Health, Career, Marriage, Gems, Numbers)
- 108 Graha Rashi Combinations (Sun to Ketu across all 12 Signs)
- 108 Graha Bhava Combinations (Sun to Ketu across all 12 Houses)
- Panchang Birth Factors (Vara, Tithi, Yoga, Karana, Paksha, Day/Night)
- 36 Drekkana Decanate Classifications (Ayudha, Sarpa, Pakshi, Chatushpada, Jala)
- 27 Nakshatra In-Depth Deity & Cosmic Shakti Profiles
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from .ephem import SIGNS, RASHIS, SIGN_LORDS, NAKSHATRAS

# 1. Complete Ascendant Portfolios (12 Signs)
ASCENDANT_PORTFOLIOS = {
    0: {
        "sign": "Aries", "rashi": "Mesha", "ruler": "Mars", "element": "Cardinal Fire",
        "physical": "Medium stature, muscular and athletic build, sharp and prominent brows, ruddy or warm complexion, swift gait, and expressive, courageous eyes.",
        "mental": "Direct, independent, ambitious, decisive, and fearless. Possesses sharp initiative and prefers pioneering new paths over following established routines.",
        "career_finance": "Thrives in leadership, military, surgical, engineering, entrepreneurship, and executive roles. Earns wealth through personal enterprise and bold initiatives.",
        "romance_marriage": "Passionate, protective, and ardent in affection. Seeks a partner who values mutual autonomy while reciprocating deep loyalty.",
        "health_guidance": "Governs the head and brain. Vulnerable to headaches, heat-related fevers, and minor physical cuts or sprains from overexertion. Moderation in spice and cooling hydration advised.",
        "lucky_factors": {"gemstone": "Red Coral (Moonga)", "metal": "Copper / Gold", "numbers": [1, 9], "day": "Tuesday", "color": "Crimson & Red"}
    },
    1: {
        "sign": "Taurus", "rashi": "Vrishabha", "ruler": "Venus", "element": "Fixed Earth",
        "physical": "Well-proportioned, sturdy and dignified build, attractive facial features, melodic voice, thick lustrous hair, and a serene, steady gaze.",
        "mental": "Patient, methodical, prudent, determined, and peace-loving. Resolute once a conviction is formed, displaying immense perseverance and loyalty.",
        "career_finance": "Adept in banking, finance, agriculture, luxury commerce, hospitality, fine arts, and architecture. Exceptional skill in accumulating liquid and tangible assets.",
        "romance_marriage": "Affectionate, devoted, and steadfast. Deeply values domestic comfort, harmonious aesthetics, and long-term marital stability.",
        "health_guidance": "Governs the throat, neck, vocal cords, and thyroid. Tendency towards overindulgence in rich foods or seasonal colds. Balanced nutrition and vocal care recommended.",
        "lucky_factors": {"gemstone": "Diamond / White Sapphire", "metal": "Silver / Platinum", "numbers": [2, 6], "day": "Friday", "color": "White & Rose Pink"}
    },
    2: {
        "sign": "Gemini", "rashi": "Mithuna", "ruler": "Mercury", "element": "Dual Air",
        "physical": "Tall or moderate slender build, agile posture, quick expressive hand gestures, bright inquisitive eyes, and a youthful, communicative demeanor.",
        "mental": "Intellectually versatile, witty, articulate, curious, and inventive. Synthesizes diverse information streams and excels in multi-tasking and communication.",
        "career_finance": "Flourishes in journalism, writing, technology, media, commercial negotiation, translation, public relations, and academia.",
        "romance_marriage": "Seeks mental stimulation and intellectual camaraderie in partnerships. Marriage thrives on engaging dialogue, humor, and shared cultural interests.",
        "health_guidance": "Governs the shoulders, arms, lungs, and nervous system. Vulnerable to respiratory sensitivity and mental restlessness. Breathwork and adequate sleep essential.",
        "lucky_factors": {"gemstone": "Emerald (Panna)", "metal": "Bronze / Green Gold", "numbers": [5, 14], "day": "Wednesday", "color": "Emerald Green"}
    },
    3: {
        "sign": "Cancer", "rashi": "Karka", "ruler": "Moon", "element": "Cardinal Water",
        "physical": "Moderate stature, rounded countenance, soft expressive features, emotional and sensitive eyes, and a protective, nurturing presence.",
        "mental": "Deeply intuitive, empathetic, compassionate, and protective of family. Possesses strong memory, emotional depth, and devotion to home and ancestral lineage.",
        "career_finance": "Success in caregiving, culinary arts, maritime commerce, human resources, real estate, psychology, and public welfare foundations.",
        "romance_marriage": "Deeply loyal, romantic, and nurturing. Values emotional reciprocity and home sanctuary. Vulnerable to shifting moods if feeling unappreciated.",
        "health_guidance": "Governs the chest, breasts, stomach, and digestive tract. Highly responsive to emotional states; emotional equilibrium supports digestive vitality.",
        "lucky_factors": {"gemstone": "Natural Pearl (Moti)", "metal": "Silver", "numbers": [2, 7], "day": "Monday", "color": "Pearl White & Silver"}
    },
    4: {
        "sign": "Leo", "rashi": "Simha", "ruler": "Sun", "element": "Fixed Fire",
        "physical": "Commanding erect posture, broad shoulders, majestic carriage, noble facial structure, lion-like thick hair, and a radiant, authoritative aura.",
        "mental": "Magnanimous, honorable, ambitious, warm-hearted, and courageous. Inspires others naturally, despising pettiness and upholding personal integrity.",
        "career_finance": "Thrives in corporate leadership, politics, government administration, performing arts, entrepreneurship, and luxury directorships.",
        "romance_marriage": "Warm, generous, and chivalrous. Bestows abundant affection and expects honor, loyalty, and mutual admiration in union.",
        "health_guidance": "Governs the heart, upper spine, and vital circulation. Demands cardiovascular conditioning, stress release, and moderation of ego-driven strain.",
        "lucky_factors": {"gemstone": "Ruby (Manikya)", "metal": "Gold", "numbers": [1, 10], "day": "Sunday", "color": "Gold & Royal Red"}
    },
    5: {
        "sign": "Virgo", "rashi": "Kanya", "ruler": "Mercury", "element": "Dual Earth",
        "physical": "Slender, neat and refined appearance, observant analytical gaze, graceful carriage, and an organized, composed presentation.",
        "mental": "Meticulous, analytical, discriminating, humble, and dedicated to practical excellence. Master of detail, diagnostics, and structured workflows.",
        "career_finance": "Excels in medicine, data analysis, accounting, research, editorial work, pharmacy, engineering auditing, and specialized craft.",
        "romance_marriage": "Caring, helpful, and dependable. Expresses affection through tangible service and thoughtful support rather than theatrical declarations.",
        "health_guidance": "Governs the digestive abdomen, bowels, and intestinal assimilation. Vulnerable to anxiety-induced digestive sensitivity. Clean fiber-rich diet recommended.",
        "lucky_factors": {"gemstone": "Emerald (Panna)", "metal": "Alloy / Bronze", "numbers": [5, 23], "day": "Wednesday", "color": "Pale Green & Cream"}
    },
    6: {
        "sign": "Libra", "rashi": "Tula", "ruler": "Venus", "element": "Cardinal Air",
        "physical": "Harmonious symmetrical proportions, graceful smile, elegant aesthetic presence, pleasant voice, and charming, sociable features.",
        "mental": "Judicious, diplomatic, fair-minded, aesthetic, and balanced. Strives for social equity, refined beauty, and peaceful coexistence.",
        "career_finance": "Success in law, diplomacy, fashion, interior design, mediation, trade arbitration, luxury retail, and artistic partnerships.",
        "romance_marriage": "Marriage is central to personal fulfillment. Seeks an egalitarian, loving partnership characterized by mutual elegance and gentle discourse.",
        "health_guidance": "Governs the kidneys, lower back, and endocrine balance. Proper daily hydration, kidney flushing, and posture alignment ensure vigor.",
        "lucky_factors": {"gemstone": "Diamond / Opal", "metal": "Silver / Platinum", "numbers": [6, 15], "day": "Friday", "color": "Pastel Blue & White"}
    },
    7: {
        "sign": "Scorpio", "rashi": "Vrishchika", "ruler": "Mars & Ketu", "element": "Fixed Water",
        "physical": "Muscular, magnetic and penetrating eyes, resolute jawline, mysterious demeanor, and an unmistakable aura of internal psychological power.",
        "mental": "Intensely perceptive, unyielding, secretive, and resilient. Unwavering loyalty to trusted allies, with extraordinary capacity for self-reinvention after crises.",
        "career_finance": "Excels in investigative research, surgery, intelligence, crisis management, mining, occult metaphysics, and turnaround consulting.",
        "romance_marriage": "Passionate, completely invested, and fiercely loyal. Demands absolute honesty and emotional authenticity; distrusts superficiality.",
        "health_guidance": "Governs the reproductive system, colon, and excretory organs. Regular physical detox and emotional release through intense physical training advised.",
        "lucky_factors": {"gemstone": "Red Coral / Bloodstone", "metal": "Copper / Gold", "numbers": [9, 18], "day": "Tuesday", "color": "Maroon & Deep Crimson"}
    },
    8: {
        "sign": "Sagittarius", "rashi": "Dhanu", "ruler": "Jupiter", "element": "Dual Fire",
        "physical": "Tall, athletic, well-formed limbs, cheerful open facial expression, high forehead, and an energetic, confident stride.",
        "mental": "Philosophical, optimistic, frank, generous, and freedom-loving. Enthusiastic seeker of higher truth, ethical wisdom, and spiritual principles.",
        "career_finance": "Flourishes in higher education, philosophy, jurisprudence, foreign relations, publishing, sports coaching, and religious leadership.",
        "romance_marriage": "Values companionship, philosophical compatibility, and intellectual adventure. Needs a partner who respects intellectual independence.",
        "health_guidance": "Governs the hips, thighs, liver, and arterial system. Overeating rich foods can strain hepatic health; regular outdoor movement is healing.",
        "lucky_factors": {"gemstone": "Yellow Sapphire (Pukhraj)", "metal": "Yellow Gold", "numbers": [3, 12], "day": "Thursday", "color": "Golden Yellow & Saffron"}
    },
    9: {
        "sign": "Capricorn", "rashi": "Makara", "ruler": "Saturn", "element": "Fixed Earth",
        "physical": "Lean or sturdy resilient physique, prominent bone structure, deep serious eyes, dignified posture, and a mature appearance that ages gracefully.",
        "mental": "Disciplined, cautious, pragmatic, highly ambitious, and patient. Climbs steadily toward long-term goals with unshakeable perseverance.",
        "career_finance": "Mastery in institutional management, engineering, governance, mining, real estate development, manufacturing, and judicial administration.",
        "romance_marriage": "Loyal, responsible, and protective provider. Takes marital commitments with utmost gravitas, prioritizing family stability and legacy.",
        "health_guidance": "Governs the knees, joints, skeletal system, and teeth. Coldness or joint stiffness alleviated by warm baths, calcium balance, and consistent exercise.",
        "lucky_factors": {"gemstone": "Blue Sapphire (Neelam)", "metal": "Iron / Steel", "numbers": [8, 17], "day": "Saturday", "color": "Dark Blue & Charcoal"}
    },
    10: {
        "sign": "Aquarius", "rashi": "Kumbha", "ruler": "Saturn & Rahu", "element": "Fixed Air",
        "physical": "Tall or medium balanced stature, distinctive features, visionary gaze, unconventional personal style, and an approachable yet detached demeanor.",
        "mental": "Intellectually progressive, humanitarian, innovative, and egalitarian. Possesses an expansive mind interested in collective welfare, science, and reform.",
        "career_finance": "Success in scientific research, advanced technology, aerospace, social activism, electricity/energy, software systems, and global NGOs.",
        "romance_marriage": "Seeks an intellectual soulmate and egalitarian collaborator. Values mental rapport, social vision, and mutual respect for individuality.",
        "health_guidance": "Governs the shins, ankles, and venous circulation. Circulatory vitality boosted through regular aerobic exercise and mindful relaxation.",
        "lucky_factors": {"gemstone": "Blue Sapphire / Amethyst", "metal": "Lead / Silver", "numbers": [4, 8], "day": "Saturday", "color": "Electric Blue & Violet"}
    },
    11: {
        "sign": "Pisces", "rashi": "Meena", "ruler": "Jupiter", "element": "Dual Water",
        "physical": "Gentle fleshy build, luminous and compassionate eyes, delicate hands and feet, soft voice, and an aura of spiritual calm and receptivity.",
        "mental": "Imaginative, compassionate, intuitive, spiritual, and altruistic. Deeply connected to the subtle dimensions of consciousness, art, and universal empathy.",
        "career_finance": "Flourishes in spiritual vocations, fine arts, poetry, oceanography, hospital administration, cinema, hospitality, and philanthropic foundations.",
        "romance_marriage": "Deeply romantic, selfless, and devotional in love. Seeks a spiritual union transcending ordinary material concerns.",
        "health_guidance": "Governs the feet, lymphatic system, and immune resilience. Vulnerable to fluid retention and subtle environmental allergens. Grounding essential.",
        "lucky_factors": {"gemstone": "Yellow Sapphire / Pearl", "metal": "Gold", "numbers": [3, 7], "day": "Thursday", "color": "Sea Green & Pale Yellow"}
    }
}

# 2. Planetary Signs Synthesis (Graha Rashi Phala)
GRAHA_RASHI_INTERPRETATIONS = {
    "Sun": [
        "Aries: Exalted Sun commands immense executive confidence, fearless leadership, radiant constitution, and pioneering independence.",
        "Taurus: Sun in Venus's earth sign seeks financial stability, practical creation, loyal bonds, and artistic appreciation with steady perseverance.",
        "Gemini: Sun in Mercury's air sign bestows intellectual versatility, articulate communication, commercial wit, and rapid cognitive agility.",
        "Cancer: Sun in Moon's water sign directs vitality toward domestic protection, ancestral honor, emotional sanctuary, and patriotic devotion.",
        "Leo: Sun in own sign expresses supreme regal dignity, magnanimous generosity, creative brilliance, and natural executive command.",
        "Virgo: Sun in Mercury's earth sign yields meticulous craftsmanship, analytical diagnostic skill, humble service, and organizational mastery.",
        "Libra: Debilitated Sun learns profound lessons in personal sovereignty, overcoming hesitation, and upholding individual boundaries in partnership.",
        "Scorpio: Sun in Mars's water sign confers intense psychological penetration, unyielding resilience in crisis, and transformative will.",
        "Sagittarius: Sun in Jupiter's fire sign radiates philosophical optimism, righteous conduct, spiritual scholarship, and ethical authority.",
        "Capricorn: Sun in Saturn's earth sign climbs patiently toward public responsibility, institutional authority, and enduring worldly accomplishment.",
        "Aquarius: Sun in Saturn's air sign focuses vitality on collective reform, humanitarian advancement, technological innovation, and group solidarity.",
        "Pisces: Sun in Jupiter's water sign channels life purpose into compassionate service, poetic imagination, mystical insight, and selfless benevolence."
    ],
    "Moon": [
        "Aries: Dynamic, spontaneous emotional responses with a courageous pioneering spirit and bold independent feelings.",
        "Taurus: Exalted Moon provides rock-solid emotional peace, contentment, aesthetic appreciation, financial prudence, and sensory stability.",
        "Gemini: Inquisitive, versatile emotional nature that processes feelings intellectually through lively discourse and diverse interests.",
        "Cancer: Moon in own sign bestows profound intuition, maternal protectiveness, domestic devotion, and deep empathetic responsiveness.",
        "Leo: Warm-hearted, dignified emotional nature needing generous expression, appreciation, creative display, and loyal bonds.",
        "Virgo: Modest, analytical emotional temperament finding security in structured service, practical organization, and wholesome routines.",
        "Libra: Harmony-seeking, romantic emotional nature desiring fair partnership, aesthetic beauty, and cooperative peace.",
        "Scorpio: Debilitated Moon experiences deep emotional transformations, penetrating psychological intuition, and unyielding emotional loyalty.",
        "Sagittarius: Jovial, philosophical emotional outlook inspired by broad horizons, spiritual truth, ethical optimism, and foreign cultures.",
        "Capricorn: Reserved, mature emotional nature that expresses care through steady responsibility, duty, and long-term security.",
        "Aquarius: Detached, humanitarian emotional temperament anchored in egalitarian ideals, camaraderie, and unconventional perspectives.",
        "Pisces: Highly receptive, compassionate, and artistic emotional nature with natural spiritual devotion and empathetic boundaries."
    ],
    "Mars": [
        "Aries: In own sign (Moolatrikona), Mars acts with extraordinary physical vigor, pioneering courage, competitive triumph, and swift decisive action.",
        "Taurus: Mars channels physical stamina into persistent material building, financial acquisition, and steadfast endurance.",
        "Gemini: Energetic mental debate, dexterous technical/verbal skill, quick argumentation, and multifaceted active interests.",
        "Cancer: Debilitated Mars experiences emotional friction requiring conscious channeling of inner frustration into defensive protection and yoga.",
        "Leo: Noble, ambitious executive energy with courageous leadership, chivalrous boldness, and dramatic creative enterprise.",
        "Virgo: Precise, surgical application of energy excel in technical problem-solving, health discipline, and detailed execution.",
        "Libra: Energy directed toward diplomacy, mediation, and defense of fairness, though interpersonal assertiveness requires balance.",
        "Scorpio: In own water sign, Mars wields formidable strategic endurance, psychological resilience, investigative power, and crisis mastery.",
        "Sagittarius: Righteous enthusiasm, ideological vigor, courageous defense of spiritual truth, and adventurous physical vitality.",
        "Capricorn: Exalted Mars achieves peerless executive discipline, institutional supremacy, tireless stamina, and monumental worldly triumphs.",
        "Aquarius: Energy invested in progressive causes, collective movements, unconventional engineering, and intellectual reform.",
        "Pisces: Compassionate and subtle action finding expression through selfless service, artistic choreography, and spiritual surrender."
    ],
    "Mercury": [
        "Aries: Sharp, quick-witted speech with direct, assertive intellectual reflexes and pioneering innovative thoughts.",
        "Taurus: Practical, commercially prudent intellect focused on tangible financial results, steady evaluation, and articulate speech.",
        "Gemini: In own air sign, Mercury displays supreme mental dexterity, multilingual eloquence, media mastery, and commercial wit.",
        "Cancer: Intuitive and associative memory with emotional intelligence, protective reasoning, and imaginative communications.",
        "Leo: Dramatic, dignified oratory with inspiring creative concepts, executive communication, and natural presentation flair.",
        "Virgo: Exalted in own earth sign, Mercury exhibits peerless diagnostic acuity, mathematical precision, editing mastery, and critical logic.",
        "Libra: Diplomatic, balanced negotiating intellect with refined aesthetic taste, objective arbitration, and graceful discourse.",
        "Scorpio: Penetrating investigative mind capable of decoding hidden patterns, cryptographic research, and psychological secrets.",
        "Sagittarius: Broad philosophical intellect inclined toward higher jurisprudence, publishing, spiritual texts, and holistic concepts.",
        "Capricorn: Methodical, structured, and pragmatic intellect excelling in corporate administration, long-term planning, and data organization.",
        "Aquarius: Visionary, unconventional thinking with a gift for technological breakthroughs, sociological models, and system architecture.",
        "Pisces: Debilitated Mercury learns to transcend dry intellectual literalism, opening doors to poetic intuition, musical grace, and mystical insight."
    ],
    "Jupiter": [
        "Aries: Bold, enthusiastic wisdom with pioneering leadership, principled courage, and inspiring moral initiative.",
        "Taurus: Wisdom oriented toward ethical commerce, sound financial husbandry, philanthropy, and family values.",
        "Gemini: Diverse intellectual scholarship, teaching versatility, literary enrichment, and engaging educational communication.",
        "Cancer: Exalted Jupiter grants supreme spiritual benevolence, ancestral grace, emotional wisdom, and boundless charitable generosity.",
        "Leo: Regal, magnanimous mentorship with grand creative vision, ethical governance, and societal respect.",
        "Virgo: Pragmatic, service-oriented counsel with emphasis on holistic health, ethical discipline, and detailed scholarship.",
        "Libra: Judicious, harmonious counseling with a talent for equitable mediation, legal ethics, and artistic refinement.",
        "Scorpio: Deep esoteric wisdom, transformative spiritual initiations, and mastery over hidden metaphysical sciences.",
        "Sagittarius: In own fire sign (Moolatrikona), Jupiter radiates high dharma, spiritual philosophy, higher jurisprudence, and cosmic faith.",
        "Capricorn: Debilitated Jupiter undergoes moral purification, grounding lofty ideals in disciplined, practical service (neecha-bhanga brings worldly wisdom).",
        "Aquarius: Universal humanitarian philosophy, visionary spiritual guidance, and dedication to collective progress and truth.",
        "Pisces: In own water sign, Jupiter unlocks profound contemplative peace, boundless compassion, spiritual intuition, and mystical realization."
    ],
    "Venus": [
        "Aries: Spontaneous, ardent, and demonstrative in love; seeks vibrant adventure and honest passion in relationships.",
        "Taurus: In own earth sign, Venus bestows refined aesthetic tastes, sensual contentment, enduring marital fidelity, and material luxury.",
        "Gemini: Playful, witty social charm with delight in conversational romance, artistic variety, and intellectual companionship.",
        "Cancer: Tender, deeply protective and domestic affection, creating a warm, beautiful home filled with culinary and emotional comforts.",
        "Leo: Generous, noble and theatrical expressions of love; takes pride in honoring and celebrating the beloved.",
        "Virgo: Debilitated Venus learns selfless devotion through dedicated humble service and mutual respect (refines discernment into divine bhakti).",
        "Libra: In own air sign (Moolatrikona), Venus exhibits peerless diplomacy, refined aesthetic sophistication, partnership harmony, and graceful charm.",
        "Scorpio: Intense, passionate, and fiercely loyal love; explores deep psychological intimacy and transformative emotional bonding.",
        "Sagittarius: Idealistic, generous and adventurous affection; seeks shared philosophical journeys and spiritual ethics in partnership.",
        "Capricorn: Dedicated, steadfast and respectful in love; values marital endurance, societal reputation, and dependable fidelity.",
        "Aquarius: Egalitarian, unconventional and freedom-loving social bonds; values intellectual friendship and mutual independence.",
        "Pisces: Exalted Venus achieves sublime romantic and aesthetic transcendence, universal empathy, artistic genius, and divine unconditioned love."
    ],
    "Saturn": [
        "Aries: Debilitated Saturn learns patient discipline, overcoming rash frustration and forging inner endurance through self-mastery.",
        "Taurus: Methodical, conservative financial discipline; builds durable material security through patient, prudent labor.",
        "Gemini: Analytical mental concentration; disciplined communication, systematic scientific study, and structured logic.",
        "Cancer: Emotional self-containment; develops mature inner resilience and protects home and family through earnest duty.",
        "Leo: Lessons in humility and distributed power; matures into responsible, unpretentious leadership through sustained effort.",
        "Virgo: Exemplary diligence in service, health hygiene, and technical problem-solving; meticulous attention to practical duty.",
        "Libra: Exalted Saturn grants sublime judicial fairness, diplomatic endurance, structural integrity, and public ethical authority.",
        "Scorpio: Formidable psychological fortitude, crisis endurance, and unwavering discipline in testing circumstances.",
        "Sagittarius: Principled adherence to spiritual law, traditional ethics, institutional duty, and structured philosophical exploration.",
        "Capricorn: In own earth sign, Saturn manifests supreme organizational stamina, institutional authority, and monumental worldly persistence.",
        "Aquarius: In own air sign (Moolatrikona), Saturn commands progressive collective discipline, scientific rigor, and enduring social institutions.",
        "Pisces: Contemplative isolation, spiritual surrender, and quiet karmic resolution of past-life debts through patient benevolence."
    ],
    "Rahu": [
        "Aries: Ambitious drive toward bold autonomy, intense competitive initiative, and pioneering self-assertion.",
        "Taurus: Strong worldly attraction toward material luxury, wealth accumulation, and sensory enjoyment.",
        "Gemini: Exalted according to classical authorities; brilliant unconventional communication, media innovation, and technological mastery.",
        "Cancer: Craves emotional sanctuary and public acclaim while learning to anchor internal peace amidst changing moods.",
        "Leo: Ambition for public recognition, political prominence, charismatic authority, and creative leadership.",
        "Virgo: Acute analytical discernment, unorthodox diagnostic ability, and competitive triumph over adversaries.",
        "Libra: Intense focus on commercial partnerships, foreign trade agreements, and societal relationships.",
        "Scorpio: Penetrating fascination with hidden occult sciences, transformative financial alchemy, and psychological power.",
        "Sagittarius: Unconventional philosophical quests, foreign spiritual journeys, and challenging orthodox dogma.",
        "Capricorn: Relentless ambition for executive rank, corporate authority, and structural worldly achievements.",
        "Aquarius: Natural affinity for futuristic technologies, mass networks, digital systems, and progressive social changes.",
        "Pisces: Imaginative fascination with foreign lands, mystical realms, cinematic arts, and spiritual dissolution."
    ],
    "Ketu": [
        "Aries: Natural martial instinct with inner detachment; independent courage that acts without seeking personal acclaim.",
        "Taurus: Detachment from material hoarding; instinctive recognition of the impermanence of worldly possessions.",
        "Gemini: Intuitive grasp of complex communication, with periodic desire to retreat from mental chatter into inner silence.",
        "Cancer: Inward emotional withdrawal; deep ancestral memory, spiritual detachment from domestic clinging, and contemplative peace.",
        "Leo: Transcendence of personal ego; inner disdain for superficial flattery and recognition of higher spiritual sovereignty.",
        "Virgo: Sharp instinctual diagnostics and healing ability with spiritual critique of mechanical materialism.",
        "Libra: Detachment from superficial social validation; seeks deep karmic truth in relationships beyond contractual convenience.",
        "Scorpio: Exalted in mystical depth; supreme potential for Kundalini awakening, occult mastery, and radical spiritual liberation.",
        "Sagittarius: Natural spiritual wisdom, past-life philosophical grounding, and intuitive understanding of higher cosmic truth.",
        "Capricorn: Detachment from worldly status games; executes institutional responsibilities with quiet spiritual equanimity.",
        "Aquarius: Intuitive perception of systemic patterns, accompanied by spiritual detachment from group conformity.",
        "Pisces: Ultimate spiritual liberation (Moksha Karaka); profound mystical devotion, psychic surrender, and divine absorption."
    ]
}

# 3. Classical 36 Drekkana Classifications (Decanates)
DREKKANA_CLASSIFICATIONS = {
    # 0 Aries
    (0, 0): {"type": "Chatushpada (Quadruped)", "nature": "Vigorous, bold, dynamic stamina", "deity": "Narada (Deva)"},
    (0, 1): {"type": "Manushya (Human)", "nature": "Resourceful, purposeful, protective", "deity": "Agastya (Manushya)"},
    (0, 2): {"type": "Ayudha (Armed)", "nature": "Martial courage, executive resolve, technical sharpness", "deity": "Durvasa (Rakshasa)"},
    # 1 Taurus
    (1, 0): {"type": "Chatushpada (Quadruped)", "nature": "Steadfast, enduring, agricultural affinity", "deity": "Narada (Deva)"},
    (1, 1): {"type": "Manushya (Human)", "nature": "Aesthetic refinement, economic wisdom", "deity": "Agastya (Manushya)"},
    (1, 2): {"type": "Chatushpada (Quadruped)", "nature": "Patient labor, material persistence", "deity": "Durvasa (Rakshasa)"},
    # 2 Gemini
    (2, 0): {"type": "Manushya (Human)", "nature": "Articulate eloquence, literary flair", "deity": "Narada (Deva)"},
    (2, 1): {"type": "Pakshi (Bird / Khaga)", "nature": "Wandering agility, swift communications", "deity": "Agastya (Manushya)"},
    (2, 2): {"type": "Ayudha (Armed)", "nature": "Sharp critical debate, analytical precision", "deity": "Durvasa (Rakshasa)"},
    # 3 Cancer
    (3, 0): {"type": "Jala (Water)", "nature": "Emotional intuition, maternal care", "deity": "Narada (Deva)"},
    (3, 1): {"type": "Sarpa (Serpent)", "nature": "Psychological depth, hidden resilience, protective vigilance", "deity": "Agastya (Manushya)"},
    (3, 2): {"type": "Sarpa (Serpent)", "nature": "Secretive introspection, transformative instincts", "deity": "Durvasa (Rakshasa)"},
    # 4 Leo
    (4, 0): {"type": "Chatushpada (Quadruped)", "nature": "Regal authority, courageous pride", "deity": "Narada (Deva)"},
    (4, 1): {"type": "Ayudha (Armed)", "nature": "Chivalrous boldness, executive command", "deity": "Agastya (Manushya)"},
    (4, 2): {"type": "Chatushpada (Quadruped)", "nature": "Magnanimous protection, enduring dignity", "deity": "Durvasa (Rakshasa)"},
    # 5 Virgo
    (5, 0): {"type": "Manushya (Human)", "nature": "Diagnostic acuity, analytical diligence", "deity": "Narada (Deva)"},
    (5, 1): {"type": "Manushya (Human)", "nature": "Practical craftsmanship, organizational mastery", "deity": "Agastya (Manushya)"},
    (5, 2): {"type": "Ayudha (Armed)", "nature": "Critical precision, technical problem solving", "deity": "Durvasa (Rakshasa)"},
    # 6 Libra
    (6, 0): {"type": "Manushya (Human)", "nature": "Equitable diplomacy, aesthetic balance", "deity": "Narada (Deva)"},
    (6, 1): {"type": "Pakshi (Bird / Khaga)", "nature": "Sociable charm, communicative negotiation", "deity": "Agastya (Manushya)"},
    (6, 2): {"type": "Chatushpada (Quadruped)", "nature": "Tenacious equity, balanced perseverance", "deity": "Durvasa (Rakshasa)"},
    # 7 Scorpio
    (7, 0): {"type": "Sarpa (Serpent)", "nature": "Penetrating insight, crisis endurance", "deity": "Narada (Deva)"},
    (7, 1): {"type": "Sarpa (Serpent)", "nature": "Intense loyalty, investigative depth", "deity": "Agastya (Manushya)"},
    (7, 2): {"type": "Chatushpada (Quadruped)", "nature": "Formidable recovery, transformative will", "deity": "Durvasa (Rakshasa)"},
    # 8 Sagittarius
    (8, 0): {"type": "Manushya (Human)", "nature": "Philosophical optimism, ethical counsel", "deity": "Narada (Deva)"},
    (8, 1): {"type": "Ayudha (Armed)", "nature": "Righteous zeal, principled courage", "deity": "Agastya (Manushya)"},
    (8, 2): {"type": "Chatushpada (Quadruped)", "nature": "Expansive horizons, athletic vitality", "deity": "Durvasa (Rakshasa)"},
    # 9 Capricorn
    (9, 0): {"type": "Chatushpada (Quadruped)", "nature": "Prudent persistence, enduring labor", "deity": "Narada (Deva)"},
    (9, 1): {"type": "Manushya (Human)", "nature": "Corporate governance, structured planning", "deity": "Agastya (Manushya)"},
    (9, 2): {"type": "Ayudha (Armed)", "nature": "Tenacious institutional defense, executive discipline", "deity": "Durvasa (Rakshasa)"},
    # 10 Aquarius
    (10, 0): {"type": "Manushya (Human)", "nature": "Humanitarian intellect, egalitarian ideals", "deity": "Narada (Deva)"},
    (10, 1): {"type": "Pakshi (Bird / Khaga)", "nature": "Visionary innovation, systemic perspective", "deity": "Agastya (Manushya)"},
    (10, 2): {"type": "Manushya (Human)", "nature": "Scientific reform, collective organization", "deity": "Durvasa (Rakshasa)"},
    # 11 Pisces
    (11, 0): {"type": "Jala (Water)", "nature": "Spiritual empathy, poetic inspiration", "deity": "Narada (Deva)"},
    (11, 1): {"type": "Pakshi (Bird / Khaga)", "nature": "Subtle imagination, mystical aspiration", "deity": "Agastya (Manushya)"},
    (11, 2): {"type": "Sarpa (Serpent)", "nature": "Transcendent surrender, profound contemplation", "deity": "Durvasa (Rakshasa)"}
}

# 4. Panchang Birth Factors
PANCHANG_FACTORS = {
    "day_night": {
        "Day": "Diva-Lagna birth: The solar principle is naturally invigorated, favoring external career recognition, executive assertiveness, public activities, and vital fatherly influence.",
        "Night": "Ratri-Lagna birth: The lunar principle is heightened, conferring fertile imaginative intuition, emotional depth, receptive adaptability, and close maternal bonds."
    },
    "paksha": {
        "Shukla": "Shukla Paksha birth: Born during the waxing Moon cycle. Mental vitality and creative optimism expand with life; favors outward expansion and harmonious public goodwill.",
        "Krishna": "Krishna Paksha birth: Born during the waning Moon cycle. Introspective, self-reliant psychological depth; excels in research, perseverance, and quiet resilience."
    },
    "varas": {
        "Ravivara": "Sunday (Sun): Natural dignity, leadership potential, honorable self-expression, and respect for righteous principles.",
        "Somavara": "Monday (Moon): Gentle, accommodating nature with strong domestic and emotional intuition, popularity, and empathy.",
        "Mangalavara": "Tuesday (Mars): Energetic, bold, competitive, decisive, and courageous in overcoming challenges.",
        "Budhavara": "Wednesday (Mercury): Inquisitive, articulate, commercially astute, witty, and intellectually versatile.",
        "Guruvara": "Thursday (Jupiter): Philosophical, generous, devoted to ethical wisdom, high learning, and spiritual truth.",
        "Shukravara": "Friday (Venus): Aesthetic, peace-loving, socially refined, artistic, and fond of beautiful comforts.",
        "Shanivara": "Saturday (Saturn): Patient, mature, disciplined, hardworking, and endowed with long-term perseverance."
    }
}

def get_graha_rashi_reading(planet: str, sign_idx: int) -> str:
    """Returns synthesized Graha Rashi reading for planet in sign index 0-11."""
    if planet in GRAHA_RASHI_INTERPRETATIONS and 0 <= sign_idx < 12:
        return GRAHA_RASHI_INTERPRETATIONS[planet][sign_idx]
    return f"{planet} placed in {SIGNS[sign_idx % 12]}."

def get_drekkana_profile(sign_idx: int, deg_in_sign: float) -> Dict[str, str]:
    """Returns the Drekkana decanate classification, nature, and deity."""
    decanate = int(deg_in_sign // 10.0)
    decanate = min(max(decanate, 0), 2)
    key = (sign_idx % 12, decanate)
    return DREKKANA_CLASSIFICATIONS.get(key, {
        "type": "Manushya (Human)", "nature": "Balanced and purposeful", "deity": "Agastya (Manushya)"
    })

def generate_comprehensive_corpus_reading(pos: Dict[str, Any], asc_lon: float) -> Dict[str, Any]:
    """Generates an exhaustive, multi-dimensional classical Vedic reading."""
    asc_sign = int(asc_lon // 30) % 12
    asc_deg = asc_lon % 30.0
    
    # 1. Ascendant Full Profile
    portfolio = ASCENDANT_PORTFOLIOS.get(asc_sign, ASCENDANT_PORTFOLIOS[0])
    lagna_drekkana = get_drekkana_profile(asc_sign, asc_deg)
    
    # 2. Graha Rashi Placements
    rashi_readings = []
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p in pos:
            p_lon = pos[p]["longitude"]
            s_idx = int(p_lon // 30) % 12
            d_idx = p_lon % 30.0
            r_text = get_graha_rashi_reading(p, s_idx)
            drk = get_drekkana_profile(s_idx, d_idx)
            rashi_readings.append({
                "planet": p,
                "sign": SIGNS[s_idx],
                "rashi": RASHIS[s_idx],
                "degree": round(d_idx, 4),
                "reading": r_text,
                "drekkana_type": drk["type"],
                "drekkana_deity": drk["deity"]
            })
            
    return {
        "ascendant_portfolio": portfolio,
        "ascendant_drekkana": lagna_drekkana,
        "graha_rashi_readings": rashi_readings,
    }

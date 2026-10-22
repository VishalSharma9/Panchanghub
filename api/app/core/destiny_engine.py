"""Comprehensive Cross-Linked Vedic Destiny, Medical/Longevity, Accident & Safety,
Lottery/Windfall, Marriage/Union, Progeny & Grandchildren (D-7), Past/Future Life (D-60),
and Ravana Samhita 9-Planet Mastery Engine.

Derived from authentic classical treatises:
- Brihat Parashara Hora Shastra (BPHS: Ayurdaya, Roga, Vivaha, Santana Saptamsha, Shashtiamsha, Graha Shanti)
- Ravana Samhita & Lal Kitab (Graha Prabandhana / 9-Planet Control, Tantric/Vedic Beej, Keep-Close vs Avoid, Rinas)
- Jaimini Upadesha Sutras (Upapada Lagna, Darakaraka, Atmakaraka, Karakamsha, Rudra, Shoola)
- Prashna Marga & Phaladeepika (Beeja/Kshetra Sphuta, Santana, Mrityu Bhaga, Durghatana)
- Sarvartha Chintamani & Bhrigu Samhita (Destiny Turning Ages, Indu Lagna Windfalls, Purva/Uttara Janma)
"""
from __future__ import annotations
import math
from datetime import date as Date, datetime, time as Time, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from . import ephem
from .ephem import SIGNS, RASHIS, SIGN_LORDS, NAKSHATRAS, NAK_LORDS, VEDIC_PLANETS
from .kundli import compute_kundli, dignity, EXALT, OWN, FRIENDS
from .vargas_ext import build_all_vargas, compute_varga_position, SHASTIAMSA_DEITIES
from .dashas_ext import get_current_dasha, compute_jaimini_karakas, compute_deep_vimshottari
from .special_lagnas import compute_special_lagnas
from .ashtakavarga_ext import full_ashtakavarga_suite
from .remedies_corpus import GRAHA_REMEDIES, compute_soul_guidance
from . import panchang as P
from . import numerology as NUM

# ---------------------------------------------------------------------------
# 1. CLASSICAL MRITYU BHAGA (FATEFUL DEGREES PER SIGN, 0..11 = Aries..Pisces)
#    Source: Phaladeepika Ch. 13 & Prashna Marga
# ---------------------------------------------------------------------------
MRITYU_BHAGA: Dict[str, List[int]] = {
    "Lagna":   [1, 9, 22, 22, 25, 2, 4, 23, 18, 20, 24, 10],
    "Sun":     [20, 9, 12, 6, 8, 24, 16, 17, 22, 2, 3, 23],
    "Moon":    [26, 12, 13, 25, 24, 11, 26, 14, 13, 25, 5, 12],
    "Mars":    [19, 28, 25, 23, 29, 28, 14, 21, 2, 15, 11, 6],
    "Mercury": [15, 14, 13, 12, 8, 18, 20, 10, 21, 22, 7, 5],
    "Jupiter": [19, 29, 12, 27, 6, 4, 13, 10, 17, 11, 15, 28],
    "Venus":   [28, 15, 11, 17, 10, 13, 4, 6, 27, 12, 29, 19],
    "Saturn":  [10, 4, 7, 9, 12, 16, 3, 18, 28, 14, 13, 15],
    "Rahu":    [14, 13, 12, 11, 24, 23, 22, 21, 10, 20, 18, 8],
    "Ketu":    [8, 18, 20, 10, 21, 22, 23, 24, 11, 12, 13, 14],
}

# ---------------------------------------------------------------------------
# 2. ANATOMICAL & MEDICAL ASTROLOGY (ROGA SHASTRA) MAPPING
# ---------------------------------------------------------------------------
SIGN_ANATOMY: List[Dict[str, str]] = [
    {"sign": "Aries", "rashi": "Mesha", "body_part": "Cranium, brain, forehead, cerebral arteries, face",
     "dosha": "Pitta", "diseases": "Migraines, head injuries, insomnia, high fevers, hypertension, neuralgia"},
    {"sign": "Taurus", "rashi": "Vrishabha", "body_part": "Throat, thyroid, vocal cords, tonsils, neck, lower jaw, eyes",
     "dosha": "Kapha", "diseases": "Thyroid disorders, tonsillitis, laryngitis, dental issues, cervical stiffness"},
    {"sign": "Gemini", "rashi": "Mithuna", "body_part": "Lungs, bronchi, shoulders, arms, nervous system, collarbone",
     "dosha": "Vata", "diseases": "Asthma, bronchitis, nervous exhaustion, shoulder/arm neuralgia, respiratory allergies"},
    {"sign": "Cancer", "rashi": "Karka", "body_part": "Chest, stomach, diaphragm, breasts, digestive mucosa, lymphatic fluid",
     "dosha": "Kapha-Jala", "diseases": "Gastritis, acid reflux, pulmonary congestion, fluid retention, emotional indigestion"},
    {"sign": "Leo", "rashi": "Simha", "body_part": "Heart, aorta, dorsal spine, upper back, spleen, vital prana",
     "dosha": "Pitta", "diseases": "Cardiac arrhythmias, blood pressure fluctuations, spinal pain, inflammatory fevers"},
    {"sign": "Virgo", "rashi": "Kanya", "body_part": "Small intestine, colon, pancreas, solar plexus, enteric nervous system",
     "dosha": "Vata-Prithvi", "diseases": "IBS, malabsorption, ulcers, food sensitivities, anxiety-driven gut disorders"},
    {"sign": "Libra", "rashi": "Tula", "body_part": "Kidneys, adrenal glands, lumbar spine, bladder, endocrine balance",
     "dosha": "Vata-Kapha", "diseases": "Renal calculi (kidney stones), lower back pain, adrenal fatigue, urinary tract issues"},
    {"sign": "Scorpio", "rashi": "Vrishchika", "body_part": "Pelvic organs, reproductive system, prostate/uterus, rectum, excretory ducts",
     "dosha": "Pitta-Jala", "diseases": "Reproductive inflammation, piles/hemorrhoids, hormonal disorders, hidden infections"},
    {"sign": "Sagittarius", "rashi": "Dhanu", "body_part": "Hips, thighs, femur, sciatic nerve, liver, arterial circulation",
     "dosha": "Pitta-Agni", "diseases": "Sciatica, hip joint wear, hepatic congestion, lipid/metabolic imbalances"},
    {"sign": "Capricorn", "rashi": "Makara", "body_part": "Knees, skeletal joints, patella, skin, teeth, cartilage",
     "dosha": "Vata", "diseases": "Osteoarthritis, knee injuries, eczema/dry skin, rheumatism, calcifications"},
    {"sign": "Aquarius", "rashi": "Kumbha", "body_part": "Calves, ankles, shins, peripheral veins, bio-electrical nervous impulses",
     "dosha": "Vata", "diseases": "Varicose veins, ankle sprains, poor peripheral circulation, spasmodic cramps"},
    {"sign": "Pisces", "rashi": "Meena", "body_part": "Feet, toes, lymphatic drainage, pineal gland, immune-sleep cycle",
     "dosha": "Kapha", "diseases": "Foot ailments, plantar pain, lymphatic sluggishness, sleep disorders, auto-sensitivity"},
]

PLANET_DISEASES: Dict[str, Dict[str, str]] = {
    "Sun": {
        "dosha": "Pitta (Bilious / Fire)",
        "organs": "Heart, right eye (male) / left eye (female), bones, spine, vitality (Ojas)",
        "affliction_diseases": "Cardiovascular strain, weak eyesight, vitamin D / bone density deficiency, high fever, sunstroke, migraines",
        "ayurvedic_fix": "Brahmi, Amalaki (Amla), pomegranate, copper-charged water at sunrise, Surya Namaskara, avoiding excess spicy/sour foods",
        "healing_mantra": "Om Hraam Hreem Hroum Sah Sooryaaya Namah + Aditya Hridaya Stotram",
    },
    "Moon": {
        "dosha": "Vata-Kapha (Phlegmatic / Water)",
        "organs": "Mind (Manas), blood plasma (Rasa Dhatu), lungs, stomach, breasts, left eye",
        "affliction_diseases": "Insomnia, emotional anxiety, mood swings, cold/sinus congestion, edema/water retention, hormonal cycles",
        "ayurvedic_fix": "Ashwagandha, Shankhpushpi, warm milk with nutmeg/cardamom at night, drinking water from silver vessel, Pranayama",
        "healing_mantra": "Om Som Somaaya Namah + Shiva Panchakshari (Om Namah Shivaya)",
    },
    "Mars": {
        "dosha": "Pitta (Intense Fire)",
        "organs": "Bone marrow (Majja), hemoglobin/red blood cells, muscles, bile, head/forehead",
        "affliction_diseases": "High blood pressure, acute inflammation, cuts/burns/surgeries, boils, ulcers, hyper-acidity, muscular tears",
        "ayurvedic_fix": "Guduchi (Giloy), Aloe Vera juice, sandalwood paste, cooling diet (ghee, sweet fruits), blood donation on Tuesdays",
        "healing_mantra": "Om Ang Angarakaya Namah + Hanuman Bahuk (specifically for physical pain & blood disorders)",
    },
    "Mercury": {
        "dosha": "Tridosha (Vata-Pitta-Kapha Mixed)",
        "organs": "Central & peripheral nervous system, skin (Twak), vocal cords, thyroid, respiratory bronchi",
        "affliction_diseases": "Nervous tremors, vertigo, skin rashes/eczema, speech stammering, digestive enzyme deficiency, mental burnout",
        "ayurvedic_fix": "Gotu Kola (Mandukaparni), Tulsi tea, green leafy vegetables, soaking green moong overnight, Oil pulling (Gandusha)",
        "healing_mantra": "Om Bum Budhaaya Namah + Vishnu Sahasranama",
    },
    "Jupiter": {
        "dosha": "Kapha (Anabolic / Ether-Water)",
        "organs": "Liver (Yakrit), pancreas, gallbladder, adipose tissue (Meda Dhatu), ears, arterial fat metabolism",
        "affliction_diseases": "Fatty liver, diabetes/insulin resistance, high cholesterol, obesity, ear/hearing issues, benign growths",
        "ayurvedic_fix": "Turmeric (Haridra) with black pepper, Triphala at bedtime, bitter greens, brisk morning walk during Brahma Muhurta",
        "healing_mantra": "Om Gram Greem Groum Sah Gurave Namah + Dakshinamurthy Stotram",
    },
    "Venus": {
        "dosha": "Kapha-Vata (Reproductive / Water)",
        "organs": "Reproductive tissues (Shukra/Artava Dhatu), kidneys, bladder, throat, facial complexion, tear ducts",
        "affliction_diseases": "Urinary/renal issues, reproductive/fertility challenges, hormonal cysts, throat infections, blood sugar swings",
        "ayurvedic_fix": "Shatavari (for women) / Safed Musli & Gokshura (for men), rose water, white sandalwood, adequate hydration",
        "healing_mantra": "Om Shum Shukraaya Namah + Sri Suktam",
    },
    "Saturn": {
        "dosha": "Vata (Catabolic / Air-Ether)",
        "organs": "Bones (Asthi), joints, teeth, knees, tendons, sciatic nerve, colon, chronic cellular aging",
        "affliction_diseases": "Arthritis, joint stiffness, chronic back/knee pain, dental decay, chronic fatigue, constipation, nerve compression",
        "ayurvedic_fix": "Warm sesame oil self-massage (Abhyanga) on Saturdays, Dashamoola, Shilajit, warm cooked foods with ginger & black sesame",
        "healing_mantra": "Om Praam Preem Proum Sah Shanaishcharaaya Namah + Maha Mrityunjaya Mantra",
    },
    "Rahu": {
        "dosha": "Vata-Sannipata (Irregular / Electrical)",
        "organs": "Autonomic nervous system, immune response, subtle pranic channels, toxin elimination",
        "affliction_diseases": "Hard-to-diagnose psychosomatic ailments, sudden allergies, autoimmune flares, phobias, viral/toxic exposure",
        "ayurvedic_fix": "Neem, Manjistha, Panchakarma detox, grounding barefoot on earth, avoiding ultra-processed foods, alcohol, and late nights",
        "healing_mantra": "Om Bhraam Bhreem Bhroum Sah Rahave Namah + Durga Kavacha",
    },
    "Ketu": {
        "dosha": "Pitta-Vata (Fiery / Micro-cellular)",
        "organs": "Spine, subtle nerve plexuses (Chakras), cellular immunity, feet, enigmatic reflexes",
        "affliction_diseases": "Mysterious fevers, spinal nerve pinching, sudden sharp pains, viral infections, hypersensitivity, diagnostic puzzles",
        "ayurvedic_fix": "Ashwagandha, Kusha grass water, meditation on Muladhara/Ajna chakra, feeding stray dogs, warm herbal foot baths",
        "healing_mantra": "Om Sraam Sreem Sroum Sah Ketave Namah + Ganesha Atharvashirsha",
    },
}

# ---------------------------------------------------------------------------
# 3. RAVANA SAMHITA 9-PLANET MASTERY & GEMSTONE / KEEP-CLOSE VS AVOID MATRIX
# ---------------------------------------------------------------------------
RAVANA_GRAHA_MASTERY: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "primary_gem": "Natural Burmese Ruby (Manikya)",
        "substitute_gem": "Red Garnet (Tamda) or Red Spinel",
        "carat_weight": "3 to 5.25 Ratti (2.7 to 4.7 Carats)",
        "metal": "Gold (Swarna) or Pure Copper (Tamra)",
        "finger": "Ring Finger (Anamika) of Right Hand",
        "wearing_day_hora": "Sunday morning within 1 hour of local Sunrise during Surya Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ घृणिः सूर्य आदित्योम (Om Ghrinih Soorya Adityom) — 108 times while dipping ring in raw milk & Ganga jal",
        "ravana_tantra_secret": "Offer Arghya at exact local Sunrise through a copper vessel with red sandalwood, 7 unbroken rice grains (Akshata), and red hibiscus while gazing at the Sun's reflection in the water stream.",
        "deity_to_worship": "Surya Narayana, Lord Rama, or Matangi / Gayatri",
        "worship_duration": "12 to 24 minutes daily at Sunrise (Minimum 3 Malas / 324 recitations; 40-day Mandala for authority breakthrough)",
        "keep_close_objects": ["Pure copper coin or Surya Yantra in wallet/desk", "Red sandalwood (Rakta Chandana) piece", "Seven-horse rising Sun painting on East wall", "Brass/copper water vessel on East side of work desk"],
        "avoid_objects": ["Black iron or rusted metal on the body", "Stagnant water or dark clutter in the East sector of home", "Accepting free salt or black clothes as gifts on Sundays"],
        "power_colors": ["Saffron", "Ruby Red", "Golden Orange", "Copper"],
        "avoid_colors": ["Pitch Black", "Dark Charcoal Grey", "Muddy Brown"],
        "power_numbers": [1, 10, 19, 28, 37, 46],
        "avoid_numbers": [8, 17, 26],
        "favorable_direction": "East (Purva)",
        "sacred_tree_plant": "Ark / Calotropis (Mandara) & Bel (Bilva)",
        "animal_service": "Feed wheat & jaggery (Gur) to brown cows or monkeys on Sundays",
    },
    "Moon": {
        "primary_gem": "Natural Basra/South Sea Pearl (Moti)",
        "substitute_gem": "Natural Moonstone (Chandrakanta Mani)",
        "carat_weight": "4.25 to 6.25 Ratti (3.8 to 5.6 Carats)",
        "metal": "Pure Sterling Silver (Chandi)",
        "finger": "Little Finger (Kanishthika) of Right Hand",
        "wearing_day_hora": "Monday morning or evening during Chandra Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ सों सोमाय नमः (Om Som Somaaya Namah) — 108 times",
        "ravana_tantra_secret": "Keep a solid silver square (4 grams) immersed in a glass of water by your bedside at night and drink that water first thing upon waking; never waste running tap water.",
        "deity_to_worship": "Lord Shiva (Somnath / Chandrashekhara) & Goddess Gauri / Lalita Tripurasundari",
        "worship_duration": "15 to 27 minutes on Monday evenings or Purnima nights (11 Malas over a Full Moon cycle)",
        "keep_close_objects": ["Solid silver square or silver coin in wallet", "Dakshinavarti Shankha (conch shell) filled with water in North-East", "Crystal quartz (Sphatika) rosary", "Silver tumbler for drinking water"],
        "avoid_objects": ["Broken mirrors or chipped glassware", "Leaking faucets or damp walls", "Wearing dark/torn clothes during sleep"],
        "power_colors": ["Pearl White", "Milky Cream", "Seafoam Pastel", "Silver"],
        "avoid_colors": ["Deep Crimson", "Heavy Black", "Dark Maroon"],
        "power_numbers": [2, 11, 20, 29, 38, 47],
        "avoid_numbers": [4, 7, 8, 9],
        "favorable_direction": "North-West (Vayavya)",
        "sacred_tree_plant": "Palash (Flame of the Forest) & White Jasmine (Mogra)",
        "animal_service": "Offer milk/rice to white cows or feed fishes with flour pellets on Mondays",
    },
    "Mars": {
        "primary_gem": "Natural Italian/Mediterranean Red Coral (Moonga)",
        "substitute_gem": "Carnelian or Red Jasper",
        "carat_weight": "5.25 to 8.25 Ratti (4.7 to 7.4 Carats)",
        "metal": "Gold or Pure Copper",
        "finger": "Ring Finger (Anamika) of Right Hand",
        "wearing_day_hora": "Tuesday morning within 2 hours of Sunrise during Mangala Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ अं अङ्गारकाय नमः (Om Ang Angarakaya Namah) — 108 times",
        "ravana_tantra_secret": "Offer sindoor mixed with jasmine (Chameli) oil to Lord Hanuman's feet on 7 consecutive Tuesdays, and place a triangular copper Mars Yantra at the South wall to neutralize enemies and accidents.",
        "deity_to_worship": "Lord Hanuman (Panchamukhi Hanuman for severe afflictions), Lord Kartikeya (Subrahmanya), & Lord Narasimha",
        "worship_duration": "20 minutes every Tuesday morning & evening (7 recitations of Hanuman Chalisa or 1 Bajrang Baan)",
        "keep_close_objects": ["Triangular copper piece or Hanuman Kavacha talisman", "Red handkerchief in pocket on important days", "Pure honey in a earthen or glass jar in the kitchen"],
        "avoid_objects": ["Blunt, rusted knives or broken weapons in the house", "Electronic junk in the South corner", "Sleeping with head directly toward North"],
        "power_colors": ["Vermilion Red", "Coral", "Scarlet", "Bright Crimson"],
        "avoid_colors": ["Jet Black", "Bottle Green", "Dark Grey"],
        "power_numbers": [9, 18, 27, 36, 45],
        "avoid_numbers": [4, 5, 8],
        "favorable_direction": "South (Dakshina)",
        "sacred_tree_plant": "Khadira (Acacia catechu) & Red Hibiscus / Neem",
        "animal_service": "Feed roasted gram (chana) and jaggery to monkeys or red cows on Tuesdays",
    },
    "Mercury": {
        "primary_gem": "Natural Colombian/Zambian Emerald (Panna)",
        "substitute_gem": "Peridot, Green Tourmaline, or Green Jade",
        "carat_weight": "3.25 to 5.25 Ratti (3 to 4.7 Carats)",
        "metal": "Gold or Panchadhatu (Five-Metal Alloy)",
        "finger": "Little Finger (Kanishthika) of Right Hand",
        "wearing_day_hora": "Wednesday morning during Budha Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ बुं बुधाय नमः (Om Bum Budhaaya Namah) — 108 times",
        "ravana_tantra_secret": "Pierce a whole alum (Fitkari) crystal or clean your teeth with alum water on Wednesdays to clear Mercury afflictions (nervous/business blocks), and gift green stationery to young students.",
        "deity_to_worship": "Lord Vishnu (Venkateshwara / Narayana), Lord Ganesha, & Goddess Tripura Sundari",
        "worship_duration": "15 minutes every Wednesday morning (Vishnu Sahasranama or 12 names of Ganesha)",
        "keep_close_objects": ["Green aventurine or emerald-colored pen for signing contracts", "Fresh Tulsi plant in the North or East balcony", "Solid brass Ganesha idol on study/office desk"],
        "avoid_objects": ["Torn books, non-working pens, or broken clocks", "broad-leafed thorny indoor plants (Cactus/Bonsai)", "Keeping unfulfilled verbal promises"],
        "power_colors": ["Emerald Green", "Mint Green", "jade", "Turquoise"],
        "avoid_colors": ["Blood Red", "Bright Orange"],
        "power_numbers": [5, 14, 23, 32, 41, 50],
        "avoid_numbers": [2, 9],
        "favorable_direction": "North (Uttara)",
        "sacred_tree_plant": "Apamarga (Achyranthes aspera) & Sacred Tulsi",
        "animal_service": "Feed fresh green grass, spinach, or soaked whole green moong to cows and birds on Wednesdays",
    },
    "Jupiter": {
        "primary_gem": "Natural Ceylon Yellow Sapphire (Pukhraj)",
        "substitute_gem": "Yellow Topaz or Natural Citrine (Sunela)",
        "carat_weight": "4.25 to 6.25 Ratti (3.8 to 5.6 Carats)",
        "metal": "Yellow Gold (Swarna)",
        "finger": "Index Finger (Tarjani) of Right Hand",
        "wearing_day_hora": "Thursday morning within 2 hours of Sunrise during Guru Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ बृं बृहस्पतये नमः (Om Brim Brihaspataye Namah) — 108 times",
        "ravana_tantra_secret": "Apply a tilak of pure saffron (Kesar) or turmeric paste on your forehead and navel (Nabhi) daily after bathing; keep a piece of raw turmeric wrapped in yellow silk in your cash locker.",
        "deity_to_worship": "Lord Dakshinamurthy (Shiva as Supreme Guru), Lord Dattatreya, & Lord Vamana/Vishnu",
        "worship_duration": "24 minutes every Thursday during Brahma Muhurta or Guru Hora (5 Malas of Guru Beej Mantra)",
        "keep_close_objects": ["Whole raw turmeric root & 5 yellow cowries in yellow cloth in safe", "Saffron (Kesar) box", "5-Mukhi Rudraksha mala", "Sacred scripture (Bhagavad Gita) in North-East"],
        "avoid_objects": ["Heavy shoes or broom/dustbin in the North-East (Ishanya) corner", "Disrespecting teachers, elders, or sacred texts", "Cutting Peepal or Banana trees"],
        "power_colors": ["Golden Yellow", "Saffron", "Mustard Gold", "Turmeric"],
        "avoid_colors": ["Dark Black", "Smoky Grey"],
        "power_numbers": [3, 12, 21, 30, 39, 48],
        "avoid_numbers": [6, 5],
        "favorable_direction": "North-East (Ishanya)",
        "sacred_tree_plant": "Peepal (Ashvattha) & Banana Tree (Kadali)",
        "animal_service": "Feed soaked chana dal with jaggery inside wheat dough balls (Peda) to cows or elephants on Thursdays",
    },
    "Venus": {
        "primary_gem": "Natural Flawless Diamond (Heera) or White Sapphire (Safed Pukhraj)",
        "substitute_gem": "Natural White Zircon (Jarkan) or Opal",
        "carat_weight": "0.5 to 1.5 Carats (Diamond) or 4.25 to 6 Ratti (Opal/White Sapphire)",
        "metal": "Platinum, White Gold, or Pure Silver",
        "finger": "Middle Finger or Little Finger of Right Hand",
        "wearing_day_hora": "Friday morning within 2 hours of Sunrise during Shukra Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ शुं शुक्राय नमः (Om Shum Shukraaya Namah) — 108 times",
        "ravana_tantra_secret": "Use natural rose or mogra attar (alcohol-free essence) on your pulse points every Friday, keep your clothes crisply ironed, and burn camphor with 2 cloves in a silver bowl at dusk.",
        "deity_to_worship": "Goddess Mahalakshmi, Sri Lalita Tripurasundari, & Santoshi/Annapurna Devi",
        "worship_duration": "18 minutes every Friday morning and Pradosha dusk (Recite Sri Suktam 3 times)",
        "keep_close_objects": ["Natural rose/sandalwood attar bottle", "Sri Yantra in silver or crystal in North-East/South-East", "6-Mukhi or 13-Mukhi Rudraksha", "Clean silk handkerchief"],
        "avoid_objects": ["Faded, stained, or torn undergarments/clothes", "Cluttered or dark South-East corner", "Harsh speech toward spouse or women"],
        "power_colors": ["Pure White", "Iridescent Pink", "baby Blue", "Pastel Lavender", "Silver"],
        "avoid_colors": ["Rust Red", "Dull Black"],
        "power_numbers": [6, 15, 24, 33, 42, 51],
        "avoid_numbers": [1, 3],
        "favorable_direction": "South-East (Agneya)",
        "sacred_tree_plant": "Gular (Cluster Fig / Audumbara) & White Rose / Jasmine",
        "animal_service": "Feed green fodder and white sorghum (Jowar) to white cows and birds on Fridays",
    },
    "Saturn": {
        "primary_gem": "Natural Ceylon Blue Sapphire (Neelam) — TEST FOR 72 HOURS UNDER PILLOW FIRST",
        "substitute_gem": "Amethyst (Jamuniya) or Iolite (Kaka Nili)",
        "carat_weight": "4.25 to 6.25 Ratti (3.8 to 5.6 Carats)",
        "metal": "Panchadhatu or Ashtadhatu or Iron/Silver",
        "finger": "Middle Finger (Madhyama) of Right Hand",
        "wearing_day_hora": "Saturday evening just before Sunset during Shani Hora in Shukla Paksha",
        "prana_pratishtha_shloka": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (Om Praam Preem Proum Sah Shanaishcharaaya Namah) — 108 times",
        "ravana_tantra_secret": "Ravana famously kept Shani under the throne's gaze: to command Saturn, practice absolute justice toward workers/servants, look at your own reflection in a bowl of mustard oil on Saturday morning and donate it (Chhaya Dana), and light a sesame oil lamp under a Peepal tree at Saturday sunset.",
        "deity_to_worship": "Lord Shani Deva, Lord Hanuman (Whom Shani promised never to afflict), & Lord Kalabhairava / Lord Kurma",
        "worship_duration": "27 minutes every Saturday evening at Sunset (Dasharatha Krit Shani Stotra + Hanuman Chalisa)",
        "keep_close_objects": ["Black horse-shoe iron ring (from a boat nail or horse shoe, forged without fire) on middle finger", "7-Mukhi or 14-Mukhi Rudraksha", "Black sesame seeds in a small pouch during travel"],
        "avoid_objects": ["Buying iron, leather, broom, salt, or oil on Saturdays", "Exploiting subordinates or manual laborers", "Accumulating scrap metal on the roof or West balcony"],
        "power_colors": ["Navy Blue", "Indigo", "Royal Violet", "Charcoal (only if Saturn is Yogakaraka)"],
        "avoid_colors": ["Fiery Red", "Bright Copper Orange"],
        "power_numbers": [8, 17, 26, 35, 44],
        "avoid_numbers": [1, 2, 9],
        "favorable_direction": "West (Paschima)",
        "sacred_tree_plant": "Shami Tree (Prosopis cineraria) & Peepal",
        "animal_service": "Feed oiled roti to black dogs, and offer cooked rice with black sesame seeds to crows on Saturdays",
    },
    "Rahu": {
        "primary_gem": "Natural Ceylon Hessonite Garnet (Gomed)",
        "substitute_gem": "Orange Zircon or Spessartine",
        "carat_weight": "5.25 to 7.25 Ratti (4.7 to 6.5 Carats)",
        "metal": "Pure Silver or Ashtadhatu (Never Gold)",
        "finger": "Middle Finger (Madhyama) of Right Hand",
        "wearing_day_hora": "Saturday evening after Sunset or Wednesday in Ardra/Swati/Shatabhisha Nakshatra",
        "prana_pratishtha_shloka": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (Om Bhraam Bhreem Bhroum Sah Rahave Namah) — 108 times",
        "ravana_tantra_secret": "To master Rahu's illusion and sudden windfalls: keep a solid silver elephant (min 25g) on your desk, wash 400g of barley in milk and flow it in running water on a Saturday, and keep fennel (Saunf) in a white cloth under your pillow.",
        "deity_to_worship": "Goddess Durga (Mahishasura Mardini), Goddess Chhinnamasta / Saraswati, & Lord Varaha",
        "worship_duration": "21 minutes during Rahu Kaal or at dusk (Durga Saptashati Argala/Kavacha or Rahu Beej)",
        "keep_close_objects": ["Solid silver elephant figurine in North-West", "8-Mukhi Rudraksha", "Peacock feather in workspace to deflect Rahu negativity"],
        "avoid_objects": ["Non-functional electronics, tangled cables, and cracked phone screens", "Smoking, intoxicants, or gambling during Rahu Kaal", "Blue/black ceiling paint"],
        "power_colors": ["Electric Blue", "Smoky Silver", "Ultraviolet", "Slate"],
        "avoid_colors": ["Bright Sunny Yellow", "Crimson Red"],
        "power_numbers": [4, 13, 22, 31, 40],
        "avoid_numbers": [1, 2, 8, 9],
        "favorable_direction": "South-West (Nairutya)",
        "sacred_tree_plant": "Durva Grass & Sandalwood (Chandana)",
        "animal_service": "Feed 7 types of grains (Satnaja) to wild birds/pigeons and care for stray/disabled animals",
    },
    "Ketu": {
        "primary_gem": "Natural Chrysoberyl Cat's Eye (Lehsunia / Vaidurya)",
        "substitute_gem": "Tiger's Eye or Quartz Cat's Eye",
        "carat_weight": "4.25 to 6.25 Ratti (3.8 to 5.6 Carats)",
        "metal": "Pure Silver or Panchadhatu",
        "finger": "Middle or Little Finger of Right Hand",
        "wearing_day_hora": "Tuesday or Thursday morning in Ashwini/Magha/Mula Nakshatra",
        "prana_pratishtha_shloka": "ॐ स्रां स्रीं स्रौं सः केतवे नमः (Om Sraam Sreem Sroum Sah Ketave Namah) — 108 times",
        "ravana_tantra_secret": "To unlock Ketu's intuitive omniscience and Trikala-Jnana (knowledge of past, present, future): apply saffron tilak behind your earlobes and forehead, hoist a triangular saffron flag at a temple, and donate a black-and-white blanket to the needy.",
        "deity_to_worship": "Lord Ganesha (Vighnaharta), Lord Matsya, & Goddess Dhumavati / Chitragupta",
        "worship_duration": "15 to 21 minutes at dawn or twilight (Ganesha Atharvashirsha or Sankata Nashana Ganesha Stotra)",
        "keep_close_objects": ["9-Mukhi Rudraksha", "Kusha grass mat (Asana) for meditation", "Small Ganesha murti in natural turmeric or stone"],
        "avoid_objects": ["Criticizing sadhus, mystics, or dogs", "Leaving roof terrace dirty or obstructed", "Breaking spiritual vows (Sankalpa)"],
        "power_colors": ["Multi-colored / Two-tone (Black & White)", "Dove Grey", "Earthy Ochre", "Saffron"],
        "avoid_colors": ["Neon Pink", "Harsh Scarlet"],
        "power_numbers": [7, 16, 25, 34, 43],
        "avoid_numbers": [2, 4, 8],
        "favorable_direction": "North-East / Zenith (Akasha)",
        "sacred_tree_plant": "Kusha Grass (Darbha) & Ashwagandha",
        "animal_service": "Feed sweet roti or milk to two-colored (black-and-white) street dogs daily",
    },
}

# ---------------------------------------------------------------------------
# 4. PAST-LIFE ARCHETYPES & RINA (KARMIC DEBTS OF PAST INCARNATIONS)
# ---------------------------------------------------------------------------
KETU_PAST_LIFE_SIGN: Dict[str, Dict[str, str]] = {
    "Aries": {
        "era_persona": "Warrior Commander, Martial Strategist, or Frontier Pioneer",
        "mastered_gifts": "Fearless initiative, rapid crisis response, physical valor, and independent leadership",
        "unfulfilled_residue": "Impatience, solitary action without consensus, or unresolved battlefield/conflict karma",
    },
    "Taurus": {
        "era_persona": "Royal Treasurer, Agrarian Landowner, Temple Artisan, or Classical Musician",
        "mastered_gifts": "Deep resource preservation, aesthetic mastery, vocal/musical resonance, and family loyalty",
        "unfulfilled_residue": "Over-attachment to material security, possessiveness, or fear of sudden transformation",
    },
    "Gemini": {
        "era_persona": "Royal Scribe, Messenger, Court Scholar, or Merchant Diplomat",
        "mastered_gifts": "Polyglot intellect, persuasive dialectic, rapid synthesis of information, and adaptability",
        "unfulfilled_residue": "Intellectual restlessness, scattering energy across too many paths without single-pointed depth",
    },
    "Cancer": {
        "era_persona": "Matriarch/Patriarch of a Large Clan, Healer, or Devotional Sanctuary Keeper",
        "mastered_gifts": "Profound emotional empathy, psychic sensitivity, nurturing protection, and ancestral memory",
        "unfulfilled_residue": "Over-identifying with family pain, emotional clinginess, or neglecting public/worldly authority",
    },
    "Leo": {
        "era_persona": "Sovereign Ruler, Aristocrat, Royal Priest, or High-Ranking Administrator",
        "mastered_gifts": "Natural regal authority, charismatic dignity, administrative command, and noble generosity",
        "unfulfilled_residue": "Subtle pride (Ahamkara), reluctance to ask for help, or difficulty functioning in egalitarian networks",
    },
    "Virgo": {
        "era_persona": "Ayurvedic Vaidya (Physician), Vedic Ritualist, Alchemist, or Master Craftsman",
        "mastered_gifts": "Surgical precision, diagnostic discernment, purity of craft, and selfless service",
        "unfulfilled_residue": "Hyper-critical perfectionism, excessive worry over flaws, and suppressing mystical surrender",
    },
    "Libra": {
        "era_persona": "Magistrate, Peace Envoy, Courtier, or Patron of the Fine Arts",
        "mastered_gifts": "Diplomatic poise, aesthetic refinement, legal/ethical equilibrium, and social grace",
        "unfulfilled_residue": "Sacrificing personal fire to keep peace, indecisiveness, or defining self through partners",
    },
    "Scorpio": {
        "era_persona": "Tantric Adept, Occult Researcher, Alchemist, or Secret Intelligence Guardian",
        "mastered_gifts": "Penetrating psychological X-ray vision, mastery over crisis, mantra siddhi, and fearlessness of death",
        "unfulfilled_residue": "Secretiveness, distrust of simplicity, or carrying intense emotional vows across lifetimes",
    },
    "Sagittarius": {
        "era_persona": "Dharmic Acharya, Philosopher-Monk, Royal Advisor, or Temple Jurist",
        "mastered_gifts": "Natural grasp of higher law (Dharma), prophetic intuition, philosophical wisdom, and teaching power",
        "unfulfilled_residue": "Dogmatic certainty, overlooking practical daily details in favor of grand ideals",
    },
    "Capricorn": {
        "era_persona": "State Builder, Guild Master, ascetic Yogi, or Chief Architect",
        "mastered_gifts": "Stoic endurance, organizational discipline, mastery of law and structure, and emotional stoicism",
        "unfulfilled_residue": "Emotional austerity, workaholism, and suppressing tender vulnerability and domestic warmth",
    },
    "Aquarius": {
        "era_persona": "Social Reformer, Astronomer-Sage, Guild Visionary, or Humanitarian Mystic",
        "mastered_gifts": "Universal brotherhood vision, systemic genius, detachment from ego, and futuristic insight",
        "unfulfilled_residue": "Detachment from personal recognition, feeling like an outsider among ordinary society",
    },
    "Pisces": {
        "era_persona": "Hermitage Rishi, Bhakti Saint, Contemplative Monk, or Temple Mystic",
        "mastered_gifts": "Transcendental compassion, effortless samadhi/meditation, poetic intuition, and ego-dissolution",
        "unfulfilled_residue": "Escapism from worldly precision, boundary porousness, or reluctance to handle material organization",
    },
}

PAST_LIFE_RINAS: Dict[str, Dict[str, str]] = {
    "Pitru Rina (Ancestral / Paternal Debt)": {
        "trigger": "Affliction to Sun, 9th house, or 5th house by Rahu/Ketu/Saturn",
        "past_life_cause": "Neglect of ancestral lineage traditions, disrespect toward elders/mentors, or unfulfilled family vows in a prior incarnation.",
        "symptoms_in_this_life": "Unexplained delays in career promotion, obstacles in progeny, sudden reputation setbacks at the moment of success.",
        "how_to_counter_and_fix": "Perform Pitru Tarpan on Amavasya (especially Mahalaya Pitru Paksha), offer water to Peepal tree on Saturdays, donate food in ancestors' name on their Tithi, and recite Aditya Hridaya Stotram.",
    },
    "Matru Rina (Maternal / Nurturing Debt)": {
        "trigger": "Affliction to Moon or 4th house by Ketu/Rahu/Saturn",
        "past_life_cause": "Emotional abandonment of mother/homeland, polluting water bodies, or breaking domestic sanctuary trust in a past life.",
        "symptoms_in_this_life": "Lack of mental peace despite wealth, property disputes, troubled sleep, or feeling emotionally unsupported.",
        "how_to_counter_and_fix": "Serve your mother and elderly women unconditionally, offer silver coins in flowing clean water, sponsor clean drinking water (Pyaau) for travelers, and worship Goddess Parvati/Gauri.",
    },
    "Deva / Guru Rina (Divine & Spiritual Preceptor Debt)": {
        "trigger": "Affliction to Jupiter, 5th/9th/12th house, or Brahmana/Guru Shrapa",
        "past_life_cause": "Misusing sacred mantras/spiritual authority for ego, abandoning a spiritual vow, or disrespecting a Guru/temple in the past life.",
        "symptoms_in_this_life": "Wisdom failing at critical moments (Buddhi Bhrama), betrayal by trusted advisors, liver/metabolic issues, or children facing hurdles.",
        "how_to_counter_and_fix": "Rebuild or clean a temple sanctum, plant a Peepal or Banana tree at a shrine, donate religious books and yellow garments to scholars on Thursdays, and chant Guru Gayatri.",
    },
    "Stri / Kalatra Rina (Spousal & Sacred Union Debt)": {
        "trigger": "Affliction to Venus, 7th house, or Upapada Lagna by Mars/Rahu/Saturn/Sun",
        "past_life_cause": "Breaking marriage vows, causing emotional heartache to a devoted partner, or misusing sensual/financial privilege in a prior life.",
        "symptoms_in_this_life": "Delayed marriage, misunderstandings in relationships, reproductive/renal sensitivities, or sudden luxury/cash-flow drains.",
        "how_to_counter_and_fix": "Practice absolute fidelity and gentle speech with partner, sponsor the wedding of an underprivileged bride (Kanyadaan support), feed white cows on Fridays, and recite Sri Suktam.",
    },
    "Bhratru /Bandhu Rina (Sibling & Comrade Debt)": {
        "trigger": "Affliction to Mars, Mercury, or 3rd/11th house",
        "past_life_cause": "Unfair division of ancestral land/wealth among siblings or betraying a comrade-in-arms in a previous birth.",
        "symptoms_in_this_life": "Blood/inflammatory issues, litigation over property, friends turning into rivals, or sudden courage depletion.",
        "how_to_counter_and_fix": "Be generous with siblings and colleagues even when you have the upper hand, donate blood voluntarily, distribute sweet boondi/jaggery on Tuesdays, and recite Sundarkand.",
    },
    "Jeeva / Bhuta Rina (Nature & Living Beings Debt)": {
        "trigger": "Affliction to Saturn, 6th/8th house, or Sarpa Dosha (Rahu-Ketu axis)",
        "past_life_cause": "Harming innocent creatures, cutting down ancient trees/groves containing serpent habitats, or harshness toward servants.",
        "symptoms_in_this_life": "Chronic enigmatic ailments, sudden accidents, skin/nerve flares, or prolonged legal/financial entanglements.",
        "how_to_counter_and_fix": "Perform Naga Pratishtha / Sarpa Samskara or Abhishekam to Nagadevata on Nag Panchami / Shashthi, feed birds, dogs, and ants daily (Pancha Maha Yajna), and never harm reptiles.",
    },
}

# ---------------------------------------------------------------------------
# 5. CORE HELPERS: FUNCTIONAL PLANETARY ROLES PER LAGNA
# ---------------------------------------------------------------------------
def _house_sign(lagna_idx: int, house: int) -> int:
    """Return 0..11 sign index for 1-based house."""
    return (lagna_idx + house - 1) % 12

def _house_lord(lagna_idx: int, house: int) -> str:
    return SIGN_LORDS[_house_sign(lagna_idx, house)]

def _house_of_planet(p_lon: float, lagna_idx: int) -> int:
    return (int(p_lon // 30) - lagna_idx) % 12 + 1

def _badhaka_house(lagna_idx: int) -> int:
    # Movable (0,3,6,9) -> 11th; Fixed (1,4,7,10) -> 9th; Dual (2,5,8,11) -> 7th
    mod = lagna_idx % 3
    return 11 if mod == 0 else (9 if mod == 1 else 7)

def classify_functional_planets(lagna_idx: int) -> Dict[str, Any]:
    """Classify all 9 Grahas into Yogakaraka, Functional Benefics, Neutrals,
    Functional Malefics, Primary Marakas, and Badhakadhipati per BPHS Ch. 34."""
    h_lords = {h: _house_lord(lagna_idx, h) for h in range(1, 13)}
    trikona_lords = {h_lords[1], h_lords[5], h_lords[9]}
    kendra_lords = {h_lords[1], h_lords[4], h_lords[7], h_lords[10]}
    dusthana_lords = {h_lords[6], h_lords[8], h_lords[12]}
    trishadaya_lords = {h_lords[3], h_lords[6], h_lords[11]}

    yogakarakas = list(( {h_lords[5], h_lords[9]} & {h_lords[4], h_lords[7], h_lords[10]} ))
    benefics = sorted(trikona_lords | set(yogakarakas))
    marakas = sorted({h_lords[2], h_lords[7]})
    badhaka_h = _badhaka_house(lagna_idx)
    badhaka_lord = h_lords[badhaka_h]

    malefics = sorted((dusthana_lords | trishadaya_lords) - trikona_lords)
    neutrals = sorted(set(VEDIC_PLANETS[:7]) - set(benefics) - set(malefics))

    return {
        "lagna_sign": SIGNS[lagna_idx],
        "lagna_rashi": RASHIS[lagna_idx],
        "lagna_lord": h_lords[1],
        "house_lords": h_lords,
        "yogakarakas": yogakarakas,
        "functional_benefics": benefics,
        "functional_neutrals": neutrals,
        "functional_malefics": malefics,
        "maraka_lords": marakas,
        "badhaka_house": badhaka_h,
        "badhaka_lord": badhaka_lord,
        "wealth_dhana_lords": sorted({h_lords[2], h_lords[5], h_lords[9], h_lords[11]}),
        "speculation_windfall_lords": sorted({h_lords[5], h_lords[8], h_lords[11]}),
    }


# ---------------------------------------------------------------------------
# 6. MODULE 1: DISEASES, MEDICAL ASTROLOGY, LONGEVITY & MARAKA / MRITYU WINDOWS
# ---------------------------------------------------------------------------
def analyze_medical_and_longevity(
    pos: Dict[str, Any],
    asc_lon: float,
    birth_jd: float,
    cur_lat: float,
    cur_lon: float,
    cur_tz_name: Optional[str],
    cur_utc_offset: Optional[float],
    ref_date: Date,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    moon_idx = int(pos["Moon"]["longitude"] // 30) % 12
    sun_idx = int(pos["Sun"]["longitude"] // 30) % 12
    roles = classify_functional_planets(lagna_idx)
    h_lords = roles["house_lords"]

    # 1. Ayurvedic Tridosha Prakriti (Vata, Pitta, Kapha)
    dosha_pts = {"Vata": 0, "Pitta": 0, "Kapha": 0}
    sign_dosha_map = [
        "Pitta", "Kapha", "Vata", "Kapha", "Pitta", "Vata",
        "Vata", "Pitta", "Pitta", "Vata", "Vata", "Kapha",
    ]
    dosha_pts[sign_dosha_map[lagna_idx]] += 40
    dosha_pts[sign_dosha_map[moon_idx]] += 35
    dosha_pts[sign_dosha_map[sun_idx]] += 25
    dominant_dosha = max(dosha_pts, key=dosha_pts.get)

    # 2. Check Mrityu Bhaga (Fateful Degrees) for Lagna & all 9 Grahas
    mrityu_bhaga_alerts = []
    lagna_deg_in_sign = asc_lon % 30.0
    mb_lagna = MRITYU_BHAGA["Lagna"][lagna_idx]
    if abs(lagna_deg_in_sign - mb_lagna) <= 1.25:
        mrityu_bhaga_alerts.append({
            "body": "Lagna (Ascendant)",
            "sign": SIGNS[lagna_idx],
            "actual_degree": round(lagna_deg_in_sign, 2),
            "mrityu_degree": mb_lagna,
            "orb": round(abs(lagna_deg_in_sign - mb_lagna), 2),
            "implication": "Physical vitality requires lifelong protection during Maraka/8th lord transits.",
            "remedy": "Recite Maha Mrityunjaya Mantra 108 times on birthdays and wear Lagna Lord Kavacha.",
        })

    for p in VEDIC_PLANETS:
        p_lon = pos[p]["longitude"]
        s_i = int(p_lon // 30) % 12
        d_in_s = p_lon % 30.0
        mb_deg = MRITYU_BHAGA[p][s_i]
        if abs(d_in_s - mb_deg) <= 1.25:
            mrityu_bhaga_alerts.append({
                "body": p,
                "sign": SIGNS[s_i],
                "actual_degree": round(d_in_s, 2),
                "mrityu_degree": mb_deg,
                "orb": round(abs(d_in_s - mb_deg), 2),
                "implication": f"{p} is within Mrityu Bhaga orb; organs and houses ruled by {p} ({PLANET_DISEASES[p]['organs']}) need careful guarding during its Dasha/Bhukti.",
                "remedy": PLANET_DISEASES[p]["healing_mantra"],
            })

    # 3. Organ & Disease Vulnerability Scan (6th Roga, 8th Chronic/Surgery, 12th Hospitalization, D-6 Shashtamsha)
    h6_sign = _house_sign(lagna_idx, 6)
    h8_sign = _house_sign(lagna_idx, 8)
    h12_sign = _house_sign(lagna_idx, 12)
    h6_lord = h_lords[6]
    h8_lord = h_lords[8]
    h12_lord = h_lords[12]

    vulnerabilities = []
    # Primary 6th house anatomical zone
    anat_6 = SIGN_ANATOMY[h6_sign]
    vulnerabilities.append({
        "category": "Primary Acute Disease Axis (6th House / Roga Sthana)",
        "sign": f"{anat_6['sign']} ({anat_6['rashi']})",
        "governing_planet": h6_lord,
        "vulnerable_organs": anat_6["body_part"],
        "potential_conditions": anat_6["diseases"],
        "ayurvedic_remedy": PLANET_DISEASES[h6_lord]["ayurvedic_fix"],
        "shloka_remedy": PLANET_DISEASES[h6_lord]["healing_mantra"],
    })
    # Primary 8th house chronic/longevity zone
    anat_8 = SIGN_ANATOMY[h8_sign]
    vulnerabilities.append({
        "category": "Chronic & Surgical Axis (8th House / Randhra Sthana)",
        "sign": f"{anat_8['sign']} ({anat_8['rashi']})",
        "governing_planet": h8_lord,
        "vulnerable_organs": anat_8["body_part"],
        "potential_conditions": anat_8["diseases"],
        "ayurvedic_remedy": PLANET_DISEASES[h8_lord]["ayurvedic_fix"],
        "shloka_remedy": PLANET_DISEASES[h8_lord]["healing_mantra"],
    })

    # Check planets in debilitation, combustion, or in 6/8/12
    sun_lon = pos["Sun"]["longitude"]
    for p in VEDIC_PLANETS:
        p_lon = pos[p]["longitude"]
        p_sign = int(p_lon // 30) % 12
        p_house = _house_of_planet(p_lon, lagna_idx)
        dig = dignity(p, p_lon) if p not in ("Rahu", "Ketu") else "shadow"
        combust = (p not in ("Sun", "Rahu", "Ketu")) and (abs(ephem.angdiff(p_lon, sun_lon)) < 8.5)
        if dig == "debilitated" or combust or p_house in (6, 8, 12):
            reason = []
            if dig == "debilitated":
                reason.append("Debilitated (Neecha)")
            if combust:
                reason.append("Combust (Asta)")
            if p_house in (6, 8, 12):
                reason.append(f"Placed in Dusthana House {p_house}")
            vulnerabilities.append({
                "category": f"Planetary Sensitivity ({p} — {', '.join(reason)})",
                "sign": f"{SIGNS[p_sign]} ({RASHIS[p_sign]})",
                "governing_planet": p,
                "vulnerable_organs": PLANET_DISEASES[p]["organs"],
                "potential_conditions": PLANET_DISEASES[p]["affliction_diseases"],
                "ayurvedic_remedy": PLANET_DISEASES[p]["ayurvedic_fix"],
                "shloka_remedy": PLANET_DISEASES[p]["healing_mantra"],
            })

    # 4. Classical BPHS Three-Pairs Longevity (Ayurdaya) & Maraka / Mrityu Analysis
    # Pair 1: Lagna Lord + 8th Lord modality
    # Pair 2: Moon + Saturn modality
    # Pair 3: Lagna + Hora Lagna modality
    def _pair_term(s1: int, s2: int) -> str:
        # 0=Movable (Chara), 1=Fixed (Sthira), 2=Dual (Dwiswabhava)
        m1, m2 = s1 % 3, s2 % 3
        if m1 == m2:
            return "Dirghayu (Long Life: 75–100+ yrs)" if m1 == 0 else (
                "Alpayu (Early Caution: <36 yrs, requires Mrityunjaya Kavacha)" if m1 == 1 else "Madhyayu (Middle Span: 65–75 yrs)"
            )
        pair_set = {m1, m2}
        if pair_set == {0, 1}:
            return "Madhyayu (Balanced Span: 68–80 yrs)"
        if pair_set == {1, 2}:
            return "Dirghayu (Extended Span: 78–96+ yrs)"
        return "Purnayu (Full Span: 72–88 yrs)"

    l1_sign = int(pos[h_lords[1]]["longitude"] // 30) % 12
    l8_sign = int(pos[h8_lord]["longitude"] // 30) % 12
    sat_sign = int(pos["Saturn"]["longitude"] // 30) % 12
    hl_sign = (lagna_idx + int(((asc_lon % 30) / 2.5))) % 12

    pair1 = _pair_term(l1_sign, l8_sign)
    pair2 = _pair_term(moon_idx, sat_sign)
    pair3 = _pair_term(lagna_idx, hl_sign)

    # Benefics in Kendra/Trikona & Saturn strength boost longevity (Kaksha Vriddhi)
    benefic_kendra = sum(
        1 for bp in ("Jupiter", "Venus", "Mercury", "Moon")
        if _house_of_planet(pos[bp]["longitude"], lagna_idx) in (1, 4, 5, 7, 9, 10)
    )
    sat_house = _house_of_planet(pos["Saturn"]["longitude"], lagna_idx)
    base_years = 76 + benefic_kendra * 3 + (4 if sat_house in (3, 6, 8, 10, 11) else 0)
    estimated_span = f"{min(base_years - 4, 84)} – {min(base_years + 8, 98)} years (with Kaksha Vriddhi & Dharmic living)"

    # Maraka Grahas & Critical Maraka Dasha Windows
    maraka_2 = h_lords[2]
    maraka_7 = h_lords[7]
    occupants_2_7 = [
        p for p in VEDIC_PLANETS
        if _house_of_planet(pos[p]["longitude"], lagna_idx) in (2, 7)
    ]

    # Scan Vimshottari Mahadasha-Antardasha for Maraka + 8th/6th Lord intersections
    tz_cur = ephem.make_tz(cur_tz_name, cur_utc_offset)
    deep_dashas = compute_deep_vimshottari(pos["Moon"]["longitude"], birth_jd, tz_cur, max_levels=2).get("mahadashas", [])
    critical_life_windows = []
    watch_lords = {maraka_2, maraka_7, h8_lord, h6_lord, "Saturn", "Rahu"}
    for md in deep_dashas:
        md_lord = md["lord"]
        for ad in md.get("antardashas", []):
            ad_lord = ad["lord"]
            if (md_lord in {maraka_2, maraka_7, h8_lord} and ad_lord in {maraka_2, maraka_7, h8_lord, "Saturn", "Rahu"}):
                if ad["end"] >= ref_date.isoformat():
                    severity = "High (Primary Maraka + 8th/Malefic Junction)" if (
                        {md_lord, ad_lord} & {maraka_2, maraka_7} and {md_lord, ad_lord} & {h8_lord, "Saturn", "Rahu"}
                    ) else "Moderate-High (Maraka Vitality Test)"
                    critical_life_windows.append({
                        "dasha_period": f"{md_lord} Mahadasha – {ad_lord} Antardasha",
                        "start_date": ad["start"][:10],
                        "end_date": ad["end"][:10],
                        "severity": severity,
                        "astronomical_reason": f"{md_lord} and {ad_lord} activate the 2nd/7th Maraka and 8th Randhra houses simultaneously.",
                        "countermeasure": "Perform Maha Mrityunjaya Japa (11,000 recitations), Rudrabhishekam on Mondays, and donate black sesame + iron on Saturdays.",
                    })
                    if len(critical_life_windows) >= 6:
                        break
        if len(critical_life_windows) >= 6:
            break

    return {
        "ayurvedic_constitution": {
            "tridosha_percentages": dosha_pts,
            "dominant_prakriti": dominant_dosha,
            "dietary_lifestyle_rule": PLANET_DISEASES[h_lords[1]]["ayurvedic_fix"],
        },
        "longevity_ayurdaya": {
            "bphs_pair_1_lagna_8th": pair1,
            "bphs_pair_2_moon_saturn": pair2,
            "bphs_pair_3_lagna_hora": pair3,
            "kaksha_vriddhi_benefics_in_kendra_trikona": benefic_kendra,
            "estimated_lifespan_potential": estimated_span,
            "primary_maraka_lords": [maraka_2, maraka_7],
            "planets_occupying_maraka_houses": occupants_2_7,
            "eighth_house_lord_ayush": h8_lord,
            "badhakadhipati_obstruction_lord": roles["badhaka_lord"],
            "maha_mrityunjaya_shloka": "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्। उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय माऽमृतात्॥ (Om Tryambakam Yajamahe Sugandhim Pushtivardhanam, Urvarukamiva Bandhanan Mrityor Mukshiya Maamritat)",
        },
        "mrityu_bhaga_degree_diagnostics": mrityu_bhaga_alerts,
        "disease_and_organ_vulnerabilities": vulnerabilities,
        "critical_maraka_and_health_windows": critical_life_windows,
    }


# ---------------------------------------------------------------------------
# 7. MODULE 2: ACCIDENTS, MISHAPS & LOCATION-CALIBRATED DANGER/SAFE WINDOWS
# ---------------------------------------------------------------------------
def analyze_accidents_and_safety(
    pos: Dict[str, Any],
    asc_lon: float,
    cur_lat: float,
    cur_lon: float,
    cur_tz_name: Optional[str],
    cur_utc_offset: Optional[float],
    ref_date: Date,
    scan_days: int = 30,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    moon_lon = pos["Moon"]["longitude"]
    natal_moon_idx = int(moon_lon // 30) % 12
    natal_nak_idx = int(moon_lon // (360 / 27)) % 27
    roles = classify_functional_planets(lagna_idx)
    h8_lord = roles["house_lords"][8]

    # D-8 Ashtamsha (1/8 division for sudden accidents & hazards)
    d8_asc_sign, _ = compute_varga_position(asc_lon, "D8")
    mars_d8_sign, _ = compute_varga_position(pos["Mars"]["longitude"], "D8")
    sat_d8_sign, _ = compute_varga_position(pos["Saturn"]["longitude"], "D8")
    rahu_d8_sign, _ = compute_varga_position(pos["Rahu"]["longitude"], "D8")

    # Natal Accident Yogas (Angaraka Mars-Rahu, Agni-Maruta Mars-Saturn, 8th/6th/1st/4th afflictions)
    mars_s = int(pos["Mars"]["longitude"] // 30) % 12
    sat_s = int(pos["Saturn"]["longitude"] // 30) % 12
    rahu_s = int(pos["Rahu"]["longitude"] // 30) % 12
    ketu_s = int(pos["Ketu"]["longitude"] // 30) % 12

    natal_hazards = []
    if mars_s == rahu_s or abs(mars_s - rahu_s) == 6:
        natal_hazards.append({
            "yoga": "Angaraka / Kuja-Rahu Axis",
            "nature": "High-speed vehicular, electrical, fire, or sudden impulsive impact hazard",
            "precaution": "Never drive when angry or during Mars/Rahu Hora; keep a copper Hanuman Kavacha in your vehicle.",
        })
    if mars_s == sat_s or abs(mars_s - sat_s) == 6:
        natal_hazards.append({
            "yoga": "Agni-Maruta / Kuja-Shani Axis",
            "nature": "Mechanical failure, bone/joint impact, heavy machinery, or fall from height",
            "precaution": "Inspect vehicle brakes/tires before long journeys; avoid nighttime highway driving on Tuesdays & Saturdays.",
        })
    if not natal_hazards:
        natal_hazards.append({
            "yoga": f"8th House ({SIGNS[_house_sign(lagna_idx, 8)]}) & D-8 ({SIGNS[d8_asc_sign]}) Sensitivity",
            "nature": f"Periodic caution during {h8_lord} and Mars/Saturn transits over the 8th/1st axis",
            "precaution": "Recite Narasimha Kavacha or Hanuman Chalisa before embarking on journeys during Chandrashtama.",
        })

    # Scan upcoming days at the USER'S CURRENT LOCATION for exact Danger & Safe Date-Time-Hour windows
    tz_cur = ephem.make_tz(cur_tz_name, cur_utc_offset)
    caution_windows = []
    safe_travel_windows = []

    for offset in range(scan_days):
        d = ref_date + timedelta(days=offset)
        jd_mid = ephem.local_midnight_jd(d, tz_cur) + 0.5
        t_moon = ephem.moon_lon(jd_mid, True)
        t_mars = ephem.calc(jd_mid, ephem.swe.MARS, True)[0]
        t_moon_sign = int(t_moon // 30) % 12
        t_nak = int(t_moon // (360 / 27)) % 27

        house_from_moon = (t_moon_sign - natal_moon_idx) % 12 + 1
        tara_num = ((t_nak - natal_nak_idx) % 27) % 9 + 1
        tara_name = P.TARAS[tara_num - 1]
        wd = P.weekday_of(d)

        try:
            ev = P.day_events(d, cur_lat, cur_lon, tz_cur)
            sr, ss, nsr = ev["sunrise"], ev["sunset"], ev["next_sunrise"]
            if sr is None or ss is None:
                continue
            rahu_a, rahu_b = P.seg(sr, ss, 8, P.RAHU_SEG[wd])
            yama_a, yama_b = P.seg(sr, ss, 8, P.YAMA_SEG[wd])
            horas = P.hora(d, cur_lat, cur_lon, cur_tz_name, cur_utc_offset)["horas"]
        except Exception:
            continue

        # Danger trigger: Chandrashtama (8th from Moon) OR Vipat(3)/Pratyak(5)/Vadha(7) Tara
        is_chandrashtama = (house_from_moon == 8)
        is_bad_tara = tara_num in (3, 5, 7)
        mars_hit = (int(t_mars // 30) % 12 in (lagna_idx, natal_moon_idx, _house_sign(lagna_idx, 8)))

        if is_chandrashtama or (is_bad_tara and wd in (2, 6)):  # Tuesday or Saturday with bad Tara
            # Find the Mars or Saturn Hora during daytime at current location
            danger_hora = next((h for h in horas[:12] if h["lord"] in ("Mars", "Saturn")), horas[0])
            reasons = []
            if is_chandrashtama:
                reasons.append(f"Chandrashtama (Transit Moon in 8th Rashi {SIGNS[t_moon_sign]} from Natal Moon)")
            if is_bad_tara:
                reasons.append(f"{tara_name} Tara ({NAKSHATRAS[t_nak]} Nakshatra)")
            if mars_hit:
                reasons.append("Transit Mars aspecting sensitive natal axis")

            caution_windows.append({
                "date": d.isoformat(),
                "weekday": P.WEEKDAYS[wd],
                "risk_level": "HIGH CAUTION" if (is_chandrashtama and is_bad_tara) else "MODERATE CAUTION",
                "peak_danger_hora": f"{danger_hora['start'][11:16]} – {danger_hora['end'][11:16]} ({danger_hora['lord']} Hora)",
                "local_rahu_kaal": f"{ephem.fmt(rahu_a, tz_cur)[11:16]} – {ephem.fmt(rahu_b, tz_cur)[11:16]}",
                "local_yamaganda": f"{ephem.fmt(yama_a, tz_cur)[11:16]} – {ephem.fmt(yama_b, tz_cur)[11:16]}",
                "direction_to_avoid_disha_shool": P.DISHA_SHOOL[wd],
                "triggers": "; ".join(reasons),
                "hazard_type": "Vehicular / sharp objects / impulsive conflict" if danger_hora["lord"] == "Mars" else "Fatigue / mechanical glitch / slip or fall",
                "protective_action": "Avoid starting high-speed travel or risky procedures in the Peak Danger Hora & Rahu Kaal; chant 'Om Namo Bhagavate Narasimhaya' 11 times before stepping out.",
            })

        # Safe & Auspicious Travel / Action Window: Good Moon house (1,3,6,7,10,11) + Good Tara (2,4,6,8,9)
        elif house_from_moon in (1, 3, 6, 7, 10, 11) and tara_num in (2, 4, 6, 8, 9) and len(safe_travel_windows) < 8:
            good_hora = next((h for h in horas[:12] if h["lord"] in ("Jupiter", "Venus", "Mercury")), horas[0])
            safe_travel_windows.append({
                "date": d.isoformat(),
                "weekday": P.WEEKDAYS[wd],
                "tara_blessing": f"{tara_name} Tara ({NAKSHATRAS[t_nak]})",
                "chandrabalam": f"House {house_from_moon} from Natal Moon ({SIGNS[t_moon_sign]})",
                "golden_safe_hora": f"{good_hora['start'][11:16]} – {good_hora['end'][11:16]} ({good_hora['lord']} Hora)",
                "favorable_for": "Long-distance travel, vehicle purchase, medical procedures, and adventure",
            })

    return {
        "current_location_calibrated": {
            "latitude": cur_lat,
            "longitude": cur_lon,
            "timezone": cur_tz_name or f"UTC{cur_utc_offset:+g}" if (cur_tz_name or cur_utc_offset is not None) else "UTC",
        },
        "d8_ashtamsha_profile": {
            "d8_lagna": SIGNS[d8_asc_sign],
            "mars_in_d8": SIGNS[mars_d8_sign],
            "saturn_in_d8": SIGNS[sat_d8_sign],
            "rahu_in_d8": SIGNS[rahu_d8_sign],
        },
        "natal_accident_indicators": natal_hazards,
        "upcoming_danger_and_caution_windows": caution_windows[:10],
        "upcoming_safe_and_protected_windows": safe_travel_windows[:8],
        "raksha_kavacha_shloka": "उग्रं वीरं महाविष्णुं ज्वलन्तं सर्वतोमुखम्। नृसिंहं भीषणं भद्रं मृत्युमृत्युं नमाम्यहम्॥ (Ugram Veeram Maha-Vishnum Jvalantam Sarvatomukham, Nrisimham Bheeshanam Bhadram Mrityur-Mrityum Namamyaham)",
    }


# ---------------------------------------------------------------------------
# 8. MODULE 3: DESTINY TURNING POINTS, GOOD/BAD DATES & BAD-LUCK BREAKER
# ---------------------------------------------------------------------------
def analyze_destiny_turning_points(
    pos: Dict[str, Any],
    asc_lon: float,
    birth_dt_utc: datetime,
    birth_jd: float,
    cur_lat: float,
    cur_lon: float,
    cur_tz_name: Optional[str],
    cur_utc_offset: Optional[float],
    ref_date: Date,
    scan_days: int = 45,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    moon_lon = pos["Moon"]["longitude"]
    natal_moon_idx = int(moon_lon // 30) % 12
    natal_nak_idx = int(moon_lon // (360 / 27)) % 27
    roles = classify_functional_planets(lagna_idx)
    tz_cur = ephem.make_tz(cur_tz_name, cur_utc_offset)
    birth_year = birth_dt_utc.year

    # 1. Lifelong Destiny Turning Ages & Years (Bhrigu Chakra + Dasha Sandhis)
    bhrigu_planet_ages = [
        (16, "Jupiter", "Educational & dharmic awakening; early mentors shape life direction"),
        (22, "Sun", "Soul authority & independent identity crystallization; career foundation"),
        (24, "Moon", "Emotional maturity, travel, domestic or public visibility shift"),
        (28, "Mars", "Peak vitality, property/ambition surge, decisive courage milestone"),
        (30, "Saturn (1st Return)", "Karmic restructuring; shedding false paths and stepping into true responsibility"),
        (32, "Mercury", "Intellectual & commercial expansion; new trade/skill mastery"),
        (36, "Ketu / Jupiter Cycle", "Spiritual & karmic pivot; culmination of early struggles into stable wisdom"),
        (42, "Rahu", "Breakthrough in status, unconventional elevation, or global/technological reach"),
        (48, "Saturn Maturity", "Consolidated authority, institutional leadership, and legacy building"),
        (54, "Jupiter-Venus", "Harvest of Purva Punya, grandchildren/mentorship, and financial fulfillment"),
        (60, "Shashtiabdapoorthi (60-Year Cosmic Reset)", "Complete Jupiter-Saturn 60-year Samvatsara return; spiritual crown"),
    ]
    life_turning_milestones = []
    for age, ruler, theme in bhrigu_planet_ages:
        yr = birth_year + age
        life_turning_milestones.append({
            "age": age,
            "year": yr,
            "activating_graha": ruler,
            "status": "Completed" if yr < ref_date.year else ("ACTIVE NOW" if yr == ref_date.year else "Upcoming"),
            "destiny_shift": theme,
        })

    # Dasha Sandhi (Mahadasha Junctions)
    deep_dashas = compute_deep_vimshottari(moon_lon, birth_jd, tz_cur, max_levels=2).get("mahadashas", [])
    dasha_turning_dates = []
    for md in deep_dashas:
        dasha_turning_dates.append({
            "mahadasha_lord": md["lord"],
            "start_date": md["start"][:10],
            "end_date": md["end"][:10],
            "is_benefic_for_lagna": md["lord"] in roles["functional_benefics"],
            "life_transformation_focus": (
                f"Major 180° destiny shift into {md['lord']} era — activates houses "
                f"{[h for h, l in roles['house_lords'].items() if l == md['lord']] or ['Nodal Karmic Axis']}."
            ),
        })

    # 2. Granular Good vs Bad Destiny Dates & Exact Local Hours (Location-Calibrated)
    good_destiny_dates = []
    bad_luck_dates = []
    benefic_lords = set(roles["functional_benefics"]) | {"Jupiter", "Venus"}

    for offset in range(scan_days):
        d = ref_date + timedelta(days=offset)
        jd_mid = ephem.local_midnight_jd(d, tz_cur) + 0.5
        t_moon = ephem.moon_lon(jd_mid, True)
        t_moon_sign = int(t_moon // 30) % 12
        t_nak = int(t_moon // (360 / 27)) % 27
        house_from_moon = (t_moon_sign - natal_moon_idx) % 12 + 1
        house_from_lagna = (t_moon_sign - lagna_idx) % 12 + 1
        tara_num = ((t_nak - natal_nak_idx) % 27) % 9 + 1
        tara_name = P.TARAS[tara_num - 1]
        wd = P.weekday_of(d)

        try:
            ev = P.day_events(d, cur_lat, cur_lon, tz_cur)
            sr, ss = ev["sunrise"], ev["sunset"]
            if sr is None or ss is None:
                continue
            dm = (ss - sr) / 15.0
            abhijit_s, abhijit_e = sr + 7 * dm, sr + 8 * dm
            rahu_a, rahu_b = P.seg(sr, ss, 8, P.RAHU_SEG[wd])
            horas = P.hora(d, cur_lat, cur_lon, cur_tz_name, cur_utc_offset)["horas"]
        except Exception:
            continue

        # Power Destiny Date: Moon in Trikona/Kendra/11th from Lagna & Moon + Sampat/Sadhaka/Kshema/Parama Mitra Tara
        if house_from_moon in (1, 3, 6, 7, 10, 11) and house_from_lagna in (1, 2, 4, 5, 7, 9, 10, 11) and tara_num in (2, 4, 6, 8, 9):
            best_hora = next((h for h in horas[:12] if h["lord"] in benefic_lords), horas[0])
            good_destiny_dates.append({
                "date": d.isoformat(),
                "weekday": P.WEEKDAYS[wd],
                "tara": f"{tara_name} ({NAKSHATRAS[t_nak]})",
                "moon_transit": f"{SIGNS[t_moon_sign]} (House {house_from_lagna} from Lagna, House {house_from_moon} from Moon)",
                "power_hora_window": f"{best_hora['start'][11:16]} – {best_hora['end'][11:16]} ({best_hora['lord']} Hora)",
                "abhijit_victory_window": "Not applicable on Wednesday" if wd == 3 else f"{ephem.fmt(abhijit_s, tz_cur)[11:16]} – {ephem.fmt(abhijit_e, tz_cur)[11:16]}",
                "best_for": "Signing life-changing contracts, career launches, investments, marriage proposals, and spiritual initiation",
            })

        # Adverse / Bad Luck Date: Moon in 6, 8, 12 from Moon + Vipat/Pratyak/Vadha Tara
        elif house_from_moon in (6, 8, 12) and tara_num in (3, 5, 7):
            bad_hora = next((h for h in horas[:12] if h["lord"] in ("Saturn", "Mars")), horas[0])
            bad_luck_dates.append({
                "date": d.isoformat(),
                "weekday": P.WEEKDAYS[wd],
                "tara": f"{tara_name} ({NAKSHATRAS[t_nak]})",
                "moon_transit": f"{SIGNS[t_moon_sign]} (House {house_from_moon} from Natal Moon)",
                "avoid_hora_window": f"{bad_hora['start'][11:16]} – {bad_hora['end'][11:16]} ({bad_hora['lord']} Hora)",
                "local_rahu_kaal": f"{ephem.fmt(rahu_a, tz_cur)[11:16]} – {ephem.fmt(rahu_b, tz_cur)[11:16]}",
                "what_to_avoid": "Avoid launching new ventures, lending money, high-stakes litigation, or emotional confrontation",
                "instant_neutralizer": f"Light a ghee/sesame lamp before stepping out and chant {GRAHA_REMEDIES[roles['lagna_lord']]['beej_transliteration']} 27 times.",
            })

    # 3. "Too Many Bad Luck" Counter-Protocol (Durbhagya Nashaka & Karma Reset)
    bad_luck_reset_protocol = {
        "diagnostic_cause": (
            f"When consecutive setbacks occur for {SIGNS[lagna_idx]} Lagna, it is triggered by affliction to the "
            f"9th Bhagya Lord ({roles['house_lords'][9]}) or obstruction by Badhakadhipati ({roles['badhaka_lord']}) "
            f"and Rahu-Ketu transit over natal luminaries."
        ),
        "step_1_salt_and_mustard_cleansing": "On Saturday evening at local Sunset, take a handful of rock salt (Sendha Namak) and black mustard seeds in your right fist, circle it 7 times anti-clockwise around your head, and flush/wash it away in running water to sever negative Drishti and stagnant Aura.",
        "step_2_bhagya_awakening_lamp": f"Every {RAVANA_GRAHA_MASTERY[roles['house_lords'][9]]['wearing_day_hora'].split()[0]} morning during {roles['house_lords'][9]} Hora, light a pure cow-ghee lamp facing {RAVANA_GRAHA_MASTERY[roles['house_lords'][9]]['favorable_direction']} and recite {GRAHA_REMEDIES[roles['house_lords'][9]]['beej_transliteration']} 108 times.",
        "step_3_badhaka_pacification": f"To unlock blocked doors caused by Badhaka Lord {roles['badhaka_lord']}, donate ({GRAHA_REMEDIES[roles['badhaka_lord']]['charitable_dana']}) without announcing it publicly.",
        "step_4_hanuman_kalabhairava_shield": "Recite Kalabhairava Ashtakam at Pradosha twilight for 11 consecutive days to command time (Kaala) and reverse chronic bad-luck streaks.",
    }

    return {
        "lifelong_destiny_turning_milestones": life_turning_milestones,
        "mahadasha_destiny_junctions": dasha_turning_dates,
        "upcoming_auspicious_destiny_dates": good_destiny_dates[:12],
        "upcoming_adverse_bad_luck_dates": bad_luck_dates[:10],
        "how_to_fix_chronic_bad_luck_protocol": bad_luck_reset_protocol,
    }


# ---------------------------------------------------------------------------
# 9. MODULE 4: LOTTERY, WINDFALL & SPECULATION LUCK (WITH EXACT DATE & HORA)
# ---------------------------------------------------------------------------
def analyze_lottery_and_windfall(
    pos: Dict[str, Any],
    asc_lon: float,
    birth_dt_utc: datetime,
    birth_jd: float,
    cur_lat: float,
    cur_lon: float,
    cur_tz_name: Optional[str],
    cur_utc_offset: Optional[float],
    ref_date: Date,
    scan_days: int = 30,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    moon_lon = pos["Moon"]["longitude"]
    sun_lon = pos["Sun"]["longitude"]
    natal_moon_idx = int(moon_lon // 30) % 12
    natal_nak_idx = int(moon_lon // (360 / 27)) % 27
    roles = classify_functional_planets(lagna_idx)
    h_lords = roles["house_lords"]

    # Indu Lagna (Classical Wealth & Windfall Ascendant per Kalidasa / BPHS)
    # Kalas: Sun=30, Moon=16, Mars=6, Mercury=8, Jupiter=10, Venus=12, Saturn=1
    KALAS = {"Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8, "Jupiter": 10, "Venus": 12, "Saturn": 1}
    l9_from_lagna = h_lords[9]
    l9_from_moon = SIGN_LORDS[(natal_moon_idx + 8) % 12]
    indu_sum = (KALAS.get(l9_from_lagna, 1) + KALAS.get(l9_from_moon, 1)) % 12
    if indu_sum == 0:
        indu_sum = 12
    indu_lagna_idx = (natal_moon_idx + indu_sum - 1) % 12
    indu_lord = SIGN_LORDS[indu_lagna_idx]

    # Evaluate 5th (Speculation/Intuition), 8th (Unearned Wealth/Lottery), 11th (Gains), 2nd (Treasury)
    h2_l, h5_l, h8_l, h11_l = h_lords[2], h_lords[5], h_lords[8], h_lords[11]
    windfall_lords = {h5_l, h8_l, h11_l, h2_l, indu_lord}

    # Calculate Natal Windfall & Lottery Potential Score
    score = 55
    windfall_yogas = []
    # Check planets in Indu Lagna or 11th from Indu Lagna
    for p in VEDIC_PLANETS:
        ps = int(pos[p]["longitude"] // 30) % 12
        if ps == indu_lagna_idx:
            score += 12
            windfall_yogas.append(f"{p} occupies Indu Lagna ({SIGNS[indu_lagna_idx]}) — Direct Koteshwara / sudden wealth magnet.")
        elif ps == (indu_lagna_idx + 10) % 12:
            score += 8
            windfall_yogas.append(f"{p} in 11th from Indu Lagna — Multiplying windfall gains.")

    # Check 5th, 8th, 11th interconnections & Rahu in 2/5/8/11
    rahu_h = _house_of_planet(pos["Rahu"]["longitude"], lagna_idx)
    if rahu_h in (2, 5, 8, 11):
        score += 12
        windfall_yogas.append(f"Rahu in House {rahu_h} — Classical Akasmika Dhana (unexpected surge/jackpot amplifier).")
    if _house_of_planet(pos[h5_l]["longitude"], lagna_idx) in (1, 2, 5, 8, 9, 11):
        score += 10
        windfall_yogas.append(f"5th Lord of Speculation ({h5_l}) well-placed in wealth/fortune house.")
    if _house_of_planet(pos[h8_l]["longitude"], lagna_idx) in (2, 5, 8, 9, 11):
        score += 8
        windfall_yogas.append(f"8th Lord of Unearned Windfalls ({h8_l}) linked to Dhana/Labha axis.")
    if not windfall_yogas:
        windfall_yogas.append(
            f"Windfall axis operates primarily during {indu_lord} (Indu Lagna Lord) and {h5_l}/{h11_l} Horas & transits."
        )
    score = min(score, 98)

    # Numerological harmonic numbers for the native
    dob = birth_dt_utc.date()
    moolank = NUM.reduce_single(dob.day)
    bhagyank = NUM.reduce_single(sum(int(c) for c in dob.strftime("%d%m%Y")))
    indu_num = NUM.PLANET_NUMBERS.get(indu_lord, 6)
    l5_num = NUM.PLANET_NUMBERS.get(h5_l, 5)
    l8_num = NUM.PLANET_NUMBERS.get(h8_l, 8)
    l11_num = NUM.PLANET_NUMBERS.get(h11_l, 3)

    # Scan upcoming days at CURRENT LOCATION for exact Golden Lottery Dates, Horas & 15-min Sub-Windows
    tz_cur = ephem.make_tz(cur_tz_name, cur_utc_offset)
    lucky_windfall_windows = []

    for offset in range(scan_days):
        d = ref_date + timedelta(days=offset)
        jd_mid = ephem.local_midnight_jd(d, tz_cur) + 0.5
        t_moon = ephem.moon_lon(jd_mid, True)
        t_moon_sign = int(t_moon // 30) % 12
        t_nak = int(t_moon // (360 / 27)) % 27
        t_pada = int(t_moon // (360 / 108)) % 4 + 1
        tara_num = ((t_nak - natal_nak_idx) % 27) % 9 + 1
        tara_name = P.TARAS[tara_num - 1]
        wd = P.weekday_of(d)

        # Trigger: Moon transiting Indu Lagna, 2nd, 5th, 8th, 9th, or 11th from Lagna/Moon AND Sampat(2)/Kshema(4)/Sadhaka(6)/Mitra(8)/Parama Mitra(9) Tara
        is_wealth_moon = (
            t_moon_sign in (
                indu_lagna_idx,
                _house_sign(lagna_idx, 2),
                _house_sign(lagna_idx, 5),
                _house_sign(lagna_idx, 9),
                _house_sign(lagna_idx, 11),
                (natal_moon_idx + 1) % 12,
                (natal_moon_idx + 4) % 12,
                (natal_moon_idx + 10) % 12,
            )
            and tara_num in (2, 4, 6, 8, 9)
        )
        if not is_wealth_moon:
            continue

        try:
            ev = P.day_events(d, cur_lat, cur_lon, tz_cur)
            sr, ss = ev["sunrise"], ev["sunset"]
            if sr is None or ss is None:
                continue
            rahu_a, rahu_b = P.seg(sr, ss, 8, P.RAHU_SEG[wd])
            rahu_start_s = ephem.fmt(rahu_a, tz_cur)[11:16]
            rahu_end_s = ephem.fmt(rahu_b, tz_cur)[11:16]
            horas = P.hora(d, cur_lat, cur_lon, cur_tz_name, cur_utc_offset)["horas"]
        except Exception:
            continue

        # Pick the Hora ruled by Indu Lord, 5th Lord, 11th Lord, Jupiter, or Venus that does NOT overlap Rahu Kaal
        golden_hora = None
        for h in horas[:14]:
            h_s = h["start"][11:16]
            if h["lord"] in (indu_lord, h5_l, h11_l, "Jupiter", "Venus") and not (rahu_start_s <= h_s < rahu_end_s):
                golden_hora = h
                break
        if not golden_hora:
            golden_hora = horas[0]

        # Compute Peak 15-Minute Lakshmi Sub-Window inside that Golden Hora (first 15 mins after Hora start)
        h_dt_start = datetime.fromisoformat(golden_hora["start"])
        lakshmi_sub_end = h_dt_start + timedelta(minutes=15)

        # Generate date-specific 6 Astro-Harmonic Speculation Numbers (1..69 range)
        day_root = NUM.reduce_single(d.day)
        hora_num = NUM.PLANET_NUMBERS.get(golden_hora["lord"], 3)
        raw_picks = sorted({
            moolank,
            bhagyank,
            indu_num + 9,
            (l5_num * 3 + t_pada) % 60 + 1,
            (l11_num * 4 + day_root) % 60 + 1,
            (hora_num * 5 + (t_nak + 1)) % 69 + 1,
            (int(pos[indu_lord]["longitude"] % 30) + d.day) % 69 + 1,
        })[:6]

        lucky_windfall_windows.append({
            "date": d.isoformat(),
            "weekday": P.WEEKDAYS[wd],
            "wealth_tara": f"{tara_name} ({NAKSHATRAS[t_nak]} Pada {t_pada})",
            "moon_wealth_sector": f"{SIGNS[t_moon_sign]} ({'Indu Lagna' if t_moon_sign == indu_lagna_idx else 'Dhana/Labha Trigger'})",
            "golden_hora_window": f"{golden_hora['start'][11:16]} – {golden_hora['end'][11:16]} ({golden_hora['lord']} Hora)",
            "peak_15m_lakshmi_moment": f"{h_dt_start.strftime('%H:%M')} – {lakshmi_sub_end.strftime('%H:%M')} Local Time",
            "harmonic_lucky_numbers": raw_picks,
            "power_root_digit": hora_num,
            "direction_to_face": RAVANA_GRAHA_MASTERY[golden_hora["lord"]]["favorable_direction"],
        })
        if len(lucky_windfall_windows) >= 10:
            break

    return {
        "windfall_and_lottery_potential_score": score,
        "indu_lagna_wealth_ascendant": {
            "sign": SIGNS[indu_lagna_idx],
            "rashi": RASHIS[indu_lagna_idx],
            "lord": indu_lord,
            "significance": "Indu Lagna is the supreme classical indicator of sudden windfalls, jackpots, and multi-fold wealth accumulation.",
        },
        "key_wealth_and_speculation_lords": {
            "5th_lord_speculation_intuition": h5_l,
            "8th_lord_sudden_unearned_windfall": h8_l,
            "11th_lord_massive_gains": h11_l,
            "2nd_lord_treasury": h2_l,
            "indu_lagna_lord": indu_lord,
        },
        "natal_windfall_yogas": windfall_yogas,
        "core_personal_lucky_digits": sorted({moolank, bhagyank, indu_num, l5_num, l11_num}),
        "location_calibrated_lottery_date_time_windows": lucky_windfall_windows,
        "lakshmi_akarshana_shloka": "ॐ श्रीं ह्रीं श्रीं कमले कमलालये प्रसीद प्रसीद श्रीं ह्रीं श्रीं ॐ महालक्ष्म्यै नमः॥ (Om Shreem Hreem Shreem Kamale Kamalalaye Praseeda Praseeda Shreem Hreem Shreem Om Mahalakshmyai Namah)",
    }


# ---------------------------------------------------------------------------
# 10. MODULE 5: MARRIAGE, NUMBER OF MARRIAGES, SPOUSE & WAYS TO FIX
# ---------------------------------------------------------------------------
def analyze_marriage_and_union(
    pos: Dict[str, Any],
    asc_lon: float,
    birth_jd: float,
    cur_tz_name: Optional[str],
    cur_utc_offset: Optional[float],
    ref_date: Date,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    roles = classify_functional_planets(lagna_idx)
    h7_sign = _house_sign(lagna_idx, 7)
    h7_lord = roles["house_lords"][7]
    h7_lord_sign = int(pos[h7_lord]["longitude"] // 30) % 12
    h7_lord_house = _house_of_planet(pos[h7_lord]["longitude"], lagna_idx)

    # Jaimini Darakaraka (planet with lowest degree in sign among 7 planets)
    karakas = compute_jaimini_karakas(pos)
    dk_planet = karakas.get("chara_karakas", {}).get("Darakaraka", {}).get("planet", "Venus")

    # Upapada Lagna (Arudha of 12th house: UL / A12)
    h12_sign = _house_sign(lagna_idx, 12)
    h12_lord = roles["house_lords"][12]
    h12_lord_sign = int(pos[h12_lord]["longitude"] // 30) % 12
    dist_12 = (h12_lord_sign - h12_sign) % 12
    ul_sign = (h12_lord_sign + dist_12) % 12
    if ul_sign == h12_sign or ul_sign == (h12_sign + 6) % 12:
        ul_sign = (ul_sign + 9) % 12
    ul_lord = SIGN_LORDS[ul_sign]
    second_from_ul_sign = (ul_sign + 1) % 12
    second_from_ul_lord = SIGN_LORDS[second_from_ul_sign]

    # Navamsha (D-9) 7th house & Venus
    d9_asc_sign, _ = compute_varga_position(asc_lon, "D9")
    d9_h7_sign = (d9_asc_sign + 6) % 12
    d9_h7_lord = SIGN_LORDS[d9_h7_sign]
    ven_d9_sign, _ = compute_varga_position(pos["Venus"]["longitude"], "D9")

    # Classical Number of Marriages / Unions Assessment (BPHS & Jaimini Upapada Sutra)
    # Factors for Dual/Multiple Unions (Dwi-Vivaha Yoga):
    # 1. 7th Lord or Venus in Dual Sign (Gemini=2, Virgo=5, Sagittarius=8, Pisces=11)
    # 2. Malefics (Mars, Saturn, Rahu, Ketu, Sun) in 7th house or 2nd from Upapada Lagna
    # 3. Multiple planets occupying the 7th house
    dual_signs = {2, 5, 8, 11}
    dwi_factors = []
    if h7_lord_sign in dual_signs and int(pos["Venus"]["longitude"] // 30) % 12 in dual_signs:
        dwi_factors.append(f"Both 7th Lord ({h7_lord}) and Karaka Venus occupy Dual (Dwiswabhava) signs.")
    planets_in_7th = [p for p in VEDIC_PLANETS if _house_of_planet(pos[p]["longitude"], lagna_idx) == 7]
    if len(planets_in_7th) >= 2:
        dwi_factors.append(f"Multiple Grahas ({', '.join(planets_in_7th)}) occupy the 7th house of union.")
    malefics_in_2nd_ul = [
        p for p in ("Mars", "Saturn", "Rahu", "Ketu", "Sun")
        if int(pos[p]["longitude"] // 30) % 12 == second_from_ul_sign
    ]
    if malefics_in_2nd_ul:
        dwi_factors.append(f"2nd house from Upapada Lagna ({SIGNS[second_from_ul_sign]}) has {', '.join(malefics_in_2nd_ul)}, testing marital longevity.")

    # Benefic protection on 7th or 2nd from UL cancels separation
    benefics_protecting = [
        p for p in ("Jupiter", "Venus", "Mercury")
        if int(pos[p]["longitude"] // 30) % 12 in (h7_sign, ul_sign, second_from_ul_sign, (h7_sign + 6) % 12)
    ]

    if len(dwi_factors) >= 2 and not benefics_protecting:
        union_count_estimate = "2 Major Unions / Marriages Indicated (Dwi-Vivaha Yoga active unless symbolic Kumbha Vivaha remedy is performed)"
        union_number = 2
    elif len(dwi_factors) >= 1:
        union_count_estimate = "1 Primary Lifelong Marriage (with 1 prior serious relationship or major marital renewal phase; protected by benefic grace)"
        union_number = 1
    else:
        union_count_estimate = "1 Stable Lifelong Marriage (Eka-Patni / Eka-Pati Dharmic Bond)"
        union_number = 1

    # Manglik / Kuja Dosha Check
    mars_h = _house_of_planet(pos["Mars"]["longitude"], lagna_idx)
    is_manglik = mars_h in (1, 2, 4, 7, 8, 12)

    # Favorable Marriage / Union Renewal Timing Windows (Vimshottari Dashas of 7th Lord, UL Lord, DK, Venus, Jupiter)
    tz_cur = ephem.make_tz(cur_tz_name, cur_utc_offset)
    deep_dashas = compute_deep_vimshottari(pos["Moon"]["longitude"], birth_jd, tz_cur, max_levels=2).get("mahadashas", [])
    marriage_windows = []
    vivaha_significators = {h7_lord, ul_lord, dk_planet, d9_h7_lord, "Venus", "Jupiter"}
    for md in deep_dashas:
        for ad in md.get("antardashas", []):
            if ad["end"] >= ref_date.isoformat() and (md["lord"] in vivaha_significators and ad["lord"] in vivaha_significators):
                marriage_windows.append({
                    "period": f"{md['lord']} Mahadasha – {ad['lord']} Antardasha",
                    "start": ad["start"][:10],
                    "end": ad["end"][:10],
                    "reason": f"Activates {md['lord']} & {ad['lord']} (7th Lord / Upapada / Darakaraka / Navamsha axis).",
                })
                if len(marriage_windows) >= 6:
                    break
        if len(marriage_windows) >= 6:
            break

    # Ways to Fix Marriage / Overcome Delays or Discord
    fixes = [
        f"Upapada Fast (Jaimini Sutra Remedy): Fast from sunrise to sunset on the weekday ruled by your Upapada Lord ({ul_lord} — {RAVANA_GRAHA_MASTERY[ul_lord]['wearing_day_hora'].split()[0]}) and offer {GRAHA_REMEDIES[ul_lord]['charitable_dana']}.",
        f"2nd-from-Upapada Protection (To prevent divorce/separation): Worship the deity of {second_from_ul_lord} ({RAVANA_GRAHA_MASTERY[second_from_ul_lord]['deity_to_worship']}) to fortify the longevity of the marriage bond.",
        "Swayamvara Parvati & Uma-Maheshwara Mantra: Recite 'Om Hreem Yogini Yogini Yogeshwari Yoga Bhayankari Sakala Sthavara Jangamasya Mukha Hridayam Mama Vasham Akarsha Akarshaya Swaha' 108 times on Fridays.",
    ]
    if union_number >= 2 or is_manglik:
        fixes.append(
            "Kumbha / Vishnu / Ark Vivaha (Symbolic First Union Remedy): Before legal marriage (or to neutralize Dwi-Vivaha & Manglik Dosha), perform symbolic ritual marriage to a clay pot (Kumbha) or Peepal/Banana tree so the astrological 'second marriage' yoga is fulfilled harmoniously within the same spouse!"
        )

    return {
        "estimated_number_of_marriages": union_number,
        "marriage_count_verdict": union_count_estimate,
        "classical_factors_detected": dwi_factors or ["7th house and Upapada Lagna show cohesive single-bond stability."],
        "benefic_protectors_on_union": benefics_protecting,
        "key_marital_pillars": {
            "7th_house_sign": SIGNS[h7_sign],
            "7th_house_lord": f"{h7_lord} (in House {h7_lord_house}, {SIGNS[h7_lord_sign]})",
            "jaimini_darakaraka_spouse_indicator": dk_planet,
            "upapada_lagna_ul": f"{SIGNS[ul_sign]} (Lord: {ul_lord})",
            "2nd_from_upapada_bond_sustainer": f"{SIGNS[second_from_ul_sign]} (Lord: {second_from_ul_lord})",
            "navamsha_d9_7th_house": f"{SIGNS[d9_h7_sign]} (Lord: {d9_h7_lord})",
            "venus_in_d9": SIGNS[ven_d9_sign],
            "manglik_kuja_status": f"Active (Mars in House {mars_h})" if is_manglik else "Non-Manglik / Harmonious",
        },
        "spouse_character_and_direction": {
            "temperament_from_darakaraka": f"Governed by {dk_planet}: brings {RAVANA_GRAHA_MASTERY[dk_planet]['deity_to_worship'].split(',')[0]} grace and {', '.join(RAVANA_GRAHA_MASTERY[dk_planet]['power_colors'][:2])} aura.",
            "favorable_meeting_direction": RAVANA_GRAHA_MASTERY[h7_lord]["favorable_direction"],
        },
        "favorable_marriage_and_renewal_windows": marriage_windows,
        "ways_to_fix_and_harmonize_marriage": fixes,
    }


# ---------------------------------------------------------------------------
# 11. MODULE 6: PROGENY, FERTILITY, NUMBER OF KIDS & GRANDCHILDREN'S FUTURES
# ---------------------------------------------------------------------------
def analyze_progeny_and_lineage(
    pos: Dict[str, Any],
    asc_lon: float,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    roles = classify_functional_planets(lagna_idx)
    h5_sign = _house_sign(lagna_idx, 5)
    h5_lord = roles["house_lords"][5]
    h9_sign = _house_sign(lagna_idx, 9)  # 5th from 5th = Grandchildren (Pautra/Pautri Bhava)
    h9_lord = roles["house_lords"][9]

    # 1. Classical Beeja Sphuta (Male Fertility Point: Sun + Venus + Jupiter) & Kshetra Sphuta (Female Fertility Point: Moon + Mars + Jupiter)
    sun_l = pos["Sun"]["longitude"]
    moon_l = pos["Moon"]["longitude"]
    mars_l = pos["Mars"]["longitude"]
    jup_l = pos["Jupiter"]["longitude"]
    ven_l = pos["Venus"]["longitude"]

    beeja_lon = (sun_l + ven_l + jup_l) % 360.0
    kshetra_lon = (moon_l + mars_l + jup_l) % 360.0
    beeja_sign = int(beeja_lon // 30) % 12
    kshetra_sign = int(kshetra_lon // 30) % 12
    beeja_d9, _ = compute_varga_position(beeja_lon, "D9")
    kshetra_d9, _ = compute_varga_position(kshetra_lon, "D9")

    # Odd sign + odd Navamsha for Beeja, Even sign + even Navamsha for Kshetra, or benefic aspect = Strong Fertility
    jup_house = _house_of_planet(jup_l, lagna_idx)
    h5_lord_house = _house_of_planet(pos[h5_lord]["longitude"], lagna_idx)
    fertility_score = 72
    if jup_house in (1, 2, 4, 5, 7, 9, 10, 11):
        fertility_score += 12
    if h5_lord_house not in (6, 8, 12):
        fertility_score += 10
    fertility_score = min(fertility_score, 98)

    # 2. Saptamsha (D-7) Divisional Chart Analysis for Exact Number of Children & Each Child's Profile
    # BPHS Ch. 80: 1st child from 5th house of D-7; 2nd child from 7th; 3rd from 9th; 4th from 11th
    # Count forward if D-7 Lagna is Odd (Aries=0, Gemini=2, Leo=4, Libra=6, Sag=8, Aqu=10), backward if Even!
    d7_asc_sign, _ = compute_varga_position(asc_lon, "D7")
    d7_is_odd = (d7_asc_sign % 2 == 0)
    step_dir = 1 if d7_is_odd else -1

    d7_planets_by_sign: Dict[int, List[str]] = {i: [] for i in range(12)}
    for p in VEDIC_PLANETS:
        ps, _ = compute_varga_position(pos[p]["longitude"], "D7")
        d7_planets_by_sign[ps].append(p)

    # Estimate number of children (typically 1 to 4 based on active fertile D-7 houses & Putrakaraka Jupiter)
    children_profiles = []
    active_child_count = 0
    for idx, offset_houses in enumerate((4, 6, 8, 10), start=1):  # 5th, 7th, 9th, 11th offsets (0-indexed: 4, 6, 8, 10)
        child_sign = (d7_asc_sign + step_dir * offset_houses) % 12
        child_lord = SIGN_LORDS[child_sign]
        child_lord_d7_sign, _ = compute_varga_position(pos[child_lord]["longitude"], "D7")
        occupants = d7_planets_by_sign[child_sign]

        # Classical Oja (Odd = Male/Yang inclination) vs Yugma (Even = Female/Yin inclination) of child_lord's D-7 sign
        gender_inclination = (
            "Strong Yang / Son inclination (Putra Yoga per Oja Rashi)"
            if (child_lord_d7_sign % 2 == 0 or child_lord in ("Sun", "Mars", "Jupiter", "Rahu"))
            else "Strong Yin / Daughter inclination (Putri Yoga per Yugma Rashi)"
        )

        # Check if this child slot is strongly activated
        is_strong = (
            child_lord not in ("Saturn", "Ketu")
            or bool(occupants)
            or idx <= 2
        )
        if is_strong and active_child_count < 3:
            active_child_count += 1
            children_profiles.append({
                "child_order": f"Child #{active_child_count}",
                "d7_house_sign": f"{SIGNS[child_sign]} ({RASHIS[child_sign]})",
                "governing_planet": child_lord,
                "d7_occupants": occupants or ["Unoccupied (governed purely by sign lord)"],
                "classical_gender_tendency": gender_inclination,
                "personality_and_future_destiny": (
                    f"Ruled by {child_lord} in {SIGNS[child_lord_d7_sign]} (D-7): gifted with "
                    f"{RAVANA_GRAHA_MASTERY[child_lord]['deity_to_worship'].split(',')[0]} blessings, excelling in "
                    f"fields connected to {child_lord} and bringing rising fortune to the family."
                ),
            })

    # 3. Grandchildren (Pautra / Pautri) & 3rd-Generation Future Analysis
    # Classical Rule: 9th House = 5th from 5th (Children's Children!), plus D-7 9th house & Jupiter
    d7_grandchild_sign = (d7_asc_sign + step_dir * 8) % 12
    d7_grandchild_lord = SIGN_LORDS[d7_grandchild_sign]
    h9_lord_sign = int(pos[h9_lord]["longitude"] // 30) % 12
    grandchild_count_est = max(2, active_child_count * 2 - 1)

    grandchildren_analysis = {
        "bhavat_bhavam_9th_house": f"{SIGNS[h9_sign]} (Ruled by {h9_lord} in {SIGNS[h9_lord_sign]})",
        "d7_grandchildren_sign": f"{SIGNS[d7_grandchild_sign]} (Ruled by {d7_grandchild_lord})",
        "estimated_grandchildren_blessing": f"{grandchild_count_est} to {grandchild_count_est + 2} Grandchildren (Vansha Vriddhi Yoga)",
        "grandchildren_future_destiny": (
            f"With {h9_lord} governing the 5th-from-5th house and {d7_grandchild_lord} ruling the D-7 9th axis, "
            f"your grandchildren carry strong {h9_lord}/{d7_grandchild_lord} samskaras — destined for higher scholarship, "
            f"international/technological prosperity, and reviving the family's spiritual & material prestige."
        ),
        "ancestral_blessing_to_leave_them": (
            f"Plant a {RAVANA_GRAHA_MASTERY[h9_lord]['sacred_tree_plant'].split('&')[0].strip()} tree and establish an annual "
            f"charity on {RAVANA_GRAHA_MASTERY[h9_lord]['wearing_day_hora'].split()[0]}s; this acts as an unbroken kavacha for 3 generations."
        ),
    }

    return {
        "fertility_and_conception_capacity": {
            "able_to_have_children": True,
            "fertility_vitality_score": fertility_score,
            "verdict": "Strong Natural Santana Yoga (Blessed Progeny Potential)" if fertility_score >= 78 else "Moderate Santana Yoga (Strengthened via Santana Gopala Mantra & Guru remedies)",
            "beeja_sphuta_longitude": round(beeja_lon, 2),
            "beeja_sphuta_sign": f"{SIGNS[beeja_sign]} (D-9: {SIGNS[beeja_d9]})",
            "kshetra_sphuta_longitude": round(kshetra_lon, 2),
            "kshetra_sphuta_sign": f"{SIGNS[kshetra_sign]} (D-9: {SIGNS[kshetra_d9]})",
            "5th_house_sign": SIGNS[h5_sign],
            "5th_house_lord": f"{h5_lord} (in House {h5_lord_house})",
            "d7_saptamsha_lagna": f"{SIGNS[d7_asc_sign]} ({'Odd / Forward Counting' if d7_is_odd else 'Even / Reverse Counting'})",
        },
        "estimated_number_of_children": f"{active_child_count} (Potential range: {active_child_count} to {active_child_count + 1})",
        "individual_children_predictions": children_profiles,
        "grandchildren_and_lineage_future": grandchildren_analysis,
        "santana_gopala_shloka": "ॐ श्रीं ह्रीं क्लीं ग्लौं देवकीसुत गोविन्द वासुदेव जगत्पते। देहि मे तनयं कृष्ण त्वामहं शरणं गतः॥ (Om Shreem Hreem Kleem Glaum Devakisuta Govinda Vasudeva Jagatpate, Dehi Me Tanayam Krishna Tvamaham Sharanam Gatah)",
    }


# ---------------------------------------------------------------------------
# 12. MODULE 7: PAST LIFE, FUTURE LIFE, KARMIC RINAS & THIS LIFE'S BLUEPRINT
# ---------------------------------------------------------------------------
def analyze_past_future_reincarnation(
    pos: Dict[str, Any],
    asc_lon: float,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    roles = classify_functional_planets(lagna_idx)
    karakas = compute_jaimini_karakas(pos)
    ak_info = karakas.get("chara_karakas", {}).get("Atmakaraka", {})
    ak_planet = ak_info.get("planet", "Sun")
    amk_planet = karakas.get("chara_karakas", {}).get("Amatyakaraka", {}).get("planet", "Jupiter")

    # 1. Past Life Analysis (Ketu Sign/House, D-60 Shashtiamsha Deity, 5th/9th Purva Punya, Retrograde Planets)
    ketu_lon = pos["Ketu"]["longitude"]
    ketu_sign = SIGNS[int(ketu_lon // 30) % 12]
    ketu_house = _house_of_planet(ketu_lon, lagna_idx)
    ketu_nak = NAKSHATRAS[int(ketu_lon // (360 / 27)) % 27]
    ketu_arch = KETU_PAST_LIFE_SIGN[ketu_sign]

    # D-60 Shashtiamsha (1/60th division — "Sarvam Shashtiamshe" for past-life root karma)
    asc_d60_part = int((asc_lon % 30.0) * 2.0) % 60
    ak_d60_part = int((pos[ak_planet]["longitude"] % 30.0) * 2.0) % 60
    lagna_d60_deity = SHASTIAMSA_DEITIES[asc_d60_part]
    ak_d60_deity = SHASTIAMSA_DEITIES[ak_d60_part]

    # Retrograde (Vakri) Planets = Unfinished Past-Life Promises & Intense Prarabdha
    retro_lessons = []
    for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        if pos[p]["speed"] < 0:
            retro_lessons.append({
                "planet": p,
                "sign": SIGNS[int(pos[p]["longitude"] // 30) % 12],
                "house": _house_of_planet(pos[p]["longitude"], lagna_idx),
                "unfinished_past_life_promise": (
                    f"Retrograde {p} in House {_house_of_planet(pos[p]['longitude'], lagna_idx)} shows a deep "
                    f"unfulfilled vow from your previous birth regarding {RAVANA_GRAHA_MASTERY[p]['deity_to_worship'].split(',')[0]} "
                    f"and {PLANET_DISEASES[p]['organs'].split(',')[0]} energy — you have returned to perfect it internally."
                ),
            })

    # Detect Active Past-Life Mistakes / Rinas (Debts) & How to Counter/Fix Them
    active_rinas = []
    sun_h = _house_of_planet(pos["Sun"]["longitude"], lagna_idx)
    moon_h = _house_of_planet(pos["Moon"]["longitude"], lagna_idx)
    jup_h = _house_of_planet(pos["Jupiter"]["longitude"], lagna_idx)
    ven_h = _house_of_planet(pos["Venus"]["longitude"], lagna_idx)
    sat_h = _house_of_planet(pos["Saturn"]["longitude"], lagna_idx)

    if sun_h in (6, 8, 12) or int(pos["Sun"]["longitude"] // 30) == int(pos["Rahu"]["longitude"] // 30):
        active_rinas.append({"rina": "Pitru Rina (Ancestral / Paternal Debt)", **PAST_LIFE_RINAS["Pitru Rina (Ancestral / Paternal Debt)"]})
    if moon_h in (6, 8, 12) or int(pos["Moon"]["longitude"] // 30) == int(pos["Ketu"]["longitude"] // 30):
        active_rinas.append({"rina": "Matru Rina (Maternal / Nurturing Debt)", **PAST_LIFE_RINAS["Matru Rina (Maternal / Nurturing Debt)"]})
    if jup_h in (6, 8, 12) or pos["Jupiter"]["speed"] < 0:
        active_rinas.append({"rina": "Deva / Guru Rina (Divine & Spiritual Preceptor Debt)", **PAST_LIFE_RINAS["Deva / Guru Rina (Divine & Spiritual Preceptor Debt)"]})
    if ven_h in (6, 8, 12) or pos["Venus"]["speed"] < 0:
        active_rinas.append({"rina": "Stri / Kalatra Rina (Spousal & Sacred Union Debt)", **PAST_LIFE_RINAS["Stri / Kalatra Rina (Spousal & Sacred Union Debt)"]})
    if sat_h in (1, 4, 7, 8, 12):
        active_rinas.append({"rina": "Jeeva / Bhuta Rina (Nature & Living Beings Debt)", **PAST_LIFE_RINAS["Jeeva / Bhuta Rina (Nature & Living Beings Debt)"]})
    if not active_rinas:
        active_rinas.append({"rina": "Pitru Rina (Ancestral / Paternal Debt)", **PAST_LIFE_RINAS["Pitru Rina (Ancestral / Paternal Debt)"]})
        active_rinas.append({"rina": "Deva / Guru Rina (Divine & Spiritual Preceptor Debt)", **PAST_LIFE_RINAS["Deva / Guru Rina (Divine & Spiritual Preceptor Debt)"]})

    # 2. This Life's True Goal, Purpose & Exact Type of Life to Live (Rahu Evolution + Atmakaraka + 10th House)
    rahu_lon = pos["Rahu"]["longitude"]
    rahu_sign = SIGNS[int(rahu_lon // 30) % 12]
    rahu_house = _house_of_planet(rahu_lon, lagna_idx)
    h10_lord = roles["house_lords"][10]

    this_life_blueprint = {
        "supreme_soul_goal_rahu_axis": (
            f"Shift from Ketu in {ketu_sign} (House {ketu_house}) to Rahu in {rahu_sign} (House {rahu_house}): "
            f"stop relying solely on past-life {ketu_arch['era_persona'].split(',')[0]} habits, and boldly master "
            f"House {rahu_house} ({rahu_sign}) frontiers in this incarnation."
        ),
        "atmakaraka_soul_king": f"{ak_planet} — Your soul chose this birth to master humility, self-realization, and dharma through {ak_planet}'s lessons.",
        "amatyakaraka_career_minister": f"{amk_planet} & 10th Lord {h10_lord} — Ideal vocation in leadership, advisory, strategy, technology, or healing governed by {amk_planet}/{h10_lord}.",
        "type_of_life_to_live": {
            "ideal_daily_routine_dinacharya": (
                f"Wake during Brahma Muhurta (90 mins before local Sunrise); perform 15 mins of "
                f"{RAVANA_GRAHA_MASTERY[roles['lagna_lord']]['deity_to_worship'].split(',')[0]} dhyana; schedule high-stakes work during "
                f"{roles['lagna_lord']} and {roles['house_lords'][9]} Horas."
            ),
            "ideal_living_environment": (
                f"Home or office with open, well-lit {RAVANA_GRAHA_MASTERY[roles['lagna_lord']]['favorable_direction']} and North-East sectors, "
                f"near {', '.join(RAVANA_GRAHA_MASTERY[roles['lagna_lord']]['keep_close_objects'][:2])}."
            ),
            "dharma_rule_never_to_break": (
                f"Never compromise on the ethical principle of {ak_planet} ({GRAHA_REMEDIES[ak_planet]['conduct_remedy']}); "
                f"when your {ak_planet} conduct is pure, all 9 planets align behind your sankalpa."
            ),
        },
    }

    # 3. Future Life & Post-Life Trajectory (12th House, 12th from Karakamsha KL, Ketu, Jupiter)
    ak_d9_sign, _ = compute_varga_position(pos[ak_planet]["longitude"], "D9")
    twelfth_from_kl = (ak_d9_sign + 11) % 12
    twelfth_kl_lord = SIGN_LORDS[twelfth_from_kl]
    ketu_d9_sign, _ = compute_varga_position(ketu_lon, "D9")
    h12_lord = roles["house_lords"][12]

    moksha_strong = (
        ketu_d9_sign in (twelfth_from_kl, ak_d9_sign, 3, 7, 11)
        or _house_of_planet(pos["Jupiter"]["longitude"], lagna_idx) in (1, 4, 5, 8, 9, 12)
    )
    future_life_trajectory = {
        "karakamsha_sign_d9": SIGNS[ak_d9_sign],
        "12th_from_karakamsha_moksha_gate": f"{SIGNS[twelfth_from_kl]} (Ruled by {twelfth_kl_lord})",
        "12th_house_lord_uttara_gati": h12_lord,
        "post_life_destination_verdict": (
            "Sayujya / Kaivalya Moksha Trajectory (Final Liberation or Ascent to Vishnuloka/Shivaloka without forced karmic rebirth)"
            if moksha_strong
            else f"Elevated Urdhva-Loka & Noble Rebirth Trajectory (Rebirth into a luminous, scholarly, and prosperous {twelfth_kl_lord}-governed spiritual lineage)"
        ),
        "how_to_consciously_engineer_next_life": (
            f"By worshipping your Ishta Devata ({RAVANA_GRAHA_MASTERY[twelfth_kl_lord]['deity_to_worship']}) and clearing your "
            f"active Rinas before age 54, you transform prarabdha into liberation (Jivanmukti)."
        ),
    }

    return {
        "past_life_reading_purva_janma": {
            "ketu_past_life_sign_and_house": f"Ketu in {ketu_sign} (House {ketu_house}, {ketu_nak} Nakshatra)",
            "past_life_archetype_and_status": ketu_arch["era_persona"],
            "talents_and_siddhis_carried_forward": ketu_arch["mastered_gifts"],
            "past_life_unfinished_attachment": ketu_arch["unfulfilled_residue"],
            "d60_shashtiamsha_lagna_deity": lagna_d60_deity,
            "d60_atmakaraka_soul_deity": ak_d60_deity,
            "retrograde_unfinished_promises": retro_lessons,
        },
        "bad_things_done_in_past_lives_and_how_to_fix": active_rinas,
        "this_life_goal_and_how_to_live": this_life_blueprint,
        "future_life_and_moksha_trajectory": future_life_trajectory,
    }


# ---------------------------------------------------------------------------
# 13. MODULE 8: RAVANA SAMHITA 9-PLANET MASTERY ("COMMAND ALL 9 GRAHAS")
# ---------------------------------------------------------------------------
def analyze_ravana_planetary_mastery(
    pos: Dict[str, Any],
    asc_lon: float,
    birth_dt_utc: datetime,
) -> Dict[str, Any]:
    lagna_idx = int(asc_lon // 30) % 12
    roles = classify_functional_planets(lagna_idx)
    h_lords = roles["house_lords"]

    # 1. Strategic Gemstone Prescription (Life Stone, Lucky Bhagya Stone, Intelligence/Punya Stone, and Forbidden Stones!)
    life_lord = h_lords[1]
    punya_lord = h_lords[5]
    bhagya_lord = h_lords[9]

    recommended_gems = [
        {
            "category": "1. Jeevana Ratna (Life & Vitality Stone — 1st House Lagna Lord)",
            "planet": life_lord,
            **{k: RAVANA_GRAHA_MASTERY[life_lord][k] for k in (
                "primary_gem", "substitute_gem", "carat_weight", "metal", "finger", "wearing_day_hora", "prana_pratishtha_shloka"
            )},
            "purpose": "Protects physical health, immunity, self-confidence, longevity, and personal magnetism.",
        },
        {
            "category": "2. Bhagya Ratna (Supreme Luck & Destiny Stone — 9th House Dharma/Fortune Lord)",
            "planet": bhagya_lord,
            **{k: RAVANA_GRAHA_MASTERY[bhagya_lord][k] for k in (
                "primary_gem", "substitute_gem", "carat_weight", "metal", "finger", "wearing_day_hora", "prana_pratishtha_shloka"
            )},
            "purpose": "Unlocks divine grace, sudden breakthroughs, wealth multiplication, and father/guru blessings.",
        },
        {
            "category": "3. Punya & Siddhi Ratna (Speculation, Progeny & Intellect Stone — 5th House Trikona Lord)",
            "planet": punya_lord,
            **{k: RAVANA_GRAHA_MASTERY[punya_lord][k] for k in (
                "primary_gem", "substitute_gem", "carat_weight", "metal", "finger", "wearing_day_hora", "prana_pratishtha_shloka"
            )},
            "purpose": "Activates Purva Punya, intuition, lottery/investment luck, children's prosperity, and mantra siddhi.",
        },
    ]

    forbidden_gems = []
    for mp in set(roles["functional_malefics"]) | {h_lords[6], h_lords[8], h_lords[12]}:
        if mp not in (life_lord, punya_lord, bhagya_lord):
            forbidden_gems.append({
                "planet": mp,
                "gem_to_avoid": RAVANA_GRAHA_MASTERY[mp]["primary_gem"],
                "why_avoid": f"{mp} rules dusthana/malefic houses for {SIGNS[lagna_idx]} Lagna; wearing its gem amplifies obstacles. Pacify it via Dana (charity) & Beej Mantra instead!",
            })

    # 2. All 9 Planets Command & Management Matrix (Ravana Samhita Protocol)
    nine_planet_command = []
    for p in VEDIC_PLANETS:
        p_lon = pos[p]["longitude"]
        p_sign = int(p_lon // 30) % 12
        p_house = _house_of_planet(p_lon, lagna_idx)
        is_benefic = p in roles["functional_benefics"]
        is_malefic = p in roles["functional_malefics"]
        strategy_type = (
            "AMPLIFY & HARNESS (Functional Benefic / Yogakaraka)"
            if is_benefic
            else ("PACIFY, TRANSMUTE & SHIELD (Functional Malefic / Dusthana)" if is_malefic else "BALANCE & CHANNEL (Neutral / Conditional)")
        )
        m_info = RAVANA_GRAHA_MASTERY[p]
        r_info = GRAHA_REMEDIES[p]
        nine_planet_command.append({
            "planet": p,
            "natal_placement": f"{SIGNS[p_sign]} (House {p_house})",
            "functional_role": strategy_type,
            "deity_to_worship": m_info["deity_to_worship"],
            "when_and_how_long_to_worship": f"{m_info['wearing_day_hora']} | {m_info['worship_duration']}",
            "beej_mantra": r_info["beej_mantra"],
            "beej_transliteration": r_info["beej_transliteration"],
            "puranic_shloka": r_info["puranic_mantra"],
            "ravana_samhita_mastery_secret": m_info["ravana_tantra_secret"],
            "charitable_dana_to_command": r_info["charitable_dana"],
        })

    # 3. Synthesized "Keep Close vs. Avoid" Master Checklist for the Native
    dob = birth_dt_utc.date()
    moolank = NUM.reduce_single(dob.day)
    bhagyank = NUM.reduce_single(sum(int(c) for c in dob.strftime("%d%m%Y")))

    keep_close_master = {
        "sacred_objects_for_wallet_and_desk": (
            RAVANA_GRAHA_MASTERY[life_lord]["keep_close_objects"][:2]
            + RAVANA_GRAHA_MASTERY[bhagya_lord]["keep_close_objects"][:2]
        ),
        "power_colors_to_wear": list(dict.fromkeys(
            RAVANA_GRAHA_MASTERY[life_lord]["power_colors"] + RAVANA_GRAHA_MASTERY[bhagya_lord]["power_colors"]
        )),
        "power_numbers_to_use": sorted(set(
            RAVANA_GRAHA_MASTERY[life_lord]["power_numbers"][:3]
            + RAVANA_GRAHA_MASTERY[bhagya_lord]["power_numbers"][:3]
            + [moolank, bhagyank]
        )),
        "favorable_metals": list(dict.fromkeys([
            RAVANA_GRAHA_MASTERY[life_lord]["metal"],
            RAVANA_GRAHA_MASTERY[bhagya_lord]["metal"],
        ])),
        "auspicious_directions_for_head_and_desk": [
            f"Primary: {RAVANA_GRAHA_MASTERY[life_lord]['favorable_direction']} ({life_lord})",
            f"Fortune: {RAVANA_GRAHA_MASTERY[bhagya_lord]['favorable_direction']} ({bhagya_lord})",
        ],
        "trees_and_plants_to_nurture": [
            RAVANA_GRAHA_MASTERY[life_lord]["sacred_tree_plant"],
            RAVANA_GRAHA_MASTERY[bhagya_lord]["sacred_tree_plant"],
        ],
        "animals_to_feed_for_instant_punya": [
            RAVANA_GRAHA_MASTERY[life_lord]["animal_service"],
            RAVANA_GRAHA_MASTERY[h_lords[8]]["animal_service"],
        ],
    }

    avoid_master = {
        "objects_to_strictly_remove_from_home_and_body": (
            RAVANA_GRAHA_MASTERY[life_lord]["avoid_objects"]
            + RAVANA_GRAHA_MASTERY[h_lords[8]]["avoid_objects"][:2]
        ),
        "colors_to_avoid_in_high_stakes": list(dict.fromkeys(
            RAVANA_GRAHA_MASTERY[life_lord]["avoid_colors"] + RAVANA_GRAHA_MASTERY[bhagya_lord]["avoid_colors"]
        )),
        "numbers_to_avoid": sorted(set(
            RAVANA_GRAHA_MASTERY[life_lord]["avoid_numbers"]
            + NUM.INIMICAL.get(moolank, [])
        )),
        "habits_and_actions_to_never_do": [
            f"Never wear the gemstone of {h_lords[8]} ({RAVANA_GRAHA_MASTERY[h_lords[8]]['primary_gem']}) or {roles['badhaka_lord']} without specific neutralization.",
            f"Avoid initiating major ventures during local Rahu Kaal or when Moon transits {SIGNS[(int(pos['Moon']['longitude'] // 30) + 7) % 12]} (8th from your Natal Moon).",
            "Never keep broken clocks, cracked mirrors, or rusted iron on the rooftop or near the main entrance.",
        ],
    }

    return {
        "functional_planet_hierarchy": roles,
        "strategic_gemstone_prescription": recommended_gems,
        "forbidden_gemstones_warning": forbidden_gems,
        "nine_graha_command_protocols": nine_planet_command,
        "things_to_keep_close_master_guide": keep_close_master,
        "things_to_avoid_master_guide": avoid_master,
    }


# ---------------------------------------------------------------------------
# 14. MASTER CROSS-LINKED DESTINY ORCHESTRATOR
# ---------------------------------------------------------------------------
def compute_master_destiny_dossier(
    birth_dt_utc: datetime,
    birth_lat: float,
    birth_lon: float,
    birth_tz_name: Optional[str] = "Asia/Kolkata",
    birth_utc_offset: Optional[float] = None,
    name: Optional[str] = "Native",
    current_lat: Optional[float] = None,
    current_lon: Optional[float] = None,
    current_tz_name: Optional[str] = None,
    current_utc_offset: Optional[float] = None,
    current_city: Optional[str] = None,
    target_date: Optional[Date] = None,
    scan_days: int = 30,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Compute the complete cross-linked Destiny, Medical/Longevity, Accident,
    Lottery/Windfall, Marriage, Progeny/Grandchildren, Past/Future Life, and
    Ravana Samhita 9-Planet Mastery Dossier calibrated to the native's current location."""
    ephem.set_ayanamsa_mode(ayanamsa)
    birth_jd = ephem.jd_from_utc(birth_dt_utc)
    pos = ephem.all_positions(birth_jd, sidereal=True, true_node=False)
    cusps, asc_lon, mc = ephem.houses(birth_jd, birth_lat, birth_lon, "W", True)

    # Resolve Current Location (defaults to Birth Location if not separately provided)
    c_lat = current_lat if current_lat is not None else birth_lat
    c_lon = current_lon if current_lon is not None else birth_lon
    c_tz = current_tz_name if (current_tz_name or current_utc_offset is not None) else birth_tz_name
    c_off = current_utc_offset if current_utc_offset is not None else birth_utc_offset
    ref_d = target_date or datetime.now(timezone.utc).date()

    # Relocation / Current Horizon Ascendant right now
    now_jd = ephem.jd_from_utc(datetime.now(timezone.utc))
    _, cur_horizon_asc, _ = ephem.houses(now_jd, c_lat, c_lon, "W", True)
    relocated_birth_cusps, relocated_birth_asc, _ = ephem.houses(birth_jd, c_lat, c_lon, "W", True)

    medical_longevity = analyze_medical_and_longevity(pos, asc_lon, birth_jd, c_lat, c_lon, c_tz, c_off, ref_d)
    accidents_safety = analyze_accidents_and_safety(pos, asc_lon, c_lat, c_lon, c_tz, c_off, ref_d, scan_days=scan_days)
    destiny_dates = analyze_destiny_turning_points(pos, asc_lon, birth_dt_utc, birth_jd, c_lat, c_lon, c_tz, c_off, ref_d, scan_days=max(scan_days, 45))
    lottery_windfall = analyze_lottery_and_windfall(pos, asc_lon, birth_dt_utc, birth_jd, c_lat, c_lon, c_tz, c_off, ref_d, scan_days=scan_days)
    marriage_union = analyze_marriage_and_union(pos, asc_lon, birth_jd, c_tz, c_off, ref_d)
    progeny_lineage = analyze_progeny_and_lineage(pos, asc_lon)
    past_future_life = analyze_past_future_reincarnation(pos, asc_lon)
    ravana_mastery = analyze_ravana_planetary_mastery(pos, asc_lon, birth_dt_utc)

    # Cross-Link Numerology & Soul Guidance
    tz_b = ephem.make_tz(birth_tz_name, birth_utc_offset)
    local_birth_dt = birth_dt_utc.astimezone(tz_b)
    num_profile = NUM.profile(
        name or "Native",
        local_birth_dt.date(),
        "chaldean",
        birth_details={
            "time": local_birth_dt.strftime("%H:%M:%S"),
            "latitude": birth_lat,
            "longitude": birth_lon,
            "timezone": birth_tz_name or "Asia/Kolkata",
            "utc_offset": birth_utc_offset,
        },
        transit_date=ref_d,
    )
    soul_guidance = compute_soul_guidance(pos, asc_lon)

    return {
        "name": name or "Native",
        "ayanamsa": ayanamsa,
        "reference_date": ref_d.isoformat(),
        "birth_chart_anchor": {
            "birth_utc": birth_dt_utc.isoformat(),
            "birth_latitude": birth_lat,
            "birth_longitude": birth_lon,
            "natal_lagna": f"{SIGNS[int(asc_lon // 30) % 12]} ({round(asc_lon % 30, 2)}°)",
            "natal_moon": f"{SIGNS[int(pos['Moon']['longitude'] // 30) % 12]} ({NAKSHATRAS[int(pos['Moon']['longitude'] // (360 / 27)) % 27]})",
            "natal_sun": f"{SIGNS[int(pos['Sun']['longitude'] // 30) % 12]} ({round(pos['Sun']['longitude'] % 30, 2)}°)",
        },
        "current_location_anchor": {
            "city": current_city or "Current Location",
            "latitude": c_lat,
            "longitude": c_lon,
            "timezone": c_tz or f"UTC{c_off:+g}" if (c_tz or c_off is not None) else "UTC",
            "relocated_birth_lagna_at_current_city": SIGNS[int(relocated_birth_asc // 30) % 12],
            "current_live_tatkalika_lagna": SIGNS[int(cur_horizon_asc // 30) % 12],
        },
        "medical_diseases_and_longevity": medical_longevity,
        "accidents_and_safety_windows": accidents_safety,
        "destiny_turning_points_and_dates": destiny_dates,
        "lottery_and_windfall_oracle": lottery_windfall,
        "marriage_count_and_remedies": marriage_union,
        "progeny_children_and_grandchildren": progeny_lineage,
        "past_life_future_life_and_purpose": past_future_life,
        "ravana_samhita_planetary_mastery": ravana_mastery,
        "cross_linked_numerology": {
            "moolank": num_profile["vedic"]["psychic_number_moolank"],
            "bhagyank": num_profile["vedic"]["destiny_number_bhagyank"],
            "namank": num_profile["vedic"]["name_number_chaldean"],
            "cosmic_harmony_score": (num_profile.get("astro_numerology") or {}).get("cosmic_harmony_score_percent"),
            "lucky_calendar_dates": num_profile["lucky_numbers_generator"]["lucky_calendar_dates"],
            "dates_to_avoid": num_profile["numbers_to_avoid"]["dates_of_month_to_avoid"],
        },
        "cross_linked_soul_guidance": soul_guidance,
    }

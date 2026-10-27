"""Other domains: I-Ching, Vastu, Palmistry reference, Kabbalah, Mayan calendar, dream symbols, crystals,
Chinese yearly forecast, and puja / dosha remedies. All text original to PanchangHub."""
from __future__ import annotations
import hashlib, random
from datetime import date as Date

# ---------------- I-Ching ----------------
TRIGRAMS = {  # bits bottom->top (1 = yang)
    "Qian": ((1, 1, 1), "Heaven", "creative strength"), "Dui": ((1, 1, 0), "Lake", "joy and openness"),
    "Li": ((1, 0, 1), "Fire", "clarity and attachment"), "Zhen": ((1, 0, 0), "Thunder", "arousing movement"),
    "Xun": ((0, 1, 1), "Wind", "gentle penetration"), "Kan": ((0, 1, 0), "Water", "danger and depth"),
    "Gen": ((0, 0, 1), "Mountain", "stillness"), "Kun": ((0, 0, 0), "Earth", "receptive devotion")}
_ORDER = ["Qian", "Zhen", "Kan", "Gen", "Kun", "Xun", "Li", "Dui"]
_KW = [[1, 34, 5, 26, 11, 9, 14, 43], [25, 51, 3, 27, 24, 42, 21, 17], [6, 40, 29, 4, 7, 59, 64, 47], [33, 62, 39, 52, 15, 53, 56, 31],
       [12, 16, 8, 23, 2, 20, 35, 45], [44, 32, 48, 18, 46, 57, 50, 28], [13, 55, 63, 22, 36, 37, 30, 49], [10, 54, 60, 41, 19, 61, 38, 58]]
HEX = ["The Creative|Act with strength and persistence; initiative is favoured", "The Receptive|Follow, support and yield; devotion brings success",
 "Difficulty at the Beginning|Early chaos; organise patiently and seek helpers", "Youthful Folly|Learn humbly; ask sincerely, not repeatedly",
 "Waiting|Nourish yourself and wait with confidence for the right time", "Conflict|Avoid litigation; seek mediation and stop halfway",
 "The Army|Discipline and good leadership are needed for collective effort", "Holding Together|Unite around a trustworthy centre; join early",
 "Small Taming|Restrain gently; small steps accumulate", "Treading|Proceed with courtesy even near danger",
 "Peace|Heaven and earth in harmony; a time of flourishing", "Standstill|Communication blocked; keep integrity and withdraw",
 "Fellowship|Cooperation in the open succeeds", "Great Possession|Abundance well used; stay modest",
 "Modesty|Balance excess and lack; humility carries things through", "Enthusiasm|Inspire others and prepare the ground",
 "Following|Adapt to the times and follow what is right", "Work on the Decayed|Repair what was spoiled; reflect before and after",
 "Approach|Favourable advance; act before the season turns", "Contemplation|Observe deeply and become an example",
 "Biting Through|Remove obstacles decisively and justly", "Grace|Beauty and form; keep substance under ornament",
 "Splitting Apart|Do not act; let decay complete itself", "Return|The turning point; light comes back, begin again",
 "Innocence|Act without hidden motives; the unexpected happens", "Great Taming|Hold power in reserve; study and accumulate",
 "Nourishment|Watch what you take in, in body and speech", "Great Preponderance|A beam under strain; act boldly but carefully",
 "The Abysmal|Repeated danger; keep sincere and flowing like water", "The Clinging|Clarity depends on what it clings to; care for it",
 "Influence|Mutual attraction; stay receptive", "Duration|Endure through consistent purpose",
 "Retreat|Withdraw in time to preserve strength", "Great Power|Strength must be used with right",
 "Progress|Rapid advance and recognition", "Darkening of the Light|Hide your light; persevere inwardly",
 "The Family|Order begins at home with clear roles", "Opposition|Small matters succeed despite divergence",
 "Obstruction|Turn back to reflect and seek help", "Deliverance|Release tension; forgive and move on quickly",
 "Decrease|Simplify; sincere small offerings suffice", "Increase|Benefit spreads; undertake ventures",
 "Breakthrough|Resolve and openly declare the truth", "Coming to Meet|A powerful encounter; beware of being led astray",
 "Gathering Together|Assemble around a shared purpose", "Pushing Upward|Steady effort upward; seek guidance",
 "Oppression|Exhaustion; speak little and stay inwardly firm", "The Well|A source available to all; maintain it",
 "Revolution|Change when the time is ripe and trust is built", "The Cauldron|Nourishment and culture; refine and transform",
 "The Arousing|Shock that brings awakening; stay composed", "Keeping Still|Quiet the restless mind; stop at the right time",
 "Development|Gradual progress, like a tree on a mountain", "The Marrying Maiden|Know your place; avoid forcing outcomes",
 "Abundance|Peak fullness; be like the sun at midday", "The Wanderer|Be cautious and correct when away from home",
 "The Gentle|Penetrate gently and persistently", "The Joyous|Shared joy and encouragement",
 "Dispersion|Dissolve rigidity; unite through the sacred", "Limitation|Set reasonable limits, not bitter ones",
 "Inner Truth|Sincerity moves even the stubborn", "Small Preponderance|Attend to small matters; stay low",
 "After Completion|Order achieved; guard against decline", "Before Completion|Almost there; proceed with caution"]

def hexagram_of(lines):
    """lines: six values bottom->top, 1 = yang / 0 = yin."""
    lo, up = tuple(lines[:3]), tuple(lines[3:])
    name = {v[0]: k for k, v in TRIGRAMS.items()}
    l, u = name[lo], name[up]
    n = _KW[_ORDER.index(l)][_ORDER.index(u)]
    t, j = HEX[n - 1].split("|")
    return {"number": n, "name": t, "judgement": j, "lower": {"trigram": l, "image": TRIGRAMS[l][1]}, "upper": {"trigram": u, "image": TRIGRAMS[u][1]},
            "lines": "".join(map(str, lines))}

def iching_cast(question: str | None = None, seed: str | None = None):
    rng = random.Random(int(hashlib.sha256((seed or question or str(random.random())).encode()).hexdigest(), 16)) if (seed or question) else random.Random()
    vals = [sum(rng.choice((2, 3)) for _ in range(3)) for _ in range(6)]  # three-coin method: 6,7,8,9
    primary = [1 if v in (7, 9) else 0 for v in vals]
    changing = [i + 1 for i, v in enumerate(vals) if v in (6, 9)]
    relating = [(1 - b) if v in (6, 9) else b for b, v in zip(primary, vals)]
    out = {"question": question, "coin_values": vals, "primary": hexagram_of(primary), "changing_lines": changing}
    if changing: out["relating"] = hexagram_of(relating)
    return out

def iching_all():
    return [{"number": i + 1, "name": h.split("|")[0], "judgement": h.split("|")[1]} for i, h in enumerate(HEX)]

# ---------------- Vastu ----------------
VASTU = {
 "North": {"deity": "Kubera", "element": "Water", "planet": "Mercury", "good_for": ["living room", "cash locker/treasury", "entrance", "water storage underground"], "avoid": ["toilet", "heavy storage", "staircase"]},
 "North-East": {"deity": "Ishana (Shiva)", "element": "Water", "planet": "Jupiter", "good_for": ["puja room", "meditation", "open space", "underground water tank", "main entrance"], "avoid": ["toilet", "kitchen", "heavy structures", "septic tank"]},
 "East": {"deity": "Indra / Surya", "element": "Air", "planet": "Sun", "good_for": ["entrance", "living room", "bathing area", "windows for morning light"], "avoid": ["toilet", "high walls", "clutter"]},
 "South-East": {"deity": "Agni", "element": "Fire", "planet": "Venus", "good_for": ["kitchen", "electrical equipment", "generator"], "avoid": ["bedroom", "water tank", "puja room"]},
 "South": {"deity": "Yama", "element": "Earth", "planet": "Mars", "good_for": ["bedroom", "storage", "heavy furniture", "staircase"], "avoid": ["main entrance (unless in the auspicious pada)", "underground water"]},
 "South-West": {"deity": "Nairitya (Pitru)", "element": "Earth", "planet": "Rahu", "good_for": ["master bedroom", "heavy storage", "locker of documents"], "avoid": ["entrance", "toilet", "kitchen", "pit or water tank"]},
 "West": {"deity": "Varuna", "element": "Water/Space", "planet": "Saturn", "good_for": ["dining room", "children's study", "overhead water tank", "staircase"], "avoid": ["kitchen fire facing west only"]},
 "North-West": {"deity": "Vayu", "element": "Air", "planet": "Moon", "good_for": ["guest room", "garage", "toilet", "store of finished goods"], "avoid": ["master bedroom for long stay", "puja room"]},
 "Centre": {"deity": "Brahma (Brahmasthana)", "element": "Space", "planet": "-", "good_for": ["open courtyard", "light & air"], "avoid": ["pillars", "toilet", "staircase", "heavy furniture"]},
}
ROOM_BEST = {"kitchen": ["South-East", "North-West"], "puja room": ["North-East", "East", "North"], "master bedroom": ["South-West", "South"],
             "bedroom": ["South", "West", "South-West", "North-West"], "toilet": ["North-West", "West", "South"], "living room": ["North", "East", "North-East"],
             "entrance": ["North-East", "East", "North"], "study": ["West", "East", "North-East"], "staircase": ["South", "West", "South-West"],
             "guest room": ["North-West"], "dining room": ["West", "East"], "water tank (overhead)": ["South-West", "West"],
             "underground water": ["North-East", "North", "East"], "garage": ["North-West", "South-East"], "septic tank": ["North-West", "West"]}

def vastu(layout: dict | None = None, facing: str | None = None):
    res = {"directions": VASTU, "room_guide": ROOM_BEST}
    if facing:
        f = facing.title().replace("Northeast", "North-East")
        res["facing"] = {"direction": f, "remark": {"East": "Excellent — morning sun; keep the north-east light.", "North": "Excellent — linked to wealth (Kubera).",
                         "North-East": "Most auspicious entrance direction.", "West": "Good for business & stability when the entrance pada is correct.",
                         "South": "Workable with correct pada and remedies (e.g. threshold metal strip).", "South-West": "Least preferred; needs remedies.",
                         "South-East": "Acceptable; keep kitchen alignment correct.", "North-West": "Good for trade and movement; avoid master bedroom here."}.get(f, "Check entrance pada.")}
    if layout:
        rows, score, n = [], 0, 0
        for room, d in layout.items():
            best = ROOM_BEST.get(room.lower()); d2 = d.title()
            if not best: continue
            ok = d2 in best; good2 = d2 not in sum([[k for k, v in VASTU.items() if room.lower() in " ".join(v["avoid"])]], [])
            pts = 10 if ok else 5 if good2 else 0
            score += pts; n += 1
            rows.append({"room": room, "direction": d2, "ideal": best, "points": pts,
                         "advice": "Ideal placement." if ok else ("Acceptable; " if pts else "Avoid; ") + f"preferred: {', '.join(best)}."})
        res["evaluation"] = rows; res["score_percent"] = round(100 * score / (10 * n)) if n else None
    return res

# ---------------- Palmistry ----------------
PALM = {
 "hand_shapes": {"Earth": "square palm, short fingers — practical, reliable, hands-on.", "Air": "square palm, long fingers — intellectual, communicative, curious.",
                 "Fire": "long palm, short fingers — energetic, impulsive, enthusiastic.", "Water": "long palm, long fingers — sensitive, intuitive, artistic."},
 "lines": {"Life line": "Curves around the thumb; describes vitality and major life changes, not length of life.",
           "Head line": "Across the middle; style of thinking. Straight = practical, sloping = imaginative, long = thorough.",
           "Heart line": "Below the fingers; emotional style. Ending under Jupiter = idealistic; under Saturn = reserved; straight = calm.",
           "Fate line": "Up the centre toward Saturn; career direction and sense of purpose. Breaks indicate career changes.",
           "Sun (Apollo) line": "Toward the ring finger; creativity, recognition and satisfaction.",
           "Mercury (health) line": "Toward the little finger; communication skill and attention to health.",
           "Marriage (relationship) lines": "Short horizontal lines on the edge below the little finger; significant attachments.",
           "Girdle of Venus": "Semicircle above the heart line; heightened sensitivity."},
 "mounts": {"Jupiter": "below index finger — ambition, leadership.", "Saturn": "below middle finger — responsibility, wisdom.",
            "Apollo (Sun)": "below ring finger — creativity, fame.", "Mercury": "below little finger — commerce, wit.",
            "Venus": "base of thumb — love, vitality.", "Moon (Luna)": "opposite thumb, lower edge — imagination, intuition.",
            "Mars (upper/lower)": "courage and resilience.", "Rahu/Ketu (Vedic)": "centre and base of palm — karmic tests and spirituality."},
 "fingers": {"long index": "confidence, leadership", "long ring": "risk-taking, creativity", "flexible thumb": "adaptable, generous",
             "stiff thumb": "determined, stubborn", "long little finger": "eloquent, persuasive"},
}
def palmistry(hand_shape=None, heart=None, head=None, life=None, fate=None):
    out = {"reference": PALM}
    r = []
    if hand_shape: r.append(PALM["hand_shapes"].get(hand_shape.title(), "Unknown hand shape"))
    if heart: r.append({"curved": "Heart line curved: warm, expressive in love.", "straight": "Heart line straight: steady, reserved emotions.",
                        "long": "Long heart line: idealistic and devoted.", "short": "Short heart line: practical about relationships."}.get(heart, ""))
    if head: r.append({"straight": "Straight head line: logical, practical thinker.", "sloping": "Sloping head line: imaginative and creative.",
                       "long": "Long head line: thorough, focused thinker.", "short": "Short head line: quick, decisive mind."}.get(head, ""))
    if life: r.append({"deep": "Deep life line: robust vitality.", "faint": "Faint life line: conserve energy; build routines.",
                       "wide curve": "Wide curve: enthusiasm and stamina.", "close to thumb": "Close to thumb: cautious with energy."}.get(life, ""))
    if fate: r.append({"present": "Clear fate line: a strong sense of direction.", "absent": "No fate line: a self-made, flexible path.",
                       "broken": "Broken fate line: notable career changes."}.get(fate, ""))
    if r: out["reading"] = [x for x in r if x]
    out["note"] = "Palmistry needs a photo/inspection of the hand; this endpoint returns reference meanings and a reading from features you describe."
    return out

# ---------------- Kabbalah ----------------
SEPHIROT = ["Keter (Crown) — unity, divine will", "Chokmah (Wisdom) — inspiration, the first spark", "Binah (Understanding) — form, structure",
            "Chesed (Mercy) — generosity, expansion", "Gevurah (Strength) — discipline, judgement", "Tiferet (Beauty) — harmony, heart",
            "Netzach (Victory) — endurance, emotion, art", "Hod (Splendour) — intellect, communication", "Yesod (Foundation) — imagination, the subconscious",
            "Malkuth (Kingdom) — the physical world, manifestation"]
def kabbalah(name: str, birth: Date | None = None):
    letters = [c for c in name.upper() if c.isalpha()]
    ordinal = sum(ord(c) - 64 for c in letters)
    def red(n):
        while n > 22: n = sum(map(int, str(n)))
        return n
    path = red(ordinal)
    seph = (ordinal - 1) % 10
    out = {"name": name, "ordinal_value": ordinal, "path_number": path, "sephirah": SEPHIROT[seph],
           "note": "English-letter gematria (A=1..Z=26); path number reduced to the 22 paths of the Tree of Life."}
    if birth:
        b = sum(map(int, birth.strftime("%Y%m%d")))
        out["birth_sephirah"] = SEPHIROT[(b - 1) % 10]
    return out

# ---------------- Mayan ----------------
DAY_SIGNS = ["Imix", "Ik'", "Ak'b'al", "K'an", "Chikchan", "Kimi", "Manik'", "Lamat", "Muluk", "Ok", "Chuwen", "Eb'", "B'en", "Ix", "Men", "K'ib'", "Kab'an", "Etz'nab'", "Kawak", "Ajaw"]
DAY_MEAN = ["crocodile — beginnings", "wind — breath, communication", "night — dreams, inner world", "seed — growth, abundance", "serpent — life force",
            "death — transformation", "deer — healing, hand", "star — harmony, art", "water — emotion, purification", "dog — loyalty, love",
            "monkey — play, creativity", "road — path, community", "reed — authority, home", "jaguar — magic, earth", "eagle — vision",
            "owl — wisdom, ancestors", "earth — movement, synchronicity", "flint — truth, clarity", "storm — renewal", "sun — enlightenment, wholeness"]
HAAB = ["Pop", "Wo'", "Sip", "Sotz'", "Sek", "Xul", "Yaxk'in", "Mol", "Ch'en", "Yax", "Sak'", "Keh", "Mak", "K'ank'in", "Muwan", "Pax", "K'ayab", "Kumk'u", "Wayeb'"]
def mayan(d: Date):
    jdn = d.toordinal() + 1721425  # proleptic Gregorian ordinal -> JDN
    days = jdn - 584283  # GMT correlation
    tone = (days + 3) % 13 + 1; sign = (days + 19) % 20
    hd = (days + 348) % 365; hm, hday = divmod(hd, 20)
    b, r = divmod(days, 144000); k, r = divmod(r, 7200); t, r = divmod(r, 360); w, kin = divmod(r, 20)
    return {"date": d.isoformat(), "long_count": f"{b}.{k}.{t}.{w}.{kin}", "tzolkin": f"{tone} {DAY_SIGNS[sign]}", "tone": tone,
            "day_sign": DAY_SIGNS[sign], "meaning": DAY_MEAN[sign], "haab": f"{hday} {HAAB[hm]}", "correlation": "GMT 584283"}

# ---------------- Dreams ----------------
DREAMS = {"snake": "transformation, hidden fears or healing energy (in Indian tradition often linked to Rahu/Ketu and kundalini)",
 "water": "emotions; clear water = peace, muddy water = confusion", "flying": "freedom, ambition, rising above a problem",
 "falling": "loss of control or insecurity; a call to ground yourself", "teeth": "anxiety about appearance, ageing or communication",
 "death": "an ending and new beginning, rarely literal", "fire": "passion, purification or anger", "house": "the self; rooms are aspects of your life",
 "exam": "feeling tested or unprepared", "baby": "a new project or a vulnerable part of you", "money": "self-worth and energy exchange",
 "temple": "spiritual seeking; blessings ahead", "cow": "abundance, nourishment and auspiciousness", "elephant": "strength, wisdom, Ganesha's blessing",
 "dog": "loyalty and friendship", "cat": "independence, intuition", "chase": "avoiding an issue that needs facing", "wedding": "union, commitment or integration",
 "rain": "cleansing and renewal", "mountain": "a goal or obstacle; climbing = progress", "car": "direction and control of your life",
 "lost": "uncertainty about direction", "ocean": "the unconscious, vast emotions", "tree": "growth, family, stability", "gold": "value, success, Jupiter's grace",
 "moon": "mind and intuition", "sun": "vitality and recognition", "blood": "life force, or depletion", "naked": "vulnerability, fear of exposure",
 "ghost": "unresolved memories", "bridge": "transition between life phases", "door": "new opportunities", "storm": "emotional turmoil before clarity",
 "fish": "abundance, spiritual nourishment", "bird": "messages, freedom", "spider": "creativity and patience, or feeling trapped",
 "flower": "beauty, love and unfolding", "school": "lessons you are currently learning", "train": "a set life path", "mirror": "self-reflection"}
def dream(symbol: str | None = None):
    if symbol:
        s = symbol.lower().strip()
        hits = {k: v for k, v in DREAMS.items() if k in s or s in k}
        return {"symbol": symbol, "meanings": hits or {"note": "Symbol not in dictionary; consider what it means to you personally."}}
    return {"symbols": DREAMS}

# ---------------- Crystals ----------------
CRYSTAL_SIGN = {"Aries": ["Carnelian", "Red Jasper", "Diamond"], "Taurus": ["Rose Quartz", "Emerald", "Malachite"], "Gemini": ["Citrine", "Agate", "Tiger's Eye"],
                "Cancer": ["Moonstone", "Pearl", "Selenite"], "Leo": ["Sunstone", "Ruby", "Pyrite"], "Virgo": ["Amazonite", "Peridot", "Moss Agate"],
                "Libra": ["Lapis Lazuli", "Opal", "Lepidolite"], "Scorpio": ["Obsidian", "Garnet", "Labradorite"], "Sagittarius": ["Turquoise", "Amethyst", "Sodalite"],
                "Capricorn": ["Garnet", "Smoky Quartz", "Onyx"], "Aquarius": ["Amethyst", "Aquamarine", "Fluorite"], "Pisces": ["Aquamarine", "Amethyst", "Bloodstone"]}
CRYSTAL_PLANET = {"Sun": "Ruby / Sunstone", "Moon": "Pearl / Moonstone", "Mars": "Red Coral / Carnelian", "Mercury": "Emerald / Green Aventurine",
                  "Jupiter": "Yellow Sapphire / Citrine", "Venus": "Diamond / Clear Quartz / White Sapphire", "Saturn": "Blue Sapphire / Amethyst",
                  "Rahu": "Hessonite (Gomed)", "Ketu": "Cat's Eye (Lehsunia)"}
CHAKRA = {"Root": ["Red Jasper", "Smoky Quartz", "Hematite"], "Sacral": ["Carnelian", "Orange Calcite"], "Solar Plexus": ["Citrine", "Tiger's Eye"],
          "Heart": ["Rose Quartz", "Green Aventurine"], "Throat": ["Blue Lace Agate", "Aquamarine"], "Third Eye": ["Amethyst", "Lapis Lazuli"], "Crown": ["Clear Quartz", "Selenite"]}
def crystals(sign=None, planet=None, chakra=None):
    if sign: return {"sign": sign, "crystals": CRYSTAL_SIGN.get(sign.title(), [])}
    if planet: return {"planet": planet, "crystal": CRYSTAL_PLANET.get(planet.title())}
    if chakra: return {"chakra": chakra, "crystals": CHAKRA.get(chakra.title(), [])}
    return {"by_sign": CRYSTAL_SIGN, "by_planet": CRYSTAL_PLANET, "by_chakra": CHAKRA,
            "note": "Vedic gemstones should be checked against the full chart before wearing."}

# ---------------- Chinese yearly forecast ----------------
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
ELEMENTS = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
TRINES = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3, 7, 11}]
SIX_HARMONY = {frozenset(x) for x in [(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]}
HARMS = {frozenset(x) for x in [(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)]}
AREA_TXT = {"great": ("an excellent year for new ventures, promotions and partnerships", "romance blossoms easily", "money flows with good planning"),
            "good": ("a supportive year; allies help your plans", "warm relationships", "steady gains"),
            "mixed": ("progress with some delays; stay flexible", "communicate clearly to avoid misunderstanding", "budget carefully"),
            "challenging": ("a testing year — avoid big risks and stay patient", "be gentle with loved ones", "save rather than speculate")}
def chinese_forecast(birth_year: int, year: int):
    a, y = (birth_year - 4) % 12, (year - 4) % 12
    el_y = ELEMENTS[(year - 4) % 10]
    if a == y: rel, tone = "Ben Ming Nian (own year) — wear red and stay cautious", "challenging"
    elif (a - y) % 12 == 6: rel, tone = "Clash (Tai Sui opposition)", "challenging"
    elif frozenset((a, y)) in HARMS: rel, tone = "Harm", "mixed"
    elif frozenset((a, y)) in SIX_HARMONY: rel, tone = "Six Harmony (secret friend)", "great"
    elif any(a in t and y in t for t in TRINES): rel, tone = "Trine (Three Harmony)", "good"
    else: rel, tone = "Neutral", "mixed" if (a - y) % 3 else "good"
    c, l, m = AREA_TXT[tone]
    return {"birth_year": birth_year, "animal": ANIMALS[a], "year": year, "year_animal": f"{el_y} {ANIMALS[y]}", "relationship": rel,
            "overall": tone, "career": c, "love": l, "money": m,
            "health": "Moderate exercise and regular rest; " + ("watch stress." if tone == "challenging" else "energy is good."),
            "lucky": {"colors": {"Wood": ["green"], "Fire": ["red", "purple"], "Earth": ["yellow", "brown"], "Metal": ["white", "gold"], "Water": ["black", "blue"]}[ELEMENTS[(birth_year - 4) % 10]],
                      "numbers": [(a % 9) + 1, ((a + 4) % 9) + 1]}}

# ---------------- Puja & dosha remedies ----------------
PUJA = {"Sun": "Surya puja / Aditya Hridayam on Sundays; offer water (arghya) at sunrise.", "Moon": "Shiva abhishek with milk on Mondays; Chandra mantra.",
        "Mars": "Hanuman puja on Tuesdays; Mangal shanti; read Hanuman Chalisa.", "Mercury": "Ganesha / Vishnu puja on Wednesdays; donate green moong.",
        "Jupiter": "Guru / Vishnu puja on Thursdays; respect teachers; donate turmeric/chana dal.", "Venus": "Lakshmi puja on Fridays; Shukra mantra; donate white sweets.",
        "Saturn": "Shani puja on Saturdays; light sesame-oil lamp; serve the needy.", "Rahu": "Durga / Rahu shanti; recite Durga Saptashati.", "Ketu": "Ganesha puja; Ketu shanti; feed dogs."}
DOSHA_REMEDY = {
 "manglik": ["Kumbh Vivah / Vishnu Vivah before marriage (traditional)", "Mangal shanti puja", "Hanuman Chalisa on Tuesdays", "Marry a partner with matching Manglik status"],
 "kaal_sarp": ["Kaal Sarp dosha nivaran puja (e.g. at Trimbakeshwar)", "Om Namah Shivaya japa", "Nag Panchami worship", "Rahu-Ketu mantras"],
 "sade_sati": ["Shani mantra 'Om Sham Shanaishcharaya Namah'", "Hanuman worship on Saturdays", "Donate black sesame / mustard oil", "Serve elders and labourers"],
 "pitra": ["Pitru tarpan & shraddha during Pitru Paksha", "Narayan Bali / Tripindi shraddha", "Feed Brahmins, crows and cows on Amavasya"],
 "guru_chandal": ["Guru mantra on Thursdays", "Respect teachers", "Donate yellow items"], "grahan": ["Surya/Chandra mantra during eclipses", "Mahamrityunjaya japa"],
 "angarak": ["Mangal-Rahu shanti", "Hanuman puja", "Avoid rash driving and anger"], "shrapit": ["Shani-Rahu shanti puja", "Mahamrityunjaya japa"],
 "vish": ["Shiva abhishek on Mondays", "Shani mantra"], "kemadruma": ["Wear pearl after consultation", "Chandra mantra", "Worship Goddess Lakshmi"],
}
def remedies_for(k: dict):
    pl = {p["name"]: p for p in k["planets"]}
    weak = [p for p, v in k["shadbala"]["planets"].items() if not v["strong"]] if "planets" in k.get("shadbala", {}) else []
    deb = [p for p, v in pl.items() if v.get("dignity") in ("debilitated", "enemy") and p in PUJA]
    targets = list(dict.fromkeys(weak + deb))
    d = k.get("doshas", {}); od = k.get("other_doshas", {})
    present = []
    if d.get("manglik", {}).get("is_manglik"): present.append("manglik")
    if d.get("kaal_sarp", {}).get("present"): present.append("kaal_sarp")
    for key, v in od.items():
        on = any(v.values()) if isinstance(v, dict) else bool(v)
        if on: present.append(key)
    cur = d.get("sade_sati", {})
    if isinstance(cur, dict) and (cur.get("current") or cur.get("active")): present.append("sade_sati")
    return {"puja_for_weak_planets": {p: PUJA[p] for p in targets}, "dosha_remedies": {x: DOSHA_REMEDY[x] for x in present if x in DOSHA_REMEDY},
            "general": ["Daily Gayatri / Mahamrityunjaya mantra", "Charity on the weekday of the weakest planet", "Keep a regular routine aligned with sunrise"],
            "note": "Traditional suggestions only; consult a qualified practitioner before gemstones or elaborate rituals."}

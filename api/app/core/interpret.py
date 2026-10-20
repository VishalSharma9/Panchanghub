"""Original template-based interpretation text (written for PanchangHub; not taken from any published source).

Readings are assembled from: planet nature + sign colouring + dignity, planet-in-house statements (9x12),
nakshatra portraits (27), yoga & dosha explanations, dasha period themes (9 mahadashas + antardasha blend),
and Western aspect templates. Text is descriptive/traditional and for guidance only.
"""
from __future__ import annotations
from .ephem import SIGNS, NAKSHATRAS

PLANET = {
 "Sun": "The Sun stands for the soul, vitality, father, authority and the urge to be recognised. Where it sits you seek to lead, to shine and to be respected for who you are.",
 "Moon": "The Moon describes the mind, emotions, mother, comfort and daily rhythms. It shows what makes you feel safe and how you absorb and reflect the moods around you.",
 "Mars": "Mars is energy, courage, drive, siblings, land and the capacity to fight for what you want. It shows where you act decisively and where impatience or conflict may arise.",
 "Mercury": "Mercury governs intellect, speech, learning, trade, writing and adaptability. It shows how you think, communicate, calculate and connect ideas.",
 "Jupiter": "Jupiter is wisdom, faith, teachers, children, wealth and moral sense. It expands whatever it touches and shows where grace, guidance and growth arrive.",
 "Venus": "Venus rules love, beauty, art, pleasure, vehicles, luxury and partnership. It shows what you find attractive and how you give and receive affection.",
 "Saturn": "Saturn is time, discipline, labour, endurance, longevity and karma. It slows matters down so they can be built to last, and rewards patience and honest effort.",
 "Rahu": "Rahu, the north node, is ambition, obsession, foreign things, innovation and worldly hunger. It magnifies desire in its area and pushes you toward unfamiliar experience.",
 "Ketu": "Ketu, the south node, is detachment, past skills, intuition, spirituality and liberation. It gives instinctive mastery but also a sense of dissatisfaction that turns you inward.",
}
SIGN = {
 "Aries": "Aries colours it with initiative, speed and directness; results come through bold first steps, though patience must be learned.",
 "Taurus": "Taurus makes it steady, sensual and value-conscious; it builds slowly, enjoys comfort and resists being hurried.",
 "Gemini": "Gemini lends curiosity, wit and versatility; it works through conversation, information and many parallel interests.",
 "Cancer": "Cancer makes it protective, emotional and home-centred; it nurtures and remembers, but can become defensive when insecure.",
 "Leo": "Leo adds warmth, pride and a flair for display; it wants to create, to lead and to be appreciated generously.",
 "Virgo": "Virgo makes it precise, analytical and service-minded; it refines, organises and improves, sometimes at the cost of worry.",
 "Libra": "Libra brings diplomacy, aesthetics and a need for balance; it works best in partnership and through fair negotiation.",
 "Scorpio": "Scorpio intensifies it with depth, secrecy and transformative power; it probes beneath the surface and does nothing by halves.",
 "Sagittarius": "Sagittarius widens it with optimism, principle and a love of learning and travel; it seeks meaning and the big picture.",
 "Capricorn": "Capricorn makes it ambitious, practical and status-aware; it climbs methodically and values results over promises.",
 "Aquarius": "Aquarius makes it independent, humanitarian and unconventional; it thinks in systems and networks and resists conformity.",
 "Pisces": "Pisces makes it compassionate, imaginative and receptive; it works through intuition, devotion and surrender rather than force.",
}
DIGNITY = {
 "exalted": "Being exalted, it is at its most capable here and tends to deliver its significations generously.",
 "debilitated": "Being debilitated, its natural expression is strained; growth comes by consciously working with its lessons (check for neecha-bhanga cancellation).",
 "moolatrikona": "In its moolatrikona it acts with clarity of purpose and dependable strength.",
 "own": "In its own sign it is comfortable and self-reliant, protecting the matters it rules.",
 "friendly": "In a friend's sign it is supported and generally cooperative.",
 "enemy": "In an enemy's sign it meets friction and must work harder to give its results.",
 "neutral": "In a neutral sign its results depend largely on aspects and house placement.",
}
HOUSE = ["self, body, temperament and overall direction of life", "wealth, family, speech, food and early education",
         "courage, siblings, short journeys, skills and communication", "home, mother, emotional security, property and vehicles",
         "intelligence, children, romance, creativity and past merit", "health, service, debts, competition and daily work",
         "marriage, partners, contracts and public dealings", "longevity, secrets, sudden change, inheritance and research",
         "dharma, fortune, father, teachers and long journeys", "career, status, authority and public reputation",
         "gains, income, friends, networks and fulfilment of desires", "expenses, loss, foreign lands, sleep and liberation"]
PH = {
 "Sun": ["a strong sense of self, leadership and good vitality, with pride to manage", "income tied to authority or government; speech can be commanding",
         "courage and initiative; competitive with siblings, successful in self-driven efforts", "pride in home and lineage, but domestic peace needs humility",
         "a sharp, creative intellect, love of drama and leadership in education", "victory over rivals, strong immunity and success in service roles",
         "a dominant partner or ego clashes in marriage; success in public roles", "interest in hidden matters, sensitivity of health and inheritance issues",
         "devotion to principle, respect for father and teachers, good fortune", "excellent for career and status; recognition from authority",
         "steady gains through influential friends and ambitions fulfilled", "expenditure on prestige, foreign connections, a need for solitude"],
 "Moon": ["an emotional, receptive and popular personality", "wealth that fluctuates, a sweet voice and attachment to family",
          "a restless, imaginative mind that loves short travel and writing", "deep comfort at home and strong attachment to mother",
          "an emotional, creative mind and affection for children", "worry and sensitivity in health; caring service to others",
          "an emotional partnership and dealings with the public", "emotional upheavals, intuition and interest in the occult",
          "faith, pilgrimage and a fortunate, devotional mind", "a public career, fame that rises and falls with the public mood",
          "many friends, gains through women or the public", "a vivid dream life, expenses on comfort and possible life abroad"],
 "Mars": ["boldness, physical energy and a quick temper", "harsh speech at times and money made through effort or property",
          "great courage, initiative and success through personal effort", "property gains but friction at home; check Manglik dosha",
          "an intense, competitive intellect; passion in romance", "victory over enemies; excellent for competition, medicine or law",
          "passionate but argumentative partnerships; a classic Manglik placement", "accident-proneness and sudden events; research and surgery suit it",
          "strong convictions and adventurous travel; arguments with elders", "drive, technical or command roles and rapid career rise",
          "gains through effort, land or brothers; ambitious friends", "hidden anger, expenses and foreign work; protect sleep and energy"],
 "Mercury": ["wit, youthfulness and a talkative, adaptable nature", "skill with money, speech and trade; a good teacher or accountant",
             "excellent communication, writing and media skills", "a learned home, interest in property or education business",
             "a sharp analytical intellect; good for exams and games of skill", "skill in solving problems; work in analysis, health or services",
             "a youthful, communicative partner and success in business deals", "research ability, interest in mysteries and insurance or tax work",
             "philosophical learning, publishing and higher studies", "a career in business, communication, IT or consultancy",
             "gains through networks, commerce and clever ideas", "an inward, imaginative mind; work with foreign clients or retreat"],
 "Jupiter": ["wisdom, optimism and protection; a respected, generous nature", "wealth, a truthful voice and a cultured family",
             "a philosophical approach to effort; supportive siblings", "a happy home, good education and blessed property",
             "intelligence, devotion and blessings through children", "victory through ethics; work in law, healing or advisory roles",
             "a wise, dignified partner and fortunate partnerships", "longevity, inheritance and interest in spiritual research",
             "strong fortune, faith and grace from teachers and father", "an honourable career in teaching, law, finance or counsel",
             "abundant gains and influential friends", "charity, spiritual expenses and liberation-oriented outlook"],
 "Venus": ["charm, beauty and an artistic, pleasure-loving nature", "wealth through arts or luxury and a pleasant voice",
           "artistic talent in writing, music or design; pleasant siblings", "a beautiful home, vehicles and comforts",
           "romance, creativity and talented children", "challenges in love or health of the reproductive system; service in arts",
           "an attractive partner and success in partnership businesses", "gains through spouse or inheritance; intense attachments",
           "fortune through women, arts and travel; refined values", "a career in arts, beauty, hospitality or finance",
           "gains through social life, arts and women; many friends", "luxurious expenses, pleasure abroad and devotion"],
 "Saturn": ["a serious, responsible nature that matures with age", "slow but lasting wealth; careful or reserved speech",
            "persistence and courage that grows with time", "responsibilities at home and delayed property gains",
            "a serious intellect and delays or responsibility around children", "strong endurance; defeats enemies through persistence",
            "delayed marriage or an older, mature partner; lasting commitments", "longevity with chronic matters to manage; deep research",
            "unorthodox beliefs and a disciplined approach to dharma", "a steady rise through hard work, often later in life",
            "gains that grow steadily; older or influential friends", "expenses, isolation or work abroad; good for meditation"],
 "Rahu": ["an unconventional image and a strong drive for recognition", "unusual sources of income and a persuasive tongue",
          "great courage, media and technology skills", "restlessness at home or a foreign residence",
          "unconventional thinking and speculative interests", "victory over rivals and success in competitive fields",
          "an unconventional or foreign partner; obsession in relationships", "sudden events, occult interest and hidden gains",
          "unorthodox beliefs and foreign travel", "ambition, fame and success in modern or foreign fields",
          "large gains and influential networks", "foreign settlement, high expenses and disturbed sleep"],
 "Ketu": ["a spiritual, detached personality with inner intensity", "detachment from family wealth; blunt speech",
          "courage and intuitive skill; occasional distance from siblings", "emotional detachment from home; inner search",
          "intuitive intelligence and interest in mantra or mystic study", "victory over enemies and healing ability",
          "detachment or karmic lessons in partnership", "deep occult and research talent; sudden spiritual turns",
          "inner philosophy that rejects dogma", "unusual or behind-the-scenes career; changes of direction",
          "gains through unusual means; few but deep friendships", "a strong pull toward moksha, retreat and spirituality"],
}
NAK = [
 "Ashwini (Ketu) gives speed, healing ability and a pioneering spirit; natives like to start things and help quickly.",
 "Bharani (Venus) is about creation, restraint and responsibility; natives carry strong desires and the capacity to bear burdens.",
 "Krittika (Sun) is sharp and purifying; natives are direct, principled and able to cut through confusion.",
 "Rohini (Moon) is fertile and attractive; natives love beauty, comfort and growth, and can be possessive.",
 "Mrigashira (Mars) is the seeker; natives are curious, gentle, restless and always looking for something more.",
 "Ardra (Rahu) brings storms that clear the air; natives are intense, analytical and transformed through hardship.",
 "Punarvasu (Jupiter) is the return of light; natives are optimistic, forgiving and able to start again after setbacks.",
 "Pushya (Saturn) nourishes; natives are caring, dutiful and protective, making it one of the most auspicious stars.",
 "Ashlesha (Mercury) coils and binds; natives are perceptive, strategic and persuasive, with deep emotional memory.",
 "Magha (Ketu) connects with ancestors; natives respect tradition, seek status and carry natural dignity.",
 "Purva Phalguni (Venus) is rest and enjoyment; natives are affectionate, creative and fond of celebration.",
 "Uttara Phalguni (Sun) is patronage; natives are generous, reliable and value commitment and contracts.",
 "Hasta (Moon) is the skilful hand; natives are clever, crafty, humorous and good with detail.",
 "Chitra (Mars) is the brilliant jewel; natives are creative, design-minded and charismatic.",
 "Swati (Rahu) is the independent wind; natives are flexible, diplomatic and business-minded.",
 "Vishakha (Jupiter) is focused ambition; natives are determined, goal-oriented and sometimes torn between two paths.",
 "Anuradha (Saturn) is devoted friendship; natives are loyal, organised and succeed far from home.",
 "Jyeshtha (Mercury) is seniority; natives are protective, resourceful and carry responsibility early.",
 "Mula (Ketu) goes to the root; natives investigate deeply, may face upheaval and seek fundamental truth.",
 "Purva Ashadha (Venus) is invincibility; natives are persuasive, proud and refuse to give up.",
 "Uttara Ashadha (Sun) is final victory; natives are ethical, steady and achieve lasting success.",
 "Shravana (Moon) is listening; natives learn by hearing, connect people and value knowledge and tradition.",
 "Dhanishta (Mars) is rhythm and wealth; natives are musical, generous and socially active.",
 "Shatabhisha (Rahu) is the hundred healers; natives are secretive, scientific, independent and healing-oriented.",
 "Purva Bhadrapada (Jupiter) is fiery transformation; natives are idealistic, intense and capable of sacrifice.",
 "Uttara Bhadrapada (Saturn) is depth and calm; natives are wise, restrained and spiritually mature.",
 "Revati (Mercury) is the nourisher of journeys; natives are kind, gentle, artistic and protective of the weak.",
]
YOGA = {
 "Gajakesari Yoga": "Jupiter in a kendra from the Moon: respect, sound judgement, protection in crisis and lasting reputation.",
 "Budhaditya Yoga": "Sun and Mercury together: intelligence, articulate speech and success in study, administration and business.",
 "Ruchaka Yoga": "Mars strong in a kendra: courage, leadership, athletic ability and command over others.",
 "Bhadra Yoga": "Mercury strong in a kendra: eloquence, learning, wit and commercial skill.",
 "Hamsa Yoga": "Jupiter strong in a kendra: righteousness, wisdom, refined tastes and spiritual merit.",
 "Malavya Yoga": "Venus strong in a kendra: beauty, luxuries, vehicles, artistic gifts and a happy married life.",
 "Shasha Yoga": "Saturn strong in a kendra: authority over masses, discipline, endurance and organisational power.",
 "Raja Yoga": "Association of kendra and trikona lords: rise in status, authority and recognition, especially in their dashas.",
 "Dhana Yoga": "Connection between wealth houses (2, 5, 9, 11) and their lords: accumulation of money and assets.",
 "Vipareeta Raja Yoga": "Lords of dusthanas (6, 8, 12) in dusthanas: success that emerges unexpectedly from adversity.",
 "Neecha Bhanga Raja Yoga": "Cancellation of debility: an early struggle turns into strength and notable achievement.",
 "Kemadruma Yoga": "No planets on either side of the Moon: periods of loneliness or financial ups and downs; strengthened Moon and kendras cancel it.",
 "Chandra Mangala Yoga": "Moon with Mars: enterprise and earning power, with emotional intensity to manage.",
 "Adhi Yoga": "Benefics in 6th, 7th and 8th from the Moon: leadership, comfort and victory over opponents.",
 "Sunapha Yoga": "Planets in the 2nd from the Moon: self-earned wealth and a good reputation.",
 "Anapha Yoga": "Planets in the 12th from the Moon: good health, charm and a contented mind.",
 "Durudhara Yoga": "Planets on both sides of the Moon: wealth, vehicles and generosity.",
 "Amala Yoga": "A benefic in the 10th: a spotless reputation and ethical career.",
 "Saraswati Yoga": "Jupiter, Venus and Mercury well placed: learning, eloquence and artistic talent.",
 "Lakshmi Yoga": "Strong 9th lord and Venus: prosperity, grace and good fortune.",
 "Parvata Yoga": "Benefics in kendras with empty 7th/8th: fame, charity and leadership.",
 "Kahala Yoga": "Strong 4th and 9th lords: boldness, a stubborn will and command.",
 "Chamara Yoga": "Exalted lagna lord in a kendra aspected by Jupiter: honour, eloquence and long life.",
 "Shubha Kartari Yoga": "Benefics flank the lagna: protection, health and good conduct.",
 "Papa Kartari Yoga": "Malefics flank the lagna: pressure and obstacles that build resilience.",
 "Veshi Yoga": "A planet other than the Moon in the 2nd from the Sun: balanced outlook and good speech.",
 "Vasi Yoga": "A planet other than the Moon in the 12th from the Sun: generosity and capability.",
 "Ubhayachari Yoga": "Planets on both sides of the Sun: king-like status and all-round competence.",
 "Shakata Yoga": "Moon in 6/8/12 from Jupiter: fortune that rises and falls like a cart wheel.",
 "Guru Mangala Yoga": "Jupiter with Mars: righteous courage and success in technical or legal fields.",
 "Vasumati Yoga": "Benefics in upachayas from lagna or Moon: steadily increasing wealth.",
 "Pushkala Yoga": "Lagna lord with the Moon's dispositor in a kendra: wealth, fame and sweet speech.",
 "Sankha Yoga": "Lords of 5th and 6th in mutual kendras: humanitarian nature, long life and prosperity.",
 "Kalanidhi Yoga": "Jupiter in 2nd or 5th with Mercury/Venus: wealth, honour and artistic learning.",
}
DOSHA = {
 "manglik": "Mangal (Kuja) dosha arises when Mars occupies the 1st, 2nd, 4th, 7th, 8th or 12th house. It is said to bring heat and impatience into marriage; it is cancelled by many conditions (Mars in own/exaltation sign, matching dosha in the partner, Jupiter's aspect) and its effect softens after age 28.",
 "kaal_sarp": "Kaal Sarp yoga forms when all seven planets lie on one side of the Rahu-Ketu axis. It indicates a life of intense highs and lows, delays followed by sudden breakthroughs, and strong karmic themes in the houses of the axis.",
 "sade_sati": "Sade Sati is Saturn's 7½-year transit over the 12th, 1st and 2nd signs from the natal Moon. It is a period of restructuring, responsibility and maturity; difficult if Saturn is weak, but often brings lasting achievement through effort.",
 "guru_chandal": "Guru Chandal dosha (Jupiter with Rahu) can confuse beliefs and judgement or bring unorthodox teachers; it can also give original, boundary-breaking wisdom when Jupiter is strong.",
 "grahan": "Grahan (eclipse) dosha occurs when the Sun or Moon is conjunct Rahu or Ketu, eclipsing confidence (Sun) or peace of mind (Moon).",
 "pitra": "Pitra dosha indicates unresolved ancestral karma (Sun/9th house afflicted by Rahu, Ketu or Saturn); shraddha, tarpan and service to elders are traditional remedies.",
 "angarak": "Angarak dosha (Mars with Rahu) brings anger, impulsiveness and accident-proneness; channel the energy into disciplined physical work.",
 "shrapit": "Shrapit dosha (Saturn with Rahu) indicates delays and karmic burdens that lift through persistence, service and Saturn remedies.",
 "vish": "Vish dosha (Moon with Saturn) can bring melancholy and emotional heaviness; routine, meditation and Shiva worship help.",
 "kemadruma": "Kemadruma yoga leaves the Moon unsupported; it can bring loneliness or unstable finances, and is cancelled by planets in kendras from lagna or Moon.",
}
DASHA = {
 "Sun": "a period of self-assertion, authority, health focus and dealings with government or father; recognition comes when you take responsibility",
 "Moon": "an emotional, public-facing period about home, mother, travel and nourishment; results fluctuate with the Moon's strength",
 "Mars": "an energetic period of initiative, property, competition and courage; guard against haste, accidents and quarrels",
 "Mercury": "a period of learning, trade, communication and networking; good for study, writing and business",
 "Jupiter": "a period of growth, teachers, children, wisdom and wealth; usually expansive and protective",
 "Venus": "a long period of relationships, comforts, vehicles, art and pleasures; marriage and luxuries are emphasised",
 "Saturn": "a long period of hard work, structure and karmic accounting; slow but durable achievement and lessons in patience",
 "Rahu": "a period of ambition, foreign links, technology and unconventional opportunity; sudden rises and confusions",
 "Ketu": "a period of detachment, spiritual searching and sudden endings that clear space for something truer",
}
ASPECT = {"Conjunction": "fuses the energies of {a} and {b}; they act together, for better or worse",
          "Opposition": "sets {a} against {b}; awareness and balance through relationships are needed",
          "Trine": "lets {a} and {b} flow together easily, giving natural talent",
          "Square": "creates productive tension between {a} and {b}, driving action and growth",
          "Sextile": "offers opportunities to combine {a} and {b} with a little effort"}
WEST_PLANET_KEY = {"Sun": "identity", "Moon": "emotions", "Mercury": "thinking", "Venus": "love and values", "Mars": "drive",
                   "Jupiter": "growth", "Saturn": "discipline", "Uranus": "independence", "Neptune": "imagination", "Pluto": "transformation",
                   "Rahu": "destiny", "Ketu": "past habits", "North Node": "destiny"}

def planet_in_sign(p, sign, dignity=None):
    t = f"{p} in {sign}. {PLANET.get(p, '')} {SIGN.get(sign, '')}"
    if dignity and dignity in DIGNITY: t += " " + DIGNITY[dignity]
    return t

def planet_in_house(p, h):
    if p not in PH: return f"{p} in house {h} highlights {HOUSE[h - 1]}."
    return f"{p} in the {_ord(h)} house (the house of {HOUSE[h - 1]}) indicates {PH[p][h - 1]}."

def _ord(n): return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

def nakshatra(i): return NAK[i]

def dasha_text(maha, antar=None):
    t = f"{maha} mahadasha: {DASHA.get(maha, '')}."
    if antar and antar != maha:
        t += f" Within it, the {antar} antardasha adds {DASHA.get(antar, '').split(';')[0]}."
    return t

def kundli_reading(k: dict) -> dict:
    planets = []
    for pl in k["planets"]:
        if pl["name"] not in PLANET: continue
        planets.append({"planet": pl["name"], "sign": pl["sign"], "house": pl["house"],
                        "in_sign": planet_in_sign(pl["name"], pl["sign"], pl.get("dignity")),
                        "in_house": planet_in_house(pl["name"], pl["house"]),
                        "nakshatra": NAK[NAKSHATRAS.index(pl["nakshatra"])]})
    lag = k["lagna"]
    asc = {"sign": lag["sign"], "text": f"{lag['sign']} ascendant. " + SIGN[lag["sign"]].replace("colours it", "shapes your personality").replace("makes it", "makes you").replace("lends", "lends you").replace("adds", "adds").replace("brings", "brings you"),
           "nakshatra": NAK[NAKSHATRAS.index(lag["nakshatra"])]}
    moon = {"nakshatra": k["moon"]["nakshatra"], "text": NAK[NAKSHATRAS.index(k["moon"]["nakshatra"])]}
    def ytxt(y):
        n = y["name"]; base = n.split(" (")[0].replace("Chandra-Mangala", "Chandra Mangala")
        return YOGA.get(n) or YOGA.get(base) or next((v for kk, v in YOGA.items() if base.startswith(kk.replace(" Yoga", ""))), None) \
            or f"{n}: {y.get('description', '')}. This combination colours the houses and planets involved and matures in their dashas."
    yogas = [{"name": y["name"], "text": ytxt(y)} for y in k.get("yogas", [])]
    d = k.get("doshas", {}); od = k.get("other_doshas", {})
    doshas = []
    if d.get("manglik", {}).get("present") or d.get("manglik", {}).get("is_manglik"): doshas.append({"name": "Manglik", "text": DOSHA["manglik"]})
    if d.get("kaal_sarp", {}).get("present"): doshas.append({"name": d["kaal_sarp"].get("name", "Kaal Sarp"), "text": DOSHA["kaal_sarp"]})
    for key, v in od.items():
        on = v.get("present") if isinstance(v, dict) else bool(v)
        if on and key in DOSHA: doshas.append({"name": key.replace("_", " ").title(), "text": DOSHA[key]})
    doshas.append({"name": "Sade Sati (general)", "text": DOSHA["sade_sati"]})
    cd = k.get("current_dasha") or []
    lv = cd if isinstance(cd, list) else (cd.get("levels") or cd.get("current") or [])
    maha = lv[0]["lord"] if lv and isinstance(lv, list) and isinstance(lv[0], dict) and "lord" in lv[0] else None
    antar = lv[1]["lord"] if maha and len(lv) > 1 else None
    dashas = [{"lord": m["lord"], "start": m["start"], "end": m["end"], "text": dasha_text(m["lord"])} for m in k["vimshottari_dasha"]["mahadasha"]]
    return {"ascendant": asc, "moon": moon, "planets": planets, "yogas": yogas, "doshas": doshas,
            "current_dasha": dasha_text(maha, antar) if maha else None, "mahadashas": dashas,
            "disclaimer": "Template-based traditional interpretation for guidance and entertainment; not a substitute for professional advice."}

def western_reading(chart: dict) -> dict:
    out = {"planets": [], "aspects": []}
    for p in chart.get("planets", []):
        n = p["name"]
        if n in PLANET or n in WEST_PLANET_KEY:
            out["planets"].append({"planet": n, "sign": p["sign"], "house": p.get("house"),
                                   "text": f"{n} ({WEST_PLANET_KEY.get(n, '')}) in {p['sign']}: {SIGN.get(p['sign'], '')}" +
                                           (f" In the {_ord(p['house'])} house it focuses on {HOUSE[p['house'] - 1]}." if p.get("house") else "")})
    for a in chart.get("aspects", [])[:40]:
        tmpl = ASPECT.get(a.get("aspect") or a.get("type"))
        if not tmpl: continue
        p1, p2 = a.get("p1") or a.get("planet1"), a.get("p2") or a.get("planet2")
        out["aspects"].append({**{k: a[k] for k in a if k in ("p1", "p2", "planet1", "planet2", "aspect", "type", "orb")},
                               "text": f"{p1} {a.get('aspect') or a.get('type')} {p2}: " + tmpl.format(a=WEST_PLANET_KEY.get(p1, p1), b=WEST_PLANET_KEY.get(p2, p2)) + "."})
    asc = chart.get("ascendant")
    if isinstance(asc, dict) and asc.get("sign"):
        out["ascendant"] = f"{asc['sign']} rising: " + SIGN[asc["sign"]]
    return out

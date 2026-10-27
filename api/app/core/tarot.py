"""Tarot: 78-card deck with upright/reversed keywords; seeded or random spreads."""
from __future__ import annotations
import hashlib, random
from datetime import date as Date

MAJOR = [("The Fool", "beginnings, spontaneity, faith", "recklessness, hesitation"),
 ("The Magician", "willpower, skill, manifestation", "manipulation, untapped talent"),
 ("The High Priestess", "intuition, mystery, inner voice", "secrets, disconnected intuition"),
 ("The Empress", "abundance, nurturing, fertility", "dependence, creative block"),
 ("The Emperor", "authority, structure, stability", "domination, rigidity"),
 ("The Hierophant", "tradition, guidance, institutions", "rebellion, new approaches"),
 ("The Lovers", "love, harmony, choices", "imbalance, misalignment"),
 ("The Chariot", "determination, victory, control", "lack of direction, aggression"),
 ("Strength", "courage, compassion, inner strength", "self-doubt, weakness"),
 ("The Hermit", "introspection, solitude, wisdom", "isolation, withdrawal"),
 ("Wheel of Fortune", "cycles, luck, destiny", "bad luck, resistance to change"),
 ("Justice", "fairness, truth, law", "dishonesty, unfairness"),
 ("The Hanged Man", "surrender, new perspective, pause", "stalling, resistance"),
 ("Death", "endings, transformation, transition", "fear of change, stagnation"),
 ("Temperance", "balance, moderation, patience", "excess, imbalance"),
 ("The Devil", "attachment, temptation, materialism", "release, breaking free"),
 ("The Tower", "upheaval, revelation, sudden change", "averted disaster, fear of change"),
 ("The Star", "hope, renewal, inspiration", "despair, disconnection"),
 ("The Moon", "illusion, intuition, uncertainty", "clarity, released fear"),
 ("The Sun", "joy, success, vitality", "temporary sadness, overconfidence"),
 ("Judgement", "awakening, reckoning, renewal", "self-doubt, ignoring the call"),
 ("The World", "completion, fulfilment, travel", "incompletion, delays")]
SUITS = {"Wands": ("energy, passion, action", "Fire"), "Cups": ("emotions, relationships, intuition", "Water"),
         "Swords": ("thoughts, conflict, truth", "Air"), "Pentacles": ("money, work, material world", "Earth")}
RANKS = [("Ace", "new opportunity"), ("Two", "balance, decisions"), ("Three", "growth, collaboration"), ("Four", "stability, rest"),
         ("Five", "conflict, loss"), ("Six", "harmony, generosity"), ("Seven", "assessment, perseverance"), ("Eight", "movement, mastery"),
         ("Nine", "near-completion, resilience"), ("Ten", "culmination, burden"), ("Page", "curiosity, message"),
         ("Knight", "pursuit, action"), ("Queen", "nurturing mastery"), ("King", "authority, control")]

def deck():
    from .tarot_art import card_slug
    cards = [{"id": i, "name": n, "arcana": "major", "upright": u, "reversed": r,
              "image": f"/tarot/card/{card_slug(n)}.svg"} for i, (n, u, r) in enumerate(MAJOR)]
    for s, (theme, el) in SUITS.items():
        for rk, m in RANKS:
            name = f"{rk} of {s}"
            cards.append({"id": len(cards), "name": name, "arcana": "minor", "suit": s, "element": el,
                          "upright": f"{m} in {theme}", "reversed": f"blocked or excessive {m} in {theme}",
                          "image": f"/tarot/card/{card_slug(name)}.svg"})
    return cards

SPREADS = {"single": ["Card"], "yes_no": ["Answer"], "three_card": ["Past", "Present", "Future"],
           "love": ["You", "Partner", "Relationship", "Challenge", "Outcome"],
           "celtic_cross": ["Present", "Challenge", "Past", "Future", "Above (goal)", "Below (subconscious)", "Advice",
                            "External influences", "Hopes and fears", "Outcome"]}

def draw(spread: str = "three_card", seed: str | None = None, question: str | None = None):
    rng = random.Random(int(hashlib.sha256((seed or str(random.random())).encode() + (question or "").encode()).hexdigest(), 16)) 
    d = deck(); rng.shuffle(d)
    pos = SPREADS[spread]; out = []
    for i, p in enumerate(pos):
        c = d[i]; rev = rng.random() < 0.3
        out.append({"position": p, "card": c["name"], "reversed": rev, "meaning": c["reversed"] if rev else c["upright"],
                    "image": c["image"]})
    res = {"spread": spread, "question": question, "cards": out}
    if spread == "yes_no":
        c = d[0]; yes = (not out[0]["reversed"]) and c["name"] not in ("The Tower", "Death", "The Devil", "The Moon", "Five of Swords", "Ten of Swords", "Three of Swords")
        res["answer"] = "Yes" if yes else "No"
    return res

def daily(on: Date, sign_or_name: str = ""):
    return draw("single", seed=f"{on.isoformat()}:{sign_or_name}")

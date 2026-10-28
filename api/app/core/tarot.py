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
    from pathlib import Path
    art = Path(__file__).resolve().parents[2] / "web" / "static" / "tarot"
    def face(name):
        slug = card_slug(name)
        if (art / f"{slug}.jpg").is_file():
            return f"/static/tarot/{slug}.jpg"
        return f"/tarot/card/{slug}.svg"
    cards = [{"id": i, "name": n, "arcana": "major", "upright": u, "reversed": r,
              "image": face(n)} for i, (n, u, r) in enumerate(MAJOR)]
    for s, (theme, el) in SUITS.items():
        for rk, m in RANKS:
            name = f"{rk} of {s}"
            cards.append({"id": len(cards), "name": name, "arcana": "minor", "suit": s, "element": el,
                          "upright": f"{m} in {theme}", "reversed": f"blocked or excessive {m} in {theme}",
                          "image": face(name)})
    return cards

SPREADS = {"single": ["Card"], "yes_no": ["Answer"], "three_card": ["Past", "Present", "Future"],
           "love": ["You", "Partner", "Relationship", "Challenge", "Outcome"],
           "celtic_cross": ["Present", "Challenge", "Past", "Future", "Above (goal)", "Below (subconscious)", "Advice",
                            "External influences", "Hopes and fears", "Outcome"]}

def draw(spread: str = "three_card", seed: str | None = None, question: str | None = None):
    """Shuffle all 78, cut, then deal. A seed (the daily card) repeats; a live draw does not."""
    if seed:
        rng = random.Random(int(hashlib.sha256(f"{seed}|{question or ''}".encode()).hexdigest(), 16))
    else:
        rng = random.SystemRandom()
    d = deck()
    for i in range(len(d) - 1, 0, -1):
        j = rng.randrange(i + 1)
        d[i], d[j] = d[j], d[i]
    cut = rng.randrange(1, len(d))
    d = d[cut:] + d[:cut]
    pos = SPREADS[spread]
    out = []
    for i, p in enumerate(pos):
        c = d[i]
        rev = rng.random() < 0.18
        out.append({"position": p, "card": c["name"], "reversed": rev,
                    "meaning": c["reversed"] if rev else c["upright"], "image": c["image"]})
    if len(out) <= 5 and out and all(c["reversed"] for c in out):
        out[-1]["reversed"] = False
        name = out[-1]["card"]
        face = next(c for c in d if c["name"] == name)
        out[-1]["meaning"] = face["upright"]
    res = {"spread": spread, "question": question, "cards": out, "deck": 78}
    if spread == "yes_no":
        res["answer"] = "No" if out[0]["reversed"] else "Yes"
    return res

def daily(on: Date, sign_or_name: str = ""):
    return draw("single", seed=f"{on.isoformat()}:{sign_or_name}")

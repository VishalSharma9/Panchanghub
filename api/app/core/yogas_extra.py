"""Additional classical yogas (BPHS / Phaladeepika families): solar (Veshi/Vasi/Ubhayachari), lunar, Nabhasa
(Ashraya, Dala, Akriti, Sankhya), wealth/learning/fame yogas, Kartari, and Arishta/Daridra indicators."""
from __future__ import annotations
from .ephem import SIGN_LORDS
from .kundli import EXALT, OWN, relation

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
BENEFIC = ["Mercury", "Jupiter", "Venus"]; MALEFIC = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
K = {1, 4, 7, 10}; TRI = {1, 5, 9}; DUS = {6, 8, 12}; UPA = {3, 6, 10, 11}

def extra_yogas(sign_of: dict, houses_of: dict, asc_sign: int):
    y = []
    add = lambda n, d: y.append({"name": n, "description": d})
    h = lambda p: houses_of[p]
    rel = lambda a, b: (sign_of[b] - sign_of[a]) % 12 + 1
    lord = lambda n: SIGN_LORDS[(asc_sign + n - 1) % 12]
    strong = lambda p: p in EXALT and (sign_of[p] == EXALT[p] or sign_of[p] in OWN.get(p, []))
    occ = lambda house: [p for p in SEVEN + ["Rahu", "Ketu"] if h(p) == house]
    # Solar yogas
    others = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    s2 = [p for p in others if rel("Sun", p) == 2]; s12 = [p for p in others if rel("Sun", p) == 12]
    if s2 and s12: add("Ubhayachari Yoga", "Planets in both 2nd and 12th from the Sun")
    elif s2: add("Veshi Yoga", "Planet(s) in 2nd from the Sun")
    elif s12: add("Vasi Yoga", "Planet(s) in 12th from the Sun")
    # Lunar
    if rel("Jupiter", "Moon") in (6, 8, 12) and h("Moon") not in K: add("Shakata Yoga", "Moon in 6/8/12 from Jupiter, not in a kendra")
    if all(rel("Moon", p) in UPA or h(p) in UPA for p in BENEFIC): add("Vasumati Yoga", "Benefics in upachaya houses")
    if rel("Moon", "Sun") in K: add("Adhama Yoga (Moon kendra to Sun)", "Moon in a kendra from the Sun: modest wealth & effort-based gains")
    # Mars/Jupiter etc.
    if sign_of["Jupiter"] == sign_of["Mars"]: add("Guru Mangala Yoga", "Jupiter conjunct Mars")
    if sign_of["Jupiter"] == sign_of["Moon"]: add("Gaja Kesari (conjunction) / Guru-Chandra Yoga", "Jupiter conjunct the Moon")
    if any(h(p) == 10 for p in BENEFIC) and not any(h(p) == 10 for p in ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]): add("Amala Yoga", "Only benefics in the 10th house")
    if all(h(p) in K | TRI | {2} for p in BENEFIC) and strong("Jupiter") or (all(h(p) in K | TRI | {2} for p in BENEFIC) and h("Jupiter") in K):
        add("Saraswati Yoga", "Jupiter, Venus and Mercury in kendra/trikona/2nd")
    l9 = lord(9)
    if (strong(l9) and h(l9) in K | TRI) and (strong("Venus") or h("Venus") in K | TRI): add("Lakshmi Yoga", "Strong 9th lord and Venus in kendra/trikona")
    if all(h(p) not in (7, 8) for p in MALEFIC) and any(h(p) in K for p in BENEFIC): add("Parvata Yoga", "Benefics in kendras, 7th & 8th free of malefics")
    if h(lord(4)) in K and h(lord(9)) in K and lord(4) != lord(9): add("Kahala Yoga", "4th and 9th lords in mutual kendras")
    l1 = lord(1)
    if strong(l1) and h(l1) in K and rel("Jupiter", l1) in (1, 5, 7, 9): add("Chamara Yoga", "Strong lagna lord in kendra aspected by Jupiter")
    if h(lord(5)) in K and h(lord(6)) in K and rel(lord(5), lord(6)) in K: add("Sankha Yoga", "5th and 6th lords in mutual kendras")
    if h("Jupiter") in (2, 5) and (sign_of["Jupiter"] in (sign_of["Mercury"], sign_of["Venus"])): add("Kalanidhi Yoga", "Jupiter in 2nd/5th with Mercury or Venus")
    md = SIGN_LORDS[sign_of["Moon"]]
    if sign_of[l1] == sign_of["Moon"] and h(md) in K: add("Pushkala Yoga", "Lagna lord with Moon; Moon's dispositor in a kendra")
    # Kartari
    def flank(house, grp): 
        a = (house % 12) + 1; b = ((house - 2) % 12) + 1
        return any(h(p) == a for p in grp) and any(h(p) == b for p in grp)
    if flank(1, BENEFIC): add("Shubha Kartari Yoga", "Benefics in 2nd and 12th from lagna")
    if flank(1, ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]): add("Papa Kartari Yoga", "Malefics in 2nd and 12th from lagna")
    # Wealth / fortune
    if h(lord(2)) in K | TRI and h(lord(11)) in K | TRI: add("Dhana Yoga (2nd & 11th lords in kendra/trikona)", "Wealth-house lords well placed")
    if sign_of[lord(5)] == sign_of[lord(9)] and lord(5) != lord(9): add("Dhana Yoga (5th & 9th lords)", "Lords of 5th and 9th conjunct")
    if sign_of[lord(9)] == sign_of[lord(10)] and lord(9) != lord(10): add("Dharma-Karmadhipati Yoga", "Lords of 9th and 10th conjunct")
    if h(lord(9)) == 10 and h(lord(10)) == 9: add("Dharma-Karmadhipati Yoga (exchange)", "9th and 10th lords exchange")
    # Parivartana (sign exchange)
    for i, a in enumerate(SEVEN):
        for b in SEVEN[i + 1:]:
            if SIGN_LORDS[sign_of[a]] == b and SIGN_LORDS[sign_of[b]] == a:
                ha, hb = h(a), h(b)
                kind = "Dainya" if ha in DUS or hb in DUS else "Khala" if 3 in (ha, hb) else "Maha"
                add(f"{kind} Parivartana Yoga", f"{a} and {b} exchange signs (houses {ha} & {hb})")
    # Arishta / Daridra
    if h(lord(11)) in DUS: add("Daridra Yoga", "11th lord in a dusthana (gains need effort)")
    if h("Moon") in DUS and any(sign_of[p] == sign_of["Moon"] for p in ["Mars", "Saturn", "Rahu"]): add("Balarishta indication", "Afflicted Moon in 6/8/12 (childhood health care advised)")
    if sign_of["Sun"] == sign_of["Saturn"]: add("Surya-Shani conjunction", "Tension between authority and duty; delayed recognition")
    # Nabhasa: Sankhya (number of signs occupied by 7 planets)
    n = len({sign_of[p] for p in SEVEN})
    sank = {1: "Gola", 2: "Yuga", 3: "Shoola", 4: "Kedara", 5: "Pasha", 6: "Damini", 7: "Vallaki (Veena)"}
    add(f"{sank[n]} Yoga (Nabhasa-Sankhya)", f"Seven planets occupy {n} sign(s)")
    q = [sign_of[p] % 3 for p in SEVEN]
    if all(x == 0 for x in q): add("Rajju Yoga (Nabhasa-Ashraya)", "All planets in movable signs")
    elif all(x == 1 for x in q): add("Musala Yoga (Nabhasa-Ashraya)", "All planets in fixed signs")
    elif all(x == 2 for x in q): add("Nala Yoga (Nabhasa-Ashraya)", "All planets in dual signs")
    hs = {h(p) for p in SEVEN}
    if hs <= K and len(hs) == 4 and all(h(p) in K for p in BENEFIC): add("Mala Yoga (Nabhasa-Dala)", "Benefics occupying kendras")
    if all(h(p) in K for p in ["Sun", "Mars", "Saturn"]) and not any(h(p) in K for p in BENEFIC): add("Sarpa Yoga (Nabhasa-Dala)", "Malefics in kendras")
    if hs <= {1, 5, 9}: add("Shringataka Yoga (Nabhasa-Akriti)", "All planets in trikonas")
    if hs <= {1, 7}: add("Shakata Yoga (Nabhasa-Akriti)", "All planets in 1st and 7th")
    if hs <= {4, 10}: add("Vihaga Yoga (Nabhasa-Akriti)", "All planets in 4th and 10th")
    if hs <= {1, 4} or hs <= {4, 7} or hs <= {7, 10} or hs <= {10, 1}: add("Gada Yoga (Nabhasa-Akriti)", "All planets in two adjacent kendras")
    if hs <= K and len(hs) == 4: add("Kamala Yoga (Nabhasa-Akriti)", "Planets spread over all four kendras")
    if hs <= {2, 5, 8, 11} or hs <= {3, 6, 9, 12}: add("Vapi Yoga (Nabhasa-Akriti)", "All planets in panapharas or apoklimas")
    if hs <= {1, 2, 3, 4}: add("Yupa Yoga (Nabhasa-Akriti)", "Planets in houses 1-4")
    if hs <= {4, 5, 6, 7}: add("Ishu (Shara) Yoga (Nabhasa-Akriti)", "Planets in houses 4-7")
    if hs <= {7, 8, 9, 10}: add("Shakti Yoga (Nabhasa-Akriti)", "Planets in houses 7-10")
    if hs <= {10, 11, 12, 1}: add("Danda Yoga (Nabhasa-Akriti)", "Planets in houses 10-1")
    span = sorted(hs)
    if len(hs) == 7:
        seq = [((span[0] - 1 + i) % 12) + 1 for i in range(7)]
        if set(seq) == hs:
            names = {1: "Nauka", 4: "Kuta", 7: "Chhatra", 10: "Chapa"}
            add(f"{names.get(span[0], 'Ardha Chandra')} Yoga (Nabhasa-Akriti)", "Planets in seven consecutive houses")
    if hs <= {1, 3, 5, 7, 9, 11} and len(hs) == 6: add("Chakra Yoga (Nabhasa-Akriti)", "Planets in alternate houses from lagna")
    if hs <= {2, 4, 6, 8, 10, 12} and len(hs) == 6: add("Samudra Yoga (Nabhasa-Akriti)", "Planets in alternate houses from 2nd")
    return y

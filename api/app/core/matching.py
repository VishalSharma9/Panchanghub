"""Kundli matching: North Indian Ashtakoota (36 guna) and South Indian 10 Porutham."""
from __future__ import annotations
from .ephem import NAKSHATRAS, RASHIS, SIGN_LORDS
from .kundli import relation

VARNA = {3: 3, 7: 3, 11: 3, 0: 2, 4: 2, 8: 2, 1: 1, 5: 1, 9: 1, 2: 0, 6: 0, 10: 0}
VARNA_NAMES = ["Shudra", "Vaishya", "Kshatriya", "Brahmin"]
YONI = ["Horse","Elephant","Sheep","Serpent","Serpent","Dog","Cat","Sheep","Cat","Rat","Rat","Cow","Buffalo","Tiger",
        "Buffalo","Tiger","Deer","Deer","Dog","Monkey","Mongoose","Monkey","Lion","Horse","Lion","Cow","Elephant"]
YONI_ENEMY = {frozenset(p) for p in [("Horse","Buffalo"),("Elephant","Lion"),("Sheep","Monkey"),("Serpent","Mongoose"),
              ("Dog","Deer"),("Cat","Rat"),("Cow","Tiger")]}
YONI_FRIENDLY = {frozenset(p) for p in [("Horse","Deer"),("Elephant","Sheep"),("Cow","Buffalo"),("Cat","Monkey"),("Dog","Mongoose"),("Rat","Serpent"),("Tiger","Lion")]}
GANA = [0,1,2,1,0,1,0,0,2,2,1,1,0,2,0,2,0,2,2,1,1,0,2,2,1,1,0]  # 0 Deva 1 Manushya 2 Rakshasa
GANA_NAMES = ["Deva", "Manushya", "Rakshasa"]
NADI = [0,1,2,2,1,0] * 5
NADI_NAMES = ["Adi", "Madhya", "Antya"]
VASHYA_NAMES = ["Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta"]
VASHYA_TABLE = [[2,1,1,0.5,1],[1,2,0.5,0,1],[1,0.5,2,1,1],[0.5,0,1,2,0],[1,1,1,0,2]]
RAJJU = ["Pada","Kati","Nabhi","Kantha","Siro","Kantha","Nabhi","Kati","Pada"] * 3
VEDHA = [(0,17),(1,16),(2,15),(3,14),(5,21),(6,20),(7,19),(8,18),(9,26),(10,25),(11,24),(12,23),(4,22),(4,13),(13,22)]

def vashya(lon):
    s, d = int(lon // 30), lon % 30
    if s in (0, 1): return 0
    if s in (2, 5, 6, 10): return 1
    if s in (3, 11): return 2
    if s == 4: return 3
    if s == 7: return 4
    if s == 8: return 1 if d < 15 else 0
    if s == 9: return 0 if d < 15 else 2

def maitri_score(l1, l2):
    if l1 == l2: return 5
    a, b = relation(l1, l2), relation(l2, l1)
    pair = sorted([a, b])
    return {("friend","friend"):5, ("friend","neutral"):4, ("neutral","neutral"):3, ("enemy","friend"):1,
            ("enemy","neutral"):0.5, ("enemy","enemy"):0}[tuple(pair)]

def ashtakoota(boy_moon: float, girl_moon: float):
    bs, gs = int(boy_moon // 30), int(girl_moon // 30)
    bn, gn = int(boy_moon // (360/27)), int(girl_moon // (360/27))
    k = []
    v = 1 if VARNA[bs] >= VARNA[gs] else 0
    k.append(("Varna", 1, v, f"{VARNA_NAMES[VARNA[bs]]} / {VARNA_NAMES[VARNA[gs]]}"))
    bv, gv = vashya(boy_moon), vashya(girl_moon)
    k.append(("Vashya", 2, VASHYA_TABLE[bv][gv], f"{VASHYA_NAMES[bv]} / {VASHYA_NAMES[gv]}"))
    t1 = ((bn - gn) % 27 + 1) % 9; t2 = ((gn - bn) % 27 + 1) % 9
    bad = {3, 5, 7}
    tscore = (0 if t1 in bad else 1.5) + (0 if t2 in bad else 1.5)
    k.append(("Tara", 3, tscore, f"counts {((bn-gn)%27+1)} / {((gn-bn)%27+1)}"))
    by, gy = YONI[bn], YONI[gn]
    ys = 4 if by == gy else 0 if frozenset((by, gy)) in YONI_ENEMY else 3 if frozenset((by, gy)) in YONI_FRIENDLY else 2
    k.append(("Yoni", 4, ys, f"{by} / {gy}"))
    bl, gl = SIGN_LORDS[bs], SIGN_LORDS[gs]
    k.append(("Graha Maitri", 5, maitri_score(bl, gl), f"{bl} / {gl}"))
    bg, gg = GANA[bn], GANA[gn]
    gtab = {(0,0):6,(1,1):6,(2,2):6,(0,1):6,(1,0):5,(0,2):1,(2,0):1,(1,2):0,(2,1):0}
    k.append(("Gana", 6, gtab[(bg, gg)], f"{GANA_NAMES[bg]} / {GANA_NAMES[gg]}"))
    dist = (bs - gs) % 12 + 1; dist2 = (gs - bs) % 12 + 1
    bk = 0 if {dist, dist2} in ({2, 12}, {5, 9}, {6, 8}) else 7
    k.append(("Bhakoot", 7, bk, f"{RASHIS[bs]} / {RASHIS[gs]} ({dist}/{dist2})"))
    nd = 0 if NADI[bn] == NADI[gn] else 8
    k.append(("Nadi", 8, nd, f"{NADI_NAMES[NADI[bn]]} / {NADI_NAMES[NADI[gn]]}"))
    total = sum(x[2] for x in k)
    verdict = "Excellent" if total >= 28 else "Very good" if total >= 24 else "Good / acceptable" if total >= 18 else "Not recommended"
    doshas = []
    if nd == 0: doshas.append("Nadi Dosha")
    if bk == 0: doshas.append("Bhakoot Dosha")
    if gtab[(bg, gg)] <= 1: doshas.append("Gana Dosha")
    return {"kootas": [{"koota": a, "max": m, "obtained": o, "detail": d} for a, m, o, d in k],
            "total": total, "max": 36, "verdict": verdict, "doshas": doshas,
            "boy": {"rashi": RASHIS[bs], "nakshatra": NAKSHATRAS[bn]}, "girl": {"rashi": RASHIS[gs], "nakshatra": NAKSHATRAS[gn]}}

def porutham(boy_moon: float, girl_moon: float):
    bs, gs = int(boy_moon // 30), int(girl_moon // 30)
    bn, gn = int(boy_moon // (360/27)), int(girl_moon // (360/27))
    c = (bn - gn) % 27 + 1  # count from girl's star to boy's
    res = []
    res.append(("Dinam", c % 9 in (2, 4, 6, 8, 0)))
    res.append(("Ganam", GANA[bn] == GANA[gn] or (GANA[gn] == 0 and GANA[bn] == 1) or (GANA[gn] == 1 and GANA[bn] == 0)))
    res.append(("Mahendram", c in (4, 7, 10, 13, 16, 19, 22, 25)))
    res.append(("Stree Deergham", c >= 13))
    res.append(("Yoni", frozenset((YONI[bn], YONI[gn])) not in YONI_ENEMY))
    rc = (bs - gs) % 12 + 1
    res.append(("Rasi", rc == 1 or (rc > 6 and rc != 8)))
    res.append(("Rasi Adhipathi", relation(SIGN_LORDS[bs], SIGN_LORDS[gs]) != "enemy" and relation(SIGN_LORDS[gs], SIGN_LORDS[bs]) != "enemy"))
    res.append(("Vasya", vashya(boy_moon) == vashya(girl_moon)))
    res.append(("Rajju", RAJJU[bn] != RAJJU[gn]))
    vedha = any({bn, gn} == {a, b} for a, b in VEDHA)
    res.append(("Vedha", not vedha))
    ok = sum(1 for _, g in res if g)
    return {"poruthams": [{"name": n, "match": g} for n, g in res], "matched": ok, "total": 10,
            "rajju_ok": RAJJU[bn] != RAJJU[gn], "boy_rajju": RAJJU[bn], "girl_rajju": RAJJU[gn],
            "verdict": "Good" if ok >= 6 and RAJJU[bn] != RAJJU[gn] else "Average" if ok >= 5 else "Not recommended"}

"""Classical yoga rule catalogue (round 4). Each rule carries a classical citation (text + chapter) so the
reader can check the source. Rules are paraphrased in our own words from the conditions given in the
public-domain translations listed in research/sources.md (Jataka Parijata tr. V. Subrahmanya Sastri 1932,
Phaladeepika tr. 1937, Kalaprakasika 1917) and the standard BPHS chapter numbering.
Simplifications (e.g. strength = own/exalted sign) are noted in each rule's text."""
from __future__ import annotations
from .ephem import SIGN_LORDS
from .kundli import EXALT, OWN

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NINE = SEVEN + ["Rahu", "Ketu"]
BEN = ["Mercury", "Jupiter", "Venus"]; MAL = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
K = {1, 4, 7, 10}; T = {1, 5, 9}; DUS = {6, 8, 12}
DEBIL = {p: (s + 6) % 12 for p, s in EXALT.items()}
FIXED = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius
BPHS, JP, PD, SAR = "Brihat Parashara Hora Shastra", "Jataka Parijata", "Phaladeepika", "Saravali"

def _ctx(sign_of, houses_of, asc):
    c = {}
    c["s"] = lambda p: sign_of[p]
    c["h"] = lambda p: houses_of[p]
    c["lord"] = lambda n: SIGN_LORDS[(asc + n - 1) % 12]
    c["rel"] = lambda a, b: (sign_of[b] - sign_of[a]) % 12 + 1
    c["exalt"] = lambda p: p in EXALT and sign_of[p] == EXALT[p]
    c["own"] = lambda p: sign_of[p] in OWN.get(p, [])
    c["strong"] = lambda p: c["exalt"](p) or c["own"](p)
    c["debil"] = lambda p: p in DEBIL and sign_of[p] == DEBIL[p]
    c["conj"] = lambda a, b: sign_of[a] == sign_of[b]
    c["asc"] = asc
    return c

def _r(name, cite, desc, fn, kind="auspicious"):
    return {"name": name, "citation": cite, "description": desc, "fn": fn, "kind": kind}

def _malika(c):
    occ = sorted({c["s"](p) for p in SEVEN})
    best = run = 1
    for i in range(1, 12 * 2):
        if (i % 12) in occ and ((i - 1) % 12) in occ: run += 1; best = max(best, run)
        else: run = 1
    return min(best, 12) >= 5 and len(occ) >= 5

def _sankhya(n):
    return lambda c: len({c["s"](p) for p in SEVEN}) == n

RULES = [
    _r("Srinatha Yoga", f"{BPHS} ch.36 / {JP} ch.7", "7th lord exalted in the 10th and the 10th lord joined with the 9th lord",
       lambda c: c["h"](c["lord"](7)) == 10 and c["exalt"](c["lord"](7)) and c["conj"](c["lord"](10), c["lord"](9))),
    _r("Sarada Yoga", f"{BPHS} ch.36 / {JP} ch.7", "10th lord in the 5th, Mercury in a kendra, Sun strong in Leo",
       lambda c: c["h"](c["lord"](10)) == 5 and c["h"]("Mercury") in K and c["s"]("Sun") == 4),
    _r("Bheri Yoga", f"{BPHS} ch.36 / {JP} ch.7", "Venus, Jupiter and the lagna lord in mutual kendras and the 9th lord strong",
       lambda c: c["rel"]("Venus", "Jupiter") in K and c["rel"]("Venus", c["lord"](1)) in K and c["strong"](c["lord"](9))),
    _r("Matsya Yoga", f"{BPHS} ch.36", "Malefics in the 1st and 9th, benefics in the 5th",
       lambda c: any(c["h"](p) == 1 for p in MAL) and any(c["h"](p) == 9 for p in MAL) and any(c["h"](p) == 5 for p in BEN)),
    _r("Kurma Yoga", f"{BPHS} ch.36 / {JP} ch.7", "Benefics in the 5th/6th/7th and malefics in the 1st/3rd/11th (simplified: no strength test)",
       lambda c: all(c["h"](p) in {5, 6, 7} for p in BEN) and all(c["h"](p) in {1, 3, 11} for p in ["Mars", "Saturn"])),
    _r("Khadga Yoga", f"{BPHS} ch.36 / {JP} ch.7", "2nd and 9th lords exchange houses, lagna lord in a kendra or trikona",
       lambda c: c["h"](c["lord"](2)) == 9 and c["h"](c["lord"](9)) == 2 and c["h"](c["lord"](1)) in K | T),
    _r("Kusuma Yoga", f"{BPHS} ch.36 / {JP} ch.7", "Fixed lagna, Venus in a kendra, Moon in a trikona and Saturn in the 10th",
       lambda c: c["asc"] in FIXED and c["h"]("Venus") in K and c["h"]("Moon") in T and c["h"]("Saturn") == 10),
    _r("Parijata Yoga", f"{BPHS} ch.36 / {JP} ch.7", "Dispositor of the lagna lord placed in a kendra or trikona and strong (simplified)",
       lambda c: (lambda d: c["h"](d) in K | T and c["strong"](d))(SIGN_LORDS[c["s"](c["lord"](1))])),
    _r("Shiva Yoga", f"{BPHS} ch.36", "5th lord in the 9th, 9th lord in the 10th, 10th lord in the 5th",
       lambda c: c["h"](c["lord"](5)) == 9 and c["h"](c["lord"](9)) == 10 and c["h"](c["lord"](10)) == 5),
    _r("Indra Yoga", f"{JP} ch.7", "5th and 11th lords exchange signs and the Moon is in the 5th",
       lambda c: c["h"](c["lord"](5)) == 11 and c["h"](c["lord"](11)) == 5 and c["h"]("Moon") == 5),
    _r("Brahma Yoga", f"{BPHS} ch.36", "Jupiter in a kendra from the 9th lord and Venus in a kendra from the 11th lord",
       lambda c: c["rel"](c["lord"](9), "Jupiter") in K and c["rel"](c["lord"](11), "Venus") in K),
    _r("Gandharva Yoga", f"{BPHS} ch.36", "10th lord in 3/7/11, lagna lord with Jupiter, Moon in the 9th",
       lambda c: c["h"](c["lord"](10)) in {3, 7, 11} and c["conj"](c["lord"](1), "Jupiter") and c["h"]("Moon") == 9),
    _r("Go Yoga", f"{BPHS} ch.36", "Jupiter strong with the 2nd lord and the lagna lord exalted (simplified)",
       lambda c: c["strong"]("Jupiter") and c["conj"]("Jupiter", c["lord"](2)) and c["exalt"](c["lord"](1))),
    _r("Devendra Yoga", f"{BPHS} ch.36", "Fixed lagna; lagna and 11th lords exchange; 2nd and 10th lords exchange",
       lambda c: c["asc"] in FIXED and c["h"](c["lord"](1)) == 11 and c["h"](c["lord"](11)) == 1 and c["h"](c["lord"](2)) == 10 and c["h"](c["lord"](10)) == 2),
    _r("Amsavatara Yoga", f"{BPHS} ch.36", "Venus and Jupiter in kendras and Saturn exalted in a kendra",
       lambda c: c["h"]("Venus") in K and c["h"]("Jupiter") in K and c["exalt"]("Saturn") and c["h"]("Saturn") in K),
    _r("Harihara-Brahma Yoga", f"{BPHS} ch.36", "Benefics in the 8th and 12th from the 2nd lord",
       lambda c: any(c["rel"](c["lord"](2), p) == 8 for p in BEN) and any(c["rel"](c["lord"](2), p) == 12 for p in BEN)),
    _r("Chatussagara Yoga", f"{SAR} ch.35 / {PD} ch.6", "All four kendras occupied by planets",
       lambda c: all(any(c["h"](p) == k for p in SEVEN) for k in K)),
    _r("Mahabhagya Yoga", f"{PD} ch.6", "Sun above the horizon (day birth) with Sun, Moon and lagna in odd signs (male rule)",
       lambda c: c["h"]("Sun") in {7, 8, 9, 10, 11, 12} and all(x % 2 == 0 for x in (c["s"]("Sun"), c["s"]("Moon"), c["asc"]))),
    _r("Kemadruma Bhanga", f"{PD} ch.6 / {BPHS} ch.38", "Kemadruma cancelled: Moon or another planet in a kendra from lagna, or a planet in a kendra from the Moon",
       lambda c: c["h"]("Moon") in K or any(c["rel"]("Moon", p) in {4, 7, 10} for p in SEVEN if p != "Moon")),
    _r("Harsha Yoga (Viparita)", f"{PD} ch.6", "6th lord placed in the 6th, 8th or 12th",
       lambda c: c["h"](c["lord"](6)) in DUS),
    _r("Sarala Yoga (Viparita)", f"{PD} ch.6", "8th lord placed in the 6th, 8th or 12th",
       lambda c: c["h"](c["lord"](8)) in DUS),
    _r("Vimala Yoga (Viparita)", f"{PD} ch.6", "12th lord placed in the 6th, 8th or 12th",
       lambda c: c["h"](c["lord"](12)) in DUS),
    _r("Dur Yoga", f"{PD} ch.6", "10th lord in the 6th, 8th or 12th: effort without due recognition", lambda c: c["h"](c["lord"](10)) in DUS, "challenging"),
    _r("Daridra Yoga (11th lord)", f"{PD} ch.6", "11th lord in the 6th, 8th or 12th", lambda c: c["h"](c["lord"](11)) in DUS, "challenging"),
    _r("Malika Yoga", f"{BPHS} ch.35 (Nabhasa) / {SAR}", "Seven planets in five or more consecutive signs", _malika),
    _r("Gola Yoga (Sankhya)", f"{BPHS} ch.35", "All seven planets in one sign", _sankhya(1), "challenging"),
    _r("Yuga Yoga (Sankhya)", f"{BPHS} ch.35", "Seven planets in two signs", _sankhya(2), "challenging"),
    _r("Shula Yoga (Sankhya)", f"{BPHS} ch.35", "Seven planets in three signs", _sankhya(3)),
    _r("Kedara Yoga (Sankhya)", f"{BPHS} ch.35", "Seven planets in four signs", _sankhya(4)),
    _r("Pasha Yoga (Sankhya)", f"{BPHS} ch.35", "Seven planets in five signs", _sankhya(5)),
    _r("Damini Yoga (Sankhya)", f"{BPHS} ch.35", "Seven planets in six signs", _sankhya(6)),
    _r("Vina (Vallaki) Yoga (Sankhya)", f"{BPHS} ch.35", "Seven planets in seven signs", _sankhya(7)),
    _r("Shubha Mala Yoga", f"{PD} ch.6", "Benefics occupying the 5th, 6th and 7th", lambda c: {c["h"](p) for p in BEN} >= {5, 6, 7}),
    _r("Ashubha Mala Yoga", f"{PD} ch.6", "Malefics occupying the 5th, 6th and 7th", lambda c: {c["h"](p) for p in MAL} >= {5, 6, 7}, "challenging"),
    _r("Lagnadhi Yoga", f"{PD} ch.6", "Benefics in the 7th and 8th from lagna, unafflicted by malefics",
       lambda c: any(c["h"](p) == 7 for p in BEN) and any(c["h"](p) == 8 for p in BEN) and not any(c["h"](p) in {7, 8} for p in MAL)),
    _r("Bhaskara Yoga", f"{BPHS} ch.36", "Mercury 2nd from the Sun, Moon 11th from Mercury, Jupiter 5th/9th from the Moon",
       lambda c: c["rel"]("Sun", "Mercury") == 2 and c["rel"]("Mercury", "Moon") == 11 and c["rel"]("Moon", "Jupiter") in {5, 9}),
    _r("Marud Yoga", f"{BPHS} ch.36", "Jupiter 5th/9th from Venus, Moon 5th from Jupiter, Sun in a kendra from the Moon",
       lambda c: c["rel"]("Venus", "Jupiter") in {5, 9} and c["rel"]("Jupiter", "Moon") == 5 and c["rel"]("Moon", "Sun") in K),
    _r("Budha Yoga", f"{BPHS} ch.36", "Jupiter in lagna, Moon in a kendra from Jupiter, Rahu 2nd from the Moon",
       lambda c: c["h"]("Jupiter") == 1 and c["rel"]("Jupiter", "Moon") in K and c["rel"]("Moon", "Rahu") == 2),
    _r("Trilochana Yoga", f"{SAR}", "Sun, Moon and Mars in mutual trines",
       lambda c: c["rel"]("Sun", "Moon") in {5, 9} and c["rel"]("Moon", "Mars") in {5, 9} and c["rel"]("Sun", "Mars") in {5, 9}),
    _r("Putra Yoga", f"{PD} ch.12", "5th lord in a kendra or trikona with or aspected by a benefic (conjunction used)",
       lambda c: c["h"](c["lord"](5)) in K | T and any(c["conj"](c["lord"](5), b) for b in BEN if b != c["lord"](5))),
    _r("Vidya Yoga", f"{PD} ch.6", "4th and 5th lords well placed (kendra/trikona) and Mercury strong",
       lambda c: c["h"](c["lord"](4)) in K | T and c["h"](c["lord"](5)) in K | T and (c["strong"]("Mercury") or c["h"]("Mercury") in K)),
    _r("Kalatra Yoga", f"{PD} ch.10", "7th lord and Venus both in kendras", lambda c: c["h"](c["lord"](7)) in K and c["h"]("Venus") in K),
    _r("Sukha Yoga", f"{PD} ch.6", "4th lord in a kendra/trikona and Venus strong",
       lambda c: c["h"](c["lord"](4)) in K | T and (c["strong"]("Venus") or c["h"]("Venus") in K)),
    _r("Bhagya Yoga", f"{PD} ch.6", "9th lord in the 9th or in its own/exaltation sign",
       lambda c: c["h"](c["lord"](9)) == 9 or c["strong"](c["lord"](9))),
    _r("Jaya Yoga", f"{SAR} ch.35", "6th lord debilitated and 10th lord exalted", lambda c: c["debil"](c["lord"](6)) and c["exalt"](c["lord"](10))),
    _r("Raja Lakshana Yoga", f"{BPHS} ch.36", "Jupiter, Venus, Mercury and Moon all in lagna or kendras",
       lambda c: all(c["h"](p) in K for p in ["Jupiter", "Venus", "Mercury", "Moon"])),
    _r("Tri-Uccha Raja Yoga", f"{PD} ch.7 / {SAR} ch.35", "Three or more planets exalted", lambda c: sum(c["exalt"](p) for p in SEVEN) >= 3),
    _r("Tri-Neecha Yoga", f"{SAR} ch.35", "Three or more planets debilitated", lambda c: sum(c["debil"](p) for p in SEVEN) >= 3, "challenging"),
    _r("Guru-Chandala Yoga", "Later Parashari / Kalaprakasika (doshas)", "Jupiter conjunct Rahu", lambda c: c["conj"]("Jupiter", "Rahu"), "challenging"),
    _r("Angaraka Yoga", "Later Parashari", "Mars conjunct Rahu", lambda c: c["conj"]("Mars", "Rahu"), "challenging"),
    _r("Grahana Yoga", "Later Parashari", "Sun or Moon conjunct Rahu/Ketu", lambda c: any(c["conj"](a, b) for a in ("Sun", "Moon") for b in ("Rahu", "Ketu")), "challenging"),
    _r("Shrapit Yoga", "Later Parashari", "Saturn conjunct Rahu", lambda c: c["conj"]("Saturn", "Rahu"), "challenging"),
    _r("Vish Yoga", "Later Parashari", "Saturn conjunct the Moon", lambda c: c["conj"]("Saturn", "Moon"), "challenging"),
    _r("Chandra Arishta", f"{BPHS} ch.11 (Arishta)", "Moon in 6/8/12 joined by a malefic",
       lambda c: c["h"]("Moon") in DUS and any(c["conj"]("Moon", m) for m in MAL), "challenging"),
    _r("Vanchana-Chora Bheeti Yoga", f"{PD} ch.6", "Rahu or Ketu in lagna with the lagna lord in a dusthana (simplified)",
       lambda c: (c["h"]("Rahu") == 1 or c["h"]("Ketu") == 1) and c["h"](c["lord"](1)) in DUS, "challenging"),
    _r("Ravi Yoga (natal)", f"{BPHS} ch.36", "Sun in the 10th and the 10th lord in the 3rd with Saturn",
       lambda c: c["h"]("Sun") == 10 and c["h"](c["lord"](10)) == 3 and c["conj"](c["lord"](10), "Saturn")),
    _r("Lakshmi-Narayana Yoga", "Later Parashari", "Mercury conjunct Venus in a kendra or trikona",
       lambda c: c["conj"]("Mercury", "Venus") and c["h"]("Venus") in K | T),
    _r("Shukra-Guru Yoga (Kalanidhi variant)", f"{PD} ch.6", "Jupiter and Venus conjunct", lambda c: c["conj"]("Jupiter", "Venus")),
    _r("Adhi Yoga from Lagna", f"{PD} ch.6", "Benefics in the 6th, 7th and 8th from lagna", lambda c: {c["h"](p) for p in BEN} >= {6, 7, 8}),
]

def classical_yogas(sign_of, houses_of, asc_sign):
    c = _ctx(sign_of, houses_of, asc_sign); out = []
    for r in RULES:
        try:
            if r["fn"](c):
                out.append({"name": r["name"], "description": r["description"], "citation": r["citation"], "kind": r["kind"]})
        except KeyError:
            continue
    return out

def catalog():
    """All yoga rules known to the engine (this module + kundli.detect_yogas + yogas_extra)."""
    import inspect, re
    from . import kundli, yogas_extra
    names = {r["name"]: r["citation"] for r in RULES}
    for mod in (kundli, yogas_extra):
        src = inspect.getsource(mod.detect_yogas if mod is kundli else mod.extra_yogas)
        for m in re.findall(r'(?:add|append)\(\(?f?"([^"{]+?(?:Yoga|indication|conjunction|Bhanga[^"]*))', src):
            names.setdefault(m.strip(), "BPHS / Phaladeepika (see module)")
    for p, n in {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa", "Venus": "Malavya", "Saturn": "Shasha"}.items():
        names.setdefault(f"{n} Yoga (Pancha Mahapurusha)", f"{BPHS} ch.75 / {PD} ch.6")
    return {"count": len(names), "yogas": [{"name": k, "citation": v} for k, v in sorted(names.items())]}

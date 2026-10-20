"""Human Design bodygraph from tropical positions (Rave mandala gate wheel).

Personality = birth moment; Design = moment when the Sun was 88 degrees of solar arc earlier.
Gates are 5.625 deg each starting with Gate 41 at 302 deg tropical (2 deg Aquarius); lines are 0.9375 deg.
Type, authority, profile, definition and incarnation-cross gates follow the standard Human Design rules.
"""
from __future__ import annotations
import swisseph as swe
from .ephem import jd_from_utc, utc_from_jd, norm, find_root

WHEEL = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
         31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50, 28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]
START = 302.0
CENTERS = {"Head": [64, 61, 63], "Ajna": [47, 24, 4, 17, 43, 11], "Throat": [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
           "G": [1, 13, 25, 46, 2, 15, 10, 7], "Heart": [21, 40, 26, 51], "Sacral": [5, 14, 29, 59, 9, 3, 42, 27, 34],
           "Spleen": [48, 57, 44, 50, 32, 28, 18], "Solar Plexus": [36, 22, 37, 6, 49, 55, 30], "Root": [53, 60, 52, 19, 39, 41, 58, 38, 54]}
GATE_CENTER = {g: c for c, gs in CENTERS.items() for g in gs}
CHANNELS = [(1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31), (9, 52), (10, 20), (10, 34), (10, 57), (11, 56), (12, 22),
            (13, 33), (16, 48), (17, 62), (18, 58), (19, 49), (20, 34), (20, 57), (21, 45), (23, 43), (24, 61), (25, 51), (26, 44),
            (27, 50), (28, 38), (29, 46), (30, 41), (32, 54), (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64)]
MOTORS = {"Heart", "Sacral", "Solar Plexus", "Root"}
BODIES = [("Sun", swe.SUN), ("Earth", None), ("Moon", swe.MOON), ("North Node", swe.TRUE_NODE), ("South Node", None),
          ("Mercury", swe.MERCURY), ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN),
          ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO)]
PROFILES = {(1, 3): "Investigator / Martyr", (1, 4): "Investigator / Opportunist", (2, 4): "Hermit / Opportunist",
            (2, 5): "Hermit / Heretic", (3, 5): "Martyr / Heretic", (3, 6): "Martyr / Role Model", (4, 6): "Opportunist / Role Model",
            (4, 1): "Opportunist / Investigator", (5, 1): "Heretic / Investigator", (5, 2): "Heretic / Hermit",
            (6, 2): "Role Model / Hermit", (6, 3): "Role Model / Martyr"}
TYPE_INFO = {"Manifestor": ("Inform before acting", "Peace", "Anger"), "Generator": ("Wait to respond", "Satisfaction", "Frustration"),
             "Manifesting Generator": ("Wait to respond, then inform", "Satisfaction & peace", "Frustration & anger"),
             "Projector": ("Wait for the invitation", "Success", "Bitterness"), "Reflector": ("Wait a lunar cycle (~29 days)", "Surprise", "Disappointment")}

def gate_line(lon: float):
    x = norm(lon - START); i = int(x // 5.625); line = int((x - i * 5.625) // 0.9375) + 1
    return WHEEL[i], line

def _tropical(jd, body):
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH)[0][0]

def _activations(jd):
    out = {}
    for name, b in BODIES:
        if name == "Earth": lon = norm(out["Sun"]["longitude"] + 180)
        elif name == "South Node": lon = norm(out["North Node"]["longitude"] + 180)
        else: lon = _tropical(jd, b)
        g, l = gate_line(lon)
        out[name] = {"longitude": round(lon, 4), "gate": g, "line": l, "activation": f"{g}.{l}"}
    return out

def design_jd(jd_birth):
    target = norm(_tropical(jd_birth, swe.SUN) - 88)
    f = lambda j: ((_tropical(j, swe.SUN) - target + 180) % 360) - 180
    return find_root(f, jd_birth - 95, jd_birth - 84, 1e-7)

def bodygraph(dt_utc):
    jd = jd_from_utc(dt_utc); jdd = design_jd(jd)
    pers, des = _activations(jd), _activations(jdd)
    gates = {v["gate"] for v in pers.values()} | {v["gate"] for v in des.values()}
    chans = [c for c in CHANNELS if c[0] in gates and c[1] in gates]
    defined = set()
    for a, b in chans: defined |= {GATE_CENTER[a], GATE_CENTER[b]}
    # connectivity of defined centers
    adj = {c: set() for c in CENTERS}
    for a, b in chans:
        ca, cb = GATE_CENTER[a], GATE_CENTER[b]; adj[ca].add(cb); adj[cb].add(ca)
    def reach(start, goal):
        seen, st = {start}, [start]
        while st:
            c = st.pop()
            if c == goal: return True
            for n in adj[c] - seen: seen.add(n); st.append(n)
        return False
    motor_throat = "Throat" in defined and any(reach(m, "Throat") for m in MOTORS if m in defined)
    if not defined: typ = "Reflector"
    elif "Sacral" in defined: typ = "Manifesting Generator" if motor_throat else "Generator"
    elif motor_throat: typ = "Manifestor"
    else: typ = "Projector"
    if "Solar Plexus" in defined: auth = "Emotional (Solar Plexus)"
    elif "Sacral" in defined: auth = "Sacral"
    elif "Spleen" in defined: auth = "Splenic"
    elif "Heart" in defined: auth = "Ego (Heart)" if typ == "Manifestor" or reach("Heart", "Throat") else "Ego Projected"
    elif "G" in defined: auth = "Self-Projected (G)"
    elif typ == "Reflector": auth = "Lunar"
    else: auth = "Mental / Environmental (none inner)"
    # definition splits
    comps, left = 0, set(defined)
    while left:
        c = left.pop(); comps += 1; st = [c]
        while st:
            x = st.pop()
            for n in adj[x] & left: left.discard(n); st.append(n)
    definition = {0: "None", 1: "Single", 2: "Split", 3: "Triple Split", 4: "Quadruple Split"}[min(comps, 4)]
    pl, dl = pers["Sun"]["line"], des["Sun"]["line"]
    strat, sig, notself = TYPE_INFO[typ]
    cross = [pers["Sun"]["gate"], pers["Earth"]["gate"], des["Sun"]["gate"], des["Earth"]["gate"]]
    angle = "Right Angle" if pl <= 3 and not (pl == 4 and dl == 1) else "Juxtaposition" if (pl, dl) == (4, 1) else "Left Angle"
    return {"type": typ, "strategy": strat, "signature": sig, "not_self_theme": notself, "authority": auth,
            "profile": f"{pl}/{dl}", "profile_name": PROFILES.get((pl, dl), ""), "definition": definition,
            "incarnation_cross": {"angle": angle, "gates": f"({cross[0]}/{cross[1]} | {cross[2]}/{cross[3]})"},
            "defined_centers": sorted(defined), "open_centers": sorted(set(CENTERS) - defined),
            "channels": [f"{a}-{b}" for a, b in chans], "gates": sorted(gates),
            "personality": pers, "design": des, "design_datetime_utc": utc_from_jd(jdd).isoformat(),
            "note": "Computed from the public Human Design mechanics (gate wheel, centers, channels); names of crosses not included."}

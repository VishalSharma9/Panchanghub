"""Human Design bodygraph from tropical positions (Rave mandala gate wheel).

Personality = birth moment; Design = moment when the Sun was 88 degrees of solar arc earlier.
Gates are 5.625 deg each starting with Gate 41 at 302 deg tropical (2 deg Aquarius); lines are 0.9375 deg.
Type, authority, profile, definition and incarnation-cross gates follow the standard Human Design rules.
"""
from __future__ import annotations
from .ephem import swe, jd_from_utc, utc_from_jd, norm, find_root

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
TYPE_READ = {
    "Manifestor": "A Manifestor is built to start things. Other people feel the impact, so the workable move is to tell them before you act. Skipping that talk is what turns into anger. Peace is the sign the type is being used properly.",
    "Generator": "A Generator has steady work energy, but it switches on in response to something real: a question, an offer, a person, a task in front of you. Starting from a blank plan and pushing it through feels like frustration. The right work feels like satisfaction.",
    "Manifesting Generator": "A Manifesting Generator also waits for a response, then moves quickly and often skips steps. Tell people what you are about to do, because the speed is easy to misread. Frustration means the response was skipped. Anger means people were left out of the move.",
    "Projector": "A Projector sees how other people work. The energy is for guiding, not for grinding all day to prove worth. The opening is an invitation or a clear recognition. Without that, effort turns into bitterness. Success here is being asked in and then being effective.",
    "Reflector": "A Reflector has no defined center. The chart samples the people and the room. A same-day yes on a big decision is not reliable. Give it a full lunar month, about 29 days, and notice which places make you feel like yourself. Surprise is the healthy feeling. Disappointment means the environment is wrong.",
}
AUTHORITY_READ = {
    "Emotional (Solar Plexus)": "Emotional authority means there is no clean answer in one mood. Ask the question again on another day. The useful answer is the one that stays when the high and the low have both passed.",
    "Sacral": "Sacral authority is a gut response in the moment, a yes or a no, not a list of reasons. If you have to talk yourself into it, that is not the sacral answer.",
    "Splenic": "Splenic authority is a quiet hit about health and safety, and it does not repeat. If you missed it and are now building a story, that story is not the authority.",
    "Ego (Heart)": "Ego authority asks whether you actually have the will. A correct-looking plan that the heart is not in is a no.",
    "Ego Projected": "The will is the authority, but it has to be spoken and recognized. Deciding in private and forcing it does not use this authority.",
    "Self-Projected (G)": "Talk the decision out loud and listen to your own voice. The answer is in what you hear yourself say, not in advice you collect.",
    "Lunar": "There is no fixed inner yes. Live with the question through a lunar cycle and watch how the answer changes with the people and places around you.",
    "Mental / Environmental (none inner)": "There is no inner authority to trust. The decision needs the right room and the right people to talk it through. The place is part of the answer.",
}
PROFILE_READ = {
    (1, 3): "1/3 investigates until the foundation is solid, then learns by trial. A mistake is data, not a verdict on you.",
    (1, 4): "1/4 studies first, then shares it with a close circle. The opportunity comes through people who already know you.",
    (2, 4): "2/4 has a natural gift and does not like being watched while using it. The call comes from friends, not from advertising yourself.",
    (2, 5): "2/5 is left alone until others project a solution onto you. Deliver what you can actually do, and correct the fantasy early.",
    (3, 5): "3/5 learns by bumping into what does not work, and other people still expect a fix. Share the experiment, not a perfect image.",
    (3, 6): "3/6 spends the early years in trial and error. Later the life is watched as an example. The bumps were the research.",
    (4, 6): "4/6 moves through a network, and over time becomes someone others measure themselves against. Keep the friendships honest.",
    (4, 1): "4/1 needs a correct foundation and then a network. Do not skip the study to keep the social pace.",
    (5, 1): "5/1 is asked to solve other people's problems. The investigation underneath the reputation is what keeps the projection honest.",
    (5, 2): "5/2 is called out of privacy to be the practical fix. You can say no when the projection is not your gift.",
    (6, 2): "6/2 watches life from a step back and still has a gift people want. Come down when the role is real, not when the noise is loud.",
    (6, 3): "6/3 is a role model who still learns by experiment. The example is the process, not a finished statue.",
}
DEFINITION_READ = {
    "None": "No center is defined, so nothing in the chart runs on its own. You are consistent only when the environment is.",
    "Single": "The defined centers connect in one piece. You do not need another person to feel your own energy. Other people are company, not a missing part.",
    "Split": "The definition is in two clusters. Certain people bridge them, and that can feel like chemistry. It is a bridge, not proof that you are incomplete alone.",
    "Triple Split": "Three clusters need a wider room of people to feel connected. One person is rarely the whole bridge.",
    "Quadruple Split": "Four clusters. You need varied contact, not a single fixed partner, for the chart to feel linked.",
}
CENTER_READ = {
    "Head": ("Inspiration is yours and it stays on. Pressure to answer every question is your own, so you can choose which ones matter.",
             "You amplify other people's questions. Not every inspiring idea in the room is yours to solve."),
    "Ajna": ("You think in a fixed way. The mind is reliable for processing, not for deciding your life.",
             "You can hold many ways of thinking. Certainty that arrives from someone else can be borrowed."),
    "Throat": ("You have a consistent voice and a way of doing. Manifestation runs through what you say and do.",
               "Your voice changes with the room. Wait until speaking is recognized, or it comes out forced."),
    "G": ("Identity and direction are stable. You know who you are without asking the room.",
          "Love and direction are sampled from the place and the people. The wrong room makes you feel lost."),
    "Heart": ("Willpower is reliable. Promises you make from the heart, you can keep. Do not promise from pride.",
              "Will is inconsistent. Proving you can push through is the trap of an open heart."),
    "Sacral": ("Work energy is available every day if the response was a yes. A mental yes with a flat gut will burn you out.",
               "You do not have sustainable work energy of your own. Rest is not laziness. Matching a Generator's hours will exhaust you."),
    "Spleen": ("Instinct about health and safety is consistent. The first quiet hit is the one to trust.",
               "You hold onto what is not healthy: jobs, people, places. Fear of letting go is the open spleen, not the truth."),
    "Solar Plexus": ("Feelings run on a wave. There is no truth at the top or the bottom of it.",
                     "You take on the feelings in the room and can mistake them for your own. Leave before you decide."),
    "Root": ("Pressure to get things done is steady. You can use it. You do not have to obey every deadline it invents.",
             "You feel other people's rush. A deadline that is not yours can still make the body panic."),
}

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
    centers = {}
    for name in CENTERS:
        defined_txt, open_txt = CENTER_READ[name]
        centers[name] = defined_txt if name in defined else open_txt
    cross_txt = (
        f"The incarnation cross uses four gates: personality Sun {cross[0]}, personality Earth {cross[1]}, "
        f"design Sun {cross[2]}, design Earth {cross[3]}. "
        + ("A right angle is a personal life. The theme is lived for its own sake." if angle == "Right Angle"
           else "A juxtaposition is a fixed, narrow path. It does not bend to the group." if angle == "Juxtaposition"
           else "A left angle is transpersonal. The life meets other people and is changed by that meeting.")
        + " The traditional cross name is not printed here. The four gates are the chart."
    )
    paragraphs = [
        f"You are a {typ}. {TYPE_READ[typ]}",
        f"Strategy: {strat}. Signature, the feeling when this is working, is {sig}. Not-self, the feeling when it is not, is {notself}.",
        AUTHORITY_READ[auth],
        f"Profile {pl}/{dl}. {PROFILE_READ.get((pl, dl), '')} The first number is the personality Sun line, the part of you that you recognize. The second is the design Sun line, the body, which other people often see before you do.",
        f"Definition is {definition.lower()}. {DEFINITION_READ[definition]}",
        "Personality activations are the birth moment. You can talk about them. Design activations are the body chart, taken when the Sun was 88 degrees earlier, about three months before birth. You live them without having chosen them.",
        cross_txt,
    ]
    return {"type": typ, "strategy": strat, "signature": sig, "not_self_theme": notself, "authority": auth,
            "profile": f"{pl}/{dl}", "profile_name": PROFILES.get((pl, dl), ""), "definition": definition,
            "incarnation_cross": {"angle": angle, "gates": f"({cross[0]}/{cross[1]} | {cross[2]}/{cross[3]})"},
            "defined_centers": sorted(defined), "open_centers": sorted(set(CENTERS) - defined),
            "channels": [f"{a}-{b}" for a, b in chans], "gates": sorted(gates),
            "personality": pers, "design": des, "design_datetime_utc": utc_from_jd(jdd).isoformat(),
            "reading": {"paragraphs": paragraphs, "centers": centers, "cross": cross_txt},
            "note": "Computed from the public Human Design mechanics (gate wheel, centers, channels); names of crosses not included."}

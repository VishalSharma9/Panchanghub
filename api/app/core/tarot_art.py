"""Original illustrated tarot faces. Each of the 78 cards is one SVG, gold-framed like a printed card."""
from __future__ import annotations
import re

W, H = 400, 700
AW, AH = 328, 468  # art window


def card_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _esc(s: str) -> str:
    return (s.replace("&", "&").replace("<", "<").replace(">", ">"))


def _sky(top: str, bot: str) -> str:
    return f'''<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>
    <rect width="{AW}" height="{AH}" fill="url(#sky)"/>'''


def _ground(y: int, fill: str) -> str:
    return f'<ellipse cx="{AW/2}" cy="{y+80}" rx="240" ry="90" fill="{fill}"/>'


def _sun(cx, cy, r, face=True) -> str:
    rays = []
    for i in range(16):
        import math
        a = i * math.pi / 8
        x1 = cx + math.cos(a) * (r + 4)
        y1 = cy + math.sin(a) * (r + 4)
        x2 = cx + math.cos(a) * (r + 18)
        y2 = cy + math.sin(a) * (r + 18)
        rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#f6d56a" stroke-width="3" stroke-linecap="round"/>')
    face = ""
    if face:
        face = f'<circle cx="{cx-8}" cy="{cy-4}" r="2.2" fill="#5a3b16"/><circle cx="{cx+8}" cy="{cy-4}" r="2.2" fill="#5a3b16"/><path d="M{cx-8},{cy+6} Q{cx},{cy+12} {cx+8},{cy+6}" fill="none" stroke="#5a3b16" stroke-width="1.6"/>'
    return "".join(rays) + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffe08a" stroke="#e0b44a" stroke-width="3"/>' + face


def _moon(cx, cy, r) -> str:
    return f'''<circle cx="{cx}" cy="{cy}" r="{r}" fill="#f4efc8"/>
    <circle cx="{cx+r*0.35:.1f}" cy="{cy-2}" r="{r*0.82:.1f}" fill="#1c2a55"/>
    <circle cx="{cx-4}" cy="{cy-2}" r="2" fill="#5c6a3a"/>'''


def _star(cx, cy, r, fill="#fff6c8") -> str:
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.4
        pts.append(f"{cx+math.cos(ang)*rad:.1f},{cy+math.sin(ang)*rad:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def _mountain(fill="#8aa0b4") -> str:
    return f'<path d="M0,{AH} L70,{AH-150} L130,{AH-70} L190,{AH-190} L250,{AH-80} L328,{AH-40} L328,{AH} Z" fill="{fill}"/>'


def _figure(x, y, h, robe, skin="#f3d0b0", hair="#2c2118", arm="down", crown=None, wings=False) -> str:
    """Standing figure. x,y is the point between the feet. h is full height."""
    s = h / 140
    hx, hy = x, y - h + 22 * s
    parts = []
    if wings:
        parts.append(f'<path d="M{x},{y-h*0.55} C{x-70*s},{y-h*0.85} {x-90*s},{y-h*0.35} {x-8*s},{y-h*0.4} Z" fill="#f7f4ee" opacity=".95"/>')
        parts.append(f'<path d="M{x},{y-h*0.55} C{x+70*s},{y-h*0.85} {x+90*s},{y-h*0.35} {x+8*s},{y-h*0.4} Z" fill="#f7f4ee"/>')
    parts.append(f'<path d="M{x-18*s:.1f},{y-h+40*s:.1f} L{x+18*s:.1f},{y-h+40*s:.1f} L{x+26*s:.1f},{y-6*s:.1f} Q{x},{y+4*s:.1f} {x-26*s:.1f},{y-6*s:.1f} Z" fill="{robe}"/>')
    parts.append(f'<path d="M{x-4*s:.1f},{y-h+42*s:.1f} L{x+6*s:.1f},{y-h+42*s:.1f} L{x+2*s:.1f},{y-18*s:.1f} Z" fill="#ffffff22"/>')
    # arm
    if arm == "up":
        parts.append(f'<path d="M{x+10*s:.1f},{y-h+55*s:.1f} Q{x+34*s:.1f},{y-h+20*s:.1f} {x+18*s:.1f},{y-h+8*s:.1f}" stroke="{robe}" stroke-width="{8*s:.1f}" fill="none" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{x+18*s:.1f}" cy="{y-h+6*s:.1f}" r="{5*s:.1f}" fill="{skin}"/>')
    elif arm == "out":
        parts.append(f'<path d="M{x-8*s:.1f},{y-h+60*s:.1f} L{x-40*s:.1f},{y-h+78*s:.1f}" stroke="{robe}" stroke-width="{7*s:.1f}" stroke-linecap="round"/>')
        parts.append(f'<path d="M{x+8*s:.1f},{y-h+60*s:.1f} L{x+40*s:.1f},{y-h+78*s:.1f}" stroke="{robe}" stroke-width="{7*s:.1f}" stroke-linecap="round"/>')
    else:
        parts.append(f'<path d="M{x+12*s:.1f},{y-h+58*s:.1f} Q{x+28*s:.1f},{y-h+90*s:.1f} {x+16*s:.1f},{y-30*s:.1f}" stroke="{robe}" stroke-width="{7*s:.1f}" fill="none" stroke-linecap="round"/>')
    parts.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{14*s:.1f}" fill="{skin}"/>')
    parts.append(f'<path d="M{hx-14*s:.1f},{hy-2*s:.1f} Q{hx},{hy-20*s:.1f} {hx+14*s:.1f},{hy-2*s:.1f} Q{hx},{hy-10*s:.1f} {hx-14*s:.1f},{hy-2*s:.1f}" fill="{hair}"/>')
    parts.append(f'<circle cx="{hx-5*s:.1f}" cy="{hy+1*s:.1f}" r="{1.3*s:.1f}" fill="#3a2a22"/><circle cx="{hx+5*s:.1f}" cy="{hy+1*s:.1f}" r="{1.3*s:.1f}" fill="#3a2a22"/>')
    if crown == "gold":
        parts.append(f'<path d="M{hx-12*s:.1f},{hy-10*s:.1f} L{hx-8*s:.1f},{hy-22*s:.1f} L{hx},{hy-12*s:.1f} L{hx+8*s:.1f},{hy-22*s:.1f} L{hx+12*s:.1f},{hy-10*s:.1f} Z" fill="#e8c56b" stroke="#8a6a22" stroke-width="1"/>')
    elif crown == "laurel":
        parts.append(f'<path d="M{hx-16*s:.1f},{hy} Q{hx},{hy-26*s:.1f} {hx+16*s:.1f},{hy}" fill="none" stroke="#3e8f4a" stroke-width="{2*s:.1f}"/>')
    elif crown == "hood":
        parts.append(f'<path d="M{hx-16*s:.1f},{hy+4*s:.1f} Q{hx},{hy-28*s:.1f} {hx+16*s:.1f},{hy+6*s:.1f} L{hx},{hy+8*s:.1f} Z" fill="{robe}"/>')
    return "".join(parts)


def _dog(x, y) -> str:
    return f'''<ellipse cx="{x}" cy="{y}" rx="22" ry="10" fill="#f7f4ee"/>
    <circle cx="{x+16}" cy="{y-8}" r="8" fill="#f7f4ee"/>
    <circle cx="{x+18}" cy="{y-10}" r="1.4" fill="#333"/>
    <path d="M{x-18},{y} q-8,6 -2,10" stroke="#f7f4ee" stroke-width="3" fill="none"/>'''


def _rose(x, y) -> str:
    return f'<circle cx="{x}" cy="{y}" r="7" fill="#d4536a"/><circle cx="{x-3}" cy="{y-2}" r="3" fill="#f2a0ad"/><path d="M{x},{y+7} q2,14 0,22" stroke="#2f7a3a" stroke-width="2" fill="none"/>'


def _cup(x, y, sc=1, fill="#d4ecf5") -> str:
    return f'''<g transform="translate({x},{y}) scale({sc})">
      <path d="M-18,-6 h36 l-6,22 q-12,14 -12,0 q0,14 -12,0 z" fill="{fill}" stroke="#c9a24a" stroke-width="2"/>
      <path d="M-16,-6 q18,-16 32,0" fill="none" stroke="#c9a24a" stroke-width="2"/>
      <rect x="-3" y="16" width="6" height="16" fill="#c9a24a"/>
      <rect x="-12" y="32" width="24" height="5" rx="2" fill="#c9a24a"/>
      <ellipse cx="0" cy="-4" rx="10" ry="4" fill="#7eb6d6" opacity=".85"/>
    </g>'''


def _wand(x, y, sc=1) -> str:
    return f'''<g transform="translate({x},{y}) scale({sc})">
      <rect x="-4" y="-36" width="8" height="74" rx="3" fill="#a86432" stroke="#6b3e1c" stroke-width="1"/>
      <ellipse cx="0" cy="-40" rx="8" ry="5" fill="#2f7a3e"/>
      <path d="M0,-34 C16,-20 14,-4 0,2" fill="#3d9a52"/>
      <path d="M0,-30 C-14,-18 -12,-4 0,0" fill="#267a40"/>
    </g>'''


def _sword(x, y, sc=1) -> str:
    return f'''<g transform="translate({x},{y}) scale({sc})">
      <path d="M0,-46 L7,-8 L0,0 L-7,-8 Z" fill="#e8eef2" stroke="#8aa0b0" stroke-width="1"/>
      <path d="M0,-46 L0,0" stroke="#ffffffaa" stroke-width="1"/>
      <rect x="-14" y="-2" width="28" height="5" rx="1" fill="#c9a24a"/>
      <rect x="-3" y="3" width="6" height="14" fill="#6b4423"/>
      <circle cx="0" cy="20" r="4" fill="#c9a24a"/>
    </g>'''


def _coin(x, y, sc=1) -> str:
    return f'''<g transform="translate({x},{y}) scale({sc})">
      <circle r="22" fill="#e6c15a" stroke="#8a6a1e" stroke-width="3"/>
      <circle r="16" fill="none" stroke="#8a6a1e" stroke-width="1.4"/>
      {_star(0, 0, 11, "#fff6d0")}
    </g>'''


def _pillar(x, y, h, cap, letter) -> str:
    return f'''<rect x="{x}" y="{y}" width="36" height="{h}" fill="#d9d3c7" stroke="#9a9286"/>
    <rect x="{x-4}" y="{y-10}" width="44" height="12" fill="{cap}"/>
    <rect x="{x-4}" y="{y+h}" width="44" height="10" fill="{cap}"/>
    <text x="{x+18}" y="{y+h/2}" text-anchor="middle" font-family="Georgia,serif" font-size="16" fill="#3a342c">{letter}</text>'''


def _tree(x, y, leaf="#2f7a3e") -> str:
    return f'''<rect x="{x-4}" y="{y-30}" width="8" height="34" fill="#6b4423"/>
    <circle cx="{x}" cy="{y-48}" r="22" fill="{leaf}"/>
    <circle cx="{x-12}" cy="{y-36}" r="14" fill="{leaf}"/>
    <circle cx="{x+12}" cy="{y-34}" r="14" fill="{leaf}"/>'''


def _water(y, fill="#2f6f93") -> str:
    return f'<path d="M0,{y} Q40,{y-12} 80,{y} T160,{y} T240,{y} T328,{y} V{AH} H0 Z" fill="{fill}"/>'


_PIPS = {
    1: [(164, 230, 1.7, False)],
    2: [(164, 120, 1.15, False), (164, 340, 1.15, True)],
    3: [(164, 100, 1.05, False), (110, 300, 1.05, False), (218, 300, 1.05, True)],
    4: [(100, 120, 1.0, False), (228, 120, 1.0, False), (100, 330, 1.0, True), (228, 330, 1.0, True)],
    5: [(100, 110, 0.95, False), (228, 110, 0.95, False), (164, 230, 0.95, False), (100, 340, 0.95, True), (228, 340, 0.95, True)],
    6: [(110, 90, 0.9, False), (218, 90, 0.9, False), (110, 230, 0.9, False), (218, 230, 0.9, False), (110, 360, 0.9, True), (218, 360, 0.9, True)],
    7: [(110, 80, 0.82, False), (218, 80, 0.82, False), (110, 190, 0.82, False), (218, 190, 0.82, False), (164, 250, 0.82, False), (110, 360, 0.82, True), (218, 360, 0.82, True)],
    8: [(110, 70, 0.78, False), (218, 70, 0.78, False), (110, 170, 0.78, False), (218, 170, 0.78, False), (110, 270, 0.78, True), (218, 270, 0.78, True), (110, 370, 0.78, True), (218, 370, 0.78, True)],
    9: [(110, 64, 0.72, False), (218, 64, 0.72, False), (110, 150, 0.72, False), (218, 150, 0.72, False), (164, 210, 0.72, False), (110, 280, 0.72, True), (218, 280, 0.72, True), (110, 370, 0.72, True), (218, 370, 0.72, True)],
    10: [(90, 60, 0.68, False), (164, 60, 0.68, False), (238, 60, 0.68, False), (120, 145, 0.68, False), (208, 145, 0.68, False), (120, 300, 0.68, True), (208, 300, 0.68, True), (90, 390, 0.68, True), (164, 390, 0.68, True), (238, 390, 0.68, True)],
}

_SUIT_FN = {"Wands": _wand, "Cups": _cup, "Swords": _sword, "Pentacles": _coin}
_SUIT_WASH = {"Wands": ("#f6e2c4", "#f3d2a4"), "Cups": ("#d5ebf6", "#c5e0f2"), "Swords": ("#e7eef3", "#d5e0ea"), "Pentacles": ("#f8efd0", "#f0e0b0")}
_RANK_N = {"Ace": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10}
_RANK_IDX = {"Ace": "A", "Two": "2", "Three": "3", "Four": "4", "Five": "5", "Six": "6", "Seven": "7", "Eight": "8", "Nine": "9", "Ten": "10",
             "Page": "P", "Knight": "Kn", "Queen": "Q", "King": "K"}
_COURT = {
    "Page": ("#e7d3a8", None, 150),
    "Knight": ("#8ea0b8", None, 160),
    "Queen": ("#c4556a", "gold", 168),
    "King": ("#3d4f86", "gold", 176),
}
_COURT_GROUND = {"Wands": "#e7c49a", "Cups": "#b7d4ea", "Swords": "#c5d0dc", "Pentacles": "#e6d39a"}


def _pips(suit: str, n: int) -> str:
    fn = _SUIT_FN[suit]
    top, bot = _SUIT_WASH[suit]
    parts = [_sky(top, bot)]
    parts.append(f'<rect x="18" y="18" width="{AW-36}" height="{AH-36}" fill="none" stroke="#c9a24a55" stroke-width="1"/>')
    for x, y, sc, inv in _PIPS[n]:
        # symbol functions are centered on their own origin; pips stored as top-left-ish centers
        rot = f' transform="rotate(180 {x} {y})"' if inv else ""
        # wrap: translate is inside symbol, so rotate around center by grouping
        parts.append(f'<g{rot}>{fn(x, y, sc)}</g>')
    return "".join(parts)


def _court(suit: str, rank: str) -> str:
    robe, crown, h = _COURT[rank]
    top, bot = _SUIT_WASH[suit]
    fn = _SUIT_FN[suit]
    horse = ""
    if rank == "Knight":
        horse = f'<ellipse cx="168" cy="360" rx="70" ry="22" fill="#6b5344"/><ellipse cx="230" cy="330" rx="16" ry="12" fill="#6b5344"/><path d="M246,328 q16,-8 8,6" stroke="#6b5344" stroke-width="4" fill="none"/>'
    return _sky(top, bot) + _ground(390, _COURT_GROUND[suit]) + f'<g opacity=".18">{fn(164, 230, 3.2)}</g>' + horse + _figure(150, 420, h, robe, crown=crown, arm="up" if rank in ("Page", "Knight") else "down") + _tree(40, 430, "#2f6b3a") + _tree(290, 440, "#2f6b3a")


def _majors() -> dict:
    A = AH
    return {
        "The Fool": _sky("#79c6ea", "#f6e7b2") + _sun(250, 78, 36) + _mountain("#7fbf8a") +
            '<path d="M40,250 L150,250 L150,468 L20,468 Z" fill="#c4a574"/>' +
            _figure(120, 430, 168, "#f4e1a8", arm="up", pack=True) + _dog(70, 448) + _rose(200, 400) +
            '<rect x="78" y="250" width="22" height="16" rx="3" fill="#d98a3a"/>',
        "The Magician": _sky("#f7e7c0", "#f3d7b0") + _ground(400, "#d9c39a") +
            '<rect x="70" y="250" width="190" height="16" rx="3" fill="#6b4423"/>' +
            _wand(100, 250, 0.55) + _cup(150, 236, 0.5) + _sword(200, 248, 0.5) + _coin(246, 236, 0.45) +
            _figure(164, 450, 180, "#b4333a", arm="up") +
            '<path d="M164,78 Q184,98 164,118 Q144,98 164,78" fill="none" stroke="#e8c56b" stroke-width="3"/>',
        "The High Priestess": _sky("#1b2748", "#3d5d8a") + _moon(164, 70, 28) +
            _pillar(40, 120, 250, "#222", "B") + _pillar(252, 120, 250, "#f4f1ea", "J") +
            '<path d="M76,140 Q164,80 252,140 L252,300 Q164,250 76,300 Z" fill="#f7f4ee" opacity=".85"/>' +
            _figure(164, 450, 190, "#2c3e73", crown="hood") +
            '<rect x="146" y="300" width="36" height="28" rx="2" fill="#f4efe4" stroke="#c9a24a"/>',
        "The Empress": _sky("#f6d5c4", "#f8e7c4") + _ground(420, "#7dae6a") + _tree(50, 450, "#2f7a3e") + _tree(280, 460, "#3d8f4e") +
            _figure(164, 440, 175, "#f2f6f0", crown="laurel") +
            '<circle cx="164" cy="250" r="16" fill="none" stroke="#c9a24a" stroke-width="2"/><circle cx="164" cy="250" r="6" fill="#c9a24a"/>' +
            _wheat(250, 400),
        "The Emperor": _sky("#f0c9a4", "#e7b8a0") + _mountain("#b9a48c") +
            '<rect x="90" y="250" width="150" height="90" rx="6" fill="#8d3b3b"/>' +
            _figure(164, 430, 175, "#9a3030", crown="gold", arm="out") +
            '<path d="M120,300 q20,-16 40,0" fill="none" stroke="#e8c56b" stroke-width="3"/>' +
            '<path d="M170,300 q20,-16 40,0" fill="none" stroke="#e8c56b" stroke-width="3"/>',
        "The Hierophant": _sky("#f3e0c0", "#e7d3b4") +
            _pillar(36, 140, 240, "#c9a24a", "") + _pillar(256, 140, 240, "#c9a24a", "") +
            _figure(164, 400, 180, "#c4552a", crown="gold") +
            '<g transform="translate(70,400)">' + _keys() + '</g>' +
            _figure(90, 460, 90, "#d9c7a4") + _figure(240, 460, 90, "#d9c7a4"),
        "The Lovers": _sky("#b9ddf5", "#f7e1c4") + _sun(164, 40, 22) +
            '<path d="M140,50 L164,90 L188,50" fill="#f7f4ee" stroke="#e8c56b"/>' +
            _figure(100, 450, 160, "#f4efe8") + _figure(230, 450, 160, "#e7b7c4") +
            _tree(40, 470, "#2f7a3e") + '<path d="M300,470 q-20,-80 10,-120" stroke="#6b4423" stroke-width="4" fill="none"/><path d="M310,360 q20,-10 8,8" fill="#c0392b"/>',
        "The Chariot": _sky("#1d2a4a", "#3e5c8a") +
            '<rect x="70" y="180" width="190" height="120" rx="8" fill="#1d2a4a" stroke="#e8c56b" stroke-width="3"/>' +
            _star(100, 210, 8) + _star(164, 200, 10) + _star(230, 210, 8) +
            _figure(164, 300, 120, "#e8eef6", crown="gold") +
            '<ellipse cx="110" cy="400" rx="36" ry="16" fill="#f7f4ee"/><ellipse cx="220" cy="400" rx="36" ry="16" fill="#2a2a2a"/>' +
            '<circle cx="90" cy="450" r="22" fill="#c9a24a"/><circle cx="240" cy="450" r="22" fill="#c9a24a"/>',
        "Strength": _sky("#f8e7c8", "#f3d2a8") + _ground(430, "#e7d3a4") +
            _figure(120, 440, 175, "#f7f4ee", crown=None, arm="out") +
            '<ellipse cx="210" cy="360" rx="48" ry="28" fill="#e0b44a"/><circle cx="250" cy="340" r="18" fill="#e0b44a"/><circle cx="258" cy="336" r="2" fill="#5a3b16"/>' +
            '<path d="M120,70 Q140,90 120,110 Q100,90 120,70" fill="none" stroke="#e8c56b" stroke-width="3"/>',
        "The Hermit": _sky("#2c3a4e", "#6d7f90") + _mountain("#9aa8b4") +
            _figure(164, 450, 190, "#4d5d70", crown="hood", arm="up") +
            '<circle cx="200" cy="150" r="14" fill="#ffe08a" stroke="#e8c56b" stroke-width="2"/>' +
            '<path d="M200,164 v26" stroke="#6b4423" stroke-width="3"/>',
        "Wheel of Fortune": _sky("#16345c", "#3e6ea5") +
            '<circle cx="164" cy="240" r="90" fill="none" stroke="#e8c56b" stroke-width="10"/>' +
            '<circle cx="164" cy="240" r="60" fill="none" stroke="#e8c56b" stroke-width="2"/>' +
            _star(164, 240, 18, "#fff6c8") +
            '<text x="164" y="160" text-anchor="middle" font-family="Georgia" font-size="18" fill="#f6e7b8">T A R O</text>' +
            _eagle(70, 80) + _lion_small(250, 90) + _bull(60, 360) + _angel_small(250, 350),
        "Justice": _sky("#efe4f4", "#f7f1e6") + _pillar(30, 80, 300, "#c9a24a", "") + _pillar(262, 80, 300, "#c9a24a", "") +
            _figure(164, 450, 185, "#9a3048", crown="gold") +
            _sword(230, 200, 0.8) + _scales(90, 200),
        "The Hanged Man": _sky("#9fd0e8", "#d5ebe8") +
            '<path d="M70,70 H260 M164,70 V120" stroke="#6b4423" stroke-width="8"/>' +
            '<g transform="rotate(180 164 280)">' + _figure(164, 360, 160, "#2f6f93", hair="#d8c07a") + '</g>' +
            '<circle cx="164" cy="150" r="22" fill="none" stroke="#e8c56b" stroke-width="3"/>',
        "Death": _sky("#f3d7a4", "#e7e0d4") + _sun(250, 60, 26) +
            '<rect x="40" y="80" width="18" height="70" fill="#d9d3c7"/><rect x="270" y="90" width="18" height="60" fill="#d9d3c7"/>' +
            _figure(150, 450, 185, "#1c1c1c", skin="#e8e4dc", hair="#111", arm="out") +
            '<rect x="200" y="160" width="6" height="90" fill="#222"/><path d="M206,160 h36 v22 h-36 z" fill="#f4f1ea"/>' +
            _rose(80, 400),
        "Temperance": _sky("#d7ecf6", "#f7e7c8") + _water(400, "#7eb0c8") +
            '<path d="M250,420 L300,250 L328,250 L328,468 L230,468 Z" fill="#d9c39a"/>' +
            _figure(150, 430, 185, "#f7f4ee", wings=True, arm="out") +
            _cup(70, 250, 0.7) + _cup(250, 280, 0.7) +
            '<path d="M100,250 C160,200 200,300 250,270" fill="none" stroke="#9fd0e8" stroke-width="3"/>',
        "The Devil": _sky("#2a120e", "#5a221c") +
            '<circle cx="164" cy="120" r="28" fill="#1a1a1a" stroke="#e8c56b" stroke-width="3"/>' +
            _star(164, 120, 14, "#c9a24a") +
            _figure(164, 300, 120, "#6b2218", crown=None, arm="up") +
            _figure(90, 460, 130, "#c4552a") + _figure(240, 460, 130, "#c4552a") +
            '<path d="M90,390 q74,20 150,0" fill="none" stroke="#e8c56b" stroke-width="2"/>',
        "The Tower": _sky("#141426", "#3a2a4a") +
            '<path d="M200,40 L230,120 L190,130 L250,468 L120,468 L150,140 L110,120 Z" fill="#6a646c"/>' +
            '<path d="M40,20 L210,200" stroke="#fff6c8" stroke-width="6"/>' +
            '<path d="M150,20 L164,0 L178,20 L164,16 Z" fill="#e8c56b"/>' +
            '<circle cx="80" cy="300" r="12" fill="#f3d0b0"/><circle cx="270" cy="250" r="12" fill="#f3d0b0"/>' +
            '<rect x="155" y="200" width="16" height="20" fill="#f6d56a"/><rect x="155" y="250" width="16" height="20" fill="#f6d56a"/>',
        "The Star": _sky("#0e1b3a", "#1d3e6e") + _water(430, "#1d4e6e") +
            _star(60, 50, 8) + _star(120, 36, 6) + _star(200, 48, 7) + _star(270, 30, 5) +
            _star(164, 70, 18) +
            _figure(150, 430, 170, "#f7f4ee", hair="#e8c56b", arm="out") +
            _cup(70, 340, 0.6) + _cup(230, 360, 0.6) + _tree(290, 450, "#1d4a34"),
        "The Moon": _sky("#141833", "#2a3560") + _moon(200, 70, 36) +
            '<rect x="40" y="160" width="28" height="150" fill="#8d9098"/><rect x="260" y="150" width="28" height="160" fill="#8d9098"/>' +
            '<path d="M164,200 V420" stroke="#f4efc8" stroke-width="3" stroke-dasharray="6 6"/>' +
            _dog(80, 400) + '<ellipse cx="250" cy="400" rx="26" ry="12" fill="#6a6e78"/>' +
            '<ellipse cx="164" cy="450" rx="20" ry="10" fill="#c9a24a"/>' + _water(430, "#1a3058"),
        "The Sun": _sky("#fff3c4", "#ffe08a") + _sun(200, 80, 48) +
            '<rect x="0" y="300" width="328" height="20" fill="#e7d3a4"/>' +
            '<circle cx="40" cy="250" r="16" fill="#e0b44a"/><circle cx="80" cy="250" r="16" fill="#e0b44a"/><circle cx="120" cy="250" r="16" fill="#e0b44a"/>' +
            '<circle cx="200" cy="250" r="16" fill="#e0b44a"/><circle cx="240" cy="250" r="16" fill="#e0b44a"/><circle cx="280" cy="250" r="16" fill="#e0b44a"/>' +
            _figure(150, 450, 150, "#f7f4ee") +
            '<ellipse cx="220" cy="400" rx="40" ry="16" fill="#f4f1ea"/><circle cx="255" cy="384" r="10" fill="#f4f1ea"/>',
        "Judgement": _sky("#d7e6f4", "#f7f1e4") +
            '<path d="M164,30 L190,80 L138,80 Z" fill="#f7f4ee"/>' +
            '<rect x="158" y="80" width="12" height="40" fill="#e8c56b"/>' +
            '<path d="M200,70 q30,10 10,24 q-20,-6 -10,-24" fill="#f7f4ee"/>' +
            '<rect x="50" y="320" width="50" height="70" fill="#6b5344"/><rect x="140" y="300" width="50" height="80" fill="#6b5344"/><rect x="230" y="330" width="50" height="64" fill="#6b5344"/>' +
            _figure(75, 360, 80, "#f7f4ee", arm="up") + _figure(165, 340, 90, "#e7d3c4", arm="up") + _figure(255, 365, 78, "#f7f4ee", arm="up"),
        "The World": _sky("#12324a", "#1e5a4a") +
            '<ellipse cx="164" cy="240" rx="70" ry="110" fill="none" stroke="#3e8f4a" stroke-width="16"/>' +
            '<ellipse cx="164" cy="240" rx="70" ry="110" fill="none" stroke="#e8c56b" stroke-width="3"/>' +
            _figure(164, 340, 160, "#c9a0d4", crown=None) +
            '<path d="M120,250 Q164,200 208,250" fill="none" stroke="#f2e6f6" stroke-width="6"/>' +
            _eagle(40, 40) + _lion_small(260, 40) + _bull(40, 400) + _angel_small(260, 390),
    }


def _wheat(x, y) -> str:
    return f'<g stroke="#e0b44a" stroke-width="2" fill="none"><path d="M{x},{y} v-40"/><path d="M{x},{y-10} l-8,-8"/><path d="M{x},{y-18} l8,-8"/><path d="M{x},{y-26} l-8,-8"/><path d="M{x},{y-34} l8,-8"/></g>'


def _keys() -> str:
    return '<circle cx="0" cy="0" r="8" fill="none" stroke="#e8c56b" stroke-width="3"/><path d="M8,0 h20 v6 h-6 v6" stroke="#e8c56b" stroke-width="3" fill="none"/><circle cx="40" cy="16" r="7" fill="none" stroke="#e8c56b" stroke-width="3"/><path d="M47,16 h18" stroke="#e8c56b" stroke-width="3"/>'


def _scales(x, y) -> str:
    return f'''<g stroke="#c9a24a" stroke-width="2" fill="none">
      <path d="M{x},{y} v36 M{x-22},{y+8} h44"/>
      <path d="M{x-22},{y+8} q10,16 0,22 q-10,-6 0,-22"/>
      <path d="M{x+22},{y+8} q10,16 0,22 q-10,-6 0,-22"/>
    </g>'''


def _eagle(x, y) -> str:
    return f'<path d="M{x},{y+10} q20,-20 40,0 q-20,6 -40,0" fill="#e8eef2"/>'


def _lion_small(x, y) -> str:
    return f'<ellipse cx="{x}" cy="{y}" rx="16" ry="10" fill="#e0b44a"/><circle cx="{x+14}" cy="{y-6}" r="7" fill="#e0b44a"/>'


def _bull(x, y) -> str:
    return f'<ellipse cx="{x}" cy="{y}" rx="18" ry="10" fill="#6b4423"/><path d="M{x-8},{y-8} l-8,-8 M{x+4},{y-8} l8,-8" stroke="#6b4423" stroke-width="2"/>'


def _angel_small(x, y) -> str:
    return f'<circle cx="{x}" cy="{y}" r="8" fill="#f3d0b0"/><path d="M{x-16},{y+4} q16,-14 32,0" fill="#f7f4ee"/>'


def _art_for(name: str) -> tuple[str, str, str]:
    """Return art svg, corner index, title."""
    majors = _majors()
    if name in majors:
        i = list(majors).index(name)
        roman = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"][i]
        return majors[name], roman, name.upper()
    rank, suit = name.split(" of ")
    if rank in _COURT:
        return _court(suit, rank), _RANK_IDX[rank], name.upper()
    return _pips(suit, _RANK_N[rank]), _RANK_IDX[rank], name.upper()


def _tiny_suit(suit: str) -> str:
    return {"Wands": _wand(0, 8, 0.28), "Cups": _cup(0, 4, 0.28), "Swords": _sword(0, 10, 0.28), "Pentacles": _coin(0, 6, 0.28)}.get(suit, "")


def render(name: str) -> str:
    art, idx, title = _art_for(name)
    suit = name.split(" of ")[1] if " of " in name else ""
    tiny = _tiny_suit(suit)
    size = 15 if len(title) > 18 else 18 if len(title) > 14 else 22
    # fix figure() unexpected pack kw if I passed it — I used pack=False in fool. Need to allow **ignore.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">
<title>{_esc(name)}</title>
<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff6d2"/><stop offset=".45" stop-color="#e0b44a"/><stop offset="1" stop-color="#8a6420"/>
  </linearGradient>
  <linearGradient id="night" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#241838"/><stop offset="1" stop-color="#120c20"/>
  </linearGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="1" stdDeviation="1.2" flood-color="#000" flood-opacity=".25"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#night)"/>
<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="16" fill="url(#gold)"/>
<rect x="18" y="18" width="{W-36}" height="{H-36}" rx="12" fill="#f6f0e4"/>
<g transform="translate(36,52)" filter="url(#soft)">{art}</g>
<rect x="36" y="52" width="{AW}" height="{AH}" fill="none" stroke="#c9a24a" stroke-width="1.25"/>
<g font-family="Georgia, 'Times New Roman', serif" fill="#1b1433">
  <text x="58" y="44" font-size="16" font-weight="700">{_esc(idx)}</text>
  <g transform="translate(58,78)">{tiny}</g>
  <g transform="translate({W-58},{H-78}) rotate(180)">
    <text x="0" y="0" font-size="16" font-weight="700" text-anchor="end">{_esc(idx)}</text>
  </g>
</g>
<rect x="46" y="538" width="308" height="46" rx="6" fill="#1b1433"/>
<text x="200" y="568" text-anchor="middle" font-family="Georgia, 'Palatino Linotype', serif" font-size="{size}" letter-spacing="1.4" fill="#f6e7b8">{_esc(title)}</text>
<path d="M28,28 h18 M28,28 v18 M{W-28},28 h-18 M{W-28},28 v18 M28,{H-28} h18 M28,{H-28} v-18 M{W-28},{H-28} h-18 M{W-28},{H-28} v-18" stroke="#e0b44a" stroke-width="1.4" fill="none"/>
</svg>'''


# figure() was defined with a fixed signature. Fool scene calls pack=False. Patch by wrapping.
_figure_orig = _figure


def _figure(x, y, h, robe, skin="#f3d0b0", hair="#2c2118", arm="down", crown=None, wings=False, pack=False):  # noqa: F811
    svg = _figure_orig(x, y, h, robe, skin=skin, hair=hair, arm=arm, crown=crown, wings=wings)
    if pack:
        svg += f'<rect x="{x-28}" y="{y-h+70}" width="20" height="14" rx="2" fill="#d98a3a"/>'
    return svg


_CACHE: dict[str, str] = {}


def svg_for(slug: str) -> str | None:
    slug = slug[:-4] if slug.endswith(".svg") else slug
    if slug in _CACHE:
        return _CACHE[slug]
    from .tarot import deck
    for c in deck():
        if card_slug(c["name"]) == slug:
            # rebuild majors so the patched _figure is used
            svg = render(c["name"])
            _CACHE[slug] = svg
            return svg
    return None

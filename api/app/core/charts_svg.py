"""SVG chart renderers: North Indian (diamond), South Indian (fixed signs), East Indian, Western wheel."""
from __future__ import annotations
import math
from .ephem import SIGNS

ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra",
        "Ketu": "Ke", "Uranus": "Ur", "Neptune": "Ne", "Pluto": "Pl", "Ascendant": "As"}
GLYPH = {"Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
         "Neptune": "♆", "Pluto": "♇", "Rahu": "☊", "Ketu": "☋"}
SIGN_GLYPH = "♈♉♊♋♌♍♎♏♐♑♒♓"
STYLE = '<style>.ln{stroke:#7a1f2b;stroke-width:2;fill:none}.t{font:600 13px system-ui,sans-serif;fill:#3b0d14}.s{font:11px system-ui;fill:#b05a00}.r{fill:#c0392b}</style>'

def _lab(p): return ABBR.get(p["name"], p["name"][:2]) + ("(R)" if p.get("retrograde") and p["name"] not in ("Rahu", "Ketu") else "")

def north_indian(asc_sign: int, planets: list[dict], size: int = 400, title: str = ""):
    """planets: [{'name','sign'(index 0-11),'retrograde'}]. House 1 at top diamond."""
    S = size; h = S / 2
    centers = [(h, h * 0.5), (h * 0.5, h * 0.22), (h * 0.22, h * 0.5), (h * 0.5, h), (h * 0.22, h * 1.5), (h * 0.5, h * 1.78),
               (h, h * 1.5), (h * 1.5, h * 1.78), (h * 1.78, h * 1.5), (h * 1.5, h), (h * 1.78, h * 0.5), (h * 1.5, h * 0.22)]
    signpos = [(h, h * 0.82), (h * 0.5, h * 0.42), (h * 0.42, h * 0.5), (h * 0.82, h), (h * 0.42, h * 1.5), (h * 0.5, h * 1.58),
               (h, h * 1.18), (h * 1.5, h * 1.58), (h * 1.58, h * 1.5), (h * 1.18, h), (h * 1.58, h * 0.5), (h * 1.5, h * 0.42)]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="North Indian chart {title}">', STYLE,
           f'<rect x="1" y="1" width="{S-2}" height="{S-2}" class="ln" fill="#fffaf0"/>',
           f'<line x1="0" y1="0" x2="{S}" y2="{S}" class="ln"/><line x1="{S}" y1="0" x2="0" y2="{S}" class="ln"/>',
           f'<polygon points="{h},0 {S},{h} {h},{S} 0,{h}" class="ln"/>']
    for i in range(12):
        sign = (asc_sign + i) % 12
        x, y = signpos[i]; out.append(f'<text x="{x:.0f}" y="{y:.0f}" class="s" text-anchor="middle">{sign + 1}</text>')
        ps = [p for p in planets if p["sign"] == sign]
        cx, cy = centers[i]
        if i == 0: ps = [{"name": "Ascendant"}] + ps
        for k, p in enumerate(ps):
            cls = "t r" if p.get("retrograde") and p["name"] not in ("Rahu", "Ketu") else "t"
            out.append(f'<text x="{cx:.0f}" y="{cy - 8 * (len(ps) - 1) + 16 * k + 4:.0f}" class="{cls}" text-anchor="middle">{_lab(p)}</text>')
    out.append("</svg>")
    return "".join(out)

def south_indian(asc_sign: int, planets: list[dict], size: int = 400, title: str = ""):
    S = size; c = S / 4
    grid = {11: (0, 0), 0: (1, 0), 1: (2, 0), 2: (3, 0), 3: (3, 1), 4: (3, 2), 5: (3, 3), 6: (2, 3), 7: (1, 3), 8: (0, 3), 9: (0, 2), 10: (0, 1)}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="South Indian chart {title}">', STYLE]
    for s, (gx, gy) in grid.items():
        x, y = gx * c, gy * c
        fill = "#ffe9c7" if s == asc_sign else "#fffaf0"
        out.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" class="ln" fill="{fill}"/>')
        out.append(f'<text x="{x + 5}" y="{y + 14}" class="s">{SIGNS[s][:3]}</text>')
        ps = [p for p in planets if p["sign"] == s]
        if s == asc_sign: ps = [{"name": "Ascendant"}] + ps
        for k, p in enumerate(ps):
            cls = "t r" if p.get("retrograde") and p["name"] not in ("Rahu", "Ketu") else "t"
            out.append(f'<text x="{x + c / 2}" y="{y + 32 + 16 * k}" class="{cls}" text-anchor="middle">{_lab(p)}</text>')
    out.append(f'<text x="{S/2}" y="{S/2}" class="t" text-anchor="middle">{title or "Rasi"}</text></svg>')
    return "".join(out)

def east_indian(asc_sign: int, planets: list[dict], size: int = 400, title: str = ""):
    """East Indian (Bengal/Odisha) style: 3x3 grid, Aries top-centre, signs run anticlockwise, corners split."""
    S = size; c = S / 3
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="East Indian chart">', STYLE,
           f'<rect x="1" y="1" width="{S-2}" height="{S-2}" class="ln" fill="#fffaf0"/>']
    for k in (1, 2):
        out.append(f'<line x1="{k*c}" y1="0" x2="{k*c}" y2="{S}" class="ln"/><line x1="0" y1="{k*c}" x2="{S}" y2="{k*c}" class="ln"/>')
    for (x0, y0, x1, y1) in [(0, 0, c, c), (S, 0, 2 * c, c), (0, S, c, 2 * c), (S, S, 2 * c, 2 * c)]:
        out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" class="ln"/>')
    pos = {0: (1.5, 0.5), 11: (0.75, 0.3), 10: (0.3, 0.75), 9: (0.5, 1.5), 8: (0.3, 2.25), 7: (0.75, 2.7), 6: (1.5, 2.5),
           5: (2.25, 2.7), 4: (2.7, 2.25), 3: (2.5, 1.5), 2: (2.7, 0.75), 1: (2.25, 0.3)}
    for s, (gx, gy) in pos.items():
        x, y = gx * c, gy * c
        ps = [p for p in planets if p["sign"] == s]
        if s == asc_sign: ps = [{"name": "Ascendant"}] + ps
        out.append(f'<text x="{x:.0f}" y="{y - 14:.0f}" class="s" text-anchor="middle">{SIGNS[s][:3]}</text>')
        for k, p in enumerate(ps):
            out.append(f'<text x="{x:.0f}" y="{y + 2 + 14 * k:.0f}" class="t" text-anchor="middle">{_lab(p)}</text>')
    out.append("</svg>")
    return "".join(out)

def western_wheel(asc: float, cusps: list[float], planets: list[dict], size: int = 460):
    S = size; C = S / 2; R1, R2, R3 = C - 6, C - 40, C - 110
    def pt(lon, r):
        a = math.radians(180 - (lon - asc))
        return C + r * math.cos(a), C - r * math.sin(a)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="Western natal wheel">', STYLE,
           f'<circle cx="{C}" cy="{C}" r="{R1}" class="ln" fill="#fffaf0"/><circle cx="{C}" cy="{C}" r="{R2}" class="ln"/><circle cx="{C}" cy="{C}" r="{R3}" class="ln"/>']
    for s in range(12):
        x1, y1 = pt(s * 30, R1); x2, y2 = pt(s * 30, R2)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="ln"/>')
        tx, ty = pt(s * 30 + 15, (R1 + R2) / 2)
        out.append(f'<text x="{tx:.1f}" y="{ty + 6:.1f}" text-anchor="middle" style="font:18px serif;fill:#7a1f2b">{SIGN_GLYPH[s]}</text>')
    for i, cpos in enumerate(cusps):
        x1, y1 = pt(cpos, R2); x2, y2 = pt(cpos, 0 if i in (0, 3, 6, 9) else R3)
        w = 2.5 if i in (0, 9) else 1
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#b05a00" stroke-width="{w}"/>')
        mid = cpos + ((cusps[(i + 1) % 12] - cpos) % 360) / 2
        tx, ty = pt(mid, R3 - 14); out.append(f'<text x="{tx:.1f}" y="{ty + 4:.1f}" class="s" text-anchor="middle">{i + 1}</text>')
    placed = []
    for p in sorted(planets, key=lambda p: p["longitude"]):
        r = R2 - 18
        for q in placed:
            if abs(((p["longitude"] - q[0] + 180) % 360) - 180) < 7: r = min(r, q[1] - 18)
        placed.append((p["longitude"], r))
        x, y = pt(p["longitude"], r)
        out.append(f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" style="font:16px serif;fill:{"#c0392b" if p.get("retrograde") else "#3b0d14"}">{GLYPH.get(p["name"], p["name"][:2])}</text>')
    out.append("</svg>")
    return "".join(out)


def sudarshan_chakra_svg(asc_sign: int, moon_sign: int, sun_sign: int, planets: list[dict], size: int = 560, title: str = "Sudarshan Chakra") -> str:
    """Renders the authentic 3-ring concentric Sudarshan Chakra per Brihat Parashara Hora Shastra.
    
    - Inner ring: Janma Lagna Kundli
    - Middle ring: Chandra Lagna Kundli
    - Outer ring: Surya Lagna Kundli
    - 12 radial sectors representing Houses 1 to 12.
    """
    S = size
    C = S / 2.0
    R0 = S * 0.08   # Center hub
    R1 = S * 0.20   # Lagna ring outer
    R2 = S * 0.33   # Chandra ring outer
    R3 = S * 0.46   # Surya ring outer
    
    planets_by_sign = {}
    for p in planets:
        s = p["sign"]
        planets_by_sign.setdefault(s, []).append(p)
        
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="{title}">',
        '<style>',
        '.sc-bg{fill:#fffdf7;stroke:#7a1f2b;stroke-width:2}',
        '.sc-ring{fill:none;stroke:#b05a00;stroke-width:1.5}',
        '.sc-spoke-main{stroke:#7a1f2b;stroke-width:1.2}',
        '.sc-hnum{font:bold 11px system-ui,sans-serif;fill:#8e1b3a}',
        '.sc-sign{font:10px system-ui,sans-serif;fill:#b05a00}',
        '.sc-planet{font:bold 11px system-ui,sans-serif;fill:#3b0d14}',
        '.sc-title{font:bold 14px serif;fill:#7a1f2b}',
        '</style>',
        f'<rect width="{S}" height="{S}" fill="#fffaf2"/>',
        f'<circle cx="{C}" cy="{C}" r="{R3}" fill="#fffdfa" stroke="#7a1f2b" stroke-width="2"/>',
        f'<circle cx="{C}" cy="{C}" r="{R2}" fill="#fffbf5" stroke="#b05a00" stroke-width="1.5"/>',
        f'<circle cx="{C}" cy="{C}" r="{R1}" fill="#fff8ee" stroke="#b05a00" stroke-width="1.5"/>',
        f'<circle cx="{C}" cy="{C}" r="{R0}" fill="#faecd6" stroke="#7a1f2b" stroke-width="1.5"/>',
        f'<text x="{C}" y="{C - 4}" text-anchor="middle" class="sc-title">ॐ</text>',
        f'<text x="{C}" y="{C + 11}" text-anchor="middle" style="font:bold 8px system-ui;fill:#7a1f2b">SUDARSHAN</text>'
    ]
    
    # 12 sectors radiating counter-clockwise from Top (-90 deg)
    for h in range(12):
        spoke_deg = -90.0 - 15.0 - (h * 30.0)
        rad = math.radians(spoke_deg)
        x0, y0 = C + R0 * math.cos(rad), C + R0 * math.sin(rad)
        x3, y3 = C + R3 * math.cos(rad), C + R3 * math.sin(rad)
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x3:.1f}" y2="{y3:.1f}" class="sc-spoke-main"/>')
        
        mid_deg = -90.0 - (h * 30.0)
        mid_rad = math.radians(mid_deg)
        
        # Outer house number
        hx = C + (R3 + 12) * math.cos(mid_rad)
        hy = C + (R3 + 12) * math.sin(mid_rad) + 4
        out.append(f'<text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" class="sc-hnum">H{h + 1}</text>')
        
        # 1. Inner Ring (Janma Lagna)
        s_in = (asc_sign + h) % 12
        sx = C + (R0 + 12) * math.cos(mid_rad)
        sy = C + (R0 + 12) * math.sin(mid_rad) + 3
        out.append(f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" class="sc-sign">{SIGNS[s_in][:3]}</text>')
        pls_in = planets_by_sign.get(s_in, [])
        if pls_in:
            pl_str = " ".join(_lab(p) for p in pls_in)
            px = C + (R1 - 10) * math.cos(mid_rad)
            py = C + (R1 - 10) * math.sin(mid_rad) + 4
            out.append(f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" class="sc-planet">{pl_str}</text>')
            
        # 2. Middle Ring (Chandra Kundli)
        s_mid = (moon_sign + h) % 12
        smx = C + (R1 + 14) * math.cos(mid_rad)
        smy = C + (R1 + 14) * math.sin(mid_rad) + 3
        out.append(f'<text x="{smx:.1f}" y="{smy:.1f}" text-anchor="middle" class="sc-sign">{SIGNS[s_mid][:3]}</text>')
        pls_mid = planets_by_sign.get(s_mid, [])
        if pls_mid:
            pl_str = " ".join(_lab(p) for p in pls_mid)
            pmx = C + (R2 - 12) * math.cos(mid_rad)
            pmy = C + (R2 - 12) * math.sin(mid_rad) + 4
            out.append(f'<text x="{pmx:.1f}" y="{pmy:.1f}" text-anchor="middle" class="sc-planet">{pl_str}</text>')
            
        # 3. Outer Ring (Surya Kundli)
        s_out = (sun_sign + h) % 12
        sox = C + (R2 + 14) * math.cos(mid_rad)
        soy = C + (R2 + 14) * math.sin(mid_rad) + 3
        out.append(f'<text x="{sox:.1f}" y="{soy:.1f}" text-anchor="middle" class="sc-sign">{SIGNS[s_out][:3]}</text>')
        pls_out = planets_by_sign.get(s_out, [])
        if pls_out:
            pl_str = " ".join(_lab(p) for p in pls_out)
            pox = C + (R3 - 12) * math.cos(mid_rad)
            poy = C + (R3 - 12) * math.sin(mid_rad) + 4
            out.append(f'<text x="{pox:.1f}" y="{poy:.1f}" text-anchor="middle" class="sc-planet">{pl_str}</text>')
            
    out.append("</svg>")
    return "".join(out)


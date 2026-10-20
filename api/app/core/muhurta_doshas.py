"""Muhurta doshas & checks drawn from Muhurta Chintamani (Venkateshwar Press ed., 1906) and Kalaprakasika (1917):
Panchaka (Moon in Dhanishta 2nd half .. Revati) and its weekday types, Panchaka-rahita muhurta (the
tithi+vara+nakshatra+lagna remainder test), Bhadra (Vishti) residence by Moon sign, Dagdha tithi,
Krakacha & Samvartaka yogas, Gand-mool nakshatras, detailed Tarabala and Chandrabala with remedies.
All text is our own paraphrase."""
from __future__ import annotations
from datetime import date as Date
from .ephem import fmt, make_tz, ascendant, NAKSHATRAS
from .panchang import (day_events, weekday_of, tithi_at, nak_at, karana_at, moon_sid, TITHIS)

PANCHAKA_TYPES = {0: ("Roga Panchaka", "health complaints; avoid starting treatment-sensitive or ceremonial work"),
                  1: ("Raja Panchaka", "considered mild; government/authority matters favoured"),
                  2: ("Agni Panchaka", "risk of fire; avoid construction, machinery and fire-related work"),
                  5: ("Chora Panchaka", "risk of theft/loss; avoid travel and trade"),
                  6: ("Mrityu Panchaka", "most severe; avoid all risky undertakings")}
PANCHAKA_AVOID = ["collecting fuel/wood", "building a roof", "making a cot/bed", "travel to the south", "cremation without the prescribed remedy (five effigies)"]
RAHITA = {1: "Mrityu", 2: "Agni", 4: "Raja", 6: "Chora", 8: "Roga"}
DAGDHA = {0: 11, 1: 10, 2: 4, 3: 2, 4: 5, 5: 7, 6: 8}  # weekday -> tithi index within paksha (0=Pratipada): Sun-Dwadashi ...
GAND_MOOL = {0, 8, 9, 17, 18, 26}  # Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati
BHADRA_VASA = {0: "Swarga", 1: "Swarga", 2: "Swarga", 7: "Swarga", 5: "Patala", 6: "Patala", 8: "Patala", 9: "Patala",
               3: "Bhumi", 4: "Bhumi", 10: "Bhumi", 11: "Bhumi"}
TARA = [("Janma", "mixed - avoid major new beginnings", "donate vegetables/greens"), ("Sampat", "wealth & gains", None),
        ("Vipat", "obstacles, danger", "donate jaggery"), ("Kshema", "well-being", None),
        ("Pratyari", "opposition", "donate salt"), ("Sadhaka", "accomplishment", None),
        ("Vadha (Naidhana)", "destruction - avoid", "donate sesame with gold"), ("Mitra", "friendly", None), ("Parama Mitra", "very friendly", None)]
CHANDRA_GOOD = {1, 3, 6, 7, 10, 11}

def _p(t): return t % 15

def _spans(f, a, b, step=2 / 1440):
    out = []; t = a; cur = f(t); s = t
    while t < b:
        t2 = min(t + step, b); v = f(t2)
        if v != cur:
            lo, hi = t, t2
            for _ in range(20):
                m = (lo + hi) / 2
                if f(m) == cur: lo = m
                else: hi = m
            out.append((cur, s, hi)); cur = v; s = hi
        t = t2
    out.append((cur, s, b)); return out

def day_doshas(d: Date, lat, lon, tz_name=None, utc_offset=None, janma_nakshatra: int | None = None, janma_rashi: int | None = None):
    tz = make_tz(tz_name, utc_offset); ev = day_events(d, lat, lon, tz)
    sr, nsr = ev["sunrise"], ev["next_sunrise"]; wd = weekday_of(d)
    out = {"date": d.isoformat(), "weekday_index": wd}
    # Panchaka: Moon sidereal in 296.67..360 (Dhanishta pada 3 to Revati)
    inP = lambda t: moon_sid(t) >= 300 - 10 / 3
    pk = [(v, a, b) for v, a, b in _spans(inP, sr, nsr) if v]
    pan = []
    for _, a, b in pk:
        st = a
        if abs(a - sr) < 1e-6:  # began before today's sunrise: walk back to the true start
            while inP(st - 0.05) and st > sr - 6: st -= 0.05
            lo, hi = st - 0.05, st
            for _ in range(25):
                m = (lo + hi) / 2
                if inP(m): hi = m
                else: lo = m
            st = hi
        from .ephem import local_from_jd
        ld = local_from_jd(st, tz).date()
        if st < day_events(ld, lat, lon, tz)["sunrise"]: ld = Date.fromordinal(ld.toordinal() - 1)
        sw = weekday_of(ld); typ = PANCHAKA_TYPES.get(sw)
        pan.append({"start": fmt(a, tz), "end": fmt(b, tz), "panchaka_began": fmt(st, tz), "type": typ[0] if typ else "Panchaka (Wed/Thu start: no special type)",
                    "effect": typ[1] if typ else "general Panchaka restrictions apply"})
    out["panchaka"] = {"active": bool(pan), "windows": pan, "avoid": PANCHAKA_AVOID if pan else [],
                       "rule": "Moon transiting Dhanishta (2nd half) through Revati, i.e. Kumbha & Meena"}
    # Panchaka-rahita: (tithi + vara + nakshatra + lagna) mod 9, all 1-based
    f = lambda t: (tithi_at(t) + 1 + wd + 1 + nak_at(t) + 1 + int(ascendant(t, lat, lon, True) // 30) + 1) % 9
    rows = []
    for v, a, b in _spans(f, sr, nsr, 4 / 1440):
        rows.append({"start": fmt(a, tz), "end": fmt(b, tz), "remainder": v, "dosha": RAHITA.get(v), "good": v not in RAHITA})
    out["panchaka_rahita"] = rows
    # Bhadra (Vishti karana) windows with residence
    bh = []
    for v, a, b in _spans(lambda t: (karana_at(t) - 1) % 7 == 6 and 1 <= karana_at(t) <= 56, sr, nsr):
        if v:
            vasa = BHADRA_VASA[int(moon_sid(a) // 30)]
            bh.append({"start": fmt(a, tz), "end": fmt(b, tz), "residence": vasa, "harmful": vasa == "Bhumi",
                       "note": "Bhadra residing on earth (Moon in Karka/Simha/Kumbha/Meena) is harmful; in Swarga/Patala it is mild"})
    out["bhadra"] = bh
    t = tithi_at(sr); n = nak_at(sr)
    out["dagdha_tithi"] = _p(t) == DAGDHA[wd]
    out["krakacha_yoga"] = (_p(t) + 1) + (wd + 1) == 13
    out["samvartaka_yoga"] = (wd == 0 and _p(t) == 6) or (wd == 3 and _p(t) == 0)
    out["gand_mool"] = n in GAND_MOOL
    out["sunrise_tithi"] = TITHIS[t]; out["sunrise_nakshatra"] = NAKSHATRAS[n]
    if janma_nakshatra is not None:
        k = ((n - (janma_nakshatra - 1)) % 27) % 9
        nm, eff, rem = TARA[k]
        out["tarabala"] = {"tara": nm, "number": k + 1, "effect": eff, "remedy": rem, "favourable": k in (1, 3, 5, 7, 8),
                           "cycle": (n - (janma_nakshatra - 1)) % 27 // 9 + 1}
    if janma_rashi is not None:
        h = (int(moon_sid(sr) // 30) - (janma_rashi - 1)) % 12 + 1
        shukla = t < 15
        out["chandrabala"] = {"house_from_janma_rashi": h, "favourable": h in CHANDRA_GOOD or (shukla and h in (2, 5, 9)),
                              "chandrashtama": h == 8, "note": "Moon in 1/3/6/7/10/11 from birth sign is good; 2/5/9 also good in Shukla paksha; 8th = Chandrashtama"}
    return out

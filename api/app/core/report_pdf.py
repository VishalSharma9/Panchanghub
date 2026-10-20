"""Comprehensive multi-section Kundli & Vedic Life Reading PDF using reportlab."""
from __future__ import annotations
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

from .interpret_ext import generate_holistic_reading
from .yogas_engine import evaluate_all_yogas
from .vargas_ext import build_all_vargas
from .dashas_ext import compute_jaimini_karakas
from .special_lagnas import compute_special_lagnas
from .ashtakavarga_ext import full_ashtakavarga_suite

MAROON = colors.HexColor("#7a1f2b")
GOLD = colors.HexColor("#c58312")
LIGHT_CREAM = colors.HexColor("#fffaf2")
DARK_INK = colors.HexColor("#2a1a12")
MUTED_BROWN = colors.HexColor("#5e4a3d")

def _table(rows, widths=None, header_bg=MAROON):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2cfae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_CREAM]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def kundli_pdf(k: dict, name: str) -> bytes:
    """Generates an exhaustive, beautifully styled multi-page Master Vedic Horoscope & Life Reading PDF."""
    buf = BytesIO()
    st = getSampleStyleSheet()
    
    # Custom typographical styles
    title_st = ParagraphStyle("RptTitle", parent=st["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=MAROON, alignment=0)
    sub_st = ParagraphStyle("RptSub", parent=st["Normal"], fontName="Helvetica-Oblique", fontSize=9, leading=13, textColor=MUTED_BROWN)
    h1_st = ParagraphStyle("RptH1", parent=st["Heading1"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=MAROON, spaceBefore=12, spaceAfter=4)
    h2_st = ParagraphStyle("RptH2", parent=st["Heading2"], fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=DARK_INK, spaceBefore=8, spaceAfter=3)
    body_st = ParagraphStyle("RptBody", parent=st["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK_INK)
    bold_st = ParagraphStyle("RptBold", parent=body_st, fontName="Helvetica-Bold")
    callout_st = ParagraphStyle("RptCallout", parent=body_st, fontSize=8, leading=11, textColor=MUTED_BROWN)

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        title=f"Vedic Horoscope & Life Reading - {name}",
        author="PanchangHub",
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    E = []

    # Title & Metadata Banner
    E.append(Paragraph(f"<font color='#7a1f2b'>PanchangHub</font> — Master Vedic Life Reading &amp; Janma Kundli", title_st))
    E.append(Paragraph(f"Native: <b>{name}</b> · Birth (UTC): {k.get('datetime_utc', '—')} · Ayanamsha: {k.get('ayanamsa', 'Lahiri')} · Whole-Sign Houses", sub_st))
    E.append(Spacer(1, 6))

    # Lagna & Moon Identity summary box
    lagna = k.get("lagna", {})
    moon = k.get("moon", {})
    ident_rows = [
        ["Key Indicator", "Sign / Rashi", "Exact Coordinate", "Nakshatra & Pada", "Nakshatra Lord"],
        ["Ascendant (Lagna)", lagna.get("sign", "—"), lagna.get("dms", "—"), f"{lagna.get('nakshatra', '—')} (Pada {lagna.get('pada', '—')})", lagna.get("nakshatra_lord", "—")],
        ["Janma Rashi (Moon)", moon.get("sign", "—"), moon.get("dms", "—"), f"{moon.get('nakshatra', '—')} (Pada {moon.get('pada', '—')})", moon.get("nakshatra_lord", "—")]
    ]
    E.append(_table(ident_rows, [110, 95, 95, 125, 95]))
    E.append(Spacer(1, 8))

    # Planetary Positions Table
    E.append(Paragraph("1. Sidereal Planetary Coordinates &amp; Dignities", h1_st))
    pl_rows = [["Planet", "Sign", "Degree", "Nakshatra", "Pada", "House", "Motion", "Dignity", "Navamsa (D9)"]]
    for p in k.get("planets", [])[:9]:
        motion = "Retrograde" if p.get("retrograde") and p["name"] not in ("Rahu", "Ketu") else ("Combust" if p.get("combust") else "Direct")
        pl_rows.append([
            p["name"], p["sign"], p["dms"], p["nakshatra"], str(p["pada"]),
            str(p["house"]), motion, p.get("dignity", "Neutral"), p.get("vargas", {}).get("D9", "—")
        ])
    E.append(_table(pl_rows, [60, 55, 65, 75, 30, 35, 65, 65, 70]))
    E.append(Spacer(1, 10))

    # Compute holistic reading and comprehensive yogas
    pos = {p["name"]: {"longitude": p["longitude"], "speed": p.get("speed", 0.0)} for p in k.get("planets", [])}
    asc_lon = lagna.get("longitude", 0.0)
    reading = generate_holistic_reading(pos, asc_lon)
    yogas_data = evaluate_all_yogas(pos, asc_lon)
    vargas_data = build_all_vargas(pos, asc_lon)
    karakas_data = compute_jaimini_karakas(pos)

    # Section 2: Ascendant Foundation
    asc_p = reading.get("ascendant_profile", {})
    E.append(Paragraph("2. Ascendant (Lagna) Constitutional Foundation", h1_st))
    E.append(Paragraph(f"<b>Ascendant Sign:</b> {asc_p.get('sign')} ({asc_p.get('rashi')}) &nbsp;|&nbsp; <b>Governing Lord:</b> {asc_p.get('ruler')} &nbsp;|&nbsp; <b>Element:</b> {asc_p.get('element')}", body_st))
    E.append(Spacer(1, 3))
    E.append(Paragraph(f"<b>Core Temperament:</b> {asc_p.get('portrait')}", body_st))
    E.append(Spacer(1, 4))
    
    strengths_table = [
        ["Key Constitutional Strengths", "Self-Mastery Growth Areas"],
        [asc_p.get("strengths", ""), asc_p.get("growth_areas", "")]
    ]
    E.append(_table(strengths_table, [260, 260], header_bg=colors.HexColor("#5e0f26")))
    E.append(Spacer(1, 10))

    # Section 3: Classical Yogas
    E.append(Paragraph(f"3. Classical Planetary Combinations (Yogas) — Auspiciousness Score: {yogas_data.get('auspiciousness_index', 0)} / 100", h1_st))
    E.append(Paragraph(f"Comprehensive evaluation identified <b>{yogas_data.get('total_yogas_detected', 0)}</b> classical yogas from classical treatises (BPHS, Phaladeepika, Saravali):", callout_st))
    E.append(Spacer(1, 4))
    
    for y in yogas_data.get("yogas", [])[:8]:
        E.append(Paragraph(f"• <b>{y['name']}</b> ({y.get('category', '')} · <i>{y.get('nature', '')}</i>): {y.get('description', '')}", body_st))
        E.append(Paragraph(f"&nbsp;&nbsp;<i>Trigger Rule: {y.get('condition', '')}</i>", callout_st))
        E.append(Spacer(1, 3))

    E.append(Spacer(1, 8))

    # Section 4: 144 House Lord Placement Analysis
    E.append(Paragraph("4. Bhava Lord Placements (144 Combinations Matrix)", h1_st))
    E.append(Paragraph("Synthesis of where each house governing lord resides, defining life focus and karmic expression:", callout_st))
    E.append(Spacer(1, 4))
    
    for hl in reading.get("house_lords", []):
        sloka_info = hl.get("bphs_sloka", {})
        sloka_txt = f"<br/><font color='#7a1f2b' size='7.5'><i>BPHS Ch. 26: {sloka_info.get('verse', '')}</i></font>" if sloka_info.get('verse') else ""
        E.append(Paragraph(
            f"<b>House {hl['house']} Lord ({hl['ruler']}) in House {hl['placed_in_house']} ({hl['placed_in_sign']}):</b> {hl['interpretation']}{sloka_txt}",
            body_st
        ))
        E.append(Spacer(1, 3))

    E.append(Spacer(1, 8))

    # Section 5: 12 Houses Shad Phala
    E.append(Paragraph("5. Twelve Houses Shad Phala (Auspicious vs. Karmic Growth Balance)", h1_st))
    sp_rows = [["House & Domain", "Planetary Occupants", "Favorable Manifestation Potential", "Growth Considerations"]]
    for sp in reading.get("shad_phala", []):
        occ = ", ".join(sp.get("occupants", [])) if sp.get("occupants") else "Unoccupied"
        sp_rows.append([
            f"H{sp['house']}: {sp['title']}", occ, sp.get("favorable_potential", ""), sp.get("growth_considerations", "")
        ])
    E.append(_table(sp_rows, [95, 75, 175, 175]))
    E.append(Spacer(1, 10))

    # Section 6: Jaimini Chara Karakas & Karakamsha
    E.append(Paragraph("6. Jaimini Chara Karakas (Soul &amp; Life Indicators)", h1_st))
    karaka_rows = [["Karaka Role", "Planet", "Degree in Sign", "Sign / Rashi", "Significance"]]
    for k_item in karakas_data.get("karakas", []):
        karaka_rows.append([
            k_item["role"], k_item["planet"], f"{k_item['degree_in_sign']}°",
            f"{k_item['sign']} ({k_item.get('rashi', '')})", k_item["description"]
        ])
    E.append(_table(karaka_rows, [110, 60, 65, 105, 180]))
    E.append(Spacer(1, 4))
    E.append(Paragraph(
        f"<b>Karakamsha Analysis:</b> Soul significator ({karakas_data.get('atmakaraka', '—')}) occupies <b>{karakas_data.get('karakamsha_sign', '—')} ({karakas_data.get('karakamsha_rashi', '—')})</b> in Navamsa, governed by <b>{karakas_data.get('karakamsha_lord', '—')}</b>.",
        body_st
    ))
    E.append(Spacer(1, 10))

    # Section 7: Shodashavarga Highlights & Vargottama
    E.append(Paragraph("7. Shodashavarga (Divisional Charts) &amp; Vargottama Auspiciousness", h1_st))
    nav = reading.get("navamsha_synthesis", {})
    if nav:
        varg_badge = " (Vargottama)" if nav.get("is_vargottama") else ""
        push_badge = " [Pushkara Navamsha]" if nav.get("is_pushkara") else ""
        E.append(Paragraph(f"<b>Navamsha (D9) Soul Blueprint:</b> Rising in {nav.get('d9_lagna_sign')} (Pada {nav.get('navamsha_pada')}), ruled by {nav.get('d9_lagna_lord')}{varg_badge}{push_badge}. Deity: {nav.get('deity')}. {nav.get('synthesis', '')}", body_st))
        if nav.get("saravali_sloka"):
            E.append(Paragraph(f"<i>Saravali Ch. 51: \"{nav['saravali_sloka']}\"</i>", callout_st))
        E.append(Spacer(1, 4))

    vargottama_list = vargas_data.get("vargottama", [])
    if vargottama_list:
        v_str = ", ".join([f"{v['planet']} in {v['sign']} ({v['type']})" for v in vargottama_list])
        E.append(Paragraph(f"<b>Vargottama Planets (Same sign in D1 &amp; D9):</b> {v_str}", body_st))
    else:
        E.append(Paragraph("<b>Vargottama Planets:</b> No planets occupy identical signs in D1 and D9.", body_st))
    E.append(Spacer(1, 4))

    v_strengths_rows = [["Planet", "Dignified Vargas Count", "Classical Auspicious Grade (Parashara)"]]
    for pl, st_info in vargas_data.get("varga_strengths", {}).items():
        v_strengths_rows.append([pl, f"{st_info['dignified_varga_count']} / 16", st_info["grade"]])
    E.append(_table(v_strengths_rows, [120, 160, 240]))
    E.append(Spacer(1, 10))

    # Section 8: Vimshottari & Yogini Dasha Timeline
    E.append(Paragraph("8. Planetary Periods (Dashas) Timeline", h1_st))
    v_dash = k.get("vimshottari_dasha", {})
    bal = v_dash.get("balance_at_birth", {})
    E.append(Paragraph(f"<b>Vimshottari Balance at Birth:</b> {bal.get('lord', '—')} ({bal.get('years_remaining', 0)} years remaining)", body_st))
    E.append(Spacer(1, 3))
    
    dasha_rows = [["Mahadasha Lord", "Start Date", "End Date", "Duration (Years)"]]
    for m in v_dash.get("mahadasha", []):
        dasha_rows.append([m["lord"], m["start"], m["end"], str(m.get("years", "—"))])
    E.append(_table(dasha_rows, [130, 130, 130, 130]))
    E.append(Spacer(1, 8))

    # Section 9: Sarvashtakavarga & Classical Remedies
    E.append(Paragraph("9. Sarvashtakavarga &amp; Classical Remedies", h1_st))
    av_data = k.get("ashtakavarga", {})
    if "signs" in av_data and "sarvashtakavarga" in av_data:
        sav_rows = [[s[:3] for s in av_data["signs"]] + ["Total"], [str(x) for x in av_data["sarvashtakavarga"]] + [str(av_data.get("total", 337))]]
        E.append(_table(sav_rows, [40]*12 + [40]))
        E.append(Spacer(1, 6))

    # Traditional Gemstone & Rudraksha Guidance
    rem = k.get("remedies", {})
    if rem:
        rem_rows = [["Category", "Prescribed Gemstone", "Ruling Planet", "Rudraksha Recommendation"]]
        for rk in ["life_stone", "benefic_stone", "lucky_stone"]:
            if rk in rem:
                r_val = rem[rk]
                rem_rows.append([rk.replace("_", " ").title(), r_val.get("gemstone", "—"), r_val.get("planet", "—"), f"{r_val.get('rudraksha', '—')} Mukhi"])
        E.append(_table(rem_rows, [110, 140, 120, 150], header_bg=colors.HexColor("#5e0f26")))
        E.append(Spacer(1, 4))
        E.append(Paragraph(rem.get("disclaimer", "Remedial gems and mantras should be observed with purity of intention and ethical conduct."), callout_st))
        E.append(Spacer(1, 8))

    # Section 10: Special Lagnas & Jaimini Arudha Padas
    try:
        jd_val = k.get("julian_day") or 2448026.5
        sun_l = pos["Sun"]["longitude"] if "Sun" in pos else 0.0
        moon_l = pos["Moon"]["longitude"] if "Moon" in pos else 0.0
        spl = compute_special_lagnas(jd_val, 20.0, 78.0, asc_lon, sun_l, moon_l, pos)
        E.append(Paragraph("10. Special Lagnas &amp; Jaimini Arudha Padas (BPHS Ch. 5 &amp; Jaimini Upadesha)", h1_st))
        spl_rows = [["Special Indicator", "Code", "Sign", "Degree (DMS)", "Signification"]]
        for k_name, row in [
            ("Hora Lagna", spl.get("hora_lagna", {})),
            ("Ghati Lagna", spl.get("ghati_lagna", {})),
            ("Bhava Lagna", spl.get("bhava_lagna", {})),
            ("Sree Lagna", spl.get("sree_lagna", {})),
            ("Pranapada Lagna", spl.get("pranapada_lagna", {})),
        ]:
            spl_rows.append([k_name, row.get("code", "—"), row.get("sign", "—"), row.get("dms", "—"), "Key harmonic reference point"])
        ind = spl.get("indu_lagna", {})
        spl_rows.append(["Indu Lagna", "IL", ind.get("sign", "—"), "—", ind.get("interpretation", "Wealth significator")])
        E.append(_table(spl_rows, [110, 45, 90, 85, 190]))
        E.append(Spacer(1, 4))
        padas = spl.get("arudha_padas", {})
        if padas:
            pada_str = ", ".join([f"{p['label']} ({p['code']}): {p['sign']}" for p in list(padas.values())[:6]])
            E.append(Paragraph(f"<b>Key Arudha Padas (Manifested Worldly Reality):</b> {pada_str}", body_st))
            E.append(Spacer(1, 8))
    except Exception:
        pass

    # Section 11: Ashtakavarga Reductions & Shodhya Pindas
    try:
        sign_of_map = {p: int(pos[p]["longitude"] // 30) % 12 for p in pos}
        sign_of_map["Lagna"] = int(asc_lon // 30) % 12
        av_ext = full_ashtakavarga_suite(sign_of_map, pos, asc_lon)
        E.append(Paragraph("11. Ashtakavarga Reductions &amp; Shodhya Pindas (BPHS Ch. 67-70)", h1_st))
        pinda_rows = [["Planet", "Rashi Pinda", "Graha Pinda", "Yoga Pinda (Total Composite Strength)", "Classical Application"]]
        for pl_name, pinda in av_ext.get("shodhya_pindas", {}).items():
            pinda_rows.append([
                pl_name, str(pinda.get("rashi_pinda", 0)), str(pinda.get("graha_pinda", 0)),
                str(pinda.get("yoga_pinda", 0)), "Longevity & transit timing multiplier"
            ])
        E.append(_table(pinda_rows, [90, 80, 80, 130, 140], header_bg=colors.HexColor("#5e0f26")))
        E.append(Spacer(1, 4))
        E.append(Paragraph(f"<b>Shodhita SAV Total:</b> {av_ext.get('shodhita_sav_total', 0)} points across 12 signs after Trikona and Ekadhipatya Shodhana reductions.", callout_st))
        E.append(Spacer(1, 8))
    except Exception:
        pass

    # Build document
    doc.build(E)
    return buf.getvalue()

def matching_pdf(res: dict, boy: str, girl: str) -> bytes:
    buf = BytesIO(); st = getSampleStyleSheet()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Kundli Matching - {boy} & {girl}", author="PanchangHub",
                            leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    a = res["ashtakoota"]
    E = [Paragraph(f"<font color='#7a1f2b'>PanchangHub</font> — Kundli Milan: {boy} &amp; {girl}", st["Title"]),
         Paragraph(f"Ashtakoota score: <b>{a.get('total')}</b> / 36 — {a.get('verdict', '')}", st["Normal"]), Spacer(1, 8),
         Paragraph("Ashtakoota (36 Guna)", st["Heading2"]),
         _table([["Koota", "Max", "Obtained", "Detail"]] + [[k["koota"], str(k["max"]), str(k["obtained"]), k["detail"]] for k in a["kootas"]])]
    p = res["porutham"]
    E += [Spacer(1, 8), Paragraph("South Indian 10 Porutham", st["Heading2"]),
          _table([["Porutham", "Match"]] + [[x["name"], "Yes" if x["match"] else "No"] for x in p["poruthams"]])]
    if "manglik" in res:
        m = res["manglik"]
        E += [Spacer(1, 8), Paragraph("Manglik compatibility", st["Heading2"]), Paragraph(m["verdict"], st["Normal"])]
    E += [Spacer(1, 8), Paragraph("Guidance: 18+ gunas is traditionally acceptable; Nadi and Bhakoot doshas have classical cancellations. "
                                  "Use together with full chart analysis.", st["Normal"])]
    doc.build(E); return buf.getvalue()

def varshaphal_pdf(v: dict, name: str) -> bytes:
    buf = BytesIO(); st = getSampleStyleSheet()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Varshaphal {v['year']} - {name}", author="PanchangHub",
                            leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    E = [Paragraph(f"<font color='#7a1f2b'>PanchangHub</font> — Varshaphal {v['year']}: {name}", st["Title"]),
         Paragraph(f"Solar return: {v['solar_return_moment']} &nbsp; Age: {v['age']} &nbsp; Year lord: <b>{v.get('year_lord', '-')}</b>", st["Normal"]),
         Paragraph(f"Muntha: {v.get('muntha', {}).get('sign', v.get('muntha')) if isinstance(v.get('muntha'), dict) else v.get('muntha')}", st["Normal"]), Spacer(1, 8),
         Paragraph("Pancha-adhikari", st["Heading2"]), _table([["Role", "Planet"]] + [[a.replace("_", " ").title(), b] for a, b in v["pancha_adhikari"].items()]),
         Spacer(1, 8), Paragraph("Mudda dasha", st["Heading2"]), _table([["Lord", "Start", "End"]] + [[m["lord"], m["start"], m["end"]] for m in v["mudda_dasha"]]),
         Spacer(1, 8), Paragraph("Tajik yogas", st["Heading2"])]
    for y in v["tajik_yogas"][:30]:
        E.append(Paragraph(f"• <b>{y['yoga']}</b> — {', '.join(y['planets'])} {y.get('note', '')}", st["Normal"]))
    E += [Spacer(1, 8), Paragraph("Sahams", st["Heading2"]), _table([["Saham", "Sign", "Longitude"]] + [[a, b["sign"], b["longitude"]] for a, b in v["sahams"].items()])]
    doc.build(E); return buf.getvalue()

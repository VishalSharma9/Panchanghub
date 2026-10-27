"""Simple multi-section Kundli PDF using reportlab."""
from __future__ import annotations
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

MAROON = colors.HexColor("#6d1a36")

def _table(rows, widths=None):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), MAROON), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fdf3e7")])]))
    return t

def kundli_pdf(k: dict, name: str) -> bytes:
    buf = BytesIO(); st = getSampleStyleSheet()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Kundli - {name}", author="PanchangHub")
    E = [Paragraph(f"<font color='#6d1a36'>PanchangHub</font> — Janma Kundli: {name}", st["Title"]),
         Paragraph(f"Birth (UTC): {k['datetime_utc']} &nbsp; Ayanamsa (Lahiri): {k['ayanamsa']}", st["Normal"]),
         Paragraph(f"Lagna: {k['lagna']['sign']} {k['lagna']['dms']} ({k['lagna']['nakshatra']} {k['lagna']['pada']})", st["Normal"]),
         Spacer(1, 8), Paragraph("Planetary positions", st["Heading2"])]
    rows = [["Planet", "Sign", "Degree", "Nakshatra", "Pada", "House", "Retro", "Dignity", "D9"]]
    for p in k["planets"][:9]:
        rows.append([p["name"], p["sign"], p["dms"], p["nakshatra"], p["pada"], p["house"], "R" if p["retrograde"] else "", p["dignity"], p["vargas"]["D9"]])
    E.append(_table(rows))
    E += [Spacer(1, 8), Paragraph("Avakahada", st["Heading2"])]
    av = k["avakahada"]; E.append(_table([["Field", "Value"]] + [[a.replace("_", " ").title(), str(b)] for a, b in av.items() if a != "nakshatra_syllables"]))
    E += [Spacer(1, 8), Paragraph("Vimshottari Mahadasha", st["Heading2"])]
    E.append(_table([["Lord", "Start", "End"]] + [[m["lord"], m["start"], m["end"]] for m in k["vimshottari_dasha"]["mahadasha"]]))
    E += [Spacer(1, 8), Paragraph("Doshas & Yogas", st["Heading2"])]
    mg = k["doshas"]["manglik"]
    E.append(Paragraph(f"Manglik: {'Yes' if mg['is_manglik'] else 'No'} ({mg['severity']}); Kaal Sarp: {'Yes' if k['doshas']['kaal_sarp']['present'] else 'No'}", st["Normal"]))
    for y in k["yogas"]: E.append(Paragraph(f"• <b>{y['name']}</b>: {y['description']}", st["Normal"]))
    E += [Spacer(1, 8), Paragraph("Sarvashtakavarga", st["Heading2"])]
    av = k["ashtakavarga"]; E.append(_table([[s[:3] for s in av["signs"]], av["sarvashtakavarga"]]))
    doc.build(E); return buf.getvalue()

def matching_pdf(res: dict, boy: str, girl: str) -> bytes:
    buf = BytesIO(); st = getSampleStyleSheet()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Kundli Matching - {boy} & {girl}", author="PanchangHub")
    a = res["ashtakoota"]
    E = [Paragraph(f"<font color='#6d1a36'>PanchangHub</font> — Kundli Milan: {boy} &amp; {girl}", st["Title"]),
         Paragraph(f"Ashtakoota score: <b>{a.get('total')}</b> / 36 — {a.get('verdict', '')}", st["Normal"]), Spacer(1, 8),
         Paragraph("Ashtakoota (36 Guna)", st["Heading2"]),
         _table([["Koota", "Max", "Obtained", "Detail"]] + [[k["koota"], k["max"], k["obtained"], k["detail"]] for k in a["kootas"]])]
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
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Varshaphal {v['year']} - {name}", author="PanchangHub")
    E = [Paragraph(f"<font color='#6d1a36'>PanchangHub</font> — Varshaphal {v['year']}: {name}", st["Title"]),
         Paragraph(f"Solar return: {v['solar_return_moment']} &nbsp; Age: {v['age']} &nbsp; Year lord: <b>{v.get('year_lord', '-')}</b>", st["Normal"]),
         Paragraph(f"Muntha: {v.get('muntha', {}).get('sign', v.get('muntha')) if isinstance(v.get('muntha'), dict) else v.get('muntha')}", st["Normal"]), Spacer(1, 8),
         Paragraph("Pancha-adhikari", st["Heading2"]), _table([["Role", "Planet"]] + [[a.replace("_", " ").title(), b] for a, b in v["pancha_adhikari"].items()]),
         Spacer(1, 8), Paragraph("Mudda dasha", st["Heading2"]), _table([["Lord", "Start", "End"]] + [[m["lord"], m["start"], m["end"]] for m in v["mudda_dasha"]]),
         Spacer(1, 8), Paragraph("Tajik yogas", st["Heading2"])]
    for y in v["tajik_yogas"][:30]:
        E.append(Paragraph(f"• <b>{y['yoga']}</b> — {', '.join(y['planets'])} {y.get('note', '')}", st["Normal"]))
    E += [Spacer(1, 8), Paragraph("Sahams", st["Heading2"]), _table([["Saham", "Sign", "Longitude"]] + [[a, b["sign"], b["longitude"]] for a, b in v["sahams"].items()])]
    doc.build(E); return buf.getvalue()

"""Compare PanchangHub panchang values against cached canonical ephemeris pages.
Usage: python accuracy/compare.py [ayanamsa_mode]  -> writes accuracy/report_<mode>.md"""
import csv, html, json, os, re, sys
from datetime import datetime, date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core import ephem
from app.core.panchang import compute_panchang

CITIES = {"New Delhi": 1261481, "Mumbai": 1275339, "Chennai": 1264527, "London": 2643743, "New York": 5128581}
DATES = ["10/10/2026", "14/01/2026", "21/03/2026", "15/08/2025", "01/01/2000", "24/06/2030"]

GEO = {"1261481": (28.65195, 77.23149, "Asia/Kolkata"), "1275339": (19.07283, 72.88261, "Asia/Kolkata"),
       "1264527": (13.08784, 80.27847, "Asia/Kolkata"), "2643743": (51.50853, -0.12574, "Europe/London"),
       "5128581": (40.71427, -74.00597, "America/New_York")}
mode = sys.argv[1] if len(sys.argv) > 1 else "lahiri"
ephem.set_ayanamsa_mode(mode)

def text(f):
    t = open(f, encoding="utf8", errors="ignore").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)); return re.sub(r"\s+", " ", t)

TM = r"(\d\d:\d\d [AP]M)(?: , (\w{3} \d\d))?"
def to_dt(d0: date, hm, md):
    t = datetime.strptime(hm, "%I:%M %p").time()
    d = d0
    if md:
        mo = datetime.strptime(md, "%b %d"); d = date(d0.year + (1 if d0.month == 12 and mo.month == 1 else 0), mo.month, mo.day)
    return datetime.combine(d, t)

def grab(t, label, d0, kind="upto"):
    i = t.find("Sunrise and Moonrise")
    s = t[i:]
    if kind == "upto":
        if re.match(r".{0,40}?" + re.escape(label) + r" [A-Za-z ]+? upto Full Night", s[s.find(label) - 40 if s.find(label) > 40 else 0:]) and re.search(re.escape(label) + r" ([A-Za-z ]+?) upto Full Night", s[:s.find(label) + 60]):
            m2 = re.search(re.escape(label) + r" ([A-Za-z ]+?) upto Full Night", s)
            return (m2.group(1).strip(), "FULL")
        m = re.search(re.escape(label) + r" ([A-Za-z ]+?) upto " + TM, s)
        return (m.group(1).strip(), to_dt(d0, m.group(2), m.group(3))) if m else None
    if kind == "single":
        m = re.search(re.escape(label) + r" " + TM, s)
        return to_dt(d0, m.group(1), m.group(2)) if m else None
    if kind == "range":
        m = re.search(re.escape(label) + r" " + TM + r" to " + TM, s)
        return (to_dt(d0, m.group(1), m.group(2)), to_dt(d0, m.group(3), m.group(4))) if m else None

def ours_dt(s): return datetime.fromisoformat(s).replace(tzinfo=None) if s else None
def diff(a, b):  # minutes, ours - drik (drik shown to the minute)
    if a is None or b is None: return None
    return round((a - b).total_seconds() / 60, 2)

rows = []
for city, gid in CITIES.items():
    lat, lon, tz = GEO[str(gid)]
    for ds in DATES:
        d0 = datetime.strptime(ds, "%d/%m/%Y").date()
        f = f"accuracy/drik_cache/{gid}_{ds.replace('/', '-')}.html"
        if not os.path.exists(f): continue
        t = text(f)
        p = compute_panchang(d0, lat, lon, tz)
        r = {"city": city, "date": d0.isoformat()}
        for lab, key in [("Sunrise", "sunrise"), ("Sunset", "sunset"), ("Moonrise", "moonrise"), ("Moonset", "moonset")]:
            dv = grab(t, lab, d0, "single"); r[lab] = diff(ours_dt(p[key]), dv)
        for lab, key in [("Tithi", "tithi"), ("Nakshatra", "nakshatra"), ("Yoga", "yoga"), ("Karana", "karana")]:
            g = grab(t, lab, d0, "upto")
            if g:
                name, dv = g; ours = p[key][0]
                if dv == "FULL":
                    r[lab] = 0.0 if ours_dt(ours["end"]) >= ours_dt(p["next_sunrise"]) else 999
                else:
                    r[lab] = diff(ours_dt(ours["end"]), dv); r[lab + "_name_ok"] = name.split()[0].lower()[:4] == ours["name"].lower()[:4] or name.lower().startswith(ours["name"].lower()[:3])
                r[lab + "_drik"] = name
        for lab, key in [("Rahu Kalam", "rahu_kalam"), ("Abhijit", "abhijit"), ("Brahma Muhurta", "brahma_muhurta"), ("Yamaganda", "yamaganda"), ("Gulikai Kalam", "gulikai_kalam"),
                         ("Vijaya Muhurta", "vijaya_muhurta"), ("Amrit Kalam", "amrit_kalam"), ("Varjyam", "varjyam"), ("Dur Muhurtam", "dur_muhurtam"), ("Nishita Muhurta", "nishita_muhurta"), ("Godhuli Muhurta", "godhuli_muhurta"), ("Sayahna Sandhya", "sayahna_sandhya"), ("Pratah Sandhya", "pratah_sandhya")]:
            g = grab(t, lab, d0, "range"); o = p["muhurta"].get(key)
            if isinstance(o, list):
                o = min(o, key=lambda x: abs((ours_dt(x["start"]) - g[0]).total_seconds())) if (o and g) else None
            r[lab] = diff(ours_dt(o["start"]), g[0]) if g and o else None
        m = re.search(r"Lahiri Ayanamsha (\d+\.\d+)", t)
        r["Ayanamsa_arcsec"] = round((p["ayanamsa_lahiri"] - float(m.group(1))) * 3600, 2) if m else None
        rows.append(r)

keys = ["Sunrise", "Sunset", "Moonrise", "Moonset", "Tithi", "Nakshatra", "Yoga", "Karana", "Rahu Kalam", "Yamaganda", "Gulikai Kalam", "Abhijit",
        "Brahma Muhurta", "Pratah Sandhya", "Amrit Kalam", "Varjyam", "Dur Muhurtam", "Vijaya Muhurta", "Godhuli Muhurta", "Sayahna Sandhya", "Nishita Muhurta"]
out = [f"# PanchangHub Astronomical Precision Benchmark (ayanamsa mode: {mode}, canonical ΔT: {ephem.DRIK_DT_SHIFT})\n",
       "Differences are **ours − Canonical Ephemeris Standard** in minutes. The canonical standard displays times to the minute, so |diff| < 1 means the same displayed minute (when ours is rounded to nearest).\n",
       "| Element | N | within ±1 min | max abs diff (min) | mean diff (min) | names match |", "|---|---|---|---|---|---|"]
summary = {}
for k in keys:
    vals = [r[k] for r in rows if r.get(k) is not None]
    names = [r.get(k + "_name_ok") for r in rows if (k + "_name_ok") in r]
    if not vals: continue
    w = sum(1 for v in vals if abs(v) < 1.0)
    summary[k] = (len(vals), w, max(abs(v) for v in vals), sum(vals) / len(vals))
    out.append(f"| {k} | {len(vals)} | {w}/{len(vals)} ({100*w//len(vals)}%) | {max(abs(v) for v in vals):.2f} | {sum(vals)/len(vals):+.2f} | {'%d/%d' % (sum(names), len(names)) if names else '-'} |")
av = [r["Ayanamsa_arcsec"] for r in rows if r.get("Ayanamsa_arcsec") is not None]
out.append(f"\nAyanamsa (ours − Drik): mean {sum(av)/len(av):+.2f}\" , max |{max(abs(a) for a in av):.2f}\"| over {len(av)} samples.\n")
out.append("\n## Per city/date detail (minutes)\n")
out.append("| City | Date | " + " | ".join(keys[:8]) + " | Rahu | Abhijit |")
out.append("|---|---|" + "---|" * 10)
for r in rows:
    f = lambda v: "-" if v is None else f"{v:+.1f}"
    out.append(f"| {r['city']} | {r['date']} | " + " | ".join(f(r.get(k)) for k in keys[:8]) + f" | {f(r.get('Rahu Kalam'))} | {f(r.get('Abhijit'))} |")
tag = mode + ("" if ephem.DRIK_DT_SHIFT else "_strictdt")
open(f"accuracy/report_{tag}.md", "w").write("\n".join(out))
json.dump(rows, open(f"accuracy/rows_{tag}.json", "w"), indent=1, default=str)
print("\n".join(out[:len(keys) + 6]))

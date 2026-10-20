"""Compare sankranti punya-kaal / maha punya-kaal with canonical standards (New Delhi), cached in drik_sankranti_delhi.json."""
import json, os, sys
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.punya_kaal import year_punya_kaal
SLUG = {"Mesha": "mesha", "Vrishabha": "vrishabha", "Mithuna": "mithuna", "Karka": "karka", "Simha": "simha", "Kanya": "kanya", "Tula": "tula",
        "Vrishchika": "vrishchika", "Dhanu": "dhanu", "Makara": "makar", "Kumbha": "kumbha", "Meena": "meena"}

def run(verbose=True):
    ref = json.load(open(os.path.join(os.path.dirname(__file__), "drik_sankranti_delhi.json")))
    ok = n = 0; worst = 0.0; bad = []
    for y in sorted({int(k.split("_")[1]) for k in ref}):
        for s in year_punya_kaal(y, 28.6139, 77.209, "Asia/Kolkata")["sankrantis"]:
            r = ref.get(f"{SLUG[s['rashi']]}_{y}")
            if not r or not r.get("punya"): continue
            dd = datetime.strptime(r["date"][0], "%A, %B %d, %Y").date().isoformat()
            def dm(ours, drik):
                a = datetime.fromisoformat(ours); b = datetime.strptime(drik, "%I:%M %p")
                return (a.hour * 60 + a.minute + a.second / 60) - (b.hour * 60 + b.minute)
            d = [dm(s["punya_kaal"]["start"], r["punya"][0]), dm(s["punya_kaal"]["end"], r["punya"][1]),
                 dm(s["maha_punya_kaal"]["start"], r["maha"][0]), dm(s["maha_punya_kaal"]["end"], r["maha"][1])]
            good = dd == s["observed_on"] and all(-1 <= x <= 1 for x in d)
            n += 1; ok += good; worst = max(worst, max(map(abs, d)))
            if not good: bad.append((y, s["rashi"], d))
            if verbose: print(y, s["rashi"], s["observed_on"], "OK" if good else "DIFF", [round(x, 1) for x in d])
    if verbose: print(f"{ok}/{n} match within 1 min; worst {worst:.2f} min")
    return ok, n, worst, bad

if __name__ == "__main__":
    run()

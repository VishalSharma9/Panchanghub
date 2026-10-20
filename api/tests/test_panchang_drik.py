"""Reference values from canonical Drik ephemeris (New Delhi) — times compared within ±1 minute."""
from datetime import datetime
from conftest import DELHI

def mins(a, b):
    return abs((datetime.fromisoformat(a).replace(tzinfo=None) - datetime.fromisoformat(b)).total_seconds()) / 60

def test_delhi_2026_10_10(client):
    p = client.get("/api/panchang", params={**DELHI, "date": "2026-10-10"}).json()
    assert mins(p["sunrise"], "2026-10-10T06:19:00") < 1
    assert mins(p["sunset"], "2026-10-10T17:57:00") < 1
    assert p["moonrise"] is None                        # No Moonrise
    assert mins(p["moonset"], "2026-10-10T17:30:00") < 1
    assert p["tithi"][0]["name"] == "Amavasya" and mins(p["tithi"][0]["end"], "2026-10-10T21:19:00") < 1
    assert p["nakshatra"][0]["name"] == "Hasta" and mins(p["nakshatra"][0]["end"], "2026-10-10T21:42:00") < 1
    assert p["yoga"][0]["name"] == "Indra" and mins(p["yoga"][0]["end"], "2026-10-10T22:02:00") < 1.5
    m = p["muhurta"]
    assert mins(m["rahu_kalam"]["start"], "2026-10-10T09:13:00") < 1
    assert mins(m["abhijit"]["start"], "2026-10-10T11:45:00") < 1
    assert abs(p["ayanamsa_lahiri"] - 24.2378) < 0.0005

def test_makar_sankranti_and_ekadashi_2026(client):
    f = client.get("/api/festivals", params={**DELHI, "year": 2026}).json()["events"]
    mk = next(e for e in f if e["name"] == "Makar Sankranti")
    assert mk["date"] == "2026-01-14" and mins(mk["moment"], "2026-01-14T15:13:00") < 1
    expected_ekadashi = ["01-14", "01-29", "02-13", "02-27", "03-15", "03-29", "04-13", "04-27", "05-13", "05-27", "06-11", "06-25",
                         "07-10", "07-25", "08-09", "08-23", "09-07", "09-22", "10-06", "10-22", "11-05", "11-20", "12-04", "12-20"]
    ours = [e["date"][5:] for e in f if e["type"] == "ekadashi"]
    assert ours == expected_ekadashi

def test_major_festivals_2026(client):
    f = {e["name"]: e["date"] for e in client.get("/api/festivals", params={**DELHI, "year": 2026}).json()["events"]}
    expected = {"Krishna Janmashtami": "2026-09-04", "Raksha Bandhan": "2026-08-28", "Hanuman Jayanti": "2026-04-02",
                "Nag Panchami": "2026-08-17", "Akshaya Tritiya": "2026-04-19", "Karwa Chauth": "2026-10-29",
                "Maha Shivaratri": "2026-02-15", "Holika Dahan": "2026-03-03", "Diwali (Lakshmi Puja)": "2026-11-08"}
    for k, v in expected.items():
        assert f[k] == v, k

def test_timing_endpoints(client):
    for path in ["/api/choghadiya", "/api/hora", "/api/gowri", "/api/lagna-table", "/api/rahu-kaal", "/api/muhurta/daily", "/api/panchang/regional"]:
        r = client.get(path, params={**DELHI, "date": "2026-10-10"}); assert r.status_code == 200, path
    c = client.get("/api/choghadiya", params={**DELHI, "date": "2026-10-10"}).json()
    assert len(c["day"]) == 8 and len(c["night"]) == 8
    h = client.get("/api/hora", params={**DELHI, "date": "2026-10-10"}).json()
    assert len(h["horas"]) == 24 and h["horas"][0]["lord"] == "Saturn"

def test_all_drik_2026_festival_dates():
    """Every festival in canonical 2026 New Delhi Hindu calendar that we model must match (85/85)."""
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("cf", os.path.join(os.path.dirname(__file__), "..", "accuracy", "compare_festivals.py"))
    cf = importlib.util.module_from_spec(spec); spec.loader.exec_module(cf)
    ok, bad, rows = cf.run(verbose=False)
    assert bad == 0, [r for r in rows if not r[3]]
    assert ok >= 85

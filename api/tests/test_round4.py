"""Round 4: classical-source driven rules."""
from datetime import date
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core import regional_rules as R, muhurta_doshas as MD, yogas_classical as YC, panchang as P

from app.core.ephem import make_tz
KOL = (22.5726, 88.3639, make_tz("Asia/Kolkata", None)); DEL = (28.6139, 77.209, "Asia/Kolkata")

@pytest.fixture(scope="module")
def client(): return TestClient(app)

def test_bengali_new_year_next_day_rule():
    # Mesha sankranti 2025-04-14 03:30 IST and 2026-04-14 09:39 IST -> Poila Boishakh on 15 April both years
    for y in (2025, 2026):
        s, day, start, _ = R.solar_date(date(y, 4, 15), "bengali", *KOL)
        assert (s, day) == (0, 1)
        assert R.solar_date(date(y, 4, 14), "bengali", *KOL)[0] == 11

def test_tamil_malayalam_odia():
    assert R.solar_date(date(2026, 4, 14), "tamil", *KOL)[:2] == (0, 1)
    assert R.solar_date(date(2026, 4, 14), "odia", *KOL)[:2] == (0, 1)
    assert R.solar_date(date(2026, 8, 17), "malayalam", *KOL)[:2] == (4, 1)  # Chingam 1
    r = R.regional_calendar(date(2026, 8, 17), 22.5726, 88.3639, "Asia/Kolkata")
    assert r["malayalam"]["kollam_era"] == 1202 and r["tamil"]["year_name"] == "Parabhava"
    assert r["tamil"]["thiruvalluvar_year"] == 2057 and r["bengali"]["bangabda"] == 1433

def test_surya_siddhanta_sun_close_to_drik():
    from app.core.panchang import sun_sid
    from app.core.ephem import jd_from_utc
    from datetime import datetime, timezone
    jd = jd_from_utc(datetime(2026, 4, 14, 6, tzinfo=timezone.utc))
    d = ((R.ss_sun(jd) - sun_sid(jd) + 180) % 360) - 180
    assert abs(d) < 1.5  # traditional sun differs from modern by well under 1.5 deg today

def test_regional_new_years_api(client):
    r = client.get("/api/festivals/regional-new-years", params={"lat": 13.08, "lon": 80.27, "tz": "Asia/Kolkata", "year": 2026}).json()
    ev = {e["name"]: e["date"] for e in r["events"]}
    assert ev["Puthandu (Tamil New Year)"] == "2026-04-14" and ev["Pohela Boishakh (Bengali New Year)"] == "2026-04-15"
    assert ev["Thai Pongal (Thai 1)"] == "2026-01-14"
    s = client.get("/api/festivals/regional-new-years", params={"lat": 13.08, "lon": 80.27, "tz": "Asia/Kolkata", "year": 2026, "siddhanta": "surya"}).json()
    assert s["siddhanta"] == "surya"

def test_godhuli_seasonal_rule():
    assert P.godhuli_season(9) == "hemanta" and P.godhuli_season(1) == "grishma" and P.godhuli_season(5) == "varsha"
    jan = P.compute_panchang(date(2026, 1, 14), *DEL)
    oct_ = P.compute_panchang(date(2026, 10, 10), *DEL)
    g = lambda p: (p.get("muhurtas") or p.get("muhurta"))["godhuli_muhurta"]
    assert g(jan)["season"] == "hemanta" and g(jan)["start"][11:16] in ("17:42", "17:43") and g(jan)["end"][11:16] in ("18:09", "18:10")  # Drik: 05:43-06:10 PM
    assert g(oct_)["season"] == "varsha" and g(oct_)["start"][11:16] == "17:57"  # Drik: 05:57 PM

def test_panchaka_and_type():
    w = MD.day_doshas(date(2026, 10, 23), *DEL)["panchaka"]
    assert w["active"] and w["windows"][0]["type"] == "Agni Panchaka"  # began Tue night 20/21 Oct
    assert not MD.day_doshas(date(2026, 10, 10), *DEL)["panchaka"]["active"]

def test_doshas_api_tarabala(client):
    r = client.get("/api/muhurta/doshas", params={"lat": 28.61, "lon": 77.21, "tz": "Asia/Kolkata", "date": "2026-10-10", "janma_nakshatra": 5, "janma_rashi": 3}).json()
    assert r["tarabala"]["tara"] == "Parama Mitra" and "chandrabala" in r and r["panchaka_rahita"]

def test_yoga_catalog_100_plus(client):
    c = client.get("/api/yogas/catalog").json()
    assert c["count"] >= 100 and all(y["citation"] for y in c["yogas"])

def test_classical_yogas_detect():
    sign = {"Sun": 4, "Moon": 4, "Mars": 4, "Mercury": 4, "Jupiter": 4, "Venus": 4, "Saturn": 4, "Rahu": 0, "Ketu": 6}
    houses = {p: 1 for p in sign}; houses["Rahu"] = 9; houses["Ketu"] = 3
    names = {y["name"] for y in YC.classical_yogas(sign, houses, 4)}
    assert "Gola Yoga (Sankhya)" in names

def test_festival_rules_and_page(client):
    assert len(client.get("/api/festivals/rules").json()["rules"]) >= 10
    r = client.get("/regional?siddhanta=surya")
    assert r.status_code == 200 and "Panchaka" in r.text

# ---- round 5: Vakya + punya kaal ----
from app.core import vakya as VK, punya_kaal as PKL

def test_chandravakyas_match_vararuci():
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("dec", os.path.join(os.path.dirname(__file__), "..", "research", "vakya", "decode.py"))
    dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
    ours = VK.chandravakyas()
    assert len(ours) == 248
    for i, w in enumerate(dec.V):
        assert abs(ours[i] - round(dec.val(w)[0] * 60)) <= 1, (i + 1, w)

def test_vakya_epoch_lumps():
    assert abs(((VK.MOON_AT_EPOCH + 5105 * VK.DHRUVA_PER_CYCLE) % 360) - (174 + 47 / 60)) < 0.01

def test_vakya_puthandu_and_thai():
    s = {x["rashi"]: x for x in VK.sankranti(2026, "Asia/Kolkata")["sankrantis"]}
    assert s["Mesha"]["vakya"].startswith("2026-04-14T09:0") or s["Mesha"]["vakya"].startswith("2026-04-14T08:5")
    ny = {e["name"]: e["date"] for e in R.regional_new_years(2026, 13.08, 80.27, "Asia/Kolkata", siddhanta="vakya")["events"]}
    assert ny["Thai Pongal (Thai 1)"] == "2026-01-15" and ny["Puthandu (Tamil New Year)"] == "2026-04-14"

def test_vakya_panchang_api(client):
    r = client.get("/api/panchang/vakya", params={"lat": 13.08, "lon": 80.27, "tz": "Asia/Kolkata", "date": "2026-10-10"}).json()
    assert r["siddhanta"] == "vakya" and r["tithi"][0]["name"] == "Amavasya" and r["nakshatra"][0]["name"] == "Hasta"
    assert client.get("/api/vakya/chandravakyas").json()["vakyas"][0]["value"] == "0s 12°03'"
    assert client.get("/api/panchang/regional/v2", params={"lat": 13.08, "lon": 80.27, "tz": "Asia/Kolkata", "siddhanta": "vakya"}).status_code == 200

def test_punya_kaal_matches_drik():
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("cp", os.path.join(os.path.dirname(__file__), "..", "accuracy", "compare_punya.py"))
    cp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cp)
    ok, n, worst, bad = cp.run(verbose=False)
    assert ok == n and n >= 30, bad

def test_punya_kaal_api(client):
    r = client.get("/api/sankranti/punya-kaal", params={"lat": 28.6139, "lon": 77.209, "tz": "Asia/Kolkata", "year": 2026}).json()
    mk = [s for s in r["sankrantis"] if s["rashi"] == "Makara"][0]
    assert mk["punya_kaal"]["start"][11:16] == "15:13" and mk["maha_punya_kaal"]["end"][11:16] in ("16:58", "16:57")

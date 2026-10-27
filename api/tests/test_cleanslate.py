"""Public pages and API bodies must not name another company's products."""
import json

BANNED = (
    "Swiss Ephemeris", "swisseph", "pyswisseph", "Drik Panchang", "drikpanchang",
    "GeoNames", "CC-BY", "Moshier", "Astrodienst", "lahiri_swiss", "Krishnamurti",
    "K.N. Rao", "B.V. Raman",
)

BIRTH = {"date": "1990-05-15", "time": "10:30:00", "timezone": "Asia/Kolkata", "latitude": 28.6139, "longitude": 77.209}


def _assert_clean(blob: str):
    low = blob.lower()
    for word in BANNED:
        assert word.lower() not in low, word


def test_health_and_openapi_are_local(client):
    h = client.get("/api/health").json()
    assert h["status"] == "ok" and h["ephemeris"].startswith("PanchangHub")
    assert "engine_version" in h and "swisseph_version" not in h
    spec = client.get("/api/openapi.json").json()
    blob = json.dumps(h) + json.dumps(spec) + client.get("/api/cities/stats").text
    _assert_clean(blob)
    assert "lahiri_mean" in json.dumps(spec)
    assert "PanchangHub Places" in client.get("/api/cities/stats").json()["source"]


def test_home_footer_has_no_credit_line(client):
    html = client.get("/").text
    assert "© PanchangHub" in html
    assert "REST API" not in html.split("<footer")[-1]
    _assert_clean(html)
    assert ">drik<" not in html.lower() and "drik (" not in html.lower()


def test_old_siddhanta_alias_is_not_echoed(client):
    r = client.get("/api/panchang/regional/v2", params={"lat": 28.61, "lon": 77.21, "tz": "Asia/Kolkata", "siddhanta": "drik"})
    assert r.status_code == 200
    body = r.json()
    assert body["siddhanta"] == "hub"
    assert "drik" not in json.dumps(body).lower()


def test_panchang_uses_solar_not_drik_key(client):
    p = client.get("/api/panchang", params={"lat": 28.61, "lon": 77.21, "tz": "Asia/Kolkata", "date": "2026-10-26"}).json()
    assert "solar" in p["ritu"] and "solar" in p["ayana"]
    assert "drik" not in p["ritu"] and "drik" not in p["ayana"]


def test_old_ayanamsa_token_is_not_published(client):
    r = client.post("/api/chart", json={**BIRTH, "system": "sidereal", "ayanamsa": "lahiri_swiss"})
    assert r.status_code == 200
    _assert_clean(r.text)
    missing = client.get("/api/zodiac/not-a-sign")
    assert missing.status_code == 404
    assert "not-a-sign" in missing.text


def test_kp_and_chara_do_not_name_people(client):
    kp = client.post("/api/kp/chart", json=BIRTH)
    assert kp.status_code == 200
    assert kp.json()["ayanamsa"] == "KP"
    _assert_clean(kp.text)
    dasha = client.post("/api/kundli/dashas", json=BIRTH)
    assert dasha.status_code == 200
    assert "K.N." in dasha.json()["chara"]["method"]
    assert "B.V." in dasha.json()["kalachakra"]["method"]
    assert "Rao" not in dasha.json()["chara"]["method"]
    assert "Raman" not in dasha.json()["kalachakra"]["method"]
    _assert_clean(dasha.text)
from conftest import BIRTH, DELHI

def test_health(client):
    r = client.get("/health"); assert r.status_code == 200 and r.json()["status"] == "ok"

def test_chart_known_sun_tropical(client):
    # J2000.0 (2000-01-01 12:00 UT): apparent Sun ≈ 280.37° → Capricorn 10°22'
    r = client.post("/chart", json={"date": "2000-01-01", "time": "12:00:00", "utc_offset": 0, "latitude": 51.4779, "longitude": 0.0})
    assert r.status_code == 200
    sun = r.json()["planets"][0]
    assert sun["name"] == "Sun" and sun["sign"] == "Capricorn"
    assert abs(sun["longitude"] - 280.37) < 0.02

def test_chart_sidereal_and_houses(client):
    r = client.post("/chart", json={**BIRTH, "system": "sidereal"})
    j = r.json(); assert r.status_code == 200
    assert j["house_system"] == "whole_sign" and 23.6 < j["ayanamsa"] < 23.9
    assert j["ascendant"]["sign"] == "Cancer"
    assert len(j["houses"]) == 12 and any(a["aspect"] for a in j["aspects"])
    names = [p["name"] for p in j["planets"]]
    assert {"Sun", "Moon", "Pluto", "Rahu", "Ketu"} <= set(names)

def test_validation(client):
    assert client.post("/chart", json={**BIRTH, "latitude": 123}).status_code == 422
    assert client.post("/chart", json={**BIRTH, "timezone": "Mars/Base"}).status_code == 422
    b = dict(BIRTH); b.pop("timezone")
    assert client.post("/chart", json=b).status_code == 422
    assert client.get("/zodiac/notasign").status_code == 404

def test_planets_nakshatra_zodiac(client):
    j = client.get("/planets", params={"datetime": "2026-10-10T12:00:00", "tz": "Asia/Kolkata", "system": "sidereal"}).json()
    assert len(j["planets"]) == 12
    n = client.get("/nakshatra", params={"datetime": "2026-10-10T12:00:00", "tz": "Asia/Kolkata"}).json()
    assert n["nakshatra"] == "Hasta" and n["pada"] == 3
    z = client.get("/zodiac/simha").json(); assert z["sign"] == "Leo" and z["element"] == "Fire"

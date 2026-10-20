from conftest import BIRTH, BIRTH2

def test_kundli(client):
    r = client.post("/api/kundli", json=BIRTH); assert r.status_code == 200
    k = r.json()
    assert k["lagna"]["rashi"] == "Karka" and k["moon"]["nakshatra"] == "Uttara Ashadha"
    assert len(k["vargas"]) == 16 and set(k["vargas"]) >= {"D1", "D9", "D60"}
    md = k["vimshottari_dasha"]["mahadasha"]
    assert [m["lord"] for m in md][:3] == ["Sun", "Moon", "Mars"] and sum(m["years"] for m in md) == 120
    assert len(md[0]["antardasha"]) == 9 and len(md[0]["antardasha"][0]["pratyantardasha"]) == 9
    assert k["ashtakavarga"]["total"] == 337
    assert {"manglik", "kaal_sarp", "sade_sati"} <= set(k["doshas"])
    assert len(k["current_dasha"]) == 5

def test_matching(client):
    m = client.post("/api/matching", json={"boy": BIRTH, "girl": BIRTH2}).json()
    a = m["ashtakoota"]; assert 0 <= a["total"] <= 36 and len(a["kootas"]) == 8
    assert sum(k["max"] for k in a["kootas"]) == 36
    assert len(m["porutham"]["poruthams"]) == 10

def test_svg_pdf(client):
    r = client.post("/api/kundli/svg?style=north", json=BIRTH); assert r.headers["content-type"].startswith("image/svg")
    r = client.post("/api/kundli/pdf", json=BIRTH); assert r.content[:4] == b"%PDF"

def test_kp_and_extras(client):
    kp = client.post("/api/kp/chart", json=BIRTH).json()
    assert len(kp["cusps"]) == 12 and all(p["sub_lord"] for p in kp["planets"])
    assert client.get("/api/kp/horary/249").json()["total_segments"] == 249
    assert client.post("/api/varshaphal", json={**BIRTH, "year": 2026}).status_code == 200
    assert client.post("/api/jaimini", json=BIRTH).json()["chara_karakas"]["Atmakaraka"] == "Moon"

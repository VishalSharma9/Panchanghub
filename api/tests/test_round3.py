"""Round 3: full shadbala, extra dashas, ghata chakra, interpretations, i18n, other domains, MCP, PDFs."""
B = {"date": "1990-05-15", "time": "10:00:00", "latitude": 28.61, "longitude": 77.21, "timezone": "Asia/Kolkata"}

def test_shadbala_full(client):
    r = client.post("/api/kundli/shadbala", json=B).json()
    sb = r["shadbala"]["planets"]
    assert set(sb) == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
    for v in sb.values():
        for k in ("uccha", "saptavargaja", "ojhayugma", "kendradi", "drekkana", "sthana", "dig", "nathonnata", "paksha", "tribhaga",
                  "abda_masa_vara_hora", "ayana", "kala", "cheshta", "naisargika", "drishti", "total_rupas"):
            assert k in v
        assert 0 <= v["uccha"] <= 60 and 0 <= v["dig"] <= 60
        assert 3 < v["total_rupas"] < 15
    assert sorted(v["rank"] for v in sb.values()) == list(range(1, 8))
    assert len(r["bhavabala"]["houses"]) == 12

def test_dashas(client):
    d = client.post("/api/kundli/dashas", json=B).json()
    ch = d["chara"]["periods"]
    assert len(ch) >= 12 and all(1 <= p["years"] <= 12 for p in ch[:12]) and len(ch[0]["antardasha"]) == 12
    kc = d["kalachakra"]
    assert kc["paramayu_years"] in (100, 85, 83, 86) and len(kc["periods"]) == 9
    assert {"shodashottari", "dwadashottari", "panchottari", "shatabdika", "chaturashiti_sama", "dwisaptati_sama",
            "shashtihayani", "shattrimsha_sama"} <= set(d["conditional"])
    assert d["conditional"]["shodashottari"]["cycle_years"] == 116 and d["conditional"]["dwadashottari"]["cycle_years"] == 112

def test_kalachakra_tables():
    from app.core.dashas import SAVYA, APASAVYA, KC_YEARS
    tot = lambda seq: sum(KC_YEARS[s] for s in seq)
    assert [tot(s) for s in SAVYA] == [100, 85, 83, 86]
    assert [tot(s) for s in APASAVYA] == [100, 85, 83, 86]

def test_ghata_and_interpretation(client):
    g = client.post("/api/kundli/ghata-chakra", json=B).json(); assert g["janma_rashi"] and g["vara"]
    r = client.post("/api/kundli/interpretation", json=B).json()
    assert len(r["planets"]) == 9 and all(len(p["in_sign"]) > 150 and "house" in p["in_house"] for p in r["planets"])
    assert r["yogas"] and r["mahadashas"] and r["current_dasha"]
    w = client.post("/api/western/interpretation", json=B).json(); assert w["planets"] and w["aspects"]

def test_interpretation_coverage():
    from app.core import interpret as I
    assert len(I.NAK) == 27 and all(len(v) == 12 for v in I.PH.values()) and len(I.PH) == 9
    assert len(I.SIGN) == 12 and len(I.DASHA) == 9

def test_i18n_api(client):
    langs = client.get("/api/languages").json()["languages"]
    assert {"hi", "ta", "te", "bn", "mr", "gu", "kn", "ml"} <= set(langs)
    for lang, sat in [("hi", "शनिवार"), ("ta", "சனி"), ("te", "శనివారం"), ("bn", "শনিবার"), ("mr", "शनिवार"), ("gu", "શનિવાર"), ("kn", "ಶನಿವಾರ"), ("ml", "ശനി")]:
        p = client.get("/api/panchang", params={"date": "2026-10-10", "lat": 28.61, "lon": 77.21, "tz": "Asia/Kolkata", "lang": lang}).json()
        assert p["vara"]["weekday"] == sat, lang
        assert p["sunrise"].startswith("2026-10-10T06:")  # times untouched
    g = client.get("/api/i18n/ta").json()["glossary"]
    assert g["nakshatras"]["Rohini"] == "ரோகிணி" and len(g["nakshatras"]) == 27

def test_i18n_site(client):
    r = client.get("/panchang", params={"lang": "hi", "date": "2026-10-10"})
    assert r.status_code == 200 and "सूर्योदय" in r.text and 'lang="hi"' in r.text and 'id="langSel"' in r.text

def test_human_design(client):
    hd = client.post("/api/human-design", json=B).json()
    assert hd["type"] in ("Manifestor", "Generator", "Manifesting Generator", "Projector", "Reflector")
    assert len(hd["personality"]) == 13 and "/" in hd["profile"]
    from app.core.human_design import gate_line, WHEEL
    assert sorted(WHEEL) == list(range(1, 65)) and gate_line(302.1) == (41, 1)

def test_other_domains(client):
    c = client.get("/api/iching/cast", params={"seed": "abc"}).json()
    assert 1 <= c["primary"]["number"] <= 64
    from app.core.esoteric import hexagram_of, mayan
    from datetime import date
    assert hexagram_of([1] * 6)["number"] == 1 and hexagram_of([0] * 6)["number"] == 2 and hexagram_of([1, 1, 1, 0, 0, 0])["number"] == 11
    assert mayan(date(2012, 12, 21))["long_count"] == "13.0.0.0.0" and mayan(date(2012, 12, 21))["tzolkin"] == "4 Ajaw"
    v = client.post("/api/vastu", json={"layout": {"kitchen": "South-East", "toilet": "North-East"}}).json()
    assert v["score_percent"] == 50
    assert "reading" in client.get("/api/palmistry", params={"hand_shape": "water", "heart": "curved"}).json()
    assert client.get("/api/kabbalah", params={"name": "abc"}).json()["ordinal_value"] == 6
    assert client.get("/api/chinese/forecast", params={"birth_year": 1990, "year": 2026}).json()["relationship"].startswith("Ben Ming")
    assert "snake" in client.get("/api/dreams", params={"symbol": "snake"}).json()["meanings"]
    assert client.get("/api/crystals", params={"sign": "Leo"}).json()["crystals"]

def test_remedies_matching_pdfs(client):
    r = client.post("/api/kundli/remedies", json=B).json(); assert "puja_for_weak_planets" in r and "dosha_remedies" in r
    m = {"boy": B, "girl": {**B, "date": "1992-08-20"}}
    mm = client.post("/api/matching/manglik", json=m).json(); assert "verdict" in mm
    pdf = client.post("/api/matching/pdf", json=m); assert pdf.content[:4] == b"%PDF"
    pdf = client.post("/api/varshaphal/pdf", json={**B, "year": 2026}); assert pdf.content[:4] == b"%PDF"

def test_varshaphal_year_lord_and_tajik(client):
    v = client.post("/api/varshaphal", json={**B, "year": 2026}).json()
    assert v["year_lord"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    assert {y["yoga"] for y in v["tajik_yogas"]} & {"Ithasala", "Ishrafa", "Khallasara", "Nakta", "Yamaya", "Radda", "Kamboola", "Manau", "Ikkabal", "Induvara"}

def test_kp_horary_chart(client):
    r = client.post("/api/kp/horary/chart", json={"number": 1, "latitude": 28.6, "longitude": 77.2, "datetime_utc": "2026-10-10T06:00:00Z"}).json()
    assert abs(r["cusps"][0]["longitude"] - r["horary"]["ascendant_start"]) < 0.01 and len(r["cusps"]) == 12

def test_yogas_extended():
    from app.core.yogas_extra import extra_yogas
    sign_of = {"Lagna": 0, "Sun": 0, "Moon": 1, "Mars": 2, "Mercury": 3, "Jupiter": 4, "Venus": 5, "Saturn": 6, "Rahu": 7, "Ketu": 1}
    houses_of = {p: s + 1 for p, s in sign_of.items() if p != "Lagna"}
    names = [y["name"] for y in extra_yogas(sign_of, houses_of, 0)]
    assert any("Vallaki" in n for n in names)

def test_new_muhurats_transit_search(client):
    for t in ("mundan", "annaprashan", "business"):
        r = client.get("/api/muhurat", params={"type": t, "start": "2026-11-01", "end": "2026-11-30", "lat": 28.6, "lon": 77.2, "tz": "Asia/Kolkata"})
        assert r.status_code == 200 and r.json()["muhurats"], t
    s = client.get("/api/transits/search", params={"planet": "Saturn", "sign": "Aries", "start": "2026-01-01", "years": 3}).json()
    assert s["results"] and s["results"][0]["to_sign"] == "Aries"
    w = client.post("/api/western/transits", json={**B, "transit_datetime": "2026-10-10T00:00:00Z"}).json(); assert w["aspects_to_natal"]

def test_mcp_and_ask(client):
    t = client.post("/api/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).json()
    assert {x["name"] for x in t["result"]["tools"]} >= {"panchang", "kundli", "festivals"}
    r = client.post("/api/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "panchang", "arguments": {"date": "2026-10-10", "lat": 28.6, "lon": 77.2, "tz": "Asia/Kolkata"}}}).json()
    assert "tithi" in r["result"]["content"][0]["text"]
    a = client.post("/api/ask", json={"question": "next ekadashi?"}).json(); assert a["intent"] == "next_ekadashi"

def test_new_site_pages(client):
    q = "date=1990-05-15&time=10:30:00&lat=28.61&lon=77.21&tz=Asia/Kolkata"
    for u in ["/human-design?" + q, "/vastu", "/iching?question=x", "/palmistry", "/tools", "/kundli?" + q]:
        r = client.get(u); assert r.status_code == 200, u
    assert "Shadbala" in client.get("/kundli?" + q).text

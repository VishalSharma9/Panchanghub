from conftest import BIRTH, BIRTH2, DELHI

def test_numerology(client):
    n = client.get("/api/numerology", params={"name": "John Smith", "dob": "1990-05-15"}).json()
    assert n["life_path"]["number"] == 3  # 1+9+9+0=19→1, 5, 15→6 => 12 → 3

def test_misc_endpoints(client):
    for m, u, j in [("get", "/api/tarot/draw?spread=celtic_cross&seed=a", None), ("get", "/api/chinese/zodiac?date=2026-02-10", None),
                    ("post", "/api/chinese/bazi", BIRTH), ("get", "/api/horoscope/daily/leo", None), ("get", "/api/horoscope/nakshatra/5", None),
                    ("post", "/api/western/synastry", {"person1": BIRTH, "person2": BIRTH2}), ("post", "/api/western/progressions", {**BIRTH, "on_date": "2026-10-10"}),
                    ("post", "/api/western/return", {**BIRTH, "after": "2026-01-01"}), ("get", "/api/moon-phases?days=30", None),
                    ("get", "/api/search/tithi?index=11&count=3", None), ("get", "/api/transits?start=2026-01-01&end=2026-12-31", None),
                    ("get", "/api/eclipses?year=2026", None), ("get", "/api/cities?q=Mumb", None)]:
        r = getattr(client, m)(u, json=j) if j else getattr(client, m)(u)
        assert r.status_code == 200, u
    cz = client.get("/api/chinese/zodiac?date=2026-02-10").json(); assert cz["animal"] == "Snake"  # before LNY 2026-02-17
    t = client.get("/api/tarot/draw?spread=celtic_cross&seed=a").json(); assert len(t["cards"]) == 10

def test_month_calendar_and_muhurat(client):
    c = client.get("/api/calendar/month", params={**DELHI, "year": 2026, "month": 2}).json(); assert len(c["days"]) == 28
    m = client.get("/api/muhurat", params={**DELHI, "type": "griha_pravesh", "start": "2026-11-01", "end": "2026-11-30"}).json()
    assert "muhurats" in m

def test_site_pages(client):
    for u in ["/", "/panchang", "/calendar", "/choghadiya", "/hora", "/rahu-kaal", "/lagna-table", "/festivals", "/kundli", "/matching",
              "/muhurat", "/transits", "/western", "/horoscope", "/numerology", "/tarot", "/robots.txt", "/sitemap.xml"]:
        r = client.get(u); assert r.status_code == 200, u
    h = client.get("/").text
    assert "PanchangHub" in h and 'rel="canonical" href="https://panchanghub.com/"' in h

"""Tests for Vedic Prashna Kundali (Horary) and Soul Guidance & Remedies Suite."""
import pytest
from datetime import datetime, timezone, date, time
from fastapi.testclient import TestClient

from app.main import app
from app.core.prashna import evaluate_prashna, QUERY_DOMAINS
from app.core.remedies_corpus import compute_soul_guidance, get_complete_remedies_for_chart, GRAHA_REMEDIES
from app.models import PrashnaRequest, KundliRequest

client = TestClient(app)

def test_prashna_engine_all_domains():
    dt_utc = datetime(2026, 10, 18, 12, 0, 0, tzinfo=timezone.utc)
    lat, lon = 28.6139, 77.2090  # New Delhi
    
    for category in QUERY_DOMAINS.keys():
        res = evaluate_prashna(dt_utc, lat, lon, category)
        assert "verdict" in res
        assert res["verdict_badge"] in ("favorable", "mixed", "unfavorable")
        assert 0 <= res["confidence_score"] <= 100
        assert "timeframe" in res and len(res["timeframe"]) > 0
        assert "testimonies" in res and len(res["testimonies"]) > 0
        assert "prashna_lagna" in res
        assert "karya_bhava" in res
        assert "tajika_yogas" in res
        assert len(res["planets"]) >= 9

def test_soul_guidance_and_remedies():
    # Sample planet coordinates
    pos = {
        "Sun": {"longitude": 185.5, "speed": 1.0},
        "Moon": {"longitude": 45.2, "speed": 13.2},
        "Mars": {"longitude": 120.1, "speed": 0.5},
        "Mercury": {"longitude": 195.0, "speed": 1.2},
        "Jupiter": {"longitude": 75.3, "speed": 0.08},
        "Venus": {"longitude": 210.4, "speed": 1.1},
        "Saturn": {"longitude": 340.2, "speed": 0.03},
        "Rahu": {"longitude": 30.0, "speed": -0.05},
        "Ketu": {"longitude": 210.0, "speed": -0.05}
    }
    asc_lon = 180.0  # Libra Lagna
    
    sg = compute_soul_guidance(pos, asc_lon)
    assert "atmakaraka" in sg
    assert "karakamsha" in sg
    assert "ishta_devata" in sg
    assert "deity_archetype" in sg["ishta_devata"]
    assert "primary_mantra" in sg["ishta_devata"]
    assert "dharma_devata" in sg
    assert "palana_devata" in sg
    assert "purushartha_matrix" in sg
    
    # Check purushartha percentages sum to ~100
    pct = sg["purushartha_matrix"]["distribution_percentages"]
    total_pct = sum(pct.values())
    assert 99.0 <= total_pct <= 101.0

def test_graha_remedies_catalogue():
    assert len(GRAHA_REMEDIES) == 9
    for g, rem in GRAHA_REMEDIES.items():
        assert "beej_mantra" in rem
        assert "puranic_mantra" in rem
        assert "gayatri_mantra" in rem
        assert rem["prescribed_japa_count"] > 0
        assert rem["kaliyuga_recommended_count"] == rem["prescribed_japa_count"] * 4
        assert "rosary_mala" in rem
        assert "best_muhurta" in rem

def test_api_endpoints_prashna_and_remedies():
    # 1. API: Prashna
    resp = client.post("/api/kundli/prashna", json={
        "date": "2026-10-18",
        "time": "14:30:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata",
        "query_category": "career",
        "question_text": "Will I get selected for the leadership role?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "verdict" in data
    assert "confidence_score" in data
    assert data["query_domain"] == "career"

    # 2. API: Soul Guidance
    kundli_payload = {
        "date": "1990-10-24",
        "time": "14:30:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata",
        "name": "Arjuna"
    }
    resp_sg = client.post("/api/kundli/soul-guidance", json=kundli_payload)
    assert resp_sg.status_code == 200
    sg_data = resp_sg.json()
    assert "atmakaraka" in sg_data
    assert "ishta_devata" in sg_data

    # 3. API: Remedies Corpus
    resp_rem = client.post("/api/kundli/remedies-corpus", json=kundli_payload)
    assert resp_rem.status_code == 200
    rem_data = resp_rem.json()
    assert "graha_remedies_catalogue" in rem_data
    assert "soul_guidance" in rem_data

    # 4. API: Mantras Catalog
    resp_man = client.get("/api/kundli/mantras")
    assert resp_man.status_code == 200
    assert "grahas" in resp_man.json()

def test_web_routes_prashna_and_kundli():
    # Web: Prashna default page
    resp = client.get("/prashna")
    assert resp.status_code == 200
    assert "Prashna Kundali" in resp.text
    assert "Ask a Prashna" in resp.text

    # Web: Prashna cast inquiry
    resp_cast = client.get("/prashna?category=finance&q_text=Will+my+investment+succeed&date=2026-10-18&time=15:00:00&lat=28.6139&lon=77.209&tz=Asia/Kolkata")
    assert resp_cast.status_code == 200
    assert "Inquiry: Wealth, Money &amp; Investments" in resp_cast.text or "Inquiry: Wealth" in resp_cast.text
    assert "Confidence Index" in resp_cast.text

    # Web: Kundli with Worksheet 11
    resp_k = client.get("/kundli?name=TestNative&date=1990-10-24&time=14:30:00&lat=28.6139&lon=77.209&tz=Asia/Kolkata")
    assert resp_k.status_code == 200
    assert "ws-soul-remedies" in resp_k.text
    assert "Atmakaraka &amp; Karakamsha" in resp_k.text
    assert "Ishta Devata" in resp_k.text
    assert "Purushartha Life Goals Alignment Matrix" in resp_k.text

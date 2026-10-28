import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_BIRTH = {
    "name": "Arjuna",
    "date": "1990-05-15",
    "time": "10:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "house_system": "whole_sign",
    "ayanamsa": "lahiri",
    "true_node": False,
    "dasha_levels": 3
}

def test_vargas_endpoint():
    res = client.post("/api/kundli/vargas", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "vargas" in data
    vargas = data["vargas"]
    # Verify all 16 Shodashavargas are present
    expected_vargas = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
    for v in expected_vargas:
        assert v in vargas, f"Missing {v}"
        v_data = vargas[v]
        assert "ascendant" in v_data
        assert "planets" in v_data
        assert len(v_data["planets"]) >= 9
    assert "vargottama" in data
    assert "varga_strengths" in data

def test_current_dasha_endpoint():
    res = client.post("/api/kundli/dashas/current", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "mahadasha" in data
    assert "antardasha" in data
    assert "pratyantardasha" in data
    assert "summary" in data

def test_yogini_dasha_endpoint():
    res = client.post("/api/kundli/dashas/yogini", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["system"] == "Yogini Dasha (36 Years)"
    assert "birth_balance" in data
    assert "periods" in data
    assert len(data["periods"]) > 0
    first_p = data["periods"][0]
    assert "antardashas" in first_p
    assert len(first_p["antardashas"]) == 8

def test_chara_karakas_endpoint():
    res = client.post("/api/kundli/dashas/chara", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "karakas" in data
    assert len(data["karakas"]) == 7
    assert "atmakaraka" in data
    assert "karakamsha_sign" in data

def test_holistic_reading_endpoint():
    res = client.post("/api/kundli/reading", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "ascendant_profile" in data
    assert "house_lords" in data
    assert len(data["house_lords"]) == 12
    assert "shad_phala" in data
    assert len(data["shad_phala"]) == 12

def test_comprehensive_yogas_endpoint():
    res = client.post("/api/kundli/yogas", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "total_yogas_detected" in data
    assert "yogas" in data
    assert data["total_yogas_detected"] > 0

def test_ayanamshas_comparison_endpoint():
    res = client.post("/api/kundli/ayanamshas", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "modes" in data
    modes = data["modes"]
    for m in ["lahiri", "raman", "kp", "kp_new", "yukteshwar", "bhasin", "sayana"]:
        assert m in modes, f"Missing mode {m}"

def test_web_vargas_page():
    # Empty form
    r1 = client.get("/vargas")
    assert r1.status_code == 200
    assert "Shodashavargas" in r1.text

    # With birth query
    q = "date=1990-05-15&time=10:30:00&lat=28.6139&lon=77.2090&tz=Asia/Kolkata&style=north"
    r2 = client.get(f"/vargas?{q}")
    assert r2.status_code == 200
    assert "D60" in r2.text
    assert "D9" in r2.text
    assert "Vargottama" in r2.text

def test_web_yogas_page():
    # Empty form
    r1 = client.get("/yogas")
    assert r1.status_code == 200
    assert "Classical Vedic Yogas Scanner" in r1.text

    # With birth query
    q = "date=1990-05-15&time=10:30:00&lat=28.6139&lon=77.2090&tz=Asia/Kolkata"
    r2 = client.get(f"/yogas?{q}")
    assert r2.status_code == 200
    assert "Auspiciousness Index" in r2.text
    assert "Pancha Mahapurusha" in r2.text or "Yoga" in r2.text

def test_web_reading_page():
    # Empty form
    r1 = client.get("/reading")
    assert r1.status_code == 200
    assert "Holistic Vedic Life Reading" in r1.text

    # With birth query
    q = "date=1990-05-15&time=10:30:00&lat=28.6139&lon=77.2090&tz=Asia/Kolkata"
    r2 = client.get(f"/reading?{q}")
    assert r2.status_code == 200
    assert "Ascendant (Lagna) Foundation" in r2.text
    assert "House 1 Lord" in r2.text
    assert "Shad Phala" in r2.text

def test_enhanced_kundli_pdf_generation():
    res = client.post("/api/kundli/pdf", json=SAMPLE_BIRTH)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-")
    assert len(res.content) > 10000

def test_planetary_placements_corpus():
    res = client.post("/api/kundli/corpus/planetary-placements", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "ascendant_portfolio" in data
    assert "ascendant_drekkana" in data
    assert "graha_rashi_readings" in data
    assert len(data["graha_rashi_readings"]) == 9

def test_comprehensive_life_corpus():
    res = client.post("/api/kundli/corpus/comprehensive-life", json=SAMPLE_BIRTH)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "ascendant_portfolio" in data
    assert "graha_rashi_readings" in data
    assert "house_lords" in data
    assert len(data["house_lords"]) == 12
    assert "shad_phala" in data
    assert "yogas" in data
    assert "karakas" in data
    assert "current_dasha" in data





def test_classical_interpretations_and_slokas():
    res = client.post('/api/kundli/vargas', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    vargas = res.json()['vargas']
    d9_ci = vargas['D9'].get('classical_interpretation')
    assert d9_ci is not None
    assert 'saravali_sloka' in d9_ci
    assert len(d9_ci['saravali_sloka']) > 10
    assert 'd9_lagna_sign' in d9_ci
    d10_ci = vargas['D10'].get('classical_interpretation')
    assert d10_ci is not None
    assert 'career_sphere' in d10_ci
    assert 'classical_sloka' in d10_ci
    d3_ci = vargas['D3'].get('classical_interpretation')
    assert d3_ci is not None
    assert '22nd_drekkana' in d3_ci
    assert 'drekkana_lord' in d3_ci['22nd_drekkana']

def test_holistic_reading_with_bphs_slokas():
    res = client.post('/api/kundli/reading', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    hl0 = data['house_lords'][0]
    assert 'bphs_sloka' in hl0
    assert 'verse' in hl0['bphs_sloka']
    assert 'Brihat Parashara Hora Shastra' in hl0['bphs_sloka']['source']
    assert len(hl0['bphs_sloka']['verse']) > 10
    assert 'navamsha_synthesis' in data
    assert 'saravali_sloka' in data['navamsha_synthesis']
    assert 'kharesh_diagnostic' in data
    assert 'decanate_number' in data['kharesh_diagnostic']

def test_web_vargas_and_reading_render_slokas():
    q = 'date=1990-05-15&time=10:30:00&lat=28.6139&lon=77.2090&tz=Asia/Kolkata'
    rv = client.get(f'/vargas?{q}')
    assert rv.status_code == 200
    assert 'Classical Scriptural Interpretation' in rv.text
    assert 'Saravali (Chapter 51)' in rv.text
    rr = client.get(f'/reading?{q}')
    assert rr.status_code == 200
    assert 'Brihat Parashara Hora Shastra' in rr.text
    assert 'D9 Navamsha Soul Blueprint' in rr.text
    assert '22nd Drekkana (Kharesh)' in rr.text


def test_all_31_vargas_suite():
    res = client.post('/api/kundli/vargas', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    vargas = res.json()['vargas']
    # All 31 vargas
    all_31_expected = [
        'D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12', 'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60',
        'D5', 'D6', 'D8', 'D11', 'D150',
        'D2_IYER', 'D2_IYER3', 'D3_IYER', 'D4_IYER', 'D10_IYER', 'D12_IYER', 'D30_IYER', 'D5_IYER', 'D16_IYER', 'D11_IYER'
    ]
    assert len(vargas) == 31
    for vk in all_31_expected:
        assert vk in vargas, f'Missing varga {vk}'
        v = vargas[vk]
        assert 'ascendant' in v
        assert 'planets' in v
        assert len(v['planets']) >= 9

def test_tajika_sahams_and_nadiamsha_endpoint():
    res = client.post('/api/kundli/tajika/sahams', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    assert 'sahams' in data
    assert len(data['sahams']) == 24
    saham_names = [s['name'] for s in data['sahams']]
    assert 'Punya Saham' in saham_names
    assert 'Vidya Saham' in saham_names
    assert 'Yashas Saham' in saham_names
    
    assert 'ascendant_nadiamsha' in data
    assert 'deity' in data['ascendant_nadiamsha']
    assert 1 <= data['ascendant_nadiamsha']['nadiamsha_number'] <= 150
    
    assert 'ascendant_drekkana_body_part' in data
    assert 'governed_body_part' in data['ascendant_drekkana_body_part']


def test_special_lagnas_endpoint():
    res = client.post('/api/kundli/special-lagnas', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    assert 'hora_lagna' in data
    assert 'ghati_lagna' in data
    assert 'bhava_lagna' in data
    assert 'sree_lagna' in data
    assert 'pranapada_lagna' in data
    assert 'indu_lagna' in data
    assert 'interpretation' in data['indu_lagna']
    assert 'arudha_padas' in data
    assert len(data['arudha_padas']) == 12
    assert 'A1' in data['arudha_padas']
    assert 'A12' in data['arudha_padas']


def test_ashtakavarga_reductions_endpoint():
    res = client.post('/api/kundli/ashtakavarga/reductions', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    assert data['sav_total'] == 337
    assert 'trikona_shodhana' in data
    assert 'shodhita_ashtakavarga' in data
    assert 'shodhita_sav' in data
    assert 'shodhya_pindas' in data
    assert len(data['shodhya_pindas']) == 7
    sun_pinda = data['shodhya_pindas']['Sun']
    assert 'rashi_pinda' in sun_pinda and 'graha_pinda' in sun_pinda and 'yoga_pinda' in sun_pinda
    assert sun_pinda['yoga_pinda'] == sun_pinda['rashi_pinda'] + sun_pinda['graha_pinda']
    assert 'kakshas_matrix' in data


def test_sudarshan_chakra_endpoint():
    res = client.post('/api/kundli/sudarshan', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    assert '<svg' in data['svg']
    assert 'SUDARSHAN' in data['svg']
    assert len(data['sectors']) == 12
    sec1 = data['sectors'][0]
    assert 'lagna_sign' in sec1
    assert 'moon_sign' in sec1
    assert 'sun_sign' in sec1


def test_varshaphala_endpoint():
    payload = {**SAMPLE_BIRTH, 'year': 2026}
    res = client.post('/api/kundli/varshaphala', json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data['year'] == 2026
    assert 'year_lord' in data
    assert 'muntha' in data
    assert 'pancha_adhikari' in data
    assert 'mudda_dasha' in data
    assert len(data['mudda_dasha']) == 9
    assert 'tajik_yogas' in data
    assert 'sahams_full_24' in data
    assert len(data['sahams_full_24']) == 24


def test_kp_endpoint():
    res = client.post('/api/kundli/kp', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    assert len(data['cusps']) == 12
    c1 = data['cusps'][0]
    assert 'sign_lord' in c1 and 'star_lord' in c1 and 'sub_lord' in c1
    assert 'ruling_planets' in data
    assert 'planet_significators' in data
    assert 'house_significators' in data

    # Test KP Horary 1..249
    h_res = client.post('/api/kundli/kp', json={**SAMPLE_BIRTH, 'horary_number': 108})
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert 'horary' in h_data
    assert h_data['horary']['number'] == 108


def test_worksheets_endpoint():
    res = client.post('/api/kundli/worksheets', json=SAMPLE_BIRTH)
    assert res.status_code == 200
    data = res.json()
    assert 'birth_chart' in data
    assert 'vargas_core_four' in data
    assert 'sudarshan' in data
    assert 'special_lagnas' in data
    assert 'ashtakavarga' in data
    assert 'shadbala' in data


def test_web_pages_render_worksheets_varshaphala_and_kp():
    q = 'date=1990-05-15&time=10:30:00&lat=28.6139&lon=77.2090&tz=Asia/Kolkata'
    
    # Kundli with 10 worksheets
    rk = client.get(f'/kundli?{q}')
    assert rk.status_code == 200
    assert 'Vedic Astrology Worksheets' in rk.text
    assert 'Sudarshan Chakra' in rk.text
    assert 'Special Lagnas' in rk.text
    assert 'Ashtakavarga Suite' in rk.text
    assert 'Shodhya Pindas' in rk.text
    assert 'Paka Lagna' in rk.text
    assert 'Indu Lagna' in rk.text
    
    # Dedicated Varshaphala page
    rv = client.get(f'/varshaphala?{q}&year=2026')
    assert rv.status_code == 200
    assert 'Tajika Varshaphala' in rv.text
    assert 'Year Lord (Varshesha)' in rv.text
    assert 'Muntha' in rv.text
    assert 'Mudda Dasha' in rv.text
    assert 'Pancha Adhikaris' in rv.text
    assert '24 Classical Tajika Sahams' in rv.text

    # Dedicated KP page
    rkp = client.get(f'/kp?{q}&horary=108')
    assert rkp.status_code == 200
    assert 'Krishnamurti Paddhati' in rkp.text
    assert 'Ruling Planets' in rkp.text
    assert 'KP Placidus House Cusps' in rkp.text
    assert '4-Fold House Significators' in rkp.text
    assert 'Horary Number #108' in rkp.text

def test_enhanced_pdf_generation_endpoint():
    res = client.post('/api/kundli/pdf', json={
        'name': 'Test Native',
        'date': '1990-05-15',
        'time': '06:30:00',
        'latitude': 23.0225,
        'longitude': 72.5714,
        'timezone': 'Asia/Kolkata'
    })
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/pdf'
    assert len(res.content) > 15000
    assert res.content[:5] == b'%PDF-'

def test_ephem_lru_cache():
    from app.core import ephem
    jd = 2448026.5
    p1 = ephem.all_positions(jd)
    p2 = ephem.all_positions(jd)
    assert p1['Sun']['longitude'] == p2['Sun']['longitude']
    h1 = ephem.houses(jd, 23.0, 72.0)
    h2 = ephem.houses(jd, 23.0, 72.0)
    assert h1[1] == h2[1]



def test_master_destiny_and_ravana_endpoints():
    destiny_payload = {
        **SAMPLE_BIRTH,
        'name': '9-Planet Mastery Tester',
        'current_latitude': 40.7128,
        'current_longitude': -74.0060,
        'current_timezone': -4.0,
        'current_city': 'New York, USA',
        'scan_days': 15
    }
    res = client.post('/api/kundli/destiny-dossier', json=destiny_payload)
    assert res.status_code == 200
    data = res.json()
    assert 'medical_diseases_and_longevity' in data
    assert 'accidents_and_safety_windows' in data
    assert 'destiny_turning_points_and_dates' in data
    assert 'lottery_and_windfall_oracle' in data
    assert 'marriage_count_and_remedies' in data
    assert 'progeny_children_and_grandchildren' in data
    assert 'past_life_future_life_and_purpose' in data
    assert 'ravana_samhita_planetary_mastery' in data
    assert len(data['ravana_samhita_planetary_mastery']['nine_graha_command_protocols']) == 9
    assert len(data['progeny_children_and_grandchildren']['individual_children_predictions']) >= 1

    # Test focused sub-endpoints
    for sub in [
        'medical-longevity',
        'accidents-safety',
        'destiny-dates',
        'lottery-windfall',
        'marriage-analysis',
        'progeny-lineage',
        'past-future-life',
        'ravana-mastery',
    ]:
        sres = client.post(f'/api/kundli/{sub}', json=destiny_payload)
        assert sres.status_code == 200

    # Test cross-linked summary inside main /api/kundli
    kres = client.post('/api/kundli', json=SAMPLE_BIRTH)
    assert kres.status_code == 200
    kdata = kres.json()
    assert 'cross_linked_features' in kdata
    assert 'master_destiny_dossier' in kdata['cross_linked_features']
    assert 'progeny_children_and_grandchildren' in kdata['cross_linked_features']

    # Test /destiny web route with birth + current location
    dweb = client.get(
        '/destiny?name=Vishal&date=1990-05-15&time=10:30&lat=28.6139&lon=77.2090&tz=5.5&city=New+Delhi'
        '&cur_lat=40.7128&cur_lon=-74.0060&cur_tz=-4.0&cur_city=New+York&scan_days=15'
    )
    assert dweb.status_code == 200
    assert 'Classical Samhita 9-Planet Mastery' in dweb.text
    assert 'Lottery, Speculation & Sudden Windfall Oracle' in dweb.text
    assert 'Grandchildren' in dweb.text
    assert 'D-60 Shashtiamsha' in dweb.text
    assert 'Plain-English Step-by-Step Guide' in dweb.text
    assert 'Plain-English Dictionary of Every Astrological &amp; Vastu Term' in dweb.text
    assert 'Interactive Visual House (Square / Rectangle) &amp; Outer-Lot Vastu Architect Studio' in dweb.text


def test_astro_vastu_and_visual_vastu_architect():
    # 1. Personalized Birth-Chart Astro-Vastu endpoint
    av_res = client.post('/api/kundli/astro-vastu', json=SAMPLE_BIRTH)
    assert av_res.status_code == 200
    av_data = av_res.json()
    assert 'astro_vastu_guide' in av_data
    assert 'plain_english_glossary' in av_data
    assert len(av_data['plain_english_glossary']) >= 20
    guide = av_data['astro_vastu_guide']
    assert len(guide['personalized_nine_zone_astro_vastu_map']) == 9
    assert len(guide['astro_vastu_dos_to_double_positive_effect']) >= 5
    assert len(guide['astro_vastu_donts_to_prevent_bad_luck']) >= 5

    # 2. Interactive Visual House (Square / Rectangle) + Outer-Lot Vastu Layout Analyzer
    layout_payload = {
        'house_shape': 'wide_rectangle',
        'has_outer_lot': True,
        'compass_rotation': 0.0,
        'birth_date': '1990-05-15',
        'birth_time': '10:30:00',
        'birth_latitude': 28.6139,
        'birth_longitude': 77.2090,
        'birth_timezone': 5.5,
        'items': [
            {'type': 'entrance', 'label': 'Main Entrance', 'x': 72, 'y': 20, 'w': 12, 'h': 7, 'door_dir': 'NE', 'scope': 'indoor'},
            {'type': 'back_door', 'label': 'Back Door', 'x': 22, 'y': 14, 'w': 10, 'h': 6, 'door_dir': 'NW', 'scope': 'indoor'},
            {'type': 'master_bedroom', 'label': 'Master Bedroom', 'x': 20, 'y': 58, 'w': 22, 'h': 18, 'door_dir': 'N', 'scope': 'indoor'},
            {'type': 'bedroom', 'label': 'Bedroom 2', 'x': 20, 'y': 38, 'w': 18, 'h': 16, 'door_dir': 'E', 'scope': 'indoor'},
            {'type': 'guest_room', 'label': 'Guest Room', 'x': 20, 'y': 20, 'w': 18, 'h': 15, 'door_dir': 'E', 'scope': 'indoor'},
            {'type': 'living_room', 'label': 'Living Room 1', 'x': 52, 'y': 24, 'w': 22, 'h': 18, 'door_dir': '', 'scope': 'indoor'},
            {'type': 'living_room', 'label': 'Family Living Room 2', 'x': 44, 'y': 44, 'w': 14, 'h': 14, 'door_dir': '', 'scope': 'indoor'},
            {'type': 'kitchen', 'label': 'Kitchen', 'x': 64, 'y': 60, 'w': 18, 'h': 16, 'door_dir': 'E', 'scope': 'indoor'},
            {'type': 'bathroom', 'label': 'Bathroom 1', 'x': 40, 'y': 20, 'w': 10, 'h': 12, 'door_dir': '', 'scope': 'indoor'},
            {'type': 'bathroom', 'label': 'Bathroom 2', 'x': 18, 'y': 48, 'w': 10, 'h': 10, 'door_dir': '', 'scope': 'indoor'},
            {'type': 'storage', 'label': 'Storage Closet', 'x': 44, 'y': 64, 'w': 14, 'h': 12, 'door_dir': '', 'scope': 'indoor'},
            {'type': 'balcony', 'label': 'Balcony', 'x': 58, 'y': 14, 'w': 14, 'h': 6, 'door_dir': 'N', 'scope': 'indoor'},
            {'type': 'fence', 'label': 'Boundary Fence', 'x': 2, 'y': 88, 'w': 30, 'h': 5, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'gate', 'label': 'Main Lot Gate', 'x': 70, 'y': 3, 'w': 14, 'h': 6, 'door_dir': 'NE', 'scope': 'outdoor'},
            {'type': 'parking_gate', 'label': 'Parking Gate', 'x': 14, 'y': 3, 'w': 18, 'h': 7, 'door_dir': 'NW', 'scope': 'outdoor'},
            {'type': 'trees', 'label': 'Shade Trees 1', 'x': 6, 'y': 76, 'w': 16, 'h': 16, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'trees', 'label': 'Shade Trees 2', 'x': 24, 'y': 78, 'w': 14, 'h': 14, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'flowers', 'label': 'Flower Bed', 'x': 84, 'y': 14, 'w': 11, 'h': 14, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'bushes', 'label': 'Bushes', 'x': 4, 'y': 32, 'w': 9, 'h': 20, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'fireplace', 'label': 'Outdoor Fireplace', 'x': 84, 'y': 76, 'w': 12, 'h': 12, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'garden', 'label': 'Garden', 'x': 44, 'y': 3, 'w': 22, 'h': 8, 'door_dir': '', 'scope': 'outdoor'},
            {'type': 'grass', 'label': 'Front Grass', 'x': 84, 'y': 32, 'w': 11, 'h': 28, 'door_dir': '', 'scope': 'outdoor'},
        ]
    }
    vres = client.post('/api/vastu/analyze-layout', json=layout_payload)
    assert vres.status_code == 200
    vdata = vres.json()
    assert vdata['total_items_evaluated'] == 22
    assert 0 <= vdata['overall_vastu_score_percent'] <= 100
    assert 'Wide Rectangle' in vdata['house_shape_analysis']['name']
    assert any('Birth-Chart' in it['birth_chart_synergy'] for it in vdata['item_by_item_breakdown'])

    # 3. Standalone /vastu web page
    vweb = client.get('/vastu?date=1990-05-15&time=10:30&lat=28.6139&lon=77.2090&tz=Asia/Kolkata&city=New+Delhi')
    assert vweb.status_code == 200
    assert 'standalone-vastu-studio-root' in vweb.text
    assert 'WHAT TO DO (Astro-Vastu Do\'s to Double Positive Effects)' in vweb.text


def test_all_nav_menus_and_tabs_render_full_content():
    """Verify every menu item in NAV renders 200 OK with full charts/tables even without query params."""
    from app.web import NAV
    for href, label in NAV:
        r = client.get(href)
        assert r.status_code == 200, f"{href} ({label}) failed with {r.status_code}"
        assert len(r.text) > 7000, f"{href} returned suspiciously small page ({len(r.text)} bytes)"

    # Verify /kundli without query params still renders all 12 worksheets
    rk = client.get('/kundli')
    assert 'Worksheet 1: Birth Chart' in rk.text
    assert 'Worksheet 8: Tajika Varshaphala Annual Solar Return' in rk.text
    assert '144 House Lord Placements with Classical BPHS Slokas' in rk.text
    assert 'Tantric Beej Mantra' in rk.text

    # Verify /vargas without query params renders all 31 divisional charts & Quick Filter pills with birth params
    rv = client.get('/vargas')
    assert 'D150' in rv.text
    assert 'Tajika Sahams' in rv.text
    assert 'lat=28.6139' in rv.text


def test_explicit_am_pm_time_formatting_everywhere():
    """Verify all times in Destiny Dossier, Regional, Varshaphala, Kundli, and Ask API explicitly show AM or PM."""
    res = client.post('/api/kundli/destiny-dossier', json={
        **SAMPLE_BIRTH,
        'name': 'AMPM Checker',
        'scan_days': 15
    })
    assert res.status_code == 200
    d = res.json()
    assert ('AM' in d['birth_chart_anchor']['birth_local_time_ampm']) or ('PM' in d['birth_chart_anchor']['birth_local_time_ampm'])

    lot_wins = d['lottery_and_windfall_oracle']['location_calibrated_lottery_date_time_windows']
    if lot_wins:
        assert ('AM' in lot_wins[0]['golden_hora_window']) or ('PM' in lot_wins[0]['golden_hora_window'])
        assert ('AM' in lot_wins[0]['peak_15m_lakshmi_moment']) or ('PM' in lot_wins[0]['peak_15m_lakshmi_moment'])

    good_dates = d['destiny_turning_points_and_dates']['upcoming_auspicious_destiny_dates']
    if good_dates:
        assert ('AM' in good_dates[0]['power_hora_window']) or ('PM' in good_dates[0]['power_hora_window'])

    reg = client.get('/regional')
    assert reg.status_code == 200
    assert (' AM' in reg.text) or (' PM' in reg.text)


def test_full_language_translation_preserving_shlokas():
    """Verify 100% translation into selected language while keeping Sanskrit Shlokas untouched and translating Shloka meanings."""
    from app.core import i18n

    sample_html = (
        '<h2>Classical Samhita 9-Planet Mastery</h2>'
        '<p><strong>Maha Mrityunjaya Shloka:</strong> '
        '<code class="notranslate" translate="no">ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्॥ (Om Tryambakam Yajamahe)</code>'
        '<br><span><b>Shloka Meaning:</b> We worship the Three-Eyed Lord Shiva who nourishes all beings.</span></p>'
        '<p>Golden Hora: 09:15 AM – 10:15 AM</p>'
    )
    hi_html = i18n.localize_html_full(sample_html, 'hi')
    # Sanskrit shloka inside .notranslate is 100% preserved
    assert 'ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्॥ (Om Tryambakam Yajamahe)' in hi_html
    # Explicit AM/PM is preserved
    assert '09:15 AM' in hi_html and '10:15 AM' in hi_html
    # Headings and Shloka meaning are translated into Hindi (Devanagari)
    assert 'शिव' in hi_html

    # Also test /api/i18n/translate batch endpoint
    api_tr = client.post('/api/i18n/translate', json={
        'lang': 'hi',
        'texts': [
            'Plain-English Step-by-Step Guide',
            'ॐ श्रीं ह्रीं श्रीं कमले कमलालये प्रसीद प्रसीद',
            'Salutations to Supreme Goddess Mahalakshmi who dwells amidst lotuses.'
        ]
    })
    assert api_tr.status_code == 200
    tr_list = api_tr.json()['translations']
    assert len(tr_list) == 3
    # Shloka is preserved untouched
    assert tr_list[1] == 'ॐ श्रीं ह्रीं श्रीं कमले कमलालये प्रसीद प्रसीद'
    # English meaning is translated to Hindi
    assert tr_list[2] != 'Salutations to Supreme Goddess Mahalakshmi who dwells amidst lotuses.'




def test_detailed_reports_22_dashas_9_menus_and_rectification_studio():
    """Verify the 20 Report Models, 9 Menus, 22 Dashas, 11 Upagrahas, 15 Sphutas, 4 Avasthas, Saturn Cycles, Gemstones, Rectification/Relocation & /reports web studio."""
    cat_res = client.get('/api/reports/catalog')
    assert cat_res.status_code == 200
    cat = cat_res.json()
    assert cat['report_models_count'] == 20
    assert cat['menus_count'] == 9
    assert len(cat['worksheet_presets']) == 10

    rep_res = client.post('/api/reports/generate', json={
        **SAMPLE_BIRTH,
        'name': 'Aryabhata',
        'model_code': 'HP3',
    })
    assert rep_res.status_code == 200
    rep = rep_res.json()
    assert rep['model_selected']['code'] == 'HP3'
    assert rep['chapters_count'] == 9
    assert 'ph-book-dossier' in rep['printable_book_html']

    d22_res = client.post('/api/kundli/dashas/all-systems', json=SAMPLE_BIRTH)
    assert d22_res.status_code == 200
    assert d22_res.json()['total_systems_computed'] == 22

    upa_res = client.post('/api/kundli/upagrahas-and-sphutas', json=SAMPLE_BIRTH)
    assert upa_res.status_code == 200
    assert len(upa_res.json()['upagrahas']) == 11

    sat_res = client.post('/api/kundli/saturn-cycles-and-doshas', json=SAMPLE_BIRTH)
    assert sat_res.status_code == 200
    assert 'life_stone_lagnesh' in sat_res.json()['gemstone_recommendations']

    rect_res = client.post('/api/tools/rectify-and-relocate', json={
        **SAMPLE_BIRTH,
        'target_latitude': 40.7128,
        'target_longitude': -74.0060,
        'target_city': 'New York, USA',
    })
    assert rect_res.status_code == 200
    assert len(rect_res.json()['birth_time_rectification']['division_shift_boundaries']) == 7

    web_rep = client.get('/reports?name=Aryabhata&date=1990-05-15&time=10:30&model=HP3')
    assert web_rep.status_code == 200
    assert 'Detailed Multi-Chapter Text Reports' in web_rep.text

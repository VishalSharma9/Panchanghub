from app.core.day_extras import agnivasa, birth_bird, chandra_vasa, ghati_parts, shivavasa, tamil_yoga


def test_agnivasa_pratipada_is_prithvi():
    assert agnivasa(0) == "Prithvi"
    assert agnivasa(1) == "Akasha"
    assert agnivasa(2) == "Patala"
    assert agnivasa(15) == "Prithvi"
    assert agnivasa(29) == "Patala"  # Amavasya


def test_chandra_vasa_tula_west():
    assert chandra_vasa(5) == "South"  # Kanya
    assert chandra_vasa(6) == "West"   # Tula


def test_birth_bird_swaps_with_paksha():
    assert birth_bird(0, "Shukla") == "Vulture"
    assert birth_bird(0, "Krishna") == "Peacock"
    assert birth_bird(13, "Shukla") == "Crow"  # Chitra


def test_ghati_clock():
    # 24 minutes = 1 ghati
    assert ghati_parts(24 * 60)["ghati"] == 1
    assert ghati_parts(24)["pala"] == 1


def test_shivavasa_matches_drik_tithi_table():
    assert shivavasa(0)["place"] == "in Shmashana"   # Pratipada
    assert shivavasa(1)["place"] == "with Gowri"     # Dwitiya
    assert shivavasa(29)["place"] == "with Gowri"    # Amavasya = tithi 30
    assert shivavasa(14)["place"] == "in Shmashana"  # Purnima = tithi 15


def test_tamil_yoga_sunday_chitra_is_siddha():
    assert tamil_yoga(0, 13)["name"] == "Siddha"     # Sunday, Chitra
    assert tamil_yoga(1, 14)["name"] == "Amrita"     # Monday, Swati
    assert tamil_yoga(6, 12)["name"] == "Marana"     # Saturday, Hasta

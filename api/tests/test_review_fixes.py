"""Guards for the Vastu, Feng Shui, and palmistry contract fixes."""
import pytest
from fastapi import HTTPException

from app.core.astro_vastu_engine import (
    _kua_number, _coord_to_zone, _segment_hits_brahmasthan,
    compute_classical_feng_shui, evaluate_visual_vastu_layout,
)
from app.core.palmistry_vision import analyze_palm_photo, PalmInputError


def test_female_kua_uses_plus_five_before_2000():
    assert _kua_number(1980, "female") == 4
    assert _kua_number(1980, "male") == 2
    assert _kua_number(2000, "male") == 9
    assert _kua_number(2000, "female") == 6


def test_feng_shui_endpoint_shape_keeps_the_birthday():
    out = compute_classical_feng_shui(1980, 5, 15, "female", facing="E", sitting="W")
    assert out["kua_number"] == 4
    assert out["flying_stars_chart"]["facing"] == "E"
    assert out["flying_stars_chart"]["resolution"] == "8-palace"
    animals = {a["guardian"]: a["direction"] for a in out["form_school_four_celestial_animals"]}
    assert animals["Red Phoenix"] == "E"
    assert animals["Black Tortoise"] == "W"
    assert animals["Green Dragon"] == "N"


def test_brahmasthan_is_the_central_third():
    assert _coord_to_zone(50, 50) == "Center"
    assert _coord_to_zone(40, 40) == "Center"
    assert _coord_to_zone(20, 20) != "Center"
    assert _segment_hits_brahmasthan(10, 50, 90, 50) is True
    assert _segment_hits_brahmasthan(10, 10, 20, 20) is False


def test_unknown_room_is_rejected_and_blocking_caps_the_score():
    with pytest.raises(ValueError):
        evaluate_visual_vastu_layout([{"type": "not_a_room", "x": 10, "y": 10, "w": 8, "h": 8}])
    scored = evaluate_visual_vastu_layout([
        {"type": "bathroom", "x": 40, "y": 5, "w": 10, "h": 10},
        {"type": "flowers", "x": 5, "y": 5, "w": 8, "h": 8},
    ])
    assert scored["score_breakdown"]["blocking_cap_applied"] is True
    assert scored["overall_score"] <= 45


def test_empty_palm_is_not_a_reading():
    with pytest.raises(PalmInputError):
        analyze_palm_photo()


def test_explicit_palm_does_not_invent_a_photo():
    out = analyze_palm_photo(hand_shape="earth", heart_line="straight", head_line="long", life_line="deep", fate_line="clear")
    assert out["extracted_palm_profile"]["has_uploaded_photo"] is False
    assert out["extracted_palm_profile"]["detection_method"] == "explicit"
    assert any(w["code"] == "BIRTH_NOT_SENT" for w in out["warnings"])


def test_layout_route_rejects_unknown_type():
    from app.api.routers.vedic import analyze_visual_vastu_layout_endpoint
    from app.models import VisualVastuLayoutRequest
    req = VisualVastuLayoutRequest(items=[{"type": "spaceship", "x": 10, "y": 10, "w": 5, "h": 5}])
    with pytest.raises(HTTPException) as caught:
        analyze_visual_vastu_layout_endpoint(req)
    assert caught.value.status_code == 422


def test_site_rules_cap_a_cut_ne_plot():
    scored = evaluate_visual_vastu_layout(
        [
            {"type": "entrance", "x": 40, "y": 5, "w": 10, "h": 6, "door_dir": "N", "entrance_pada": 1},
            {"type": "bathroom", "x": 60, "y": 60, "w": 10, "h": 10, "floor": 2},
            {"type": "kitchen", "x": 62, "y": 62, "w": 12, "h": 10, "floor": 0},
        ],
        land_high="NE",
        plot_cuts=["NE"],
        roads=[{"hits": "NE_corner"}],
    )
    ids = {f["rule_id"] for f in scored["site_findings"]}
    assert {"vastu.land_slope", "vastu.plot_cut", "vastu.veedhi_shoola", "vastu.toilet_above_kitchen"} <= ids
    assert scored["overall_score"] <= 45

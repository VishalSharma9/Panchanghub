from __future__ import annotations
from datetime import date as Date, datetime, time as Time
from typing import Any, List, Literal, Optional
from zoneinfo import ZoneInfo, available_timezones
from pydantic import BaseModel, Field, field_validator, model_validator

_TZS = None
def valid_tz(tz: str) -> str:
    global _TZS
    if _TZS is None: _TZS = available_timezones()
    if tz not in _TZS: raise ValueError(f"unknown IANA timezone '{tz}'")
    return tz


def normalize_date_str(v, default="1990-05-15"):
    """Repair a 5-digit year typo and clamp an impossible calendar day."""
    if isinstance(v, Date):
        return v
    if not isinstance(v, str) or not v.strip():
        return default
    s = v.strip()
    parts = s.split("-")
    if len(parts) == 3:
        y_raw, m_raw, d_raw = parts[0].lstrip("+"), parts[1], parts[2][:2]
        if len(y_raw) > 4 and y_raw.isdigit():
            if y_raw.startswith("0") and len(y_raw) == 5:
                y_raw = y_raw[1:]
            elif y_raw[:2] in ("18", "19", "20"):
                y_raw = y_raw[:2] + y_raw[-2:]
            else:
                y_raw = y_raw[:4]
        try:
            y_i = max(1, min(3000, int(y_raw)))
            m_i = max(1, min(12, int(m_raw)))
            d_i = max(1, min(31, int(d_raw)))
            for dd in range(d_i, 27, -1):
                try:
                    return Date(y_i, m_i, dd).isoformat()
                except ValueError:
                    continue
        except ValueError:
            return default
    return default

class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, examples=[28.6139])
    longitude: float = Field(..., ge=-180, le=180, examples=[77.2090])
    timezone: Optional[str] = Field(None, description="IANA timezone, e.g. Asia/Kolkata", examples=["Asia/Kolkata"])
    utc_offset: Optional[float] = Field(None, ge=-14, le=14, description="Hours east of UTC, used if timezone omitted")

    @field_validator("timezone")
    @classmethod
    def _tz(cls, v):
        return valid_tz(v) if v else v

    @model_validator(mode="after")
    def _need(self):
        if self.timezone is None and self.utc_offset is None:
            raise ValueError("provide either timezone or utc_offset")
        return self

class BirthData(Location):
    date: Date = Field(..., examples=["1990-05-15"])
    time: Time = Field(..., examples=["10:30:00"])

_OLD_MEAN = "lahiri_" + "sw" + "iss"

def _public_ayan(v):
    # Older clients used a non-Indian label on Lahiri. Keep Lahiri; do not store that label.
    return "lahiri_mean" if v == _OLD_MEAN else v

class ChartRequest(BirthData):
    system: Literal["tropical", "sidereal"] = "tropical"
    house_system: Optional[Literal["placidus", "koch", "equal", "whole_sign", "porphyry", "regiomontanus", "campanus"]] = Field(
        None, description="Default: placidus (tropical) / whole_sign (sidereal)")
    true_node: bool = False
    ayanamsa: Literal["lahiri", "lahiri_mean", "raman", "kp", "true_chitra", "fagan_bradley"] = "lahiri"

    @field_validator("ayanamsa", mode="before")
    @classmethod
    def _ayan_alias(cls, v):
        return _public_ayan(v)

class KundliRequest(BirthData):
    name: Optional[str] = Field(None, max_length=100)
    house_system: Literal["whole_sign", "placidus", "equal"] = "whole_sign"
    true_node: bool = False
    dasha_levels: int = Field(3, ge=1, le=3)
    ayanamsa: Literal["lahiri", "lahiri_mean", "raman", "kp", "true_chitra"] = "lahiri"
    target_date: Optional[Date] = Field(None, description="Date used for the running dasha. Defaults to today.")

    @field_validator("ayanamsa", mode="before")
    @classmethod
    def _ayan_alias(cls, v):
        return _public_ayan(v)

class MatchRequest(BaseModel):
    boy: BirthData
    girl: BirthData

class VarshaphalaRequest(KundliRequest):
    year: Optional[int] = Field(None, description="Year for which Solar Return (Varshaphala) is computed. Defaults to current year.")

class KPRequest(KundliRequest):
    horary_number: Optional[int] = Field(None, ge=1, le=249, description="Optional KP Horary Prashna number (1-249)")

class PrashnaRequest(BaseModel):
    date: Optional[Date] = Field(None, description="Date of query (defaults to current date)")
    time: Optional[Time] = Field(None, description="Time of query (defaults to current time)")
    latitude: float = Field(..., ge=-90, le=90, examples=[28.6139])
    longitude: float = Field(..., ge=-180, le=180, examples=[77.2090])
    timezone: Optional[str] = Field("Asia/Kolkata", description="IANA timezone")
    utc_offset: Optional[float] = Field(None, ge=-14, le=14)
    query_category: Literal["career", "marriage", "finance", "health", "children", "property", "travel", "litigation"] = Field(
        "career", description="Classical horary question domain"
    )
    question_text: Optional[str] = Field(None, description="Optional natural language query text")

class DestinyRequest(KundliRequest):
    current_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Current living/travel latitude for location-calibrated hours & dates")
    current_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Current living/travel longitude for location-calibrated hours & dates")
    current_timezone: Optional[str | float] = Field(None, description="Current location IANA timezone (e.g. America/New_York) or UTC offset in hours")
    current_utc_offset: Optional[float] = Field(None, ge=-14, le=14, description="Current location UTC offset in hours")
    current_city: Optional[str] = Field(None, description="Current city display name")
    scan_days: int = Field(30, ge=7, le=180, description="Number of upcoming days to scan for lottery, accident, and destiny date-time windows")
    gender: Optional[str] = Field("male", description="Gender ('male' or 'female') for Feng Shui Kua & classical calibrations")
    sections: Optional[List[str]] = Field(None, description="Optional list of sections/traditions to include in filtered report")

    @model_validator(mode="after")
    def _normalize_current_tz(self):
        if isinstance(self.current_timezone, (int, float)):
            if self.current_utc_offset is None:
                self.current_utc_offset = float(self.current_timezone)
            self.current_timezone = None
        elif isinstance(self.current_timezone, str):
            try:
                val = float(self.current_timezone)
                if self.current_utc_offset is None:
                    self.current_utc_offset = val
                self.current_timezone = None
            except ValueError:
                pass
        return self


class TraditionsReportRequest(KundliRequest):
    gender: Optional[str] = Field("male", description="Gender ('male' or 'female') used for Classical Feng Shui Kua & Nadi leaf calibrations")
    focus_mode: Optional[str] = Field("all", description="Filter report focus: personal_insight, event_prediction, remedies_and_healing, or all")
    goal: Optional[str] = Field(None, description="Alias for focus_mode")
    school_preference: Optional[str] = Field("all", description="Filter by eastern_vedic, western, global_cultural, holistic_balance, or all")
    approach: Optional[str] = Field(None, description="Alias for school_preference")
    selected_traditions: Optional[List[str]] = Field(None, description="Optional list of specific traditions to include")
    traditions: Optional[List[str]] = Field(None, description="Alias for selected_traditions")
    sitting: Optional[str] = Field(None, description="House sitting direction, opposite the front door")
    facing: Optional[str] = Field(None, description="Direction the front door faces")


class PalmistryPhotoRequest(BaseModel):
    image_base64: Optional[str] = Field(None, description="Base64 data URL or raw base64 of the palm photo")
    thumb_image_base64: Optional[str] = Field(None, description="Optional base64 data URL or raw base64 of the thumbprint close-up")
    hand_side: Optional[str] = Field("right", description="Which hand is photographed ('right' or 'left')")
    active_spectrum: Optional[str] = Field("ridge_enhance", description="Selected spectrum mode for primary display")
    hand_shape: Optional[str] = Field(None, description="Optional manual override for hand shape (earth, air, fire, water)")
    heart_line: Optional[str] = Field(None, description="Optional manual override for heart line (curved, straight, chained, broken)")
    head_line: Optional[str] = Field(None, description="Optional manual override for head line (long, short, sloping, joined)")
    life_line: Optional[str] = Field(None, description="Optional manual override for life line (deep, wide, faint, double)")
    fate_line: Optional[str] = Field(None, description="Optional manual override for fate line (clear, broken, absent, late)")
    thumbprint_type: Optional[str] = Field(None, description="Optional manual override for thumbprint (shankha_loop, chakra_whorl, padma_arch, simha_composite)")
    image_metrics: Optional[dict] = Field(None, description="Optional client-extracted image metrics")
    thumb_metrics: Optional[dict] = Field(None, description="Optional client-extracted thumbprint metrics")
    detected_features: Optional[dict] = Field(None, description="Optional client-detected features")
    birth_date: Optional[str] = Field(None, description="Optional birth date YYYY-MM-DD to cross-link with Lal Kitab, Nadi & Tridosha")
    date: Optional[str] = Field(None, description="Alias for birth_date")
    birth_time: Optional[str] = Field("10:30:00", description="Optional birth time HH:MM:SS")
    time: Optional[str] = Field(None, description="Alias for birth_time")
    latitude: Optional[float] = Field(None, description="Birth latitude. Omit to skip the chart link.")
    longitude: Optional[float] = Field(None, description="Birth longitude. Omit to skip the chart link.")
    timezone: Optional[str] = Field(None, description="Birth timezone")
    utc_offset: Optional[float] = Field(None, description="Optional UTC offset")
    gender: Optional[str] = Field("male", description="Optional gender ('male' or 'female') for Feng Shui Kua & Vastu synthesis")


class VastuPlacedItemModel(BaseModel):
    model_config = {"extra": "allow"}
    id: Optional[int | str] = Field(None, description="Unique block ID")
    type: str = Field("living_room", description="Item type key from /api/vastu/catalog (e.g. puja_room, meditation_hall, medication_cabinet, gym_room, storage, grain_pantry, washer_dryer, kitchen_stove, indoor_taps, water_hose, kids_slide, trench_ditch, gate, parking_gate, side_pedestrian_gate, photo_living, photo_deceased, photo_gods, tv_screen, wall_mirror, wall_clock)")
    label: Optional[str] = Field(None, description="Custom label for the room or fixture")
    x: float = Field(50.0, description="Left X coordinate percentage (0-100)")
    y: float = Field(50.0, description="Top Y coordinate percentage (0-100)")
    w: float = Field(12.0, description="Width percentage (1-100)")
    h: float = Field(10.0, description="Height percentage (1-100)")
    door_dir: Optional[str] = Field("", description="Door, gate, cook, photo, or TV facing direction ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')")
    cook_facing: Optional[str] = Field("", description="Direction the cook faces at the stove")
    bed_head: Optional[str] = Field("", description="Direction the head of the bed points")
    desk_facing: Optional[str] = Field("", description="Direction a study desk faces")
    stair_turn: Optional[str] = Field("", description="clockwise or counter-clockwise as you climb")
    water_kind: Optional[str] = Field("", description="pool, well, bore, or sump")
    floor: Optional[int] = Field(0, description="Floor index. A higher toilet over a kitchen is flagged.")
    entrance_pada: Optional[int] = Field(None, description="1-9 door segment, counted left to right from outside")
    gate_mech: Optional[str] = Field("", description="Gate/door opening or sliding mechanism ('swing_in_cw', 'swing_in_ccw', 'double_in', 'swing_out', 'slide_ne', 'slide_sw', 'rollup')")
    wall_side: Optional[str] = Field("", description="Wall mounting side for photo frames, TV, mirror, clock ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')")
    flow_dir: Optional[str] = Field("", description="Drainage flow/slope direction for trenches/ditches ('NE', 'N', 'E', 'NW', 'SE', 'W', 'S', 'SW', 'stagnant')")
    scope: Optional[str] = Field("indoor", description="Placement scope ('indoor', 'outdoor', 'outside_boundary')")


class VastuWallLineModel(BaseModel):
    model_config = {"extra": "allow"}
    id: Optional[int | str] = None
    label: Optional[str] = Field("Interior Wall Line", description="Wall label")
    x1: float = Field(20.0, description="Start X coordinate (0-100)")
    y1: float = Field(50.0, description="Start Y coordinate (0-100)")
    x2: float = Field(80.0, description="End X coordinate (0-100)")
    y2: float = Field(50.0, description="End Y coordinate (0-100)")
    wall_type: Optional[str] = Field("partition", description="'partition' or 'load_bearing'")


class VastuFenceLoopModel(BaseModel):
    model_config = {"extra": "allow"}
    id: Optional[int | str] = None
    label: Optional[str] = Field("Perimeter Fence Loop", description="Fence loop label")
    closed: bool = Field(True, description="True for a 360-degree closed fence loop, False for an open loop")
    open_side: Optional[str] = Field("", description="If open loop, which compass side is open ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')")
    points: List[dict] = Field(default_factory=list, description="List of {'x': float, 'y': float} vertices in 0-100 coordinates")


class VisualVastuLayoutRequest(BaseModel):
    model_config = {"extra": "allow"}
    house_shape: str = Field("square", description="'square', 'wide_rectangle', or 'deep_rectangle'")
    has_outer_lot: bool = Field(True, description="Whether outer property lot/boundary items and perimeter fence are active")
    compass_rotation: float = Field(0.0, description="Compass rotation degrees from True North at top (0, 45, 90, 135, 180, 225, 270, 315)")
    items: Optional[List[VastuPlacedItemModel | dict]] = Field(None, description="Placed indoor/outdoor rooms, fixtures, photo frames, TV, gates, trenches, etc. If omitted or empty and use_chart_ideal_preset_if_empty=True, uses the native's Birth-Chart Ideal Preset.")
    walls: Optional[List[VastuWallLineModel | dict]] = Field(None, description="Drawn interior/exterior wall lines")
    fences: Optional[List[VastuFenceLoopModel | dict]] = Field(None, description="Perimeter fence loops (closed 360-degree loop or open loop)")
    use_chart_ideal_preset_if_empty: bool = Field(False, description="If True and items is empty/omitted, automatically populates the Birth-Chart Ideal Vastu & Feng Shui arrangement")
    # Birth chart calibration fields
    date: Optional[str] = Field(None, description="Birth date YYYY-MM-DD for Astro-Vastu & Feng Shui Kua calibration")
    birth_date: Optional[str] = Field(None, description="Alias for date")
    time: Optional[str] = Field("10:30:00", description="Birth time HH:MM:SS")
    birth_time: Optional[str] = Field(None, description="Alias for time")
    latitude: Optional[float] = Field(None, description="Birth latitude")
    lat: Optional[float] = Field(None, description="Alias for latitude")
    birth_latitude: Optional[float] = Field(None, description="Alias for latitude")
    longitude: Optional[float] = Field(None, description="Birth longitude")
    lon: Optional[float] = Field(None, description="Alias for longitude")
    birth_longitude: Optional[float] = Field(None, description="Alias for longitude")
    timezone: Optional[str | float] = Field("Asia/Kolkata", description="Birth timezone IANA name or UTC offset")
    tz: Optional[str | float] = Field(None, description="Alias for timezone")
    birth_timezone: Optional[str | float] = Field(None, description="Alias for timezone")
    gender: Optional[str] = Field("male", description="Gender ('male' or 'female') for Classical Feng Shui Kua & Eight Mansions")
    sitting: Optional[str] = Field(None, description="House sitting direction")
    facing: Optional[str] = Field(None, description="Direction the front door faces")
    land_high: Optional[str] = Field(None, description="Compass side where the plot is highest")
    roads: Optional[List[dict]] = Field(None, description="Roads hitting the plot")
    plot_cuts: Optional[List[str]] = Field(None, description="Missing plot corners")
    plot_extensions: Optional[List[str]] = Field(None, description="Plot corners that stick out")
    # Optional Palmistry photo or profile to combine Palm + Birth Chart + Vastu in a single API call
    palm_data: Optional[dict] = Field(None, description="Optional extracted palm profile (hand_shape, life_line, head_line, heart_line, fate_line, thumbprint_type) or dict containing image_base64")
    palm_image_base64: Optional[str] = Field(None, description="Optional base64 palm photo to analyze via Computer Vision and combine directly with Birth Chart & Vastu")
    thumb_image_base64: Optional[str] = Field(None, description="Optional base64 thumbprint close-up photo")
    hand_shape: Optional[str] = Field(None, description="Optional direct palm hand shape override (fire, earth, air, water)")
    life_line: Optional[str] = Field(None, description="Optional direct palm life line override (deep, wide, double, faint)")
    head_line: Optional[str] = Field(None, description="Optional direct palm head line override (long, straight, sloping, short)")
    heart_line: Optional[str] = Field(None, description="Optional direct palm heart line override (curved, straight, chained, broken)")
    fate_line: Optional[str] = Field(None, description="Optional direct palm fate line override (clear, late, broken, absent)")
    thumbprint_type: Optional[str] = Field(None, description="Optional direct Nadi thumbprint override (chakra_whorl, shankha_loop, padma_arch, simha_composite)")








class DetailedReportRequest(KundliRequest):
    gender: Optional[str] = Field("male", description="Native gender ('male' or 'female')")
    model_code: Optional[str] = Field(
        "HP3",
        description="Report Model Code: HC1..HC4, HP1..HP4, KP1..KP2, VC1..VC2, VP1..VP2, HM1..HM2, PH1..PH2, PV, or MASTER_COMPLETE",
    )
    chapters: Optional[List[str]] = Field(None, description="Optional filter of specific chapter codes")
    target_year: Optional[int] = Field(None, description="Target solar return year for Varshaphala chapters")


class RectifyRelocateRequest(KundliRequest):
    target_latitude: Optional[float] = Field(None, description="Target relocation latitude")
    target_longitude: Optional[float] = Field(None, description="Target relocation longitude")
    target_city: Optional[str] = Field(None, description="Target relocation city name")

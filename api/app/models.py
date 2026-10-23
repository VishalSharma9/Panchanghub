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


def normalize_date_str(v: Any, default: str = "1990-05-15") -> Any:
    """Repair browser 5-digit year typos (e.g. '19992-05-04' -> '1992-05-04') and out-of-range dates."""
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
            return Date(y_i, m_i, min(d_i, 28)).isoformat()
        except Exception:
            return default
    return s


class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, examples=[28.6139])
    longitude: float = Field(..., ge=-180, le=180, examples=[77.2090])
    timezone: Optional[str] = Field(None, description="IANA timezone, e.g. Asia/Kolkata", examples=["Asia/Kolkata"])
    utc_offset: Optional[float] = Field(None, ge=-14, le=14, description="Hours east of UTC, used if timezone omitted")

    @field_validator("timezone", mode="before")
    @classmethod
    def _tz_before(cls, v):
        if v is None or v == "":
            return None
        try:
            float(v)
            return None
        except (ValueError, TypeError):
            return valid_tz(str(v))

    @model_validator(mode="before")
    @classmethod
    def _extract_numeric_tz(cls, data: Any):
        if isinstance(data, dict) and data.get("timezone") is not None and data.get("utc_offset") is None:
            try:
                data = dict(data)
                data["utc_offset"] = float(data["timezone"])
                data["timezone"] = None
            except (ValueError, TypeError):
                pass
        return data

    @model_validator(mode="after")
    def _need(self):
        if self.timezone is None and self.utc_offset is None:
            self.timezone = "Asia/Kolkata"
        return self

class BirthData(Location):
    date: Date = Field(..., examples=["1990-05-15"])
    time: Time = Field(..., examples=["10:30:00"])

    @field_validator("date", mode="before")
    @classmethod
    def _clean_date(cls, v):
        return normalize_date_str(v)

class ChartRequest(BirthData):
    system: Literal["tropical", "sidereal"] = "tropical"
    house_system: Optional[Literal["placidus", "koch", "equal", "whole_sign", "porphyry", "regiomontanus", "campanus"]] = Field(
        None, description="Default: placidus (tropical) / whole_sign (sidereal)")
    true_node: bool = False
    ayanamsa: Literal["lahiri", "lahiri_swiss", "raman", "kp", "kp_new", "yukteshwar", "bhasin", "true_chitra", "fagan_bradley", "suryasiddhanta", "sayana"] = "lahiri"

class KundliRequest(BirthData):
    name: Optional[str] = Field(None, max_length=100)
    house_system: Literal["whole_sign", "placidus", "equal"] = "whole_sign"
    true_node: bool = False
    dasha_levels: int = Field(3, ge=1, le=5)
    ayanamsa: Literal["lahiri", "lahiri_swiss", "raman", "kp", "kp_new", "yukteshwar", "bhasin", "true_chitra", "fagan_bradley", "suryasiddhanta", "sayana"] = "lahiri"
    target_date: Optional[Date] = Field(None, description="Optional target date to evaluate current running dasha (defaults to today)")

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
    latitude: Optional[float] = Field(28.6139, description="Optional birth latitude")
    longitude: Optional[float] = Field(77.2090, description="Optional birth longitude")
    timezone: Optional[str] = Field("Asia/Kolkata", description="Optional birth timezone")
    utc_offset: Optional[float] = Field(None, description="Optional UTC offset")






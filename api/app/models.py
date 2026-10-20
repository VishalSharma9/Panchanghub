from __future__ import annotations
from datetime import date as Date, datetime, time as Time
from typing import Literal, Optional
from zoneinfo import ZoneInfo, available_timezones
from pydantic import BaseModel, Field, field_validator, model_validator

_TZS = None
def valid_tz(tz: str) -> str:
    global _TZS
    if _TZS is None: _TZS = available_timezones()
    if tz not in _TZS: raise ValueError(f"unknown IANA timezone '{tz}'")
    return tz

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



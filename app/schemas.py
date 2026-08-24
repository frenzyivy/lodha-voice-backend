from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---------- Projects ----------

class ProjectOut(BaseModel):
    id: int
    name: str
    location: str
    price_min: int
    price_max: int
    configurations: str
    possession_date: str
    rera_number: str
    amenities: str
    status: str
    description: str

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    location: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    configurations: Optional[str] = None
    possession_date: Optional[str] = None
    rera_number: Optional[str] = None
    amenities: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


# ---------- Leads ----------

class LeadOut(BaseModel):
    id: int
    name: Optional[str]
    phone: str
    project_id: Optional[int]
    budget: Optional[str]
    configuration_interest: Optional[str]
    call_id: Optional[str]
    status: str
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    name: Optional[str] = None
    budget: Optional[str] = None
    configuration_interest: Optional[str] = None


# ---------- Calls ----------

class CallLogOut(BaseModel):
    id: int
    vapi_call_id: str
    lead_id: Optional[int]
    duration_seconds: int
    transcript: str
    summary: str
    recording_url: str
    outcome: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Vapi function-call payloads ----------
# Vapi sends function calls in its own envelope; these are the inner "arguments" shapes.

class GetProjectInfoArgs(BaseModel):
    project_name: str


class LogLeadArgs(BaseModel):
    name: Optional[str] = None
    phone: str
    project_name: Optional[str] = None
    budget: Optional[str] = None
    configuration_interest: Optional[str] = None
    call_id: Optional[str] = None
    notes: Optional[str] = None


class Stats(BaseModel):
    calls_today: int
    leads_today: int
    total_leads: int
    site_visits_booked: int
    conversion_rate: float

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # must match Vapi prompt exactly
    location = Column(String, nullable=False)
    price_min = Column(Integer, nullable=False)   # in INR, e.g. 15000000
    price_max = Column(Integer, nullable=False)
    configurations = Column(String, nullable=False)   # "1,2,3 BHK"
    possession_date = Column(String, nullable=False)  # "Dec 2027" — free text is fine here
    rera_number = Column(String, nullable=False)
    amenities = Column(Text, nullable=False)  # comma-separated
    status = Column(String, default="active")  # active / sold_out / paused
    description = Column(Text, default="")

    leads = relationship("Lead", back_populates="project")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    budget = Column(String, nullable=True)
    configuration_interest = Column(String, nullable=True)
    call_id = Column(String, nullable=True, index=True)  # links to CallLog.vapi_call_id
    status = Column(String, default="new")  # new / contacted / site_visit_booked / closed / lost
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="leads")


class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    vapi_call_id = Column(String, unique=True, index=True, nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    duration_seconds = Column(Integer, default=0)
    transcript = Column(Text, default="")
    summary = Column(Text, default="")
    recording_url = Column(String, default="")
    outcome = Column(String, default="unknown")  # interested / not_interested / callback / no_answer
    created_at = Column(DateTime, default=datetime.utcnow)

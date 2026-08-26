from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import verify_dashboard_token
from app import models, schemas

router = APIRouter(prefix="/api", tags=["dashboard"], dependencies=[Depends(verify_dashboard_token)])


# ---------- Projects ----------

@router.get("/projects", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


@router.patch("/projects/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).get(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


# ---------- Leads ----------

@router.get("/leads", response_model=List[schemas.LeadOut])
def list_leads(
    project_id: Optional[int] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    q = db.query(models.Lead)
    if project_id:
        q = q.filter(models.Lead.project_id == project_id)
    if status_filter:
        q = q.filter(models.Lead.status == status_filter)
    return q.order_by(models.Lead.created_at.desc()).all()


@router.patch("/leads/{lead_id}", response_model=schemas.LeadOut)
def update_lead(lead_id: int, update: schemas.LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).get(lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead


# ---------- Calls ----------

@router.get("/calls", response_model=List[schemas.CallLogOut])
def list_calls(db: Session = Depends(get_db)):
    return db.query(models.CallLog).order_by(models.CallLog.created_at.desc()).limit(200).all()


# ---------- Stats ----------

@router.get("/stats", response_model=schemas.Stats)
def get_stats(db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    calls_today = db.query(models.CallLog).filter(models.CallLog.created_at >= today_start).count()
    leads_today = db.query(models.Lead).filter(models.Lead.created_at >= today_start).count()
    total_leads = db.query(models.Lead).count()
    site_visits = db.query(models.Lead).filter(models.Lead.status == "site_visit_booked").count()
    closed = db.query(models.Lead).filter(models.Lead.status == "closed").count()

    conversion_rate = round((closed / total_leads) * 100, 1) if total_leads else 0.0

    return schemas.Stats(
        calls_today=calls_today,
        leads_today=leads_today,
        total_leads=total_leads,
        site_visits_booked=site_visits,
        conversion_rate=conversion_rate,
    )

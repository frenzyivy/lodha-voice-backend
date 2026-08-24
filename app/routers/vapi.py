from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import verify_vapi_secret
from app import models

router = APIRouter(prefix="/vapi", tags=["vapi"], dependencies=[Depends(verify_vapi_secret)])


def _project_to_dict(p: models.Project) -> dict:
    return {
        "name": p.name,
        "location": p.location,
        "price_range": f"₹{p.price_min:,} - ₹{p.price_max:,}",
        "configurations": p.configurations,
        "possession_date": p.possession_date,
        "rera_number": p.rera_number,
        "amenities": p.amenities,
        "status": p.status,
        "description": p.description,
    }


@router.post("/functions/get-project-info")
async def get_project_info(request: Request, db: Session = Depends(get_db)):
    """Called by Vapi's getProjectInfo function during a live call.
    Vapi wraps the arguments in its own envelope - we pull `project_name` out defensively
    so this works whether Vapi sends {"project_name": ...} directly or nested under
    message.toolCalls[0].function.arguments (their format has changed before)."""
    body = await request.json()
    project_name = _extract_arg(body, "project_name")

    if not project_name:
        return {"result": "No project name provided. Ask the caller which project they mean."}

    project = (
        db.query(models.Project)
        .filter(models.Project.name.ilike(project_name.strip()))
        .filter(models.Project.status == "active")
        .first()
    )

    if not project:
        # This is the guardrail in action: no row = the assistant has nothing to say.
        return {
            "result": "This project is not one we currently have information on. "
                       "Politely tell the caller you don't have details on that one, "
                       "and offer to share info on a project you do cover instead."
        }

    return {"result": _project_to_dict(project)}


@router.post("/functions/list-projects")
async def list_projects(db: Session = Depends(get_db)):
    """Returns just the names of active projects - lets the assistant sanity-check
    what it's allowed to discuss without exposing full data."""
    names = [
        p.name for p in db.query(models.Project).filter(models.Project.status == "active").all()
    ]
    return {"result": {"projects": names}}


@router.post("/functions/log-lead")
async def log_lead(request: Request, db: Session = Depends(get_db)):
    """Called by Vapi's logLeadInterest function, usually near the end of a call."""
    body = await request.json()

    phone = _extract_arg(body, "phone")
    if not phone:
        return {"result": "Phone number is required to log a lead."}

    project_name = _extract_arg(body, "project_name")
    project = None
    if project_name:
        project = db.query(models.Project).filter(models.Project.name.ilike(project_name.strip())).first()

    lead = models.Lead(
        name=_extract_arg(body, "name"),
        phone=phone,
        project_id=project.id if project else None,
        budget=_extract_arg(body, "budget"),
        configuration_interest=_extract_arg(body, "configuration_interest"),
        call_id=_extract_arg(body, "call_id"),
        notes=_extract_arg(body, "notes") or "",
        status="new",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {"result": f"Lead logged for {lead.phone}."}


@router.post("/webhook/call-ended")
async def call_ended(request: Request, db: Session = Depends(get_db)):
    """Vapi's end-of-call-report webhook. Saves the call, then hands off to n8n
    for notifications/CRM sync (set N8N_WEBHOOK_URL as an env var and un-comment
    the httpx call once your n8n workflow is ready)."""
    body = await request.json()
    message = body.get("message", body)  # Vapi nests most of this under "message"

    call = message.get("call", {})
    vapi_call_id = call.get("id") or message.get("callId") or "unknown"

    existing = db.query(models.CallLog).filter(models.CallLog.vapi_call_id == vapi_call_id).first()
    if existing:
        return {"status": "already logged"}

    call_log = models.CallLog(
        vapi_call_id=vapi_call_id,
        duration_seconds=int(message.get("durationSeconds", 0) or 0),
        transcript=message.get("transcript", "") or "",
        summary=message.get("summary", "") or "",
        recording_url=message.get("recordingUrl", "") or "",
        outcome=message.get("endedReason", "unknown") or "unknown",
    )

    # Link to a lead logged during this same call, if any
    linked_lead = db.query(models.Lead).filter(models.Lead.call_id == vapi_call_id).first()
    if linked_lead:
        call_log.lead_id = linked_lead.id

    db.add(call_log)
    db.commit()

    # --- n8n handoff (enable once your workflow is ready) ---
    # import os, httpx
    # n8n_url = os.getenv("N8N_WEBHOOK_URL")
    # if n8n_url:
    #     async with httpx.AsyncClient() as client:
    #         await client.post(n8n_url, json={
    #             "call_id": vapi_call_id,
    #             "outcome": call_log.outcome,
    #             "lead_id": call_log.lead_id,
    #         }, timeout=10)

    return {"status": "logged"}


def _extract_arg(body: dict, key: str):
    """Defensively pull a function argument out of whatever shape Vapi sent.
    Handles flat bodies and Vapi's nested toolCalls[].function.arguments format."""
    if key in body:
        return body.get(key)

    message = body.get("message", {})
    tool_calls = message.get("toolCalls") or message.get("toolCallList") or []
    for tc in tool_calls:
        args = tc.get("function", {}).get("arguments", {})
        if isinstance(args, dict) and key in args:
            return args.get(key)

    params = body.get("parameters", {})
    if key in params:
        return params.get(key)

    return None

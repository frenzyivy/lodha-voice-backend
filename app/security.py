import os
import secrets
from fastapi import Header, HTTPException, status

VAPI_SHARED_SECRET = os.getenv("VAPI_SHARED_SECRET", "change-me-in-production")
DASHBOARD_TOKEN = os.getenv("DASHBOARD_TOKEN", "change-me-too")


def verify_vapi_secret(x_vapi_secret: str = Header(default="")):
    """Checks the custom header Vapi sends on every function/webhook call.
    Configure this same header + value in the Vapi dashboard for each function/webhook."""
    if not secrets.compare_digest(x_vapi_secret, VAPI_SHARED_SECRET):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Vapi secret")


def verify_vapi_secret(authorization: str = Header(default="")):
    """Checks the Authorization: Bearer <secret> header Vapi sends."""
    expected = f"Bearer {VAPI_SHARED_SECRET}"
    if not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Vapi secret")

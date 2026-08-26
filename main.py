from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="Lodha Voice Bot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your n8n webhook URL
N8N_WEBHOOK_URL = "https://n8n.allianzabiz.cloud/webhook/vapi-webhook-lodha"

@app.get("/")
async def root():
    return {"message": "Lodha Voice Bot is running!"}

@app.post("/vapi/webhook/call-ended")
async def vapi_call_ended(data: dict):
    """Vapi sends call data here when a call ends."""
    try:
        call_id = data.get("callId", "unknown")
        phone_number = data.get("phoneNumber", "unknown")
        transcript = data.get("transcript", "")
        duration = data.get("duration", 0)
        
        print(f" Call ended: {phone_number}")
        print(f" Transcript: {transcript[:100]}...")
        
        # Send to n8n
        async with httpx.AsyncClient() as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json={
                    "callId": call_id,
                    "phoneNumber": phone_number,
                    "transcript": transcript,
                    "duration": duration
                },
                timeout=30
            )
        
        print(f" Sent to n8n: {response.status_code}")
        
        return {"success": True, "callId": call_id}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

# dashboard API 

# Storage for calls and leads
calls_storage = []
leads_storage = {}

@app.post("/api/save-call")
async def save_call(data: dict):
    """Save call data for dashboard"""
    call_data = {
        "id": data.get("callId"),
        "phone": data.get("phoneNumber"),
        "project": data.get("project", "Unknown"),
        "quality": data.get("quality", "Warm"),
        "duration": data.get("duration", 0),
        "timestamp": data.get("timestamp", "")
    }
    
    calls_storage.append(call_data)
    
    phone = data.get("phoneNumber")
    if phone not in leads_storage:
        leads_storage[phone] = {
            "phone": phone,
            "name": data.get("name", "Unknown"),
            "projects": [data.get("project", "Unknown")],
            "quality": data.get("quality", "Warm"),
            "budget": data.get("budget", "N/A"),
            "lastCall": data.get("timestamp", "")
        }
    
    return {"success": True}

@app.get("/api/calls")
async def get_calls():
    """Get all calls for dashboard"""
    return {"calls": calls_storage[-50:]}

@app.get("/api/leads")
async def get_leads():
    """Get all leads for dashboard"""
    return {"leads": list(leads_storage.values())}

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    hot_count = sum(1 for c in calls_storage if c.get("quality") == "Hot")
    warm_count = sum(1 for c in calls_storage if c.get("quality") == "Warm")
    cold_count = sum(1 for c in calls_storage if c.get("quality") == "Cold")
    
    avg_duration = 0
    if calls_storage:
        avg_duration = sum(c.get("duration", 0) for c in calls_storage) // len(calls_storage)
    
    return {
        "totalCalls": len(calls_storage),
        "totalLeads": len(leads_storage),
        "hotLeads": hot_count,
        "warmLeads": warm_count,
        "coldLeads": cold_count,
        "avgDuration": avg_duration
    }
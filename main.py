import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import vapi, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lodha Voice AI Backend")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vapi.router)
app.include_router(dashboard.router)


@app.get("/")
def health():
    return {"status": "ok"}

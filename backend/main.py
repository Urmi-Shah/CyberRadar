from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
from models import Base
from routes.incidents import router as incident_router
from routes.pipeline import router as pipeline_router
from routes.analytics import router as analytics_router
from routes.map import router as map_router
from routes.reports import router as reports_router

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

app = FastAPI(title="CyberRadar", description="AI-Powered Cyber Threat Intelligence Platform", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(incident_router)
app.include_router(pipeline_router)
app.include_router(analytics_router)
app.include_router(map_router)
app.include_router(reports_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "CyberRadar is running", "ui": "/app/dashboard.html"}

app.mount("/app", StaticFiles(directory=FRONTEND, html=True), name="frontend")

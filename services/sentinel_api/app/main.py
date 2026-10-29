import sys
import os
from pathlib import Path

# Path Fix: Ensure the 'app' module can be found regardless of where uvicorn is started from
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .api.health import router as health_router
from .api.auth import router as auth_router
from .api.cases import router as cases_router
from .api.evidence import router as evidence_router
from .api.forensics import router as forensics_router
from .api.log_analysis import router as log_analysis_router
from .api.integrity import router as integrity_router
from .api.timeline import router as timeline_router
from .api.reports import router as reports_router
from .api.sync import router as sync_router
from .api.ai import router as ai_router
from .api.advanced import router as advanced_router
from .core.config import settings
from .core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list if settings.cors_origin_list else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")
app.include_router(forensics_router, prefix="/api/v1/forensics")
app.include_router(log_analysis_router, prefix="/api/v1")
app.include_router(integrity_router, prefix="/api/v1")
app.include_router(timeline_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(advanced_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.app_version}

from fastapi import APIRouter
from services.pipeline_services import sync_pipeline

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])

@router.post("/sync")
def pipeline_sync():
    return sync_pipeline()

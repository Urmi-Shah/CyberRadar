from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import Incident
from schemas import IncidentCreate
from datetime import datetime

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("")
def get_incidents(limit: int = 20, search: str = ""):
    db = SessionLocal()
    try:
        q = db.query(Incident).order_by(Incident.id.desc())
        if search:
            q = q.filter(Incident.description.ilike(f"%{search}%"))
        return q.limit(min(limit, 100)).all()
    finally:
        db.close()

@router.post("")
def create_incident(item: IncidentCreate):
    db = SessionLocal()
    try:
        dt = datetime.strptime(item.date, "%Y-%m-%d")
        obj = Incident(
            incident_id=f"MAN-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            date=item.date,
            year=dt.year,
            month=dt.strftime("%B"),
            state=item.state,
            city=item.city,
            incident_type=item.incident_type,
            severity=item.severity,
            sector=item.sector,
            financial_loss_inr=item.financial_loss_inr,
            affected_users=item.affected_users,
            status=item.status,
            source=item.source or "Manual Entry",
            description=item.description,
            ai_summary=item.ai_summary or f"Manual incident recorded as {item.incident_type}.",
            recommendation=item.recommendation or "Review the incident and apply appropriate containment controls."
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {"success": True, "incident_id": obj.incident_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(400, str(e))
    finally:
        db.close()

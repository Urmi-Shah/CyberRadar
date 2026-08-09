from pydantic import BaseModel

class IncidentCreate(BaseModel):
    date: str
    state: str = "Unknown"
    city: str = "Unknown"
    incident_type: str = "Other"
    severity: str = "Medium"
    sector: str = "General"
    financial_loss_inr: int = 0
    affected_users: int = 0
    status: str = "Active"
    source: str = "Manual Entry"
    description: str = ""
    ai_summary: str = ""
    recommendation: str = ""

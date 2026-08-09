from fastapi import APIRouter, Query
from services.analytics import analyze, filter_options

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def dashboard(
    period: str = "all",
    state: str = "All",
    city: str = "All",
    incident_type: str = "All",
    sector: str = "All",
    source: str = "All",
    status: str = "All",
    severities: str = "",
    search: str = "",
    start: str = "",
    end: str = "",
):
    return analyze({
        "period": period, "state": state, "city": city,
        "incident_type": incident_type, "sector": sector,
        "source": source, "status": status, "severities": severities,
        "search": search, "start": start, "end": end
    })

@router.get("/filters")
def filters():
    return filter_options()

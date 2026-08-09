from sqlalchemy import Column, Integer, String
from database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(String)
    date = Column(String)
    year = Column(Integer)
    month = Column(String)
    state = Column(String)
    city = Column(String)
    incident_type = Column(String)
    severity = Column(String)
    sector = Column(String)
    financial_loss_inr = Column(Integer)
    affected_users = Column(Integer)
    status = Column(String)
    source = Column(String)
    description = Column(String)
    ai_summary = Column(String)
    recommendation = Column(String)
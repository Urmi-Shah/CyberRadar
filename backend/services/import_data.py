import pandas as pd
from database import SessionLocal
from models import Incident
import os
# Change this path if your file name is different
EXCEL_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 "../../dataset/CyberRadar_Synthetic_India_Cyber_Incidents_2024_2026_10000.xlsx")
)

df = pd.read_excel(EXCEL_FILE)

db = SessionLocal()

count = 0

for _, row in df.iterrows():

    # Skip duplicate Incident_ID
    exists = db.query(Incident).filter(
        Incident.incident_id == str(row["Incident_ID"])
    ).first()

    if exists:
        continue

    incident = Incident(
        incident_id=str(row["Incident_ID"]),
        date=str(row["Date"]),
        year=int(row["Year"]),
        month=str(row["Month"]),
        state=str(row["State"]),
        city=str(row["City"]),
        incident_type=str(row["Incident_Type"]),
        severity=str(row["Severity"]),
        sector=str(row["Sector"]),
        financial_loss_inr=int(float(row["Financial_Loss_INR"])),
        affected_users=int(row["Affected_Users"]),
        status=str(row["Status"]),
        source=str(row["Source"]),
        description=str(row["Description"]),
        ai_summary=str(row["AI_Summary"]),
        recommendation=str(row["Recommendation"])
    )

    db.add(incident)
    count += 1

db.commit()
db.close()

print(f"✅ {count} incidents imported successfully!")
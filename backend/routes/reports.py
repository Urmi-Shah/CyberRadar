from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Incident
import pandas as pd
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


router = APIRouter(prefix="/reports", tags=["Reports"])

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_dataframe(
    db: Session,
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
    end: str = ""
):
    records = db.query(Incident).all()

    rows = []

    for x in records:
        rows.append({
            "Incident ID": x.incident_id,
            "Date": x.date,
            "State": x.state or "",
            "City": x.city or "",
            "Attack": x.incident_type or "",
            "Severity": x.severity or "",
            "Sector": x.sector or "",
            "Financial Loss":x.financial_loss_inr or 0,
            "Affected Users": int(x.affected_users or 0),
            "Source": x.source or "",
            "Status": getattr(x, "status", "") or ""
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # -----------------------------
    # STATE
    # -----------------------------
    if state and state.lower() != "all":
        df = df[
            df["State"].astype(str).str.lower()
            == state.strip().lower()
        ]

    # -----------------------------
    # CITY
    # -----------------------------
    if city and city.lower() != "all":
        df = df[
            df["City"].astype(str).str.lower()
            == city.strip().lower()
        ]

    # -----------------------------
    # ATTACK TYPE
    # -----------------------------
    if incident_type and incident_type.lower() != "all":
        df = df[
            df["Attack"].astype(str).str.lower()
            == incident_type.strip().lower()
        ]

    # -----------------------------
    # SECTOR
    # -----------------------------
    if sector and sector.lower() != "all":
        df = df[
            df["Sector"].astype(str).str.lower()
            == sector.strip().lower()
        ]

    # -----------------------------
    # SOURCE
    # -----------------------------
    if source and source.lower() != "all":
        df = df[
            df["Source"].astype(str).str.lower()
            == source.strip().lower()
        ]

    # -----------------------------
    # STATUS
    # -----------------------------
    if status and status.lower() != "all":
        df = df[
            df["Status"].astype(str).str.lower()
            == status.strip().lower()
        ]

    # -----------------------------
    # SEVERITY
    # -----------------------------
    if severities:
        selected = [
            x.strip().lower()
            for x in severities.split(",")
            if x.strip()
        ]

        if selected:
            df = df[
                df["Severity"]
                .astype(str)
                .str.lower()
                .isin(selected)
            ]

    # -----------------------------
    # SEARCH
    # -----------------------------
    if search:
        s = search.strip().lower()

        mask = (
            df["Incident ID"].astype(str).str.lower().str.contains(s, na=False)
            | df["State"].astype(str).str.lower().str.contains(s, na=False)
            | df["City"].astype(str).str.lower().str.contains(s, na=False)
            | df["Attack"].astype(str).str.lower().str.contains(s, na=False)
            | df["Sector"].astype(str).str.lower().str.contains(s, na=False)
            | df["Source"].astype(str).str.lower().str.contains(s, na=False)
        )

        df = df[mask]

    # -----------------------------
    # DATE
    # -----------------------------
    if "Date" in df.columns:
        df["_date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        today = pd.Timestamp.today().normalize()

        if period == "today":
            df = df[df["_date"].dt.date == today.date()]

        elif period == "week":
            df = df[df["_date"] >= today - pd.Timedelta(days=7)]

        elif period == "month":
            df = df[df["_date"] >= today - pd.Timedelta(days=30)]

        elif period == "6months":
            df = df[df["_date"] >= today - pd.Timedelta(days=180)]

        elif period == "year":
            df = df[df["_date"] >= today - pd.Timedelta(days=365)]

        if start:
            start_date = pd.to_datetime(
                start,
                errors="coerce"
            )

            if not pd.isna(start_date):
                df = df[df["_date"] >= start_date]

        if end:
            end_date = pd.to_datetime(
                end,
                errors="coerce"
            )

            if not pd.isna(end_date):
                end_date = end_date + pd.Timedelta(days=1)
                df = df[df["_date"] < end_date]

        df.drop(columns=["_date"], inplace=True, errors="ignore")

    return df.reset_index(drop=True)


# =========================================================
# CSV
# =========================================================

@router.get("/csv")
def export_csv(
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
    db: Session = Depends(get_db)
):
    df = load_dataframe(
        db,
        period,
        state,
        city,
        incident_type,
        sector,
        source,
        status,
        severities,
        search,
        start,
        end
    )

    path = REPORT_DIR / "CyberRadar_Report.csv"

    df.to_csv(
        path,
        index=False
    )

    return FileResponse(
        path,
        filename="CyberRadar_Report.csv",
        media_type="text/csv"
    )


# =========================================================
# EXCEL
# =========================================================

@router.get("/excel")
def export_excel(
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
    db: Session = Depends(get_db)
):
    df = load_dataframe(
        db,
        period,
        state,
        city,
        incident_type,
        sector,
        source,
        status,
        severities,
        search,
        start,
        end
    )

    path = REPORT_DIR / "CyberRadar_Report.xlsx"

    df.to_excel(
        path,
        index=False
    )

    return FileResponse(
        path,
        filename="CyberRadar_Report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================================================
# PDF
# =========================================================

@router.get("/pdf")
def export_pdf(
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
    db: Session = Depends(get_db)
):
    df = load_dataframe(
        db,
        period,
        state,
        city,
        incident_type,
        sector,
        source,
        status,
        severities,
        search,
        start,
        end
    )

    path = REPORT_DIR / "CyberRadar_Report.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "CyberRadar",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Cyber Threat Intelligence Report",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # FILTER INFORMATION

    filters = [
        ["Filter", "Selected"],
        ["Date Range", period],
        ["State", state],
        ["City", city],
        ["Attack Type", incident_type],
        ["Sector", sector],
        ["Source", source],
        ["Status", status],
        ["Severity", severities or "All"]
    ]

    filter_table = Table(
        filters,
        colWidths=[180, 270]
    )

    filter_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#111827")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(filter_table)

    story.append(
        Spacer(1, 15)
    )

    # KPI

    total = len(df)

    critical = 0
    loss = 0
    users = 0

    if not df.empty:
        critical = int(
            (
                df["Severity"]
                .astype(str)
                .str.lower()
                == "critical"
            ).sum()
        )

        loss = float(
            df["Financial Loss"].sum()
        )

        users = int(
            df["Affected Users"].sum()
        )

    kpi_data = [
        ["Metric", "Value"],
        ["Total Incidents", f"{total:,}"],
        ["Critical Threats", f"{critical:,}"],
        ["Financial Loss",f"INR {loss:,.0f}"],
        ["Affected Users", f"{users:,}"]
    ]

    kpi_table = Table(
        kpi_data,
        colWidths=[250, 200]
    )

    kpi_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#111827")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(kpi_table)

    story.append(
        Spacer(1, 20)
    )

    # INCIDENT DATA

    if df.empty:

        story.append(
            Paragraph(
                "No incidents match the selected filters.",
                styles["Normal"]
            )
        )

    else:

        story.append(
            Paragraph(
                "Filtered Incident Data",
                styles["Heading2"]
            )
        )

        pdf_columns = [
            "Incident ID",
            "Date",
            "State",
            "City",
            "Attack",
            "Severity"
        ]

        table_data = [
            pdf_columns
        ]

        for _, row in df.head(100).iterrows():

            table_data.append([
                str(row.get("Incident ID", "")),
                str(row.get("Date", "")),
                str(row.get("State", "")),
                str(row.get("City", "")),
                str(row.get("Attack", "")),
                str(row.get("Severity", ""))
            ])

        incident_table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                60,
                65,
                75,
                75,
                100,
                65
            ]
        )

        incident_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#111827")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    4
                )
            ])
        )

        story.append(incident_table)

        if len(df) > 100:
            story.append(
                Spacer(1, 10)
            )

            story.append(
                Paragraph(
                    f"Showing first 100 of {len(df):,} filtered incidents.",
                    styles["Normal"]
                )
            )

    doc.build(story)

    return FileResponse(
        path,
        filename="CyberRadar_Report.pdf",
        media_type="application/pdf"
    )
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import pandas as pd

from database import SessionLocal
from models import Incident


router = APIRouter(
    prefix="/map",
    tags=["Threat Map"]
)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# HELPER
# ============================================================

def build_dataframe(db: Session):

    incidents = db.query(Incident).all()

    if not incidents:
        return pd.DataFrame(
            columns=[
                "state",
                "city",
                "incident_type",
                "severity",
                "sector",
                "financial_loss",
                "affected_users"
            ]
        )

    rows = []

    for x in incidents:

        rows.append({
            "state": str(x.state or "").strip(),
            "city": str(x.city or "").strip(),
            "incident_type": str(x.incident_type or "Unknown").strip(),
            "severity": str(x.severity or "Unknown").strip(),
            "sector": str(x.sector or "Unknown").strip(),
            "financial_loss": float(x.financial_loss_inr or 0),
            "affected_users": int(x.affected_users or 0)
})

    df = pd.DataFrame(rows)

    # Remove empty states
    df = df[df["state"] != ""]

    return df
# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(total, critical):

    if total == 0:
        return 0, "LOW"

    critical_ratio = critical / total

    risk_score = (
        critical_ratio * 100
        + min(total / 100, 40)
    )

    risk_score = min(
        100,
        round(risk_score)
    )

    if risk_score >= 75:
        level = "CRITICAL"

    elif risk_score >= 50:
        level = "HIGH"

    elif risk_score >= 25:
        level = "MEDIUM"

    else:
        level = "LOW"

    return risk_score, level


# ============================================================
# ALL STATES
# ============================================================

@router.get("/states")
def get_state_map(
    db: Session = Depends(get_db)
):

    df = build_dataframe(db)

    if df.empty:

        return {
            "states": {},
            "total_states": 0
        }


    result = {}


    for state, group in df.groupby(
        "state",
        dropna=True
    ):

        total = len(group)


        # ----------------------------------------------------
        # Critical
        # ----------------------------------------------------

        critical = int(
            (
                group["severity"]
                .astype(str)
                .str.lower()
                == "critical"
            ).sum()
        )


        # ----------------------------------------------------
        # Financial Loss
        # ----------------------------------------------------

        financial_loss = float(
            group["financial_loss"].sum()
        )


        # ----------------------------------------------------
        # Affected Users
        # ----------------------------------------------------

        affected_users = int(
            group["affected_users"].sum()
        )


        # ----------------------------------------------------
        # Most common attack
        # ----------------------------------------------------

        attack_mode = group[
            "incident_type"
        ].mode()

        top_attack = (
            attack_mode.iloc[0]
            if not attack_mode.empty
            else "Unknown"
        )


        # ----------------------------------------------------
        # Most affected city
        # ----------------------------------------------------

        city_mode = group[
            "city"
        ].mode()

        top_city = (
            city_mode.iloc[0]
            if not city_mode.empty
            else "Unknown"
        )


        # ----------------------------------------------------
        # Most affected sector
        # ----------------------------------------------------

        sector_mode = group[
            "sector"
        ].mode()

        top_sector = (
            sector_mode.iloc[0]
            if not sector_mode.empty
            else "Unknown"
        )


        # ----------------------------------------------------
        # Risk
        # ----------------------------------------------------

        risk_score, risk_level = calculate_risk(
            total,
            critical
        )


        result[str(state)] = {

            "incidents": total,

            "critical": critical,

            "financial_loss": financial_loss,

            "affected_users": affected_users,

            "top_attack": top_attack,

            "top_city": top_city,

            "top_sector": top_sector,

            "risk_score": risk_score,

            "risk_level": risk_level
        }


    return {
        "states": result,
        "total_states": len(result)
    }


# ============================================================
# SINGLE STATE
# ============================================================

@router.get("/state/{state_name}")
def get_single_state(
    state_name: str,
    db: Session = Depends(get_db)
):

    df = build_dataframe(db)

    if df.empty:

        raise HTTPException(
            status_code=404,
            detail="No incident data available"
        )


    # Case-insensitive state matching

    state_df = df[
        df["state"]
        .str.lower()
        == state_name.strip().lower()
    ]


    if state_df.empty:

        raise HTTPException(
            status_code=404,
            detail=f"No data found for state: {state_name}"
        )


    total = len(state_df)


    critical = int(
        (
            state_df["severity"]
            .astype(str)
            .str.lower()
            == "critical"
        ).sum()
    )


    financial_loss = float(
        state_df["financial_loss"].sum()
    )


    affected_users = int(
        state_df["affected_users"].sum()
    )


    attack_mode = state_df[
        "incident_type"
    ].mode()

    top_attack = (
        attack_mode.iloc[0]
        if not attack_mode.empty
        else "Unknown"
    )


    city_mode = state_df[
        "city"
    ].mode()

    top_city = (
        city_mode.iloc[0]
        if not city_mode.empty
        else "Unknown"
    )


    sector_mode = state_df[
        "sector"
    ].mode()

    top_sector = (
        sector_mode.iloc[0]
        if not sector_mode.empty
        else "Unknown"
    )


    risk_score, risk_level = calculate_risk(
        total,
        critical
    )


    return {

        "state": state_name,

        "incidents": total,

        "critical": critical,

        "financial_loss": financial_loss,

        "affected_users": affected_users,

        "top_attack": top_attack,

        "top_city": top_city,

        "top_sector": top_sector,

        "risk_score": risk_score,

        "risk_level": risk_level
    }
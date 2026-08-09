import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

DB_PATH = str(Path(__file__).resolve().parents[1] / "cyberradar.db")


def load_dataframe():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM incidents", conn)
    finally:
        conn.close()
    if df.empty:
        return df
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["financial_loss_inr"] = pd.to_numeric(df["financial_loss_inr"], errors="coerce").fillna(0)
    df["affected_users"] = pd.to_numeric(df["affected_users"], errors="coerce").fillna(0)
    for col in ["state", "city", "incident_type", "severity", "sector", "status", "source"]:
        df[col] = df[col].fillna("Unknown").astype(str)
    return df


def _period_filter(df, period, start=None, end=None):
    if df.empty or period in (None, "all", ""):
        return df
    today = pd.Timestamp.now().normalize()
    if period == "today":
        return df[df["date_dt"] >= today]
    if period == "yesterday":
        return df[(df["date_dt"] >= today - pd.Timedelta(days=1)) & (df["date_dt"] < today)]
    if period == "week":
        return df[df["date_dt"] >= today - pd.Timedelta(days=7)]
    if period == "month":
        return df[df["date_dt"] >= today - pd.Timedelta(days=30)]
    if period == "6months":
        return df[df["date_dt"] >= today - pd.Timedelta(days=183)]
    if period == "year":
        return df[df["date_dt"] >= today - pd.Timedelta(days=365)]
    if period == "custom":
        s = pd.to_datetime(start, errors="coerce") if start else None
        e = pd.to_datetime(end, errors="coerce") if end else None
        if s is not None and pd.notna(s):
            df = df[df["date_dt"] >= s]
        if e is not None and pd.notna(e):
            df = df[df["date_dt"] <= e + pd.Timedelta(days=1)]
        return df
    return df


def apply_filters(df, filters):
    df = _period_filter(df, filters.get("period", "all"), filters.get("start"), filters.get("end"))
    for key in ["state", "city", "incident_type", "sector", "source", "status"]:
        value = filters.get(key)
        if value and value != "All":
            df = df[df[key].str.casefold() == value.casefold()]
    severities = filters.get("severities") or []
    if isinstance(severities, str):
        severities = [x for x in severities.split(",") if x]
    if severities:
        wanted = {x.casefold() for x in severities}
        df = df[df["severity"].str.casefold().isin(wanted)]
    search = filters.get("search")
    if search:
        s = search.casefold()
        mask = False
        for col in ["incident_id", "state", "city", "incident_type", "sector", "source", "description"]:
            mask = mask | df[col].str.casefold().str.contains(s, na=False)
        df = df[mask]
    return df


def _counts(df, column, limit=None):
    s = df[column].value_counts()
    if limit:
        s = s.head(limit)
    return {"labels": s.index.tolist(), "values": [int(v) for v in s.values]}


def analyze(filters=None):
    filters = filters or {}
    all_df = load_dataframe()
    df = apply_filters(all_df.copy(), filters)

    if df.empty:
        return {
            "kpis": {"total": 0, "critical": 0, "loss": 0, "users": 0, "avg_loss": 0, "avg_users": 0},
            "insights": {"risk_score": 0, "risk_level": "NO DATA", "top_state": "—", "top_city": "—", "top_attack": "—", "top_sector": "—"},
            "charts": {},
            "rows": []
        }

    risk_map = {"low": 25, "medium": 50, "high": 75, "critical": 95}
    df["risk_score"] = df["severity"].str.casefold().map(risk_map).fillna(50)

    total = len(df)
    critical = int((df["severity"].str.casefold() == "critical").sum())
    loss = float(df["financial_loss_inr"].sum())
    users = int(df["affected_users"].sum())
    avg_loss = float(df["financial_loss_inr"].mean())
    avg_users = float(df["affected_users"].mean())
    risk = float(np.mean(df["risk_score"]))

    if risk >= 85:
        risk_level = "CRITICAL"
    elif risk >= 65:
        risk_level = "HIGH"
    elif risk >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    monthly = (
        df.dropna(subset=["date_dt"])
        .assign(period=lambda x: x["date_dt"].dt.to_period("M").astype(str))
        .groupby("period").size().reset_index(name="count")
    )
    daily = (
        df.dropna(subset=["date_dt"])
        .assign(period=lambda x: x["date_dt"].dt.strftime("%Y-%m-%d"))
        .groupby("period").size().reset_index(name="count")
    )
    financial = (
        df.dropna(subset=["date_dt"])
        .assign(period=lambda x: x["date_dt"].dt.to_period("M").astype(str))
        .groupby("period")["financial_loss_inr"].sum().reset_index()
    )

    latest = df.sort_values("date_dt", ascending=False).head(15)
    rows = latest[["incident_id", "date", "state", "city", "incident_type", "severity", "sector", "source"]].fillna("").to_dict("records")

    return {
        "kpis": {
            "total": total,
            "critical": critical,
            "loss": loss,
            "users": users,
            "avg_loss": avg_loss,
            "avg_users": avg_users,
        },
        "insights": {
            "risk_score": round(risk, 1),
            "risk_level": risk_level,
            "top_state": df["state"].value_counts().idxmax(),
            "top_city": df["city"].value_counts().idxmax(),
            "top_attack": df["incident_type"].value_counts().idxmax(),
            "top_sector": df["sector"].value_counts().idxmax(),
        },
        "charts": {
            "monthly": {"labels": monthly["period"].tolist(), "values": monthly["count"].astype(int).tolist()},
            "daily": {"labels": daily["period"].tolist(), "values": daily["count"].astype(int).tolist()},
            "financial": {"labels": financial["period"].tolist(), "values": financial["financial_loss_inr"].astype(float).tolist()},
            "attack": _counts(df, "incident_type"),
            "severity": _counts(df, "severity"),
            "states": _counts(df, "state", 10),
            "cities": _counts(df, "city", 10),
            "sector": _counts(df, "sector"),
            "source": _counts(df, "source"),
            "status": _counts(df, "status"),
        },
        "rows": rows,
    }


def filter_options():
    df = load_dataframe()
    if df.empty:
        return {}
    return {c: sorted(df[c].dropna().astype(str).unique().tolist()) for c in ["state", "city", "incident_type", "sector", "source", "status", "severity"]}

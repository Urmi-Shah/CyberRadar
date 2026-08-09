import re

def classify_incident(title, summary=""):

    text = f"{title} {summary}".lower()

    incident_type = "Other"
    severity = "Medium"
    sector = "General"
    risk_score = 50

    # -------------------------
    # Incident Type
    # -------------------------

    if re.search(r"ransomware", text):
        incident_type = "Ransomware"
        severity = "Critical"
        risk_score = 95

    elif re.search(r"phishing", text):
        incident_type = "Phishing"
        severity = "High"
        risk_score = 85

    elif re.search(r"ddos", text):
        incident_type = "DDoS"
        severity = "High"
        risk_score = 80

    elif re.search(r"malware|trojan", text):
        incident_type = "Malware"
        severity = "High"
        risk_score = 84

    elif re.search(r"vulnerability|cve|zero-day|exploit", text):
        incident_type = "Vulnerability"
        severity = "Critical"
        risk_score = 92

    elif re.search(r"data breach|breach|leak", text):
        incident_type = "Data Breach"
        severity = "Critical"
        risk_score = 94

    # -------------------------
    # Sector Detection
    # -------------------------

    if re.search(r"bank|banking|finance|bitcoin|crypto|wallet", text):
        sector = "Banking"

    elif re.search(r"hospital|health|medical", text):
        sector = "Healthcare"

    elif re.search(r"government|ministry", text):
        sector = "Government"

    elif re.search(r"school|college|university", text):
        sector = "Education"

    elif re.search(r"e-commerce|shopping|amazon", text):
        sector = "E-Commerce"

    elif re.search(r"telecom", text):
        sector = "Telecom"

    # -------------------------
    # Confidence Score
    # -------------------------

    confidence = min(99, risk_score + 3)

    return {
        "incident_type": incident_type,
        "severity": severity,
        "sector": sector,
        "risk_score": risk_score,
        "confidence": confidence
    }
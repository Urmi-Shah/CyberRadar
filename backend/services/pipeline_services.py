import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from database import SessionLocal
from models import Incident
from services.ai_classifier import classify_incident

RSS_FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews"
}

def _tag_text(parent, names):
    for child in list(parent):
        tag = child.tag.split("}")[-1]
        if tag in names and child.text:
            return child.text.strip()
    return ""

def fetch_rss(url, limit=30):
    req = urllib.request.Request(url, headers={"User-Agent": "CyberRadar/2.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        xml = response.read()
    root = ET.fromstring(xml)
    items = []
    for item in root.iter():
        if item.tag.split("}")[-1] not in {"item", "entry"}:
            continue
        title = _tag_text(item, {"title"})
        summary = _tag_text(item, {"description", "summary", "content"})
        link = _tag_text(item, {"link"})
        if not link:
            for child in list(item):
                if child.tag.split("}")[-1] == "link":
                    link = child.attrib.get("href", "")
                    break
        published = _tag_text(item, {"pubDate", "published", "updated"})
        items.append({"title": title, "summary": summary, "link": link, "published": published})
        if len(items) >= limit:
            break
    return items

def _date_from_text(text):
    if not text:
        return datetime.now()
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"
    ]:
        try:
            return datetime.strptime(text.strip(), fmt).replace(tzinfo=None)
        except ValueError:
            pass
    return datetime.now()

def sync_pipeline():
    db = SessionLocal()
    added = 0
    found = 0
    errors = []
    articles = []
    try:
        for source, url in RSS_FEEDS.items():
            try:
                entries = fetch_rss(url)
                found += len(entries)
                for entry in entries:
                    title = entry["title"] or "Untitled"
                    summary = re.sub(r"<[^>]+>", " ", entry["summary"] or "").strip()
                    link = entry["link"] or ""
                    # Store link in description because the current schema predates source_url.
                    exists = db.query(Incident).filter(Incident.description == link).first() if link else None
                    if exists:
                        continue
                    analysis = classify_incident(title, summary)
                    dt = _date_from_text(entry["published"])
                    obj = Incident(
                        incident_id=f"LIVE-{abs(hash(link or title))}",
                        date=dt.strftime("%Y-%m-%d"), year=dt.year, month=dt.strftime("%B"),
                        state="Unknown", city="Unknown", incident_type=analysis["incident_type"],
                        severity=analysis["severity"], sector=analysis["sector"], financial_loss_inr=0,
                        affected_users=0, status="Active", source=source, description=link,
                        ai_summary=summary[:1000], recommendation="Review the advisory and apply relevant mitigations."
                    )
                    db.add(obj); added += 1
                    articles.append({"title":title,"source":source,"date":dt.strftime("%Y-%m-%d"),
                                     "incident_type":analysis["incident_type"],"severity":analysis["severity"],
                                     "sector":analysis["sector"],"risk_score":analysis["risk_score"],
                                     "confidence":analysis["confidence"],"link":link})
            except Exception as e:
                errors.append(f"{source}: {e}")
        db.commit()
        return {"pipeline_status":"Completed" if not errors else "Completed with warnings",
                "last_sync":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"articles_found":found,
                "records_added":added,"articles":articles,"errors":errors}
    finally:
        db.close()

# CyberRadar — Data + Scraping + Analytics Phase

This version focuses on the first working end-to-end milestone:

**Historical dataset + manual entry + live web scraping → SQLite → Pandas/NumPy analysis → dropdown/checkbox query → dynamic charts.**

## What is working

### 1. Historical dataset
The supplied 10,000-record CyberRadar dataset is already stored in `backend/cyberradar.db`.

### 2. Manual entry
Use **Manual Entry** on the dashboard. The incident is inserted into SQLite and immediately included in the next analysis query.

### 3. Web scraping
Click **Sync Now**. CyberRadar fetches The Hacker News RSS feed, classifies each article with the existing rule-based cyber classifier, deduplicates against stored links, and inserts new incidents.

If the computer has no internet connection, the sync will report the source error instead of crashing the application.

### 4. Dynamic analysis
The dashboard uses Pandas and NumPy against the SQLite dataset.

Filters:
- All data
- Today
- Yesterday
- Last 7 days
- Last 30 days
- Last 6 months
- Last 1 year
- Custom date range
- State
- City
- Attack type
- Sector
- Source
- Status
- Multiple severity checkboxes
- Search

### 5. Charts
The query drives:
- Incident trend
- Attack distribution
- Severity distribution
- Top states
- Top cities
- Financial loss trend
- Sector distribution
- Source distribution

Nothing in the KPI/chart layer is hardcoded.

## Run

```cmd
cd CyberRadar\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/app/dashboard.html
```

## Important

Do not open `dashboard.html` directly with `file://`. Run FastAPI first so the page can call the APIs.

## Next phase

After this milestone is verified, add:

1. Excel/CSV upload from the UI
2. NVD + CISA ingestion
3. 3-hour scheduler
4. ML train/test + cross-validation
5. TensorFlow forecasting
6. Threat map
7. Reports
8. Authentication

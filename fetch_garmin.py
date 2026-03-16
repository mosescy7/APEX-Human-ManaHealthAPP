"""
fetch_garmin.py
---------------
Connects to Garmin Connect and saves your data as CSV files into garmin_data/.
Run this once (or whenever you want fresh data):

    python fetch_garmin.py

The R Markdown dashboard (garmin_dashboard.Rmd) then reads those CSVs.
"""

import os, json, warnings
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from garminconnect import Garmin
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# ── credentials ──────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / '.env')
email    = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')

if not email or not password:
    import getpass
    email    = input("Garmin email: ")
    password = getpass.getpass("Garmin password: ")

print(f"Logging in as {email} ...")
api = Garmin(email, password)
api.login()
print("Logged in.\n")

TODAY   = date.today()
OUT_DIR = Path(__file__).parent / 'garmin_data'
OUT_DIR.mkdir(exist_ok=True)

def save(df, name):
    path = OUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  Saved {name}.csv  ({len(df)} rows)")

# ── steps (30 days) ───────────────────────────────────────────────────────────
print("Fetching steps ...")
rows = []
for i in range(30):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_steps_data(d)
        rows.append({'date': d, 'steps': sum(s.get('steps', 0) for s in (data or []))})
    except Exception:
        pass
save(pd.DataFrame(rows).sort_values('date'), 'steps')

# ── heart rate (30 days) ─────────────────────────────────────────────────────
print("Fetching heart rate ...")
rows = []
for i in range(30):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_heart_rates(d)
        if data:
            rows.append({
                'date':       d,
                'resting_hr': data.get('restingHeartRate'),
                'max_hr':     data.get('maxHeartRate'),
                'min_hr':     data.get('minHeartRate'),
            })
    except Exception:
        pass
save(pd.DataFrame(rows).sort_values('date'), 'heart_rate')

# ── HRV (30 days) ─────────────────────────────────────────────────────────────
print("Fetching HRV ...")
rows = []
for i in range(30):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_hrv_data(d)
        if data and data.get('hrvSummary'):
            s = data['hrvSummary']
            rows.append({
                'date':        d,
                'weekly_avg':  s.get('weeklyAvg'),
                'last_night':  s.get('lastNight'),
                'status':      s.get('status', ''),
            })
    except Exception:
        pass
save(pd.DataFrame(rows).sort_values('date'), 'hrv')

# ── sleep (30 days) ───────────────────────────────────────────────────────────
print("Fetching sleep ...")
rows = []
for i in range(30):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_sleep_data(d)
        if data and data.get('dailySleepDTO'):
            dto = data['dailySleepDTO']
            rows.append({
                'date':   d,
                'total':  round((dto.get('sleepTimeSeconds') or 0) / 3600, 2),
                'deep':   round((dto.get('deepSleepSeconds') or 0) / 3600, 2),
                'light':  round((dto.get('lightSleepSeconds') or 0) / 3600, 2),
                'rem':    round((dto.get('remSleepSeconds') or 0) / 3600, 2),
                'awake':  round((dto.get('awakeSleepSeconds') or 0) / 3600, 2),
                'score':  (dto.get('sleepScores') or {}).get('overall', {}).get('value'),
            })
    except Exception:
        pass
save(pd.DataFrame(rows).sort_values('date'), 'sleep')

# ── body battery (14 days) ────────────────────────────────────────────────────
print("Fetching body battery ...")
rows = []
try:
    start_d = (TODAY - timedelta(days=14)).isoformat()
    bb_data = api.get_body_battery(start_d, TODAY.isoformat())
    for day in (bb_data or []):
        for entry in (day.get('bodyBatteryValuesArray') or []):
            if entry and len(entry) >= 2 and entry[1] is not None:
                rows.append({
                    'datetime': pd.to_datetime(entry[0], unit='ms').isoformat(),
                    'battery':  entry[1]
                })
except Exception as e:
    print(f"  Body battery skipped: {e}")
save(pd.DataFrame(rows), 'body_battery')

# ── stress (14 days) ──────────────────────────────────────────────────────────
print("Fetching stress ...")
rows = []
for i in range(14):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_stress_data(d)
        if data:
            rows.append({
                'date': d,
                'avg_stress': data.get('avgStressLevel'),
                'max_stress': data.get('maxStressLevel'),
            })
    except Exception:
        pass
save(pd.DataFrame(rows).sort_values('date'), 'stress')

# ── respiration (14 days) ─────────────────────────────────────────────────────
print("Fetching respiration ...")
rows = []
for i in range(14):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_respiration_data(d)
        if data:
            rows.append({
                'date':        d,
                'awake_brpm':  data.get('avgWakingRespirationValue'),
                'sleep_brpm':  data.get('avgSleepRespirationValue'),
            })
    except Exception:
        pass
save(pd.DataFrame(rows).sort_values('date'), 'respiration')

# ── SpO2 (14 days) ────────────────────────────────────────────────────────────
print("Fetching SpO2 ...")
rows = []
for i in range(14):
    d = (TODAY - timedelta(days=i)).isoformat()
    try:
        data = api.get_spo2_data(d)
        if data and data.get('spO2HourlyAverages'):
            for entry in data['spO2HourlyAverages']:
                if entry.get('value'):
                    rows.append({
                        'datetime': entry.get('startGMT', ''),
                        'spo2':     entry['value']
                    })
    except Exception:
        pass
save(pd.DataFrame(rows), 'spo2')

# ── activities (last 50) ──────────────────────────────────────────────────────
print("Fetching activities ...")
rows = []
try:
    activities = api.get_activities(0, 50)
    for a in (activities or []):
        rows.append({
            'date':         a.get('startTimeLocal','')[:10],
            'type':         a.get('activityType', {}).get('typeKey','').replace('_',' ').title(),
            'distance_km':  round((a.get('distance') or 0) / 1000, 2),
            'duration_min': round((a.get('duration') or 0) / 60, 1),
            'avg_hr':       a.get('averageHR'),
            'max_hr':       a.get('maxHR'),
            'calories':     a.get('calories'),
            'elevation_m':  a.get('elevationGain'),
            'vo2max':       a.get('vO2MaxValue'),
        })
except Exception as e:
    print(f"  Activities skipped: {e}")
save(pd.DataFrame(rows).sort_values('date', ascending=False), 'activities')

print(f"\nDone! All CSVs saved to: {OUT_DIR}")
print("Now open garmin_dashboard.Rmd in RStudio or VS Code and knit it.")

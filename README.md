# APEX-Human-ManaHealthApp

## The APEX Human

The north star of this project is the **APEX Human** — a person who consistently performs at their highest potential across body, mind, and environment, sustainably over a lifetime.

This means optimising seven interconnected domains simultaneously:

| Domain | What It Covers |
|---|---|
| Physical | VO2 max, strength, body composition, mobility |
| Metabolic | Blood glucose, insulin sensitivity, CGM data |
| Biochemical / Hormonal | Blood biomarkers, hormones, epigenetic age |
| Cognitive | Working memory, processing speed, focus, BDNF |
| Psychological | HRV, resilience, emotional regulation, wellbeing |
| Environmental | Light, air quality, temperature, nature exposure |
| Purpose & Meaning | Ikigai, values, social connection, flow state |

No domain operates alone. The interactions between them — sleep affecting hormones, stress degrading gut integrity, muscle mass determining glucose metabolism — are where performance is actually determined. Mana Health exists to map those interactions and turn them into actionable intelligence.

---

## Mana Health App

### Overview

**Mana Health** is a personal health intelligence platform designed to optimize human performance using data. It is the engineering implementation of the APEX Human framework — integrating **biological, behavioral, and environmental data** into a single system that analyzes patterns and generates insights to help you perform at the highest level in sports, health, and daily life.

Mana Health combines data from:

* Blood work biomarkers
* Wearable health devices (Garmin / Apple Watch)
* Smart scale body composition
* Training performance metrics
* Nutrition tracking
* Sleep and recovery data
* Lifestyle habits and routines

The platform uses data engineering, statistical analysis, and machine learning to identify patterns and recommend optimizations that improve:

* Athletic performance
* Recovery and fatigue management
* Energy levels
* Metabolic health
* Longevity and resilience

The long-term vision is to create a **data-driven personal optimization engine for human performance.**

---

### Core Philosophy

High-level performance in sport and life depends on the interaction of multiple systems:

* Physiology
* Nutrition
* Recovery
* Training
* Environment
* Daily habits

Mana Health aims to quantify these systems and transform them into **actionable intelligence**.

Instead of guessing what improves performance, Mana Health relies on **measured biological signals and behavioral data**.

---

## Data Sources

Mana Health integrates multiple streams of health and lifestyle data.

### Blood Work (Biomarkers)

Blood work provides deep insight into physiological health and recovery capacity.

#### Metabolic Health
* Glucose
* HbA1c
* Insulin
* Cholesterol
* Triglycerides

#### Inflammation
* CRP
* Homocysteine

#### Hormones
* Testosterone
* Cortisol
* Thyroid (TSH, T3, T4)

#### Nutrient Levels
* Vitamin D
* Iron / Ferritin
* Magnesium
* B12

Blood markers help detect:
* Overtraining
* Nutrient deficiencies
* Hormonal imbalance
* Recovery capacity

---

### Wearable Data (Garmin / Apple Watch)

Wearables provide continuous physiological monitoring.

#### Cardiovascular
* Resting heart rate
* Heart rate variability (HRV)
* Heart rate zones

#### Activity
* Running, Cycling, Swimming
* Steps and Distance
* Training load

#### Sleep
* Sleep duration
* Sleep stages (Deep, REM, Light, Awake)
* Sleep consistency and score

#### Recovery
* Stress scores
* Body battery (Garmin)
* Recovery metrics

---

### Smart Scale Data

* Body weight
* Body fat percentage
* Lean mass / Muscle mass
* Hydration
* Bone mass

---

### Training Data

Sports tracked: Running · Cycling · Swimming · Strength · Endurance

Example metrics: Pace · Distance · Time · Power · VO₂ Max · Training load

---

### Nutrition Tracking

* Calories
* Macronutrients (protein, carbs, fats)
* Meal timing and hydration
* Micronutrients

---

### Lifestyle Data

* Sleep schedule
* Sauna and cold exposure
* Sun exposure (Vitamin D)
* Stress levels
* Daily routine

---

## System Architecture

```
Data Sources
│
├── Blood Work Labs
├── Garmin Watch API
├── Smart Scale
├── Nutrition Logs
├── Training Sessions
└── Lifestyle Tracking
        │
        ▼
Data Ingestion Layer
(API + Data Connectors)
        │
        ▼
Central Database
(SQL / Data Warehouse)
        │
        ▼
Analytics Layer
(Python / R / Statistical Models)
        │
        ▼
Insight Engine
(Correlations + Pattern Detection)
        │
        ▼
Visualization & Dashboard
(Web App / BI Tools)
```

---

## Analytics & Modeling

### Correlation Analysis
* Does sleep duration influence running performance?
* How does HRV relate to training intensity?
* Does sun exposure correlate with Vitamin D levels?

### Time Series Analysis
* Biomarker trends over time
* Training adaptation curves
* Body composition shifts

### Predictive Modeling
* Fatigue prediction from HRV and sleep data
* Performance forecasting from training load
* Injury risk scoring from overtraining signals

### Pattern Detection
* Identifying recovery patterns
* Detecting nutrition deficiencies from performance drops
* Correlating lifestyle habits with biomarker changes

---

## Current Implementation — Garmin Connect Dashboard

The current phase of Mana Health focuses on pulling live data from **Garmin Connect** and visualizing it in an interactive dashboard. This is implemented across three files:

| File | Purpose |
|------|---------|
| `fetch_garmin.py` | Authenticates with Garmin Connect API and saves all health data to CSV files in `garmin_data/` |
| `garmin_dashboard.ipynb` | Jupyter notebook — interactive charts, runs cell by cell in VS Code |
| `garmin_dashboard.Rmd` | R Markdown version — same charts using ggplot2 + plotly (requires R + RStudio) |
| `garmin_dashboard.html` | Standalone HTML dashboard — opens directly in any browser, no installs required |

---

### Garmin Dashboard — Sections & Metrics

#### Section 1 · Login to Garmin Connect
Authenticates using credentials stored in `.env` (never hardcoded). Falls back to interactive prompt if `.env` is not present.

```
GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=yourpassword
```

#### Section 2 · Steps (Last 30 Days)
* Daily step count bar chart
* 10,000-step daily goal line
* 30-day average and goal attainment count

**API call:** `api.get_steps_data(date)`

#### Section 3 · Heart Rate (Last 30 Days)
* Resting HR trend line with markers
* Max HR and Min HR dotted reference lines
* Shaded HR range band
* 30-day avg resting HR and avg max HR

**API call:** `api.get_heart_rates(date)`

#### Section 4 · HRV Status (Last 30 Days)
Heart Rate Variability (SDNN) — a key recovery and readiness indicator.

* Last-night HRV bar chart (colour-scaled low → high)
* 7-day rolling average overlay line
* Average last-night and weekly HRV values

**API call:** `api.get_hrv_data(date)`

> Requires a compatible Garmin device with wrist HRV tracking (e.g. Forerunner 955, Fenix 7, Epix).

#### Section 5 · Sleep (Last 30 Days)
* Stacked bar chart: Deep / REM / Light / Awake hours per night
* 8-hour goal reference line
* Sleep score trend (line + markers, colour-scaled 0–100)
* Summary: avg total, deep, REM sleep and avg sleep score

**API call:** `api.get_sleep_data(date)`

#### Section 6 · Body Battery (Last 14 Days)
* Continuous body battery level area chart (hourly resolution)
* "Low battery" (25) alert line
* Daily max and min battery averages

**API call:** `api.get_body_battery(start_date, end_date)`

#### Section 7 · Stress (Last 14 Days)
* Daily average stress bar chart
* Colour-coded: green (low) → yellow (medium) → orange (high) → red (very high)
* Average stress level summary

**API call:** `api.get_stress_data(date)`

#### Section 8 · Recent Activities (Last 50)
* Sortable activity table: Date · Type · Distance · Duration · Avg HR · Calories · Elevation
* Pie chart: activity type distribution
* Bar chart: monthly total activity minutes

**API call:** `api.get_activities(start, limit)`

#### Section 9 · Training Status & VO₂ Max
* VO₂ Max trend over time (extracted from activity records)
* Raw training load JSON summary

**API calls:** `api.get_activities()`, `api.get_training_load()`

#### Section 10 · Respiration Rate (Last 14 Days)
* Awake vs asleep breathing rate comparison lines
* Average waking and sleep respiration values

**API call:** `api.get_respiration_data(date)`

#### Section 11 · Blood Oxygen — SpO₂ (Last 14 Days)
* Hourly SpO₂ area chart
* 95% threshold alert line
* Average and minimum SpO₂ values

**API call:** `api.get_spo2_data(date)`

> Requires a Garmin device with pulse oximetry (e.g. Forerunner 945/955, Fenix series).

#### Section 12 · Health Snapshot (Today)
A summary table of today's key metrics:

| Metric | Source |
|--------|--------|
| Resting HR | Heart rate API |
| Steps today | Steps API |
| Last night sleep | Sleep API |
| Sleep score | Sleep API |
| HRV (last night) | HRV API |
| HRV status | HRV API |
| Avg stress | Stress API |

---

## Setup & Usage

### Prerequisites

```bash
# Python 3.10+
pip install garminconnect plotly pandas python-dotenv nbformat ipykernel
```

### Credentials

Create a `.env` file in this directory:

```
GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=yourpassword
```

> `.env` is listed in `.gitignore` and will never be committed to version control.

### Running the Dashboard

**Option A — HTML (no installs beyond Python):**
```bash
python fetch_garmin.py          # fetch fresh data
python generate_html_dashboard.py   # build + open in browser
```

**Option B — Jupyter Notebook in VS Code:**
1. Open `garmin_dashboard.ipynb` in VS Code
2. Select Python 3 kernel
3. Run All Cells (`Ctrl+Shift+P` → "Notebook: Run All Cells")

**Option C — R Markdown (requires R + RStudio):**
1. Install R: https://cran.r-project.org
2. Install RStudio: https://posit.co/download/rstudio-desktop/
3. Run `python fetch_garmin.py` to fetch data
4. Open `garmin_dashboard.Rmd` in RStudio and press **Knit**

### Refreshing Data

```bash
python fetch_garmin.py
```

Re-run whenever you want the latest data. The HTML and notebook dashboards will pick up the new CSVs automatically.

---

## Project Files

```
apple_health_export/
│
├── .env                         # Garmin credentials (gitignored)
├── .gitignore
│
├── fetch_garmin.py              # Pulls data from Garmin Connect API → CSV
├── generate_html_dashboard.py   # Builds standalone HTML dashboard
├── build_notebook.py            # Regenerates the Jupyter notebook
│
├── garmin_dashboard.ipynb       # Jupyter notebook dashboard (VS Code)
├── garmin_dashboard.Rmd         # R Markdown dashboard (RStudio)
├── garmin_dashboard.html        # Standalone HTML dashboard (browser)
│
└── garmin_data/                 # CSV exports from Garmin API
    ├── steps.csv
    ├── heart_rate.csv
    ├── hrv.csv
    ├── sleep.csv
    ├── body_battery.csv
    ├── stress.csv
    ├── respiration.csv
    ├── spo2.csv
    └── activities.csv
```

---

## Roadmap to the APEX Human

### Phase 1 — Wearable Foundation (Current)
Track the continuous physiological signals that define physical and recovery status.

- [x] Garmin Connect API integration
- [x] Interactive HTML dashboard
- [x] Jupyter notebook dashboard
- [x] R Markdown dashboard
- [ ] Apple Watch / Oura Ring integration
- [ ] HRV-based daily readiness score

### Phase 2 — Metabolic Layer
Understand how the body processes fuel and manages blood sugar — the engine behind energy, performance, and longevity.

- [ ] Continuous glucose monitoring (CGM) integration — Levels / Dexcom
- [ ] Smart scale integration (Withings) — body composition over time
- [ ] Nutrition log integration — calories, macros, meal timing
- [ ] Metabolic score: glucose variability, time-in-range, fasting insulin trend

### Phase 3 — Biochemical & Hormonal Layer
Surface what the bloodwork reveals — the chemical signals that drive everything from recovery capacity to cognitive sharpness.

- [ ] Blood work biomarker tracking module — manual entry + trend analysis
- [ ] Hormone panel tracking — testosterone, cortisol curve, thyroid, Vitamin D
- [ ] Supplement and medication logging
- [ ] Epigenetic age tracking (TruDiagnostic TruAge) — DunedinPACE over time

### Phase 4 — Cognitive Layer
Measure and improve the brain's capacity for focus, learning, and decision-making.

- [ ] Daily cognitive assessment module — reaction time, working memory, processing speed
- [ ] Flow state frequency tracking
- [ ] Sleep architecture → cognitive performance correlation
- [ ] EEG integration (Muse S) — attention quality and meditation depth

### Phase 5 — Psychological Layer
Quantify resilience, emotional regulation, and wellbeing — the foundation that determines how much of your biological capacity you can actually access.

- [ ] Daily check-in — subjective energy, focus, mood, stress (1-minute input)
- [ ] PERMA wellbeing score — tracked weekly
- [ ] HRV ↔ mood correlation — does measured recovery predict reported wellbeing?
- [ ] Cortisol diurnal curve — salivary testing logged over time

### Phase 6 — Environmental Layer
Monitor the invisible inputs — light, air, temperature — that shape biology passively and continuously.

- [ ] Indoor air quality integration (Awair / IQAir) — CO2, PM2.5, VOCs
- [ ] Morning sunlight and evening light exposure logging
- [ ] Sleep environment tracking — temperature, darkness, noise
- [ ] Sauna and cold exposure session logging

### Phase 7 — Intelligence Engine
Move from dashboards to decisions — correlate every domain, detect patterns, and generate personalised recommendations.

- [ ] Cross-domain correlation engine — what affects what, with what time lag?
- [ ] Personal baseline modelling — individual reference ranges, not population averages
- [ ] Predictive fatigue model from HRV, sleep, and training load
- [ ] Injury risk scoring from overtraining signals
- [ ] LLM-powered natural language insights ("Your glucose variability was highest on days following under 5 hours of sleep")
- [ ] Priority intervention queue — top 3 actions most likely to move the needle today

### Phase 8 — Purpose & Meaning Layer
The most overlooked domain with the strongest longitudinal evidence for longevity and sustained performance.

- [ ] Ikigai and meaning-in-life score — tracked over time
- [ ] Values clarity and goal alignment module
- [ ] Social connection metrics — relationship quality, loneliness index
- [ ] Weekly reflection and RPM planning integration

### Phase 9 — Unified APEX Dashboard
Bring every domain into a single, unified application.

- [ ] Web application with full cross-domain dashboard
- [ ] APEX Score — a single daily composite score across all seven domains
- [ ] Mobile-responsive interface
- [ ] Weekly and monthly performance reports
- [ ] Longitudinal trends across all biomarkers and lifestyle inputs

---

## Author

Moses Cyabukombe
# Ornament Health — Integration Research

**App:** Ornament Health (ornament.health)
**Purpose:** Personal biomarker and lab test tracking app
**Role in Mana Health:** Primary source for blood work, hormones, and biochemical data

---

## What Ornament Does

Ornament is a personal health record app focused on lab data. It lets you:

- Upload and store lab test results and blood work
- Track biomarker trends over time with reference ranges
- Auto-import lab results from Gmail (LabCorp, MyQuest, etc.)
- Get insights and flags on out-of-range values
- Aggregate results from multiple labs into one place

---

## Data Export (Regular User)

| Format | Available |
|---|---|
| PDF | Yes — Monitor > Documents > Export to PDF |
| CSV | No |
| JSON | No |
| HL7 FHIR | No |

Export is limited to PDF only for standard users. No automated or structured data export is available without API access.

---

## API

Ornament has a documented REST API hosted at `https://ornament.readme.io/reference/getting-started-with-your-api`.

**Status: B2B gated — not a free public consumer API.**

### Access Requirements
- Requires creating a **Healer account in Ornament Pro** (their B2B web portal)
- Requires generating an API key from that account
- Pricing is not publicly listed — contact `b2b@ornament.health`

### API Endpoints (9 categories)
- **Medical Data API** — biomarkers, profiles, health records (returns JSON) ← most relevant
- **File API** — document upload and storage
- **Health Advisor API** — health condition insights
- **Accounting API** — patient/user account management
- **Thesaurus API** — reference data: 4,100+ biomarkers, diseases, medications
- Image Set API, Linked Profiles, Submissions, Diseases

### Authentication
Bearer token authentication.

---

## Third-Party Integrations

| Integration | Direction | Notes |
|---|---|---|
| Apple Health | Ornament → Apple Health (outbound only) | Lab values unlikely to sync into Apple Health native types |
| Gmail | Gmail → Ornament | Auto-imports LabCorp, MyQuest lab result emails |
| SelfDecode | B2B partnership | SelfDecode embedded Ornament's PDF digitization service |
| Garmin | None | No integration exists |
| Oura / WHOOP | None | No integration exists |

---

## Developer Documentation

- Hosted at `https://ornament.readme.io`
- Covers authentication, full endpoint reference, webhook integration
- No public SDK or open-source libraries
- GitHub: `github.com/Ornament-Health` — internal React Native components only, nothing public-facing

---

## Integration Options for Mana Health

### Option 1 — Ornament B2B API (Best)
Contact Ornament directly and request developer API access. The **Medical Data API** returns biomarkers as structured JSON — exactly what Mana Health needs.

**Contact:** `b2b@ornament.health`
**Ask:** Whether individual developers can get Ornament Pro API access, and what the pricing is.

If approved, the pipeline would be:
```
Ornament Medical Data API (JSON)
        ↓
fetch_ornament.py (new script, similar to fetch_garmin.py)
        ↓
ornament_data/*.csv (biomarkers, trends, reference ranges)
        ↓
Mana Health Dashboard
```

### Option 2 — PDF Parsing (Manual Fallback)
Export PDF from Ornament → parse with a Python PDF extraction library (e.g. `pdfplumber`, `camelot`).

- Pros: No API access required
- Cons: Manual, fragile, requires re-running every time data is updated

### Option 3 — Build Direct Lab Import
Pull lab data directly from LabCorp / MyQuest via their FHIR R4 patient portals (available under the 21st Century Cures Act). Bypasses Ornament entirely.

### Option 4 — Alternative Platforms
If Ornament remains a walled garden, consider platforms with more open integration:
- **Heads Up Health** — connects wearables + labs; physician-grade dashboard
- **Function Health** — 100+ biomarker annual subscription with structured data access
- **InsideTracker** — sport + health optimization blood panel with API

---

## Recommended Next Step

Email Ornament B2B at `b2b@ornament.health`:

> *"I'm a developer building a personal health intelligence platform. I use Ornament to track my blood work and biomarkers and would like to integrate my own data via your Medical Data API. Is API access available for individual developers under Ornament Pro, and what does pricing look like?"*

---

## Status

- [ ] Contact Ornament B2B re: API access
- [ ] Evaluate PDF parsing as interim solution
- [ ] Add Ornament as Phase 3 data source in Mana Health roadmap once access confirmed
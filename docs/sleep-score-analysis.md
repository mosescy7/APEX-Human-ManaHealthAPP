# Sleep Score Analysis — Path to Consistent 90+

**Data window:** 30 nights, Feb 15 – Mar 16, 2026 (`garmin_data/*.csv`, pulled via Garmin Connect API)
**Analysis date:** 2026-06-19

## Data scope note (read this first)

This export does not contain a `DI_CONNECT` folder or raw per-night JSON — `garmin_data/` has 9 CSVs pulled via `fetch_garmin.py`, covering **30 nights only**. A few real constraints this puts on the analysis:

- **Zero nights scored 90+. Zero nights even scored 80+.** The ceiling in this window is **77** (Mar 1). "What happened on 90+ nights" can't be answered directly — it hasn't happened yet. Section 2 below reverse-engineers it from the best nights (top-7, ≥70) vs. worst instead, and uses regression to show how far that is from 90+.
- `sleep.csv` has no bedtime/wake-clock timestamps — only duration, stages, score. Bedtime *consistency* can't be measured directly; day-of-week patterns are used as a proxy.
- `hrv.csv` only has `weekly_avg` — `last_night` is empty for every row. The weekly trend is used, not nightly HRV-vs-score correlation.
- `stress.csv` and `respiration.csv` only start **Mar 3** (missing the first 2.5 weeks).

None of this blocks a real, numbers-grounded report — it just means the current ceiling is reported honestly instead of dressed up.

---

## 1. Current sleep profile

| Metric | Value |
|---|---|
| Nights tracked | 30 (Feb 15 – Mar 16) |
| Mean score | **58.8** (SD 14.2) |
| Median | 63 |
| Range | 19 – **77** |
| Nights 90+ / 80+ | **0 / 0** |
| Nights "Fair" (60–79) | 17/30 (57%) |
| Nights "Poor" (<60) | 13/30 (43%) |
| Avg total sleep | **6.08 h** (SD 1.8 h) |
| Nights <7h | 21/30 (70%) |
| Nights ≥8h | 3/30 (10%) |
| Avg deep / light / REM / awake | 19.6% / 75.2% / **5.3%** / 9.2% |
| Trend (1st half vs 2nd half) | 58.1 → 59.6 (flat — no improvement over the month) |

Using Garmin's own bands (90–100 Excellent, 80–89 Good, 60–79 Fair, <60 Poor), this dataset never once hit "Good," let alone "Excellent" — it oscillates entirely within Fair/Poor. The single biggest number here is **REM at 5.3% of total sleep** — healthy adult REM is ~20–25%. That's not a small gap; it's the headline finding of this whole dataset.

---

## 2. What happened on the best nights (no 90+ nights exist yet)

Since there's no 90+ precedent, the **top-7 nights (score ≥70)** were compared against the **bottom-7 (score ≤48)**:

| | Top 7 | Bottom 7 |
|---|---|---|
| Avg score | 73.6 | 37.9 |
| Avg total sleep | **7.47 h** | 3.67 h |
| Avg REM% | **9.1%** | **0.22%** |
| Avg awake% | **3.5%** | **20.9%** |
| Avg deep% | 18.9% | 25.4%* |

*Deep% is *higher* on the worst nights — a math artifact of short, fragmented sleep, not a real signal. **Deep sleep is not the lever here.**

Correlations across all 30 nights confirm it:

| Variable | r vs. score |
|---|---|
| Total sleep duration | **+0.875** |
| REM (hours) | +0.77 |
| REM % | +0.74 |
| Awake % | **−0.41** |
| Deep % | −0.19 (noise) |

**What went right, every single time:** every top-7 night combined ≥6.85h of sleep with <6.3% awake time. Every time *either* condition broke — even with plenty of total sleep — the score dropped. Examples: Mar 9 (8.13h, but 0% REM, scored only 57), Feb 20 (7.2h but 14.3% awake, scored 66), Mar 12 (8.22h but 10.7% awake, scored 63). **Duration alone doesn't save a fragmented night.**

What *didn't* matter: prior-day exercise. Some top nights followed full rest days (Mar 1, Feb 18, Feb 19), others followed heavy training days (Feb 27: run+treadmill+strength, 98 min; Mar 6: long run+strength, 118 min). Correlation between prior-day training load and that night's score is essentially zero (r = −0.03 to +0.11). **Working out isn't the problem here — duration and fragmentation are.**

A regression (`score ≈ 17 + 6.9 × hours`) tells the real ceiling story: extrapolating the current trend to **9.5h predicts only ~82**. Duration alone — even maxed out — plateaus in the low 80s. **Getting to 90+ requires fixing fragmentation and REM simultaneously, not just sleeping longer.**

---

## 3. Key barriers (ranked by data weight)

1. **Chronic sleep restriction.** Avg 6.08h, 70% of nights under 7h, only 3/30 nights ≥8h. This is the dominant lever (r=0.875) and the biggest deficit.
2. **Fragmentation.** Avg awake% = 9.2%, but 7/30 nights exceed 10% — up to **69%** on Feb 17 and **37%** on Mar 13. This is the #2 lever (r=−0.41) and it multiplies with duration — long nights with high awake% still cap out in the 50s-60s.
3. **REM is functionally absent.** Avg 5.3% vs. a 20–25% norm, and **8 of 30 nights (27%) had literally zero REM recorded.** Mechanistically: REM concentrates in the back half of the night, so truncated sleep selectively strips it out — exactly what the data shows (deep% holds up, REM% collapses).
4. **Declining HRV under heavy, near-daily training load.** Weekly HRV avg fell from a peak of 71 (Feb 21) to lows of 59 (Mar 10/13) — a 17% drop over the month — while training included near-daily running/strength/swimming plus two ultra efforts just before this window (51km and 59.6km runs, late Jan) and an 8-hour, 3,596-kcal hike on Feb 21. That hike was followed by the **worst 3-night stretch in the entire dataset: 29 → 47 → 19** (Feb 23 barely registered any sleep at all).
5. **No fixed weekly rhythm — Sunday night is the weak point.** Monday-dated nights (reflecting Sunday-night sleep) average **47.2** — the worst of any day — with only **5.10h** average duration, vs. Thursday's 70.0 average score and 7.30h duration. That's a 2.2-hour weekly swing in sleep opportunity depending on day of week.

Worth a separate flag, not a top-5 item: **Mar 9 — 8.13h of sleep with 0% REM and the lowest deep% in the whole dataset (9.2%, almost all light sleep).** That's a long night with almost no real architecture. If this recurs without an obvious cause (late alcohol, big meal, screen use), it's worth mentioning to a doctor — long-duration/zero-REM nights are a pattern sometimes seen with sleep-disordered breathing.

---

## 4. Personalized action plan (highest impact first)

**1. Fix time-in-bed first: 8.5–9h every night, no exceptions, for 2 weeks.**
Why: r=0.875 with score; the regression says moving from 6.08h to 9h alone would lift the average into the high-70s/low-80s. This is the single highest-leverage change available.
Timeline: visible score lift within 3–5 nights; sustained average shift in ~2 weeks.

**2. Attack fragmentation specifically — get awake% under 6% (the top-night average).**
Why: it's the #2 lever and it *gates* duration — Mar 9 (8.13h) and Mar 12 (8.22h) both got capped in the 50s/60s purely because of restlessness. Audit alcohol/caffeine timing, room temperature, screens before bed, and watch-band fit (a loose band can read as restlessness).
Timeline: 1–2 weeks to see awake% trend down.

**3. Protect Sunday night with the same fixed schedule used mid-week.**
Why: Monday-dated nights average 47.2 and 5.1h vs. Thursday's 70.0 and 7.3h — this single weekly dip is dragging the whole month's average down by itself.
Timeline: 1–2 weekend cycles (~10–14 days) to flatten it.

**4. Mandatory full rest day immediately after any unusually large effort (ultra-distance runs, multi-hour hikes).**
Why: the Feb 21 8-hour hike was followed by the single worst stretch in the dataset (29→47→19), and HRV has trended down 17% over a month of near-daily training with no visible deload.
Timeline: prevents the next crash immediately; HRV should stabilize within 2–3 weeks of consistent deloads.

**5. Investigate the Mar 9 anomaly (8.13h, 0% REM) if it recurs.**
Why: REM is otherwise reliably present on long, low-fragmentation nights — a long night with zero REM doesn't fit the established pattern.
Timeline: log behavior immediately; watch for recurrence over the next 2–4 weeks.

---

## 5. Weekly routine template

| Day | Sleep window | Training | Notes |
|---|---|---|---|
| **Sun (night)** | Fixed bedtime, identical to weekdays | Easy/no training | Highest-risk night (avg score 47, 5.1h) — protect it hardest |
| **Mon** | 8.5–9h target | Easy run or rest | Recovery from weekend |
| **Tue** | 8.5–9h target | Strength or moderate run | |
| **Wed** | 8.5–9h target | Strength + run (naturally strong night, avg 68) | |
| **Thu** | 8.5–9h target | Hardest session of the week | Thursday is empirically the best sleep day (avg 70, 7.3h) — load is handled well *here* |
| **Fri** | 8.5–9h target | Moderate / easy | |
| **Sat** | 8.5–9h target | Long run / long hike if scheduled | If effort is large (>90 min or >700 kcal), Sunday becomes a mandatory rest day, not optional |
| **Sun (day)** | — | Full rest if Saturday was a big effort | Breaks the post-big-effort crash pattern seen after Feb 21 |

---

## 6. HRV & recovery rules

`hrv.csv` only has weekly averages (no nightly values), so these rules are built on the trend, not single-night triggers:

- **Weekly HRV avg drops ≥5 points over 5–7 days (e.g., 71→64):** under-recovery signal. Downgrade the next hard run/strength session to easy/active recovery, and prioritize hitting the full 9h sleep window that night.
- **Weekly HRV avg is at or below the current floor (~59–60):** don't add new training stress that week. The only goal is sleep + easy movement until it climbs back toward 65+.
- **Any single session >90 min or >700 kcal:** automatic rest day the next day, full stop — this is the rule the Feb 21 hike violated, and it cost a 3-night collapse.
- **Recommendation:** the `last_night` HRV field is empty in every row — the Garmin API supports nightly HRV, so it's worth re-pulling `fetch_garmin.py` with that field populated. Without nightly granularity, the single-night HRV dip that typically *precedes* a bad sleep night can't be caught — currently the damage is only visible in hindsight via the weekly average.

---

## 7. 30-day protocol

Starting point: avg score 58.8, avg duration 6.08h, avg awake% 9.2%, ceiling ever reached = 77.

- **Week 1 — Fix duration.** Fixed 8.5h time-in-bed, every night including weekends. Target: avg score 65–70, zero nights below 60.
- **Week 2 — Fix continuity.** Hold 8.5–9h, add the fragmentation audit (alcohol/screens/temperature/band fit) to get awake% under 8%. Target: avg score 72–76, **first night ever at 80+.**
- **Week 3 — Fix the weekly pattern.** Apply the same schedule to Sunday night specifically; enforce the mandatory rest day after any big effort. Target: avg score 75–82, multiple 80+ nights.
- **Week 4 — Tune with HRV.** Duration and continuity should be solid by now; start modulating training intensity against the weekly HRV trend from Section 6. Target: **first 85–90 nights**, moving average ~80+.

This isn't a generic plan — it's literally what the regression and correlation data say is required: an 80+ night needs both ≥8.5h *and* <6% awake time at once, which has never happened simultaneously in this 30-day record. Weeks 1–2 are about proving each lever works independently; weeks 3–4 are about holding both at once, which is the actual unlock for 90+.

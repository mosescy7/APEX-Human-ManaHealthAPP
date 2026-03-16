"""
generate_html_dashboard.py
Reads garmin_data/ CSVs and builds a standalone HTML dashboard.
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from pathlib import Path
from datetime import date

DATA  = Path(__file__).parent / "garmin_data"
TODAY = date.today()
SECTIONS = []   # list of (title, fig_or_html, stats_html)

def read(name):
    p = DATA / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def stat_row(*items):
    cards = ""
    for label, value in items:
        cards += f"""
        <div class="stat-card">
          <div class="stat-value">{value}</div>
          <div class="stat-label">{label}</div>
        </div>"""
    return f'<div class="stat-row">{cards}</div>'

# ── 1. STEPS ──────────────────────────────────────────────────────────────────
df = read("steps")
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["color"] = df["steps"].apply(lambda x: "#27ae60" if x >= 10000 else "#95a5a6")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date"], y=df["steps"],
        marker_color=df["color"],
        hovertemplate="%{x|%b %d}<br><b>%{y:,} steps</b><extra></extra>",
        name="Steps"
    ))
    fig.add_hline(y=10000, line_dash="dash", line_color="red",
                  annotation_text="10,000 goal", annotation_position="top right")
    fig.update_layout(title="Daily Steps — Last 30 Days",
                      xaxis_title=None, yaxis_title="Steps",
                      template="plotly_white", height=400,
                      yaxis=dict(tickformat=","), showlegend=False)
    avg = df["steps"].mean()
    days_goal = (df["steps"] >= 10000).sum()
    stats = stat_row(
        ("30-day Average", f"{avg:,.0f} steps/day"),
        ("Days ≥ 10,000", f"{days_goal} / {len(df)}"),
        ("Best Day", f"{df['steps'].max():,}"),
    )
    SECTIONS.append(("Steps", fig, stats))

# ── 2. HEART RATE ─────────────────────────────────────────────────────────────
df = read("heart_rate").dropna(subset=["resting_hr"])
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.concat([df["date"], df["date"][::-1]]),
        y=pd.concat([df["max_hr"], df["min_hr"][::-1]]),
        fill="toself", fillcolor="rgba(231,76,60,0.1)",
        line=dict(color="rgba(0,0,0,0)"), name="HR Range", showlegend=True
    ))
    fig.add_trace(go.Scatter(x=df["date"], y=df["max_hr"],
        mode="lines", name="Max HR",
        line=dict(color="#e74c3c", width=1, dash="dot"),
        hovertemplate="%{x|%b %d}<br>Max: %{y} bpm<extra></extra>"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["resting_hr"],
        mode="lines+markers", name="Resting HR",
        line=dict(color="#8e44ad", width=2.5), marker=dict(size=6),
        hovertemplate="%{x|%b %d}<br><b>Resting: %{y} bpm</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["min_hr"],
        mode="lines", name="Min HR",
        line=dict(color="#3498db", width=1, dash="dot"),
        hovertemplate="%{x|%b %d}<br>Min: %{y} bpm<extra></extra>"))
    fig.update_layout(title="Heart Rate — Last 30 Days",
                      xaxis_title=None, yaxis_title="BPM",
                      template="plotly_white", height=400,
                      hovermode="x unified")
    stats = stat_row(
        ("Avg Resting HR", f"{df['resting_hr'].mean():.1f} bpm"),
        ("Lowest Resting", f"{df['resting_hr'].min():.0f} bpm"),
        ("Avg Max HR",     f"{df['max_hr'].mean():.1f} bpm"),
    )
    SECTIONS.append(("Heart Rate", fig, stats))

# ── 3. HRV ────────────────────────────────────────────────────────────────────
df = read("hrv").dropna(subset=["last_night"])
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["date"], y=df["last_night"],
        marker=dict(color=df["last_night"],
                    colorscale=[[0,"#f39c12"],[0.5,"#f1c40f"],[1,"#1abc9c"]],
                    cmin=df["last_night"].min(), cmax=df["last_night"].max(),
                    showscale=True, colorbar=dict(title="ms")),
        name="Last Night HRV",
        hovertemplate="%{x|%b %d}<br><b>HRV: %{y:.1f} ms</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["weekly_avg"],
        mode="lines", name="7-day Avg",
        line=dict(color="#16a085", width=2.5),
        hovertemplate="%{x|%b %d}<br>7d avg: %{y:.1f} ms<extra></extra>"))
    fig.update_layout(title="HRV (SDNN) — Last 30 Days",
                      xaxis_title=None, yaxis_title="ms",
                      template="plotly_white", height=400,
                      hovermode="x unified")
    stats = stat_row(
        ("Avg Last-Night HRV", f"{df['last_night'].mean():.1f} ms"),
        ("Avg Weekly HRV",     f"{df['weekly_avg'].mean():.1f} ms"),
        ("Best Night",         f"{df['last_night'].max():.1f} ms"),
    )
    SECTIONS.append(("HRV", fig, stats))

# ── 4. SLEEP ──────────────────────────────────────────────────────────────────
df = read("sleep")
df = df[df["total"] > 0] if not df.empty else df
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Sleep Stages (hours)", "Sleep Score"),
                        row_heights=[0.65, 0.35], vertical_spacing=0.1)
    colors = {"deep": "#1a237e", "rem": "#80cbc4", "light": "#5c6bc0", "awake": "#ef9a9a"}
    labels = {"deep": "Deep", "rem": "REM", "light": "Light", "awake": "Awake"}
    for col, color in colors.items():
        fig.add_trace(go.Bar(x=df["date"], y=df[col],
            name=labels[col], marker_color=color,
            hovertemplate=f"%{{x|%b %d}}<br>{labels[col]}: %{{y:.2f}} h<extra></extra>"), 1, 1)
    fig.add_hline(y=8, line_dash="dash", line_color="green",
                  annotation_text="8h goal", row=1, col=1)
    if "score" in df.columns and df["score"].notna().any():
        df_s = df.dropna(subset=["score"])
        fig.add_trace(go.Bar(x=df_s["date"], y=df_s["score"],
            marker=dict(color=df_s["score"],
                        colorscale=[[0,"#e74c3c"],[0.5,"#f1c40f"],[1,"#27ae60"]],
                        cmin=0, cmax=100, showscale=False),
            name="Sleep Score",
            hovertemplate="%{x|%b %d}<br><b>Score: %{y}</b><extra></extra>"), 2, 1)
    fig.update_layout(barmode="stack", template="plotly_white", height=600,
                      title="Sleep — Last 30 Days", hovermode="x unified")
    score_avg = df["score"].mean() if "score" in df.columns else float("nan")
    stats = stat_row(
        ("Avg Total Sleep", f"{df['total'].mean():.2f} h/night"),
        ("Avg Deep Sleep",  f"{df['deep'].mean():.2f} h"),
        ("Avg REM Sleep",   f"{df['rem'].mean():.2f} h"),
        ("Avg Sleep Score", f"{score_avg:.0f} / 100" if pd.notna(score_avg) else "N/A"),
    )
    SECTIONS.append(("Sleep", fig, stats))

# ── 5. BODY BATTERY ───────────────────────────────────────────────────────────
df = read("body_battery")
if not df.empty:
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.dropna(subset=["battery"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["datetime"], y=df["battery"],
        mode="lines", fill="tozeroy",
        line=dict(color="#f39c12", width=1.5),
        fillcolor="rgba(243,156,18,0.2)",
        hovertemplate="%{x|%b %d %H:%M}<br><b>Battery: %{y}</b><extra></extra>"))
    fig.add_hline(y=25, line_dash="dash", line_color="red",
                  annotation_text="Low (25)", annotation_position="bottom right")
    fig.update_layout(title="Body Battery — Last 14 Days",
                      xaxis_title=None, yaxis_title="Level (0–100)",
                      yaxis=dict(range=[0, 105]),
                      template="plotly_white", height=400)
    daily = df.groupby(df["datetime"].dt.date)["battery"]
    stats = stat_row(
        ("Avg Daily Max", f"{daily.max().mean():.0f}"),
        ("Avg Daily Min", f"{daily.min().mean():.0f}"),
        ("Overall Avg",   f"{df['battery'].mean():.0f}"),
    )
    SECTIONS.append(("Body Battery", fig, stats))

# ── 6. STRESS ─────────────────────────────────────────────────────────────────
df = read("stress").dropna(subset=["avg_stress"])
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    def stress_color(v):
        if v < 26:   return "#27ae60"
        elif v < 51: return "#f1c40f"
        elif v < 76: return "#e67e22"
        else:        return "#e74c3c"
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["date"], y=df["avg_stress"],
        marker_color=[stress_color(v) for v in df["avg_stress"]],
        hovertemplate="%{x|%b %d}<br><b>Stress: %{y}</b><extra></extra>",
        name="Avg Stress"))
    fig.update_layout(title="Daily Average Stress — Last 14 Days",
                      xaxis_title=None, yaxis_title="Stress Level (0–100)",
                      yaxis=dict(range=[0, 100]),
                      template="plotly_white", height=400, showlegend=False)
    avg = df["avg_stress"].mean()
    level = "Low" if avg < 26 else "Medium" if avg < 51 else "High" if avg < 76 else "Very High"
    stats = stat_row(
        ("Avg Stress", f"{avg:.1f} / 100"),
        ("Status",     level),
        ("Max Stress", f"{df['avg_stress'].max():.0f}"),
    )
    SECTIONS.append(("Stress", fig, stats))

# ── 7. RESPIRATION ────────────────────────────────────────────────────────────
df = read("respiration")
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["awake_brpm", "sleep_brpm"], how="all")
    fig = go.Figure()
    if "awake_brpm" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["awake_brpm"],
            mode="lines+markers", name="Awake",
            line=dict(color="#3498db", width=2), marker=dict(size=6),
            hovertemplate="%{x|%b %d}<br>Awake: %{y:.1f} brpm<extra></extra>"))
    if "sleep_brpm" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["sleep_brpm"],
            mode="lines+markers", name="Asleep",
            line=dict(color="#9b59b6", width=2), marker=dict(size=6),
            hovertemplate="%{x|%b %d}<br>Asleep: %{y:.1f} brpm<extra></extra>"))
    fig.update_layout(title="Respiration Rate — Last 14 Days",
                      xaxis_title=None, yaxis_title="Breaths / min",
                      template="plotly_white", height=400,
                      hovermode="x unified")
    stats = stat_row(
        ("Avg Awake",  f"{df['awake_brpm'].mean():.1f} brpm"),
        ("Avg Asleep", f"{df['sleep_brpm'].mean():.1f} brpm"),
    )
    SECTIONS.append(("Respiration", fig, stats))

# ── 8. ACTIVITIES ─────────────────────────────────────────────────────────────
df = read("activities")
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    # Activity type pie
    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig_pie = go.Figure(go.Pie(
        labels=type_counts["type"], values=type_counts["count"],
        textposition="inside", textinfo="label+percent",
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set2)
    ))
    fig_pie.update_layout(title="Activity Type Mix (last 50)",
                          template="plotly_white", height=450)

    # Monthly minutes
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["duration_min"].sum().reset_index()
    fig_min = go.Figure(go.Bar(x=monthly["month"], y=monthly["duration_min"],
        marker_color="#9b59b6",
        hovertemplate="%{x}<br><b>%{y:.0f} min</b><extra></extra>"))
    fig_min.update_layout(title="Monthly Activity Minutes",
                          xaxis_title=None, yaxis_title="Minutes",
                          template="plotly_white", height=400)

    # VO2 max trend
    df_vo2 = df.dropna(subset=["vo2max"]).sort_values("date")
    fig_vo2 = None
    if not df_vo2.empty:
        fig_vo2 = go.Figure()
        fig_vo2.add_trace(go.Scatter(x=df_vo2["date"], y=df_vo2["vo2max"],
            mode="lines+markers", name="VO2 Max",
            line=dict(color="#e67e22", width=2.5), marker=dict(size=7),
            hovertemplate="%{x|%b %d}<br><b>VO₂ Max: %{y:.1f}</b><extra></extra>"))
        fig_vo2.update_layout(title="VO₂ Max Over Time",
                              xaxis_title=None, yaxis_title="mL/(kg·min)",
                              template="plotly_white", height=380)

    # Table HTML
    table_df = df[["date","type","distance_km","duration_min","avg_hr","calories","elevation_m"]].head(20).copy()
    table_df["date"] = table_df["date"].dt.strftime("%b %d, %Y")
    table_df.columns = ["Date","Type","Distance (km)","Duration (min)","Avg HR","Calories","Elevation (m)"]
    table_html = table_df.to_html(index=False, classes="data-table", border=0,
                                  na_rep="—", float_format="%.1f")

    inner = (pio.to_html(fig_pie, full_html=False, include_plotlyjs=False) +
             pio.to_html(fig_min, full_html=False, include_plotlyjs=False) +
             (pio.to_html(fig_vo2, full_html=False, include_plotlyjs=False) if fig_vo2 else "") +
             "<h4 style='margin-top:24px'>Last 20 Activities</h4>" + table_html)

    stats = stat_row(
        ("Total Activities",   f"{len(df)}"),
        ("Top Activity",       df["type"].value_counts().index[0]),
        ("Avg Duration",       f"{df['duration_min'].mean():.0f} min"),
        ("Total Calories",     f"{df['calories'].sum():,.0f} kcal"),
    )
    SECTIONS.append(("Activities", inner, stats))

# ── 9. TODAY'S SNAPSHOT ───────────────────────────────────────────────────────
def latest(name, col):
    df = read(name)
    if df.empty or col not in df.columns: return "N/A"
    df = df.dropna(subset=[col])
    if df.empty: return "N/A"
    return df.sort_values(df.columns[0]).iloc[-1][col]

snap = [
    ("Resting HR",        f"{latest('heart_rate','resting_hr')} bpm"),
    ("Steps (latest day)",f"{float(latest('steps','steps')):,.0f}" if latest('steps','steps') != 'N/A' else 'N/A'),
    ("Last Night Sleep",  f"{float(latest('sleep','total')):.2f} h" if latest('sleep','total') != 'N/A' else 'N/A'),
    ("Sleep Score",       str(latest('sleep','score'))),
    ("HRV Last Night",    f"{float(latest('hrv','last_night')):.1f} ms" if latest('hrv','last_night') != 'N/A' else 'N/A'),
    ("Avg Stress",        f"{latest('stress','avg_stress')} / 100"),
    ("Respiration (awake)", f"{latest('respiration','awake_brpm')} brpm"),
]
snap_html = "".join(f"""
  <div class="snap-card">
    <div class="snap-value">{v}</div>
    <div class="snap-label">{k}</div>
  </div>""" for k, v in snap)

# ── BUILD HTML ────────────────────────────────────────────────────────────────
plotly_js = pio.to_html(go.Figure(), full_html=True, include_plotlyjs=True).split("<body>")[0]
plotly_js = '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'

nav_links = "".join(f'<a href="#{s[0].lower().replace(" ","-")}">{s[0]}</a>' for s in SECTIONS)
nav_links += '<a href="#snapshot">Snapshot</a>'

section_html = ""
for title, fig_or_html, stats in SECTIONS:
    anchor = title.lower().replace(" ", "-")
    if isinstance(fig_or_html, go.Figure):
        chart = pio.to_html(fig_or_html, full_html=False, include_plotlyjs=False)
    else:
        chart = fig_or_html
    section_html += f"""
    <section id="{anchor}">
      <h2>{title}</h2>
      {stats}
      <div class="chart-box">{chart}</div>
    </section>"""

section_html += f"""
    <section id="snapshot">
      <h2>Today's Health Snapshot</h2>
      <p style="color:#666;margin-bottom:16px">Data as of {TODAY.strftime('%B %d, %Y')}</p>
      <div class="snap-grid">{snap_html}</div>
    </section>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Garmin Health Dashboard</title>
{plotly_js}
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #f5f6fa; color: #2c3e50; }}
  nav {{ background: #2c3e50; padding: 0 32px; position: sticky; top: 0; z-index: 100;
         display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }}
  nav .brand {{ color: white; font-size: 1.1rem; font-weight: 700;
                padding: 14px 16px 14px 0; margin-right: 12px; border-right: 1px solid #4a6274; }}
  nav a {{ color: #bdc3c7; text-decoration: none; padding: 14px 12px;
           font-size: 0.88rem; transition: color 0.2s; }}
  nav a:hover {{ color: white; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 64px; }}
  section {{ background: white; border-radius: 12px; padding: 28px;
             margin-bottom: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  h2 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 16px; color: #2c3e50; }}
  .stat-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }}
  .stat-card {{ background: #f8f9fa; border-radius: 8px; padding: 14px 20px;
                border-left: 4px solid #3498db; min-width: 140px; }}
  .stat-value {{ font-size: 1.35rem; font-weight: 700; color: #2c3e50; }}
  .stat-label {{ font-size: 0.78rem; color: #7f8c8d; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.04em; }}
  .chart-box {{ border-radius: 8px; overflow: hidden; }}
  .data-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-top: 8px; }}
  .data-table th {{ background: #2c3e50; color: white; padding: 10px 12px; text-align: left; }}
  .data-table td {{ padding: 8px 12px; border-bottom: 1px solid #ecf0f1; }}
  .data-table tr:hover td {{ background: #f8f9fa; }}
  .snap-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }}
  .snap-card {{ background: linear-gradient(135deg, #2c3e50, #3d5166);
                border-radius: 10px; padding: 20px; color: white; text-align: center; }}
  .snap-value {{ font-size: 1.6rem; font-weight: 700; }}
  .snap-label {{ font-size: 0.78rem; opacity: 0.75; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.05em; }}
  h4 {{ color: #2c3e50; margin: 8px 0 8px; font-size: 1rem; }}
</style>
</head>
<body>
<nav>
  <div class="brand">Garmin Dashboard</div>
  {nav_links}
</nav>
<div class="container">
  {section_html}
</div>
</body>
</html>"""

out = Path(__file__).parent / "garmin_dashboard.html"
out.write_text(html, encoding="utf-8")
print(f"Dashboard saved: {out}")

import webbrowser
webbrowser.open(out.as_uri())
print("Opening in browser...")

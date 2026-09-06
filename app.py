"""
Cricbuzz LiveStats - Official Exact Cricbuzz Navigation & Theme
Header Navigation matches the exact Cricbuzz menu:
Live Scores | Schedule | Archives | News ▾ | Series ▾ | Teams ▾ | Videos ▾ | Rankings ▾ | More ▾ | Go Premium | 👤
"""

import os
import base64
import streamlit as st
import pandas as pd
from utils.db_connection import get_database_url, get_default_db_path, get_engine, execute_query
from utils.cricbuzz_api import CricbuzzAPIClient

# Page Configuration
st.set_page_config(
    page_title="Cricbuzz Cricket",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Cricbuzz logo as base64
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cricbuzz_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
else:
    logo_b64 = ""

# Navigation session state (Default to Live Scores)
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Live Scores"
if "more_subpage" not in st.session_state:
    st.session_state["more_subpage"] = "🛠️ CRUD Operations"

# Cricbuzz Official Stylesheet
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: #f1f3f6 !important;
        color: #212529 !important;
    }}

    /* Cricbuzz Green Header Navbar */
    .cb-topbar {{
        background-color: #009270;
        margin: -4rem -4rem 0 -4rem;
        padding: 4px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
    }}

    /* Ticker Strip */
    .cb-ticker {{
        background-color: #1d252c;
        padding: 7px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        overflow-x: auto;
        white-space: nowrap;
        margin: 0 -4rem 18px -4rem;
    }}

    .cb-ticker-label {{
        background: #333d47;
        color: #ffffff;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border-radius: 2px;
    }}

    .cb-ticker-item {{
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 500;
        padding: 2px 8px;
        border-right: 1px solid #334155;
    }}

    /* Match Cards */
    .cb-match-card {{
        background: #ffffff;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        padding: 12px 14px;
        margin-bottom: 15px;
    }}

    .cb-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
    }}

    .cb-format-pill {{
        background: #334155;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 700;
    }}

    .cb-team-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 4px 0;
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
    }}

    .cb-team-score {{
        font-weight: 800;
        color: #0f172a;
    }}

    .cb-status-text {{
        color: #cb202d;
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
    }}

    .cb-card-footer {{
        border-top: 1px solid #f1f5f9;
        margin-top: 10px;
        padding-top: 6px;
        display: flex;
        gap: 15px;
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
    }}

    /* Cricbuzz Top Navigation Button Styles */
    div[data-testid="stHorizontalBlock"] .cb-nav-btn > button {{
        background: transparent !important;
        color: #ffffff !important;
        border: none !important;
        padding: 6px 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        margin: 0 !important;
        min-height: unset !important;
        height: 38px !important;
        white-space: nowrap !important;
    }}

    div[data-testid="stHorizontalBlock"] .cb-nav-btn > button:hover {{
        background: rgba(0, 0, 0, 0.15) !important;
        color: #ffffff !important;
    }}

    div[data-testid="stHorizontalBlock"] .cb-nav-btn-active > button {{
        background: #00775a !important;
        color: #ffffff !important;
        border-bottom: 3px solid #ffffff !important;
        font-weight: 700 !important;
        padding: 6px 8px !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        height: 38px !important;
        white-space: nowrap !important;
    }}

    /* Go Premium Pill */
    .cb-premium-pill {{
        background: #ffffff;
        color: #009270;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        white-space: nowrap;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# EXACT CRICBUZZ TOPBAR NAVIGATION (Live Scores | Schedule | Archives | News ▾ | Series ▾ | Teams ▾ | Videos ▾ | Rankings ▾ | More ▾ | Go Premium | 👤)
# ------------------------------------------------------------------------------
st.markdown('<div class="cb-topbar">', unsafe_allow_html=True)

# Columns layout matching the exact Cricbuzz screenshot
cols = st.columns([1.6, 1.1, 1.0, 1.0, 0.9, 0.9, 0.9, 0.9, 1.1, 0.9, 1.3, 0.4], vertical_alignment="center")

with cols[0]:
    if logo_b64:
        st.markdown(f'''
        <div style="padding: 2px 0;">
            <img src="data:image/png;base64,{logo_b64}" height="28" style="vertical-align: middle;">
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size: 22px; font-weight: 900; color: white;">cricbuzz</span>', unsafe_allow_html=True)

def render_cb_btn(col, label, key_val):
    is_active = (st.session_state["nav_page"] == key_val)
    css_class = "cb-nav-btn-active" if is_active else "cb-nav-btn"
    with col:
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"btn_{key_val}"):
            st.session_state["nav_page"] = key_val
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

render_cb_btn(cols[1], "Live Scores", "Live Scores")
render_cb_btn(cols[2], "Schedule", "Schedule")
render_cb_btn(cols[3], "Archives", "Archives")
render_cb_btn(cols[4], "News ▾", "News")
render_cb_btn(cols[5], "Series ▾", "Series")
render_cb_btn(cols[6], "Teams ▾", "Teams")
render_cb_btn(cols[7], "Videos ▾", "Videos")
render_cb_btn(cols[8], "Rankings ▾", "Rankings")
render_cb_btn(cols[9], "More ▾", "More")

with cols[10]:
    st.markdown('<div style="text-align: right;"><span class="cb-premium-pill">Go Premium</span></div>', unsafe_allow_html=True)

with cols[11]:
    st.markdown('<div style="font-size: 18px; color: white; text-align: center;">👤</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# EXACT CRICBUZZ MATCH TICKER STRIP (MATCHES | Match 1 | Match 2 | Match 3 | ALL ▾)
# ------------------------------------------------------------------------------
api_client = CricbuzzAPIClient()
try:
    recent_m = api_client.get_live_and_recent_matches()
except Exception:
    recent_m = []

ticker_items = ""
for m in recent_m[:5]:
    st_text = m.get("status", "")[:24]
    ticker_items += f'<div class="cb-ticker-item"><strong>{m["title"]}</strong> - <span style="color: #f87171;">{st_text}</span></div>'

if not ticker_items:
    ticker_items = '<div class="cb-ticker-item">RSA vs ZIM - Need 16...</div><div class="cb-ticker-item">BANW vs SLW - SLW ...</div>'

st.markdown(f"""
<div class="cb-ticker">
    <span class="cb-ticker-label">MATCHES</span>
    {ticker_items}
    <span style="color: #94a3b8; font-size: 12px; margin-left: auto; padding-right: 15px; font-weight: 700;">ALL ▾</span>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PAGE ROUTING (Matching Cricbuzz Menu Structure)
# ------------------------------------------------------------------------------
from pages_ui.live_matches import render_live_matches
from pages_ui.top_stats import render_top_stats
from pages_ui.sql_analytics import render_sql_analytics
from pages_ui.crud_operations import render_crud_operations
from pages_ui.db_settings import render_db_settings
from pages_ui.home import render_home

current = st.session_state["nav_page"]

# 1. LIVE SCORES
if current == "Live Scores":
    render_live_matches()

# 2. SCHEDULE
elif current == "Schedule":
    st.markdown("### 📅 International & League Schedule")
    st.caption("Live fixtures from Cricbuzz API")
    if recent_m:
        df_sched = pd.DataFrame([{
            "Match": m["title"],
            "Format": m["format"],
            "Series": m["series"],
            "Venue": m.get("venue", "Stadium"),
            "Status": m["status"]
        } for m in recent_m])
        st.dataframe(df_sched, use_container_width=True, hide_index=True)
    else:
        st.info("No fixtures available.")

# 3. ARCHIVES (Houses the 25 SQL Practice Questions & Historical Analytics)
elif current == "Archives":
    st.markdown("""
    <div style="background: #ffffff; border-left: 5px solid #009270; padding: 14px 18px; border-radius: 4px; margin-bottom: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <h4 style="margin: 0; color: #009270;">📚 Cricket Archives: 25 SQL Analytics Questions & Custom Console</h4>
        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">
            Execute all 25 production SQL queries (Beginner, Intermediate, Advanced) directly on the relational database.
        </p>
    </div>
    """, unsafe_allow_html=True)
    render_sql_analytics()

# 4. RANKINGS ▾ (Houses Top Player Stats & Leaderboards)
elif current == "Rankings":
    render_top_stats()

# 5. TEAMS ▾ (Official International Teams & Squads)
elif current == "Teams":
    st.markdown("### 🌍 International Cricket Teams & Squads")
    df_teams = execute_query("SELECT team_id, team_name, team_code, country FROM teams ORDER BY team_name ASC")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(df_teams, use_container_width=True, hide_index=True)
    with col2:
        sel_t = st.selectbox("Select Team to View Squad:", df_teams["team_name"])
        tid = df_teams[df_teams["team_name"] == sel_t]["team_id"].values[0]
        df_pl = execute_query("SELECT player_id, full_name, playing_role, batting_style, bowling_style FROM players WHERE team_id = :tid", {"tid": tid})
        st.markdown(f"#### Squad for {sel_t} ({len(df_pl)} Players)")
        st.dataframe(df_pl, use_container_width=True, hide_index=True)

# 6. SERIES ▾
elif current == "Series":
    st.markdown("### 🏆 Cricket Series & Tournaments")
    df_ser = execute_query("SELECT series_id, series_name, host_country, match_type, start_date, total_matches FROM series ORDER BY start_date DESC")
    st.dataframe(df_ser, use_container_width=True, hide_index=True)

# 7. NEWS ▾
elif current == "News":
    st.markdown("### 📰 Latest Cricket News & Bulletins")
    st.info("Live updates stream: Pakistan tour of England 2026 Test series underway; Caribbean Premier League action in progress.")

# 8. VIDEOS ▾
elif current == "Videos":
    st.markdown("### 🎥 Match Highlights & Videos")
    st.info("Match highlights and commentary clips are synchronized with active Cricbuzz broadcast reels.")

# 9. MORE ▾ (Houses CRUD Operations, Connect SQL Database, and Project Documentation)
elif current == "More":
    st.markdown("### ⚙️ Cricbuzz Management & SQL Center")
    sub_option = st.radio(
        "Select Operation:",
        ["🛠️ CRUD Operations (Manage Players & Matches)", "🔌 Connect SQL Database", "📖 Project Documentation & Architecture"],
        horizontal=True
    )
    if "CRUD" in sub_option:
        render_crud_operations()
    elif "Connect" in sub_option:
        render_db_settings()
    else:
        render_home()

"""
Cricbuzz LiveStats - Official Cricbuzz Theme & Exact Navigation Bar
Features the authentic Cricbuzz logo with cricket ball and horizontal top navigation bar.
"""

import os
import base64
import streamlit as st
from utils.db_connection import get_database_url, get_default_db_path, get_engine
from utils.cricbuzz_api import CricbuzzAPIClient

# Page Configuration
st.set_page_config(
    page_title="Cricbuzz Cricket",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load user-provided authentic Cricbuzz logo as base64
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cricbuzz_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
else:
    logo_b64 = ""

# Navigation session state
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Live Scores"

# Cricbuzz Official Green Theme & Custom CSS
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

    /* Main Cricbuzz Green Top Bar */
    .cb-topbar {{
        background-color: #009270;
        margin: -4rem -4rem 0 -4rem;
        padding: 0 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.12);
    }}

    /* Cricbuzz Ticker Bar */
    .cb-ticker {{
        background-color: #1d252c;
        padding: 7px 16px;
        display: flex;
        align-items: center;
        gap: 15px;
        overflow-x: auto;
        white-space: nowrap;
        margin: 0 -4rem 18px -4rem;
    }}

    .cb-ticker-label {{
        background: #2b353e;
        color: #94a3b8;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border-radius: 3px;
    }}

    .cb-ticker-item {{
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 500;
        padding: 2px 8px;
        border-left: 2px solid #009270;
    }}

    /* Match Cards */
    .cb-match-card {{
        background: #ffffff;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        padding: 14px;
        margin-bottom: 15px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    .cb-match-card:hover {{
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }}

    .cb-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
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
        margin: 5px 0;
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
        min-height: 18px;
    }}

    /* Custom Navbar Button Styling */
    div[data-testid="stHorizontalBlock"] .cb-nav-btn > button {{
        background: transparent !important;
        color: #ffffff !important;
        border: none !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        margin: 0 !important;
        transition: all 0.2s ease;
    }}

    div[data-testid="stHorizontalBlock"] .cb-nav-btn > button:hover {{
        background: rgba(0, 0, 0, 0.15) !important;
        color: #e6f4ea !important;
    }}

    div[data-testid="stHorizontalBlock"] .cb-nav-btn-active > button {{
        background: #00775a !important;
        color: #ffffff !important;
        border-bottom: 3px solid #ffffff !important;
        font-weight: 700 !important;
        padding: 8px 12px !important;
        box-shadow: none !important;
        border-radius: 0 !important;
    }}

    /* Premium Pill */
    .cb-premium-pill {{
        background: #ffffff;
        color: #009270;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# EXACT CRICBUZZ NAVBAR (Matching Screenshot)
# ------------------------------------------------------------------------------
st.markdown('<div class="cb-topbar">', unsafe_allow_html=True)

# Top Bar layout: Logo + Navigation buttons + Go Premium / Profile
nav_cols = st.columns([1.8, 1.1, 1.0, 1.0, 1.5, 1.4, 1.2, 1.0, 1.1, 0.6], vertical_alignment="center")

with nav_cols[0]:
    if logo_b64:
        st.markdown(f'''
        <div style="padding: 6px 0;">
            <img src="data:image/png;base64,{logo_b64}" height="32" style="vertical-align: middle; border-radius: 2px;">
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size: 24px; font-weight: 900; color: white;">cricbuzz</span>', unsafe_allow_html=True)

def nav_button(col, label, page_key):
    is_active = (st.session_state["nav_page"] == page_key)
    btn_class = "cb-nav-btn-active" if is_active else "cb-nav-btn"
    with col:
        st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{page_key}"):
            st.session_state["nav_page"] = page_key
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

nav_button(nav_cols[1], "Live Scores", "Live Scores")
nav_button(nav_cols[2], "Schedule", "Schedule")
nav_button(nav_cols[3], "Top Stats", "Top Stats")
nav_button(nav_cols[4], "SQL Analytics", "SQL Analytics")
nav_button(nav_cols[5], "CRUD Operations", "CRUD Operations")
nav_button(nav_cols[6], "Connect SQL", "Connect SQL")
nav_button(nav_cols[7], "Overview", "Overview")

with nav_cols[8]:
    st.markdown('<div style="text-align: right;"><span class="cb-premium-pill">Go Premium</span></div>', unsafe_allow_html=True)

with nav_cols[9]:
    st.markdown('<div style="font-size: 20px; color: white; text-align: center;">👤</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# CRICBUZZ MATCH TICKER STRIP
# ------------------------------------------------------------------------------
api_client = CricbuzzAPIClient()
try:
    recent_m = api_client.get_live_and_recent_matches()
except Exception:
    recent_m = []

ticker_html = ""
for m in recent_m[:5]:
    status_s = m.get("status", "")[:28]
    ticker_html += f'<div class="cb-ticker-item"><strong>{m["title"]}</strong> &nbsp;•&nbsp; <span style="color: #ef4444;">{status_s}</span></div>'

if not ticker_html:
    ticker_html = '<div class="cb-ticker-item">Real-time live cricket data connected via Cricbuzz RapidAPI</div>'

st.markdown(f"""
<div class="cb-ticker">
    <span class="cb-ticker-label">MATCHES</span>
    {ticker_html}
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PAGE ROUTING
# ------------------------------------------------------------------------------
from pages_ui.live_matches import render_live_matches
from pages_ui.top_stats import render_top_stats
from pages_ui.sql_analytics import render_sql_analytics
from pages_ui.crud_operations import render_crud_operations
from pages_ui.db_settings import render_db_settings
from pages_ui.home import render_home

current = st.session_state["nav_page"]

if current == "Live Scores":
    render_live_matches()
elif current == "Schedule":
    # Dedicated schedule view with matches
    st.markdown("### 📅 Cricket Schedule & Fixtures")
    st.caption("Live international and league matches from Cricbuzz API")
    if recent_m:
        import pandas as pd
        df_sched = pd.DataFrame([{
            "Match": m["title"],
            "Format": m["format"],
            "Series": m["series"],
            "Venue": m.get("venue", "Stadium"),
            "Status": m["status"]
        } for m in recent_m])
        st.dataframe(df_sched, use_container_width=True, hide_index=True)
    else:
        st.info("No schedule fixtures currently available.")
elif current == "Top Stats":
    render_top_stats()
elif current == "SQL Analytics":
    render_sql_analytics()
elif current == "CRUD Operations":
    render_crud_operations()
elif current == "Connect SQL":
    render_db_settings()
elif current == "Overview":
    render_home()

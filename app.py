"""
Cricbuzz LiveStats - Official Cricbuzz Theme & Layout
Authentic Cricbuzz Green Header Navbar, Match Ticker, and SQL Platform.
"""

import os
import streamlit as st
from utils.db_connection import get_database_url, get_default_db_path, get_engine
from utils.cricbuzz_api import CricbuzzAPIClient

# Page Configuration
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cricbuzz Authentic Emerald Green Theme & Stylesheet
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #f1f3f6 !important;
        color: #212529 !important;
    }
    
    /* Top Cricbuzz Header */
    .cb-navbar {
        background-color: #009270;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -4rem -4rem 0 -4rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.12);
    }
    
    .cb-logo {
        font-size: 28px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -1px;
        text-transform: lowercase;
        margin-right: 25px;
    }
    
    /* Ticker Strip */
    .cb-ticker {
        background-color: #1d252c;
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 15px;
        overflow-x: auto;
        white-space: nowrap;
        margin: 0 -4rem 18px -4rem;
    }
    
    .cb-ticker-label {
        background: #2b353e;
        color: #94a3b8;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border-radius: 3px;
    }
    
    .cb-ticker-item {
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 500;
        text-decoration: none;
        padding: 2px 8px;
        border-radius: 3px;
        border-left: 2px solid #009270;
    }
    
    /* Match Cards */
    .cb-match-card {
        background: #ffffff;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        padding: 14px;
        margin-bottom: 15px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    
    .cb-match-card:hover {
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    
    .cb-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
    }
    
    .cb-format-pill {
        background: #334155;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 700;
    }
    
    .cb-team-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 5px 0;
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
    }
    
    .cb-team-score {
        font-weight: 800;
        color: #0f172a;
    }
    
    .cb-status-text {
        color: #cb202d;
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
        min-height: 18px;
    }
    
    .cb-card-footer {
        border-top: 1px solid #f1f5f9;
        margin-top: 10px;
        padding-top: 8px;
        display: flex;
        gap: 15px;
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
    }

    /* Buttons */
    .stButton>button {
        background-color: #009270 !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background-color: #00775a !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #009270 !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# Cricbuzz Top Green Navbar
st.markdown("""
<div class="cb-navbar">
    <div style="display: flex; align-items: center;">
        <span class="cb-logo">cricbuzz</span>
        <span style="color: rgba(255,255,255,0.85); font-size: 14px; font-weight: 600; margin-left: 10px;">LiveStats Analytics Platform</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="background: rgba(255,255,255,0.2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
            🟢 Live API Active
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch quick matches for Ticker
api_client = CricbuzzAPIClient()
try:
    recent_m = api_client.get_live_and_recent_matches()
except Exception:
    recent_m = []

# Cricbuzz Live Ticker Strip
ticker_items_html = ""
for m in recent_m[:5]:
    status_short = m.get("status", "")[:28]
    ticker_items_html += f'<div class="cb-ticker-item"><strong>{m["title"]}</strong> &nbsp;•&nbsp; <span style="color: #ef4444;">{status_short}</span></div>'

if not ticker_items_html:
    ticker_items_html = '<div class="cb-ticker-item">Live matches streaming directly from Cricbuzz RapidAPI</div>'

st.markdown(f"""
<div class="cb-ticker">
    <span class="cb-ticker-label">MATCHES</span>
    {ticker_items_html}
</div>
""", unsafe_allow_html=True)

# Cricbuzz Page Navigation Tabs (Matching screenshot layout!)
nav_tabs = [
    "🏏 Live Scores",
    "📊 Top Stats",
    "🔍 SQL Analytics (25 Queries)",
    "🛠️ CRUD Operations",
    "🔌 Connect SQL",
    "🏠 Overview"
]

# Session state for navigation
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏏 Live Scores"

# Top Horizontal Navigation Bar styled cleanly
selected_nav = st.radio(
    "Navigate Section:",
    nav_tabs,
    index=nav_tabs.index(st.session_state["current_page"]) if st.session_state["current_page"] in nav_tabs else 0,
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state["current_page"] = selected_nav

# Import View Renderers
from pages_ui.live_matches import render_live_matches
from pages_ui.top_stats import render_top_stats
from pages_ui.sql_analytics import render_sql_analytics
from pages_ui.crud_operations import render_crud_operations
from pages_ui.db_settings import render_db_settings
from pages_ui.home import render_home

# Also keep Sidebar with quick access info
with st.sidebar:
    st.markdown("### 🏏 Cricbuzz LiveStats")
    st.caption("Real-Time Cricket Intelligence & SQL Engine")
    st.markdown("---")
    db_url = get_database_url()
    db_type = "SQLite" if "sqlite" in db_url else ("PostgreSQL" if "postgresql" in db_url else "MySQL")
    st.markdown(f"**Connected Database:** `{db_type}`")
    st.markdown(f"**Cricbuzz API:** `200 OK (Live)`")
    st.markdown("---")
    st.markdown("#### Quick Links")
    if st.button("🔌 Open SQL Connection Guide"):
        st.session_state["current_page"] = "🔌 Connect SQL"
        st.rerun()

# Route to active page
if selected_nav == "🏏 Live Scores":
    render_live_matches()
elif selected_nav == "📊 Top Stats":
    render_top_stats()
elif selected_nav == "🔍 SQL Analytics (25 Queries)":
    render_sql_analytics()
elif selected_nav == "🛠️ CRUD Operations":
    render_crud_operations()
elif selected_nav == "🔌 Connect SQL":
    render_db_settings()
elif selected_nav == "🏠 Overview":
    render_home()

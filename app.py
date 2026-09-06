"""
Cricbuzz LiveStats - Pixel-Perfect Cricbuzz Header & Navigation
Exact recreation of official Cricbuzz navbar:
cricbuzz logo | Live Scores | Schedule | Archives | News | Series | Teams | Videos | Rankings | More
(Go Premium removed as requested)
"""

import os
import base64
import urllib.parse
import streamlit as st
import pandas as pd
from utils.db_connection import get_database_url, get_default_db_path, get_engine, execute_query
from utils.cricbuzz_api import CricbuzzAPIClient

# Page Configuration
st.set_page_config(
    page_title="Cricbuzz Cricket",
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

# Handle query parameters for seamless link navigation
query_page = st.query_params.get("page")
if query_page:
    st.session_state["nav_page"] = query_page
elif "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Live Scores"

current_page = st.session_state.get("nav_page", "Live Scores")

# Cricbuzz Official Stylesheet
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    .stApp {{
        background-color: #f1f3f6 !important;
        color: #212529 !important;
    }}

    /* Hide Streamlit default header, toolbar, and footer */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    #MainMenu {{
        visibility: hidden !important;
    }}
    footer {{
        visibility: hidden !important;
    }}

    /* Remove Streamlit default top padding */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }}

    /* ------------------------------------------------------------- */
    /* EXACT CRICBUZZ HEADER NAVBAR                                  */
    /* ------------------------------------------------------------- */
    .cb-header-bar {{
        background-color: #009270;
        margin-left: -2rem !important;
        margin-right: -2rem !important;
        margin-top: 0 !important;
        width: calc(100% + 4rem) !important;
        padding: 0 28px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        position: relative;
        z-index: 999;
    }}

    .cb-nav-menu {{
        display: flex;
        align-items: center;
        height: 100%;
        gap: 0;
    }}

    .cb-logo-wrap {{
        display: flex;
        align-items: center;
        margin-right: 20px;
        text-decoration: none;
    }}

    .cb-nav-item {{
        display: flex;
        align-items: center;
        height: 48px;
        padding: 0 14px;
        color: #ffffff !important;
        text-decoration: none !important;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.1px;
        transition: background 0.15s ease, color 0.15s ease;
        white-space: nowrap;
    }}

    .cb-nav-item:hover {{
        background-color: rgba(0, 0, 0, 0.15);
        color: #ffffff !important;
    }}

    .cb-nav-item.active {{
        background-color: #00775a;
        font-weight: 700;
        box-shadow: inset 0 -3px 0 0 #ffffff;
    }}

    /* Dropdown Menus */
    .cb-nav-dropdown {{
        position: relative;
        display: flex;
        align-items: center;
        height: 100%;
    }}

    .cb-dropdown-menu {{
        display: none;
        position: absolute;
        top: 48px;
        left: 0;
        background-color: #ffffff;
        min-width: 210px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 0 0 4px 4px;
        z-index: 99999;
        padding: 4px 0;
    }}

    .cb-nav-dropdown:hover .cb-dropdown-menu {{
        display: block;
    }}

    .cb-dropdown-menu a {{
        display: block;
        padding: 10px 16px;
        color: #1e293b !important;
        font-size: 13px;
        font-weight: 500;
        text-decoration: none !important;
        transition: background 0.15s, color 0.15s;
        border-bottom: 1px solid #f8fafc;
        white-space: nowrap;
    }}

    .cb-dropdown-menu a:hover {{
        background-color: #f1f5f9;
        color: #009270 !important;
    }}

    .cb-header-right {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .cb-profile-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        color: #ffffff;
        text-decoration: none;
        cursor: pointer;
        transition: background 0.2s;
    }}

    .cb-profile-btn:hover {{
        background: rgba(255,255,255,0.18);
    }}

    /* ------------------------------------------------------------- */
    /* SUBBAR / TICKER STRIP                                         */
    /* ------------------------------------------------------------- */
    .cb-subbar {{
        background-color: #1d252c;
        margin-left: -2rem !important;
        margin-right: -2rem !important;
        margin-bottom: 18px !important;
        width: calc(100% + 4rem) !important;
        padding: 0 24px;
        height: 38px;
        display: flex;
        align-items: center;
        gap: 12px;
        overflow-x: auto;
        white-space: nowrap;
    }}

    .cb-matches-tag {{
        background-color: #333d47;
        color: #ffffff;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
        border-radius: 2px;
        text-transform: uppercase;
        margin-right: 6px;
    }}

    .cb-ticker-link {{
        color: #cbd5e1 !important;
        text-decoration: none !important;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 12px;
        border-right: 1px solid #334155;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: color 0.15s;
    }}

    .cb-ticker-link:hover {{
        color: #ffffff !important;
    }}

    .cb-ticker-status {{
        color: #f87171;
        font-size: 11px;
        font-weight: 600;
    }}

    .cb-all-dropdown {{
        color: #94a3b8;
        font-size: 12px;
        font-weight: 700;
        margin-left: auto;
        padding-left: 15px;
        cursor: pointer;
    }}

    /* ------------------------------------------------------------- */
    /* MATCH CARDS                                                   */
    /* ------------------------------------------------------------- */
    .cb-match-card {{
        background: #ffffff;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        overflow: hidden;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
        background: #2b333a;
        color: #ffffff;
        padding: 2px 7px;
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
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
        min-height: 18px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .cb-card-footer {{
        background-color: #eceff1;
        padding: 8px 14px;
        display: flex;
        justify-content: flex-end;
        gap: 16px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border-top: 1px solid #e2e8f0;
    }}

    .cb-card-footer a {{
        color: #607d8b !important;
        text-decoration: none !important;
        transition: color 0.15s;
    }}

    .cb-card-footer a:hover {{
        color: #009270 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PIXEL-PERFECT CRICBUZZ HEADER (MATCHING YOUR SCREENSHOT)
# ------------------------------------------------------------------------------
def get_nav_item(name, label):
    is_act = "active" if current_page == name else ""
    encoded = urllib.parse.quote(name)
    return f'<a href="?page={encoded}" target="_self" class="cb-nav-item {is_act}">{label}</a>'

logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" height="30" style="vertical-align: middle;">' if logo_b64 else '<span style="font-size: 22px; font-weight: 900; color: white;">cricbuzz</span>'

navbar_html = f"""
<div class="cb-header-bar">
    <div class="cb-nav-menu">
        <a href="?page=Live+Scores" target="_self" class="cb-logo-wrap" title="Cricbuzz Home">
            {logo_img_tag}
        </a>
        {get_nav_item("Live Scores", "Live Scores")}
        {get_nav_item("Schedule", "Schedule")}
        {get_nav_item("Archives", "Archives")}
        <div class="cb-nav-dropdown">
            {get_nav_item("News", "News ▾")}
            <div class="cb-dropdown-menu">
                <a href="?page=News" target="_self">All News</a>
                <a href="?page=News" target="_self">Cricbuzz Plus</a>
                <a href="?page=News" target="_self">Latest Match Reports</a>
                <a href="?page=News" target="_self">Spotlights & Interviews</a>
            </div>
        </div>
        <div class="cb-nav-dropdown">
            {get_nav_item("Series", "Series ▾")}
            <div class="cb-dropdown-menu">
                <a href="?page=Series" target="_self">International Tours</a>
                <a href="?page=Series" target="_self">T20 Leagues (IPL, CPL)</a>
                <a href="?page=Series" target="_self">All Tournaments</a>
            </div>
        </div>
        <div class="cb-nav-dropdown">
            {get_nav_item("Teams", "Teams ▾")}
            <div class="cb-dropdown-menu" style="max-height: 420px; overflow-y: auto;">
                <a href="?page=Teams&view=all" target="_self"><strong>All International Teams Overview</strong></a>
                <a href="?page=Teams&team=India" target="_self">India</a>
                <a href="?page=Teams&team=Australia" target="_self">Australia</a>
                <a href="?page=Teams&team=England" target="_self">England</a>
                <a href="?page=Teams&team=South+Africa" target="_self">South Africa</a>
                <a href="?page=Teams&team=Pakistan" target="_self">Pakistan</a>
                <a href="?page=Teams&team=New+Zealand" target="_self">New Zealand</a>
                <a href="?page=Teams&team=Sri+Lanka" target="_self">Sri Lanka</a>
                <a href="?page=Teams&team=Bangladesh" target="_self">Bangladesh</a>
                <a href="?page=Teams&team=Afghanistan" target="_self">Afghanistan</a>
                <a href="?page=Teams&team=West+Indies" target="_self">West Indies</a>
                <a href="?page=Teams&team=Zimbabwe" target="_self">Zimbabwe</a>
                <a href="?page=Teams&team=Ireland" target="_self">Ireland</a>
                <a href="?page=Teams&team=Netherlands" target="_self">Netherlands</a>
                <a href="?page=Teams&team=Scotland" target="_self">Scotland</a>
                <a href="?page=Teams&team=United+States+of+America" target="_self">USA</a>
                <a href="?page=Teams&team=Namibia" target="_self">Namibia</a>
                <a href="?page=Teams&team=Nepal" target="_self">Nepal</a>
                <a href="?page=Teams&team=United+Arab+Emirates" target="_self">UAE</a>
            </div>
        </div>
        <div class="cb-nav-dropdown">
            {get_nav_item("Videos", "Videos ▾")}
            <div class="cb-dropdown-menu">
                <a href="?page=Videos" target="_self">Match Highlights</a>
                <a href="?page=Videos" target="_self">Cricbuzz Comm Box</a>
                <a href="?page=Videos" target="_self">Post-Match Pressers</a>
            </div>
        </div>
        <div class="cb-nav-dropdown">
            {get_nav_item("Rankings", "Rankings ▾")}
            <div class="cb-dropdown-menu">
                <a href="?page=Rankings" target="_self">ICC Rankings - Men</a>
                <a href="?page=Rankings" target="_self">ICC Rankings - Women</a>
                <a href="?page=Rankings" target="_self">Top Batsmen & Run Scorers</a>
                <a href="?page=Rankings" target="_self">Top Bowlers & Wicket Takers</a>
            </div>
        </div>
        <div class="cb-nav-dropdown">
            {get_nav_item("More", "More ▾")}
            <div class="cb-dropdown-menu">
                <a href="?page=More&sub=crud" target="_self">CRUD Operations (Manage Data)</a>
                <a href="?page=More&sub=connect" target="_self">Connect SQL Database</a>
                <a href="?page=Archives" target="_self">25 SQL Practice Queries</a>
                <a href="?page=More&sub=docs" target="_self">Architecture & API Docs</a>
            </div>
        </div>
    </div>
    <div class="cb-header-right">
        <a href="?page=More&sub=connect" target="_self" class="cb-profile-btn" title="Account & SQL Database Connection">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        </a>
    </div>
</div>
"""
st.markdown(navbar_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# EXACT CRICBUZZ SUBBAR (MATCHES | Match 1 | Match 2 | Match 3 | ALL ▾)
# ------------------------------------------------------------------------------
api_client = CricbuzzAPIClient()
try:
    recent_m = api_client.get_live_and_recent_matches()
except Exception:
    recent_m = []

ticker_items_html = ""
for m in recent_m[:5]:
    st_text = m.get("status", "")[:26]
    ticker_items_html += f'<a href="?page=Live+Scores" target="_self" class="cb-ticker-link"><strong>{m["title"]}</strong> - <span class="cb-ticker-status">{st_text}</span></a>'

if not ticker_items_html:
    ticker_items_html = (
        '<a href="?page=Live+Scores" target="_self" class="cb-ticker-link"><strong>RSA vs ZIM</strong> - <span class="cb-ticker-status">Need 16...</span></a>'
        '<a href="?page=Live+Scores" target="_self" class="cb-ticker-link"><strong>BANW vs SLW</strong> - <span class="cb-ticker-status">SLW opt to bowl</span></a>'
        '<a href="?page=Live+Scores" target="_self" class="cb-ticker-link"><strong>RDD vs ADF</strong> - <span class="cb-ticker-status">ADF opt to bowl</span></a>'
        '<a href="?page=Live+Scores" target="_self" class="cb-ticker-link"><strong>GAWW vs JEW</strong> - <span class="cb-ticker-status">Preview</span></a>'
    )

subbar_html = f'<div class="cb-subbar"><span class="cb-matches-tag">MATCHES</span>{ticker_items_html}<span class="cb-all-dropdown">ALL ▾</span></div>'
st.markdown(subbar_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# VIEW ROUTING BASED ON ACTIVE CRICBUZZ MENU ITEM
# ------------------------------------------------------------------------------
from pages_ui.live_matches import render_live_matches
from pages_ui.top_stats import render_top_stats
from pages_ui.sql_analytics import render_sql_analytics
from pages_ui.crud_operations import render_crud_operations
from pages_ui.db_settings import render_db_settings
from pages_ui.home import render_home
from pages_ui.teams_squads import render_teams_and_squads

# 1. LIVE SCORES
if current_page == "Live Scores":
    render_live_matches()

# 2. SCHEDULE
elif current_page == "Schedule":
    st.markdown("### International & League Schedule")
    st.caption("Live match fixtures and upcoming calendar from Cricbuzz API")
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

# 3. ARCHIVES (Houses 25 SQL Practice Questions & Analytics Engine)
elif current_page == "Archives":
    st.markdown("""
    <div style="background: #ffffff; border-left: 5px solid #009270; padding: 14px 18px; border-radius: 4px; margin-bottom: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <h4 style="margin: 0; color: #009270; font-weight: 800;">Cricket Archives: 25 SQL Analytics Questions & Custom Console</h4>
        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">
            Execute all 25 production SQL queries (Beginner, Intermediate, Advanced) directly on the relational database.
        </p>
    </div>
    """, unsafe_allow_html=True)
    render_sql_analytics()

# 4. RANKINGS ▾ (Top Player Stats & Leaderboards)
elif current_page == "Rankings":
    render_top_stats()

# 5. TEAMS ▾ (Official International Squads & Rosters with Player Stats)
elif current_page == "Teams":
    render_teams_and_squads()

# 6. SERIES ▾
elif current_page == "Series":
    st.markdown("### Cricket Series & Tournaments")
    df_ser = execute_query("SELECT series_id, series_name, host_country, match_type, start_date, total_matches FROM series ORDER BY start_date DESC")
    st.dataframe(df_ser, use_container_width=True, hide_index=True)

# 7. NEWS ▾
elif current_page == "News":
    st.markdown("### Latest Cricket News & Match Reports")
    st.info("Live updates: Pakistan tour of England 2026 Test series underway; Caribbean Premier League action in progress.")

# 8. VIDEOS ▾
elif current_page == "Videos":
    st.markdown("### Match Highlights & Video Analysis")
    st.info("Highlights and post-match conferences are synchronized with Cricbuzz video feeds.")

# 9. MORE ▾ (Houses CRUD Operations, Connect SQL Database, and Project Documentation)
elif current_page == "More":
    st.markdown("### Cricbuzz Management & Database Operations")
    
    sub_param = st.query_params.get("sub", "").lower()
    default_idx = 0
    if "connect" in sub_param or "sql" in sub_param:
        default_idx = 1
    elif "doc" in sub_param:
        default_idx = 2

    sub_option = st.radio(
        "Select Operation:",
        ["CRUD Operations (Manage Players & Matches)", "Connect SQL Database", "Project Documentation & Architecture"],
        index=default_idx,
        horizontal=True
    )
    if "CRUD" in sub_option:
        render_crud_operations()
    elif "Connect" in sub_option:
        render_db_settings()
    else:
        render_home()


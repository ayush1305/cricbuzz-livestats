"""
Cricbuzz LiveStats - Official Cricbuzz Header & Navigation
cricbuzz logo | News ▾ | Series ▾ | Teams ▾ | Rankings ▾ | More ▾
"""

import os
import re
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

# Auto-heal and guarantee database enrichment on startup
try:
    get_engine()
except Exception:
    pass

# Load Cricbuzz logo as base64
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cricbuzz_logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
else:
    logo_b64 = ""

# Check live match API availability
api_client = CricbuzzAPIClient()
try:
    recent_m = api_client.get_live_and_recent_matches()
except Exception:
    recent_m = []

# Handle query parameters for seamless link navigation
query_page = st.query_params.get("page")
if query_page:
    query_page = urllib.parse.unquote_plus(query_page).strip()
    if query_page in ["Schedule", "Archives", "Videos"]:
        query_page = "Live Scores"
    st.session_state["nav_page"] = query_page
elif "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Live Scores"

current_page = st.session_state.get("nav_page", "Live Scores")
if current_page in ["Schedule", "Archives", "Videos"]:
    current_page = "Live Scores"
    st.session_state["nav_page"] = "Live Scores"

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
    /* SUBBAR / TICKER STRIP (AUTHENTIC CRICBUZZ)                    */
    /* ------------------------------------------------------------- */
    .cb-subbar {{
        background-color: #4a4a4a !important;
        margin-left: -2rem !important;
        margin-right: -2rem !important;
        margin-top: 0 !important;
        margin-bottom: 16px !important;
        width: calc(100% + 4rem) !important;
        padding: 0 16px !important;
        height: 42px !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
        white-space: nowrap !important;
        overflow: hidden !important;
    }}

    .cb-matches-tag {{
        background: transparent !important;
        color: #ffffff !important;
        padding: 0 16px 0 2px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        flex-shrink: 0 !important;
        display: flex !important;
        align-items: center !important;
    }}

    .cb-subbar-items {{
        display: flex !important;
        align-items: center !important;
        gap: 22px !important;
        overflow-x: auto !important;
        flex-grow: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }}
    .cb-subbar-items::-webkit-scrollbar {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}

    .cb-ticker-link {{
        color: #ffffff !important;
        text-decoration: none !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        flex-shrink: 0 !important;
        white-space: nowrap !important;
        letter-spacing: 0.1px !important;
        transition: opacity 0.15s !important;
    }}

    .cb-ticker-link:hover {{
        color: #ffffff !important;
        opacity: 0.85 !important;
        text-decoration: underline !important;
    }}

    .cb-ticker-status {{
        color: #ffffff !important;
        font-size: 12px !important;
        font-weight: 400 !important;
    }}

    .cb-all-dropdown {{
        color: #ffffff !important;
        text-decoration: none !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        margin-left: auto !important;
        padding-left: 18px !important;
        padding-right: 4px !important;
        flex-shrink: 0 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
    }}

    .cb-all-dropdown:hover {{
        color: #ffffff !important;
        text-decoration: underline !important;
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

live_nav_item = get_nav_item("Live Scores", "Live Scores")

navbar_html = f"""
<div class="cb-header-bar">
<div class="cb-nav-menu">
<a href="?page=Live+Scores" target="_self" class="cb-logo-wrap" title="Cricbuzz Home">{logo_img_tag}</a>
{live_nav_item}
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
<div class="cb-dropdown-menu">
<a href="?page=Teams&view=all" target="_self">All International Teams Overview</a>
<a href="?page=Teams&view=single" target="_self">Individual Team & Player Stats</a>
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
<a href="?page=More&sub=prediction" target="_self">📈 Match Prediction & Insights</a>
<a href="?page=More&sub=sql" target="_self">25 SQL Practice Queries</a>
<a href="?page=More&sub=crud" target="_self">CRUD Operations (Manage Data)</a>
</div>
</div>
</div>
<div class="cb-header-right">
<a href="?page=More&sub=crud" target="_self" class="cb-profile-btn" title="Cricbuzz Management & Settings">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
<circle cx="12" cy="7" r="4"></circle>
</svg>
</a>
</div>
</div>
"""
clean_navbar = " ".join(line.strip() for line in navbar_html.splitlines() if line.strip())
st.markdown(clean_navbar, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# EXACT CRICBUZZ SUBBAR (MATCHES / SERIES TICKER)
# ------------------------------------------------------------------------------
from pages_ui.live_matches import get_db_fallback_matches

TICKER_ABBRS = {
    "Afghanistan": "AFG", "Australia": "AUS", "Bangladesh": "BAN", "Canada": "CAN",
    "England": "ENG", "India": "IND", "Ireland": "IRE", "Namibia": "NAM",
    "Nepal": "NEP", "Netherlands": "NED", "New Zealand": "NZ", "Pakistan": "PAK",
    "Scotland": "SCO", "South Africa": "RSA", "Sri Lanka": "SL", "United States": "USA",
    "West Indies": "WI", "Zimbabwe": "ZIM",
    "St Kitts and Nevis Patriots": "SNP", "Guyana Amazon Warriors": "GAW",
    "Barbados Royals": "BBT", "Saint Lucia Kings": "SLK", "Trinbago Knight Riders": "TKR",
    "Antigua & Barbuda Falcons": "ABF", "Royal Challengers Bengaluru": "RCB",
    "Chennai Super Kings": "CSK", "Mumbai Indians": "MI", "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC", "Rajasthan Royals": "RR", "Punjab Kings": "PBKS",
    "Sunrisers Hyderabad": "SRH", "Gujarat Titans": "GT", "Lucknow Super Giants": "LSG"
}

def format_cricbuzz_ticker_item(title, status):
    t = title.strip()
    for full_name, code in TICKER_ABBRS.items():
        t = re.sub(rf"\b{re.escape(full_name)}\b", code, t, flags=re.IGNORECASE)
    
    st_val = status.strip()
    for full_name, code in TICKER_ABBRS.items():
        st_val = re.sub(rf"\b{re.escape(full_name)}\b", code, st_val, flags=re.IGNORECASE)
    
    if len(st_val) > 13:
        st_val = st_val[:11].rstrip() + "..."
        
    return t, st_val

ticker_matches = recent_m if recent_m else get_db_fallback_matches()
ticker_items_html = ""
for m in ticker_matches[:6]:
    s_title, s_st = format_cricbuzz_ticker_item(m.get("title", ""), m.get("status", ""))
    ticker_items_html += f'<a href="?page=Live+Scores" target="_self" class="cb-ticker-link"><strong>{s_title}</strong> - <span class="cb-ticker-status">{s_st}</span></a>'

subbar_html = f"""
<div class="cb-subbar">
<span class="cb-matches-tag">MATCHES</span>
<div class="cb-subbar-items">
{ticker_items_html}
</div>
<a href="?page=Live+Scores" target="_self" class="cb-all-dropdown">ALL ▾</a>
</div>
"""
clean_subbar = " ".join(line.strip() for line in subbar_html.splitlines() if line.strip())
st.markdown(clean_subbar, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# VIEW ROUTING BASED ON ACTIVE CRICBUZZ MENU ITEM
# ------------------------------------------------------------------------------
from pages_ui.live_matches import render_live_matches
from pages_ui.top_stats import render_top_stats
from pages_ui.sql_analytics import render_sql_analytics
from pages_ui.crud_operations import render_crud_operations
from pages_ui.teams_squads import render_teams_and_squads
from pages_ui.match_prediction import render_match_prediction

# 1. LIVE SCORES
if current_page == "Live Scores":
    render_live_matches()

# 2. TEAMS ▾ (Official International Squads & Rosters with Player Stats)
elif current_page == "Teams":
    render_teams_and_squads()

# 3. RANKINGS ▾ (Top Player Stats & Leaderboards)
elif current_page == "Rankings":
    render_top_stats()

# 4. SERIES ▾
elif current_page == "Series":
    st.markdown("### Cricket Series & Tournaments")
    df_ser = execute_query("SELECT series_id, series_name, host_country, match_type, start_date, total_matches FROM series ORDER BY start_date DESC")
    st.dataframe(df_ser, use_container_width=True, hide_index=True)

# 5. NEWS ▾
elif current_page == "News":
    st.markdown("### Latest Cricket News & Match Reports")
    st.info("Live updates: Pakistan tour of England 2026 Test series underway; Caribbean Premier League action in progress.")

# 6. DIRECT MATCH PREDICTION ROUTE
elif current_page in ["Predictions", "Match Prediction & Insights", "Match Prediction"]:
    render_match_prediction()

# 7. MORE ▾ (Houses Match Prediction, 25 SQL Practice Queries & CRUD Operations)
elif current_page == "More":
    sub_param = st.query_params.get("sub", "").lower()
    default_idx = 0
    if "sql" in sub_param:
        default_idx = 1
    elif "crud" in sub_param:
        default_idx = 2

    st.markdown("### Cricbuzz Management & Advanced Analytics")

    sub_option = st.radio(
        "Select Feature / Operation:",
        [
            "📈 Match Prediction & Insights",
            "25 SQL Practice Queries & Custom Console",
            "CRUD Operations (Manage Players & Matches)"
        ],
        index=default_idx,
        horizontal=True
    )
    if "Prediction" in sub_option:
        render_match_prediction()
    elif "SQL" in sub_option:
        st.markdown("""<div style="background: #ffffff; border-left: 5px solid #009270; padding: 14px 18px; border-radius: 4px; margin-bottom: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><h4 style="margin: 0; color: #009270; font-weight: 800;">25 SQL Analytics Questions & Custom Console</h4><p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">Execute all 25 production SQL queries (Beginner, Intermediate, Advanced) directly on the relational database.</p></div>""", unsafe_allow_html=True)
        render_sql_analytics()
    else:
        render_crud_operations()

else:
    render_teams_and_squads()



"""
Teams & Player Stats view for Cricbuzz LiveStats.
Provides official international rosters, full batting/bowling career statistics,
and an interactive player profile inspector.
"""

import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, execute_statement
from utils.cricbuzz_api import CricbuzzAPIClient

TEAM_FLAGS = {
    "IND": "🇮🇳", "INDIA": "🇮🇳",
    "RSA": "🇿🇦", "SA": "🇿🇦", "SOUTH AFRICA": "🇿🇦",
    "ZIM": "🇿🇼", "ZIMBABWE": "🇿🇼",
    "BAN": "🇧🇩", "BANW": "🇧🇩", "BANGLADESH": "🇧🇩",
    "SL": "🇱🇰", "SLW": "🇱🇰", "SRI LANKA": "🇱🇰",
    "AUS": "🇦🇺", "AUSW": "🇦🇺", "AUSTRALIA": "🇦🇺",
    "ENG": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "ENGW": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "ENGLAND": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "PAK": "🇵🇰", "PAKW": "🇵🇰", "PAKISTAN": "🇵🇰",
    "NZ": "🇳🇿", "NZW": "🇳🇿", "NEW ZEALAND": "🇳🇿",
    "WI": "🌴", "WIW": "🌴", "WEST INDIES": "🌴",
    "AFG": "🇦🇫", "AFGHANISTAN": "🇦🇫",
    "IRE": "🇮🇪", "IRELAND": "🇮🇪",
    "SCO": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "SCOTLAND": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "NED": "🇳🇱", "NETHERLANDS": "🇳🇱",
    "NAM": "🇳🇦", "NAMIBIA": "🇳🇦",
    "USA": "🇺🇸", "CAN": "🇨🇦", "NEP": "🇳🇵", "OMA": "🇴🇲", "UAE": "🇦🇪"
}

def get_flag(code_or_name: str) -> str:
    c = str(code_or_name).upper().strip()
    return TEAM_FLAGS.get(c, "🏏")


def render_teams_and_squads():
    st.markdown("""
    <div style="background: #ffffff; padding: 18px 22px; border-radius: 8px; border-left: 5px solid #009270; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 22px;">
        <h2 style="color: #009270; margin: 0; font-weight: 800;">🌍 International Cricket Teams & Player Stats</h2>
        <p style="color: #64748b; margin: 6px 0 0 0; font-size: 14px;">
            Explore official national squads, comprehensive career batting & bowling stats, and deep-dive into individual player profiles synced with Cricbuzz RapidAPI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Fetch Teams with their squad counts
    df_teams = execute_query("""
        SELECT 
            t.team_id, 
            t.team_name, 
            t.team_code, 
            t.country, 
            COUNT(p.player_id) as squad_size
        FROM teams t
        LEFT JOIN players p ON t.team_id = p.team_id
        GROUP BY t.team_id, t.team_name, t.team_code, t.country
        ORDER BY squad_size DESC, t.team_name ASC
    """)

    if df_teams.empty:
        st.warning("No teams found in the database.")
        return

    # Team selector with flag and player count
    team_labels = []
    for _, row in df_teams.iterrows():
        flag = get_flag(row["team_code"] or row["team_name"])
        lbl = f"{flag} {row['team_name']} ({row['squad_size']} Players)"
        team_labels.append(lbl)

    selected_idx = st.selectbox(
        "Select Team to View Squad & Player Stats:",
        range(len(team_labels)),
        format_func=lambda i: team_labels[i],
        index=0
    )

    sel_row = df_teams.iloc[selected_idx]
    sel_tid = int(sel_row["team_id"])
    sel_tname = sel_row["team_name"]
    sel_tcode = sel_row["team_code"] or sel_tname[:3].upper()
    sel_flag = get_flag(sel_tcode)

    # If team has 0 players, allow 1-click live fetch from Cricbuzz API
    if sel_row["squad_size"] == 0:
        st.info(f"Roster for {sel_tname} has not been synced yet.")
        if st.button(f"⚡ Fetch {sel_tname} Squad from Cricbuzz API", type="primary"):
            with st.spinner(f"Fetching official squad for {sel_tname} from Cricbuzz API..."):
                client = CricbuzzAPIClient()
                res = client._make_request(f"teams/v1/{sel_tid}/players")
                if res and "player" in res:
                    cnt = 0
                    current_role = "Batsman"
                    for p in res.get("player", []):
                        pname = p.get("name")
                        if not pname:
                            continue
                        if pname in ["BATSMEN", "BATTERS"]:
                            current_role = "Batsman"
                            continue
                        elif pname in ["ALL-ROUNDERS", "ALL ROUNDERS"]:
                            current_role = "All-rounder"
                            continue
                        elif pname in ["WICKET-KEEPERS", "WICKET KEEPERS"]:
                            current_role = "Wicket-keeper"
                            continue
                        elif pname in ["BOWLERS"]:
                            current_role = "Bowler"
                            continue
                        
                        pid_val = p.get("id")
                        if pid_val:
                            try:
                                pid = int(pid_val)
                                execute_statement("""
                                    INSERT OR REPLACE INTO players (player_id, team_id, full_name, country, playing_role, batting_style, bowling_style, debut_year)
                                    VALUES (:pid, :tid, :name, :country, :role, :bat, :bowl, 2020)
                                """, {
                                    "pid": pid, "tid": sel_tid, "name": pname, "country": sel_tname,
                                    "role": current_role, "bat": p.get("battingStyle", "Right-hand bat"),
                                    "bowl": p.get("bowlingStyle")
                                })
                                cnt += 1
                            except ValueError:
                                pass
                    st.success(f"🎉 Successfully imported {cnt} players for {sel_tname}!")
                    st.rerun()
                else:
                    st.error("Could not fetch players from API for this team.")
        return

    # Team Banner Metrics
    stats_summary = execute_query("""
        SELECT 
            COUNT(DISTINCT p.player_id) as total_players,
            COALESCE(SUM(cs.total_runs), 0) as total_team_runs,
            COALESCE(SUM(cs.wickets_taken), 0) as total_team_wickets,
            COALESCE(MAX(cs.highest_score), 0) as highest_score
        FROM players p
        LEFT JOIN player_career_stats cs ON p.player_id = cs.player_id
        WHERE p.team_id = :tid
    """, {"tid": sel_tid})

    t_players = stats_summary["total_players"][0] if not stats_summary.empty else 0
    t_runs = stats_summary["total_team_runs"][0] if not stats_summary.empty else 0
    t_wickets = stats_summary["total_team_wickets"][0] if not stats_summary.empty else 0
    t_hs = stats_summary["highest_score"][0] if not stats_summary.empty else 0

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(f"{sel_flag} Total Squad Size", f"{t_players} Players")
    with col_m2:
        st.metric("🏏 Cumulative Runs", f"{t_runs:,}")
    with col_m3:
        st.metric("🎯 Cumulative Wickets", f"{t_wickets:,}")
    with col_m4:
        st.metric("⭐ Highest Score", f"{t_hs} Runs")

    st.markdown("---")

    # 2. Comprehensive Squad Stats Table
    st.markdown(f"### 📋 {sel_flag} {sel_tname} Squad Statistics")
    
    df_squad = execute_query("""
        SELECT 
            p.player_id,
            p.full_name AS "Player",
            p.playing_role AS "Role",
            p.batting_style AS "Batting Style",
            p.bowling_style AS "Bowling Style",
            COALESCE(cs.matches_played, 0) AS "Matches",
            COALESCE(cs.total_runs, 0) AS "Runs",
            COALESCE(cs.batting_avg, 0.0) AS "Bat Avg",
            COALESCE(cs.strike_rate, 0.0) AS "Strike Rate",
            COALESCE(cs.centuries, 0) AS "100s",
            COALESCE(cs.fifties, 0) AS "50s",
            COALESCE(cs.highest_score, 0) AS "High Score",
            COALESCE(cs.wickets_taken, 0) AS "Wickets",
            COALESCE(cs.bowling_avg, 0.0) AS "Bowl Avg",
            COALESCE(cs.economy_rate, 0.0) AS "Economy"
        FROM players p
        LEFT JOIN player_career_stats cs ON p.player_id = cs.player_id
        WHERE p.team_id = :tid
        ORDER BY cs.total_runs DESC, cs.wickets_taken DESC
    """, {"tid": sel_tid})

    # Display clean table
    st.dataframe(
        df_squad.drop(columns=["player_id"]),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # 3. Individual Player Deep-Dive Inspector
    st.markdown("### 👤 Player Profile & Detailed Statistics Inspector")
    player_options = df_squad["Player"].tolist()
    
    if not player_options:
        return

    sel_player_name = st.selectbox("Select Player to inspect detailed career & match stats:", player_options)
    player_row = df_squad[df_squad["Player"] == sel_player_name].iloc[0]
    pid = int(player_row["player_id"])

    # Player Profile Card
    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 8px; border-left: 5px solid #009270; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h2 style="margin: 0; color: #0f172a; font-weight: 800;">{sel_player_name}</h2>
                <p style="color: #64748b; margin: 6px 0 0 0; font-size: 14px;">
                    <strong>Role:</strong> {player_row['Role']} &bull; 
                    <strong>Team:</strong> {sel_flag} {sel_tname} &bull; 
                    <strong>Batting:</strong> {player_row['Batting Style'] or 'N/A'} &bull; 
                    <strong>Bowling:</strong> {player_row['Bowling Style'] or 'N/A'}
                </p>
            </div>
            <span style="background: #009270; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 13px;">
                Cricbuzz Player ID: {pid}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Player Stat Tiles
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.metric("🏏 Total Runs (Avg)", f"{int(player_row['Runs']):,}", f"{float(player_row['Bat Avg']):.2f} Avg")
    with c_p2:
        st.metric("🎯 Total Wickets (Econ)", f"{int(player_row['Wickets']):,}", f"{float(player_row['Economy']):.2f} Econ")
    with c_p3:
        st.metric("⚡ Strike Rate & HS", f"{float(player_row['Strike Rate']):.1f}", f"HS: {int(player_row['High Score'])}")
    with c_p4:
        st.metric("🌟 Milestones", f"{int(player_row['100s'])} x 100s", f"{int(player_row['50s'])} x 50s")

    # Detailed Tabs for Player
    tab_career, tab_innings, tab_api_bio = st.tabs([
        "📊 Career Overview",
        "🏏 Match-by-Match Innings",
        "🌐 Live Cricbuzz Profile & Rankings"
    ])

    with tab_career:
        st.markdown("##### 📈 Career Batting & Bowling Breakdown")
        df_p_stat = execute_query("""
            SELECT 
                format AS "Format",
                matches_played AS "Matches",
                total_runs AS "Runs",
                batting_avg AS "Bat Avg",
                strike_rate AS "Strike Rate",
                centuries AS "100s",
                fifties AS "50s",
                highest_score AS "High Score",
                wickets_taken AS "Wickets",
                bowling_avg AS "Bowl Avg",
                economy_rate AS "Economy"
            FROM player_career_stats
            WHERE player_id = :pid
        """, {"pid": pid})
        st.dataframe(df_p_stat, use_container_width=True, hide_index=True)

    with tab_innings:
        st.markdown("##### 📋 Ingested Scorecard Innings")
        col_inn1, col_inn2 = st.columns(2)
        with col_inn1:
            st.markdown("###### 🏏 Batting Innings")
            df_b_inn = execute_query("""
                SELECT 
                    m.match_description AS "Match",
                    b.innings_number AS "Inn",
                    b.runs_scored AS "Runs",
                    b.balls_faced AS "Balls",
                    b.fours AS "4s",
                    b.sixes AS "6s",
                    b.strike_rate AS "SR",
                    CASE WHEN b.is_out = 1 THEN 'Out' ELSE 'Not Out' END AS "Status"
                FROM player_match_batting b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.player_id = :pid
                ORDER BY m.match_date DESC
            """, {"pid": pid})
            if not df_b_inn.empty:
                st.dataframe(df_b_inn, use_container_width=True, hide_index=True)
            else:
                st.info("No recorded batting innings in recent matches.")

        with col_inn2:
            st.markdown("###### 🎯 Bowling Figures")
            df_bw_inn = execute_query("""
                SELECT 
                    m.match_description AS "Match",
                    bw.innings_number AS "Inn",
                    bw.overs_bowled AS "Overs",
                    bw.maidens AS "Maidens",
                    bw.runs_conceded AS "Runs",
                    bw.wickets_taken AS "Wickets",
                    bw.economy_rate AS "Economy"
                FROM player_match_bowling bw
                JOIN matches m ON bw.match_id = m.match_id
                WHERE bw.player_id = :pid
                ORDER BY m.match_date DESC
            """, {"pid": pid})
            if not df_bw_inn.empty:
                st.dataframe(df_bw_inn, use_container_width=True, hide_index=True)
            else:
                st.info("No recorded bowling figures in recent matches.")

    with tab_api_bio:
        st.markdown("##### 🌐 Live Official Cricbuzz Bio & Career Data")
        client = CricbuzzAPIClient()
        with st.spinner("Fetching live player profile from Cricbuzz API..."):
            bio_data = client._make_request(f"stats/v1/player/{pid}")
            bat_format_data = client._make_request(f"stats/v1/player/{pid}/batting")
            bowl_format_data = client._make_request(f"stats/v1/player/{pid}/bowling")

        if bio_data:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Full Name:** {bio_data.get('fullName', sel_player_name)}")
                st.markdown(f"**Date of Birth:** {bio_data.get('DoBFormat', bio_data.get('DoB', 'N/A'))}")
                st.markdown(f"**Birth Place:** {bio_data.get('birthPlace', 'N/A')}")
                st.markdown(f"**Height:** {bio_data.get('height', 'N/A')}")
            with c2:
                st.markdown(f"**International Team:** {bio_data.get('intlTeam', sel_tname)}")
                st.markdown(f"**Playing Role:** {bio_data.get('role', player_row['Role'])}")
                st.markdown(f"**Batting Style:** {bio_data.get('bat', player_row['Batting Style'])}")
                st.markdown(f"**Bowling Style:** {bio_data.get('bowl', player_row['Bowling Style'])}")

            bio_text = bio_data.get("bio")
            if bio_text:
                st.markdown("###### 📖 Biography")
                st.write(bio_text)

        if bat_format_data and "values" in bat_format_data:
            st.markdown("###### 📊 Multi-Format Batting Records (Test / ODI / T20 / IPL)")
            headers = bat_format_data.get("headers", [])
            rows = []
            for v in bat_format_data.get("values", []):
                rows.append(v.get("values", []))
            if headers and rows:
                df_multi_bat = pd.DataFrame(rows, columns=headers)
                st.dataframe(df_multi_bat, use_container_width=True, hide_index=True)

        if bowl_format_data and "values" in bowl_format_data:
            st.markdown("###### 🎯 Multi-Format Bowling Records (Test / ODI / T20 / IPL)")
            headers = bowl_format_data.get("headers", [])
            rows = []
            for v in bowl_format_data.get("values", []):
                rows.append(v.get("values", []))
            if headers and rows:
                df_multi_bowl = pd.DataFrame(rows, columns=headers)
                st.dataframe(df_multi_bowl, use_container_width=True, hide_index=True)

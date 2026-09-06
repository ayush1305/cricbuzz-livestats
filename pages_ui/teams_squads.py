"""
Teams & Player Stats view for Cricbuzz LiveStats.
Provides official international rosters, comprehensive career batting & bowling stats,
and individual player profile inspectors without emojis.
"""

import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, execute_statement
from utils.cricbuzz_api import CricbuzzAPIClient


def render_teams_and_squads():
    st.markdown("""
    <div style="background: #ffffff; padding: 18px 24px; border-radius: 4px; border-left: 5px solid #009270; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 20px;">
        <h2 style="color: #009270; margin: 0; font-weight: 800; font-size: 24px;">International Cricket Teams & Squads</h2>
        <p style="color: #64748b; margin: 6px 0 0 0; font-size: 14px;">
            Official national squads, player career analytics, and individual player performance logs synced with Cricbuzz.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Fetch all teams with their squad sizes and stats
    df_teams = execute_query("""
        SELECT 
            t.team_id, 
            t.team_name, 
            t.team_code, 
            t.country, 
            COUNT(p.player_id) AS squad_size,
            COALESCE(SUM(cs.total_runs), 0) AS total_runs,
            COALESCE(SUM(cs.wickets_taken), 0) AS total_wickets,
            COALESCE(MAX(cs.highest_score), 0) AS highest_score
        FROM teams t
        LEFT JOIN players p ON t.team_id = p.team_id
        LEFT JOIN player_career_stats cs ON p.player_id = cs.player_id
        GROUP BY t.team_id, t.team_name, t.team_code, t.country
        ORDER BY squad_size DESC, t.team_name ASC
    """)

    if df_teams.empty:
        st.warning("No teams found in the database.")
        return

    # View Mode Selection: All Teams Overview vs Individual Team View
    query_view = st.query_params.get("view", "")
    query_team = st.query_params.get("team", "")

    default_view_idx = 0 if query_view == "all" else 1
    if not query_view and not query_team:
        default_view_idx = 0

    view_mode = st.radio(
        "Select View:",
        ["All International Teams Overview", "Individual Team & Player Stats"],
        index=default_view_idx,
        horizontal=True
    )

    # --------------------------------------------------------------------------
    # VIEW 1: ALL INTERNATIONAL TEAMS OVERVIEW
    # --------------------------------------------------------------------------
    if view_mode == "All International Teams Overview":
        st.markdown("### International Teams Comparison")
        st.caption("Overview of all national teams, squad sizes, and cumulative international records.")

        df_display_teams = df_teams.copy()
        df_display_teams = df_display_teams[df_display_teams["squad_size"] > 0]

        overview_table = df_display_teams.rename(columns={
            "team_name": "Team",
            "team_code": "Code",
            "country": "Country",
            "squad_size": "Squad Size",
            "total_runs": "Total Runs",
            "total_wickets": "Total Wickets",
            "highest_score": "Highest Score"
        })[["Team", "Code", "Country", "Squad Size", "Total Runs", "Total Wickets", "Highest Score"]]

        st.dataframe(overview_table, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### Quick Jump to Team Squad")
        btn_cols = st.columns(6)
        main_countries = ["India", "Australia", "England", "South Africa", "Pakistan", "New Zealand", 
                          "Sri Lanka", "Bangladesh", "Afghanistan", "West Indies", "Zimbabwe", "Ireland"]
        
        for idx, cname in enumerate(main_countries):
            col = btn_cols[idx % 6]
            with col:
                if st.button(cname, use_container_width=True):
                    st.query_params["team"] = cname
                    st.query_params["view"] = "single"
                    st.rerun()

    # --------------------------------------------------------------------------
    # VIEW 2: INDIVIDUAL TEAM & PLAYER STATS
    # --------------------------------------------------------------------------
    else:
        st.markdown("### Individual Team & Player Roster")

        # Prepare team options
        team_names = df_teams[df_teams["squad_size"] > 0]["team_name"].tolist()
        
        # Add remaining teams that might not have squads yet
        empty_teams = df_teams[df_teams["squad_size"] == 0]["team_name"].tolist()
        all_options = team_names + [f"{t} (Unsynced)" for t in empty_teams]

        # Determine default index
        default_team_idx = 0
        if query_team:
            for idx, opt in enumerate(team_names):
                if query_team.lower() == opt.lower():
                    default_team_idx = idx
                    break

        selected_team_str = st.selectbox(
            "Select International Team:",
            all_options,
            index=default_team_idx
        )

        clean_team_name = selected_team_str.replace(" (Unsynced)", "")
        sel_row = df_teams[df_teams["team_name"] == clean_team_name].iloc[0]
        sel_tid = int(sel_row["team_id"])
        sel_tname = sel_row["team_name"]
        sel_tcode = sel_row["team_code"] or sel_tname[:3].upper()

        # If team has 0 players, allow 1-click live fetch from Cricbuzz API
        if sel_row["squad_size"] == 0:
            st.info(f"Squad for {sel_tname} has not been synced yet.")
            if st.button(f"Fetch {sel_tname} Squad from Cricbuzz API", type="primary"):
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
                        st.success(f"Successfully imported {cnt} players for {sel_tname}!")
                        st.rerun()
                    else:
                        st.error("Could not fetch players from API for this team.")
            return

        # Team Summary Metrics (Clean, without emojis)
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            st.metric("Total Squad Size", f"{int(sel_row['squad_size'])} Players")
        with c_m2:
            st.metric("Total Team Runs", f"{int(sel_row['total_runs']):,}")
        with c_m3:
            st.metric("Total Team Wickets", f"{int(sel_row['total_wickets']):,}")
        with c_m4:
            st.metric("Highest Individual Score", f"{int(sel_row['highest_score'])}")

        st.markdown("---")

        # 2. Squad Table with full stats
        st.markdown(f"#### {sel_tname} Official Squad")
        
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

        st.dataframe(
            df_squad.drop(columns=["player_id"]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # 3. Individual Player Stats Inspector
        st.markdown("#### Player Profile & Performance Inspector")
        player_options = df_squad["Player"].tolist()
        
        if not player_options:
            return

        sel_player_name = st.selectbox("Select Player to inspect career numbers & match innings:", player_options)
        player_row = df_squad[df_squad["Player"] == sel_player_name].iloc[0]
        pid = int(player_row["player_id"])

        # Player Info Header
        st.markdown(f"""
        <div style="background: #ffffff; border-radius: 4px; border-left: 5px solid #009270; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h3 style="margin: 0; color: #0f172a; font-weight: 800;">{sel_player_name}</h3>
                    <p style="color: #64748b; margin: 4px 0 0 0; font-size: 13px;">
                        Role: {player_row['Role']} &bull; 
                        Team: {sel_tname} &bull; 
                        Batting: {player_row['Batting Style'] or 'N/A'} &bull; 
                        Bowling: {player_row['Bowling Style'] or 'N/A'}
                    </p>
                </div>
                <span style="background: #009270; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 12px;">
                    Cricbuzz ID: {pid}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Player Metric Tiles
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            st.metric("Total Runs (Bat Avg)", f"{int(player_row['Runs']):,}", f"{float(player_row['Bat Avg']):.2f} Avg")
        with c_p2:
            st.metric("Total Wickets (Economy)", f"{int(player_row['Wickets']):,}", f"{float(player_row['Economy']):.2f} Econ")
        with c_p3:
            st.metric("Strike Rate & High Score", f"{float(player_row['Strike Rate']):.1f}", f"HS: {int(player_row['High Score'])}")
        with c_p4:
            st.metric("Milestones", f"{int(player_row['100s'])} Hundreds", f"{int(player_row['50s'])} Fifties")

        # Tabs for detailed breakdown
        tab_career, tab_innings, tab_api_bio = st.tabs([
            "Career Overview",
            "Match-by-Match Innings",
            "Cricbuzz Profile & Rankings"
        ])

        with tab_career:
            st.markdown("##### Career Batting & Bowling Breakdown")
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
            st.markdown("##### Ingested Match Scorecards")
            col_inn1, col_inn2 = st.columns(2)
            with col_inn1:
                st.markdown("###### Batting Innings")
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
                    st.info("No recorded batting innings in recent scorecard matches.")

            with col_inn2:
                st.markdown("###### Bowling Figures")
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
                    st.info("No recorded bowling figures in recent scorecard matches.")

        with tab_api_bio:
            st.markdown("##### Official Cricbuzz Profile & Bio")
            client = CricbuzzAPIClient()
            with st.spinner("Fetching player profile from Cricbuzz API..."):
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
                    st.markdown("###### Biography")
                    st.write(bio_text)

            if bat_format_data and "values" in bat_format_data:
                st.markdown("###### Multi-Format Batting Records (Test / ODI / T20 / IPL)")
                headers = bat_format_data.get("headers", [])
                rows = []
                for v in bat_format_data.get("values", []):
                    rows.append(v.get("values", []))
                if headers and rows:
                    df_multi_bat = pd.DataFrame(rows, columns=headers)
                    st.dataframe(df_multi_bat, use_container_width=True, hide_index=True)

            if bowl_format_data and "values" in bowl_format_data:
                st.markdown("###### Multi-Format Bowling Records (Test / ODI / T20 / IPL)")
                headers = bowl_format_data.get("headers", [])
                rows = []
                for v in bowl_format_data.get("values", []):
                    rows.append(v.get("values", []))
                if headers and rows:
                    df_multi_bowl = pd.DataFrame(rows, columns=headers)
                    st.dataframe(df_multi_bowl, use_container_width=True, hide_index=True)

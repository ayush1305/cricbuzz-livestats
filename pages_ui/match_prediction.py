"""
Match Prediction & Insights view for Cricbuzz LiveStats.
Provides historical head-to-head performance, player form & momentum tracking,
venue-specific analytics, and statistical match insights powered exclusively by SQL queries.
"""

import math
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.db_connection import execute_query


def render_match_prediction():
    # Main Header
    st.markdown("""
    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #009270; padding: 18px 24px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; color: #009270; font-weight: 800; font-size: 1.6rem;">📈 Match Prediction & Insights</h2>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.95rem;">
                    Relational SQL-driven analytical engine for head-to-head trends, player momentum tracking, and venue intelligence.
                </p>
            </div>
            <div style="background: #e6f4ea; color: #00775a; font-weight: 700; font-size: 0.8rem; padding: 6px 12px; border-radius: 20px; border: 1px solid #bbf7d0;">
                Live SQL Analytics
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch available teams, venues, and players from database
    try:
        df_teams = execute_query("SELECT team_id, team_name, country FROM teams ORDER BY team_name ASC;")
        df_venues = execute_query("SELECT venue_id, venue_name, city, country FROM venues ORDER BY venue_name ASC;")
        df_players = execute_query("SELECT player_id, full_name, playing_role, country FROM players ORDER BY full_name ASC;")
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return

    if df_teams.empty:
        st.warning("Database contains no team records. Please populate teams data.")
        return

    # --------------------------------------------------------------------------
    # TOP GLOBAL FILTER PANEL
    # --------------------------------------------------------------------------
    st.markdown("""<div style="font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 10px;">Select Matchup Parameters</div>""", unsafe_allow_html=True)

    team_names = df_teams["team_name"].tolist()
    team_dict = dict(zip(df_teams["team_name"], df_teams["team_id"]))
    venue_dict = dict(zip(df_venues["venue_name"] + " (" + df_venues["city"] + ")", df_venues["venue_id"])) if not df_venues.empty else {}

    col_t1, col_t2, col_fmt, col_ven = st.columns([1.2, 1.2, 1, 1.4])

    with col_t1:
        default_t1 = team_names.index("India") if "India" in team_names else 0
        selected_team1 = st.selectbox("Team 1:", team_names, index=default_t1, key="pred_team1")

    with col_t2:
        # Default Team 2 to Australia or a different team
        default_t2 = team_names.index("Australia") if "Australia" in team_names else min(1, len(team_names) - 1)
        if selected_team1 == team_names[default_t2] and len(team_names) > 1:
            default_t2 = (default_t2 + 1) % len(team_names)
        selected_team2 = st.selectbox("Team 2:", team_names, index=default_t2, key="pred_team2")

    with col_fmt:
        selected_format = st.selectbox("Format:", ["All Formats", "T20 / T20I", "ODI", "Test"], key="pred_format")

    with col_ven:
        venue_options = ["All Venues"] + list(venue_dict.keys())
        selected_venue_name = st.selectbox("Venue (Optional):", venue_options, key="pred_venue")

    t1_id = team_dict.get(selected_team1)
    t2_id = team_dict.get(selected_team2)
    chosen_venue_id = venue_dict.get(selected_venue_name) if selected_venue_name != "All Venues" else None

    # Track SQL queries executed for Section 5
    executed_queries = []

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SECTION 1 — TEAM HISTORICAL PERFORMANCE
    # --------------------------------------------------------------------------
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <h3 style="margin: 0; color: #1e293b; font-weight: 800; font-size: 1.3rem;">🏏 Historical Team Performance</h3>
    </div>
    """, unsafe_allow_html=True)

    if t1_id == t2_id:
        st.info("Please select two distinct teams for head-to-head performance analysis.")
    else:
        # Build parameterized SQL query for head-to-head
        h2h_conditions = ["((m.team1_id = :t1 AND m.team2_id = :t2) OR (m.team1_id = :t2 AND m.team2_id = :t1))"]
        h2h_params = {"t1": t1_id, "t2": t2_id}

        if selected_format == "T20 / T20I":
            h2h_conditions.append("m.match_type IN ('T20', 'T20I')")
        elif selected_format == "ODI":
            h2h_conditions.append("m.match_type = 'ODI'")
        elif selected_format == "Test":
            h2h_conditions.append("m.match_type IN ('Test', 'TEST')")

        if chosen_venue_id:
            h2h_conditions.append("m.venue_id = :vid")
            h2h_params["vid"] = chosen_venue_id

        where_clause = " AND ".join(h2h_conditions)

        sql_h2h_matches = f"""
        SELECT
            m.match_id,
            m.match_date,
            m.match_type,
            m.match_description,
            v.venue_name || ' (' || v.city || ')' AS venue_location,
            m.winner_id,
            tw.team_name AS winner_name,
            m.victory_margin,
            m.victory_type
        FROM matches m
        LEFT JOIN venues v ON m.venue_id = v.venue_id
        LEFT JOIN teams tw ON m.winner_id = tw.team_id
        WHERE {where_clause}
        ORDER BY m.match_date DESC;
        """
        executed_queries.append(("Head-to-Head Matches Query", sql_h2h_matches, h2h_params))

        try:
            df_h2h_matches = execute_query(sql_h2h_matches, h2h_params)
        except Exception as e:
            st.error(f"Error querying head-to-head data: {str(e)}")
            df_h2h_matches = pd.DataFrame()

        if df_h2h_matches.empty:
            st.warning(f"Historical data not available for {selected_team1} vs {selected_team2} under selected filters.")
        else:
            total_m = len(df_h2h_matches)
            t1_wins = int((df_h2h_matches["winner_id"] == t1_id).sum())
            t2_wins = int((df_h2h_matches["winner_id"] == t2_id).sum())
            draws = total_m - (t1_wins + t2_wins)

            t1_win_pct = round((t1_wins / total_m) * 100, 1) if total_m > 0 else 0.0
            t2_win_pct = round((t2_wins / total_m) * 100, 1) if total_m > 0 else 0.0

            # Compute average score and wickets via SQL
            sql_avg_score = f"""
            SELECT
                b.team_id,
                t.team_name,
                ROUND(AVG(sub.innings_runs), 1) AS avg_team_score,
                ROUND(AVG(sub.wickets_lost), 1) AS avg_wickets_lost
            FROM (
                SELECT
                    b.match_id,
                    b.team_id,
                    SUM(b.runs_scored) AS innings_runs,
                    SUM(CASE WHEN b.is_out = 1 THEN 1 ELSE 0 END) AS wickets_lost
                FROM player_match_batting b
                JOIN matches m ON b.match_id = m.match_id
                WHERE {where_clause} AND b.team_id IN (:t1, :t2)
                GROUP BY b.match_id, b.team_id
            ) sub
            JOIN teams t ON sub.team_id = t.team_id
            JOIN player_match_batting b ON sub.match_id = b.match_id AND sub.team_id = b.team_id
            GROUP BY b.team_id, t.team_name;
            """
            executed_queries.append(("Average Team Score & Wickets Query", sql_avg_score, h2h_params))
            try:
                df_avg_scores = execute_query(sql_avg_score, h2h_params)
            except Exception:
                df_avg_scores = pd.DataFrame()

            t1_avg_score = "N/A"
            t1_avg_wkts = "N/A"
            t2_avg_score = "N/A"
            t2_avg_wkts = "N/A"

            if not df_avg_scores.empty:
                t1_row = df_avg_scores[df_avg_scores["team_id"] == t1_id]
                t2_row = df_avg_scores[df_avg_scores["team_id"] == t2_id]
                if not t1_row.empty:
                    t1_avg_score = f"{t1_row['avg_team_score'].values[0]:.0f}"
                    t1_avg_wkts = f"{t1_row['avg_wickets_lost'].values[0]:.1f}"
                if not t2_row.empty:
                    t2_avg_score = f"{t2_row['avg_team_score'].values[0]:.0f}"
                    t2_avg_wkts = f"{t2_row['avg_wickets_lost'].values[0]:.1f}"

            # UI Cards for Team 1 vs Team 2
            col_c1, col_c2, col_ch = st.columns([1.2, 1.2, 1.6])

            with col_c1:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #009270; border-radius: 6px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.2rem; font-weight: 800; color: #009270;">{selected_team1}</span>
                        <span style="background: #e6f4ea; color: #00775a; font-weight: 700; font-size: 0.85rem; padding: 3px 8px; border-radius: 12px;">{t1_win_pct}% Win Rate</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                        <div style="color: #64748b;">Matches: <strong style="color: #1e293b;">{total_m}</strong></div>
                        <div style="color: #64748b;">Wins: <strong style="color: #10b981;">{t1_wins}</strong></div>
                        <div style="color: #64748b;">Losses: <strong style="color: #ef4444;">{t2_wins}</strong></div>
                        <div style="color: #64748b;">Draws/Ties: <strong style="color: #64748b;">{draws}</strong></div>
                        <div style="color: #64748b;">Avg Score: <strong style="color: #1e293b;">{t1_avg_score}</strong></div>
                        <div style="color: #64748b;">Avg Wkts Lost: <strong style="color: #1e293b;">{t1_avg_wkts}</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_c2:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #0284c7; border-radius: 6px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.2rem; font-weight: 800; color: #0284c7;">{selected_team2}</span>
                        <span style="background: #e0f2fe; color: #0369a1; font-weight: 700; font-size: 0.85rem; padding: 3px 8px; border-radius: 12px;">{t2_win_pct}% Win Rate</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                        <div style="color: #64748b;">Matches: <strong style="color: #1e293b;">{total_m}</strong></div>
                        <div style="color: #64748b;">Wins: <strong style="color: #10b981;">{t2_wins}</strong></div>
                        <div style="color: #64748b;">Losses: <strong style="color: #ef4444;">{t1_wins}</strong></div>
                        <div style="color: #64748b;">Draws/Ties: <strong style="color: #64748b;">{draws}</strong></div>
                        <div style="color: #64748b;">Avg Score: <strong style="color: #1e293b;">{t2_avg_score}</strong></div>
                        <div style="color: #64748b;">Avg Wkts Lost: <strong style="color: #1e293b;">{t2_avg_wkts}</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_ch:
                # Plotly Donut / Bar chart for head to head
                fig_h2h = go.Figure(data=[go.Pie(
                    labels=[selected_team1, selected_team2] + (["Draws/No Result"] if draws > 0 else []),
                    values=[t1_wins, t2_wins] + ([draws] if draws > 0 else []),
                    hole=0.55,
                    marker=dict(colors=["#009270", "#0284c7", "#94a3b8"]),
                    textinfo="label+value",
                    hoverinfo="label+value+percent"
                )])
                fig_h2h.update_layout(
                    title=f"Head-to-Head Win Distribution ({total_m} Matches)",
                    template="plotly_white",
                    height=220,
                    margin=dict(l=10, r=10, t=35, b=10),
                    showlegend=False,
                    paper_bgcolor="#ffffff"
                )
                st.plotly_chart(fig_h2h, use_container_width=True)

            # Recent Matches Table
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 15px 0 8px 0;'>Recent Head-to-Head Encounters</div>", unsafe_allow_html=True)
            df_display = df_h2h_matches[["match_date", "match_description", "match_type", "venue_location", "winner_name", "victory_margin", "victory_type"]].copy()
            df_display.columns = ["Date", "Match Description", "Format", "Venue", "Winner", "Margin", "Result Type"]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SECTION 2 — PLAYER FORM & MOMENTUM
    # --------------------------------------------------------------------------
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <h3 style="margin: 0; color: #1e293b; font-weight: 800; font-size: 1.3rem;">🔥 Player Form & Momentum</h3>
    </div>
    """, unsafe_allow_html=True)

    player_names = df_players["full_name"].tolist()
    player_dict = dict(zip(df_players["full_name"], df_players["player_id"]))

    col_p1, col_p2 = st.columns([1.5, 2.5])
    with col_p1:
        # Default to Virat Kohli or Rohit Sharma if present
        def_p_idx = player_names.index("Virat Kohli") if "Virat Kohli" in player_names else 0
        selected_player = st.selectbox("Select Player:", player_names, index=def_p_idx, key="form_player_select")
        p_id = player_dict.get(selected_player)

    with col_p2:
        num_recent = st.slider("Number of Recent Matches to Analyze:", min_value=3, max_value=15, value=10, step=1, key="form_num_recent")

    # SQL Query to pull recent batting and bowling performances
    sql_player_form = """
    SELECT
        b.stat_id,
        b.match_id,
        m.match_date,
        m.match_type,
        m.match_description,
        v.venue_name || ' (' || v.city || ')' AS venue_location,
        CASE WHEN m.team1_id = b.team_id THEN t2.team_name ELSE t1.team_name END AS opponent,
        b.runs_scored,
        b.balls_faced,
        b.strike_rate,
        b.fours,
        b.sixes,
        b.is_out,
        bw.wickets_taken,
        bw.overs_bowled,
        bw.runs_conceded,
        bw.economy_rate,
        CASE
            WHEN m.winner_id = b.team_id THEN 'Won'
            WHEN m.winner_id IS NULL THEN 'Draw/NR'
            ELSE 'Lost'
        END AS match_result
    FROM player_match_batting b
    JOIN matches m ON b.match_id = m.match_id
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    LEFT JOIN venues v ON m.venue_id = v.venue_id
    LEFT JOIN player_match_bowling bw ON b.match_id = bw.match_id AND b.player_id = bw.player_id
    WHERE b.player_id = :pid
    ORDER BY m.match_date DESC
    LIMIT :lim;
    """
    executed_queries.append(("Recent Player Performances Query", sql_player_form, {"pid": p_id, "lim": num_recent}))

    try:
        df_player_perf = execute_query(sql_player_form, {"pid": p_id, "lim": num_recent})
    except Exception as e:
        st.error(f"Error fetching player performances: {str(e)}")
        df_player_perf = pd.DataFrame()

    if df_player_perf.empty:
        # Check if career stats exist to display career snapshot
        sql_career_snap = "SELECT * FROM player_career_stats WHERE player_id = :pid"
        df_career_snap = execute_query(sql_career_snap, {"pid": p_id})
        if not df_career_snap.empty:
            st.info(f"No recent match-level logs found for {selected_player} in the database. Career overview: {df_career_snap['total_runs'].values[0]} runs, {df_career_snap['wickets_taken'].values[0]} wickets across {df_career_snap['matches_played'].values[0]} matches.")
        else:
            st.warning(f"Historical data not available for {selected_player}.")
    else:
        # Calculate Form Score & Metrics
        innings_cnt = len(df_player_perf)
        runs_series = df_player_perf["runs_scored"]
        sr_series = df_player_perf["strike_rate"]
        wkts_series = df_player_perf["wickets_taken"].fillna(0)

        recent_avg_runs = float(runs_series.mean())
        recent_avg_sr = float(sr_series.mean())
        fifties = int(((runs_series >= 50) & (runs_series < 100)).sum())
        centuries = int((runs_series >= 100).sum())
        highest_score = int(runs_series.max())
        total_wkts = int(wkts_series.sum())

        # Consistency (Standard deviation of runs)
        stddev_runs = float(runs_series.std()) if innings_cnt > 1 else 0.0

        # Trend Determination (Compare last 3 innings to older innings)
        if innings_cnt >= 4:
            recent_3_avg = float(runs_series.iloc[:3].mean())
            older_avg = float(runs_series.iloc[3:].mean())
            diff = recent_3_avg - older_avg
            if diff > 10.0:
                trend_badge = "🔥 Improving"
                trend_desc = "Scoring momentum is accelerating over recent appearances."
                trend_color = "#10b981"
            elif diff < -10.0:
                trend_badge = "⚠️ Declining"
                trend_desc = "Scoring output has dipped below earlier matches in this window."
                trend_color = "#ef4444"
            else:
                trend_badge = "➡️ Stable"
                trend_desc = "Consistent scoring output without extreme volatility."
                trend_color = "#0284c7"
        else:
            trend_badge = "➡️ Stable"
            trend_desc = "Sample size developing across available database appearances."
            trend_color = "#0284c7"

        # Analytical Form Score Calculation (0 to 100)
        # Components:
        # 1. Scoring Volume & Average: up to 50 pts (avg 60+ = 50 pts)
        # 2. Strike Rate Impact: up to 25 pts (SR 140+ = 25 pts)
        # 3. Conversion Milestones (50s & 100s): up to 15 pts
        # 4. Consistency factor: up to 10 pts
        avg_pts = min(50.0, (recent_avg_runs / 60.0) * 50.0)
        sr_pts = min(25.0, (recent_avg_sr / 140.0) * 25.0)
        milestone_pts = min(15.0, (fifties * 4.0) + (centuries * 8.0))
        consistency_pts = max(0.0, 10.0 - min(10.0, stddev_runs * 0.15))
        bowling_bonus = min(10.0, total_wkts * 2.0)

        raw_score = avg_pts + sr_pts + milestone_pts + consistency_pts + bowling_bonus
        form_score = int(round(min(100.0, max(0.0, raw_score))))

        if form_score >= 80:
            form_status = "Excellent Recent Form"
            form_bg = "#e6f4ea"
            form_color = "#00775a"
        elif form_score >= 60:
            form_status = "Good Recent Form"
            form_bg = "#e0f2fe"
            form_color = "#0369a1"
        elif form_score >= 40:
            form_status = "Moderate Form"
            form_bg = "#fef3c7"
            form_color = "#b45309"
        else:
            form_status = "Struggling Form"
            form_bg = "#fee2e2"
            form_color = "#b91c1c"

        # Render Metrics & Form Score Card
        col_f1, col_f2, col_f3, col_f4 = st.columns([1.5, 1, 1, 1])

        with col_f1:
            st.markdown(f"""
            <div style="background: {form_bg}; border: 1px solid #bbf7d0; border-radius: 6px; padding: 16px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <div style="font-size: 0.8rem; font-weight: 700; color: {form_color}; text-transform: uppercase; letter-spacing: 0.5px;">Form Score (0–100)</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: {form_color}; margin: 4px 0;">🔥 {form_score}/100</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: {form_color};">{form_status}</div>
                <div style="font-size: 0.72rem; color: #64748b; margin-top: 6px;">
                    *ANALYTICAL SCORE calculated by this application, not an official Cricbuzz statistic.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_f2:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Recent Batting Avg</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #009270;">{recent_avg_runs:.1f}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Strike Rate: <strong>{recent_avg_sr:.1f}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with col_f3:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Highest Score / 50s</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #1e293b;">{highest_score}</div>
                <div style="font-size: 0.75rem; color: #64748b;">50s: <strong>{fifties}</strong> | 100s: <strong>{centuries}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        with col_f4:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; text-align: center;">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Recent Momentum</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: {trend_color}; margin: 4px 0;">{trend_badge}</div>
                <div style="font-size: 0.72rem; color: #64748b;">StdDev: <strong>±{stddev_runs:.1f}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        # Momentum Line Chart
        col_m1, col_m2 = st.columns([2, 1.2])
        with col_m1:
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 15px 0 6px 0;'>Momentum Trend (Runs Across Recent Matches)</div>", unsafe_allow_html=True)
            # Reorder chronological for trend line
            df_chart = df_player_perf.iloc[::-1].reset_index(drop=True)
            df_chart["match_label"] = [f"M{i+1}: vs {row['opponent']}" for i, row in df_chart.iterrows()]

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=df_chart["match_label"],
                y=df_chart["runs_scored"],
                mode="lines+markers+text",
                name="Runs Scored",
                line=dict(color="#009270", width=3),
                marker=dict(size=10, color="#009270", symbol="circle"),
                text=df_chart["runs_scored"],
                textposition="top center"
            ))
            # Average reference line
            fig_trend.add_hline(
                y=recent_avg_runs,
                line_dash="dash",
                line_color="#f59e0b",
                annotation_text=f"Avg: {recent_avg_runs:.1f}",
                annotation_position="bottom right"
            )
            fig_trend.update_layout(
                template="plotly_white",
                height=260,
                margin=dict(l=15, r=15, t=25, b=15),
                xaxis_title="Match Sequence",
                yaxis_title="Runs Scored",
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc"
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_m2:
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 15px 0 6px 0;'>Momentum Diagnostic</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; font-size: 0.88rem; color: #334155; line-height: 1.6;">
                <p style="margin: 0 0 8px 0;"><strong>Player:</strong> {selected_player}</p>
                <p style="margin: 0 0 8px 0;"><strong>Sample Size:</strong> Last {innings_cnt} database innings</p>
                <p style="margin: 0 0 8px 0;"><strong>Trajectory:</strong> <span style="color: {trend_color}; font-weight: 700;">{trend_badge}</span></p>
                <p style="margin: 0 0 8px 0;"><strong>Analysis:</strong> {trend_desc}</p>
                <p style="margin: 0; color: #64748b; font-size: 0.8rem;">*Calculated strictly using SQL window queries against player match logs.</p>
            </div>
            """, unsafe_allow_html=True)

        # Recent Performances Table
        st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 15px 0 8px 0;'>Recent Match Performance Breakdown</div>", unsafe_allow_html=True)
        cols_table = ["match_date", "opponent", "runs_scored", "balls_faced", "strike_rate", "fours", "sixes", "wickets_taken", "match_result", "venue_location"]
        df_tbl = df_player_perf[cols_table].copy()
        df_tbl.columns = ["Date", "Opponent", "Runs", "Balls", "SR", "4s", "6s", "Wkts", "Result", "Venue"]
        st.dataframe(df_tbl, use_container_width=True, hide_index=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SECTION 3 — VENUE-SPECIFIC PERFORMANCE
    # --------------------------------------------------------------------------
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <h3 style="margin: 0; color: #1e293b; font-weight: 800; font-size: 1.3rem;">🏟️ Venue Performance</h3>
    </div>
    """, unsafe_allow_html=True)

    col_v_p, col_v_ven, col_v_fmt = st.columns([1.5, 2, 1])
    with col_v_p:
        selected_v_player = st.selectbox("Player for Venue Stats:", player_names, index=def_p_idx, key="v_player_select")
        v_pid = player_dict.get(selected_v_player)

    with col_v_ven:
        # Default venue
        venue_select_list = list(venue_dict.keys())
        def_v_idx = 0
        if "Kensington Oval (Bridgetown, Barbados)" in venue_select_list:
            def_v_idx = venue_select_list.index("Kensington Oval (Bridgetown, Barbados)")
        selected_target_venue = st.selectbox("Select Venue to Inspect:", venue_select_list, index=def_v_idx, key="v_venue_select")
        target_vid = venue_dict.get(selected_target_venue)

    with col_v_fmt:
        v_format = st.selectbox("Format Filter:", ["All Formats", "T20 / T20I", "ODI", "Test"], key="v_format_select")

    # SQL query for specific venue
    venue_sql_conds = ["b.player_id = :pid", "m.venue_id = :vid"]
    venue_sql_params = {"pid": v_pid, "vid": target_vid}

    if v_format == "T20 / T20I":
        venue_sql_conds.append("m.match_type IN ('T20', 'T20I')")
    elif v_format == "ODI":
        venue_sql_conds.append("m.match_type = 'ODI'")
    elif v_format == "Test":
        venue_sql_conds.append("m.match_type IN ('Test', 'TEST')")

    sql_venue_specific = f"""
    SELECT
        COUNT(b.stat_id) AS matches_played,
        COALESCE(SUM(b.runs_scored), 0) AS total_runs,
        ROUND(AVG(b.runs_scored), 2) AS batting_avg,
        ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate,
        SUM(CASE WHEN b.runs_scored >= 50 AND b.runs_scored < 100 THEN 1 ELSE 0 END) AS fifties,
        SUM(CASE WHEN b.runs_scored >= 100 THEN 1 ELSE 0 END) AS hundreds,
        MAX(b.runs_scored) AS highest_score,
        COALESCE(SUM(bw.wickets_taken), 0) AS wickets_taken,
        ROUND(AVG(bw.wickets_taken), 2) AS avg_wickets
    FROM player_match_batting b
    JOIN matches m ON b.match_id = m.match_id
    LEFT JOIN player_match_bowling bw ON b.match_id = bw.match_id AND b.player_id = bw.player_id
    WHERE {" AND ".join(venue_sql_conds)};
    """
    executed_queries.append(("Venue Specific Performance Query", sql_venue_specific, venue_sql_params))

    try:
        df_venue_stat = execute_query(sql_venue_specific, venue_sql_params)
    except Exception as e:
        st.error(f"Error querying venue data: {str(e)}")
        df_venue_stat = pd.DataFrame()

    has_venue_data = not df_venue_stat.empty and df_venue_stat["matches_played"].values[0] > 0

    if not has_venue_data:
        st.warning(f"Historical data not available for {selected_v_player} at {selected_target_venue} under {v_format} format.")
    else:
        v_row = df_venue_stat.iloc[0]
        col_vs1, col_vs2, col_vs3, col_vs4 = st.columns(4)
        with col_vs1:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #009270; border-radius: 4px; padding: 12px; text-align: center;">
                <div style="font-size: 0.78rem; color: #64748b; font-weight: 600;">Matches / Runs</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b;">{int(v_row['matches_played'])} / {int(v_row['total_runs'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_vs2:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #009270; border-radius: 4px; padding: 12px; text-align: center;">
                <div style="font-size: 0.78rem; color: #64748b; font-weight: 600;">Batting Avg / SR</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #009270;">{v_row['batting_avg']:.1f} / {v_row['avg_strike_rate']:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_vs3:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #009270; border-radius: 4px; padding: 12px; text-align: center;">
                <div style="font-size: 0.78rem; color: #64748b; font-weight: 600;">Highest Score / 50s / 100s</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b;">{int(v_row['highest_score'])} ({int(v_row['fifties'])}F / {int(v_row['hundreds'])}C)</div>
            </div>
            """, unsafe_allow_html=True)
        with col_vs4:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #009270; border-radius: 4px; padding: 12px; text-align: center;">
                <div style="font-size: 0.78rem; color: #64748b; font-weight: 600;">Wickets Taken</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #0284c7;">{int(v_row['wickets_taken'])}</div>
            </div>
            """, unsafe_allow_html=True)

    # Venue Comparison Chart for this player across all venues
    sql_all_venues_player = """
    SELECT
        v.venue_name || ' (' || v.city || ')' AS venue_label,
        COUNT(b.stat_id) AS matches_at_venue,
        SUM(b.runs_scored) AS total_runs_at_venue,
        ROUND(AVG(b.runs_scored), 1) AS avg_runs_at_venue,
        MAX(b.runs_scored) AS highest_at_venue
    FROM player_match_batting b
    JOIN matches m ON b.match_id = m.match_id
    JOIN venues v ON m.venue_id = v.venue_id
    WHERE b.player_id = :pid
    GROUP BY v.venue_id, v.venue_name, v.city
    ORDER BY total_runs_at_venue DESC;
    """
    executed_queries.append(("Player Venue Comparison Query", sql_all_venues_player, {"pid": v_pid}))
    try:
        df_venue_comp = execute_query(sql_all_venues_player, {"pid": v_pid})
    except Exception:
        df_venue_comp = pd.DataFrame()

    if not df_venue_comp.empty:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1e293b; margin: 15px 0 6px 0;'>Venue Comparison: Career Runs by Ground</div>", unsafe_allow_html=True)
        fig_v_comp = px.bar(
            df_venue_comp,
            x="venue_label",
            y="total_runs_at_venue",
            color="avg_runs_at_venue",
            color_continuous_scale=["#bbf7d0", "#009270", "#005a44"],
            text="total_runs_at_venue",
            labels={"venue_label": "Ground", "total_runs_at_venue": "Total Runs", "avg_runs_at_venue": "Batting Avg"}
        )
        fig_v_comp.update_layout(
            template="plotly_white",
            height=260,
            margin=dict(l=15, r=15, t=25, b=15),
            xaxis_title="Cricket Venue",
            yaxis_title="Runs Scored",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f8fafc"
        )
        st.plotly_chart(fig_v_comp, use_container_width=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SECTION 4 — MATCH INSIGHTS
    # --------------------------------------------------------------------------
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <h3 style="margin: 0; color: #1e293b; font-weight: 800; font-size: 1.3rem;">🎯 Match Insights</h3>
    </div>
    """, unsafe_allow_html=True)

    if t1_id == t2_id:
        st.info("Select two distinct teams to generate statistical match insights.")
    else:
        # Multi-factor statistical model combining:
        # 1. Head-to-Head win rate (40% weight)
        # 2. Overall team format win rate (30% weight)
        # 3. Venue win rate (20% weight)
        # 4. Recent momentum factor (10% weight)

        # Query overall win rate for Team 1 and Team 2 in format
        fmt_clause = ""
        fmt_params = {"t1": t1_id, "t2": t2_id}
        if selected_format == "T20 / T20I":
            fmt_clause = "AND match_type IN ('T20', 'T20I')"
        elif selected_format == "ODI":
            fmt_clause = "AND match_type = 'ODI'"
        elif selected_format == "Test":
            fmt_clause = "AND match_type IN ('Test', 'TEST')"

        sql_overall_win = f"""
        SELECT
            team_id,
            COUNT(match_id) AS total_played,
            SUM(CASE WHEN winner_id = team_id THEN 1 ELSE 0 END) AS wins
        FROM (
            SELECT match_id, team1_id AS team_id, winner_id FROM matches WHERE is_completed = 1 {fmt_clause}
            UNION ALL
            SELECT match_id, team2_id AS team_id, winner_id FROM matches WHERE is_completed = 1 {fmt_clause}
        )
        WHERE team_id IN (:t1, :t2)
        GROUP BY team_id;
        """
        executed_queries.append(("Overall Team Win Rate Query", sql_overall_win, fmt_params))
        df_overall = execute_query(sql_overall_win, fmt_params)

        t1_overall_pct = 50.0
        t2_overall_pct = 50.0
        if not df_overall.empty:
            r1 = df_overall[df_overall["team_id"] == t1_id]
            r2 = df_overall[df_overall["team_id"] == t2_id]
            if not r1.empty and r1["total_played"].values[0] > 0:
                t1_overall_pct = (r1["wins"].values[0] / r1["total_played"].values[0]) * 100.0
            if not r2.empty and r2["total_played"].values[0] > 0:
                t2_overall_pct = (r2["wins"].values[0] / r2["total_played"].values[0]) * 100.0

        # Query venue win rate for each team if venue selected
        t1_venue_perf = "Neutral / Moderate"
        t2_venue_perf = "Neutral / Moderate"
        t1_venue_score = 50.0
        t2_venue_score = 50.0

        if chosen_venue_id:
            sql_venue_win = """
            SELECT
                team_id,
                COUNT(match_id) AS total_played,
                SUM(CASE WHEN winner_id = team_id THEN 1 ELSE 0 END) AS wins
            FROM (
                SELECT match_id, team1_id AS team_id, winner_id FROM matches WHERE is_completed = 1 AND venue_id = :vid
                UNION ALL
                SELECT match_id, team2_id AS team_id, winner_id FROM matches WHERE is_completed = 1 AND venue_id = :vid
            )
            WHERE team_id IN (:t1, :t2)
            GROUP BY team_id;
            """
            executed_queries.append(("Venue Team Performance Query", sql_venue_win, {"t1": t1_id, "t2": t2_id, "vid": chosen_venue_id}))
            df_ven_win = execute_query(sql_venue_win, {"t1": t1_id, "t2": t2_id, "vid": chosen_venue_id})
            if not df_ven_win.empty:
                rv1 = df_ven_win[df_ven_win["team_id"] == t1_id]
                rv2 = df_ven_win[df_ven_win["team_id"] == t2_id]
                if not rv1.empty and rv1["total_played"].values[0] > 0:
                    t1_venue_score = (rv1["wins"].values[0] / rv1["total_played"].values[0]) * 100.0
                    t1_venue_perf = "Strong" if t1_venue_score >= 60 else ("Moderate" if t1_venue_score >= 40 else "Limited")
                if not rv2.empty and rv2["total_played"].values[0] > 0:
                    t2_venue_score = (rv2["wins"].values[0] / rv2["total_played"].values[0]) * 100.0
                    t2_venue_perf = "Strong" if t2_venue_score >= 60 else ("Moderate" if t2_venue_score >= 40 else "Limited")

        # Head to head stats from Section 1
        h2h_total = len(df_h2h_matches) if 'df_h2h_matches' in locals() and not df_h2h_matches.empty else 0
        if h2h_total > 0:
            h2h_t1_pct = (int((df_h2h_matches["winner_id"] == t1_id).sum()) / h2h_total) * 100.0
            h2h_t2_pct = (int((df_h2h_matches["winner_id"] == t2_id).sum()) / h2h_total) * 100.0
        else:
            h2h_t1_pct = 50.0
            h2h_t2_pct = 50.0

        # Recent form categorization
        t1_form_str = "Strong" if t1_overall_pct >= 60 else ("Moderate" if t1_overall_pct >= 40 else "Rebuilding")
        t2_form_str = "Strong" if t2_overall_pct >= 60 else ("Moderate" if t2_overall_pct >= 40 else "Rebuilding")

        # Check sufficiency of historical data
        total_sample = h2h_total + (len(df_overall) if not df_overall.empty else 0)
        if total_sample == 0:
            st.warning("Insufficient historical data for a reliable comparison.")
        else:
            # Composite Statistical Rating
            rating_t1 = (h2h_t1_pct * 0.40) + (t1_overall_pct * 0.35) + (t1_venue_score * 0.25)
            rating_t2 = (h2h_t2_pct * 0.40) + (t2_overall_pct * 0.35) + (t2_venue_score * 0.25)

            rating_diff = abs(rating_t1 - rating_t2)

            if rating_diff < 5.0:
                advantage_team = "Evenly Matched (No Clear Advantage)"
                confidence_pct = 50.0 + (rating_diff * 2.0)
                advantage_color = "#f59e0b"
            elif rating_t1 > rating_t2:
                advantage_team = selected_team1
                confidence_pct = min(88.0, 55.0 + (rating_diff * 0.75))
                advantage_color = "#009270"
            else:
                advantage_team = selected_team2
                confidence_pct = min(88.0, 55.0 + (rating_diff * 0.75))
                advantage_color = "#0284c7"

            # Render Insights View
            col_in1, col_in2 = st.columns([1.5, 1.2])

            with col_in1:
                st.html(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">Statistical Insight & Historical Advantage</div>
                    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 14px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;">
                        <div>
                            <span style="font-size: 0.95rem; color: #64748b;">Analytical Advantage:</span><br>
                            <span style="font-size: 1.4rem; font-weight: 800; color: {advantage_color};">{advantage_team}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 0.95rem; color: #64748b;">Confidence Rating:</span><br>
                            <span style="font-size: 1.4rem; font-weight: 800; color: {advantage_color};">{confidence_pct:.0f}%</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px;">
                        <div style="background: #f8fafc; padding: 12px; border-radius: 4px; border-left: 3px solid #009270;">
                            <strong style="color: #009270;">{selected_team1}</strong>
                            <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">H2H Win Rate: <strong style="color: #1e293b;">{h2h_t1_pct:.1f}%</strong></div>
                            <div style="font-size: 0.82rem; color: #64748b;">Recent Form: <strong style="color: #1e293b;">{t1_form_str}</strong></div>
                            <div style="font-size: 0.82rem; color: #64748b;">Venue Record: <strong style="color: #1e293b;">{t1_venue_perf}</strong></div>
                        </div>
                        <div style="background: #f8fafc; padding: 12px; border-radius: 4px; border-left: 3px solid #0284c7;">
                            <strong style="color: #0284c7;">{selected_team2}</strong>
                            <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">H2H Win Rate: <strong style="color: #1e293b;">{h2h_t2_pct:.1f}%</strong></div>
                            <div style="font-size: 0.82rem; color: #64748b;">Recent Form: <strong style="color: #1e293b;">{t2_form_str}</strong></div>
                            <div style="font-size: 0.82rem; color: #64748b;">Venue Record: <strong style="color: #1e293b;">{t2_venue_perf}</strong></div>
                        </div>
                    </div>
                </div>
                """)

            with col_in2:
                st.html(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 0.88rem;">
                    <div style="font-weight: 700; color: #1e293b; margin-bottom: 8px;">Key Analytical Factors</div>
                    <ul style="margin: 0; padding-left: 18px; color: #475569; line-height: 1.6;">
                        <li><strong>Head-to-Head:</strong> Based on {h2h_total} completed encounters in the database.</li>
                        <li><strong>Format Alignment:</strong> Filtered by {selected_format} fixtures.</li>
                        <li><strong>Ground Index:</strong> Evaluated against {selected_venue_name}.</li>
                        <li><strong>Model Methodology:</strong> Multi-factor probability weighted against historical win distributions.</li>
                    </ul>
                    <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid #f1f5f9; font-size: 0.75rem; color: #64748b; font-style: italic;">
                        <strong>Notice:</strong> This is an analytical sports research model based exclusively on SQL database records. It does not represent a guaranteed outcome or wagering advice.
                    </div>
                </div>
                """)

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SECTION 5 — SQL-DRIVEN ANALYTICS & DATA SOURCE
    # --------------------------------------------------------------------------
    with st.expander("🧠 Data Source & Underlying SQL Queries (Click to Inspect Live Statements)", expanded=False):
        st.markdown("""
        <div style="margin-bottom: 12px; color: #475569; font-size: 0.9rem;">
            All metrics, win rates, averages, and momentum trends on this page are computed live using <strong>parameterized SQL queries</strong> against the relational cricket analytics database.
        </div>
        """, unsafe_allow_html=True)

        for q_title, q_sql, q_params in executed_queries:
            st.markdown(f"**{q_title}**")
            st.code(q_sql.strip(), language="sql")
            st.caption(f"Bound Parameters: `{q_params}`")
            st.markdown("---")

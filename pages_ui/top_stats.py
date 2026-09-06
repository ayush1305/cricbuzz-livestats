"""
Top Player Stats and Leaderboards view for Cricbuzz LiveStats.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import execute_query
from utils.visualizer import create_top_run_scorers_chart


def render_top_stats():
    st.title("Top Player Statistics & Global Leaderboards")
    st.markdown("Explore batting, bowling, and all-round excellence across Test, ODI, and T20I formats.")

    col1, col2 = st.columns([1, 2])
    with col1:
        format_filter = st.selectbox("Select Cricket Format:", ["ODI", "Test", "T20I"])
    with col2:
        stat_category = st.radio(
            "Category:",
            ["Top Batting Records", "Top Bowling Figures", "All-Round Dominance"],
            horizontal=True
        )

    if "Batting" in stat_category:
        query = f"""
        SELECT
            p.full_name AS player_name,
            p.country,
            pcs.total_runs,
            pcs.batting_avg,
            pcs.strike_rate,
            pcs.centuries,
            pcs.fifties,
            pcs.highest_score
        FROM player_career_stats pcs
        JOIN players p ON pcs.player_id = p.player_id
        WHERE pcs.format = '{format_filter}'
        ORDER BY pcs.total_runs DESC
        LIMIT 10;
        """
        df = execute_query(query)
        st.subheader(f"Top 10 Run Scorers in {format_filter} Cricket")

        if not df.empty:
            chart = create_top_run_scorers_chart(df)
            st.plotly_chart(chart, use_container_width=True)

            st.dataframe(
                df.style.format({
                    "total_runs": "{:,}",
                    "batting_avg": "{:.2f}",
                    "strike_rate": "{:.2f}",
                    "centuries": "{:d}",
                    "fifties": "{:d}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No records found for the selected filter.")

    elif "Bowling" in stat_category:
        query = f"""
        SELECT
            p.full_name AS bowler_name,
            p.country,
            pcs.wickets_taken,
            pcs.bowling_avg,
            pcs.economy_rate,
            pcs.matches_played
        FROM player_career_stats pcs
        JOIN players p ON pcs.player_id = p.player_id
        WHERE pcs.format = '{format_filter}' AND pcs.wickets_taken > 0
        ORDER BY pcs.wickets_taken DESC
        LIMIT 10;
        """
        df = execute_query(query)
        st.subheader(f"Leading Wicket Takers in {format_filter} Cricket")

        if not df.empty:
            fig = px.bar(
                df,
                x="wickets_taken",
                y="bowler_name",
                color="economy_rate",
                orientation="h",
                color_continuous_scale="Viridis",
                text="wickets_taken",
                title=f"🎯 Leading Wicket Takers ({format_filter})",
                labels={"wickets_taken": "Total Wickets", "bowler_name": "Bowler", "economy_rate": "Economy"}
            )
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                template="plotly_dark",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                df.style.format({
                    "wickets_taken": "{:,}",
                    "bowling_avg": "{:.2f}",
                    "economy_rate": "{:.2f}",
                    "matches_played": "{:d}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No bowling records available for the selected format.")

    else: # All-Round Dominance
        query = f"""
        SELECT
            p.full_name AS player_name,
            p.country,
            pcs.total_runs,
            pcs.batting_avg,
            pcs.wickets_taken,
            pcs.bowling_avg,
            ROUND((pcs.total_runs * 0.01) + (pcs.wickets_taken * 2.0), 2) AS allround_index
        FROM player_career_stats pcs
        JOIN players p ON pcs.player_id = p.player_id
        WHERE pcs.format = '{format_filter}' AND p.playing_role = 'All-rounder'
        ORDER BY allround_index DESC;
        """
        df = execute_query(query)
        st.subheader(f"Top Ranked All-Rounders in {format_filter}")

        if not df.empty:
            fig = px.scatter(
                df,
                x="total_runs",
                y="wickets_taken",
                text="player_name",
                size="allround_index",
                color="country",
                title="⚖️ Runs vs Wickets Matrix (All-Rounders)",
                labels={"total_runs": "Total Career Runs", "wickets_taken": "Total Wickets"}
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No all-rounder records for this format.")

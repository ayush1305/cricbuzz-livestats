"""
SQL Practice Questions and Analytics Engine view for Cricbuzz LiveStats.
Provides interactive execution of all 25 Practice Questions (Beginner, Intermediate, Advanced)
plus a Custom SQL Query Console.
"""

import time
import streamlit as st
import pandas as pd
from utils.db_connection import execute_query
from utils.sql_catalog import SQL_QUESTIONS
from utils.visualizer import (
    create_toss_win_chart,
    create_player_form_trend_chart,
    create_bowler_economy_chart,
    create_head_to_head_chart,
    create_top_run_scorers_chart
)


def render_sql_analytics():
    st.title("SQL Practice & Analytics Engine")
    st.markdown("Execute all 25 production-grade SQL practice questions with instant results, execution plans, and dynamic visualizations.")

    tab_catalog, tab_custom = st.tabs(["25 Practice Queries", "Custom SQL Console"])

    with tab_catalog:
        render_practice_catalog()

    with tab_custom:
        render_custom_console()


def render_practice_catalog():
    # Filter by Difficulty
    col_filter, col_select = st.columns([1, 2])
    with col_filter:
        difficulty_filter = st.selectbox(
            "Filter by Difficulty Level:",
            ["All Levels (1-25)", "Beginner Level (Q1-Q8)", "Intermediate Level (Q9-Q16)", "Advanced Level (Q17-Q25)"]
        )

    # Filter list
    if "Beginner" in difficulty_filter:
        filtered_questions = [q for q in SQL_QUESTIONS if q["difficulty"] == "Beginner"]
    elif "Intermediate" in difficulty_filter:
        filtered_questions = [q for q in SQL_QUESTIONS if q["difficulty"] == "Intermediate"]
    elif "Advanced" in difficulty_filter:
        filtered_questions = [q for q in SQL_QUESTIONS if q["difficulty"] == "Advanced"]
    else:
        filtered_questions = SQL_QUESTIONS

    with col_select:
        q_options = [f"Q{q['id']:02d}: {q['title']} [{q['difficulty']}]" for q in filtered_questions]
        selected_q_idx = st.selectbox("Choose a Question:", range(len(q_options)), format_func=lambda i: q_options[i])
        current_q = filtered_questions[selected_q_idx]

    # Question Details Card
    badge_colors = {
        "Beginner": "#10B981",
        "Intermediate": "#F59E0B",
        "Advanced": "#EF4444"
    }
    badge_bg = badge_colors.get(current_q["difficulty"], "#3B82F6")

    st.markdown(f"""
    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 18px; border-radius: 4px; border-left: 5px solid {badge_bg}; margin: 15px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #0f172a;">Question {current_q['id']}: {current_q['title']}</h3>
            <span style="background: {badge_bg}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;">
                {current_q['difficulty']}
            </span>
        </div>
        <p style="margin: 6px 0; color: #64748b; font-size: 0.9rem;"><strong>Domain Category:</strong> {current_q['category']}</p>
        <div style="margin-top: 10px; font-size: 1.05rem; color: #1e293b; line-height: 1.5; font-weight: 500;">
            {current_q['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SQL Statement Block
    st.subheader("SQL Query Implementation")
    st.code(current_q["sql"], language="sql")

    # Execution controls
    col_exec, col_csv = st.columns([1, 4])
    with col_exec:
        run_btn = st.button("Execute Query", key=f"run_q_{current_q['id']}", type="primary")

    # Execute automatically or on button click
    start_time = time.time()
    try:
        df = execute_query(current_q["sql"])
        elapsed_ms = (time.time() - start_time) * 1000

        st.markdown(f"""
        <div style="display: flex; gap: 15px; margin: 10px 0;">
            <span style="color: #10B981; font-weight: bold;">Query executed successfully</span>
            <span style="color: #64748b;">Latency: <strong>{elapsed_ms:.2f} ms</strong></span>
            <span style="color: #64748b;">Rows returned: <strong>{len(df)}</strong></span>
        </div>
        """, unsafe_allow_html=True)

        # Tabular View
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Download CSV
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Result as CSV",
                data=csv_data,
                file_name=f"cricket_analytics_q{current_q['id']}.csv",
                mime="text/csv",
                key=f"csv_q_{current_q['id']}"
            )

            # Visualizations for specific questions
            qid = current_q["id"]
            if qid == 3:
                st.plotly_chart(create_top_run_scorers_chart(df), use_container_width=True)
            elif qid == 17:
                st.plotly_chart(create_toss_win_chart(df), use_container_width=True)
            elif qid == 18:
                st.plotly_chart(create_bowler_economy_chart(df), use_container_width=True)
            elif qid == 22:
                st.plotly_chart(create_head_to_head_chart(df), use_container_width=True)
            elif qid == 23:
                st.plotly_chart(create_player_form_trend_chart(df), use_container_width=True)

        else:
            st.warning("Query returned 0 rows with current database parameters.")

    except Exception as err:
        st.error(f"Execution Error: {str(err)}")

    # Educational Explanation
    st.subheader("Query Explanation & Techniques")
    st.info(current_q["explanation"])


def render_custom_console():
    st.subheader("Interactive Custom SQL Console")
    st.markdown("Run your own queries directly on the cricket analytics schema.")

    default_custom = "SELECT full_name, country, playing_role FROM players LIMIT 10;"
    custom_sql = st.text_area("Write SQL Query (SELECT only):", value=default_custom, height=130)

    col_btn, col_help = st.columns([1, 4])
    with col_btn:
        exec_custom = st.button("Run Custom SQL", type="primary")

    with st.expander("Available Tables & Schema Reference"):
        st.markdown("""
        * **teams** (`team_id`, `team_name`, `team_code`, `country`)
        * **players** (`player_id`, `team_id`, `full_name`, `country`, `playing_role`, `batting_style`, `bowling_style`, `debut_year`)
        * **venues** (`venue_id`, `venue_name`, `city`, `country`, `capacity`)
        * **series** (`series_id`, `series_name`, `host_country`, `match_type`, `start_date`, `total_matches`)
        * **matches** (`match_id`, `series_id`, `match_description`, `match_type`, `team1_id`, `team2_id`, `venue_id`, `match_date`, `toss_winner_id`, `toss_decision`, `winner_id`, `victory_margin`, `victory_type`, `is_completed`)
        * **player_match_batting** (`stat_id`, `match_id`, `player_id`, `team_id`, `innings_number`, `batting_position`, `runs_scored`, `balls_faced`, `fours`, `sixes`, `strike_rate`, `is_out`)
        * **player_match_bowling** (`stat_id`, `match_id`, `player_id`, `team_id`, `innings_number`, `overs_bowled`, `maidens`, `runs_conceded`, `wickets_taken`, `economy_rate`)
        * **player_match_fielding** (`stat_id`, `match_id`, `player_id`, `catches`, `stumpings`, `run_outs`)
        * **player_career_stats** (`stat_id`, `player_id`, `format`, `matches_played`, `total_runs`, `batting_avg`, `strike_rate`, `centuries`, `fifties`, `highest_score`, `wickets_taken`, `bowling_avg`, `economy_rate`, `catches`, `stumpings`)
        """)

    if exec_custom and custom_sql.strip():
        sql_clean = custom_sql.strip().lower()
        if not sql_clean.startswith("select") and not sql_clean.startswith("with"):
            st.error("For database safety, the console only allows `SELECT` and `WITH` analytical queries. Use the CRUD page for mutations.")
            return

        try:
            t0 = time.time()
            df_custom = execute_query(custom_sql)
            t_diff = (time.time() - t0) * 1000

            st.success(f"Execution finished in {t_diff:.2f} ms ({len(df_custom)} rows)")
            st.dataframe(df_custom, use_container_width=True, hide_index=True)

            csv = df_custom.to_csv(index=False).encode("utf-8")
            st.download_button("Download Results CSV", csv, "custom_query_results.csv", "text/csv")
        except Exception as e:
            st.error(f"SQL Error: {str(e)}")

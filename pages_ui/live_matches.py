"""
Live Scores & Matches view for Cricbuzz LiveStats.
Designed to mimic the exact Cricbuzz card layout and live scorecards.
"""

import streamlit as st
import pandas as pd
from utils.cricbuzz_api import CricbuzzAPIClient


def render_live_matches():
    client = CricbuzzAPIClient()
    matches = client.get_live_and_recent_matches()

    if not matches:
        st.warning("No matches available from Cricbuzz API.")
        return

    # Section Title
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 15px 0 10px 0;">
        <h3 style="margin: 0; color: #1e293b; font-weight: 800;">Featured Matches</h3>
        <span style="font-size: 13px; color: #009270; font-weight: 700;">LIVE UPDATES &bull; RAPIDAPI</span>
    </div>
    """, unsafe_allow_html=True)


    # Render Match Cards Grid (3 cards per row like Cricbuzz)
    cols = st.columns(3)
    for idx, m in enumerate(matches[:6]):
        col = cols[idx % 3]
        with col:
            t1 = m.get("team1", {})
            t2 = m.get("team2", {})
            t1_name = t1.get('code', t1.get('name', 'T1'))
            t2_name = t2.get('code', t2.get('name', 'T2'))
            t1_score = t1.get("scores", ["-"])[0]
            t2_score = t2.get("scores", ["-"])[0]
            status_txt = m.get("status", "Match in Progress")
            series_name = m.get("series", "International Series")
            m_format = m.get("format", "T20I")

            # Cricbuzz status styling: blue for match results, red for live/target
            st_lower = status_txt.lower()
            if any(w in st_lower for w in ["won by", "won the", "tied", "drawn", "complete"]):
                status_color = "#1866db"
            else:
                status_color = "#cb202d"

            # Authentic Cricbuzz Match Card
            st.markdown(f"""
            <div class="cb-match-card">
                <div style="padding: 12px 14px 10px 14px;">
                    <div class="cb-card-header">
                        <span title="{series_name}">{series_name[:28]}</span>
                        <span class="cb-format-pill">{m_format}</span>
                    </div>
                    <div class="cb-team-row">
                        <span>{t1_name}</span>
                        <span class="cb-team-score">{t1_score}</span>
                    </div>
                    <div class="cb-team-row">
                        <span>{t2_name}</span>
                        <span class="cb-team-score">{t2_score}</span>
                    </div>
                    <div class="cb-status-text" style="color: {status_color};">
                        {status_txt}
                    </div>
                </div>
                <div class="cb-card-footer">
                    <a href="?page=Rankings" target="_self">POINTS TABLE</a>
                    <a href="?page=Schedule" target="_self">SCHEDULE</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Match Detail Inspector
    st.markdown("### Official Match Scorecard & Ball Commentary")
    match_titles = [f"{m['title']} ({m['format']}) - {m.get('series', '')[:30]}" for m in matches]
    selected_idx = st.selectbox(
        "Select match to inspect detailed scorecard:",
        range(len(match_titles)),
        format_func=lambda i: match_titles[i]
    )
    sel_match = matches[selected_idx]
    mid = sel_match["match_id"]

    # Match header summary
    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 8px; border-left: 5px solid #009270; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #0f172a;">{sel_match['title']}</h3>
            <span style="background: #009270; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;">
                Match ID: {mid}
            </span>
        </div>
        <p style="color: #64748b; margin: 6px 0;">
            <strong>Series:</strong> {sel_match['series']} &bull; 
            <strong>Venue:</strong> {sel_match.get('venue', 'Stadium')}
        </p>
        <p style="color: #cb202d; font-weight: 700; margin: 4px 0 0 0;">
            {sel_match['status']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for Scorecard vs Commentary
    tab_sc, tab_comm = st.tabs(["Scorecard", "Ball-by-Ball Commentary"])

    with tab_sc:
        with st.spinner("Fetching official scorecard from Cricbuzz API..."):
            scorecard_data = client.get_match_scorecard(mid)

        innings_list = scorecard_data.get("innings", [])
        if innings_list:
            inn_subtabs = st.tabs([f"Innings {i+1}: {inn['team']} ({inn.get('score', 0)}/{inn.get('wickets', 0)})" for i, inn in enumerate(innings_list)])
            for i, inn in enumerate(innings_list):
                with inn_subtabs[i]:
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        st.metric("Total Score", f"{inn.get('score', 0)} / {inn.get('wickets', 0)}", f"{inn.get('overs', 0)} Overs")
                    with c_s2:
                        st.metric("Run Rate", f"{inn.get('runrate', 0.0)} RPO")

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        st.markdown("##### Batting Card")
                        bats = inn.get("batsmen", [])
                        if bats:
                            df_b = pd.DataFrame(bats)
                            df_b.rename(columns={
                                "name": "Batsman", "runs": "R", "balls": "B",
                                "fours": "4s", "sixes": "6s", "sr": "SR", "dismissal": "Dismissal"
                            }, inplace=True)
                            st.dataframe(df_b, use_container_width=True, hide_index=True)
                        else:
                            st.info("No batting entries recorded.")

                    with col_b2:
                        st.markdown("##### Bowling Card")
                        bowls = inn.get("bowlers", [])
                        if bowls:
                            df_bw = pd.DataFrame(bowls)
                            df_bw.rename(columns={
                                "name": "Bowler", "overs": "O", "maidens": "M",
                                "runs": "R", "wickets": "W", "econ": "Econ"
                            }, inplace=True)
                            st.dataframe(df_bw, use_container_width=True, hide_index=True)
                        else:
                            st.info("No bowling figures recorded.")
        else:
            st.info("Live scorecard is being updated by Cricbuzz scorers.")

    with tab_comm:
        with st.spinner("Streaming commentary from Cricbuzz API..."):
            comm_lines = client.get_match_commentary(mid)

        if comm_lines:
            for line in comm_lines[:20]:
                is_wkt = any(w in line.lower() for w in ["out", "wicket", "clean bowled", "caught", "lbw"])
                is_bnd = any(b in line.lower() for b in ["four", "six", "boundary", "maximum"])
                border_c = "#cb202d" if is_wkt else ("#009270" if is_bnd else "#cbd5e1")
                bg_c = "#fff5f5" if is_wkt else ("#f0fdf4" if is_bnd else "#ffffff")

                st.markdown(f"""
                <div style="padding: 10px 14px; margin-bottom: 8px; background-color: {bg_c}; border-radius: 6px; border-left: 4px solid {border_c}; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                    <span style="color: #1e293b; font-size: 13px; font-weight: {'700' if is_wkt or is_bnd else '400'};">{line}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Live commentary will stream as deliveries occur.")

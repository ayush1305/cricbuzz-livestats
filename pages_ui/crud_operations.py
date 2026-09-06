"""
CRUD Operations view for Cricbuzz LiveStats.
Form-based data management for Players and Matches.
"""

import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, execute_statement


def render_crud_operations():
    st.title("Database CRUD Management Center")
    st.markdown("Perform Create, Read, Update, and Delete operations on relational cricket entities with validation.")

    crud_tab1, crud_tab2 = st.tabs(["Player Management", "Match Management"])

    with crud_tab1:
        render_player_crud()

    with crud_tab2:
        render_match_crud()


def render_player_crud():
    st.subheader("Manage Player Records")
    action = st.radio("Operation:", ["View & Search Players", "Add New Player", "Update Player", "Delete Player"], horizontal=True)

    # Fetch reference teams
    try:
        df_teams = execute_query("SELECT team_id, team_name FROM teams ORDER BY team_name ASC")
        team_map = dict(zip(df_teams["team_name"], df_teams["team_id"]))
    except Exception:
        team_map = {}

    # 1. READ / SEARCH
    if action == "View & Search Players":
        col_search, col_role = st.columns([2, 1])
        with col_search:
            search_name = st.text_input("Search by Player Name:")
        with col_role:
            role_filter = st.selectbox("Filter Role:", ["All Roles", "Batsman", "Bowler", "All-rounder", "Wicket-keeper"])

        query = """
        SELECT
            p.player_id,
            p.full_name,
            t.team_name,
            p.country,
            p.playing_role,
            p.batting_style,
            p.bowling_style,
            p.debut_year
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE 1=1
        """
        params = {}
        if search_name.strip():
            query += " AND p.full_name LIKE :name"
            params["name"] = f"%{search_name.strip()}%"
        if role_filter != "All Roles":
            query += " AND p.playing_role = :role"
            params["role"] = role_filter

        query += " ORDER BY p.player_id DESC;"

        df_players = execute_query(query, params)
        st.caption(f"Showing {len(df_players)} player records")
        st.dataframe(df_players, use_container_width=True, hide_index=True)

    # 2. CREATE
    elif action == "Add New Player":
        st.markdown("#### Register a New Player")
        with st.form("add_player_form"):
            name = st.text_input("Full Name *", placeholder="e.g. Jasprit Bumrah")
            col_t, col_c = st.columns(2)
            with col_t:
                sel_team = st.selectbox("National Team *", list(team_map.keys()))
            with col_c:
                country = st.text_input("Country *", value=sel_team)

            col_r, col_d = st.columns(2)
            with col_r:
                role = st.selectbox("Playing Role *", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
            with col_d:
                debut = st.number_input("Debut Year", min_value=1950, max_value=2030, value=2024)

            col_bat, col_bowl = st.columns(2)
            with col_bat:
                bat_style = st.selectbox("Batting Style", ["Right-hand bat", "Left-hand bat"])
            with col_bowl:
                bowl_style = st.selectbox("Bowling Style", [
                    "Right-arm fast", "Right-arm fast-medium", "Right-arm offbreak",
                    "Right-arm legbreak", "Left-arm fast", "Slow left-arm orthodox", "None"
                ])

            submit_add = st.form_submit_button("Save Player to Database", type="primary")

        if submit_add:
            if not name.strip():
                st.error("Player name cannot be empty.")
            else:
                try:
                    # Determine next ID
                    df_max = execute_query("SELECT COALESCE(MAX(player_id), 0) + 1 AS next_id FROM players")
                    new_id = int(df_max["next_id"][0])
                    team_id = team_map.get(sel_team)

                    stmt = """
                    INSERT INTO players (player_id, team_id, full_name, country, playing_role, batting_style, bowling_style, debut_year)
                    VALUES (:pid, :tid, :name, :country, :role, :bat, :bowl, :debut)
                    """
                    execute_statement(stmt, {
                        "pid": new_id,
                        "tid": team_id,
                        "name": name.strip(),
                        "country": country.strip(),
                        "role": role,
                        "bat": bat_style,
                        "bowl": None if bowl_style == "None" else bowl_style,
                        "debut": int(debut)
                    })
                    st.success(f"Player '{name}' successfully registered with ID #{new_id}!")
                except Exception as e:
                    st.error(f"Failed to create player: {str(e)}")

    # 3. UPDATE
    elif action == "Update Player":
        st.markdown("#### Modify Player Details")
        df_all = execute_query("SELECT player_id, full_name FROM players ORDER BY full_name ASC")
        if df_all.empty:
            st.warning("No players found to update.")
            return

        player_options = {f"{row['full_name']} (ID: {row['player_id']})": row['player_id'] for _, row in df_all.iterrows()}
        selected_player_str = st.selectbox("Select Player to Edit:", list(player_options.keys()))
        target_pid = player_options[selected_player_str]

        curr = execute_query("SELECT * FROM players WHERE player_id = :pid", {"pid": target_pid}).iloc[0]

        with st.form("update_player_form"):
            up_name = st.text_input("Full Name", value=curr["full_name"])
            col_t, col_c = st.columns(2)
            with col_t:
                team_names = list(team_map.keys())
                curr_team_name = [k for k, v in team_map.items() if v == curr["team_id"]]
                default_team_idx = team_names.index(curr_team_name[0]) if curr_team_name else 0
                up_team = st.selectbox("Team", team_names, index=default_team_idx)
            with col_c:
                up_country = st.text_input("Country", value=curr["country"])

            col_r, col_d = st.columns(2)
            with col_r:
                roles = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
                r_idx = roles.index(curr["playing_role"]) if curr["playing_role"] in roles else 0
                up_role = st.selectbox("Playing Role", roles, index=r_idx)
            with col_d:
                up_debut = st.number_input("Debut Year", min_value=1950, max_value=2030, value=int(curr["debut_year"] or 2020))

            up_bat = st.selectbox("Batting Style", ["Right-hand bat", "Left-hand bat"], index=0 if curr["batting_style"] == "Right-hand bat" else 1)
            up_bowl = st.text_input("Bowling Style", value=curr["bowling_style"] or "None")

            submit_update = st.form_submit_button("Update Player Record", type="primary")

        if submit_update:
            try:
                stmt = """
                UPDATE players
                SET full_name = :name,
                    team_id = :tid,
                    country = :country,
                    playing_role = :role,
                    batting_style = :bat,
                    bowling_style = :bowl,
                    debut_year = :debut
                WHERE player_id = :pid
                """
                execute_statement(stmt, {
                    "pid": target_pid,
                    "name": up_name.strip(),
                    "tid": team_map.get(up_team),
                    "country": up_country.strip(),
                    "role": up_role,
                    "bat": up_bat,
                    "bowl": None if up_bowl == "None" else up_bowl.strip(),
                    "debut": int(up_debut)
                })
                st.success(f"Record for '{up_name}' updated successfully!")
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

    # 4. DELETE
    elif action == "Delete Player":
        st.markdown("#### Remove Player Record")
        df_all = execute_query("SELECT player_id, full_name, country FROM players ORDER BY full_name ASC")
        if df_all.empty:
            st.warning("No players available to delete.")
            return

        del_options = {f"{row['full_name']} ({row['country']}, ID: {row['player_id']})": row['player_id'] for _, row in df_all.iterrows()}
        selected_del = st.selectbox("Select Player to Delete:", list(del_options.keys()))
        target_pid = del_options[selected_del]

        st.warning("Deleting this player will remove associated player records. This operation cannot be undone.")
        confirm_del = st.checkbox("I understand and confirm deletion of this player.")

        if st.button("Permanently Delete Player", type="primary", disabled=not confirm_del):
            try:
                execute_statement("DELETE FROM players WHERE player_id = :pid", {"pid": target_pid})
                st.success("Player deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Deletion failed: {str(e)}")


def render_match_crud():
    st.subheader("Manage Match Records")
    m_action = st.radio("Match Action:", ["View Matches", "Schedule New Match", "Delete Match"], horizontal=True)

    if m_action == "View Matches":
        df_m = execute_query("""
        SELECT
            m.match_id,
            m.match_description,
            m.match_type,
            t1.team_code AS team_1,
            t2.team_code AS team_2,
            v.venue_name,
            m.match_date,
            tw.team_code AS winner,
            m.victory_margin,
            m.victory_type
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN teams tw ON m.winner_id = tw.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        ORDER BY m.match_date DESC
        """)
        st.dataframe(df_m, use_container_width=True, hide_index=True)

    elif m_action == "Schedule New Match":
        df_teams = execute_query("SELECT team_id, team_name FROM teams ORDER BY team_name ASC")
        df_venues = execute_query("SELECT venue_id, venue_name FROM venues ORDER BY venue_name ASC")
        team_map = dict(zip(df_teams["team_name"], df_teams["team_id"]))
        venue_map = dict(zip(df_venues["venue_name"], df_venues["venue_id"]))

        with st.form("new_match_form"):
            desc = st.text_input("Match Description *", placeholder="e.g. IND vs AUS 1st ODI 2025")
            m_type = st.selectbox("Match Type", ["Test", "ODI", "T20I"])
            col1, col2 = st.columns(2)
            with col1:
                t1 = st.selectbox("Team 1", list(team_map.keys()), index=0)
            with col2:
                t2 = st.selectbox("Team 2", list(team_map.keys()), index=min(1, len(team_map)-1))

            ven = st.selectbox("Venue", list(venue_map.keys()))
            m_date = st.date_input("Match Date")
            submit_match = st.form_submit_button("Save Match", type="primary")

        if submit_match:
            if t1 == t2:
                st.error("Team 1 and Team 2 cannot be the same.")
            elif not desc.strip():
                st.error("Match description is required.")
            else:
                try:
                    df_max = execute_query("SELECT COALESCE(MAX(match_id), 0) + 1 AS next_id FROM matches")
                    new_mid = int(df_max["next_id"][0])
                    stmt = """
                    INSERT INTO matches (match_id, match_description, match_type, team1_id, team2_id, venue_id, match_date, is_completed)
                    VALUES (:mid, :desc, :mtype, :t1, :t2, :vid, :mdate, 0)
                    """
                    execute_statement(stmt, {
                        "mid": new_mid,
                        "desc": desc.strip(),
                        "mtype": m_type,
                        "t1": team_map[t1],
                        "t2": team_map[t2],
                        "vid": venue_map[ven],
                        "mdate": m_date
                    })
                    st.success(f"Match scheduled successfully with ID #{new_mid}!")
                except Exception as e:
                    st.error(f"Failed to create match: {str(e)}")

    elif m_action == "Delete Match":
        df_all_m = execute_query("SELECT match_id, match_description, match_date FROM matches ORDER BY match_date DESC")
        if df_all_m.empty:
            st.warning("No matches available to delete.")
            return

        m_dict = {f"{row['match_description']} ({row['match_date']}, ID: {row['match_id']})": row['match_id'] for _, row in df_all_m.iterrows()}
        sel_m = st.selectbox("Select Match to Delete:", list(m_dict.keys()))
        target_mid = m_dict[sel_m]

        if st.button("Delete Selected Match", type="primary"):
            try:
                execute_statement("DELETE FROM matches WHERE match_id = :mid", {"mid": target_mid})
                st.success("Match deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {str(e)}")

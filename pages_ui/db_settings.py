"""
SQL Database Connection Center for Cricbuzz LiveStats.
Provides step-by-step interactive connection management for SQLite, PostgreSQL, and MySQL.
"""

import os
import streamlit as st
from utils.db_connection import (
    get_database_url,
    test_connection,
    get_default_db_path,
    get_engine,
    execute_query
)
from database.sync_api_data import sync_real_data


def render_db_settings():
    st.markdown("""
    <div style="background: #ffffff; padding: 20px; border-radius: 8px; border-left: 5px solid #009270; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <h2 style="color: #009270; margin: 0; font-weight: 900;">🔌 SQL Database Connection Center</h2>
        <p style="color: #64748b; margin: 6px 0 0 0; font-size: 15px;">
            Cricbuzz LiveStats is database-agnostic. You can run locally on <strong>SQLite (Ready Out-of-the-Box)</strong>, or connect to your external <strong>PostgreSQL</strong> or <strong>MySQL</strong> servers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Current Status Banner
    curr_url = get_database_url()
    active_type = "SQLite" if "sqlite" in curr_url else ("PostgreSQL" if "postgresql" in curr_url else "MySQL")

    try:
        team_count = execute_query("SELECT COUNT(*) as c FROM teams")['c'][0]
        player_count = execute_query("SELECT COUNT(*) as c FROM players")['c'][0]
        match_count = execute_query("SELECT COUNT(*) as c FROM matches")['c'][0]
    except Exception:
        team_count, player_count, match_count = 0, 0, 0

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Active SQL Engine", active_type)
    with col_s2:
        st.metric("Teams in DB", team_count)
    with col_s3:
        st.metric("Players in DB", player_count)
    with col_s4:
        st.metric("Matches in DB", match_count)

    st.markdown("---")

    # Connection Tabs
    tab_sqlite, tab_pg, tab_mysql, tab_guide = st.tabs([
        "📁 Option 1: SQLite (Current / Zero-Config)",
        "🐘 Option 2: Connect PostgreSQL",
        "🐬 Option 3: Connect MySQL",
        "📖 Step-by-Step Connection Guide"
    ])

    # 1. SQLITE
    with tab_sqlite:
        st.markdown("### 📁 SQLite Database Configuration")
        st.info("💡 **Zero Configuration Required**: SQLite requires no background service or password. Data is stored directly in your workspace.")
        
        default_p = get_default_db_path()
        st.code(f"Active SQLite File: {default_p}", language="text")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔌 Test SQLite Connection", type="primary"):
                ok, msg = test_connection(f"sqlite:///{default_p}")
                if ok:
                    st.success("✅ SQLite database is connected and fully operational!")
                else:
                    st.error(f"❌ {msg}")
        with c2:
            if st.button("🔄 Re-Sync Live Cricbuzz Data to SQLite"):
                with st.spinner("Fetching latest real-time records from Cricbuzz API..."):
                    sync_real_data(f"sqlite:///{default_p}")
                    st.success("🎉 SQLite database successfully updated with real Cricbuzz data!")
                    st.rerun()

    # 2. POSTGRESQL
    with tab_pg:
        st.markdown("### 🐘 Connect to an External PostgreSQL Database")
        st.markdown("Enter your PostgreSQL database credentials below to switch your connection:")

        with st.form("pg_connect_form"):
            col1, col2 = st.columns(2)
            with col1:
                pg_host = st.text_input("PostgreSQL Host:", value="localhost")
                pg_port = st.text_input("Port:", value="5432")
                pg_db = st.text_input("Database Name:", value="cricket_analytics")
            with col2:
                pg_user = st.text_input("Username:", value="postgres")
                pg_pwd = st.text_input("Password:", type="password", value="")

            pg_conn_url = f"postgresql+psycopg2://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"
            st.caption(f"Target URL: `postgresql+psycopg2://{pg_user}:****@{pg_host}:{pg_port}/{pg_db}`")

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                test_pg = st.form_submit_button("🔌 Test PostgreSQL Connection", type="primary")
            with c_btn2:
                sync_pg = st.form_submit_button("⚡ Connect & Sync Real Data to PostgreSQL")

        if test_pg:
            ok, msg = test_connection(pg_conn_url)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

        if sync_pg:
            ok, msg = test_connection(pg_conn_url)
            if not ok:
                st.error(f"Cannot sync: {msg}. Please ensure your database server is running.")
            else:
                with st.spinner("Initializing schema and syncing real Cricbuzz API data into PostgreSQL..."):
                    try:
                        sync_real_data(pg_conn_url)
                        os.environ["DATABASE_URL"] = pg_conn_url
                        get_engine(pg_conn_url)
                        st.success("🎉 PostgreSQL successfully connected and populated with real Cricbuzz records!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sync failed: {str(e)}")

    # 3. MYSQL
    with tab_mysql:
        st.markdown("### 🐬 Connect to an External MySQL Database")
        st.markdown("Enter your MySQL credentials to connect:")

        with st.form("mysql_connect_form"):
            col1, col2 = st.columns(2)
            with col1:
                my_host = st.text_input("MySQL Host:", value="localhost")
                my_port = st.text_input("Port:", value="3306")
                my_db = st.text_input("Database Name:", value="cricket_analytics")
            with col2:
                my_user = st.text_input("Username:", value="root")
                my_pwd = st.text_input("Password:", type="password", value="")

            my_conn_url = f"mysql+pymysql://{my_user}:{my_pwd}@{my_host}:{my_port}/{my_db}"
            st.caption(f"Target URL: `mysql+pymysql://{my_user}:****@{my_host}:{my_port}/{my_db}`")

            c_m1, c_m2 = st.columns(2)
            with c_m1:
                test_my = st.form_submit_button("🔌 Test MySQL Connection", type="primary")
            with c_m2:
                sync_my = st.form_submit_button("⚡ Connect & Sync Real Data to MySQL")

        if test_my:
            ok, msg = test_connection(my_conn_url)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

        if sync_my:
            ok, msg = test_connection(my_conn_url)
            if not ok:
                st.error(f"Cannot sync: {msg}. Please ensure your MySQL server is running.")
            else:
                with st.spinner("Initializing schema and syncing real Cricbuzz data into MySQL..."):
                    try:
                        sync_real_data(my_conn_url)
                        os.environ["DATABASE_URL"] = my_conn_url
                        get_engine(my_conn_url)
                        st.success("🎉 MySQL successfully connected and populated with real Cricbuzz records!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sync failed: {str(e)}")

    # 4. STEP-BY-STEP INSTRUCTIONS GUIDE
    with tab_guide:
        st.markdown("""
        ### 📖 How to Connect Any SQL Database to Cricbuzz LiveStats

        #### Method A: SQLite (Default - Ready Right Now)
        You do not need to install any database server. The application is already connected to:
        `database/cricket_analytics.db`
        - All 25 SQL queries run directly on this database.
        - SQLite has been enhanced with a custom Python `STDDEV` statistical function for windowed analytics.

        ---

        #### Method B: PostgreSQL (Step-by-Step)
        1. **Start PostgreSQL** on your computer.
        2. Open your PostgreSQL terminal (psql or pgAdmin) and create a database:
           ```sql
           CREATE DATABASE cricket_analytics;
           ```
        3. Open the **Option 2: Connect PostgreSQL** tab above.
        4. Enter your host (`localhost`), port (`5432`), user (`postgres`), and password.
        5. Click **⚡ Connect & Sync Real Data to PostgreSQL**.
        6. The platform will automatically create all tables, indexes, and sync real Cricbuzz matches into PostgreSQL!

        ---

        #### Method C: MySQL (Step-by-Step)
        1. **Start MySQL Server** (or XAMPP / MySQL Workbench).
        2. Create the database:
           ```sql
           CREATE DATABASE cricket_analytics;
           ```
        3. Open the **Option 3: Connect MySQL** tab above.
        4. Enter your MySQL port (`3306`), user (`root`), and password.
        5. Click **⚡ Connect & Sync Real Data to MySQL**.
        """)

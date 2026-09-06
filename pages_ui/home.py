"""
Home page view for Cricbuzz LiveStats.
"""

import streamlit as st
import pandas as pd
from utils.db_connection import execute_query, get_engine
from utils.cricbuzz_api import CricbuzzAPIClient


def render_home():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #009270 0%, #005a44 100%); padding: 24px; border-radius: 8px; color: white; margin-bottom: 24px; box-shadow: 0 2px 5px rgba(0,0,0,0.08);">
        <h1 style="margin: 0; color: #FFFFFF; font-weight: 900;">Cricbuzz LiveStats Platform</h1>
        <p style="margin: 8px 0 0 0; font-size: 1.15rem; color: #E6F4EA;">
            Cricket intelligence engine integrating live Cricbuzz REST API feeds with relational SQL analytics, 25 production queries, and full CRUD operations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick System Metrics
    try:
        t_count = execute_query("SELECT COUNT(*) as c FROM teams")['c'][0]
        p_count = execute_query("SELECT COUNT(*) as c FROM players")['c'][0]
        m_count = execute_query("SELECT COUNT(*) as c FROM matches")['c'][0]
        s_count = execute_query("SELECT COUNT(*) as c FROM series")['c'][0]
    except Exception:
        t_count, p_count, m_count, s_count = 0, 0, 0, 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Teams Enrolled", t_count)
    with col2:
        st.metric("Players Profiled", p_count)
    with col3:
        st.metric("Matches Recorded", m_count)
    with col4:
        st.metric("Series & Tournaments", s_count)

    st.markdown("---")

    # Business Use Cases
    st.subheader("Industry & Business Use Cases")
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1:
        st.info("""
        **1. Sports Media & Broadcasting**
        * Real-time match commentary feeds
        * Pre-match head-to-head records
        * Milestone tracking (100s, 5w hauls)
        """)
        st.success("""
        **4. Educational Institutions**
        * Real-world SQL practice on live data
        * CTEs, Window Functions & Joins
        * Database design and relational CRUD
        """)

    with col_u2:
        st.warning("""
        **2. Fantasy Cricket Platforms**
        * Player recent form momentum
        * Venue-specific bowling economics
        * Clutch performance index
        """)
        st.error("""
        **5. Prediction & Match Odds**
        * Toss advantage probability metrics
        * Defending vs Chasing win rates
        * Player consistency via standard deviation
        """)

    with col_u3:
        st.info("""
        **3. Cricket Analytics Firms**
        * Multi-format player evaluation
        * Batting partnership synergy ranking
        * Quarterly career trajectory modeling
        """)
        st.markdown("""
        <div style="background-color: #1e293b; padding: 14px; border-radius: 8px; border-left: 4px solid #38bdf8;">
            <strong style="color: #38bdf8;">Live Engine Status</strong><br>
            <small style="color: #cbd5e1;">Connected to active SQL engine with instant execution & REST API sync.</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # SQL Connection Guide
    st.subheader("How to Connect Your SQL Database")
    st.markdown("""
    Cricbuzz LiveStats is **database-agnostic** and operates seamlessly on **SQLite**, **PostgreSQL**, and **MySQL**.
    Use the **DB Settings** tab in the navigation bar or edit your `.env` configuration file.
    """)

    tabs = st.tabs(["SQLite (Default Zero-Config)", "PostgreSQL", "MySQL"])

    with tabs[0]:
        st.markdown("""
        **Zero setup required!** Cricbuzz LiveStats automatically generates and maintains a local SQLite database at:
        `database/cricket_analytics.db`
        - Custom `STDDEV` statistical functions are automatically injected into SQLite.
        - Full ACID transactions, foreign keys, and indexes are enabled out of the box.
        - You can reset or re-seed the sample data anytime with the **Reset / Re-Seed Database** button in DB Settings.
        """)

    with tabs[1]:
        st.markdown("""
        To connect to an external PostgreSQL server:
        1. Ensure your PostgreSQL server is running and create the database:
        ```sql
        CREATE DATABASE cricket_analytics;
        ```
        2. Set the environment variables in `.env` (or via the **DB Settings** page):
        ```env
        DB_TYPE=postgresql
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=cricket_analytics
        DB_USER=postgres
        DB_PASSWORD=your_secure_password
        ```
        Or supply the direct SQLAlchemy connection URL:
        ```
        DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/cricket_analytics
        ```
        3. Click **Initialize Schema & Seed** to migrate tables and load data into Postgres!
        """)

    with tabs[2]:
        st.markdown("""
        To connect to an external MySQL server:
        1. Create your database:
        ```sql
        CREATE DATABASE cricket_analytics;
        ```
        2. Set the environment variables in `.env` (or via **DB Settings**):
        ```env
        DB_TYPE=mysql
        DB_HOST=localhost
        DB_PORT=3306
        DB_NAME=cricket_analytics
        DB_USER=root
        DB_PASSWORD=your_secure_password
        ```
        Or supply the direct SQLAlchemy connection URL:
        ```
        DATABASE_URL=mysql+pymysql://root:password@localhost:3306/cricket_analytics
        ```
        3. Click **Initialize Schema & Seed** to populate MySQL.
        """)

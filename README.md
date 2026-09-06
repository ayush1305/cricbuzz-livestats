# Cricbuzz LiveStats - Cricket Analytics & SQL Dashboard

A comprehensive cricket analytics web application integrating real-time Cricbuzz API data with a relational SQL database (SQLite, PostgreSQL, MySQL), featuring interactive visualizations, full CRUD data management, and an execution engine for 25 SQL practice questions across Beginner, Intermediate, and Advanced tiers.

---

## Key Features

1. **Live Match Intelligence**:
   - Real-time match scores, ball-by-ball commentary, and match status.
   - Live Batsmen scorecards (Runs, Balls, 4s, 6s, Strike Rate) and Bowling figures (Overs, Maidens, Runs, Wickets, Economy).
   - Seamless RapidAPI Cricbuzz integration with a built-in high-fidelity **Simulator Mode** when offline or API quota is exceeded.

2. **Top Player Stats & Global Leaderboards**:
   - Format-specific leaderboards (Test, ODI, T20I).
   - Top run scorers, leading wicket-takers, and all-round rating matrices.
   - Interactive Plotly visualizations (bar charts, scatter matrices, radar views).

3. **25 Production-Grade SQL Practice Questions**:
   - Categorized into **Beginner (Q1-Q8)**, **Intermediate (Q9-Q16)**, and **Advanced (Q17-Q25)**.
   - Live query runner with execution latency benchmarking in milliseconds.
   - One-click CSV export of query results.
   - Plain-English explanations of underlying database concepts (CTEs, Window Functions, Self-Joins, Conditional Pivots).
   - **Interactive Custom SQL Console**: Allows users to write and execute any arbitrary `SELECT` or `WITH` queries directly on the database.

4. **Relational CRUD Operations**:
   - Form-based UI for managing `players` and `matches`.
   - Create, Read, Update, and Delete records with validation and foreign key integrity.

5. **Database-Agnostic Centralized Connection**:
   - Centralized handler in `utils/db_connection.py`.
   - Seamless support for **SQLite** (default zero-config), **PostgreSQL**, and **MySQL**.
   - Custom `STDDEV` statistical functions polyfilled on SQLite so complex analytical queries execute cross-platform.

---

## Project Directory Structure

```text
cricbuzz_livestats/
├── app.py                          # Main Streamlit web application
├── main.py                         # Application alias entrypoint
├── requirements.txt                # Python dependencies list
├── .env.example                    # Template environment file
├── README.md                       # Complete documentation & SQL setup guide
├── database/
│   ├── schema.sql                  # Relational DDL (teams, players, venues, matches, stats)
│   ├── seed_data.py                # Comprehensive multi-year realistic dataset populator
│   ├── queries.sql                 # 25 commented SQL queries file
│   └── cricket_analytics.db        # SQLite database (auto-created upon startup)
├── utils/
│   ├── __init__.py
│   ├── db_connection.py            # Centralized database engine & connection manager
│   ├── cricbuzz_api.py             # Cricbuzz RapidAPI client fetching live matches, scorecards & comms
│   ├── sql_catalog.py              # Catalog of 25 SQL practice questions & explanations
│   └── visualizer.py               # Interactive Plotly chart generators
├── pages_ui/
│   ├── home.py                     # Home & architecture overview
│   ├── live_matches.py             # Live scorecards and commentary stream
│   ├── top_stats.py                # Leaderboards and player performance charts
│   ├── sql_analytics.py            # 25 questions execution engine + Custom SQL Console
│   ├── crud_operations.py          # Form-based Player and Match CRUD operations
│   └── db_settings.py              # Database switcher (SQLite/Postgres/MySQL) & API settings
└── tests/
    └── test_queries.py             # Automated test verifying all 25 queries execute cleanly
```

---

## Quick Start Guide

### 1. Prerequisites & Dependencies
Ensure Python 3.9+ is installed. Install required packages:
```bash
pip install -r requirements.txt
```

### 2. Launching the Application
Run the Streamlit application:
```bash
streamlit run app.py
```
Or alternatively:
```bash
python main.py
```

The web dashboard will open automatically in your default browser at `http://localhost:8501`.

---

## How to Connect Your SQL Database

Cricbuzz LiveStats supports **SQLite**, **PostgreSQL**, and **MySQL**.

### Option A: SQLite (Default Zero-Configuration)
- No database server installation is required.
- On first launch, the application automatically creates `database/cricket_analytics.db` and populates it with realistic international cricket records.
- SQLite is injected with a custom `STDDEV` aggregate function in Python so that advanced statistical queries (like Q19 and Q23) execute natively.

---

### Option B: PostgreSQL
1. **Create the database in PostgreSQL:**
   ```sql
   CREATE DATABASE cricket_analytics;
   ```
2. **Configure via `.env` file:**
   Create a `.env` file in the project root:
   ```env
   DB_TYPE=postgresql
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=cricket_analytics
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```
   Or set the direct SQLAlchemy connection URL:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/cricket_analytics
   ```
3. **Migrate & Seed:**
   - In the Streamlit app, navigate to **DB & API Settings**.
   - Select **PostgreSQL**, enter your credentials, and click **Test Connection**.
   - Click **Reset & Re-Seed Database** to build tables and load data into PostgreSQL.

---

### Option C: MySQL
1. **Create the database in MySQL:**
   ```sql
   CREATE DATABASE cricket_analytics;
   ```
2. **Configure via `.env` file:**
   ```env
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=cricket_analytics
   DB_USER=root
   DB_PASSWORD=your_password
   ```
   Or set the SQLAlchemy connection URL:
   ```env
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/cricket_analytics
   ```
3. **Migrate & Seed:**
   - Navigate to **DB & API Settings** in the app.
   - Click **Test Connection**, then click **Reset & Re-Seed Database**.

---

## Configuring Cricbuzz RapidAPI Key

1. Sign up for free at [RapidAPI Cricbuzz Cricket API](https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/).
2. Copy your RapidAPI Key.
3. Either:
   - Enter it in the **DB & API Settings** page under the **RapidAPI Cricbuzz Key** tab.
   - Or set `RAPIDAPI_KEY=your_key_here` in your `.env` file.
4. The API key connects directly to the live Cricbuzz database for streaming live matches, scorecards, and player statistics.

---

## Summary of the 25 SQL Practice Questions

| # | Question Title | Difficulty | Key SQL Techniques |
|---|---|---|---|
| **Q1** | Indian National Cricket Team Players | Beginner | Basic `WHERE`, `ORDER BY` |
| **Q2** | Matches Played in the Last 30 Days | Beginner | `INNER JOIN`, relative date arithmetic |
| **Q3** | Top 10 Highest Run Scorers in ODI Cricket | Beginner | `JOIN`, `ORDER BY DESC`, `LIMIT 10` |
| **Q4** | Major Venues with Capacity > 50,000 | Beginner | Numerical filter, descending sort |
| **Q5** | Total Match Wins by Team | Beginner | `COUNT()`, `GROUP BY` |
| **Q6** | Player Count by Playing Role | Beginner | Aggregate demographic grouping |
| **Q7** | Highest Batting Score by Format | Beginner | `MAX()` aggregate, `GROUP BY format` |
| **Q8** | Cricket Series Commencing in 2024 | Beginner | Year extraction `strftime('%Y')` |
| **Q9** | All-Rounders with 1000+ Runs & 50+ Wickets | Intermediate | Multi-conditional threshold filtering |
| **Q10** | Details of Last 20 Completed Matches | Intermediate | Multiple joins to `teams` table |
| **Q11** | Player Performance Comparison Across Formats | Intermediate | Conditional aggregation (`CASE WHEN` pivot) |
| **Q12** | Home vs Away Team Performance | Intermediate | Contextual condition `v.country = t.country` |
| **Q13** | Consecutive Batting Partnerships 100+ Runs | Intermediate | Self-join on `b2.position = b1.position + 1` |
| **Q14** | Bowler Venue Mastery (>=3 Matches, >=4 Overs) | Intermediate | Multi-column `GROUP BY`, `HAVING COUNT()` |
| **Q15** | Clutch Players in Close Matches | Intermediate | Pressure scenario criteria (<50 runs/<5 wkts) |
| **Q16** | Annual Batting Evolution Since 2020 | Intermediate | Grouping by player & year, match count threshold |
| **Q17** | Toss Decision Advantage & Win Probability | Advanced | Ratio calculation, grouping by toss decision |
| **Q18** | Economical Bowlers in Limited-Overs | Advanced | Dual threshold filtering in `HAVING` |
| **Q19** | Batsman Scoring Consistency via Standard Dev | Advanced | Statistical dispersion analysis `STDDEV()` |
| **Q20** | Multi-Format Match Count & Average Matrix | Advanced | Cross-tabulation across Test, ODI, and T20I |
| **Q21** | Comprehensive Weighted Performance Ranking | Advanced | CTEs + `DENSE_RANK() OVER (PARTITION BY ...)` |
| **Q22** | Head-to-Head Team Match Prediction | Advanced | Alphabetical team normalization + win percentages |
| **Q23** | Recent Player Form & Momentum Classification | Advanced | `ROW_NUMBER()` windowing + rolling averages |
| **Q24** | Batting Partnership Success Rate & Synergy | Advanced | Partnership pairing + success percentage rank |
| **Q25** | Quarterly Performance Evolution & Career Phase | Advanced | Multi-stage CTEs + `LAG()` time-series delta |

---

## Automated Testing

Run the automated verification suite to test all 25 queries:
```bash
python tests/test_queries.py
```
All 25 queries will be validated against the active database engine, displaying execution latency and returned row counts.


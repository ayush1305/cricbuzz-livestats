"""
SQL Query Catalog for Cricbuzz LiveStats.
Contains all 25 Practice Questions categorized by difficulty with:
- ID, Title, Difficulty, Business Category
- Question formulation in natural language
- Runnable SQL query string
- Educational explanation of SQL techniques (CTEs, Window Functions, Self-Joins, etc.)
"""

from typing import List, Dict, Any

SQL_QUESTIONS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # BEGINNER LEVEL (QUESTIONS 1 - 8)
    # --------------------------------------------------------------------------
    {
        "id": 1,
        "difficulty": "Beginner",
        "category": "Player Profile & Scouting",
        "title": "Indian National Cricket Team Players",
        "question": "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
        "sql": """SELECT
    full_name,
    playing_role,
    batting_style,
    bowling_style
FROM players
WHERE country = 'India'
ORDER BY full_name ASC;""",
        "explanation": "Demonstrates basic filtering with `WHERE country = 'India'` and ordering with `ORDER BY full_name ASC` on the `players` table."
    },
    {
        "id": 2,
        "difficulty": "Beginner",
        "category": "Media & Broadcasting",
        "title": "Matches Played in the Last 30 Days",
        "question": "Show all cricket matches that were played in the last 30 days. Include the match description, both team names, venue name with city, and the match date. Sort by most recent matches first.",
        "sql": """SELECT
    m.match_description,
    t1.team_name AS team_1,
    t2.team_name AS team_2,
    v.venue_name || ' (' || v.city || ')' AS venue_location,
    m.match_date
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.match_date >= DATE('now', '-30 days')
ORDER BY m.match_date DESC;""",
        "explanation": "Illustrates multi-table `INNER JOIN` operations linking matches with team1, team2, and venue, using relative date calculation `DATE('now', '-30 days')`."
    },
    {
        "id": 3,
        "difficulty": "Beginner",
        "category": "Record Books & Hall of Fame",
        "title": "Top 10 Highest Run Scorers in ODI Cricket",
        "question": "List the top 10 highest run scorers in ODI cricket. Show player name, total runs scored, batting average, and number of centuries. Display the highest run scorer first.",
        "sql": """SELECT
    p.full_name AS player_name,
    pcs.total_runs,
    pcs.batting_avg,
    pcs.centuries
FROM player_career_stats pcs
JOIN players p ON pcs.player_id = p.player_id
WHERE pcs.format = 'ODI'
ORDER BY pcs.total_runs DESC
LIMIT 10;""",
        "explanation": "Uses `JOIN`, `WHERE pcs.format = 'ODI'`, and descending sorting with `LIMIT 10` to extract the premier run scorers."
    },
    {
        "id": 4,
        "difficulty": "Beginner",
        "category": "Venue & Infrastructure",
        "title": "Major Venues with Capacity Exceeding 50,000",
        "question": "Display all cricket venues that have a seating capacity of more than 50,000 spectators. Show venue name, city, country, and capacity. Order by largest capacity first.",
        "sql": """SELECT
    venue_name,
    city,
    country,
    capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;""",
        "explanation": "A clean numerical comparison query using `WHERE capacity > 50000` sorted descending."
    },
    {
        "id": 5,
        "difficulty": "Beginner",
        "category": "Team Standings",
        "title": "Total Match Wins by Team",
        "question": "Calculate how many matches each team has won. Show team name and total number of wins. Display teams with most wins first.",
        "sql": """SELECT
    t.team_name,
    COUNT(m.match_id) AS total_wins
FROM teams t
JOIN matches m ON t.team_id = m.winner_id
WHERE m.is_completed = 1
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;""",
        "explanation": "Demonstrates aggregation with `COUNT(m.match_id)` grouped by team identifier."
    },
    {
        "id": 6,
        "difficulty": "Beginner",
        "category": "Squad Composition",
        "title": "Player Count by Playing Role",
        "question": "Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper). Show the role and count of players for each role.",
        "sql": """SELECT
    playing_role,
    COUNT(player_id) AS player_count
FROM players
GROUP BY playing_role
ORDER BY player_count DESC;""",
        "explanation": "Demonstrates `GROUP BY playing_role` to analyze squad demographic distributions."
    },
    {
        "id": 7,
        "difficulty": "Beginner",
        "category": "Format Records",
        "title": "Highest Individual Batting Score by Cricket Format",
        "question": "Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I). Display the format and the highest score for that format.",
        "sql": """SELECT
    m.match_type AS cricket_format,
    MAX(b.runs_scored) AS highest_individual_score
FROM player_match_batting b
JOIN matches m ON b.match_id = m.match_id
GROUP BY m.match_type
ORDER BY highest_individual_score DESC;""",
        "explanation": "Combines `JOIN` with `MAX()` aggregate grouped by cricket match format."
    },
    {
        "id": 8,
        "difficulty": "Beginner",
        "category": "Tournaments & Schedule",
        "title": "Cricket Series Commencing in 2024",
        "question": "Show all cricket series that started in the year 2024. Include series name, host country, match type, start date, and total number of matches planned.",
        "sql": """SELECT
    series_name,
    host_country,
    match_type,
    start_date,
    total_matches
FROM series
WHERE strftime('%Y', start_date) >= '2024'
ORDER BY start_date DESC;""",
        "explanation": "Uses date function `strftime('%Y', start_date) = '2024'` to filter tournaments commencing in calendar year 2024."
    },

    # --------------------------------------------------------------------------
    # INTERMEDIATE LEVEL (QUESTIONS 9 - 16)
    # --------------------------------------------------------------------------
    {
        "id": 9,
        "difficulty": "Intermediate",
        "category": "Fantasy & Scouting",
        "title": "All-Rounders with 1000+ Runs & 50+ Wickets",
        "question": "Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career. Display player name, total runs, total wickets, and the cricket format.",
        "sql": """SELECT
    p.full_name AS player_name,
    pcs.format AS cricket_format,
    pcs.total_runs,
    pcs.wickets_taken AS total_wickets
FROM player_career_stats pcs
JOIN players p ON pcs.player_id = p.player_id
WHERE p.playing_role = 'All-rounder'
  AND pcs.total_runs > 1000
  AND pcs.wickets_taken > 50
ORDER BY pcs.total_runs DESC;""",
        "explanation": "Multi-conditional filtering across both batting and bowling milestones for all-rounders."
    },
    {
        "id": 10,
        "difficulty": "Intermediate",
        "category": "Broadcasting & Match Reports",
        "title": "Details of Last 20 Completed Matches",
        "question": "Get details of the last 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name. Display most recent matches first.",
        "sql": """SELECT
    m.match_description,
    t1.team_name AS team_1,
    t2.team_name AS team_2,
    tw.team_name AS winning_team,
    m.victory_margin,
    m.victory_type,
    v.venue_name
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
JOIN teams tw ON m.winner_id = tw.team_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.is_completed = 1
ORDER BY m.match_date DESC
LIMIT 20;""",
        "explanation": "Multiple joins against the same entity table (`teams` joined 3 times for team1, team2, and winner) plus venue lookup."
    },
    {
        "id": 11,
        "difficulty": "Intermediate",
        "category": "Multi-Format Analysis",
        "title": "Player Performance Comparison Across Formats",
        "question": "Compare each player's performance across different cricket formats. For players who have played at least 2 different formats, show their total runs in Test cricket, ODI cricket, and T20I cricket, along with their overall batting average across all formats.",
        "sql": """SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN pcs.format = 'Test' THEN pcs.total_runs ELSE 0 END) AS test_runs,
    SUM(CASE WHEN pcs.format = 'ODI' THEN pcs.total_runs ELSE 0 END) AS odi_runs,
    SUM(CASE WHEN pcs.format = 'T20I' THEN pcs.total_runs ELSE 0 END) AS t20i_runs,
    ROUND(AVG(pcs.batting_avg), 2) AS overall_batting_avg
FROM players p
JOIN player_career_stats pcs ON p.player_id = pcs.player_id
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT pcs.format) >= 2
ORDER BY (SUM(pcs.total_runs)) DESC;""",
        "explanation": "Utilizes conditional aggregation (`CASE WHEN ... THEN`) as a pivot table, filtered with `HAVING COUNT(DISTINCT pcs.format) >= 2`."
    },
    {
        "id": 12,
        "difficulty": "Intermediate",
        "category": "Analytics & Team Management",
        "title": "Home vs Away Team Performance",
        "question": "Analyze each international team's performance when playing at home versus playing away. Determine whether each team played at home or away based on whether the venue country matches the team's country. Count wins for each team in both home and away conditions.",
        "sql": """SELECT
    t.team_name,
    SUM(CASE WHEN v.country = t.country AND m.winner_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN v.country != t.country AND m.winner_id = t.team_id THEN 1 ELSE 0 END) AS away_wins,
    COUNT(CASE WHEN m.winner_id = t.team_id THEN 1 END) AS total_wins
FROM teams t
JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.is_completed = 1
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;""",
        "explanation": "Calculates contextual wins by comparing venue country with team country in a conditional `SUM(CASE WHEN ...)`."
    },
    {
        "id": 13,
        "difficulty": "Intermediate",
        "category": "Tactical Partnerships",
        "title": "Consecutive Batting Partnerships of 100+ Runs",
        "question": "Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings. Show both player names, their combined partnership runs, and which innings it occurred in.",
        "sql": """SELECT
    m.match_description,
    p1.full_name AS batsman_1,
    b1.runs_scored AS runs_1,
    p2.full_name AS batsman_2,
    b2.runs_scored AS runs_2,
    (b1.runs_scored + b2.runs_scored) AS combined_partnership_runs,
    b1.innings_number
FROM player_match_batting b1
JOIN player_match_batting b2 
    ON b1.match_id = b2.match_id 
   AND b1.team_id = b2.team_id 
   AND b1.innings_number = b2.innings_number
   AND b2.batting_position = b1.batting_position + 1
JOIN players p1 ON b1.player_id = p1.player_id
JOIN players p2 ON b2.player_id = p2.player_id
JOIN matches m ON b1.match_id = m.match_id
WHERE (b1.runs_scored + b2.runs_scored) >= 100
ORDER BY combined_partnership_runs DESC;""",
        "explanation": "Employs a self-join on `player_match_batting` where `b2.batting_position = b1.batting_position + 1` in the same innings."
    },
    {
        "id": 14,
        "difficulty": "Intermediate",
        "category": "Venue Specific Insights",
        "title": "Bowler Venue Mastery (>= 3 Matches & >= 4 Overs)",
        "question": "Examine bowling performance at different venues. For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate, total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.",
        "sql": """SELECT
    p.full_name AS bowler_name,
    v.venue_name,
    v.city,
    COUNT(DISTINCT bw.match_id) AS matches_played_at_venue,
    SUM(bw.wickets_taken) AS total_wickets_at_venue,
    ROUND(AVG(bw.economy_rate), 2) AS avg_economy_rate
FROM player_match_bowling bw
JOIN players p ON bw.player_id = p.player_id
JOIN matches m ON bw.match_id = m.match_id
JOIN venues v ON m.venue_id = v.venue_id
WHERE bw.overs_bowled >= 4.0
GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name, v.city
HAVING COUNT(DISTINCT bw.match_id) >= 3
ORDER BY total_wickets_at_venue DESC, avg_economy_rate ASC;""",
        "explanation": "Multi-column grouping by player and venue with `HAVING COUNT(DISTINCT match_id) >= 3` and workload threshold filtering."
    },
    {
        "id": 15,
        "difficulty": "Intermediate",
        "category": "Clutch Performance Analytics",
        "title": "Clutch Players in Close Matches (<50 Runs or <5 Wickets)",
        "question": "Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets. For these close matches, calculate each player's average runs scored, total close matches played, and how many of those close matches their team won when they batted.",
        "sql": """SELECT
    p.full_name AS player_name,
    COUNT(DISTINCT m.match_id) AS close_matches_played,
    ROUND(AVG(b.runs_scored), 2) AS avg_runs_in_close_matches,
    SUM(CASE WHEN m.winner_id = b.team_id THEN 1 ELSE 0 END) AS team_close_match_wins
FROM player_match_batting b
JOIN players p ON b.player_id = p.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE m.is_completed = 1
  AND (
      (m.victory_type = 'runs' AND m.victory_margin < 50)
      OR
      (m.victory_type = 'wickets' AND m.victory_margin < 5)
  )
GROUP BY p.player_id, p.full_name
ORDER BY avg_runs_in_close_matches DESC;""",
        "explanation": "Filters matches based on pressure scenario criteria and aggregates batsman scoring with win attribution."
    },
    {
        "id": 16,
        "difficulty": "Intermediate",
        "category": "Yearly Performance Evolution",
        "title": "Annual Batting Evolution Since 2020",
        "question": "Track how players' batting performance changes over different years. For matches since 2020, show each player's average runs per match and average strike rate for each year. Only include players who played at least 5 matches in that year.",
        "sql": """SELECT
    p.full_name AS player_name,
    strftime('%Y', m.match_date) AS match_year,
    COUNT(DISTINCT m.match_id) AS matches_played,
    ROUND(AVG(b.runs_scored), 2) AS avg_runs_per_match,
    ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate
FROM player_match_batting b
JOIN players p ON b.player_id = p.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE strftime('%Y', m.match_date) >= '2020'
GROUP BY p.player_id, p.full_name, strftime('%Y', m.match_date)
HAVING COUNT(DISTINCT m.match_id) >= 5
ORDER BY player_name ASC, match_year ASC;""",
        "explanation": "Grouped by player and parsed calendar year, using `HAVING COUNT(DISTINCT match_id) >= 5` to filter qualified seasons."
    },

    # --------------------------------------------------------------------------
    # ADVANCED LEVEL (QUESTIONS 17 - 25)
    # --------------------------------------------------------------------------
    {
        "id": 17,
        "difficulty": "Advanced",
        "category": "Sports Betting & Strategy",
        "title": "Toss Decision Advantage & Match Win Probability",
        "question": "Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).",
        "sql": """SELECT
    toss_decision,
    COUNT(match_id) AS total_matches,
    SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS toss_winner_won_match,
    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(match_id), 2) AS toss_win_match_win_pct
FROM matches
WHERE is_completed = 1 AND toss_winner_id IS NOT NULL AND toss_decision IS NOT NULL
GROUP BY toss_decision;""",
        "explanation": "Probability analysis using conditional ratios `100.0 * SUM(CASE WHEN toss_winner_id = winner_id) / COUNT(*)` grouped by decision."
    },
    {
        "id": 18,
        "difficulty": "Advanced",
        "category": "Limited Overs Analytics",
        "title": "Most Economical Bowlers in Limited-Overs Cricket",
        "question": "Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.",
        "sql": """SELECT
    p.full_name AS bowler_name,
    COUNT(DISTINCT bw.match_id) AS matches_bowled,
    ROUND(AVG(bw.overs_bowled), 2) AS avg_overs_per_match,
    ROUND(AVG(bw.economy_rate), 2) AS overall_economy_rate,
    SUM(bw.wickets_taken) AS total_wickets
FROM player_match_bowling bw
JOIN players p ON bw.player_id = p.player_id
JOIN matches m ON bw.match_id = m.match_id
WHERE m.match_type IN ('ODI', 'T20I')
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT bw.match_id) >= 10
   AND AVG(bw.overs_bowled) >= 2.0
ORDER BY overall_economy_rate ASC;""",
        "explanation": "Calculates overall economy and wickets across limited-overs formats with double threshold filtering in `HAVING`."
    },
    {
        "id": 19,
        "difficulty": "Advanced",
        "category": "Advanced Statistical Modeling",
        "title": "Batsman Scoring Consistency via Standard Deviation",
        "question": "Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played since 2022. A lower standard deviation indicates more consistent performance.",
        "sql": """SELECT
    p.full_name AS batsman_name,
    COUNT(b.stat_id) AS qualifying_innings,
    ROUND(AVG(b.runs_scored), 2) AS avg_runs,
    ROUND(STDDEV(b.runs_scored), 2) AS stddev_runs
FROM player_match_batting b
JOIN players p ON b.player_id = p.player_id
JOIN matches m ON b.match_id = m.match_id
WHERE b.balls_faced >= 10
  AND strftime('%Y', m.match_date) >= '2022'
GROUP BY p.player_id, p.full_name
HAVING COUNT(b.stat_id) >= 3
ORDER BY stddev_runs ASC;""",
        "explanation": "Executes statistical dispersion analysis using custom `STDDEV()` to quantify batting predictability and reliability."
    },
    {
        "id": 20,
        "difficulty": "Advanced",
        "category": "Cross-Format Dominance",
        "title": "Multi-Format Match Count & Average Matrix",
        "question": "Analyze how many matches each player has played in different cricket formats and their batting average in each format. Show the count of Test matches, ODI matches, and T20 matches for each player, along with their respective batting averages. Only include players who have played at least 20 total matches across all formats.",
        "sql": """SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN pcs.format = 'Test' THEN pcs.matches_played ELSE 0 END) AS test_matches,
    MAX(CASE WHEN pcs.format = 'Test' THEN pcs.batting_avg ELSE NULL END) AS test_avg,
    SUM(CASE WHEN pcs.format = 'ODI' THEN pcs.matches_played ELSE 0 END) AS odi_matches,
    MAX(CASE WHEN pcs.format = 'ODI' THEN pcs.batting_avg ELSE NULL END) AS odi_avg,
    SUM(CASE WHEN pcs.format = 'T20I' THEN pcs.matches_played ELSE 0 END) AS t20i_matches,
    MAX(CASE WHEN pcs.format = 'T20I' THEN pcs.batting_avg ELSE NULL END) AS t20i_avg,
    SUM(pcs.matches_played) AS total_matches_played
FROM players p
JOIN player_career_stats pcs ON p.player_id = pcs.player_id
GROUP BY p.player_id, p.full_name
HAVING SUM(pcs.matches_played) >= 20
ORDER BY total_matches_played DESC;""",
        "explanation": "Multi-dimensional matrix cross-tabulation across Test, ODI, and T20I with aggregate volume thresholds."
    },
    {
        "id": 21,
        "difficulty": "Advanced",
        "category": "Player Valuation Index",
        "title": "Comprehensive Weighted Performance Ranking System",
        "question": "Create a comprehensive performance ranking system for players combining batting, bowling, and fielding into a single weighted score using the exact specified formula and rank players in each format.",
        "sql": """WITH player_points AS (
    SELECT
        p.full_name AS player_name,
        pcs.format AS cricket_format,
        ROUND(
            (COALESCE(pcs.total_runs, 0) * 0.01) + 
            (COALESCE(pcs.batting_avg, 0) * 0.5) + 
            (COALESCE(pcs.strike_rate, 0) * 0.3), 
            2
        ) AS batting_points,
        ROUND(
            (COALESCE(pcs.wickets_taken, 0) * 2.0) + 
            (CASE WHEN pcs.bowling_avg > 0 THEN (50.0 - pcs.bowling_avg) * 0.5 ELSE 0 END) + 
            (CASE WHEN pcs.economy_rate > 0 THEN (6.0 - pcs.economy_rate) * 2.0 ELSE 0 END), 
            2
        ) AS bowling_points,
        ROUND(
            (COALESCE(pcs.catches, 0) * 3.0) + 
            (COALESCE(pcs.stumpings, 0) * 5.0), 
            2
        ) AS fielding_points
    FROM player_career_stats pcs
    JOIN players p ON pcs.player_id = p.player_id
),
ranked_players AS (
    SELECT
        player_name,
        cricket_format,
        batting_points,
        bowling_points,
        fielding_points,
        ROUND(batting_points + bowling_points + fielding_points, 2) AS total_score,
        DENSE_RANK() OVER (
            PARTITION BY cricket_format 
            ORDER BY (batting_points + bowling_points + fielding_points) DESC
        ) AS format_rank
    FROM player_points
)
SELECT
    format_rank,
    cricket_format,
    player_name,
    batting_points,
    bowling_points,
    fielding_points,
    total_score
FROM ranked_players
WHERE format_rank <= 5
ORDER BY cricket_format ASC, format_rank ASC;""",
        "explanation": "Employs Common Table Expressions (CTEs) and `DENSE_RANK() OVER (PARTITION BY cricket_format ORDER BY ... DESC)` to compute weighted holistic ratings."
    },
    {
        "id": 22,
        "difficulty": "Advanced",
        "category": "Head-to-Head Predictions",
        "title": "Head-to-Head Team Match Prediction Analysis",
        "question": "Build a head-to-head match prediction analysis between teams. For each pair of teams that have played at least 5 matches against each other in the last 3 years, calculate total matches, wins, win percentages, and average victory margin.",
        "sql": """WITH team_pair_matches AS (
    SELECT
        CASE WHEN t1.team_name < t2.team_name THEN t1.team_name ELSE t2.team_name END AS team_a,
        CASE WHEN t1.team_name < t2.team_name THEN t2.team_name ELSE t1.team_name END AS team_b,
        m.match_id,
        m.match_date,
        m.winner_id,
        tw.team_name AS winner_name,
        m.victory_margin
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    JOIN teams tw ON m.winner_id = tw.team_id
    WHERE m.is_completed = 1
      AND strftime('%Y', m.match_date) >= '2021'
)
SELECT
    team_a,
    team_b,
    COUNT(match_id) AS total_matches_played,
    SUM(CASE WHEN winner_name = team_a THEN 1 ELSE 0 END) AS team_a_wins,
    SUM(CASE WHEN winner_name = team_b THEN 1 ELSE 0 END) AS team_b_wins,
    ROUND(100.0 * SUM(CASE WHEN winner_name = team_a THEN 1 ELSE 0 END) / COUNT(match_id), 1) AS team_a_win_pct,
    ROUND(100.0 * SUM(CASE WHEN winner_name = team_b THEN 1 ELSE 0 END) / COUNT(match_id), 1) AS team_b_win_pct,
    ROUND(AVG(victory_margin), 1) AS avg_victory_margin
FROM team_pair_matches
GROUP BY team_a, team_b
HAVING COUNT(match_id) >= 5
ORDER BY total_matches_played DESC;""",
        "explanation": "Normalizes undirected rivalries using alphabetical CASE assignment (`CASE WHEN t1 < t2 THEN t1 ELSE t2 END`) and computes win percentages."
    },
    {
        "id": 23,
        "difficulty": "Advanced",
        "category": "Form & Momentum",
        "title": "Recent Player Form & Momentum Classification",
        "question": "Analyze recent player form and momentum. For each player's last 10 batting performances, calculate average runs in last 5 vs last 10, strike rate, 50+ scores, standard deviation, and categorize players into 'Excellent Form', 'Good Form', 'Average Form', or 'Poor Form'.",
        "sql": """WITH numbered_innings AS (
    SELECT
        b.player_id,
        p.full_name AS player_name,
        b.runs_scored,
        b.strike_rate,
        m.match_date,
        ROW_NUMBER() OVER (PARTITION BY b.player_id ORDER BY m.match_date DESC) AS innings_recency
    FROM player_match_batting b
    JOIN players p ON b.player_id = p.player_id
    JOIN matches m ON b.match_id = m.match_id
),
last_10_innings AS (
    SELECT *
    FROM numbered_innings
    WHERE innings_recency <= 10
),
form_metrics AS (
    SELECT
        player_id,
        player_name,
        COUNT(runs_scored) AS innings_count,
        ROUND(AVG(CASE WHEN innings_recency <= 5 THEN runs_scored END), 2) AS avg_runs_last_5,
        ROUND(AVG(runs_scored), 2) AS avg_runs_last_10,
        ROUND(AVG(strike_rate), 2) AS recent_strike_rate,
        SUM(CASE WHEN runs_scored >= 50 THEN 1 ELSE 0 END) AS fifties_in_last_10,
        ROUND(STDDEV(runs_scored), 2) AS consistency_stddev
    FROM last_10_innings
    GROUP BY player_id, player_name
    HAVING COUNT(runs_scored) >= 5
)
SELECT
    player_name,
    innings_count,
    avg_runs_last_5,
    avg_runs_last_10,
    recent_strike_rate,
    fifties_in_last_10,
    consistency_stddev,
    CASE
        WHEN avg_runs_last_5 >= 50.0 OR (avg_runs_last_5 >= 40.0 AND fifties_in_last_10 >= 3) THEN 'Excellent Form'
        WHEN avg_runs_last_5 >= 35.0 OR (avg_runs_last_5 >= 30.0 AND fifties_in_last_10 >= 2) THEN 'Good Form'
        WHEN avg_runs_last_5 >= 20.0 THEN 'Average Form'
        ELSE 'Poor Form'
    END AS form_category
FROM form_metrics
ORDER BY avg_runs_last_5 DESC;""",
        "explanation": "Leverages window function `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY match_date DESC)` to slice rolling windows and dynamically categorize momentum."
    },
    {
        "id": 24,
        "difficulty": "Advanced",
        "category": "Partnership Mastery",
        "title": "Batting Partnership Success Rate & Synergy",
        "question": "Study successful batting partnerships. For pairs of players who have batted together as consecutive batsmen in at least 5 partnerships, calculate average partnership runs, 50+ partnerships, highest score, success rate %, and rank them.",
        "sql": """WITH consecutive_partnerships AS (
    SELECT
        CASE WHEN p1.full_name < p2.full_name THEN p1.full_name ELSE p2.full_name END AS batsman_a,
        CASE WHEN p1.full_name < p2.full_name THEN p2.full_name ELSE p1.full_name END AS batsman_b,
        (b1.runs_scored + b2.runs_scored) AS partnership_runs
    FROM player_match_batting b1
    JOIN player_match_batting b2
        ON b1.match_id = b2.match_id
       AND b1.team_id = b2.team_id
       AND b1.innings_number = b2.innings_number
       AND b2.batting_position = b1.batting_position + 1
    JOIN players p1 ON b1.player_id = p1.player_id
    JOIN players p2 ON b2.player_id = p2.player_id
)
SELECT
    batsman_a,
    batsman_b,
    COUNT(*) AS total_partnerships,
    ROUND(AVG(partnership_runs), 2) AS avg_partnership_runs,
    SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) AS fifty_plus_partnerships,
    MAX(partnership_runs) AS highest_partnership_score,
    ROUND(100.0 * SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) / COUNT(*), 1) AS success_rate_pct,
    DENSE_RANK() OVER (ORDER BY AVG(partnership_runs) DESC) AS partnership_rank
FROM consecutive_partnerships
GROUP BY batsman_a, batsman_b
HAVING COUNT(*) >= 5
ORDER BY avg_partnership_runs DESC;""",
        "explanation": "Consecutive self-join with bilateral name normalization and window ranking `DENSE_RANK() OVER (ORDER BY AVG(partnership_runs) DESC)`."
    },
    {
        "id": 25,
        "difficulty": "Advanced",
        "category": "Time-Series Career Analytics",
        "title": "Quarterly Performance Evolution & Career Trajectory",
        "question": "Perform a time-series analysis of player performance evolution. Track quarterly averages, compare with LAG(), and categorize career phase ('Career Ascending', 'Career Declining', 'Career Stable') for players with >= 6 quarters and >= 3 matches/quarter.",
        "sql": """WITH quarterly_stats AS (
    SELECT
        b.player_id,
        p.full_name AS player_name,
        strftime('%Y', m.match_date) || '-Q' || ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter_str,
        COUNT(DISTINCT m.match_id) AS quarter_matches,
        ROUND(AVG(b.runs_scored), 2) AS avg_runs,
        ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate
    FROM player_match_batting b
    JOIN players p ON b.player_id = p.player_id
    JOIN matches m ON b.match_id = m.match_id
    GROUP BY b.player_id, p.full_name, quarter_str
    HAVING COUNT(DISTINCT m.match_id) >= 3
),
quarterly_trend AS (
    SELECT
        player_id,
        player_name,
        quarter_str,
        quarter_matches,
        avg_runs,
        avg_strike_rate,
        LAG(avg_runs, 1) OVER (PARTITION BY player_id ORDER BY quarter_str) AS prev_quarter_runs,
        CASE
            WHEN LAG(avg_runs, 1) OVER (PARTITION BY player_id ORDER BY quarter_str) IS NULL THEN 'Baseline'
            WHEN avg_runs > LAG(avg_runs, 1) OVER (PARTITION BY player_id ORDER BY quarter_str) + 5.0 THEN 'Improving'
            WHEN avg_runs < LAG(avg_runs, 1) OVER (PARTITION BY player_id ORDER BY quarter_str) - 5.0 THEN 'Declining'
            ELSE 'Stable'
        END AS performance_trajectory
    FROM quarterly_stats
),
player_phase_summary AS (
    SELECT
        player_id,
        player_name,
        COUNT(quarter_str) AS total_quarters,
        ROUND(AVG(avg_runs), 2) AS career_avg_runs,
        SUM(CASE WHEN performance_trajectory = 'Improving' THEN 1 ELSE 0 END) AS improving_quarters,
        SUM(CASE WHEN performance_trajectory = 'Declining' THEN 1 ELSE 0 END) AS declining_quarters
    FROM quarterly_trend
    GROUP BY player_id, player_name
    HAVING COUNT(quarter_str) >= 6
)
SELECT
    player_name,
    total_quarters,
    career_avg_runs,
    improving_quarters,
    declining_quarters,
    CASE
        WHEN improving_quarters > declining_quarters THEN 'Career Ascending'
        WHEN declining_quarters > improving_quarters THEN 'Career Declining'
        ELSE 'Career Stable'
    END AS career_phase
FROM player_phase_summary
ORDER BY career_avg_runs DESC;""",
        "explanation": "Advanced multi-stage CTE time-series model utilizing `LAG()` window function over dynamic calendar quarters and delta categorization."
    }
]

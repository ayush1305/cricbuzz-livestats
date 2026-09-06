-- ==============================================================================
-- Cricbuzz LiveStats - 25 Comprehensive SQL Practice & Analytics Queries
-- Structured into Beginner (1-8), Intermediate (9-16), and Advanced (17-25)
-- Compatible with SQLite, PostgreSQL, and MySQL
-- ==============================================================================

-- ==============================================================================
-- BEGINNER LEVEL (QUESTIONS 1 - 8)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Question 1: Find all players who represent India. Display their full name,
-- playing role, batting style, and bowling style.
-- ------------------------------------------------------------------------------
SELECT
    full_name,
    playing_role,
    batting_style,
    bowling_style
FROM players
WHERE country = 'India'
ORDER BY full_name ASC;

-- ------------------------------------------------------------------------------
-- Question 2: Show all cricket matches that were played in the last 30 days.
-- Include the match description, both team names, venue name with city, and the match date.
-- Sort by most recent matches first.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY m.match_date DESC;

-- ------------------------------------------------------------------------------
-- Question 3: List the top 10 highest run scorers in ODI cricket.
-- Show player name, total runs scored, batting average, and number of centuries.
-- Display the highest run scorer first.
-- ------------------------------------------------------------------------------
SELECT
    p.full_name AS player_name,
    pcs.total_runs,
    pcs.batting_avg,
    pcs.centuries
FROM player_career_stats pcs
JOIN players p ON pcs.player_id = p.player_id
WHERE pcs.format = 'ODI'
ORDER BY pcs.total_runs DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- Question 4: Display all cricket venues that have a seating capacity of more than
-- 50,000 spectators. Show venue name, city, country, and capacity.
-- Order by largest capacity first.
-- ------------------------------------------------------------------------------
SELECT
    venue_name,
    city,
    country,
    capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;

-- ------------------------------------------------------------------------------
-- Question 5: Calculate how many matches each team has won.
-- Show team name and total number of wins. Display teams with most wins first.
-- ------------------------------------------------------------------------------
SELECT
    t.team_name,
    COUNT(m.match_id) AS total_wins
FROM teams t
JOIN matches m ON t.team_id = m.winner_id
WHERE m.is_completed = 1
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;

-- ------------------------------------------------------------------------------
-- Question 6: Count how many players belong to each playing role
-- (like Batsman, Bowler, All-rounder, Wicket-keeper). Show the role and count of players.
-- ------------------------------------------------------------------------------
SELECT
    playing_role,
    COUNT(player_id) AS player_count
FROM players
GROUP BY playing_role
ORDER BY player_count DESC;

-- ------------------------------------------------------------------------------
-- Question 7: Find the highest individual batting score achieved in each cricket
-- format (Test, ODI, T20I). Display the format and the highest score for that format.
-- ------------------------------------------------------------------------------
SELECT
    m.match_type AS cricket_format,
    MAX(b.runs_scored) AS highest_individual_score
FROM player_match_batting b
JOIN matches m ON b.match_id = m.match_id
GROUP BY m.match_type
ORDER BY highest_individual_score DESC;

-- ------------------------------------------------------------------------------
-- Question 8: Show all cricket series that started in or since the year 2024.
-- Include series name, host country, match type, start date, and total matches planned.
-- ------------------------------------------------------------------------------
SELECT
    series_name,
    host_country,
    match_type,
    start_date,
    total_matches
FROM series
WHERE strftime('%Y', start_date) >= '2024'
ORDER BY start_date DESC;


-- ==============================================================================
-- INTERMEDIATE LEVEL (QUESTIONS 9 - 16)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Question 9: Find all-rounder players who have scored more than 1000 runs AND
-- taken more than 50 wickets in their career. Display player name, total runs,
-- total wickets, and the cricket format.
-- ------------------------------------------------------------------------------
SELECT
    p.full_name AS player_name,
    pcs.format AS cricket_format,
    pcs.total_runs,
    pcs.wickets_taken AS total_wickets
FROM player_career_stats pcs
JOIN players p ON pcs.player_id = p.player_id
WHERE p.playing_role = 'All-rounder'
  AND pcs.total_runs > 1000
  AND pcs.wickets_taken > 50
ORDER BY pcs.total_runs DESC;

-- ------------------------------------------------------------------------------
-- Question 10: Get details of the last 20 completed matches.
-- Show match description, both team names, winning team, victory margin,
-- victory type (runs/wickets), and venue name. Display most recent matches first.
-- ------------------------------------------------------------------------------
SELECT
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
LIMIT 20;

-- ------------------------------------------------------------------------------
-- Question 11: Compare each player's performance across different cricket formats.
-- For players who have played at least 2 different formats, show their total runs
-- in Test, ODI, and T20I, along with their overall batting average across all formats.
-- ------------------------------------------------------------------------------
SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN pcs.format = 'Test' THEN pcs.total_runs ELSE 0 END) AS test_runs,
    SUM(CASE WHEN pcs.format = 'ODI' THEN pcs.total_runs ELSE 0 END) AS odi_runs,
    SUM(CASE WHEN pcs.format = 'T20I' THEN pcs.total_runs ELSE 0 END) AS t20i_runs,
    ROUND(AVG(pcs.batting_avg), 2) AS overall_batting_avg
FROM players p
JOIN player_career_stats pcs ON p.player_id = pcs.player_id
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT pcs.format) >= 2
ORDER BY (SUM(pcs.total_runs)) DESC;

-- ------------------------------------------------------------------------------
-- Question 12: Analyze each international team's performance when playing at home
-- versus playing away. Determine home/away based on whether the venue country
-- matches the team's country. Count wins for each team in both conditions.
-- ------------------------------------------------------------------------------
SELECT
    t.team_name,
    SUM(CASE WHEN v.country = t.country AND m.winner_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN v.country != t.country AND m.winner_id = t.team_id THEN 1 ELSE 0 END) AS away_wins,
    COUNT(CASE WHEN m.winner_id = t.team_id THEN 1 END) AS total_wins
FROM teams t
JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
JOIN venues v ON m.venue_id = v.venue_id
WHERE m.is_completed = 1
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;

-- ------------------------------------------------------------------------------
-- Question 13: Identify batting partnerships where two consecutive batsmen
-- (batting positions next to each other) scored a combined total of 100 or more
-- runs in the same innings. Show both player names, combined partnership runs,
-- and which innings it occurred in.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY combined_partnership_runs DESC;

-- ------------------------------------------------------------------------------
-- Question 14: Examine bowling performance at different venues. For bowlers who
-- have played at least 3 matches at the same venue, calculate their average economy
-- rate, total wickets taken, and number of matches played at each venue.
-- Focus on bowlers who bowled at least 4 overs in each match.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY total_wickets_at_venue DESC, avg_economy_rate ASC;

-- ------------------------------------------------------------------------------
-- Question 15: Identify players who perform exceptionally well in close matches
-- (decided by less than 50 runs OR less than 5 wickets). Calculate each player's
-- average runs scored, total close matches played, and how many of those close
-- matches their team won when they batted.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY avg_runs_in_close_matches DESC;

-- ------------------------------------------------------------------------------
-- Question 16: Track how players' batting performance changes over different years.
-- For matches since 2020, show each player's average runs per match and average
-- strike rate for each year. Only include players with at least 5 matches in that year.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY player_name ASC, match_year ASC;


-- ==============================================================================
-- ADVANCED LEVEL (QUESTIONS 17 - 25)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Question 17: Investigate whether winning the toss gives teams an advantage in
-- winning matches. Calculate what percentage of matches are won by the team that
-- wins the toss, broken down by their toss decision (bat vs bowl first).
-- ------------------------------------------------------------------------------
SELECT
    toss_decision,
    COUNT(match_id) AS total_matches,
    SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS toss_winner_won_match,
    ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(match_id), 2) AS toss_win_match_win_pct
FROM matches
WHERE is_completed = 1 AND toss_winner_id IS NOT NULL AND toss_decision IS NOT NULL
GROUP BY toss_decision;

-- ------------------------------------------------------------------------------
-- Question 18: Find the most economical bowlers in limited-overs cricket (ODI and T20).
-- Calculate each bowler's overall economy rate and total wickets taken.
-- Bowled in at least 10 matches and bowled at least 2 overs per match on average.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY overall_economy_rate ASC;

-- ------------------------------------------------------------------------------
-- Question 19: Determine which batsmen are most consistent in their scoring.
-- Calculate the average runs scored and standard deviation of runs for each player.
-- Only include players who faced at least 10 balls per innings and played since 2022.
-- Lower standard deviation indicates higher consistency.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY stddev_runs ASC;

-- ------------------------------------------------------------------------------
-- Question 20: Analyze how many matches each player has played in different cricket
-- formats and their batting average in each format (Test, ODI, T20).
-- Only include players who have played at least 20 total matches across all formats.
-- ------------------------------------------------------------------------------
SELECT
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
ORDER BY total_matches_played DESC;

-- ------------------------------------------------------------------------------
-- Question 21: Create a comprehensive performance ranking system for players.
-- Batting points: (runs_scored × 0.01) + (batting_average × 0.5) + (strike_rate × 0.3)
-- Bowling points: (wickets_taken × 2) + ((50 - bowling_average) × 0.5) + ((6 - economy_rate) × 2)
-- Fielding points: (catches × 3) + (stumpings × 5)
-- Rank the top performers in each cricket format.
-- ------------------------------------------------------------------------------
WITH player_points AS (
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
ORDER BY cricket_format ASC, format_rank ASC;

-- ------------------------------------------------------------------------------
-- Question 22: Build a head-to-head match prediction analysis between teams.
-- For each pair of teams with at least 5 matches against each other in the last 3 years:
-- Calculate total matches, wins for each team, win percentages, and average victory margin.
-- ------------------------------------------------------------------------------
WITH team_pair_matches AS (
    SELECT
        CASE WHEN t1.team_name < t2.team_name THEN t1.team_name ELSE t2.team_name END AS team_a,
        CASE WHEN t1.team_name < t2.team_name THEN t2.team_name ELSE t1.team_name END AS team_b,
        m.match_id,
        m.match_date,
        m.winner_id,
        tw.team_name AS winner_name,
        m.victory_margin,
        m.victory_type,
        m.toss_decision,
        v.venue_name
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    JOIN teams tw ON m.winner_id = tw.team_id
    JOIN venues v ON m.venue_id = v.venue_id
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
ORDER BY total_matches_played DESC;

-- ------------------------------------------------------------------------------
-- Question 23: Analyze recent player form and momentum. For each player's last 10
-- batting performances, calculate:
-- Average runs in last 5 vs last 10, strike rate, 50+ scores, consistency (stddev),
-- and categorize form ("Excellent Form", "Good Form", "Average Form", "Poor Form").
-- ------------------------------------------------------------------------------
WITH numbered_innings AS (
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
ORDER BY avg_runs_last_5 DESC;

-- ------------------------------------------------------------------------------
-- Question 24: Study successful batting partnerships to identify best player combinations.
-- Pairs of players who batted together as consecutive batsmen (positions differ by 1)
-- in at least 5 partnerships: average partnership runs, 50+ partnerships, highest score,
-- success rate %, and rank.
-- ------------------------------------------------------------------------------
WITH consecutive_partnerships AS (
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
ORDER BY avg_partnership_runs DESC;

-- ------------------------------------------------------------------------------
-- Question 25: Time-series analysis of player performance evolution.
-- Track how batting changes quarterly (runs and strike rate), compare to previous quarter,
-- trajectory, and categorize career phase ("Career Ascending", "Career Declining", "Career Stable")
-- for players spanning >= 6 quarters and >= 3 matches per quarter.
-- ------------------------------------------------------------------------------
WITH quarterly_stats AS (
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
ORDER BY career_avg_runs DESC;

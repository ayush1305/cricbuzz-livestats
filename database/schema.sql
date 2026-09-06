-- ==============================================================================
-- Cricbuzz LiveStats Database Schema
-- Compatible with SQLite, PostgreSQL, and MySQL
-- ==============================================================================

-- 1. TEAMS TABLE
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    team_code VARCHAR(10) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL
);

-- 2. PLAYERS TABLE
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    team_id INTEGER,
    full_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    playing_role VARCHAR(50) NOT NULL, -- 'Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'
    batting_style VARCHAR(50),         -- 'Right-hand bat', 'Left-hand bat'
    bowling_style VARCHAR(50),         -- 'Right-arm fast', 'Right-arm offbreak', etc.
    debut_year INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL
);

-- 3. VENUES TABLE
CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY,
    venue_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL
);

-- 4. SERIES TABLE
CREATE TABLE IF NOT EXISTS series (
    series_id INTEGER PRIMARY KEY,
    series_name VARCHAR(150) NOT NULL,
    host_country VARCHAR(100) NOT NULL,
    match_type VARCHAR(20) NOT NULL,    -- 'Test', 'ODI', 'T20I'
    start_date DATE NOT NULL,
    total_matches INTEGER NOT NULL
);

-- 5. MATCHES TABLE
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    series_id INTEGER,
    match_description VARCHAR(200) NOT NULL,
    match_type VARCHAR(20) NOT NULL,    -- 'Test', 'ODI', 'T20I'
    team1_id INTEGER NOT NULL,
    team2_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    match_date DATE NOT NULL,
    toss_winner_id INTEGER,
    toss_decision VARCHAR(20),          -- 'bat', 'bowl'
    winner_id INTEGER,
    victory_margin INTEGER,
    victory_type VARCHAR(20),           -- 'runs', 'wickets', 'tie', 'no result'
    is_completed BOOLEAN DEFAULT 1,
    FOREIGN KEY (series_id) REFERENCES series(series_id) ON DELETE SET NULL,
    FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (toss_winner_id) REFERENCES teams(team_id),
    FOREIGN KEY (winner_id) REFERENCES teams(team_id)
);

-- 6. PLAYER MATCH BATTING INNINGS
CREATE TABLE IF NOT EXISTS player_match_batting (
    stat_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    innings_number INTEGER NOT NULL,    -- 1, 2, 3, 4
    batting_position INTEGER NOT NULL,  -- 1 to 11
    runs_scored INTEGER NOT NULL DEFAULT 0,
    balls_faced INTEGER NOT NULL DEFAULT 0,
    fours INTEGER NOT NULL DEFAULT 0,
    sixes INTEGER NOT NULL DEFAULT 0,
    strike_rate REAL DEFAULT 0.0,
    is_out BOOLEAN DEFAULT 1,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- 7. PLAYER MATCH BOWLING INNINGS
CREATE TABLE IF NOT EXISTS player_match_bowling (
    stat_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    innings_number INTEGER NOT NULL,
    overs_bowled REAL NOT NULL DEFAULT 0.0,
    maidens INTEGER NOT NULL DEFAULT 0,
    runs_conceded INTEGER NOT NULL DEFAULT 0,
    wickets_taken INTEGER NOT NULL DEFAULT 0,
    economy_rate REAL DEFAULT 0.0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- 8. PLAYER MATCH FIELDING
CREATE TABLE IF NOT EXISTS player_match_fielding (
    stat_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    catches INTEGER DEFAULT 0,
    stumpings INTEGER DEFAULT 0,
    run_outs INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE
);

-- 9. PLAYER CAREER STATS SUMMARY
CREATE TABLE IF NOT EXISTS player_career_stats (
    stat_id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    format VARCHAR(20) NOT NULL,        -- 'Test', 'ODI', 'T20I'
    matches_played INTEGER DEFAULT 0,
    total_runs INTEGER DEFAULT 0,
    batting_avg REAL DEFAULT 0.0,
    strike_rate REAL DEFAULT 0.0,
    centuries INTEGER DEFAULT 0,
    fifties INTEGER DEFAULT 0,
    highest_score INTEGER DEFAULT 0,
    wickets_taken INTEGER DEFAULT 0,
    bowling_avg REAL DEFAULT 0.0,
    economy_rate REAL DEFAULT 0.0,
    catches INTEGER DEFAULT 0,
    stumpings INTEGER DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    UNIQUE(player_id, format)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_players_country ON players(country);
CREATE INDEX IF NOT EXISTS idx_players_role ON players(playing_role);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_type ON matches(match_type);
CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner_id);
CREATE INDEX IF NOT EXISTS idx_batting_player ON player_match_batting(player_id);
CREATE INDEX IF NOT EXISTS idx_batting_match ON player_match_batting(match_id);
CREATE INDEX IF NOT EXISTS idx_bowling_player ON player_match_bowling(player_id);
CREATE INDEX IF NOT EXISTS idx_bowling_match ON player_match_bowling(match_id);

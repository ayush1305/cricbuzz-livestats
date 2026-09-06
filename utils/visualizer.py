"""
Visualizer module for Cricbuzz LiveStats.
Provides interactive Plotly charts tailored to Cricbuzz green and white theme.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_top_run_scorers_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart for top run scorers."""
    if df.empty or "player_name" not in df.columns:
        return go.Figure()
    
    fig = px.bar(
        df,
        x="total_runs",
        y="player_name",
        orientation="h",
        color="total_runs",
        color_continuous_scale=["#bbf7d0", "#009270", "#005a44"],
        text="total_runs",
        title="Top Run Scorers",
        labels={"total_runs": "Total Runs", "player_name": "Player"}
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Total Runs",
        yaxis_title="Player",
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc"
    )
    return fig


def create_toss_win_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart for toss win match win percentage."""
    if df.empty or "toss_decision" not in df.columns:
        return go.Figure()

    fig = px.pie(
        df,
        names="toss_decision",
        values="toss_winner_won_match",
        hole=0.45,
        title="Match Wins by Toss Decision (Bat vs Bowl)",
        color_discrete_sequence=["#009270", "#0284c7"]
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
        paper_bgcolor="#ffffff"
    )
    return fig


def create_player_form_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart for recent form (last 5 vs last 10)."""
    if df.empty or "player_name" not in df.columns:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["player_name"],
        y=df["avg_runs_last_5"],
        name="Last 5 Innings Avg",
        marker_color="#009270"
    ))
    fig.add_trace(go.Bar(
        x=df["player_name"],
        y=df["avg_runs_last_10"],
        name="Last 10 Innings Avg",
        marker_color="#0284c7"
    ))
    fig.update_layout(
        barmode="group",
        title="Player Form Momentum: Last 5 vs Last 10 Matches",
        xaxis_title="Player",
        yaxis_title="Batting Average",
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc"
    )
    return fig


def create_bowler_economy_chart(df: pd.DataFrame) -> go.Figure:
    """Scatter chart comparing economy rate against wickets taken."""
    if df.empty or "bowler_name" not in df.columns:
        return go.Figure()

    fig = px.scatter(
        df,
        x="overall_economy_rate",
        y="total_wickets",
        text="bowler_name",
        size="matches_bowled",
        color="overall_economy_rate",
        color_continuous_scale="Tealgrn",
        title="Limited-Overs Economy Rate vs Wickets",
        labels={"overall_economy_rate": "Economy Rate", "total_wickets": "Total Wickets"}
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc"
    )
    return fig


def create_head_to_head_chart(df: pd.DataFrame) -> go.Figure:
    """Comparison bar chart for head-to-head records."""
    if df.empty or "team_a" not in df.columns:
        return go.Figure()

    fig = go.Figure()
    rivalries = [f"{row['team_a']} vs {row['team_b']}" for _, row in df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=rivalries,
        y=df["team_a_wins"],
        name="Team A Wins",
        marker_color="#009270"
    ))
    fig.add_trace(go.Bar(
        x=rivalries,
        y=df["team_b_wins"],
        name="Team B Wins",
        marker_color="#f59e0b"
    ))
    fig.update_layout(
        barmode="stack",
        title="Head-to-Head Win Distribution",
        xaxis_title="Rivalry",
        yaxis_title="Total Matches Won",
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc"
    )
    return fig

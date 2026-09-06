"""
Real-Time Cricbuzz Cricket API Integration Module.
Directly interfaces with the Cricbuzz RapidAPI endpoints:
- Matches: matches/v1/live, matches/v1/recent
- Scorecard: mcenter/v1/{match_id}/hscard
- Commentary: mcenter/v1/{match_id}/comm
- Teams & Squads: teams/v1/international, teams/v1/{team_id}/players
"""

import os
import re
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "2fe75634d2mshf7b85a8c84dbbc1p18741ajsnd4dba5799d5d")
try:
    import streamlit as st
    if hasattr(st, "secrets") and "RAPIDAPI_KEY" in st.secrets:
        RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
except Exception:
    pass

RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
BASE_URL = f"https://{RAPIDAPI_HOST}"


class CricbuzzAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RAPIDAPI_KEY", RAPIDAPI_KEY)
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
        self.is_live_configured = bool(self.api_key and len(self.api_key.strip()) > 10)

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Makes an authenticated HTTP GET request to the real Cricbuzz RapidAPI."""
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=12)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_live_and_recent_matches(self) -> List[Dict[str, Any]]:
        """
        Fetches live and recent real matches directly from Cricbuzz API.
        """
        parsed_matches = []
        for ep in ["matches/v1/live", "matches/v1/recent"]:
            res = self._make_request(ep)
            if not res or "typeMatches" not in res:
                continue

            for tm in res.get("typeMatches", []):
                m_type = tm.get("matchType", "International")
                for sm in tm.get("seriesMatches", []):
                    wrapper = sm.get("seriesAdWrapper", {})
                    series_name = wrapper.get("seriesName", "Cricket Series")
                    for m in wrapper.get("matches", []):
                        minfo = m.get("matchInfo", {})
                        mscore = m.get("matchScore", {})
                        mid = minfo.get("matchId")
                        if not mid or any(pm["match_id"] == mid for pm in parsed_matches):
                            continue

                        t1 = minfo.get("team1", {})
                        t2 = minfo.get("team2", {})

                        # Extract real scores from live API
                        t1_scores = []
                        t2_scores = []
                        t1_data = mscore.get("team1Score", {})
                        for k in ["inngs1", "inngs2"]:
                            if k in t1_data:
                                inn = t1_data[k]
                                t1_scores.append(f"{inn.get('runs', 0)}/{inn.get('wickets', 0)} ({inn.get('overs', 0)} ov)")

                        t2_data = mscore.get("team2Score", {})
                        for k in ["inngs1", "inngs2"]:
                            if k in t2_data:
                                inn = t2_data[k]
                                t2_scores.append(f"{inn.get('runs', 0)}/{inn.get('wickets', 0)} ({inn.get('overs', 0)} ov)")

                        venue = minfo.get("venueInfo", {})
                        venue_str = f"{venue.get('ground', 'Stadium')}, {venue.get('city', '')}".strip(", ")

                        parsed_matches.append({
                            "match_id": mid,
                            "title": f"{t1.get('teamName', 'Team 1')} vs {t2.get('teamName', 'Team 2')}",
                            "series": series_name,
                            "format": minfo.get("matchFormat", m_type),
                            "venue": venue_str or "Cricket Ground",
                            "status": minfo.get("status", "Match Live"),
                            "state": minfo.get("state", "In Progress"),
                            "team1": {
                                "name": t1.get("teamName", "Team 1"),
                                "code": t1.get("teamSName", "T1"),
                                "scores": t1_scores or ["Score pending"]
                            },
                            "team2": {
                                "name": t2.get("teamName", "Team 2"),
                                "code": t2.get("teamSName", "T2"),
                                "scores": t2_scores or ["Yet to bat"]
                            }
                        })

        return parsed_matches

    def get_match_scorecard(self, match_id: int) -> Dict[str, Any]:
        """
        Fetches official scorecard from Cricbuzz API: mcenter/v1/{match_id}/hscard.
        """
        res = self._make_request(f"mcenter/v1/{match_id}/hscard")
        if not res or "scorecard" not in res:
            return {"innings": [], "status": "Scorecard not available"}

        parsed_innings = []
        for inn in res.get("scorecard", []):
            bat_list = []
            for b in inn.get("batsman", []):
                bat_list.append({
                    "name": b.get("name"),
                    "runs": b.get("runs"),
                    "balls": b.get("balls"),
                    "fours": b.get("fours"),
                    "sixes": b.get("sixes"),
                    "sr": b.get("strkrate"),
                    "dismissal": b.get("outdec")
                })

            bowl_list = []
            for bw in inn.get("bowler", []):
                bowl_list.append({
                    "name": bw.get("name"),
                    "overs": bw.get("overs"),
                    "maidens": bw.get("maidens"),
                    "runs": bw.get("runs"),
                    "wickets": bw.get("wickets"),
                    "econ": bw.get("economy")
                })

            score_val = inn.get("score")
            if score_val is None:
                score_val = sum(b["runs"] for b in bat_list if b["runs"] is not None)

            parsed_innings.append({
                "team": inn.get("batteamname") or inn.get("batteamsname", "Team"),
                "score": score_val,
                "wickets": inn.get("wickets", 0),
                "overs": inn.get("overs", 0.0),
                "runrate": inn.get("runrate", 0.0),
                "batsmen": bat_list,
                "bowlers": bowl_list
            })

        return {
            "status": res.get("status", "Match Completed"),
            "innings": parsed_innings
        }

    def get_match_commentary(self, match_id: int) -> List[str]:
        """
        Fetches real-time live ball commentary from Cricbuzz API: mcenter/v1/{match_id}/comm.
        """
        res = self._make_request(f"mcenter/v1/{match_id}/comm")
        if not res or "comwrapper" not in res:
            return []

        lines = []
        for cw in res.get("comwrapper", []):
            c = cw.get("commentary", {})
            txt = c.get("commtxt", "")
            if not txt:
                continue

            for f in c.get("commentaryformats", []):
                for item in f.get("value", []):
                    txt = txt.replace(item.get("id", ""), item.get("value", ""))
            txt = re.sub(r"B\d+\$", "", txt).strip()
            if txt:
                lines.append(txt)

        return lines

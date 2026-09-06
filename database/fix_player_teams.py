"""
Fix player national team assignments using official Cricbuzz API intlTeam data.
Ensures Indian roster only contains Indian players, South Africa contains Quinton de Kock, etc.
"""

import sqlite3
import time
from utils.cricbuzz_api import CricbuzzAPIClient

client = CricbuzzAPIClient()
conn = sqlite3.connect("database/cricket_analytics.db")
cur = conn.cursor()

# Team name to team_id mapping
TEAM_MAP = {
    'india': 2,
    'pakistan': 3,
    'australia': 4,
    'sri lanka': 5,
    'bangladesh': 6,
    'united arab emirates': 7,
    'uae': 7,
    'england': 9,
    'west indies': 10,
    'south africa': 11,
    'zimbabwe': 12,
    'new zealand': 13,
    'kenya': 14,
    'united states of america': 15,
    'usa': 15,
    'scotland': 23,
    'netherlands': 24,
    'canada': 26,
    'ireland': 27,
    'nepal': 72,
    'afghanistan': 96,
    'namibia': 161,
    'oman': 304,
    'uganda': 44,
    'papua new guinea': 287,
    'png': 287,
    'hong kong': 8
}

cur.execute("SELECT player_id, full_name FROM players WHERE country = 'International' OR team_id = 2")
rows = cur.fetchall()

print(f"Inspecting {len(rows)} players for country verification...")

known_indian_names = [
    "rohit sharma", "virat kohli", "shubman gill", "jasprit bumrah",
    "mohammed shami", "rishabh pant", "kl rahul", "hardik pandya",
    "ravindra jadeja", "suryakumar yadav", "axar patel", "mohammed siraj",
    "kuldeep yadav", "sanju samson", "arshdeep singh", "yashasvi jaiswal",
    "rinku singh", "tilak varma", "shivam dube", "ravi bishnoi",
    "washington sundar", "shardul thakur", "ishan kishan", "ruturaj gaikwad",
    "prasidh krishna", "avesh khan", "mukesh kumar", "shreyas iyer",
    "yuzvendra chahal", "deepak chahar", "bhuvneshwar kumar", "umran malik",
    "harshit rana", "nitish kumar reddy", "mayank yadav", "abhishek sharma", "dhruv jurel"
]

updated_count = 0
for pid, name in rows:
    nl = name.lower().strip()
    # If clearly Indian star
    if any(k in nl for k in known_indian_names):
        cur.execute("UPDATE players SET team_id = 2, country = 'India' WHERE player_id = ?", (pid,))
        continue
    
    # Query Cricbuzz API for exact intlTeam
    profile = client._make_request(f"stats/v1/player/{pid}")
    intl_team = profile.get("intlTeam", "").strip() if profile else ""
    
    assigned_tid = None
    assigned_country = None
    
    if intl_team:
        for tname, tid in TEAM_MAP.items():
            if tname in intl_team.lower():
                assigned_tid = tid
                assigned_country = intl_team
                break

    # If still unassigned, check common players
    if not assigned_tid:
        if "quinton de kock" in nl or "pretorius" in nl or "klaasen" in nl or "miller" in nl:
            assigned_tid = 11
            assigned_country = "South Africa"
        elif "pooran" in nl or "pollard" in nl or "narine" in nl or "hetmyer" in nl or "mayers" in nl or "allen" in nl or "cornwall" in nl:
            assigned_tid = 10
            assigned_country = "West Indies"
        elif "moeen" in nl or "hales" in nl or "robinson" in nl or "lawrence" in nl or "cox" in nl:
            assigned_tid = 9
            assigned_country = "England"
        elif "shanaka" in nl or "hasaranga" in nl:
            assigned_tid = 5
            assigned_country = "Sri Lanka"
        elif "erasmus" in nl or "frylinck" in nl:
            assigned_tid = 161
            assigned_country = "Namibia"
        elif "raza" in nl or "burl" in nl:
            assigned_tid = 12
            assigned_country = "Zimbabwe"
        elif "munro" in nl or "neesham" in nl:
            assigned_tid = 13
            assigned_country = "New Zealand"

    if assigned_tid:
        cur.execute("UPDATE players SET team_id = ?, country = ? WHERE player_id = ?", (assigned_tid, assigned_country, pid))
        cur.execute("UPDATE player_match_batting SET team_id = ? WHERE player_id = ?", (assigned_tid, pid))
        cur.execute("UPDATE player_match_bowling SET team_id = ? WHERE player_id = ?", (assigned_tid, pid))
        updated_count += 1
        print(f"Re-assigned {name} -> {assigned_country} (Team ID: {assigned_tid})")
    else:
        # If not an international player, remove from India (assign to League/Other team or clean up)
        cur.execute("UPDATE players SET team_id = 999, country = 'Other' WHERE player_id = ? AND team_id = 2", (pid,))

conn.commit()

# Final audit
cur.execute("SELECT count(*), country, team_id FROM players WHERE team_id = 2 GROUP BY country")
print("\nIndia roster after cleanup:", cur.fetchall())

cur.execute("SELECT full_name, country FROM players WHERE team_id = 11 AND (full_name LIKE '%Quinton%' OR full_name LIKE '%Rabada%')")
print("South Africa stars:", cur.fetchall())

conn.close()
print(f"Cleaned up player assignments. Updated {updated_count} players.")

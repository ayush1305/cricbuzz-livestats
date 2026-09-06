"""
Data Synchronizer for Cricbuzz LiveStats.
Pulls real-time data directly from Cricbuzz RapidAPI.
Contains ZERO fake data.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.sync_api_data import sync_real_data


def seed_all_data(db_url=None):
    """Syncs real-time international data from the Cricbuzz API."""
    sync_real_data(db_url)


if __name__ == "__main__":
    seed_all_data()

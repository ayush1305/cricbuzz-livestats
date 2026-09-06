"""
Test runner to verify that all 25 SQL queries execute successfully
and return non-empty dataframes without errors.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import execute_query
from utils.sql_catalog import SQL_QUESTIONS

def test_all_25_queries():
    print(f"Testing execution of all {len(SQL_QUESTIONS)} SQL practice queries...")
    passed = 0
    failed = 0

    for item in SQL_QUESTIONS:
        qid = item["id"]
        title = item["title"]
        difficulty = item["difficulty"]
        sql = item["sql"]

        start_time = time.time()
        try:
            df = execute_query(sql)
            elapsed_ms = (time.time() - start_time) * 1000
            row_count = len(df)
            print(f"[{difficulty:12}] Q{qid:02d}: {title[:40]:<40} -> {row_count} rows in {elapsed_ms:.1f}ms")
            passed += 1
        except Exception as e:
            print(f"[FAILED      ] Q{qid:02d}: {title} -> ERROR: {str(e)}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed out of {len(SQL_QUESTIONS)} queries.")
    print("="*60)
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    test_all_25_queries()

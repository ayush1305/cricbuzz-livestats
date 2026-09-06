"""
Entrypoint alias for Cricbuzz LiveStats (main.py).
Executes the Streamlit application app.py.
"""

import sys
import os

# Redirect execution to app.py
if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    os.system(f"streamlit run {app_path}")
else:
    # When executed via streamlit run main.py
    import app

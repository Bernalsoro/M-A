"""
Entry point for Streamlit Cloud deployment.
This file redirects to the actual dashboard app.
Updated: Added interactive filters to all charts
"""

import sys
from pathlib import Path

# Add liquidity_dashboard/src to path
dashboard_src = Path(__file__).parent / "liquidity_dashboard" / "src"
sys.path.insert(0, str(dashboard_src))

# Import and run the dashboard
from dashboard_app import main

if __name__ == "__main__":
    main()

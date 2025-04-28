import os

# Configuration constants for the Movie ELO Battler

# --- Base Directory ---
# Get the directory where this config file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data') # Define the data directory path

# --- File Paths ---
# Construct full paths using os.path.join
MOVIES_CSV = os.path.join(DATA_DIR, 'movies_with_posters.csv') # Main movie info + ELO rating
MOVIE_DATA_CSV = os.path.join(DATA_DIR, 'movie_metadata.csv')   # Tracks comparisons, W/L/D
FIGHTS_CSV = os.path.join(DATA_DIR, 'head_to_head.csv')       # Comparison history log

# --- ELO Parameters ---
DEFAULT_ELO = 1200
# K-Factor tiers based on min comparisons in a matchup
K_TIERS = {
    15: 64,        # High K for new movies (< 15 comparisons)
    50: 40,        # Medium K for established movies (15-50 comparisons)
    float('inf'): 24 # Lower K for well-ranked movies (> 50 comparisons)
}

# --- UI Parameters ---
POSTER_WIDTH = 180 # Adjust poster size in pixels

# --- Slider Outcome Mapping ---
SLIDER_OPTIONS = ["A Much Better", "A Slightly Better", "Even / Tie", "B Slightly Better", "B Much Better"]
SCORE_MAP = {
    "A Much Better": 1.0,
    "A Slightly Better": 0.75,
    "Even / Tie": 0.5,
    "B Slightly Better": 0.25,
    "B Much Better": 0.0
}

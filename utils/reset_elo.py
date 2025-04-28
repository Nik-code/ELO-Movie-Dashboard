import pandas as pd
import os
import sys

# --- Configuration ---
# Construct paths relative to the script's *parent* directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # utils directory
BASE_DIR = os.path.dirname(SCRIPT_DIR) # Parent directory (Movie_Elo)
DATA_DIR = os.path.join(BASE_DIR, 'data') # Path to data directory

MOVIES_CSV = os.path.join(DATA_DIR, 'movies_with_posters.csv') # File with ratings to reset
MOVIE_DATA_CSV = os.path.join(DATA_DIR, 'movie_metadata.csv')   # Metadata file to reset/clear
FIGHTS_CSV = os.path.join(DATA_DIR, 'head_to_head.csv')       # History file to clear
DEFAULT_ELO = 1200

# --- Main Reset Logic ---
if __name__ == "__main__":
    print("--- Starting ELO Reset ---")
    print(f"Looking for data files in: {DATA_DIR}")

    # 1. Reset Ratings in Main Movie File
    if os.path.exists(MOVIES_CSV):
        try:
            print(f"Reading {MOVIES_CSV} to reset ratings...")
            df = pd.read_csv(MOVIES_CSV)
            if 'Rating' in df.columns:
                df['Rating'] = DEFAULT_ELO
                df.to_csv(MOVIES_CSV, index=False)
                print(f"Ratings in {MOVIES_CSV} reset to {DEFAULT_ELO}.")
            else:
                print(f"Warning: 'Rating' column not found in {MOVIES_CSV}. Cannot reset ratings.")
        except Exception as e:
            print(f"Error processing {MOVIES_CSV}: {e}")
    else:
        print(f"Warning: {MOVIES_CSV} not found. Skipping rating reset.")

    # 2. Reset/Clear Metadata File
    if os.path.exists(MOVIE_DATA_CSV):
        try:
            print(f"Resetting data in {MOVIE_DATA_CSV}...")
            # Re-initialize with 0s based on main movie file
            if os.path.exists(MOVIES_CSV) and 'Title' in pd.read_csv(MOVIES_CSV, nrows=0).columns:
                 movies_df = pd.read_csv(MOVIES_CSV)
                 titles = movies_df['Title'].drop_duplicates().tolist()
                 meta_df = pd.DataFrame(0, index=titles, columns=['Comparisons', 'Wins', 'Losses', 'Draws'])
                 meta_df.index.name = 'Title'
                 meta_df.reset_index().to_csv(MOVIE_DATA_CSV, index=False)
                 print(f"{MOVIE_DATA_CSV} re-initialized with 0 counts.")
            else:
                 # Fallback: Just clear the file if main movie file isn't available
                 print(f"Warning: Cannot read titles from {MOVIES_CSV}. Clearing {MOVIE_DATA_CSV} instead.")
                 with open(MOVIE_DATA_CSV, 'w') as f:
                     f.write("Title,Comparisons,Wins,Losses,Draws\n") # Write header only

        except Exception as e:
            print(f"Error processing {MOVIE_DATA_CSV}: {e}")
    else:
        print(f"Info: {MOVIE_DATA_CSV} not found. Nothing to reset.")

    # 3. Clear Fights History File
    if os.path.exists(FIGHTS_CSV):
        try:
            print(f"Clearing {FIGHTS_CSV}...")
            # Try to get header
            try:
                header = pd.read_csv(FIGHTS_CSV, nrows=0).columns.tolist()
                header_line = ','.join(header) + '\n'
            except Exception:
                print("Warning: Could not read header from fights file. Using default.")
                header_line = "Movie A,Movie B,Outcome,Score A\n" # Assume default header

            # Write only the header back
            with open(FIGHTS_CSV, 'w') as f:
                f.write(header_line)
            print(f"{FIGHTS_CSV} cleared (header kept).")
        except Exception as e:
            print(f"Could not clear {FIGHTS_CSV}: {e}")
    else:
        print(f"Info: {FIGHTS_CSV} not found. Nothing to clear.")

    print("--- Reset Complete ---")


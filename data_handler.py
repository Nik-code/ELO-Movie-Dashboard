import pandas as pd
import os
import streamlit as st # Used only for st.error/st.warning/st.info
# Import constants from the config file
from config import DEFAULT_ELO, MOVIE_DATA_CSV

# Note: MOVIES_CSV is passed as an argument now where needed

# @st.cache_data # Removed cache
def load_movie_data(filename):
    """Loads main movie data (Title, Genres, PosterURL, Rating)."""
    if not os.path.exists(filename):
        st.error(f"Error: Movie data file '{filename}' not found!")
        return pd.DataFrame(columns=['Title', 'Genres', 'PosterURL', 'Rating'])
    try:
        df = pd.read_csv(filename, keep_default_na=False, na_values=[''])
        required_cols = ['Title', 'Genres', 'Rating']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Error: Required column '{col}' missing from '{filename}'.")
                return pd.DataFrame(columns=['Title', 'Genres', 'PosterURL', 'Rating'])

        if 'PosterURL' not in df.columns: df['PosterURL'] = ''
        df['PosterURL'] = df['PosterURL'].fillna('')
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(DEFAULT_ELO).astype(int)
        if 'Genres' in df.columns:
            df['Genres'] = df['Genres'].fillna('Unknown').astype(str).replace(r'^\s*$', 'Unknown', regex=True)
        else: df['Genres'] = 'Unknown'
        df['Title'] = df['Title'].fillna('Untitled').astype(str)

        if df['Title'].duplicated().any():
            st.warning("Duplicate titles found! Keeping first occurrence.")
            df = df.drop_duplicates(subset=['Title'], keep='first')

        final_cols = ['Title', 'Genres', 'PosterURL', 'Rating']
        other_cols = [col for col in df.columns if col not in final_cols]
        df = df[final_cols + other_cols].set_index('Title', drop=False) # Set Title as index
        return df
    except Exception as e:
        st.error(f"Error loading '{filename}': {e}")
        return pd.DataFrame(columns=['Title', 'Genres', 'PosterURL', 'Rating'])

def load_movie_metadata(filename=MOVIE_DATA_CSV, movie_titles=None):
    """Loads or initializes metadata (Comparisons, Wins, Losses, Draws)."""
    required_meta_cols = ['Comparisons', 'Wins', 'Losses', 'Draws']
    if os.path.exists(filename):
        try:
            meta_df = pd.read_csv(filename).set_index('Title')
            if not all(col in meta_df.columns for col in required_meta_cols):
                 raise ValueError("Metadata file missing required columns.")
            # Add any new movies found in the main list but not in metadata
            if movie_titles is not None:
                current_titles = set(movie_titles)
                meta_titles = set(meta_df.index)
                missing_titles = current_titles - meta_titles
                if missing_titles:
                    print(f"Adding {len(missing_titles)} new movies to metadata.")
                    new_meta_rows = pd.DataFrame(0, index=list(missing_titles), columns=required_meta_cols)
                    meta_df = pd.concat([meta_df, new_meta_rows])
            return meta_df
        except Exception as e:
            st.error(f"Error loading metadata file '{filename}': {e}. Reinitializing.")
            # Fallback to initializing if load fails

    # Initialize if file doesn't exist or load failed
    if movie_titles is not None:
        st.info(f"Initializing metadata file '{filename}'.")
        return pd.DataFrame(0, index=movie_titles, columns=required_meta_cols)
    else:
        st.error("Cannot initialize metadata without movie titles list.")
        return pd.DataFrame(columns=required_meta_cols).set_index('Title')

def save_movie_data(df, filename):
    """Saves the main movie DataFrame (including updated ratings)."""
    try:
        save_df = df.reset_index(drop=True)
        final_cols = ['Title', 'Genres', 'PosterURL', 'Rating']
        other_cols = [col for col in save_df.columns if col not in final_cols]
        save_df = save_df[final_cols + other_cols]
        save_df.to_csv(filename, index=False)
    except Exception as e:
        st.error(f"Error saving main data '{filename}': {e}")

def save_movie_metadata(meta_df, filename=MOVIE_DATA_CSV):
    """Saves the movie metadata DataFrame."""
    try:
        meta_df.reset_index().to_csv(filename, index=False)
    except Exception as e:
        st.error(f"Error saving metadata '{filename}': {e}")

def log_fight(movie_a_title, movie_b_title, outcome_description, score_a, filename):
    """Logs the comparison result to the history file."""
    new_fight = pd.DataFrame({
        'Movie A': [movie_a_title], 'Movie B': [movie_b_title],
        'Outcome': [outcome_description], 'Score A': [score_a]
    })
    try:
        if not os.path.exists(filename):
            new_fight.to_csv(filename, index=False)
        else:
            new_fight.to_csv(filename, mode='a', header=False, index=False)
    except Exception as e:
        st.error(f"Error saving fight to '{filename}': {e}")


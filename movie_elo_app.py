import streamlit as st
import pandas as pd
import os
# Import functions and constants from other modules
import config
from elo_logic import get_k_factor, update_elo
from data_handler import load_movie_data, load_movie_metadata, save_movie_data, save_movie_metadata, log_fight
from selection_logic import select_movie_pair

# --- Streamlit App ---
st.set_page_config(page_title="Movie ELO Battler", layout="wide")
st.title("🎬 Movie ELO Battler!")
st.write(f"Hey Nik! Let's rank some movies!")

# --- Initialize Session State ---
# Load data into session state ONCE at the start
if 'movies_df' not in st.session_state:
    st.session_state.movies_df = load_movie_data(config.MOVIES_CSV)
    if st.session_state.movies_df.empty:
        st.error("Initial movie data load failed. Cannot continue.")
        st.stop()
    if len(st.session_state.movies_df) < 2:
        st.warning("Not enough movies loaded to start comparisons.")
        st.stop()

if 'meta_df' not in st.session_state:
     if 'movies_df' in st.session_state and not st.session_state.movies_df.empty:
          # Pass the list of titles from the already loaded movies_df
          st.session_state.meta_df = load_movie_metadata(
              filename=config.MOVIE_DATA_CSV,
              movie_titles=st.session_state.movies_df.index.tolist()
          )
     else:
          st.error("Cannot load metadata because movie data is not available.")
          # Create an empty placeholder to avoid errors later
          st.session_state.meta_df = pd.DataFrame(columns=['Comparisons', 'Wins', 'Losses', 'Draws']).set_index('Title')

# Initialize other session state variables
if 'show_dashboard' not in st.session_state: st.session_state.show_dashboard = False
if 'current_pair_titles' not in st.session_state: st.session_state.current_pair_titles = None

# --- Main Logic ---
# Get data from session state for use in the current run
movies_df = st.session_state.movies_df
meta_df = st.session_state.meta_df

# --- Comparison Mode ---
if not st.session_state.show_dashboard:
    st.header("🥊 Rate the Matchup!")

    # Select a pair if none is currently selected
    if st.session_state.current_pair_titles is None:
        if len(movies_df) >= 2:
             # Use the imported selection logic
             title_a, title_b = select_movie_pair(movies_df, meta_df)
             if title_a and title_b:
                  st.session_state.current_pair_titles = (title_a, title_b)
             else:
                  st.error("Failed to select a valid movie pair. Please check data.")
                  st.stop()
        else:
            st.warning("Need at least two movies to compare!")
            st.stop()

    # Get data for the current pair
    try:
        title_a, title_b = st.session_state.current_pair_titles
        # Verify titles exist before accessing .loc to prevent KeyErrors
        if title_a not in movies_df.index or title_b not in movies_df.index:
             raise KeyError(f"Title '{title_a}' or '{title_b}' not found in movies_df.")
        if title_a not in meta_df.index or title_b not in meta_df.index:
             raise KeyError(f"Title '{title_a}' or '{title_b}' not found in meta_df.")

        movie_a = movies_df.loc[title_a]
        movie_b = movies_df.loc[title_b]
        meta_a = meta_df.loc[title_a]
        meta_b = meta_df.loc[title_b]

    except KeyError as e: # Handle cases where data might be missing after loading
         st.error(f"Error accessing movie data or metadata: {e}. Reloading pair...")
         st.session_state.current_pair_titles = None
         st.rerun()
    except Exception as e: # Catch other potential errors during access
         st.error(f"An unexpected error occurred: {e}. Reloading pair...")
         st.session_state.current_pair_titles = None
         st.rerun()

    # --- Display Movies Side-by-Side ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"A: {movie_a['Title']}")
        poster_a_url = movie_a.get('PosterURL', '')
        # Display poster or placeholder
        if isinstance(poster_a_url, str) and poster_a_url.startswith('http'):
             st.image(poster_a_url, width=config.POSTER_WIDTH)
        else:
             st.markdown(f'<div style="height:{int(config.POSTER_WIDTH*1.5)}px; display:flex; align-items:center; justify-content:center; border:1px dashed gray; color:gray;">(No Poster)</div>', unsafe_allow_html=True)
        st.caption(f"Genre: {movie_a.get('Genres', 'N/A')}")
        st.caption(f"Rating: {movie_a.get('Rating', 'N/A')} | Comparisons: {int(meta_a.get('Comparisons', 0))}")

    with col_b:
        st.subheader(f"B: {movie_b['Title']}")
        poster_b_url = movie_b.get('PosterURL', '')
        # Display poster or placeholder
        if isinstance(poster_b_url, str) and poster_b_url.startswith('http'):
             st.image(poster_b_url, width=config.POSTER_WIDTH)
        else:
             st.markdown(f'<div style="height:{int(config.POSTER_WIDTH*1.5)}px; display:flex; align-items:center; justify-content:center; border:1px dashed gray; color:gray;">(No Poster)</div>', unsafe_allow_html=True)
        st.caption(f"Genre: {movie_b.get('Genres', 'N/A')}")
        st.caption(f"Rating: {movie_b.get('Rating', 'N/A')} | Comparisons: {int(meta_b.get('Comparisons', 0))}")

    st.markdown("---") # Separator

    # --- Slider for Outcome Selection ---
    # Use constants from config
    outcome = st.select_slider(
        'Select the outcome:',
        options=config.SLIDER_OPTIONS,
        value="Even / Tie" # Default slider position
    )
    # Use constants from config
    score_a = config.SCORE_MAP.get(outcome, 0.5) # Default to 0.5 if outcome is unexpected

    # --- Submit and Skip Buttons ---
    submit_col, skip_col = st.columns([3, 1]) # Adjust button width ratio if needed
    with submit_col:
        if st.button("Submit Result", key="submit", use_container_width=True):
            # --- Perform Updates ---
            # 1. Get comparison counts & determine K-Factor
            comparisons_a = meta_a.get('Comparisons', 0)
            comparisons_b = meta_b.get('Comparisons', 0)
            k = get_k_factor(comparisons_a, comparisons_b) # From elo_logic

            # 2. Update ELO ratings
            new_rating_a, new_rating_b = update_elo(movie_a['Rating'], movie_b['Rating'], score_a, k) # From elo_logic
            # Update DataFrames stored in session state
            st.session_state.movies_df.loc[title_a, 'Rating'] = new_rating_a
            st.session_state.movies_df.loc[title_b, 'Rating'] = new_rating_b

            # 3. Update metadata (Comparisons, W/L/D)
            st.session_state.meta_df.loc[title_a, 'Comparisons'] += 1
            st.session_state.meta_df.loc[title_b, 'Comparisons'] += 1
            if outcome == "Even / Tie":
                st.session_state.meta_df.loc[title_a, 'Draws'] += 1
                st.session_state.meta_df.loc[title_b, 'Draws'] += 1
            elif outcome in ["A Much Better", "A Slightly Better"]:
                st.session_state.meta_df.loc[title_a, 'Wins'] += 1
                st.session_state.meta_df.loc[title_b, 'Losses'] += 1
            elif outcome in ["B Much Better", "B Slightly Better"]:
                st.session_state.meta_df.loc[title_a, 'Losses'] += 1
                st.session_state.meta_df.loc[title_b, 'Wins'] += 1

            # --- Logging & Saving ---
            log_fight(movie_a['Title'], movie_b['Title'], outcome, score_a, config.FIGHTS_CSV) # From data_handler
            st.session_state.current_pair_titles = None # Ensure a new pair is selected next time

            # Save updated data to files using functions from data_handler
            save_movie_data(st.session_state.movies_df, config.MOVIES_CSV)
            save_movie_metadata(st.session_state.meta_df, config.MOVIE_DATA_CSV)

            # Rerun the script to display the next pair
            st.rerun()

    with skip_col:
        if st.button("Skip", key="skip", use_container_width=True):
            # Just get a new pair, don't update/save anything
            st.session_state.current_pair_titles = None
            st.rerun()

    st.markdown("---")
    # --- Done Comparing Button ---
    if st.button("✅ Done Comparing (Show Dashboard)"):
        st.session_state.show_dashboard = True
        # Save data one last time before switching view
        save_movie_data(st.session_state.movies_df, config.MOVIES_CSV)
        save_movie_metadata(st.session_state.meta_df, config.MOVIE_DATA_CSV)
        st.rerun()


# --- Dashboard Mode ---
else:
    st.header("📊 Movie ELO Dashboard")

    # Button to switch back to comparison mode
    if st.button("🔙 Compare More Movies"):
        st.session_state.show_dashboard = False
        st.session_state.current_pair_titles = None # Clear current pair
        st.rerun()

    # --- Prepare Data for Dashboard ---
    # Ensure metadata is loaded correctly before joining
    if 'meta_df' not in st.session_state or st.session_state.meta_df.empty:
         st.warning("Metadata not loaded, attempting reload...")
         if 'movies_df' in st.session_state and not st.session_state.movies_df.empty:
              st.session_state.meta_df = load_movie_metadata(
                  filename=config.MOVIE_DATA_CSV,
                  movie_titles=st.session_state.movies_df.index.tolist()
              )
         else:
             st.error("Cannot reload metadata as movie data is missing.")
             st.stop() # Stop if essential data is missing

    # Proceed only if meta_df is valid
    if not st.session_state.meta_df.empty:
        # Join movie data with metadata
        ranked_movies_base = st.session_state.movies_df.join(st.session_state.meta_df, how='left')
        # Fill NaN stats with 0 and ensure integer type
        stat_cols = ['Comparisons', 'Wins', 'Losses', 'Draws']
        for col in stat_cols:
            if col not in ranked_movies_base.columns: ranked_movies_base[col] = 0
            else: ranked_movies_base[col] = ranked_movies_base[col].fillna(0).astype(int)
        # Sort by Rating (ensure it's int first)
        ranked_movies_base = ranked_movies_base.astype({'Rating': 'int'}).sort_values('Rating', ascending=False).reset_index(drop=True) # Drop old index

        # --- Search Filter ---
        st.subheader("🏆 Overall Rankings")
        search_term = st.text_input("Search Titles:", key="ranking_search")
        # Apply filter
        if search_term:
            ranked_movies_filtered = ranked_movies_base[ranked_movies_base['Title'].str.contains(search_term, case=False, na=False)]
        else:
            ranked_movies_filtered = ranked_movies_base

        # --- Display Rankings Table ---
        display_cols = ['Title', 'Rating', 'Comparisons', 'Wins', 'Losses', 'Draws', 'Genres']
        # Ensure all columns exist before displaying
        display_cols = [col for col in display_cols if col in ranked_movies_filtered.columns]
        st.dataframe(ranked_movies_filtered[display_cols])
        st.caption(f"Showing {len(ranked_movies_filtered)} out of {len(ranked_movies_base)} movies.")
    else:
         st.error("Could not display rankings because metadata failed to load.")


    # --- Display Genre Insights ---
    st.subheader("🎭 Insights by Genre")
    try:
        # Use the main movies_df from session state for this calculation
        # Reset index if 'Title' is the index, otherwise just copy
        if isinstance(st.session_state.movies_df.index, pd.Index) and st.session_state.movies_df.index.name == 'Title':
             movies_df_for_genre = st.session_state.movies_df.reset_index(drop=True)
        else:
             movies_df_for_genre = st.session_state.movies_df.copy()

        # Ensure required columns exist in the copy
        if 'Title' not in movies_df_for_genre.columns or 'Genres' not in movies_df_for_genre.columns or 'Rating' not in movies_df_for_genre.columns:
             raise ValueError("Required columns missing for genre analysis.")

        movies_df_for_genre['Genres'] = movies_df_for_genre['Genres'].fillna('').astype(str)
        # Explode genres for analysis
        genres_expanded = movies_df_for_genre.assign(Genre=movies_df_for_genre['Genres'].str.split('|')).explode('Genre')

        # Clean up the resulting 'Genre' column
        genres_expanded['Genre'] = genres_expanded['Genre'].str.strip()
        genres_expanded = genres_expanded[(genres_expanded['Genre'] != '') & (genres_expanded['Genre'] != 'Unknown')]

        if not genres_expanded.empty:
            # Group by the new 'Genre' column and calculate stats
            genre_stats = genres_expanded.groupby('Genre')['Rating'].agg(['mean', 'count']).sort_values(['mean', 'count'], ascending=False)
            genre_stats.rename(columns={'mean': 'Average Rating', 'count': 'Movie Count'}, inplace=True)
            genre_stats['Average Rating'] = genre_stats['Average Rating'].round(0).astype(int)
            # Display stats, optionally filter for genres with > 1 movie
            st.dataframe(genre_stats[genre_stats['Movie Count'] > 1])
        else:
            st.write("No valid genre information available for insights.")
    except Exception as e:
        # Print the specific error to help diagnose
        st.error(f"Could not generate genre insights: {e}")
        # import traceback # Uncomment for detailed traceback during debugging
        # st.text(traceback.format_exc())


    # --- Display Comparison History ---
    st.subheader("📜 Comparison History")
    if os.path.exists(config.FIGHTS_CSV):
        try:
            fights_df = pd.read_csv(config.FIGHTS_CSV)
            # Display relevant columns based on current format
            display_hist_cols = ['Movie A', 'Movie B', 'Outcome', 'Score A']
            display_hist_cols = [col for col in display_hist_cols if col in fights_df.columns] # Filter existing columns
            st.dataframe(fights_df[display_hist_cols].tail(20)) # Show last 20
        except Exception as e:
            st.warning(f"Could not display comparison history: {e}")
    else:
        st.write("No comparison history recorded yet.")


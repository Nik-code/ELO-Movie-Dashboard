import pandas as pd
import requests
import time
import os
from tqdm import tqdm
import numpy as np # To check for NaN values properly
import sys # To exit gracefully

# --- Configuration ---
# Construct paths relative to the script's *parent* directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # utils directory
BASE_DIR = os.path.dirname(SCRIPT_DIR) # Parent directory (Movie_Elo)
DATA_DIR = os.path.join(BASE_DIR, 'data') # Path to data directory

# File to read from and update
TARGET_CSV = os.path.join(DATA_DIR, 'movies_with_posters.csv')

# !!! IMPORTANT: Replace with your actual TMDb API Key (v3 auth) !!!
# Get a free key from https://www.themoviedb.org/settings/api
TMDB_API_KEY = 'YOUR_TMDB_API_KEY_HERE' # Placeholder - DO NOT COMMIT YOUR ACTUAL KEY

# --- TMDb API Settings ---
TMDB_POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500' # w500 is a common poster size
REQUEST_DELAY = 0.5 # Delay between API requests (in seconds) - be respectful!
RETRY_ATTEMPTS = 2    # How many times to retry on connection errors
RETRY_DELAY = 3       # How many seconds to wait before retrying connection errors
API_TIMEOUT = 10      # Seconds to wait for API response

# --- Script Settings ---
SAVE_INTERVAL = 20    # Save progress every X movies processed

# --- Helper Function to Get Poster URL (with retries) ---
def get_poster_url(movie_title, api_key):
    """
    Fetches the movie poster URL from TMDb based on the title.
    Includes retries for connection errors.

    Args:
        movie_title (str): The title of the movie to search for.
        api_key (str): Your TMDb API key (v3 auth).

    Returns:
        str or None: The full URL to the poster image (w500 size) or None if not found/error.
    """
    # Basic validation
    if not isinstance(movie_title, str) or not movie_title.strip():
        print(f"  Invalid movie title provided: {movie_title}")
        return None
    if not api_key or api_key == 'YOUR_TMDB_API_KEY_HERE':
        # Don't proceed without a valid API key placeholder being replaced
        if attempts == 0: # Only print this warning once per movie title
             print(f"  Skipping '{movie_title}': API key is missing or still set to placeholder.")
        return None

    search_url = f"https://api.themoviedb.org/3/search/movie"
    params = {'api_key': api_key, 'query': movie_title}
    attempts = 0

    while attempts <= RETRY_ATTEMPTS:
        try:
            # --- Search for movie ID ---
            response = requests.get(search_url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if not data.get('results'): # Check if 'results' key exists and is not empty
                # print(f"  No TMDb results found for '{movie_title}'") # Optional: uncomment for more detail
                return None # No results found, don't retry

            # Assume the first result is the most relevant
            first_result = data['results'][0]
            movie_id = first_result.get('id')
            if not movie_id:
                 print(f"  Found result for '{movie_title}' but missing movie ID.")
                 return None # Cannot proceed without ID

            # --- Get movie details for poster path ---
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            details_params = {'api_key': api_key}
            details_response = requests.get(details_url, params=details_params, timeout=API_TIMEOUT)
            details_response.raise_for_status()
            details_data = details_response.json()

            poster_path = details_data.get('poster_path')
            if poster_path and isinstance(poster_path, str):
                # Successfully found poster path
                return f"{TMDB_POSTER_BASE_URL}{poster_path}"
            else:
                # Movie found, but no poster path available
                # print(f"  Movie '{movie_title}' (ID: {movie_id}) found, but no poster path.") # Optional
                return None # Don't retry if poster path is missing

        except requests.exceptions.ConnectionError as e:
            attempts += 1
            print(f"  Connection error for '{movie_title}' (Attempt {attempts}/{RETRY_ATTEMPTS+1}). Retrying in {RETRY_DELAY}s...")
            if attempts > RETRY_ATTEMPTS:
                print(f"  Failed to fetch '{movie_title}' after multiple connection retries.")
                return None # Max retries exceeded
            time.sleep(RETRY_DELAY) # Wait before retrying connection errors

        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors (like 401 Unauthorized, 404 Not Found on details)
            print(f"  HTTP error fetching data for '{movie_title}': {e}. No retry.")
            return None # Don't retry HTTP errors other than potential rate limits (which requests might handle)

        except requests.exceptions.Timeout:
            print(f"  Timeout fetching data for '{movie_title}'. No retry.")
            return None # Don't retry timeouts

        except requests.exceptions.RequestException as e:
            # Handle other potential request errors
            print(f"  Request error fetching data for '{movie_title}': {e}. No retry.")
            return None

        except Exception as e:
            # Catch any other unexpected errors during API interaction
            print(f"  An unexpected error occurred processing '{movie_title}': {e}")
            import traceback
            traceback.print_exc() # Print detailed traceback for unexpected errors
            return None # Don't retry unknown errors

    # This should only be reached if all retry attempts failed due to ConnectionError
    return None


# --- Main Script Logic ---
if __name__ == "__main__":
    print("--- Movie Poster Fetcher ---")
    print(f"Looking for movie list in: {TARGET_CSV}")

    # Check if API key has been replaced
    if not TMDB_API_KEY or TMDB_API_KEY == 'YOUR_TMDB_API_KEY_HERE':
         print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
         print("!!! ERROR: Please replace 'YOUR_TMDB_API_KEY_HERE' in this script !!!")
         print("!!! with your actual TMDb API key before running.              !!!")
         print("!!! Get a free key from https://www.themoviedb.org/settings/api !!!")
         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
         sys.exit(1) # Exit the script if key is missing

    # Check if target CSV exists
    if not os.path.exists(TARGET_CSV):
        print(f"\nError: Target file '{TARGET_CSV}' not found.")
        print("Please ensure the movie list CSV exists in the 'data' folder.")
        sys.exit(1)

    # --- Load Data ---
    try:
        # Read the target CSV, keep empty strings as '' for easier checking later
        df = pd.read_csv(TARGET_CSV, keep_default_na=False, na_values=[''])
        print(f"Successfully read {len(df)} movies from {TARGET_CSV}.")
    except Exception as e:
         print(f"\nError reading {TARGET_CSV}: {e}")
         sys.exit(1)

    # --- Validate Columns ---
    if 'Title' not in df.columns:
        print("\nError: 'Title' column not found in the CSV.")
        sys.exit(1)
    if 'PosterURL' not in df.columns:
        print("\nAdding missing 'PosterURL' column.")
        # Add PosterURL before Rating if Rating exists, otherwise at the end
        if 'Rating' in df.columns:
            rating_col_index = df.columns.get_loc('Rating')
            df.insert(rating_col_index, 'PosterURL', '') # Initialize with empty string
        else:
            df['PosterURL'] = '' # Initialize with empty string
        # Ensure it's treated as string
        df['PosterURL'] = df['PosterURL'].astype(str)

    # Ensure PosterURL is string type for checks
    df['PosterURL'] = df['PosterURL'].astype(str)

    # --- Identify Movies Needing Fetching ---
    print(f"\nChecking {len(df)} movies for missing poster URLs...")
    # Find rows where PosterURL is empty or doesn't start with http
    missing_mask = ~df['PosterURL'].str.startswith('http', na=False)
    movies_to_fetch_indices = df[missing_mask].index.tolist()

    print(f"Found {len(movies_to_fetch_indices)} movies needing poster URLs fetched.")

    if not movies_to_fetch_indices:
        print("No missing poster URLs found. Exiting.")
        sys.exit(0)

    # --- Fetching Loop ---
    fetched_count = 0
    update_count = 0
    # Use tqdm for a progress bar only on the movies we need to fetch
    for index in tqdm(movies_to_fetch_indices, desc="Fetching missing posters"):
        # Get title safely
        title = df.loc[index, 'Title']
        if not isinstance(title, str) or not title.strip():
            print(f"  Skipping row index {index}: Missing or invalid title.")
            continue

        # Fetch the URL
        fetched_url = get_poster_url(title, TMDB_API_KEY)
        fetched_count += 1

        # Update DataFrame only if a valid URL was fetched
        if fetched_url:
            df.loc[index, 'PosterURL'] = fetched_url
            update_count += 1
        else:
            # Keep existing value (which should be empty or non-URL)
            pass

        # Add a small delay between API calls
        time.sleep(REQUEST_DELAY)

        # Save progress periodically
        if fetched_count > 0 and fetched_count % SAVE_INTERVAL == 0:
            print(f"\n--- Saving progress ({fetched_count}/{len(movies_to_fetch_indices)} fetched attempts) ---")
            try:
                df.to_csv(TARGET_CSV, index=False)
                print(f"Progress saved to {TARGET_CSV}")
            except Exception as e:
                print(f"  Error saving intermediate progress: {e}")

    # --- Final Summary and Save ---
    print(f"\nFinished fetching attempts.")
    print(f"Successfully fetched and updated {update_count} new poster URLs.")

    # Final save
    print(f"\nSaving final updated data to: {TARGET_CSV}")
    try:
        df.to_csv(TARGET_CSV, index=False)
        # Recalculate final counts after saving
        final_df = pd.read_csv(TARGET_CSV, keep_default_na=False, na_values=[''])
        final_df['PosterURL'] = final_df['PosterURL'].astype(str)
        success_count = final_df['PosterURL'].str.startswith('http', na=False).sum()
        total_count = len(final_df)
        fail_count = total_count - success_count

        print(f"\n--- Final Summary ---")
        print(f"Total movies in file: {total_count}")
        print(f"Movies with posters now: {success_count}")
        if fail_count > 0:
            print(f"Movies still missing posters: {fail_count}")
        print("Done!")

    except Exception as e:
        print(f"\nError saving final file: {e}")


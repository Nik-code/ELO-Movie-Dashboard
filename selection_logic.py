import pandas as pd
import random
import numpy as np

def select_movie_pair(movies_df, meta_df):
    """
    Selects a pair of movies for comparison, prioritizing movies with fewer comparisons.

    Args:
        movies_df (pd.DataFrame): DataFrame containing movie titles as index.
        meta_df (pd.DataFrame): DataFrame containing metadata, including 'Comparisons'.

    Returns:
        tuple: A tuple containing two distinct movie titles, or (None, None) if selection fails.
    """
    if len(movies_df) < 2:
        print("Not enough movies to select a pair.")
        return None, None

    # Ensure metadata is aligned with movie list and has 'Comparisons'
    try:
        # Align meta_df with movies_df index, fill missing comparisons with 0
        aligned_meta = meta_df.reindex(movies_df.index).fillna({'Comparisons': 0})
        comparisons = aligned_meta['Comparisons'].astype(int)
    except Exception as e:
        print(f"Error aligning metadata for selection: {e}. Using uniform selection.")
        # Fallback to simple random sample if metadata alignment fails
        valid_titles = movies_df.index.tolist()
        return random.sample(valid_titles, 2)

    # Calculate weights: Higher weight for fewer comparisons
    # Adding 1 avoids division by zero and gives 0-comparison movies highest weight.
    # Using power (e.g., ^2) can increase the priority further.
    weights = 1 / (comparisons + 1)**1.5 # Increase exponent (e.g., 1.5 or 2) for stronger priority

    # Normalize weights to sum to 1 (required by random.choices)
    total_weight = weights.sum()
    if total_weight <= 0: # Handle edge case where all weights might be zero (shouldn't happen with +1)
        print("Warning: Zero total weight during selection. Using uniform selection.")
        valid_titles = movies_df.index.tolist()
        return random.sample(valid_titles, 2)

    probabilities = weights / total_weight

    # Ensure probabilities are valid
    if probabilities.isnull().any() or not np.isclose(probabilities.sum(), 1.0):
         print("Warning: Invalid probabilities calculated. Using uniform selection.")
         valid_titles = movies_df.index.tolist()
         return random.sample(valid_titles, 2)

    # Select the first movie based on weighted probability
    valid_titles = movies_df.index.tolist()
    try:
        title_a = random.choices(valid_titles, weights=probabilities.values, k=1)[0]
    except ValueError as e:
        print(f"Error during weighted choice for title_a: {e}. Using uniform selection.")
        return random.sample(valid_titles, 2)


    # Select the second movie randomly from the remaining titles
    remaining_titles = [t for t in valid_titles if t != title_a]
    if not remaining_titles:
        print("Warning: Only one movie available after selecting the first. Cannot form a pair.")
        # This should only happen if len(movies_df) was 1, which is checked earlier.
        # As a fallback, maybe return the same movie twice? Or handle differently.
        # For now, let's return None, None, though this state shouldn't be reached.
        return None, None

    title_b = random.choice(remaining_titles)

    return title_a, title_b

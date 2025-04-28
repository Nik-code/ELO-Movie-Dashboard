import math
# Import K_TIERS from the config file
from config import K_TIERS

def calculate_expected_score(rating_a, rating_b):
    """Calculates the expected score of player A winning against player B."""
    # Clamp ratings to avoid extreme values if necessary (optional)
    # rating_a = max(1, rating_a)
    # rating_b = max(1, rating_b)
    try:
        exponent = (rating_b - rating_a) / 400.0
        # Avoid potential overflow if ratings are vastly different
        if exponent > 40:  # Corresponds to 10^40, practically 0 probability
            return 0.0
        if exponent < -40: # Corresponds to 10^-40, practically 1 probability
            return 1.0
        return 1.0 / (1.0 + 10.0**exponent)
    except OverflowError:
        # Handle potential overflow if ratings are extremely far apart
        # Determine outcome based on which rating is significantly larger
        return 0.0 if rating_b > rating_a else 1.0


def get_k_factor(comparisons_a, comparisons_b):
    """Determines K-factor based on the minimum comparison count of the two movies."""
    # Ensure comparisons are non-negative integers
    comparisons_a = max(0, int(comparisons_a))
    comparisons_b = max(0, int(comparisons_b))

    min_comparisons = min(comparisons_a, comparisons_b)
    # Iterate through sorted thresholds to find the correct K-factor
    for threshold in sorted(K_TIERS.keys()):
        if min_comparisons <= threshold:
            return K_TIERS[threshold]
    # This part should ideally not be reached if float('inf') is a key
    # Return the K-factor associated with the largest finite threshold or a default
    finite_thresholds = [t for t in K_TIERS if t != float('inf')]
    if finite_thresholds:
        return K_TIERS[max(finite_thresholds)]
    else: # Fallback if K_TIERS is somehow empty or only has infinity
        return 24 # Default fallback K

def update_elo(rating_a, rating_b, score_a, k):
    """Updates the ELO ratings based on the match outcome and specific K-factor."""
    # Ensure ratings are numeric
    rating_a = float(rating_a)
    rating_b = float(rating_b)

    expected_a = calculate_expected_score(rating_a, rating_b)
    # Calculate rating change for A
    change_a = k * (score_a - expected_a)
    new_rating_a = rating_a + change_a

    # Calculate rating change for B (must be opposite of A's change before rounding)
    # Note: score_b = 1 - score_a
    # expected_b = 1 - expected_a
    # change_b = k * (score_b - expected_b) = k * ((1 - score_a) - (1 - expected_a)) = k * (expected_a - score_a) = -change_a
    new_rating_b = rating_b - change_a

    # Optional: Add a minimum ELO floor if desired
    # new_rating_a = max(100, new_rating_a)
    # new_rating_b = max(100, new_rating_b)

    return round(new_rating_a), round(new_rating_b)

# ELO-Movie-Dashboard 🎬📊

Rank your personal movie collection! This Streamlit app uses the ELO rating system, pairwise comparisons with posters, and a dashboard to create and track your personalized film ratings.

## Features

* **ELO Rating System:** Ranks movies based on head-to-head matchups using the standard ELO algorithm.
* **Visual Comparisons:** Shows movie posters side-by-side during rating.
* **Nuanced Input:** Uses a slider ("Much Better", "Slightly Better", "Even", etc.) for more granular rating adjustments.
* **Variable K-Factor:** ELO ratings change more significantly for movies with fewer comparisons, allowing for faster initial ranking and later stability. Configurable in `config.py`.
* **Weighted Selection:** Prioritizes pairing movies that have been compared less often to ensure more even coverage.
* **Skip Option:** Easily skip pairs you can't decide between or don't remember well.
* **Persistent Storage:** Saves ratings (`movies_with_posters.csv`), comparison history (`head_to_head.csv`), and movie metadata (`movie_metadata.csv`) to CSV files in a `data/` directory.
* **Dashboard:** View overall rankings, search/filter movies, see comparison stats (Wins/Losses/Draws), and view basic genre insights.
* **Poster Fetching Utility:** Includes an optional script (`utils/fetch_posters.py`) to automatically find and add poster URLs using the TMDb API.
* **Reset Utility:** Includes a script (`utils/reset_elo.py`) to easily reset all ELO scores and clear comparison history/metadata.

## Project Structure

```
ELO-Movie-Dashboard/├── data/
|   ├── movies_with_posters.csv  # Your movie list, posters, and ratings
|   ├── movie_metadata.csv     # Comparison counts, W/L/D stats (auto-generated)
|   └── head_to_head.csv       # Log of all comparisons made (auto-generated)
├── utils/                 # Utility scripts
|   ├── fetch_posters.py     # Optional script to fetch poster URLs
|   └── reset_elo.py         # Script to reset data
├── config.py              # Configuration constants (file paths, ELO settings)
├── data_handler.py        # Functions for loading/saving CSV data
├── elo_logic.py           # ELO calculation functions
├── selection_logic.py     # Logic for selecting movie pairs
├── movie_elo_app.py       # Main Streamlit application script
├── requirements.txt       # Python dependencies
├── .gitignore             # Specifies intentionally untracked files
├── LICENSE                # Project license (e.g., MIT)
└── README.md              # This file
```

## Setup and Usage

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Nik-code/ELO-Movie-Dashboard.git](https://github.com/Nik-code/ELO-Movie-Dashboard.git)
    cd ELO-Movie-Dashboard
    ```

2.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create `data` Directory:**
    * Manually create a folder named `data` in the root of the project directory. This folder is ignored by git, so it won't exist after cloning.
        ```bash
        mkdir data
        ```

5.  **Prepare Your Movie List (`movies_with_posters.csv`):**
    * Create a CSV file named `movies_with_posters.csv` inside the `data` folder you just created.
    * It **must** have these columns in this order: `Title`, `Genres`, `PosterURL`, `Rating`.
        * `Title`: The exact movie title (should be unique).
        * `Genres`: Pipe-separated genres (e.g., `Action|Adventure|Sci-Fi`). Use `Unknown` if a movie has no listed genres.
        * `PosterURL`: A direct URL to the movie poster image (e.g., ending in `.jpg`). Leave blank if you don't have one or will fetch it later.
        * `Rating`: The ELO rating. Leave blank or set to `1200` (the default) for new movies. The app will assign the default if blank.
    * **Example Row:**
        ```csv
        Title,Genres,PosterURL,Rating
        Inception,"Action|Sci-Fi|Thriller","[https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep2B1QiDKuh.jpg](https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep2B1QiDKuh.jpg)",1550
        Your Name,"Animation|Drama|Romance","",1300
        New Movie,"Comedy|Drama","",
        ```

6.  **Fetch Poster URLs (Optional but Recommended):**
    * If you left `PosterURL` blank for many movies, you can use the included script to fetch them.
    * **Get a TMDb API Key:** Sign up for a free account at [themoviedb.org](https://www.themoviedb.org/) and request an API key (v3 auth) in your account settings.
    * **Edit the Script:** Open `utils/fetch_posters.py` and replace `'YOUR_TMDB_API_KEY_HERE'` with your actual API key. **Do not commit your API key to GitHub!**
    * **Run the Fetcher:** From the project root directory (`ELO-Movie-Dashboard/`), run:
        ```bash
        python utils/fetch_posters.py
        ```
        This will read `data/movies_with_posters.csv`, find missing poster URLs using TMDb, and update the file in place.

7.  **Run the App:**
    * From the project root directory (`ELO-Movie-Dashboard/`), run:
        ```bash
        streamlit run movie_elo_app.py
        ```
    * The app will automatically create `movie_metadata.csv` and `head_to_head.csv` in the `data` folder if they don't exist.

8.  **Resetting Data (Optional):**
    * To reset all ELO scores to the default (1200) and clear comparison history/metadata, run the reset script from the project root directory:
        ```bash
        python utils/reset_elo.py
        ```

## How it Works

* The app presents two movies selected from your list, prioritizing those with fewer comparisons using weighted random selection.
* You use the slider to indicate which movie you prefer and by how much ("A Much Better" to "B Much Better").
* Based on your input and the movies' current ELO ratings, the ELO scores are updated. The magnitude of the change depends on the outcome surprise and a variable K-factor (higher changes for less-compared movies).
* The comparison outcome and movie metadata (comparison counts, W/L/D) are saved to their respective CSV files in the `data/` folder.
* The dashboard shows the current rankings (searchable) and stats.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

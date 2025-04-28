# 🎬📊 ELO-Movie-Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

Rank your personal movie collection!  
This Streamlit app uses the ELO rating system, pairwise comparisons with posters, and a dashboard to create and track your personalized film ratings.

---

## 📸 Preview

![Dashboard Screenshot](assets/Movie%20ELO%20Battler.jpeg)

---

## ✨ Features

- **ELO Rating System:** Ranks movies based on head-to-head matchups using the standard ELO algorithm.
- **Visual Comparisons:** Displays movie posters side-by-side during rating.
- **Nuanced Input:** Slider-based preferences ("Much Better", "Slightly Better", "Even", etc.) for more granular adjustments.
- **Variable K-Factor:** Dynamic ELO adjustment speeds (faster for early rankings, more stable later).
- **Weighted Selection:** Prioritizes under-compared movies for fairer rankings.
- **Skip Option:** Skip undecidable pairs easily.
- **Persistent Storage:** Automatically saves ratings (`movies_with_posters.csv`), history (`head_to_head.csv`), and metadata (`movie_metadata.csv`).
- **Dashboard View:** Search, filter, and view ranking statistics.
- **Poster Fetching Utility:** Script to auto-fetch missing movie posters via TMDb API.
- **Reset Utility:** Script to reset your ELO scores and wipe history when needed.

---

## 🗂️ Project Structure

```
ELO-Movie-Dashboard/
├── data/
│   ├── movies_with_posters.csv
│   ├── movie_metadata.csv
│   └── head_to_head.csv
├── utils/
│   ├── fetch_posters.py
│   └── reset_elo.py
├── config.py
├── data_handler.py
├── elo_logic.py
├── selection_logic.py
├── movie_elo_app.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Setup and Usage

1. **Clone the Repository**
    ```bash
    git clone https://github.com/Nik-code/ELO-Movie-Dashboard.git
    cd ELO-Movie-Dashboard
    ```

2. **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Create the `data/` Directory**
    ```bash
    mkdir data
    ```

5. **Prepare Your Movie List (`movies_with_posters.csv`)**
    Create a CSV inside `/data/` with these columns:
    - `Title`
    - `Genres` (pipe-separated, e.g., `Action|Adventure|Sci-Fi`)
    - `PosterURL` (optional, can fetch later)
    - `Rating` (optional, default is 1200)

    **Example Row:**
    ```csv
    Title,Genres,PosterURL,Rating
    Inception,"Action|Sci-Fi|Thriller","https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep2B1QiDKuh.jpg",1550
    Your Name,"Animation|Drama|Romance","",1300
    ```

6. **(Optional) Fetch Poster URLs via TMDb**
    - Update your API key inside `utils/fetch_posters.py`.
    - Run:
    ```bash
    python utils/fetch_posters.py
    ```

7. **Run the App**
    ```bash
    streamlit run movie_elo_app.py
    ```

8. **Reset Data (Optional)**
    ```bash
    python utils/reset_elo.py
    ```

---

## 🧠 How It Works

- Two movies are presented randomly (weighted to prefer less-compared movies).
- You select which movie you prefer and how strongly.
- The ELO algorithm updates scores based on your input.
- All history and metadata are logged to CSVs for persistence and dashboard display.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

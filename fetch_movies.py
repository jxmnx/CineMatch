
import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
OUTPUT_FILE = "data/multilingual_movies.csv"

LANGUAGES = {
    "ml": "Malayalam",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "en": "English",
}

def fetch_movies(language, pages=3):
    movies = []

    for page in range(1, pages + 1):
        try:
            response = requests.get(
                "https://api.themoviedb.org/3/discover/movie",
                params={
                    "api_key": API_KEY,
                    "with_original_language": language,
                    "sort_by": "popularity.desc",
                    "page": page,
                },
                timeout=20,
            )
            response.raise_for_status()

            for movie in response.json().get("results", []):
                movies.append({
                    "id": movie.get("id"),
                    "title": movie.get("title", ""),
                    "original_language": language,
                    "genres": "",
                    "keywords": "",
                    "overview": movie.get("overview", ""),
                    "vote_average": movie.get("vote_average", 0),
                    "vote_count": movie.get("vote_count", 0),
                    "poster_path": movie.get("poster_path") or "",
                })

            print(f"{LANGUAGES[language]}: fetched page {page}")
            time.sleep(0.3)

        except requests.RequestException as error:
            print(f"Could not fetch {LANGUAGES[language]} page {page}: {error}")
            break

    return movies


def main():
    if not API_KEY:
        print("TMDB_API_KEY is missing from your .env file.")
        return

    os.makedirs("data", exist_ok=True)
    all_movies = []

    for language in LANGUAGES:
        all_movies.extend(fetch_movies(language, pages=3))

    if not all_movies:
        print("No movies fetched. Check your API key and internet connection.")
        return

    new_data = pd.DataFrame(all_movies)
    new_data = new_data.drop_duplicates(subset="id")

    if os.path.exists(OUTPUT_FILE):
        old_data = pd.read_csv(OUTPUT_FILE)
        new_data = pd.concat([old_data, new_data], ignore_index=True)
        new_data = new_data.drop_duplicates(subset="id", keep="last")

    new_data.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved {len(new_data)} unique movies to {OUTPUT_FILE}")
    print("\nMovies per language:")
    print(new_data["original_language"].value_counts().to_string())


if __name__ == "__main__":
    main()

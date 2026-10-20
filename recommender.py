
import pandas as pd
import ast
import os
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_poster_path(movie_id, movie_title=""):
    movie_id = str(int(movie_id))

    # Return a cached poster immediately
    if movie_id in poster_cache:
        return poster_cache[movie_id]

    # TMDB is currently unreachable, so skip network requests.
    return ""

    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )

        if response.status_code == 200:
            poster = response.json().get("poster_path") or ""

            if poster:
                poster_cache[movie_id] = poster
                save_poster_cache()
                return poster

    except requests.RequestException:
        print(f"Could not retrieve poster for {movie_title or movie_id}")

    return ""
POSTER_CACHE_PATH = "data/poster_cache.csv"

def load_poster_cache():
    if os.path.exists(POSTER_CACHE_PATH):
        cache = pd.read_csv(POSTER_CACHE_PATH)
        return dict(zip(cache["id"].astype(str), cache["poster"].fillna("")))
    return {}

poster_cache = load_poster_cache()

def save_poster_cache():
    pd.DataFrame([
        {"id": movie_id, "poster": poster}
        for movie_id, poster in poster_cache.items()
    ]).to_csv(POSTER_CACHE_PATH, index=False)
# Load the movie dataset
DATA_PATH = "data/tmdb_5000_movies.csv"

movies = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Total movies:", len(movies))


# Convert genre and keyword JSON strings into readable words
def extract_names(text):
    try:
        items = ast.literal_eval(text)
        return " ".join(item["name"] for item in items)
    except (ValueError, TypeError, SyntaxError):
        return ""


# Prepare movie information
movies["genres_text"] = movies["genres"].apply(extract_names)
movies["keywords_text"] = movies["keywords"].apply(extract_names)
movies["overview"] = movies["overview"].fillna("")

movies["combined_features"] = (
    movies["genres_text"] + " " +
    movies["keywords_text"] + " " +
    movies["overview"]
)

# Convert text into numerical vectors
tfidf = TfidfVectorizer(stop_words="english", max_features=20000)

tfidf_matrix = tfidf.fit_transform(movies["combined_features"])

# Calculate similarity between movies
similarity_matrix = cosine_similarity(tfidf_matrix, dense_output=False)

print("ML model prepared successfully!")


# Recommend similar movies
def recommend_movies(movie_title, number_of_recommendations=5):
    matches = movies[
        movies["title"].str.casefold() == movie_title.strip().casefold()
    ]

    if matches.empty:
        return []

    movie_index = matches.index[0]

    scores = similarity_matrix[movie_index].toarray().ravel()
    ranked_indices = scores.argsort()[::-1]

    recommendations = []

    for index in ranked_indices:
        if index == movie_index:
            continue

        row = movies.iloc[index]

        recommendations.append({
    "title": row["title"],
    "genres": row["genres_text"],
    "rating": row["vote_average"],
    "similarity": round(float(scores[index]) * 100, 2),
    "poster": get_poster_path(row["id"], row["title"])
})
        if len(recommendations) == number_of_recommendations:
            break

    return recommendations


# Test the recommendation engine
if __name__ == "__main__":
    movie_name = input("Enter a movie title: ")
    results = recommend_movies(movie_name)

    if results:
        print(f"\nMovies similar to {movie_name}:\n")

        for i, movie in enumerate(results, start=1):
            print(f"{i}. {movie['title']}")
            print(f"   Genres: {movie['genres']}")
            print(f"   Rating: {movie['rating']}")
            print(f"   Similarity: {movie['similarity']}%")
            print()
    else:
        print("Movie not found. Please check the title.")

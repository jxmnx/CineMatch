
from flask import Flask, render_template, request, jsonify
from recommender import movies, recommend_movies

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    search_query = ""
    error = None

    if request.method == "POST":
        search_query = request.form.get("movie_title", "").strip()

        if search_query:
            recommendations = recommend_movies(search_query)

            if not recommendations:
                error = "Movie not found. Try another title."

    return render_template(
        "index.html",
        recommendations=recommendations,
        search_query=search_query,
        error=error
    )


@app.route("/suggest")
def suggest():
    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return jsonify([])

    matches = movies[
        movies["title"].astype(str).str.contains(
            query, case=False, regex=False, na=False
        )
    ]["title"].drop_duplicates().head(8).tolist()

    return jsonify(matches)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5055, debug=False)

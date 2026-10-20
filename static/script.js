
document.addEventListener("DOMContentLoaded", () => {
    // =====================================
    // 1. Movie search suggestions
    // =====================================

    const input = document.getElementById("movie-input");
    const suggestions = document.getElementById("suggestions");

    if (input && suggestions) {
        let controller;
        let selectedIndex = -1;

        function hideSuggestions() {
            suggestions.innerHTML = "";
            suggestions.style.display = "none";
            selectedIndex = -1;
        }

        function selectMovie(title) {
            input.value = title;
            hideSuggestions();

            if (input.form) {
                input.form.requestSubmit();
            }
        }

        input.addEventListener("input", async () => {
            const query = input.value.trim();

            if (controller) {
                controller.abort();
            }

            if (query.length < 2) {
                hideSuggestions();
                return;
            }

            controller = new AbortController();

            try {
                const response = await fetch(
                    `/suggest?q=${encodeURIComponent(query)}`,
                    { signal: controller.signal }
                );

                if (!response.ok) {
                    throw new Error("Suggestion request failed");
                }

                const titles = await response.json();

                if (input.value.trim() !== query) {
                    return;
                }

                hideSuggestions();

                if (!titles.length) {
                    return;
                }

                titles.forEach((title) => {
                    const item = document.createElement("div");
                    item.className = "suggestion-item";
                    item.textContent = title;
                    item.setAttribute("role", "option");

                    item.addEventListener("click", () => {
                        selectMovie(title);
                    });

                    suggestions.appendChild(item);
                });

                suggestions.style.display = "block";
            } catch (error) {
                if (error.name !== "AbortError") {
                    console.error(
                        "Could not load movie suggestions:",
                        error
                    );
                }
            }
        });

        input.addEventListener("keydown", (event) => {
            const items =
                suggestions.querySelectorAll(".suggestion-item");

            if (!items.length) {
                return;
            }

            if (event.key === "ArrowDown") {
                event.preventDefault();
                selectedIndex =
                    (selectedIndex + 1) % items.length;
            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                selectedIndex =
                    (selectedIndex - 1 + items.length) % items.length;
            } else if (event.key === "Escape") {
                hideSuggestions();
                return;
            } else if (
                event.key === "Enter" &&
                selectedIndex >= 0
            ) {
                event.preventDefault();
                selectMovie(items[selectedIndex].textContent);
                return;
            } else {
                return;
            }

            items.forEach((item, index) => {
                const isSelected = index === selectedIndex;

                item.style.background = isSelected ? "#444" : "";
                item.setAttribute(
                    "aria-selected",
                    String(isSelected)
                );

                if (isSelected) {
                    item.scrollIntoView({ block: "nearest" });
                }
            });
        });

        document.addEventListener("click", (event) => {
            if (!event.target.closest(".search-container")) {
                hideSuggestions();
            }
        });
    }

    // =====================================
    // 2. Movie recommendation arrow buttons
    // =====================================

    const movieRow = document.getElementById("recommendation-row");
    const arrowButtons = document.querySelectorAll(".row-arrow");

    if (movieRow && arrowButtons.length) {
        arrowButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const direction = button.dataset.direction;

                // Scroll by approximately one card and its gap.
                const firstCard = movieRow.querySelector(".movie-card");

                const cardWidth = firstCard
                    ? firstCard.getBoundingClientRect().width
                    : 240;

                const rowStyles = window.getComputedStyle(movieRow);
                const gap = parseFloat(rowStyles.columnGap) || 16;
                const distance = cardWidth + gap;

                movieRow.scrollBy({
                    left: direction === "right" ? distance : -distance,
                    behavior: "smooth"
                });
            });
        });
    }
   
    // =====================================
    // 3. Movie details popup
    // =====================================

    const movieModal = document.getElementById("movie-modal");
    const modalContent = movieModal?.querySelector(".movie-modal-content");

    if (movieModal && modalContent && movieRow) {
        const modalPoster = document.getElementById("modal-movie-poster");
        const modalTitle = document.getElementById("modal-movie-title");
        const modalRating = document.getElementById("modal-movie-rating");
        const modalMatch = document.getElementById("modal-movie-match");
        const modalGenres = document.getElementById("modal-movie-genres");

        let previouslyFocusedElement = null;

        function openMovieModal(card) {
            const title = card.querySelector(".movie-info h3")?.textContent.trim() || "Movie details";
            const poster = card.querySelector(".movie-poster");
            const genres = card.querySelector(".movie-genres")?.textContent.trim() || "Genres unavailable";
            const rating = card.querySelector(".rating")?.textContent.trim() || "Rating unavailable";
            const match = card.querySelector(".match-score")?.textContent.trim()
                || card.querySelector(".match-label")?.textContent.trim()
                || "Match score unavailable";

            previouslyFocusedElement = document.activeElement;

            modalTitle.textContent = title;
            modalGenres.textContent = genres;
            modalRating.textContent = rating;
            modalMatch.textContent = match;

            if (poster && poster.getAttribute("src")) {
                modalPoster.src = poster.src;
                modalPoster.alt = `${title} poster`;
                modalPoster.style.display = "block";
            } else {
                modalPoster.removeAttribute("src");
                modalPoster.alt = "";
                modalPoster.style.display = "none";
            }

            movieModal.classList.add("is-open");
            movieModal.setAttribute("aria-hidden", "false");
            document.body.style.overflow = "hidden";
            modalContent.focus();
        }

        function closeMovieModal() {
            if (!movieModal.classList.contains("is-open")) return;

            movieModal.classList.remove("is-open");
            movieModal.setAttribute("aria-hidden", "true");
            document.body.style.overflow = "";

            if (previouslyFocusedElement?.isConnected) {
                previouslyFocusedElement.focus();
            }
        }

        movieRow.querySelectorAll(".movie-card").forEach((card) => {
            card.setAttribute("tabindex", "0");
            card.setAttribute("role", "button");

            card.addEventListener("click", (event) => {
                if (event.target.closest("a, button")) return;
                openMovieModal(card);
            });

            card.addEventListener("keydown", (event) => {
                if (event.target !== card) return;

                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    openMovieModal(card);
                }
            });
        });

        movieModal.querySelectorAll("[data-close-modal]").forEach((element) => {
            element.addEventListener("click", closeMovieModal);
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeMovieModal();
            }
        });
    }
 // Watch Trailer button
const trailerButton = document.getElementById("modal-watch-trailer");
const modalTitle = document.getElementById("modal-movie-title");

if (trailerButton && modalTitle) {
    trailerButton.addEventListener("click", function () {
        const movieTitle = modalTitle.textContent.trim();

        if (movieTitle && movieTitle !== "Movie title") {
            const query = encodeURIComponent(
                movieTitle + " official trailer"
            );

            const youtubeUrl =
                "https://www.youtube.com/results?search_query=" + query;

            window.open(youtubeUrl, "_blank", "noopener,noreferrer");
        }
    });
}
});

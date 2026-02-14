document.addEventListener("DOMContentLoaded", () => {
  console.log("HOME SEARCH READY");

  const input = document.getElementById("home-search");
  const suggestions = document.getElementById("search-suggestions");

  if (!input || !suggestions) {
    console.warn("Search elements not found");
    return;
  }

  // =========================
  // LIVE SEARCH INPUT
  // =========================
  input.addEventListener("input", async () => {
    const query = input.value.trim();

    if (query.length < 2) {
      suggestions.innerHTML = "";
      suggestions.style.display = "none";
      return;
    }

    try {
      const res = await fetch(
        `/kiosk/api/search/?q=${encodeURIComponent(query)}`
      );
      const data = await res.json();

      if (!data.results || data.results.length === 0) {
        suggestions.innerHTML = "";
        suggestions.style.display = "none";
        return;
      }

      // ✅ CORRECT MARKUP (matches your CSS)
      suggestions.innerHTML = data.results
        .slice(0, 5)
        .map(item => `
          <div class="search-item">
            <div class="search-title">
              ${item.title}
            </div>
            <span class="search-pill ${item.type.toLowerCase()}">
              ${item.type}
            </span>
          </div>
        `)
        .join("");

      suggestions.style.display = "block";

    } catch (err) {
      console.error("Search error:", err);
    }
  });

  // =========================
  // CLICK RESULT → SEARCH PAGE
  // =========================
  suggestions.addEventListener("click", e => {
    const item = e.target.closest(".search-item");
    if (!item) return;

    const query = input.value.trim();
    if (!query) return;

    window.location.href =
      `/kiosk/search/?q=${encodeURIComponent(query)}`;
  });

  // =========================
  // CLOSE ON OUTSIDE CLICK
  // =========================
  document.addEventListener("click", e => {
    if (
      !e.target.closest(".center-search") &&
      !e.target.closest("#search-suggestions")
    ) {
      suggestions.innerHTML = "";
      suggestions.style.display = "none";
    }
  });
});
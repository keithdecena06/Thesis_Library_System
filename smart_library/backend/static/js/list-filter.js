document.addEventListener("DOMContentLoaded", () => {
  const chips = document.querySelectorAll(".filter-chips .chip");
  const rows = document.querySelectorAll(".list-row:not(.empty)");
  const searchInput =
    document.getElementById("bookSearch") ||
    document.getElementById("thesisSearch");
  const listCount = document.getElementById("listCount");

  let activeYear = "all";

  const pageType = document.getElementById("thesisSearch") ? "thesis" : "book";

  function updateCount(visibleCount) {
    if (!listCount) return;

    const singular = pageType === "thesis" ? "thesis" : "book";
    const plural = pageType === "thesis" ? "theses" : "books";

    const hasSearch = searchInput && searchInput.value.trim() !== "";
    const hasFilter = activeYear !== "all";

    if (hasSearch || hasFilter) {
      listCount.textContent = `${visibleCount} matching ${visibleCount === 1 ? singular : plural}`;
    } else {
      listCount.textContent = `${visibleCount} ${visibleCount === 1 ? singular : plural} available`;
    }
  }

  function applyFilters() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
    let visibleCount = 0;

    rows.forEach((row) => {
      const rowYear = row.dataset.year || "";
      const title = row.dataset.title || "";
      const author = row.dataset.author || "";
      const student = row.dataset.student || "";
      const category = row.dataset.category || "";

      const matchesYear = activeYear === "all" || rowYear === activeYear;
      const matchesSearch =
        query === "" ||
        title.includes(query) ||
        author.includes(query) ||
        student.includes(query) ||
        category.includes(query);

      const shouldShow = matchesYear && matchesSearch;

      row.style.display = shouldShow ? "grid" : "none";

      if (shouldShow) {
        visibleCount++;
      }
    });

    updateCount(visibleCount);
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");

      activeYear = chip.dataset.year;
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  applyFilters();
});
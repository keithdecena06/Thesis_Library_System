document.addEventListener("DOMContentLoaded", () => {
  const chips = document.querySelectorAll(".chip");
  const rows = document.querySelectorAll(".list-row:not(.empty)");

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      // ACTIVE STATE
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");

      const year = chip.dataset.year;

      rows.forEach(row => {
        if (year === "all") {
          row.style.display = "grid";
        } else {
          row.style.display =
            row.dataset.year === year ? "grid" : "none";
        }
      });
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const chips = document.querySelectorAll(".filter-chips .chip");
  const rows  = document.querySelectorAll(".list-row:not(.empty)");

  chips.forEach(chip => {
    chip.addEventListener("click", () => {

      // active state
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");

      const selectedYear = chip.dataset.year;

      rows.forEach(row => {
        const rowYear = row.dataset.year;

        if (selectedYear === "all" || rowYear === selectedYear) {
          row.style.display = "grid";
        } else {
          row.style.display = "none";
        }
      });

    });
  });

});
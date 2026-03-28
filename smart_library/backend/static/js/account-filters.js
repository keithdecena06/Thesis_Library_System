document.addEventListener("DOMContentLoaded", () => {

  const pills = document.querySelectorAll(".filter-pill");
  const items = document.querySelectorAll(".recent-item");
  const expandBtn = document.querySelector(".expand-btn");

  const modal = document.getElementById("activityModal");
  const modalContent = document.getElementById("modalContent");
  const closeModal = document.getElementById("closeModal");

  /* =========================
     FILTER PILLS
  ========================== */
  pills.forEach(pill => {
    pill.addEventListener("click", () => {

      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");

      const filter = pill.dataset.filter;

      items.forEach(item => {
        if (filter === "all") {
          item.style.display = "block";
        } else {
          item.style.display =
            item.dataset.type === filter ? "block" : "none";
        }
      });

    });
  });

  /* =========================
     OPEN MODAL
  ========================== */
  if (expandBtn) {
    expandBtn.addEventListener("click", () => {

      // clone activity list
      const originalContent = document.querySelector(".activity-scroll").innerHTML;
      modalContent.innerHTML = originalContent;

      modal.classList.add("active");
      document.body.style.overflow = "hidden";

    });
  }

  /* =========================
     CLOSE MODAL
  ========================== */
  if (closeModal) {
    closeModal.addEventListener("click", () => {
      modal.classList.remove("active");
      document.body.style.overflow = "auto";
    });
  }

  // Close when clicking backdrop
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "auto";
    }
  });

});
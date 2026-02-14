document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("kiosk-theme");
  if (savedTheme) {
    document.body.classList.add(savedTheme);
  }

  document.querySelectorAll(".theme-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.body.className = "";
      const theme = btn.dataset.theme;
      document.body.classList.add(theme);
      localStorage.setItem("kiosk-theme", theme);
    });
  });
});
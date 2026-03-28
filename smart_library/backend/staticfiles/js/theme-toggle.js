const toggle = document.getElementById("theme-toggle");
const body = document.body;

/* Load saved theme */
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {
  body.classList.add("theme-dark");
  toggle.checked = true;
}

/* Toggle theme */
toggle.addEventListener("change", () => {
  if (toggle.checked) {
    body.classList.add("theme-dark");
    localStorage.setItem("theme", "dark");
  } else {
    body.classList.remove("theme-dark");
    localStorage.setItem("theme", "light");
  }
});
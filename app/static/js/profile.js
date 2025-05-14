function toggleBioEdit() {
  const form = document.getElementById("bio-form");
  const display = document.getElementById("bio-display");
  if (form.style.display === "none") {
    form.style.display = "block";
    display.style.display = "none";
  } else {
    form.style.display = "none";
    display.style.display = "block";
  }
}

function toggleTheme() {
  const body = document.body;
  body.classList.toggle("dark-mode");
  const isDark = body.classList.contains("dark-mode");
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
  }
});

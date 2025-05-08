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
  
document.getElementById("entryForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);

    const gameTitle = formData.get("gameTitle");
    const playerCount = formData.get("playerCount");
    const scores = formData.get("scores");
    const result = formData.get("result");
    const duration = formData.get("duration");
    const role = formData.get("role");

    const entryList = document.getElementById("entryList");
    const li = document.createElement("li");

    li.textContent = `🎲 ${gameTitle} | Players: ${playerCount} | Scores: ${scores} | Result: ${result} | Duration: ${duration} min | Role: ${role}`;
    entryList.appendChild(li);

    alert("Submission successful!");
    e.target.reset();
});

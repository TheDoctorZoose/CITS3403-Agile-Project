document.addEventListener('DOMContentLoaded', function() {
    const addPlayerBtn = document.getElementById('addPlayerBtn');
    const playersContainer = document.getElementById('playersContainer');
    let playerCount = 1; // Only Player 1 exists initially
  
    addPlayerBtn.addEventListener('click', function() {
      playerCount += 1;
  
      if (playerCount > 10) {
        alert("You have reached the maximum number of players (10).");
        return;
      }
  
      const fieldset = document.createElement('fieldset');
      fieldset.classList.add('player-info');
      fieldset.setAttribute('data-player', playerCount);
  
      fieldset.innerHTML = `
        <legend>Player ${playerCount}</legend>
  
        <label for="player${playerCount}Name">Name:</label>
        <input type="text" id="player${playerCount}Name" name="player${playerCount}Name" required placeholder="Player Name" />
  
        <label for="player${playerCount}Username">Username (optional):</label>
        <input type="text" id="player${playerCount}Username" name="player${playerCount}Username" placeholder="Username" />
  
        <label><input type="checkbox" id="player${playerCount}Win" name="player${playerCount}Win"> Win?</label>
        <label><input type="checkbox" id="player${playerCount}First" name="player${playerCount}First"> Went First?</label>
        <label><input type="checkbox" id="player${playerCount}FirstTime" name="player${playerCount}FirstTime"> First Time Playing?</label>
  
        <label for="player${playerCount}Score">Score:</label>
        <input type="number" id="player${playerCount}Score" name="player${playerCount}Score" placeholder="e.g., 50" />
  
        <button type="button" class="removePlayerBtn" style="margin-top: 10px;">❌ Remove Player</button>
      `;
  
      playersContainer.appendChild(fieldset);
  
      fieldset.querySelector('.removePlayerBtn').addEventListener('click', function() {
        fieldset.remove();
      });
    });
  });
  
document.addEventListener('DOMContentLoaded', function () {
    const visibilitySelect = document.getElementById('visibility');
    const friendSelection = document.getElementById('friend-selection');

    function toggleFriendSelection() {
        if (visibilitySelect && friendSelection) {
            friendSelection.style.display = (visibilitySelect.value === 'friends') ? 'block' : 'none';
        }
    }

    if (visibilitySelect) {
        visibilitySelect.addEventListener('change', toggleFriendSelection);
        toggleFriendSelection();
    }

    const addPlayerBtn = document.getElementById('addPlayerBtn');
    const playersContainer = document.getElementById('playersContainer');
    let playerCount = 1;

    addPlayerBtn.addEventListener('click', function () {
        playerCount++;
        if (playerCount > 10) {
            alert("You have reached the maximum number of players (10).");
            return;
        }

        const idx = playerCount - 1;
        const fs = document.createElement('fieldset');
        fs.classList.add('player-info');
        fs.setAttribute('data-index', idx.toString());

        fs.innerHTML = `
      <legend>Player ${playerCount}</legend>

      <div class="mb-3">
        <label class="form-label">Name:</label>
        <input type="text" name="player_name" class="form-control" required placeholder="Player Name">
      </div>

      <div class="mb-3">
        <label class="form-label">Username (optional):</label>
        <input type="text" name="player_username" class="form-control" placeholder="Username">
      </div>

      <div class="form-check mb-2">
        <label class="form-check-label" for="win${idx}">Win?</label>
        <input class="form-check-input" type="checkbox" name="win" value="${idx}" id="win${idx}">
      </div>
      <div class="form-check mb-2">
        <label class="form-check-label" for="first${idx}">Went First?</label>
        <input class="form-check-input" type="checkbox" name="went_first" value="${idx}" id="first${idx}">
      </div>
      <div class="form-check mb-3">
        <label class="form-check-label" for="ft${idx}">First Time Playing?</label>
        <input class="form-check-input" type="checkbox" name="first_time_playing" value="${idx}" id="ft${idx}">
      </div>

      <div class="mb-3">
        <label class="form-label">Score:</label>
        <input type="number" name="score" class="form-control" placeholder="e.g., 50">
      </div>

      <button type="button" class="removePlayerBtn btn btn-outline-danger">Remove Player</button>
    `;

        fs.querySelector('.removePlayerBtn').addEventListener('click', () => fs.remove());

        fs.querySelector('.removePlayerBtn').addEventListener('click', function () {
            fs.remove();
            playerCount -= 1;   // Ensures player count can still be maximum 10 even after removing players
        });

        playersContainer.appendChild(fs);
    });

    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function () {
            const entryId = this.dataset.entryId;
            const likeCountSpan = this.querySelector('.like-count');
            const btn = this;

            fetch(`/like/${entryId}`, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                credentials: 'same-origin'
            })
                .then(res => res.json())
                .then(data => {
                    data.liked = undefined;
                    data.like_count = undefined;
                    if (data.success) {
                        likeCountSpan.textContent = data.like_count;
                        btn.classList.toggle('liked', data.liked);
                    }
                });
        });
    });

    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function () {
            const entryId = this.dataset.entryId;
            const favoriteCountSpan = this.querySelector('.favorite-count');
            const btn = this;

            fetch(`/favorite/${entryId}`, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                credentials: 'same-origin'
            })
                .then(res => res.json())
                .then(data => {
                    data.favorite_count = undefined;
                    data.favorited = undefined;
                    if (data.success) {
                        favoriteCountSpan.textContent = data.favorite_count;
                        btn.classList.toggle('favorited', data.favorited);
                    }
                });
        });
    });
});

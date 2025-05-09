document.addEventListener('DOMContentLoaded', function () {
  // ✅ 可见性选择逻辑
  const visibilitySelect = document.getElementById('visibility');
  const friendSelection = document.getElementById('friend-selection');

  function toggleFriendSelection() {
    if (visibilitySelect && friendSelection) {
      friendSelection.style.display = (visibilitySelect.value === 'friends') ? 'block' : 'none';
    }
  }

  if (visibilitySelect) {
    visibilitySelect.addEventListener('change', toggleFriendSelection);
    toggleFriendSelection(); // 初始化
  }

  // ✅ 添加玩家功能
  const addPlayerBtn = document.getElementById('addPlayerBtn');
  const playersContainer = document.getElementById('playersContainer');
  const csvInput = document.getElementById('csvInput');
  const loadCsvBtn = document.getElementById('loadCsvBtn');
  let playerCount = 1;

  addPlayerBtn.addEventListener('click', function () {
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

    fieldset.querySelector('.removePlayerBtn').addEventListener('click', function () {
      fieldset.remove();
    });
  });

  // ✅ 加载 CSV 填充表单
  loadCsvBtn.addEventListener('click', function () {
    const file = csvInput.files[0];
    if (!file) return alert('Please select a CSV file first.');

    const reader = new FileReader();
    reader.onload = function (e) {
      const lines = e.target.result.split(/\r?\n/);
      const headers = lines[0].split(',');
      const values = lines[1]?.split(',');
      if (!values) return;

      const data = {};
      headers.forEach((h, i) => {
        data[h.trim()] = values[i]?.trim();
      });

      // 填充基本字段
      if (data['game_title']) document.getElementById('gameTitle').value = data['game_title'];
      if (data['date_played']) document.getElementById('datePlayed').value = data['date_played'];

      // 自动填充玩家
      for (let i = 1; i <= 10; i++) {
        if (data[`player${i}Name`]) {
          if (i > playerCount) addPlayerBtn.click();

          document.getElementById(`player${i}Name`).value = data[`player${i}Name`] || '';
          document.getElementById(`player${i}Username`).value = data[`player${i}Username`] || '';
          document.getElementById(`player${i}Win`).checked = data[`player${i}Win`] === 'true';
          document.getElementById(`player${i}First`).checked = data[`player${i}First`] === 'true';
          document.getElementById(`player${i}FirstTime`).checked = data[`player${i}FirstTime`] === 'true';
          document.getElementById(`player${i}Score`).value = data[`player${i}Score`] || '';
        }
      }
    };
    reader.readAsText(file);
  });

  // ✅ 点赞功能
  document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', function () {
      const entryId = this.dataset.entryId;
      const likeCountSpan = this.querySelector('.like-count');
      const btn = this;

      fetch(`/like/${entryId}`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin'
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            likeCountSpan.textContent = data.like_count;
            btn.classList.toggle('liked', data.liked);
          }
        });
    });
  });

  // ✅ 收藏功能
  document.querySelectorAll('.favorite-btn').forEach(button => {
    button.addEventListener('click', function () {
      const entryId = this.dataset.entryId;
      const favoriteCountSpan = this.querySelector('.favorite-count');
      const btn = this;

      fetch(`/favorite/${entryId}`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin'
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            favoriteCountSpan.textContent = data.favorite_count;
            btn.classList.toggle('favorited', data.favorited);
          }
        });
    });
  });
});

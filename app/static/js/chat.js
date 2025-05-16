document.addEventListener("DOMContentLoaded", function () {
    const CURRENT_USER_ID = window.CURRENT_USER_ID;
    const MESSAGE_HISTORY = window.MESSAGE_HISTORY || [];
    const ws = new WebSocket("ws://" + location.host + "/ws/chat?user_id=" + CURRENT_USER_ID);

    const chatBox = document.getElementById("chatBox");
    const userList = document.getElementById("userList");
    const msgInput = document.getElementById("msgInput");
    const sendBtn = document.getElementById("sendBtn");

    const messageCache = {}; // key = other user ID, value = array of messages

    // Populate cache with history
    MESSAGE_HISTORY.forEach(msg => {
        msg.sender_email = undefined;
        msg.receiver_id = undefined;
        msg.sender_id = undefined;
        const otherId = msg.sender_id === CURRENT_USER_ID ? msg.receiver_id : msg.sender_id;
        const direction = msg.sender_id === CURRENT_USER_ID ? "outgoing" : "incoming";
        if (!messageCache[otherId]) messageCache[otherId] = [];
        messageCache[otherId].push({
            from: msg.from, // ensure consistent identity label
            from_id: msg.sender_id,
            to_id: msg.receiver_id,
            content: msg.content || msg.message,
            timestamp: msg.timestamp,
            direction: direction
        });
    });

    function renderChat(toId) {
        const messages = messageCache[toId] || [];
        chatBox.innerHTML = '';
        messages.forEach(msg => {
            const className = msg.direction === "outgoing" ? "chat-msg right" : "chat-msg left";
            const senderLabel = msg.direction === "outgoing" ? "You" : msg.from;
            chatBox.innerHTML += `<p class="${className}"><b>${senderLabel}:</b> ${msg.content} <small>${msg.timestamp}</small></p>`;
        });
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    userList.addEventListener("change", () => {
        renderChat(userList.value);
    });

    sendBtn.addEventListener("click", () => {
        const to = userList.value;
        const content = msgInput.value.trim();
        if (to && content && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({to: to, message: content}));
            msgInput.value = "";
        }
    });

    ws.onmessage = e => {
        const data = JSON.parse(e.data);
        const direction = data.direction;
        const otherId = direction === "incoming" ? data.from_id : data.to_id;

        if (!messageCache[otherId]) messageCache[otherId] = [];
        messageCache[otherId].push({
            from: direction === "outgoing" ? "You" : data.from,
            from_id: data.from_id,
            to_id: data.to_id,
            content: data.message,
            timestamp: data.timestamp,
            direction: direction
        });

        if (userList.value === otherId) {
            renderChat(otherId);
        }
    };

    ws.onopen = () => {
        console.log("✅ WebSocket connected.");
        renderChat(userList.value);
    };

    ws.onclose = () => {
        console.log("❌ WebSocket closed.");
    };
});

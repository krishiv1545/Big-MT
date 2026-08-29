console.log("room.js loaded");

const roomElement = document.querySelector(".room");
const roomUuid = roomElement.dataset.roomUuid;

console.log("Room UUID:", roomUuid);

const chatPanel = document.getElementById("chat-panel");
const chatButton = document.getElementById("chat-btn");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-message");
const chatMessages = document.getElementById("chat-messages");


const protocol = window.location.protocol === "https:"
    ? "wss"
    : "ws";


const chatSocket = new WebSocket(
    `${protocol}://${window.location.host}/ws/chat/${roomUuid}/`
);


chatSocket.onopen = function () {
    console.log("Chat WebSocket connected.");
};


chatSocket.onclose = function (event) {
    console.log("Chat WebSocket disconnected.", event);
};


chatSocket.onerror = function (error) {
    console.error("Chat WebSocket error:", error);
};


chatSocket.onmessage = function (event) {

    const data = JSON.parse(event.data);

    if (data.type !== "chat_message") {
        return;
    }

    addMessage(
        data.username,
        data.message
    );
};


chatForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const message = chatInput.value.trim();

    if (!message) {
        return;
    }

    if (chatSocket.readyState !== WebSocket.OPEN) {
        console.error("Chat connection is not open.");
        return;
    }

    chatSocket.send(
        JSON.stringify({
            message: message
        })
    );

    chatInput.value = "";
    chatInput.focus();
});


let lastMessageUsername = null;


function addMessage(username, message) {

    const messageElement = document.createElement("div");

    messageElement.className = "chat-message";

    if (username !== lastMessageUsername) {

        messageElement.innerHTML = `
            <div class="chat-message-user">
                ${escapeHtml(username)}
            </div>

            <div class="chat-message-text">
                ${escapeHtml(message)}
            </div>
        `;

    } else {

        messageElement.classList.add("continuation");

        messageElement.innerHTML = `
            <div class="chat-message-text">
                ${escapeHtml(message)}
            </div>
        `;
    }

    chatMessages.appendChild(messageElement);

    lastMessageUsername = username;

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


chatButton.addEventListener("click", function () {

    chatPanel.classList.toggle("open");
    chatButton.classList.toggle("active");

    if (chatPanel.classList.contains("open")) {
        chatInput.focus();
    }
});

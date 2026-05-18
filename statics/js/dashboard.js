// ================= CSRF =================
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}


// ================= RENDER MESSAGE =================
function renderMessage(msg) {
    const div = document.createElement("div");

    // match your CSS
    div.className = msg.role === "user" ? "message user" : "message ai";

    if (msg.role === "user") {
        div.innerText = msg.content;
    } else {
        div.innerHTML = marked.parse(msg.content);
    }

    return div;
}


// ================= LOAD CHAT HISTORY =================
function loadMessages(chatId) {
    const chatArea = document.getElementById("chatArea");

    if (!chatArea) return;

    fetch(`/get-messages/${chatId}`)
    .then(res => res.json())
    .then(data => {
        chatArea.innerHTML = "";

        data.messages.forEach(msg => {
            chatArea.appendChild(renderMessage(msg));
        });

        chatArea.scrollTop = chatArea.scrollHeight;
    })
    .catch(err => console.error("Load error:", err));
}


// ================= TYPING INDICATOR =================
function showTyping(chatArea) {
    const el = document.createElement("div");
    el.className = "typing-indicator";
    el.id = "typingIndicator";
    el.innerHTML = "<span></span><span></span><span></span>";
    chatArea.appendChild(el);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
}


// ================= SEND MESSAGE =================
let isSending = false;

function sendMessage() {
    if (isSending) return;

    const input    = document.getElementById("userInput");
    const chatArea = document.getElementById("chatArea");
    const sendBtn  = document.querySelector('[onclick="sendMessage()"]');

    if (!input || !chatArea) return;

    const message = input.value.trim();
    if (!message) return;

    const pathParts = window.location.pathname.split('/');
    const chatId = pathParts[2];

    if (!chatId) {
        alert("Please click 'New Chat' first.");
        return;
    }

    isSending = true;
    if (sendBtn) sendBtn.disabled = true;

    // Optimistically show user message immediately
    chatArea.appendChild(renderMessage({ role: "user", content: message }));
    input.value = "";
    chatArea.scrollTop = chatArea.scrollHeight;

    showTyping(chatArea);

    fetch(`/dashboard/${chatId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: `message=${encodeURIComponent(message)}`
    })
    .then(res => res.json())
    .then(data => {
        hideTyping();

        if (data.error) {
            chatArea.appendChild(renderMessage({
                role: "assistant",
                content: "⚠️ **Error:** " + data.error + "\n\nPlease try again."
            }));
        } else {
            chatArea.appendChild(renderMessage({ role: "assistant", content: data.ai }));
        }

        chatArea.scrollTop = chatArea.scrollHeight;
    })
    .catch(err => {
        hideTyping();
        console.error("Send error:", err);
        chatArea.appendChild(renderMessage({
            role: "assistant",
            content: "⚠️ Network error. Please try again."
        }));
    })
    .finally(() => {
        isSending = false;
        if (sendBtn) sendBtn.disabled = false;
    });
}


// ================= ENTER KEY =================
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("userInput");

    if (input) {
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});


// ================= AUTO LOAD CHAT =================
document.addEventListener("DOMContentLoaded", function () {
    const pathParts = window.location.pathname.split('/');
    const chatId = pathParts[2];

    if (chatId) {
        loadMessages(chatId);
    }
});


// ================= DROPDOWN =================
function toggleUserMenu() {
    const menu = document.getElementById("dropdownMenu");
    if (!menu) return;

    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}


// ================= CLOSE DROPDOWN =================
document.addEventListener("click", function(event) {
    const menu = document.getElementById("dropdownMenu");
    const userMenu = document.querySelector(".user-menu");

    if (!menu || !userMenu) return;

    if (!userMenu.contains(event.target)) {
        menu.style.display = "none";
    }
});


// ================= DELETE CHAT =================
function deleteChat(chatId) {
    if (!confirm("Delete this chat?")) return;

    fetch(`/delete-chat/${chatId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = "/dashboard/";
        }
    })
    .catch(err => console.error("Delete error:", err));
}


// ================= UPLOAD MENU =================
function toggleUploadMenu() {
    const menu = document.getElementById("uploadMenu");
    if (!menu) return;

    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}


// ================= FILE UPLOAD =================
function uploadFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    const chatArea = document.getElementById("chatArea");

    const formData = new FormData();
    formData.append("file", file);

    // show file name
    chatArea.appendChild(renderMessage({
        role: "user",
        content: `📄 ${file.name}`
    }));

    fetch(`/upload/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {

        if (data.error) {
            chatArea.appendChild(renderMessage({
                role: "assistant",
                content: "❌ Upload failed"
            }));
            return;
        }

        chatArea.appendChild(renderMessage({
            role: "assistant",
            content: data.result
        }));

        chatArea.scrollTop = chatArea.scrollHeight;
    })
    .catch(err => console.error("UPLOAD ERROR:", err));

    event.target.value = "";
}


// ================= IMAGE UPLOAD =================
function uploadImage(event) {
    const file = event.target.files[0];
    if (!file) return;

    const input = document.getElementById("userInput");
    input.value = `🖼 ${file.name}`;
}


// ================= CLOSE UPLOAD MENU =================
document.addEventListener("click", function(event) {
    const menu = document.getElementById("uploadMenu");
    const container = document.querySelector(".upload-menu-container");

    if (!menu || !container) return;

    if (!container.contains(event.target)) {
        menu.style.display = "none";
    }
});
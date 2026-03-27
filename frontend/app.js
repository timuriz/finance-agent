async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    const responce = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData
    });
    const data = await responce.json();

    const report = document.getElementById("reportOutput");

    report.innerHTML = `
        <p><strong>Total spent:</strong> $${Math.abs(data.total).toFixed(2)}</p>

        <h3>Categories</h3>
        <ul>
            ${Object.entries(data.categories)
                .map(([key, value]) =>
                    `<li>${key}: $${Math.abs(value).toFixed(2)}</li>`
                )
                .join("")}
        </ul>
    `;
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const chat = document.getElementById("chatOutput");

    const message = input.value;

    
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.textContent = message;
    chat.appendChild(userMsg);

    const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();


    const aiMsg = document.createElement("div");
    aiMsg.className = "message ai";
    aiMsg.textContent = data.response;
    chat.appendChild(aiMsg);

    input.value = "";

    chat.scrollTop = chat.scrollHeight;
}
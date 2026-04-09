async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
        
    const formData = new FormData();
    formData.append("file", file);
    formData.append("currency", document.getElementById("currencySelect").value);

    const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData
    });


    if (!response.ok) {
        const error = await response.json();
        report.innerHTML = `<p style="color:red";>Error ${error.detail}</p>`;
        return;
    }



    const data = await response.json();
    const currency = document.getElementById("currencySelect").value;

    const report = document.getElementById("reportOutput");

    const values = Object.values(data.categories).map(v => Math.abs(v));
    const maxValue = Math.max(...values);
 
    report.innerHTML = `
        <p><strong>Total spent:</strong> ${data.total_display} ${currency}</p>
        <h3>Categories</h3>
        <div class="chart">
            ${Object.entries(data.categories)
                .map(([category, amount]) => {
                    const abs = Math.abs(amount);
                    const pct = (abs / maxValue * 100).toFixed(1);
                    return `
                        <div class="chart-row">
                            <span class="chart-label">${category}</span>
                            <div class="chart-bar-wrap">
                                <div class="chart-bar" style="width: ${pct}%"></div>
                                <span class="chart-value">${abs.toFixed(2)} ${currency}</span>
                            </div>
                        </div>`;
                })
                .join("")}
        </div>
    `;
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const chat = document.getElementById("chatOutput");

    const message = input.value;

    
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.innerHTML = `<strong>You:</strong> ${message}`;
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

    if (!data.response) {
        aiMsg.textContent = "⚠️ No response from AI";
    } else {
        let formatted = data.response
            .replace(/\n/g, "<br>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        aiMsg.innerHTML = `<strong>AI:</strong><br>` + formatted;
    }

    chat.appendChild(aiMsg);

    chat.scrollTop = chat.scrollHeight; 
}
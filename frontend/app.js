async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const btn = document.getElementById("uploadBtn");

  btn.disabled = true;
  btn.textContent = "Processing...";
  const report = document.getElementById("reportOutput");
  report.innerHTML = `<p>Analysing your transactions...</p>`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("currency", document.getElementById("currencySelect").value);

  const response = await fetch("http://127.0.0.1:8000/analyze", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    report.innerHTML = `<p style="color:red;">Error ${error.detail}</p>`;
    btn.disabled = false;
    btn.textContent = "Upload CSV";
    return;
  }

  const data = await response.json();
  const currency = document.getElementById("currencySelect").value;

  const values = Object.values(data.categories).map((v) => Math.abs(v));
  const maxValue = Math.max(...values);

  report.innerHTML = `   
        <p><strong>Total spent:</strong> ${data.total_display} ${currency}</p> 
        <h3>Categories</h3>
        <div class="chart">
            ${Object.entries(data.categories)
              .map(([category, amount]) => {
                const abs = Math.abs(amount);
                const pct = ((abs / maxValue) * 100).toFixed(1);
                const conf = data.confidence[category] || 0;
                const confColor =
                  conf >= 80 ? "green" : conf >= 50 ? "orange" : "red";

                return `
                  <div class="chart-row">
                      <span class="chart-label">
                          ${category}
                        <span class="conf-badge" 
                            style="color:${confColor};"
                            onmouseenter="showTip(event, 'AI confidence in this category')"
                            onmouseleave="hideTip()">
                            ${conf}%
                        </span>
                      </span>
                      <div class="chart-bar-wrap">
                          <div class="chart-bar" style="width: ${pct}%"></div>
                          <span class="chart-value">${abs.toFixed(2)} ${currency}</span>
                      </div>
                  </div>`;
              })
              .join("")} 
        </div>
        <p style="font-size:0.78rem; color:#6b7280; margin-top:8px;">
            ℹ️ Percentages show how confident the AI is in each category assignment.
            <span style="color:green;">Green (≥80%)</span> = high confidence,
            <span style="color:orange;">Orange (50-79%)</span> = medium,
            <span style="color:red;">Red (&lt;50%)</span> = low — review manually.
        </p>
    `;
  btn.disabled = false;
  btn.textContent = "Upload CSV";
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
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message }),
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

const tip = document.createElement("div");
tip.style.cssText = "position:fixed;background:#1f2937;color:white;padding:4px 10px;border-radius:4px;font-size:0.72rem;pointer-events:none;display:none;z-index:9999;";
document.body.appendChild(tip);

function showTip(e, text) {
    tip.textContent = text;
    tip.style.display = "block";
    tip.style.left = (e.clientX + 12) + "px";
    tip.style.top = (e.clientY - 28) + "px";
}

function hideTip() {
    tip.style.display = "none";
}
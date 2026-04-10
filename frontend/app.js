async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const btn = document.getElementById("uploadBtn");
  const report = document.getElementById("reportOutput");

  btn.disabled = true;
  btn.textContent = "Processing…";
  report.innerHTML = `<p style="color:#8e8e93;font-size:0.875rem;">Analysing your transactions…</p>`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("currency", document.getElementById("currencySelect").value);

  const response = await fetch("http://127.0.0.1:8000/analyze", {
    method: "POST",
    body: formData,
  });

  btn.disabled = false;
  btn.textContent = "Upload CSV";

  if (!response.ok) {
    const error = await response.json();
    report.innerHTML = `<p style="color:#ff453a;">Error: ${error.detail}</p>`;
    return;
  }

  const data = await response.json();
  const currency = document.getElementById("currencySelect").value;

  const fmt = (n) =>
    `${currency} ${Number(n).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;

  // ── Summary cards ──────────────────────────────────────────────────────
  const netSign  = data.net_balance >= 0 ? "+" : "";
  const netClass = data.net_balance >= 0 ? "net-pos" : "net-neg";

  const summaryHTML = `
    <div class="summary-grid">
      <div class="summary-card">
        <div class="s-label">Income</div>
        <div class="s-value income">${fmt(data.income)}</div>
      </div>
      <div class="summary-card">
        <div class="s-label">Total spent</div>
        <div class="s-value expenses">${fmt(data.expenses)}</div>
      </div>
      <div class="summary-card">
        <div class="s-label">Net balance</div>
        <div class="s-value ${netClass}">${netSign}${fmt(data.net_balance)}</div>
      </div>
    </div>`;

  // ── Bar chart ───────────────────────────────────────────────────────────
  const values   = Object.values(data.categories);
  const maxValue = Math.max(...values);

  const chartRows = Object.entries(data.categories)
    .map(([category, amount]) => {
      const pct      = ((amount / maxValue) * 100).toFixed(1);
      const conf     = data.confidence[category] ?? 0;
      const isLow    = conf < 50;
      const confColor = conf >= 80 ? "#30d158" : conf >= 50 ? "#ff9f0a" : "#ff453a";

      const confBadge = isLow
        ? `<span class="review-badge">review</span>`
        : `<span class="conf-pct" style="color:${confColor};">${conf}%</span>`;

      return `
        <div class="chart-row${isLow ? " low-conf" : ""}">
          <span class="chart-label">
            ${category}
            ${confBadge}
          </span>
          <div class="chart-bar-wrap">
            <div class="chart-bar-track">
              <div class="chart-bar" style="width:${pct}%"></div>
            </div>
            <span class="chart-value">${fmt(amount)}</span>
          </div>
        </div>`;
    })
    .join("");

  report.innerHTML = `
    ${summaryHTML}
    <div class="section-header">Expenses by category</div>
    <div class="chart">${chartRows}</div>
    <div class="legend">
      <div class="legend-item">
        <span class="legend-dot" style="background:#30d158;"></span>
        High confidence ≥80%
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#ff9f0a;"></span>
        Medium 50–79%
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#ff453a;"></span>
        Low &lt;50% — review manually
      </div>
    </div>`;
}

// ── Chat ────────────────────────────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById("chatInput");
  const chat  = document.getElementById("chatOutput");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";

  const userMsg = document.createElement("div");
  userMsg.className = "message user";
  userMsg.innerHTML = `<strong>You:</strong> ${message}`;
  chat.appendChild(userMsg);
  chat.scrollTop = chat.scrollHeight;

  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data   = await response.json();
  const aiMsg  = document.createElement("div");
  aiMsg.className = "message ai";

  if (!data.response) {
    aiMsg.textContent = "⚠️ No response from AI";
  } else {
    const formatted = data.response
      .replace(/\n/g, "<br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    aiMsg.innerHTML = `<strong>AI:</strong><br>${formatted}`;
  }

  chat.appendChild(aiMsg);
  chat.scrollTop = chat.scrollHeight;
}

// ── Tooltip ──────────────────────────────────────────────────────────────────
const tip = document.createElement("div");
tip.style.cssText =
  "position:fixed;background:#1f2937;color:#fff;padding:4px 10px;border-radius:4px;" +
  "font-size:0.72rem;pointer-events:none;display:none;z-index:9999;";
document.body.appendChild(tip);

function showTip(e, text) {
  tip.textContent = text;
  tip.style.display = "block";
  tip.style.left = e.clientX + 12 + "px";
  tip.style.top  = e.clientY - 28 + "px";
}

function hideTip() {
  tip.style.display = "none";
}

# Finance Agent

A personal finance analysis tool — upload a bank transaction CSV, get an instant dark-themed dashboard with income vs. spend breakdown, ML-powered categorisation with per-category confidence scores, anomaly detection, and a Gemini-powered AI chat agent you can question in plain English.

---

## Demo

![Finance Agent demo](docs/finance-agent.gif)

---

## Features

### Dashboard
- **Income / Expenses / Net balance** summary cards at a glance
- **Spending bar chart** — all bars share a fixed left baseline so amounts are directly comparable
- **Multi-currency support** — select USD, EUR, GBP, JPY, UAH before upload; live exchange-rate conversion applied automatically

### ML Categorisation
- **TF-IDF + Logistic Regression** model trained on 50 000 synthetic bank-statement descriptions
- **8 categories** — groceries, café & restaurant, transport, entertainment, shopping, health, bills & utilities, income
- **Confidence score** shown inline per category (green ≥ 80 % / orange 50–79 % / red < 50 %)
- **"Review" badge** on any category where AI confidence is below 50 % so you know what to check manually
- **Keyword fallback** — if ML confidence is too low the categoriser falls back to an extensive keyword ruleset covering 100 + merchant names and phrases
- **Smart column mapping** — accepts CSVs with non-standard headers (`operation_amount`, `transaction_date`, `details`, etc.) and maps them automatically

### AI Chat Agent
- Ask questions in natural language: *"Why did I overspend in March?"*, *"What were my biggest anomalies?"*
- Agent selects the right tool automatically (`get_summary`, `get_category_breakdown`, `get_anomalies`, `get_overspending`, `get_date_range`) and passes computed data to Gemini for a clear, concise answer
- **Date-range filtering** — questions like *"show me spending between Jan 1 and Feb 28"* are parsed and applied automatically
- Chat history preserved for the session

### Data & Privacy
- **Anomaly detection** — flags transactions > 2 standard deviations from your mean spend
- All analysis runs **locally** — no transaction data leaves your machine; only natural-language questions are sent to the Gemini API

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| ML model | scikit-learn (TF-IDF · Logistic Regression) |
| LLM / AI agent | Google Gemini (`gemini-3-flash-preview`) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Config | python-dotenv |
| Data generation | Custom synthetic generator (50 k rows, 8 categories) |

---

## Project Structure

```
finance-agent/
├── backend/
│   ├── api.py               # FastAPI — /analyze and /chat endpoints
│   ├── agent.py             # LLM tool-use agent (decision + execution loop)
│   ├── categorization.py    # ML categoriser + keyword fallback
│   ├── anomaly_detection.py # Statistical anomaly detection (2σ)
│   ├── data_processing.py   # Column mapping, cleaning, aggregation helpers
│   ├── llm_insights.py      # One-shot Gemini insight generator
│   ├── report.py            # Report formatting
│   ├── train_model.py       # Model training script
│   └── config.py            # Loads .env and exports constants
├── frontend/
│   ├── index.html
│   ├── styles.css           # Dark theme, CSS variables
│   └── app.js
├── models/
│   └── category_model.pkl   # Trained model (git-ignored)
├── data/                    # CSV files (git-ignored)
├── docs/                    # Demo gif and assets
├── data-generator.py        # Synthetic transaction generator
├── .env.example             # Environment variable template
└── .gitignore
```

---

## Getting Started

### Prerequisites

- **Python 3.9** (see [compatibility note](#python-version-compatibility) below)
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/finance-agent.git
cd finance-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# open .env and paste your Gemini API key
```

### 4. Generate training data and train the model

```bash
python data-generator.py          # writes data/synthetic_transactions_v2.csv

cd backend
python train_model.py             # trains and saves models/category_model.pkl
```

### 5. Start the backend

```bash
cd backend
uvicorn api:app --reload
```

### 6. Open the frontend

Open `frontend/index.html` directly in your browser (no build step needed).

---

## How It Works

1. **Upload** a CSV — any export from a bank works; the column mapper handles non-standard headers (`operation_amount`, `transaction_date`, `details`, etc.)
2. **Categorisation** — each transaction description is passed through the TF-IDF + LR model; if confidence is below the threshold the keyword fallback takes over
3. **Income separation** — credit transactions are summed as income and excluded from the expense chart; the summary row shows income, total spent, and net balance
4. **Anomaly detection** — transactions more than 2σ from the mean are flagged
5. **Chart rendering** — categories are sorted by spend, bars grow from a shared baseline, confidence is shown inline
6. **Chat** — your question goes to the agent, which decides which analytical tool to run, executes it against the in-memory DataFrame, then sends the result to Gemini to generate a plain-English answer

---

## CSV Format

The app accepts any CSV with at least these three pieces of information (column names are flexible):

| Field | Accepted column names |
|---|---|
| Date | `date`, `transaction_date`, `date_time`, `when` |
| Description | `description`, `details`, `about` |
| Amount | `amount`, `operation_amount`, `transaction_amount`, `value`, `sum` |
| Currency *(optional)* | `currency`, `ccy`, `operation_currency` |

Amounts can be **signed** (negatives = expenses) or **unsigned** (all positive, treated as expenses).

---

## Python Version Compatibility

This project is developed and tested on **Python 3.9.6**. It is likely to break on Python 3.10+ due to two known issues:

### 1. `google-generativeai` import changed in newer versions
On Python 3.10+ with `google-generativeai >= 0.9`, the import style changed:

```python
# Breaks on newer installs
from google import genai

# Use this instead (works on 3.9 with google-generativeai==0.8.x)
import google.generativeai as genai
```

### 2. `libexpat` / `pyexpat` crash on macOS + Python 3.13 (Homebrew)
If you installed Python 3.13 via Homebrew on macOS, `pip` itself may crash with:
```
ImportError: dlopen(pyexpat.cpython-313-darwin.so): Symbol not found: _XML_SetAllocTrackerActivationThreshold
```
This is a known conflict between Homebrew's Python 3.13 and the system `libexpat`. Fix options:
- Reinstall via `brew reinstall expat && brew reinstall python@3.13`
- Or use the [official python.org installer](https://www.python.org/downloads/) for 3.13, which bundles its own `libexpat`

### Recommended fix for Python 3.10+
Pin the exact versions from `requirements.txt` and retrain the model after any Python or scikit-learn upgrade (the `.pkl` file is version-specific):

```bash
pip install -r requirements.txt
cd backend && python train_model.py
```

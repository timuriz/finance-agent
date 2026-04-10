from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
from data_processing import process_data, total_spent, spending_by_category, convert_to_base
from agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GLOBAL_DF = None
CHAT_HISTORY = []


@app.post("/analyze")
async def analyze(file: UploadFile, currency = Form(default="USD")):
    contents = await file.read()
    
    try:
        df = process_data(io.StringIO(contents.decode()))
        df = convert_to_base(df, base_currency=currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


    global GLOBAL_DF, CHAT_HISTORY
    GLOBAL_DF = df
    CHAT_HISTORY = []


    income = round(df[df["type"] == "credit"]["amount"].sum(), 2)
    expenses_df = df[df["type"] == "debit"].copy()
    expenses = round(abs(expenses_df["amount"].sum()), 2)
    net_balance = round(income - expenses, 2)

    category_totals = (
        expenses_df.groupby("category")["amount"].sum().abs().sort_values(ascending=False)
    )
    category_confidence = (
        expenses_df.groupby("category")["confidence"].mean().round().astype(int)
    )

    return {
        "income": income,
        "expenses": expenses,
        "net_balance": net_balance,
        "categories": category_totals.to_dict(),
        "confidence": category_confidence.to_dict(),
    }


@app.post("/chat")
async def chat(request: dict):
    message = request["message"]

    if GLOBAL_DF is None:
        return {"response": "Please upload your CSV first before asking question"}

    result = run_agent(message, GLOBAL_DF, history=CHAT_HISTORY)

    return {"response": result["answer"]}
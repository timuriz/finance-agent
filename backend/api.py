from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
from data_processing import (
    process_data, 
    total_spent, 
    spending_by_category, 
    convert_to_base,
    spending_by_month
    )
from agent import run_agent_stream_async

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


def my_generator():
    yield "first chunk"
    yield "second chunk"
    yield "third chunk"

@app.get("/stream")
def stream():
    return StreamingResponse(my_generator(), media_type="text/plain")

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

    monthly = spending_by_month(df)
    monthly_dict = {str(k): round(abs(v), 2) for k, v in monthly.items()}


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
        "monthly": monthly_dict,
    }


@app.post("/chat")
async def chat(request: dict):
    message = request["message"]

    if GLOBAL_DF is None:
        return {"response": "Please upload your CSV first before asking question"}

    async def generate():
        async for chunk in run_agent_stream_async(message, GLOBAL_DF, history=CHAT_HISTORY):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
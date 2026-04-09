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

    global GLOBAL_DF, CHAT_HISTORY
    GLOBAL_DF = df
    CHAT_HISTORY = []

    
    try:
        df = process_data(io.StringIO(contents.decode()))
        df = convert_to_base(df, base_currency=currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


    global GLOBAL_DF
    GLOBAL_DF = df


    total = total_spent(df)

    return {
        "total": total,
        "total_display": f"+{total:.2f}" if total > 0 else f"{total:.2f}",
        "categories": spending_by_category(df).to_dict(),
        }


@app.post("/chat")
async def chat(request: dict):
    message = request["message"]

    if GLOBAL_DF is None:
        return {"response": "Please upload your CSV first before asking question"}

    result = run_agent(message, GLOBAL_DF, hisory=CHAT_HISTORY)

    CHAT_HISTORY.append({
        "user": message,
        "assistant": result["answer"]
    })
    if len(CHAT_HISTORY) > 5:
        CHAT_HISTORY.pop(0)

    return {"response": result["answer"]}
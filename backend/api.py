from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import io

from data_processing import process_data, total_spent, spending_by_category, category_by_percentage
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


@app.post("/analyze")
async def analyze(file: UploadFile):
    contents = await file.read()

    df = process_data(io.StringIO(contents.decode()))

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

    result = run_agent(message, GLOBAL_DF)

    return {"response": result["answer"]}
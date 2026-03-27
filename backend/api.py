from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import io

from data_processing import process_data
from analytics import total_spent, spending_by_category
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

    return {
        "total": total_spent(df),
        "categories": spending_by_category(df).to_dict()
    }


@app.post("/chat")
async def chat(request: dict):
    message = request["message"]

    result = run_agent(message, GLOBAL_DF)

    return {"response": result["answer"]}
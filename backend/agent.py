from data_processing import (
    total_spent,
    top_category,
    spending_by_category,
    detect_overspending,
    date_range
)
from anomaly_detection import detect_anomalies
import json
import google.generativeai as genai
from datetime import date
from config import GOOGLE_API_KEY
import pandas as pd

# ------------------------
# TOOL DEFINITIONS
# ------------------------

TOOLS = {
    "get_summary": "Returns total spending and top category",
    "get_category_breakdown": "Returns spending per category",
    "get_anomalies": "Returns unusual transactions",
    "get_overspending": "Returns categories with high spending",
}


def get_summary(df):
    return {
        "total_spent": abs(total_spent(df)),
        "top_category": top_category(df)
    }




def get_category_breakdown(df):
    return spending_by_category(df).to_dict()


def get_anomalies_tool(df):
    anomalies = detect_anomalies(df)
    return anomalies[["description", "amount"]].to_dict(orient="records")


def get_overspending_tool(df):
    return detect_overspending(df).to_dict()


# ------------------------
# TOOL EXECUTION
# ------------------------

def execute_tool(tool_name, df):
    if tool_name == "get_summary":
        return get_summary(df)

    elif tool_name == "get_category_breakdown":
        return get_category_breakdown(df)

    elif tool_name == "get_anomalies":
        return get_anomalies_tool(df)

    elif tool_name == "get_overspending":
        return get_overspending_tool(df)

    else:
        return {"error": "Unknown tool"}

# ------------------------
# PROMPTS
# ------------------------

def build_decision_prompt(user_query):
    today = date.today().isoformat()
    return f"""
You are a financial assistant agent. Today is {today}

You MUST choose ONE tool, and extract any date from user message.

TOOLS:
- get_summary
- get_category_breakdown
- get_anomalies
- get_overspending

USER QUESTION:
{user_query}

Respond obly with valid JSON, no markdown, no explanation:\n like:
{{
  "tool": "<tool_name>",
  "start_date": "<YYYY-MM-DD or null>",
  "end_date": "<YYYY-MM-DD or null>",
  "reason": "<brief reason>"
}}
"""

def build_explanation_prompt(user_query, tool_result):
    return f"""
You are a financial assistant.

The user asked:
{user_query}

Here is the computed data:
{tool_result}

IMPORTANT: Negative amounts represent expenses (money spent). Positive amounts represent income.
When explaining spending, use absolute values and say "spent $X" not "-$X".

Explain the answer clearly and give a useful insight.

Do NOT mention tools.
Be concise.
"""


# ------------------------
# LLM SETUP
# ------------------------

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")


# ------------------------
# MAIN AGENT FUNCTION
# ------------------------

def run_agent(user_query, df):
    prompt = build_decision_prompt(user_query)
    response = model.generate_content(prompt)
    
    # Parse JSON from LLM
    try:
        decision = json.loads(response.text.strip())
    except json.JSONDecodeError:
        return {"answer": "I couldn't understand that question."}
    
    tool = decision.get("tool")
    start_date = decision.get("start_date") 
    end_date = decision.get("end_date")     
    
    if tool not in TOOLS:
        return {"answer": "I couldn't determine the correct tool to use."}
    
    filtered_df = df.copy()
    if start_date:
        filtered_df = filtered_df[filtered_df["date"] >= pd.Timestamp(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df["date"] <= pd.Timestamp(end_date)]

    if filtered_df.empty:
        date_range_str = f"{start_date} to {end_date}" if start_date else "that period"
        return {"answer": f"No transaction found for {date_range_str}."}
    
    
    tool_result = execute_tool(tool, filtered_df)
    
    explanation_prompt = build_explanation_prompt(user_query, tool_result)
    explanation_response = model.generate_content(explanation_prompt)
    
    return {"decision": decision, "answer": explanation_response.text}
from data_processing import (
    total_spent,
    top_category,
    spending_by_category,
    detect_overspending,
    spending_by_month
)
from anomaly_detection import detect_anomalies
import json
from google import genai
from datetime import date
from config import GOOGLE_API_KEY
import pandas as pd



#-------------------------
# MODEL SETUP
#-------------------------


client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL = "gemini-3-flash-preview"


# ------------------------
# TOOL DEFINITIONS
# ------------------------

TOOLS = {
    "get_summary": "Returns total spending and top category",
    "get_category_breakdown": "Returns spending per category",
    "get_anomalies": "Returns unusual transactions",
    "get_overspending": "Returns categories with high spending",
    "get_spending_by_month": "Returns total spend by given month",
    "none": "Answer from conversation history",
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

def get_spending_by_month(df):
    return spending_by_month(df).to_dict()


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

    elif tool_name == "get_spending_by_month":
        return get_spending_by_month(df);

    else:
        return {"error": "Unknown tool"}

# ------------------------
# PROMPTS
# ------------------------

def build_decision_prompt(user_query, last_result=None):
    today = date.today().isoformat()
    last_result_text = f"\nLast computed result: {last_result}" if last_result else ""
    return f"""
You are a financial assistant agent. Today is {today}
{last_result_text}

You MUST choose ONE tool,OR if the question can be answered from the last result above, use "none". and extract any date from user message.

TOOLS:
- get_summary
- get_category_breakdown
- get_anomalies
- get_overspending
- none  (use when answering a follow-up from previous context)

USER QUESTION:
{user_query}

Respond only with valid JSON, no markdown, no explanation:\n like:
{{
  "tool": "<tool_name>",
  "start_date": "<YYYY-MM-DD or null>",
  "end_date": "<YYYY-MM-DD or null>",
  "reason": "<brief reason>"
}}
"""

def build_explanation_prompt(user_query, tool_result, history):

    history_text = ""
    if history:
        history_text = "\n\nPrevious conversation:\n"
        for turn in history:
            history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"


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




# ------------------------
# MAIN AGENT FUNCTION
# ------------------------

def run_agent(user_query, df, history=None):
    if history is None:
        history = []

    last_result = history[-1].get("result") if history else None
    prompt = build_decision_prompt(user_query, last_result)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    
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

    if tool == "none":
        tool_result = last_result or "No previous data available."
    else:
        filtered_df = df.copy()
        if start_date:
            filtered_df = filtered_df[filtered_df["date"] >= pd.Timestamp(start_date)]
        if end_date:
            filtered_df = filtered_df[filtered_df["date"] <= pd.Timestamp(end_date)]

        if filtered_df.empty:
            date_range_str = f"{start_date} to {end_date}" if start_date else "that period"
            return {"answer": f"No transaction found for {date_range_str}."}
        tool_result = execute_tool(tool, filtered_df)
    
    explanation_prompt = build_explanation_prompt(user_query, tool_result, history)
    explanation_response = client.models.generate_content(model=MODEL, contents=explanation_prompt)
    answer = explanation_response.text

    history.append({
        "user": user_query,
        "assistant": answer,
        "result": tool_result
    })
    if len(history) > 5:
        history.pop(0)
    
    return {"decision": decision, "answer": explanation_response.text}
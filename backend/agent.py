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
from google.genai import errors, types


#-------------------------
# MODEL SETUP
#-------------------------


client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL = "gemini-2.5-flash"


def _response_text(response) -> str:
    """Access response text without triggering the multi-part candidates warning."""
    try:
        return response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        return response.text


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
    expenses_only = df[df["type"] == "debit"]
    return {
        "total_spent": abs(total_spent(expenses_only)),
        "top_category": top_category(expenses_only)
    }


def get_category_breakdown(df):
    expenses_only = df[df["type"] == "debit"]
    return spending_by_category(expenses_only).to_dict()


def get_anomalies_tool(df):
    anomalies = detect_anomalies(df)
    return anomalies[["description", "amount"]].to_dict(orient="records")


def get_overspending_tool(df):
    expenses_only = df[df["type"] == "debit"]
    return detect_overspending(expenses_only).to_dict()

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
You are a financial assistant agent. Today's date is {today} (for reference only — do NOT use it to infer date ranges).
{last_result_text}

You MUST choose ONE tool, OR if the question can be answered from the last result above, use "none".

CRITICAL DATE RULE: start_date and end_date MUST be null unless the user's message contains an explicit date or date range (e.g. "in January", "last month", "from March to April"). Questions about categories, savings, spending habits, or percentages do NOT imply a date range. When in doubt, use null.

TOOLS:
- get_summary
- get_category_breakdown
- get_anomalies
- get_overspending
- none  (use when answering a follow-up from previous context)

USER QUESTION:
{user_query}

Respond only with valid JSON, no markdown, no explanation:
{{
  "tool": "<tool_name>",
  "start_date": null,
  "end_date": null,
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
def run_agent_stream(user_query, df, history=None):
    if history is None:
        history = []

    last_result = history[-1].get("result") if history else None
    prompt = build_decision_prompt(user_query, last_result)
   
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    try:
        decision = json.loads(_response_text(response).strip())
    except json.JSONDecodeError:
        yield "I couldn't understand that question."
        return

    tool = decision.get("tool")
    start_date = decision.get("start_date")
    end_date = decision.get("end_date")

    if tool not in TOOLS:
        yield "I couldn't determine the correct tool to use."
        return

    if tool == "none":
        tool_result = last_result or "No previous data available."
    else:
        filtered_df = df.copy()
        date_filtered = False
        if start_date and start_date != "null":
            filtered_df = filtered_df[filtered_df["date"] >= pd.Timestamp(start_date)]
            date_filtered = True
        if end_date and end_date != "null":
            filtered_df = filtered_df[filtered_df["date"] <= pd.Timestamp(end_date)]
            date_filtered = True
        if filtered_df.empty:
            if date_filtered:
                yield "No transactions found for that period."
            else:
                yield "No transaction data is available. Please upload your bank statement first."
            return
        tool_result = execute_tool(tool, filtered_df)

    explanation_prompt = build_explanation_prompt(user_query, tool_result, history)

    # stream the explanation
    full_answer = ""
    try:
        for chunk in client.models.generate_content_stream(model=MODEL, contents=explanation_prompt):
            if chunk.text:                    # ← guard against None thinking chunks
                full_answer += chunk.text
                yield chunk.text
    except errors.ServerError as e:
        yield "The AI service is temporarily unavailable. Please try again in a moment."
        return
    except errors.APIError as e:
        if e.code == 429:
            yield "Too many requests — please wait a moment and try again."
        else:
            yield f"API error: {e.message}"
        return
    history.append({"user": user_query, "assistant": full_answer, "result": tool_result})
    if len(history) > 5:
        history.pop(0)

async def run_agent_stream_async(user_query, df, history=None):
    if history is None:
        history = []

    last_result = history[-1].get("result") if history else None
    prompt = build_decision_prompt(user_query, last_result)

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    try:
        decision = json.loads(_response_text(response).strip())
    except json.JSONDecodeError:
        yield "I couldn't understand that question."
        return

    tool = decision.get("tool")
    start_date = decision.get("start_date")
    end_date = decision.get("end_date")

    if tool not in TOOLS:
        yield "I couldn't determine the correct tool to use."
        return

    if tool == "none":
        tool_result = last_result or "No previous data available."
    else:
        filtered_df = df.copy()
        date_filtered = False
        if start_date and start_date != "null":
            filtered_df = filtered_df[filtered_df["date"] >= pd.Timestamp(start_date)]
            date_filtered = True
        if end_date and end_date != "null":
            filtered_df = filtered_df[filtered_df["date"] <= pd.Timestamp(end_date)]
            date_filtered = True
        if filtered_df.empty:
            if date_filtered:
                yield "No transactions found for that period."
            else:
                yield "No transaction data is available. Please upload your bank statement first."
            return
        tool_result = execute_tool(tool, filtered_df)

    explanation_prompt = build_explanation_prompt(user_query, tool_result, history)

    full_answer = ""
    try:
        async for chunk in await client.aio.models.generate_content_stream(
            model=MODEL, contents=explanation_prompt
        ):
            if chunk.text:
                full_answer += chunk.text
                yield chunk.text
    except errors.ServerError:
        yield "The AI service is temporarily unavailable. Please try again."
        return
    except errors.APIError as e:
        yield f"Error: {e.message}"
        return

    history.append({"user": user_query, "assistant": full_answer, "result": tool_result})
    if len(history) > 5:
        history.pop(0)

def run_agent(user_query, df, history=None):
    if history is None:
        history = []

    last_result = history[-1].get("result") if history else None
    prompt = build_decision_prompt(user_query, last_result)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    
    # Parse JSON from LLM
    try:
        decision = json.loads(_response_text(response).strip())
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
        if start_date and start_date != "null":
            filtered_df = filtered_df[filtered_df["date"] >= pd.Timestamp(start_date)]
        if end_date and end_date != "null":
            filtered_df = filtered_df[filtered_df["date"] <= pd.Timestamp(end_date)]

        if filtered_df.empty:
            date_range_str = f"{start_date} to {end_date}" if start_date else "that period"
            return {"answer": f"No transaction found for {date_range_str}."}
        tool_result = execute_tool(tool, filtered_df)
    
    explanation_prompt = build_explanation_prompt(user_query, tool_result, history)

    explanation_response = client.models.generate_content(model=MODEL, contents=explanation_prompt)
    answer = _response_text(explanation_response)

    history.append({
        "user": user_query,
        "assistant": answer,
        "result": tool_result
    })
    if len(history) > 5:
        history.pop(0)

    return {"decision": decision, "answer": answer}
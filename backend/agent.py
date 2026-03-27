from analytics import total_spent, top_category, spending_by_category
from anomaly_detection import detect_anomalies
import google.generativeai as genai
import os

def get_anomalies(df):
    anomalies = detect_anomalies(df)
    return anomalies[["description", "amount"]].to_dict(orient="records")

def get_category_breakdown(df):
    return spending_by_category(df).to_dict()

def get_summary(df):
    return{
        "total spent": abs(total_spent(df)),
        "total category": top_category(df)
    }

def execute_tool(tool_name, df):
    if tool_name == "get_summary":
        return get_summary(df)
    elif tool_name == "get_category_breakdown":
        return get_category_breakdown(df)
    elif tool_name == "get_anomalies":
        return get_anomalies(df)
    else: 
        return "Uknown tool"

def extract_tool(responce_text):
    for line in responce_text.split("\n"):
        if "Tool:" in line:
            return line.split("Tool:")[1].strip()
    return None

def build_explanation_prompt(user_query, tool_result):
    return f"""
You are a financial assistant.

The user asked:
{user_query}

Here is the computed data:
{tool_result}

Explain the answer clearly and give a useful insight.

Do NOT mention tools.
Be concise.
"""

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-3-flash-preview")

def run_agent(user_query, df):
    
    decision_prompt = f"""
You are a financial assistant agent.

You MUST choose ONE tool.

TOOLS:
- get_summary
- get_category_breakdown
- get_anomalies

USER QUESTION:
{user_query}

Respond EXACTLY like:
Tool: <tool_name>
Reason: <why>
"""
    
    decision_response = model.generate_content(decision_prompt)
    decision_text = decision_response.text

    tool = extract_tool(decision_text)

    tool_result = execute_tool(tool, df)

    explanation_prompt = build_explanation_prompt(user_query, tool_result)
    explanation_response = model.generate_content(explanation_prompt)

    return {
        "decision": decision_text,
        "answer": explanation_response.text
    }

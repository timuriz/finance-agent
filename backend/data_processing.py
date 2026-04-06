import pandas as pd
from categorization import categorize_transaction
from anomaly_detection import detect_anomalies

def load_data(path):
    df = pd.read_csv(path, sep=None, engine="python")
    return df

def handle_missing_values(df):
   df = df.dropna(subset=["date", "description", "amount"])
   return df

def remove_duplicates(df):
   df = df.drop_duplicates()
   return df

def detect_amount_pattern(df):
   if (df["amount"] < 0).any():
      return "signed"
   else:
      return "unsigned"

def clean_data(df):
   df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True, errors="coerce")
   df["amount"] = df["amount"].astype(float)
   
   pattern = detect_amount_pattern(df)
   
   if pattern == "signed":
      df["type"] = df["amount"].apply(lambda x: "debit" if x < 0 else "credit")
   
   elif pattern == "unsigned":
    
      df["amount"] = -df["amount"]
      df["type"] = "debit"

   return df

column_map = {"date": ["date", "date_time", "transaction_date", "time", "when"],
              "description": ["description", "details", "about", "category"],
               "amount": ["amount", "value", "sum"] }

def map_columns(df):
   df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

   mapping = {}

   for standard_col, possible_names in column_map.items():
      for col in df.columns:
         if any(name in col for name in possible_names):
            mapping[col] = standard_col
            break
   
   df = df.rename(columns=mapping)
   return df

REQUIRED = ["date", "description", "amount"]

def validate_columns(df):
   for col in REQUIRED:
      if col not in df.columns:
         raise ValueError(f"Missing required column: {col}")

def normalize_amount(df):
   if "amount" in df.columns:
      return df
   
   elif "debit" in df.columns and "credit" in df.columns:
      df["amount"] = df["credit"] - df["debit"]
      return df
   
   else:
      raise ValueError("No valid amount column found")
   
def total_spent(df):
    return df["amount"].sum()

def spending_by_category(df):
    return df.groupby("category")["amount"].sum().sort_values()

def top_category(df):
    return df.groupby("category")["amount"].sum().idxmin()

def category_by_percentage(df):
    total = abs(df["amount"].sum())

    return (abs(spending_by_category(df)) / total ) * 100

def detect_overspending(df):
    percentages = category_by_percentage(df)

    return percentages[percentages > 30]

def date_range(df, start_date, end_date):
   return df[[date] >= start_date] & df[[date] <= end_date]

def process_data(path):
    df = load_data(path)

    df = map_columns(df)
    #print("Columns after mapping:", df.columns.tolist())
    validate_columns(df)

    df = handle_missing_values(df)
    df = remove_duplicates(df)

    df = normalize_amount(df)
    df = clean_data(df)

    df = df[["date", "description", "amount", "type"]]

    df["category"] = df["description"].apply(categorize_transaction)

    return df

if __name__ == "__main__":
   from report import generate_report
   from llm_insights import generate_ai_insight
   from agent import run_agent
   df = process_data("/Users/timur/Downloads/Expenses_clean.csv")

   total = total_spent(df)
   category_spending = spending_by_category(df)
   top_cat = top_category(df)
   anomalies = detect_anomalies(df)

   report = generate_report(df, anomalies)

   print(report)

   #ai_text = generate_ai_insight(total, category_spending, anomalies)

   #print("\n--- AI INSIGHTS ---")
   #print(ai_text)
   #result = run_agent("How much i spent last week? And what i should to to spend less money", df.head())

   #print("\n--- DECISION ---")
   #print(result["decision"])

   #print("\n--- FINAL ANSWER ---")
   #print(result["answer"])

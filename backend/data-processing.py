import pandas as pd
from categorization import categorize_transaction

def load_data(path):
    df = pd.read_csv(path)
    return df

def detect_amount_pattern(df):
   if (df["amount"] < 0).any():
      return "signed"
   else:
      return "unsigned"

def clean_data(df):
   df["date"] = pd.to_datetime(df["date"])
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

def process_data(path):
    df = load_data(path)

    df = map_columns(df)
    print("Columns after mapping:", df.columns.tolist())
    validate_columns(df)

    df = normalize_amount(df)
    df = clean_data(df)

    df = df[["date", "description", "amount", "type"]]

    #df[["description"]] = categorize_transaction(df[["description"]])
    df["category"] = df["description"].apply(categorize_transaction)

    return df

df = process_data("/Users/timur/Downloads/Expenses_clean.csv")
print(df[["amount", "type"]].head())
import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df

def normalize_columns(df):
   df = df.rename(columns={"date_time": "date", "category": "description"})
   return df

def clean_data(df):
   df["date"] = pd.to_datetime(df["date"])
   df["amount"] = df["amount"].astype(float)
   df["type"] = df["amount"].apply(lambda x: "debit" if x < 0 else "credit")

   return df

if __name__ == "__main__":
  df = load_data("/Users/timur/Downloads/Expenses_clean.csv")
  df = normalize_columns(df)
  df = clean_data(df)

print(df.head())
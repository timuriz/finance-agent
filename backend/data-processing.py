import pandas as pd



def load_data(path):
    df = pd.read_csv(path)
    return df

if __name__ == "__main__":
  df = load_data("/Users/timur/Downloads/Expenses_clean.csv")
  print(df.head())

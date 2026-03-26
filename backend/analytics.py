def total_spent(df):
    return df["amount"].sum()

def spending_by_category(df):
    return df.groupby("category")["amount"].sum()

def top_category(df):
    return df.groupby("category")["amount"].sum().idxmin()
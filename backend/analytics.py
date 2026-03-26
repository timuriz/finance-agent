def total_spend(df):
    return df["amount"].sum()

def spending_by_category(df):
    return df.groupby("category")["amount"].sum()
    
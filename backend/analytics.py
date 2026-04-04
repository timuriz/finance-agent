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
from data_processing import top_category, detect_overspending, category_by_percentage


def generate_report(df, anomalies):
    total = abs(df["amount"].sum())
    top = top_category(df)
    overspending = detect_overspending(df)

    return f"""
Summary:
Total spent: {total:.2f}

Top category:
{top}

Overspending:
{overspending.to_dict()}

Anomalies:
{len(anomalies)} unusual transactions
"""
def generate_report(df, anomalies, total, category_spending, top_cat):
    report = f"""
FINANCIAL REPORT
================

Summary:
Total spent: {abs(total):.2f}

Top spending category:
{top_cat}

Spending breakdown:
{category_spending}

Anomalies detected:
{len(anomalies)} unusual transactions

"""
    return report
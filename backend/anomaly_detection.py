import numpy as np
def detect_anomalies(df):
    anomalies = []

    for category in df["category"].unique():
        subset = df[df["category"] == category]

        mean = np.mean(df["amount"])
        std = np.std(df["amount"])

        threshold = 3 * std

        cat_anomalies = df[abs(df["amount"] - mean) > threshold]

        anomalies.append(cat_anomalies)

    return
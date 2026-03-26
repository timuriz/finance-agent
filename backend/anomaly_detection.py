import numpy as np
import pandas as pd

def detect_anomalies(df):
    anomalies = []

    for category in df["category"].unique():
        subset = df[df["category"] == category]

        mean = np.mean(subset["amount"])
        std = np.std(subset["amount"])

        threshold = 3 * std

        cat_anomalies = subset[abs(subset["amount"] - mean) > threshold]

        anomalies.append(cat_anomalies)

    return pd.concat(anomalies)
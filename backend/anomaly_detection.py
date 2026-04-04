import numpy as np
import pandas as pd

def detect_anomalies(df):
    threshold = df["amount"].std() * 2
    mean = df["amount"].mean()

    anomalies = df[abs(df["amount"] - mean) > threshold]

    return anomalies[["date", "description", "amount"]]
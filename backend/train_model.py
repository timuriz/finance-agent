import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

df = pd.read_csv("../data/synthetic_transactions_v2.csv")


x = df["description"]
y = df["category"]

vectorizer = TfidfVectorizer(ngram_range=(1,2))
X_vec = vectorizer.fit_transform(x)

model = LogisticRegression()
model.fit(X_vec, y)

_dir = os.path.dirname(__file__)  # directory of categorization.py
_model_path = os.path.join(_dir, "..", "models", "category_model.pkl")

with open(_model_path, "wb") as f:
    pickle.dump((vectorizer, model), f)
print("Model trained and saved")

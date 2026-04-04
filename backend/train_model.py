import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

df = pd.read_csv("/Users/timur/Documents/projects/synthetic_transactions.csv")

x = df["description"]
y = df["category"]

vectorizer = TfidfVectorizer(ngram_range=(1,2))
X_vec = vectorizer.fit_transform(x)

model = LogisticRegression()
model.fit(X_vec, y)

with open("finance-agent/models/category_model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("Model trained and saved")
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

df = pd.read_csv("../data/training_data.csv")

x = df["description"]
y = df["category"]

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(x)

model = LogisticRegression()
model.fit(X_vec, y)

with open("../models/category_model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("Model trained and saved")
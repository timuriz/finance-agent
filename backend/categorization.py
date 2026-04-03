import pickle

with open("../models/category_model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)


def categorize_transaction(description):
    description = description.lower()

    X = vectorizer.transform([description])
    
    probs = model.predict_proba(X)[0]
    max_prob = max(probs)
    
    if max_prob < 0.:
        return "Other"
    
    return model.predict(X)[0]
    



CATEGORY_RULES = {
    "food": ["cafe", "restaurant", "starbucks", "food"],
    "transport": ["uber", "bus", "train", "transport", "taxi"],
    "health": ["pharmacy", "health"],
    "entertainment": ["netflix", "spotify","steam", "leisure"],
    "shopping": ["clothes", "bought for myself", "gifts"]
}

def categorize_transaction_fallback(description):
    description = description.lower().strip().replace(" ", "_")

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description:
                return category
    
    return "other"

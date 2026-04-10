import pickle



with open("../models/category_model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)


CATEGORY_RULES = {
    "food": ["cafe", "restaurant", "starbucks", "food"],
    "transport": ["uber", "bus", "train", "transport", "taxi"],
    "health": ["pharmacy", "health"],
    "entertainment": ["netflix", "spotify","steam", "leisure"],
    "shopping": ["clothes", "bought for myself", "gifts"]
}


def categorize_transaction(description):
    description = description.lower()

    try:
        X = vectorizer.transform([description])
        probs = model.predict_proba(X)[0]
        max_prob = max(probs)
        
        if max_prob > 0.4:
            category = model.predict(X)[0].lower()
            return category, round(max_prob * 100)
    except Exception as e:
        pass

    description = description.lower().strip().replace(" ", "_")
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description:
                return category, 100
    
    return "other", 0

def categorize_transaction_fallback(description):
    description = description.lower().strip().replace(" ", "_")

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description:
                return category
    
    return "other"

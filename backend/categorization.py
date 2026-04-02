import pickle

with open("../models/category_model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)


def categorize_transaction(description):
    try:
        X = vectorizer.transform([description])
        return model.predict(X)[0]
    except:
        return "other"



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


print(categorize_transaction("Metro"))
print(categorize_transaction("Cafe"))
print(categorize_transaction("Loan"))
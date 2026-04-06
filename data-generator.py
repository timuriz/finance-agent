import random
import pandas as pd

# ✅ New categories
categories = [
    "groceries",
    "cafe_restaurant",
    "transport",
    "entertainment",
    "shopping",
    "health",
    "bills_utilities",
    "income"
]

# ✅ Merchants + generic sources
merchants = {
    "groceries": [
        "Lidl", "Tesco", "Carrefour", "Aldi", "BILLA", "SPAR",
        "supermarket", "grocery store", "mini market"
    ],

    "cafe_restaurant": [
        "Starbucks", "McDonald's", "KFC", "Subway",
        "restaurant", "cafe", "bistro", "pizzeria",
        "burger place", "sushi bar", "kebab shop",
        "pub", "beer bar", "wine bar", "brasserie"
    ],

    "transport": [
        "Uber", "Bolt", "metro", "bus", "tram",
        "taxi", "train", "Trainline", "fuel",
        "gas station", "parking"
    ],

    "entertainment": [
        "Netflix", "Spotify", "cinema", "movie theater",
        "concert", "festival", "bowling", "arcade",
        "theatre", "museum", "nightclub", "gaming"
    ],

    "shopping": [
        "Amazon", "Zalando", "mall",
        "clothing store", "electronics store",
        "online shop", "market"
    ],

    "health": [
        "pharmacy", "hospital", "clinic",
        "dentist", "gym", "fitness",
        "medication", "doctor"
    ],

    "bills_utilities": [
        "rent", "electricity", "water bill",
        "internet", "wifi", "mobile bill",
        "insurance", "utilities"
    ],

    "income": [
        "salary", "freelance", "bonus",
        "refund", "cashback"
    ]
}

# ✅ Strong keyword layer (VERY IMPORTANT)
keywords = {
    "groceries": [
        "groceries", "food shopping", "weekly shop",
        "vegetables", "fruits", "milk", "bread", "market", "supermarket"
    ],

    "cafe_restaurant": [
        "pizza", "burger", "coffee", "dinner", "coffee"
        "lunch", "breakfast", "brunch",
        "beer", "drinks", "wine", "takeaway",
        "delivery", "snack", "meal"
    ],

    "transport": [
        "ride", "trip", "ticket", "fare",
        "commute", "fuel", "gas", "parking"
    ],

    "entertainment": [
        "concert", "cinema", "movie", "ticket",
        "bowling", "game", "festival",
        "party", "club", "event", "show"
    ],

    "shopping": [
        "clothes", "shoes", "electronics",
        "order", "purchase", "online order",
        "delivery", "package"
    ],

    "health": [
        "medicine", "treatment", "checkup",
        "workout", "training", "supplements"
    ],

    "bills_utilities": [
        "monthly", "invoice", "bill",
        "subscription", "payment"
    ],

    "income": [
        "salary", "payout", "transfer",
        "received", "deposit"
    ]
}

# ✅ Noise (bank realism)
noise_tokens = [
    "POS", "TXN", "ONLINE", "CARD", "VISA",
    "MASTERCARD", "DEBIT", "CREDIT",
    "SEPA", "IBAN", "APP", "WEB",
    "PAYPAL", "STRIPE", "ECOM"
]

locations = [
    "LONDON", "PARIS", "BERLIN", "MADRID",
    "ROME", "AMSTERDAM", "VIENNA",
    "EU", "EUR", "SEPA", ""
]

actions = [
    "payment", "purchase", "charge",
    "txn", "order", "subscription", "fee"
]

# ✅ Amount logic (optional but powerful)
amount_ranges = {
    "groceries": (-120, -20),
    "cafe_restaurant": (-60, -5),
    "transport": (-40, -2),
    "entertainment": (-120, -10),
    "shopping": (-400, -20),
    "health": (-200, -10),
    "bills_utilities": (-1200, -30),
    "income": (500, 4000)
}

def random_case(text):
    return random.choice([str.lower, str.upper, str.title])(text)

def generate_amount(category):
    low, high = amount_ranges[category]
    return round(random.uniform(low, high), 2)

def generate_sample():
    category = random.choice(categories)

    merchant = random.choice(merchants[category])
    keyword = random.choice(keywords[category])
    noise = random.choice(noise_tokens)
    location = random.choice(locations)
    action = random.choice(actions)

    patterns = [

        # --- CLEAN HUMAN STYLE ---
        f"{merchant}",
        f"{keyword}",
        f"{merchant} {keyword}",
        f"{keyword} {merchant}",

        # --- SOCIAL / CONTEXT ---
        f"{merchant} with friends",
        f"{keyword} night",
        f"{merchant} weekend",
        f"{keyword} downtown",

        # --- FOOD / ACTIVITY ---
        f"{keyword} dinner",
        f"{keyword} lunch",
        f"{keyword} drinks",
        f"{keyword} takeaway",

        # --- EVENTS ---
        f"{keyword} tickets",
        f"{keyword} event",
        f"{merchant} entry",

        # --- SHOPPING ---
        f"bought at {merchant}",
        f"shopping {merchant}",
        f"{keyword} order",

        # --- BILLS ---
        f"{merchant} monthly",
        f"{merchant} bill",
        f"{merchant} payment",

        # --- INCOME ---
        f"{merchant} received",
        f"{merchant} transfer",

        # --- BANK STYLE ---
        f"{merchant} {noise}",
        f"{merchant} {noise} {location}",
        f"{merchant} {action} {noise}",
        f"{merchant}*{action[:3].upper()} {location}",
        f"{merchant}-{location}-{noise}",
        f"{merchant} {noise}/{location}",
        f"{noise} {merchant} {keyword}"
    ]

    description = random.choice(patterns)

    # 🔥 Inject extra keyword sometimes (VERY IMPORTANT)
    if random.random() < 0.5:
        description += f" {random.choice(keywords[category])}"

    description = random_case(description)

    amount = generate_amount(category)

    return description, category, amount


def generate_dataset(n=5000):
    data = [generate_sample() for _ in range(n)]
    df = pd.DataFrame(data, columns=["description", "category", "amount"])
    return df


if __name__ == "__main__":
    df = generate_dataset(10000)
    df.to_csv("synthetic_transactions_v2.csv", index=False)
    print("Dataset generated:", len(df))
"""
Synthetic transaction data generator.
Produces richly varied bank-statement descriptions for training the
TF-IDF + Logistic Regression categorisation model.

Run:  python data-generator.py
Out:  data/synthetic_transactions_v2.csv
"""

import random
import string
import pandas as pd

# ── Categories ────────────────────────────────────────────────────────────────
CATEGORIES = [
    "groceries",
    "cafe_restaurant",
    "transport",
    "entertainment",
    "shopping",
    "health",
    "bills_utilities",
    "income",
]

# ── Merchants ─────────────────────────────────────────────────────────────────
MERCHANTS = {
    "groceries": [
        # Discount / budget
        "Lidl", "Aldi", "Netto", "Penny", "Asda",
        # Mid-range
        "Tesco", "Sainsbury's", "Carrefour", "Rewe", "Edeka",
        "BILLA", "SPAR", "Coop", "Migros", "Kaufland",
        # Premium / organic
        "Whole Foods", "Trader Joe's", "Waitrose", "M&S Food",
        "Marks Spencer", "Naturkost", "Bio Company",
        # Generic
        "supermarket", "grocery store", "mini market",
        "food market", "corner shop", "local market",
    ],

    "cafe_restaurant": [
        # Coffee chains
        "Starbucks", "Costa Coffee", "Pret a Manger", "Caffe Nero",
        "Tim Hortons", "Dunkin", "Greggs",
        # Fast food
        "McDonald's", "Burger King", "KFC", "Subway", "Five Guys",
        "Shake Shack", "Wendy's", "Popeyes", "Chick-fil-A",
        # Pizza
        "Pizza Hut", "Domino's", "Papa John's", "Pizza Express",
        # Casual dining
        "Nando's", "Wagamama", "Chipotle", "Olive Garden",
        "TGI Friday's", "Applebee's", "Chili's", "itsu", "Leon",
        # Asian
        "sushi bar", "ramen shop", "dim sum", "Thai restaurant",
        "Indian takeaway", "Chinese restaurant",
        # Generic
        "restaurant", "cafe", "bistro", "pizzeria",
        "burger joint", "kebab shop", "brasserie",
        "wine bar", "pub", "tapas bar", "diner",
        "food truck", "street food", "bakery",
    ],

    "transport": [
        # Ride-hailing
        "Uber", "Bolt", "Lyft", "Free Now", "Cabify",
        # Rail / metro
        "National Rail", "Eurostar", "Deutsche Bahn", "SNCF",
        "Renfe", "Trenitalia", "TfL", "metro", "tram",
        # Bus / coach
        "FlixBus", "Megabus", "National Express", "Greyhound",
        # Air
        "Ryanair", "EasyJet", "Wizz Air", "Vueling",
        # Car rental
        "Hertz", "Sixt", "Enterprise", "Avis", "Europcar",
        # Fuel
        "Shell", "BP", "Total", "Esso", "Texaco",
        "Q8", "Neste", "Orlen", "Circle K",
        # Parking / toll
        "parking", "car park", "toll gate",
        # Generic
        "taxi", "bus", "train", "ferry",
    ],

    "entertainment": [
        # Streaming – video
        "Netflix", "HBO Max", "Disney+", "Apple TV+",
        "Amazon Prime Video", "Hulu", "Paramount+",
        "Peacock", "Crunchyroll", "MUBI",
        # Streaming – music
        "Spotify", "Apple Music", "Tidal", "Deezer",
        "YouTube Premium", "Amazon Music",
        # Gaming
        "Steam", "PlayStation", "Xbox", "Nintendo",
        "Epic Games", "GOG", "Humble Bundle",
        "Twitch", "Roblox",
        # Venues
        "cinema", "AMC", "Odeon", "Vue Cinema",
        "Cinepolis", "Cineworld",
        "concert venue", "theatre", "opera house",
        "museum", "art gallery", "science center",
        # Activities
        "bowling", "escape room", "laser tag",
        "mini golf", "trampoline park",
        "nightclub", "festival", "comedy club",
    ],

    "shopping": [
        # Fashion
        "Zara", "H&M", "ASOS", "Shein", "Uniqlo",
        "Gap", "Mango", "Primark", "Next", "Topshop",
        "Nike", "Adidas", "Puma", "Under Armour",
        "Ralph Lauren", "Tommy Hilfiger",
        # Online marketplaces
        "Amazon", "eBay", "Etsy", "AliExpress",
        "Wish", "Vinted",
        # Electronics
        "Apple Store", "MediaMarkt", "Currys", "Best Buy",
        "Fnac", "Saturn", "Elkjøp",
        # Home & furniture
        "IKEA", "Wayfair", "Habitat", "John Lewis",
        # Beauty
        "Sephora", "Douglas", "Boots Beauty", "MAC Cosmetics",
        "L'Occitane",
        # Sport / outdoor
        "Decathlon", "REI", "Sports Direct",
        # Generic
        "online shop", "clothing store", "electronics store",
        "department store", "outlet store",
    ],

    "health": [
        # Pharmacy chains
        "Boots", "Walgreens", "CVS", "Lloyds Pharmacy",
        "dm Drogerie", "Rossmann",
        # Insurance / health providers
        "Bupa", "AXA Health", "Cigna", "Vitality",
        "Nuffield Health", "Aviva Health",
        # Gyms / fitness
        "PureGym", "David Lloyd", "Anytime Fitness",
        "Planet Fitness", "CrossFit", "Equinox",
        "LA Fitness", "Curves",
        # Supplements / nutrition
        "MyProtein", "Holland Barrett", "GNC",
        "Bulk Powders", "iHerb",
        # Medical / dental
        "dentist", "GP surgery", "clinic",
        "hospital", "optician", "physiotherapy",
        "blood test", "laboratory", "specialist",
        # Wellness
        "yoga studio", "pilates", "spa",
        "mental health app", "therapy",
    ],

    "bills_utilities": [
        # Energy
        "EDF", "British Gas", "E.ON", "npower",
        "RWE", "Engie", "ENEL", "Vattenfall",
        "SSE", "Octopus Energy",
        # Water
        "Thames Water", "Severn Trent", "Anglian Water",
        "Scottish Water",
        # Broadband / TV
        "BT", "Virgin Media", "Sky", "TalkTalk",
        "Vodafone Home", "Deutsche Telekom",
        "Orange", "Swisscom",
        # Mobile
        "O2", "EE", "Three", "Vodafone",
        "AT&T", "Verizon", "T-Mobile",
        # Insurance
        "AXA Insurance", "Allianz", "Aviva",
        "Direct Line", "LV Insurance",
        "Admiral", "Zurich",
        # Housing
        "rent", "landlord payment", "mortgage",
        "council tax", "home insurance",
        # Generic
        "utilities", "electricity bill", "gas bill",
        "water bill", "broadband", "phone bill",
    ],

    "income": [
        # Salary / employment
        "salary", "payroll", "wage", "monthly pay",
        "employer", "company payroll",
        # Freelance / gig
        "Upwork", "Fiverr", "Toptal", "PeoplePerHour",
        "freelance payment", "contractor fee",
        # Platforms / marketplace
        "Stripe payout", "PayPal transfer",
        "Revolut transfer", "Wise transfer",
        # Investments
        "dividend", "interest payment",
        "investment return", "broker payout",
        # Refunds / cashback
        "refund", "cashback", "tax rebate",
        "VAT refund", "government payment",
        # Rental income
        "rental income", "Airbnb payout",
        # Bonuses
        "bonus", "commission", "incentive payment",
        "performance bonus",
    ],
}

# ── Keywords (strong category signals) ───────────────────────────────────────
KEYWORDS = {
    "groceries": [
        "groceries", "grocery", "food shopping", "weekly shop",
        "supermarket run", "vegetables", "fruits", "dairy",
        "milk", "bread", "eggs", "meat", "produce",
        "fresh food", "organic", "bulk food",
    ],

    "cafe_restaurant": [
        "coffee", "latte", "espresso", "cappuccino",
        "lunch", "dinner", "breakfast", "brunch",
        "burger", "pizza", "pasta", "sushi", "ramen",
        "kebab", "takeaway", "delivery meal", "dine in",
        "beer", "wine", "cocktail", "drinks",
        "snack", "dessert", "cake", "sandwich",
    ],

    "transport": [
        "ride", "journey", "trip", "commute",
        "ticket", "fare", "pass", "travel card",
        "fuel", "petrol", "diesel", "charging",
        "parking fee", "toll", "ferry crossing",
        "airport transfer", "shuttle",
    ],

    "entertainment": [
        "subscription", "streaming", "membership",
        "movie", "film", "series", "show",
        "concert ticket", "gig", "festival pass",
        "game", "gaming", "dlc", "in-app purchase",
        "bowling", "escape room", "event ticket",
        "night out", "club entry",
    ],

    "shopping": [
        "clothes", "clothing", "shoes", "sneakers",
        "jacket", "dress", "shirt", "trousers",
        "electronics", "laptop", "phone", "headphones",
        "gadget", "appliance",
        "online order", "purchase", "delivery",
        "gift", "accessories", "jewellery",
        "furniture", "homeware", "kitchenware",
    ],

    "health": [
        "medicine", "medication", "prescription",
        "vitamins", "supplements", "protein",
        "gym", "workout", "fitness class",
        "doctor visit", "dental", "checkup",
        "physio", "therapy", "massage",
        "health insurance", "medical",
    ],

    "bills_utilities": [
        "monthly bill", "direct debit", "standing order",
        "rent payment", "mortgage payment",
        "electricity", "gas", "water",
        "broadband bill", "phone plan",
        "insurance premium", "council tax",
        "subscription renewal", "annual fee",
    ],

    "income": [
        "salary received", "wage credit",
        "freelance income", "project payment",
        "payout", "transfer received",
        "refund received", "cashback credited",
        "dividend payment", "interest credited",
        "bonus received", "commission paid",
    ],
}

# ── Bank-statement noise ──────────────────────────────────────────────────────
NOISE_TOKENS = [
    "POS", "TXN", "ONLINE", "CARD", "VISA", "MASTERCARD",
    "DEBIT", "CREDIT", "SEPA", "IBAN", "APP", "WEB",
    "PAYPAL", "STRIPE", "ECOM", "CONTACTLESS",
    "RECURRING", "AUTOPAY", "DIRECT DEBIT",
]

LOCATIONS = [
    "LONDON", "PARIS", "BERLIN", "MADRID", "ROME",
    "AMSTERDAM", "VIENNA", "WARSAW", "PRAGUE",
    "DUBLIN", "LISBON", "BRUSSELS", "STOCKHOLM",
    "NEW YORK", "LOS ANGELES", "CHICAGO",
    "EU", "GB", "DE", "FR", "US", "",
]

ACTIONS = [
    "payment", "purchase", "charge", "txn",
    "order", "subscription", "fee", "transfer",
    "debit", "credit", "invoice",
]

# ── Amount ranges ─────────────────────────────────────────────────────────────
AMOUNT_RANGES = {
    "groceries":       (-130,  -10),
    "cafe_restaurant": (-65,    -3),
    "transport":       (-80,    -2),
    "entertainment":   (-150,   -5),
    "shopping":        (-500,  -15),
    "health":          (-250,   -5),
    "bills_utilities": (-1500, -30),
    "income":          (400,  6000),
}

# ── Category weights (income is naturally rarer) ──────────────────────────────
WEIGHTS = {
    "groceries":       12,
    "cafe_restaurant": 14,
    "transport":       13,
    "entertainment":   11,
    "shopping":        13,
    "health":          10,
    "bills_utilities": 11,
    "income":           6,
}

_CATEGORIES_POOL = [c for c, w in WEIGHTS.items() for _ in range(w)]


def _ref_number():
    """Short alphanumeric reference as seen in real bank statements."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(6, 10)))


def _random_case(text):
    choice = random.random()
    if choice < 0.40:
        return text.upper()
    elif choice < 0.70:
        return text.title()
    else:
        return text.lower()


def generate_amount(category):
    lo, hi = AMOUNT_RANGES[category]
    return round(random.uniform(lo, hi), 2)


def generate_description(category):
    merchant = random.choice(MERCHANTS[category])
    keyword  = random.choice(KEYWORDS[category])
    noise    = random.choice(NOISE_TOKENS)
    location = random.choice(LOCATIONS)
    action   = random.choice(ACTIONS)
    ref      = _ref_number()

    patterns = [
        # ── Plain human descriptions ──────────────────────────────────────
        merchant,
        keyword,
        f"{merchant} {keyword}",
        f"{keyword} at {merchant}",
        f"{keyword} from {merchant}",

        # ── Contextual / social ───────────────────────────────────────────
        f"{merchant} with friends",
        f"{keyword} outing",
        f"{merchant} visit",
        f"{keyword} downtown",
        f"{keyword} near work",

        # ── Activity combos ───────────────────────────────────────────────
        f"{merchant} - {keyword}",
        f"{keyword} ({merchant})",
        f"{merchant} / {keyword}",

        # ── Bills / recurring ─────────────────────────────────────────────
        f"{merchant} monthly",
        f"{merchant} bill",
        f"{merchant} payment",
        f"DD {merchant}",
        f"Direct Debit {merchant}",
        f"SO {merchant}",
        f"Standing Order {merchant}",
        f"{merchant} direct debit",
        f"{merchant} auto-renewal",

        # ── Income patterns ───────────────────────────────────────────────
        f"{merchant} received",
        f"{merchant} inbound transfer",
        f"Credit {merchant}",
        f"Payment from {merchant}",
        f"{keyword} credited",

        # ── Shopping / order ─────────────────────────────────────────────
        f"Order {merchant}",
        f"Purchase {merchant}",
        f"{merchant} online",
        f"{merchant} delivery",
        f"Return {merchant}",

        # ── Bank statement styles ─────────────────────────────────────────
        f"{merchant} {noise}",
        f"{merchant} {noise} {location}",
        f"{merchant} {action} {noise}",
        f"{merchant}*{action[:3].upper()} {location}",
        f"{merchant}*{ref}",
        f"{merchant}-{location}-{noise}",
        f"{merchant} {noise}/{location}",
        f"{noise} {merchant} {keyword}",
        f"{noise} {merchant} {location}",
        f"{merchant} {ref} {location}",
        f"{merchant} | {action} | {ref}",
        f"{merchant}/{action}/{location}",
        f"CARD PAYMENT {merchant} {location}",
        f"CONTACTLESS {merchant}",
        f"RECURRING {merchant}",
        f"AUTOPAY {merchant} {action}",
        f"{merchant} {noise} REF {ref}",

        # ── Truncated merchant (realistic statement trimming) ──────────────
        f"{merchant[:6].upper()} {location} {noise}",
    ]

    desc = random.choice(patterns)

    # Inject an extra keyword ~55% of the time (boosts bigram signal)
    if random.random() < 0.55:
        desc = f"{desc} {random.choice(KEYWORDS[category])}"

    return _random_case(desc)


def generate_sample():
    category    = random.choice(_CATEGORIES_POOL)
    description = generate_description(category)
    amount      = generate_amount(category)
    return description, category, amount


def generate_dataset(n: int = 50_000) -> pd.DataFrame:
    data = [generate_sample() for _ in range(n)]
    df   = pd.DataFrame(data, columns=["description", "category", "amount"])
    return df


if __name__ == "__main__":
    import os

    out_dir  = os.path.join(os.path.dirname(__file__), "data")
    out_path = os.path.join(out_dir, "synthetic_transactions_v2.csv")

    print("Generating dataset…")
    df = generate_dataset(50_000)
    df.to_csv(out_path, index=False)

    print(f"Saved {len(df):,} rows → {out_path}")
    print("\nCategory distribution:")
    print(df["category"].value_counts().to_string())

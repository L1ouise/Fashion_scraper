from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import datetime

load_dotenv()

uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "FASHIONDB")
collection_name = os.getenv("DB_COLLECTION", "PRODUCTS")

df = pd.read_csv("data/products_labeled.csv")

client = MongoClient(uri)
db = client[db_name]
collection = db[collection_name]

for _, row in df.iterrows():
    collection.update_one(
        {"title": row["title"]},    # correspondance par titre
        {"$set": {"label": row["label"]}}  # ajout du champ label
    )

print("✅ Labels intégrés dans MongoDB !")
# export_from_mongo.py
import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def export_mongo_to_csv():
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "FASHIONDB")
    collection_name = os.getenv("DB_COLLECTION", "PRODUCTS")

    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    docs = list(collection.find({}, {"_id": 0}))  # on enlève l'id Mongo

    if not docs:
        print("⚠️ Aucune donnée trouvée dans MongoDB.")
        return

    df = pd.DataFrame(docs)
    os.makedirs("data", exist_ok=True)
    csv_path = "data/products.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"✅ Exportation terminée : {len(df)} produits enregistrés dans {csv_path}")

if __name__ == "__main__":
    export_mongo_to_csv()

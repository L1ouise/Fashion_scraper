import os
import numpy as np
from pymongo import MongoClient
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.utils import img_to_array, load_img
from dotenv import load_dotenv 
from tqdm import tqdm
import requests
from io import BytesIO
from PIL import Image
import os
from datetime import datetime

load_dotenv()

uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "FASHIONDB")
collection_name = os.getenv("DB_COLLECTION", "PRODUCTS")

client = MongoClient(uri)
db = client[db_name]
collection = db[collection_name]

base_model = MobileNetV2(weights="imagenet", include_top=False, pooling="avg")  # GlobalAveragePooling
model = Model(inputs=base_model.input, outputs=base_model.output)

def load_image(img_path_or_url, target_size=(224,224)):
    try:
        if img_path_or_url.startswith("http"):
            response = requests.get(img_path_or_url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            img = Image.open(img_path_or_url).convert("RGB")
        img = img.resize(target_size)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        return img_array
    except Exception as e:
        print(f"❌ Impossible de charger l'image {img_path_or_url} : {e}")
        return None
for product in tqdm(collection.find()):
    img_url = product.get("image_url")
    if not img_url:
        continue

    img_array = load_image(img_url)
    if img_array is None:
        continue

    features = model.predict(img_array)
    features = features.flatten().tolist()  # transformer en liste pour MongoDB

    # --- 5️⃣ Sauvegarder les features dans MongoDB ---
    collection.update_one(
        {"_id": product["_id"]},
        {"$set": {"features": features}}
    )

print("✅ Extraction des features terminée et sauvegardée dans MongoDB !")
import streamlit as st
import numpy as np
import pandas as pd
from pymongo import MongoClient
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image as kimage
from sklearn.neighbors import NearestNeighbors
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
import base64

st.set_page_config(
    page_title="Fashion Finder 👗",
    page_icon="👠",
    layout="wide"
)

st.markdown("""
    <style>
    .product-card {
        background-color: #fff;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .price {
        font-weight: bold;
        color: #e63946;
    }
    .category {
        font-size: 0.9em;
        color: #777;
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "FASHIONDB")
DB_COLLECTION = os.getenv("DB_COLLECTION", "PRODUCTS")
FEATURE_FIELD = "features"

def load_products_from_mongo():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[DB_COLLECTION]
    docs = list(col.find({}, {"_id":0, "product_id":1, "title":1, "price":1, "image_url":1, "label":1, FEATURE_FIELD:1}))
    df = pd.DataFrame(docs)
    # Filtre les docs sans features
    if FEATURE_FIELD in df.columns:
        df = df[df[FEATURE_FIELD].notna()]
    else:
        df[FEATURE_FIELD] = None
    df.reset_index(drop=True, inplace=True)
    return df

@st.cache_resource(show_spinner=False)
def build_nn_index(feature_matrix, n_neighbors=10, metric='cosine'):
    # sklearn NearestNeighbors (cosine) - metric 'cosine' fonctionne avec sklearn >=0.22
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric, n_jobs=-1)
    nn.fit(feature_matrix)
    return nn

# ---------- Feature extractor (MobileNetV2) ----------
@st.cache_resource(show_spinner=False)
def load_feature_extractor():
    # MobileNetV2 with global average pooling
    base = MobileNetV2(weights="imagenet", include_top=False, pooling="avg", input_shape=(224,224,3))
    return base

def preprocess_pil(img_pil, target_size=(224,224)):
    img = img_pil.convert("RGB").resize(target_size)
    arr = kimage.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    arr = preprocess_input(arr)
    return arr

def extract_features_from_pil(img_pil, extractor):
    x = preprocess_pil(img_pil)
    feat = extractor.predict(x, verbose=0)
    feat = feat.reshape(-1)
    return feat

# ---------- Main ----------
st.title("👗 Fashion Finder — Recherche par similarité")

df = load_products_from_mongo()

if df.empty:
    st.warning("Aucune donnée avec features dans MongoDB. Extrait d'abord les features et stocke-les dans le champ 'features'.")
    st.stop()

st.sidebar.markdown("**Filtres**")
site_filter = st.sidebar.multiselect("Label", options=sorted(df['label'].dropna().unique()), default=None)

if site_filter:
    df_filtered = df[df['label'].isin(site_filter)].reset_index(drop=True)
else:
    df_filtered = df

st.sidebar.write(f"Produits disponibles (avec features): {len(df_filtered)}")

# Build feature matrix
feature_list = df_filtered[FEATURE_FIELD].apply(lambda x: np.array(x, dtype=np.float32))
feature_matrix = np.stack(feature_list.values)

# Build NN index
K = st.sidebar.slider("Top K similar", 1, 12, 5)
nn = build_nn_index(feature_matrix, n_neighbors=K+1, metric='cosine')  # +1 car 1st is itself possibly

# Upload image
uploaded = st.file_uploader("Téléverse une image de vêtement (jpg/png)", type=["jpg","jpeg","png"])

if uploaded:
    img = Image.open(BytesIO(uploaded.read()))
    st.image(img, caption="Image requête", width=250)

    extractor = load_feature_extractor()
    query_feat = extract_features_from_pil(img, extractor).reshape(1, -1)

    # Perform search
    dists, idxs = nn.kneighbors(query_feat, n_neighbors=K+1)
    dists = dists.ravel()
    idxs = idxs.ravel()

    # Skip the identical item if distance ~0 (optional)
    results = []
    for dist, ix in zip(dists, idxs):
        rec = df_filtered.iloc[ix].to_dict()
        rec["score"] = float(1 - dist)  # conversion cosine distance -> similarity (approx)
        results.append(rec)

    # If self-match exists, drop it (very small dist)
    results = [r for r in results if r.get("image_url") and r["score"] < 0.999]  # keep others (tweak threshold)
    results = results[:K]

    st.markdown("### Résultats similaires")
    cols = st.columns(min(K,5))
    for i, prod in enumerate(results):
        with cols[i % len(cols)]:
            # Afficher image si disponible
            if prod.get("image_url"):
                st.image(prod["image_url"], width=180)
            st.markdown(f"**{prod.get('title','')}**")
            st.markdown(f"_Label_: {prod.get('label','')}")
            st.markdown(f"_URL_: {prod.get('image_url','')}")
            st.markdown(f"**Prix**: {prod.get('price','N/A')}")
            st.markdown(f"**Score**: {prod.get('score'):.3f}")
            st.markdown("---")
else:
    st.info("Téléverse une image pour obtenir les top K propositions similaires.")

# Bonus: quick table view
with st.expander("Voir la table des produits (échantillon)"):
    st.dataframe(df_filtered.sample(min(50, len(df_filtered))))
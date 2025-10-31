import pandas as pd
import unidecode  # pip install unidecode

df = pd.read_csv("data/products.csv")

def infer_label(title):
    title_clean = unidecode.unidecode(title.lower())  # enlever accents

    # Vêtements
    if any(x in title_clean for x in ["robe", "dresse"]): return "robe"
    elif any(x in title_clean for x in ["jupe", "skirt"]): return "jupe"
    elif any(x in title_clean for x in ["pantalon", "trousers", "jean", "legging"]): return "pantalon"
    elif any(x in title_clean for x in ["short", "bermuda"]): return "short"
    elif any(x in title_clean for x in ["t-shirt", "tee", "top", "debardeur"]): return "t-shirt"
    elif any(x in title_clean for x in ["pull", "sweater", "cardigan"]): return "pull"
    elif any(x in title_clean for x in ["veste", "jacket", "blazer"]): return "veste"
    elif any(x in title_clean for x in ["manteau", "coat", "overcoat"]): return "manteau"
    elif any(x in title_clean for x in ["chemise", "shirt", "blouse"]): return "chemise"
    elif any(x in title_clean for x in ["sweat", "hoodie", "sweatshirt"]): return "sweat"

    # Chaussures
    elif any(x in title_clean for x in ["chaussure", "sneaker", "boots", "sandale", "heel"]): return "chaussure"

    # Accessoires
    elif any(x in title_clean for x in ["sac", "handbag", "bag", "pochette", "clutch"]): return "sac"
    elif any(x in title_clean for x in ["ceinture", "belt"]): return "ceinture"
    elif any(x in title_clean for x in ["lunette", "glasses", "sunglasses"]): return "lunette"
    elif any(x in title_clean for x in ["chapeau", "hat", "cap"]): return "chapeau"
    elif any(x in title_clean for x in ["bijou", "jewel", "necklace", "earring", "bracelet", "ring"]): return "bijou"
    elif any(x in title_clean for x in ["foulard", "scarf"]): return "foulard"

    # Autres
    else: 
        return "autre"

df["label"] = df["title"].apply(infer_label)
df.to_csv("data/products_labeled.csv", index=False)
print("✅ Fichier labellisé enregistré : data/products_labeled.csv")

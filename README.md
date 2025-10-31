# 👗 FashionScraper — H&M Visual Product Finder

### 🎯 Objectif
Application Streamlit permettant de parcourir et visualiser les vêtements issus du site H&M.  
Ce projet constitue une première étape vers un moteur de **recherche visuelle intelligente** dans la mode.

---

### 🧩 Fonctionnalités actuelles
- Scraping automatisé des produits H&M (titre, prix, image, lien).  
- Stockage des données dans MongoDB Atlas.  
- Interface Streamlit pour afficher les produits et leurs caractéristiques.  
- Visualisation simple des catégories et des prix.

---

### ⚙️ Technologies utilisées
| Domaine | Outils |
|----------|--------|
| Web Scraping | Selenium, BeautifulSoup |
| Base de données | MongoDB Atlas |
| Interface Web | Streamlit |
| Data Processing | Pandas, NumPy |
| IA (en perspective) | TensorFlow, MobileNetV2 |

---

### 🧱 Structure du projet
fashion_scraper/
├── app.py
├── app_streamlit.py
├── utils.py
├── data/
├── notebook.py
├── extra_features.py
├── export_from_mongo.py
├── requirement.txt
├── README.md
└── .gitignore


---

### 🚀 Lancer le projet

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/L1ouise/Fashion_scraper.git
   cd fashion_scraper
2. **Installer les dépendances**
   pip install -r requirements.txt
3. **Lancer l'application streamlit**
   streamlit run app_streamlit.py

4. **Étapes futures**

Ajout d’autres sites : Zalando, Farfetch, etc.

Entraînement d’un modèle CNN sur des datasets de mode (DeepFashion).

Recherche visuelle basée sur les features extraits (embeddings).

Amélioration du design Streamlit.

5. **Auteur Louise NDONGUEP**
Master Big Data & Intelligence Artificielle
Projet aligné avec les valeurs de créativité et d’innovation au service de la mode éthique.

## 🥗 NutriScan — Assistant nutrition intelligent

NutriScan est une application d'aide aux choix alimentaires, basée sur des données ouvertes (OpenFoodFacts, tables nutritionnelles) et sur l'IA (LLM via LiteLLM + Groq).  
Elle permet d'analyser un produit, de comparer plusieurs références et de proposer des alternatives plus saines, avec une interface simple et pédagogique.

## 🎯 Fonctionnalités (MVP)

- **Recherche de produits** : par nom ou code-barres (OpenFoodFacts API)
- **Fiche produit détaillée** : Nutri-Score, NOVA, ingrédients, additifs, nutriments clés
- **Analyse IA** : interprétation en langage naturel (qualité nutritionnelle, risques, points forts)
- **Comparateur multi-produits** : comparaison côte à côte de plusieurs produits
- **Recommandation d'alternatives** : propositions plus saines basées sur le profil utilisateur
- **Chatbot nutrition** : questions/réponses sur les produits, les additifs, les régimes
- **Visualisations interactives** : au moins 3 graphiques (répartition nutriments, comparaison produits, etc.)

## 🛠️ Installation

```bash
# Cloner le repo
git clone https://github.com/Mourad13Git/Nutriscan_Project.git
cd Nutriscan_Project

# Installer les dépendances avec uv
uv sync

# Préparer les variables d'environnement
cp .env.example .env
# Éditer .env et renseigner la clé Groq (GROQ_API_KEY)
```

## 🚀 Lancement

```bash
uv run streamlit run app.py
```

L'application Streamlit se lancera dans votre navigateur (par défaut sur `http://localhost:8501`).

## 📊 Sources de données

- [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/) — Base de produits alimentaires ouverte
- [Tables de composition nutritionnelle ANSES / CIQUAL](https://www.data.gouv.fr/fr/datasets/table-de-composition-nutritionnelle-des-aliments-ciqual/) — Données de référence (optionnel dans un premier temps)

## 🤖 IA & LiteLLM

L'application utilise **LiteLLM** pour interagir avec des modèles Groq.  
Deux modèles doivent être configurés via les variables d'environnement :

- `LITELLM_MODEL_PRIMARY` — modèle principal (rapide) pour les réponses interactives
- `LITELLM_MODEL_SECONDARY` — modèle secondaire (plus gros / plus cher) pour des analyses plus poussées

Vous devez également fournir :

- `GROQ_API_KEY` — clé API Groq (ne jamais la committer dans Git)

## 📂 Structure du projet

```text
Nutriscan_Project/
├── .env.example        # Template des variables d'environnement
├── .gitignore
├── pyproject.toml      # Gestion des dépendances avec uv
├── uv.lock            # Lock file des dépendances
├── README.md
├── app.py              # Application Streamlit principale
├── utils/
│   ├── __init__.py
│   ├── data.py        # Intégration OpenFoodFacts API
│   ├── charts.py      # Visualisations Plotly
│   └── chatbot.py     # Intégration LiteLLM + Groq
├── data/
│   └── processed/     # Données pré-traitées 
│       └── .gitkeep
└── notebooks/         # Exploration et prototypage 
```

## 🔗 Liens

- **Repository GitHub** : [https://github.com/Mourad13Git/Nutriscan_Project](https://github.com/Mourad13Git/Nutriscan_Project)

## 👥 Équipe

- Aymane HAJLI
- Farah MEHANNEK

## 📄 Licence

MIT



# 🚀 Guide de push sur GitHub

## ✅ Fichiers supprimés
- ✅ `PRESENTATION_NUTRISCAN.md` — Supprimé
- ✅ `REPARTITION_PRESENTATION.md` — Supprimé

## ✅ Fichiers ignorés par Git (via .gitignore)
- ✅ `.env` — Clés API (ne jamais committer)
- ✅ `.venv/` — Environnement virtuel
- ✅ `__pycache__/` — Cache Python
- ✅ `*.egg-info/` — Fichiers de build
- ✅ `nutriscan.egg-info/` — Sera ignoré automatiquement

## 📋 Commandes Git à exécuter

### 1. Initialiser Git (si pas déjà fait)
```bash
git init
```

### 2. Ajouter le remote GitHub
```bash
git remote add origin https://github.com/Mourad13Git/Nutriscan_Project.git
```

### 3. Vérifier les fichiers à committer
```bash
git status
```

### 4. Ajouter tous les fichiers (sauf ceux dans .gitignore)
```bash
git add .
```

### 5. Vérifier ce qui sera commité
```bash
git status
```

### 6. Premier commit
```bash
git commit -m "Initial commit: NutriScan - Assistant nutrition intelligent"
```

### 7. Push sur GitHub
```bash
git branch -M main
git push -u origin main
```

## ⚠️ Vérifications avant le push

### Fichiers qui DOIVENT être commités
- ✅ `app.py`
- ✅ `pyproject.toml`
- ✅ `uv.lock`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `utils/` (tous les fichiers .py)
- ✅ `data/processed/.gitkeep`
- ✅ `.env.example` (si créé manuellement)

### Fichiers qui NE DOIVENT PAS être commités
- ❌ `.env` (contient ta clé API Groq)
- ❌ `.venv/`
- ❌ `__pycache__/`
- ❌ `nutriscan.egg-info/`
- ❌ `PRESENTATION_*.md`
- ❌ `REPARTITION_*.md`

## 🔧 Si le dossier `nutriscan.egg-info/` apparaît dans `git status`

Supprime-le manuellement (il sera régénéré si besoin) :
```bash
# Windows PowerShell
Remove-Item -Recurse -Force nutriscan.egg-info
```

## 📝 Note sur .env.example

Si le fichier `.env.example` n'existe pas encore, crée-le manuellement avec ce contenu :

```bash
# Clé API Groq (obligatoire)
GROQ_API_KEY=your_groq_api_key_here

# Modèles LiteLLM (optionnel)
LITELLM_MODEL_PRIMARY=groq/llama-3.1-8b-instant
LITELLM_MODEL_SECONDARY=groq/llama-3.1-8b-instant
```

Puis ajoute-le :
```bash
git add .env.example
```

---

**Une fois le push réussi, ton projet sera disponible sur :**
https://github.com/Mourad13Git/Nutriscan_Project


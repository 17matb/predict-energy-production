# Prévision de Production d'Énergie Renouvelable

## 📌 Contexte du projet

Dans le cadre de la transition énergétique, il devient essentiel d'anticiper la production d'énergie issue des sources renouvelables (solaire, éolienne et hydraulique).

Ce projet vise à **prédire la production quotidienne d'énergie** de trois sites situés dans la région de Montpellier à partir de données environnementales et hydrologiques locales.

Les prédictions permettront d'optimiser le fonctionnement des parcs et d'anticiper la demande énergétique.

---

## 🎯 Objectifs

- Préparer, nettoyer et structurer les données de production et environnementales
- Concevoir un modèle de machine learning capable de prédire la production quotidienne
- Sauvegarder le modèle et le scaler pour une réutilisation dans une API
- Créer une API de prédiction via FastAPI (en cours de développement par le binôme)

---

## 🧩 Architecture du projet

predict_energy_production/
├── .venv/
├── data/
│   ├── solar_production.csv
│   ├── wind_production.csv
│   └── hydro_production.csv
├── models/
│   ├── random_forest_model.pkl
│   └── scaler.pkl
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── model.py
│   ├── preprocess.py
│   ├── utils.py
│   └── database.py
├── main.py
├── requirements.txt
├── README.md
└── tests/
    └── test_model.py

---

## ⚙️ Installation et exécution

### 1️⃣ Cloner le dépôt

```bash
git clone git@github.com:17matb/predict-energy-production.git
cd predict-energy-production/predict_energy_production
```

### 2️⃣ Installer les dépendances avec uv

Ce projet utilise **uv** pour la gestion des dépendances et l'environnement virtuel.

```bash
# Installation de uv (si nécessaire)
curl -LsSf https://astral.sh/uv/install.sh | sh

# uv créera automatiquement l'environnement virtuel lors de la première exécution
```

### 3️⃣ Utilisation du programme

Le programme offre plusieurs options d'exécution via la ligne de commande :

```bash
uv run main.py -h
```

**Options disponibles :**

| Option | Description |
|--------|-------------|
| `-h, --help` | Affiche le message d'aide |
| `-e, --explore` | Retourne l'exploration des données |
| `-i, --insert` | Insère les données nettoyées dans la base de données |
| `-p, --production` | Retourne les valeurs de production pour une plage de dates |
| `-t, --train` | Lance l'entrainement de notre modèle |
| `-P, --predict` | Effectue des prédictions de production |

**Exemples d'utilisation :**

```bash
# Explorer les données
uv run main.py --explore

# Insérer les données dans la base
uv run main.py --insert

# Obtenir les valeurs de production
uv run main.py --production

# Lancer les prédictions
uv run main.py --predict
```

---

## 🧠 Modélisation

### 🔹 Préparation des données

- Nettoyage des valeurs manquantes
- Implémentation des dates absentes en prenant la médiane mensuelle 
- Harmonisation des formats de dates
- Standardisation des variables quantitatives via `StandardScaler`
- Séparation en ensembles d'entraînement et de test

### 🔹 Entraînement

Le modèle principal est un **RandomForestRegressor** de scikit-learn, entraîné pour Eolienne :

- **Éolien** : basé sur les vitesses et directions de vent

**Métriques utilisées** pour évaluer les performances :
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score

### 🔹 Sauvegarde

Les objets entraînés sont sauvegardés avec `joblib` au format `.pkl` :

```python
def save_model(model, path: str = "models/random_forest_model.pkl"):
    joblib.dump(model, path)
    print(f"\n Modèle sauvegardé sous : {path}")
```

---

## 🧩 API FastAPI (en cours de développement)

L'API permettra d'interroger les modèles via trois endpoints :

| Endpoint | Description |
|----------|-------------|
| `/predict` | Prédiction de la production éolienne quotidienne ||

L'endpoint chargera le modèle `.pkl` correspondant et renverra la prédiction à partir des valeurs fournies par l'utilisateur (requête POST JSON).

---

## 🧮 Base de données

Les données sont destinées à être stockées dans une base **PostgreSQL Supabase**. Chaque table représente un producteur (solar, wind, hydro) et contient :

- Date de mesure
- Variables environnementales
- Valeur de production correspondante

Le schéma est documenté dans la documentation technique.

---

## 🧰 Technologies utilisées

| Domaine | Outils / Librairies |
|---------|---------------------|
| Langage principal | Python 3.12 |
| Gestionnaire de dépendances | uv |
| Data Science | pandas, numpy, scikit-learn |
| Visualisation | matplotlib, seaborn |
| Sauvegarde modèle | joblib (.pkl) |
| API (en cours) | FastAPI |
| Base de données | Supabase (PostgreSQL) |
| Gestion de version | Git / GitHub |
| Organisation projet | Méthode Agile / Scrum (Trello) |

---

## 🧾 Documentation et livrables

- 📁 **Dépôt Git** : [lien GitHub du projet](https://github.com/17matb/predict-energy-production)
- 📋 **Tableau d'organisation de tâches** : lien Trello partagé avec le formateur
- 🗂️ **Schéma de base de données** : Présenté durant la présentation orale
- 🧱 **Diagramme de classes Producteur** : Présenté durant la présentation orale

---

## 🧪 Tests

Des tests unitaires sont fournis dans `tests/` pour valider le bon fonctionnement des classes et méthodes du projet.

### Tests de la classe `ProducteurEolien`

Les tests utilisent **pytest** et **unittest.mock** pour simuler les appels à la base de données sans dépendance externe.

**Cas de tests couverts :**

| Test | Description |
|------|-------------|
| `test_load_data_filtre_dates` | Vérifie que `load_data()` applique correctement le filtre sur les dates |
| `test_calculer_production_nominal` | Vérifie que `calculer_production()` retourne les statistiques attendues (moyenne, max, min) |
| `test_calculer_production_aucune_donnee` | Vérifie le comportement lorsqu'aucune donnée n'est disponible sur la période (retour de NaN) |
| `test_calculer_production_dates_hors_limites` | Vérifie que les dates hors limites renvoient un DataFrame vide avec des NaN |
| `test_calculer_production_depuis_df` | Vérifie que `calculer_production()` utilise bien `self.df` pré-chargé |
| `test_load_data_sans_bornes` | Vérifie que `load_data()` renvoie toutes les données si aucun filtre de date n'est appliqué |

**Exécution des tests :**

```bash
# Lancer tous les tests
uv run pytest

# Lancer les tests avec verbose
uv run pytest -v

# Lancer un fichier de test spécifique
uv run pytest tests/test_productors.py
```

**Exemple de test avec mock :**

```python
@patch("productors.productors.DBHandler.fetch")
def test_calculer_production_nominal(mock_fetch):
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-01-20"]),
        "prod_eolienne": [10, 20, 30]
    })
    
    prod = ProducteurEolien("prod_eolienne")
    prod.load_data("2025-01-01", "2025-01-31")
    result = prod.calculer_production()
    
    assert result["moyenne"] == 20
    assert result["max"] == 30
    assert result["min"] == 10
```

## 🚀 Améliorations futures

- Intégration complète de l'API FastAPI avec endpoints `/predict/*`
- Déploiement du modèle sur Supabase ou HuggingFace Spaces
- Interface utilisateur Streamlit (prévue mais non développée)
- Cron journalier pour récupération automatique des données depuis les API météo/hydrométrie

---

## 📄 Licence

Ce projet est développé dans un cadre éducatif.

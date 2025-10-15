import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from models.data_preparation import prepare_data


def initialize_model() -> RandomForestRegressor:
    """Initialise le modèle Random Forest avec des hyperparamètres optimisés."""
    return RandomForestRegressor(
        n_estimators=800,        # Nombre d’arbres
        min_samples_leaf=5,      # Lissage feuilles / évite les sur-réactions aux pics
        max_features='sqrt',     # Diversité entre arbres (fort impact)
        bootstrap=True,          # Échantillonnage avec remise
        n_jobs=-1,               # Utilise tous les cœurs CPU
        random_state=42          # Pour reproductibilité
    )


def train_model(model, X_train, y_train):
    """Entraîne le modèle sur les données d'entraînement."""
    print("Entraînement du modèle Random Forest...")
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Évalue le modèle sur les données de test."""
    print("\n Évaluation du modèle...")
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE : {mae:.2f}")
    print(f"MSE : {mse:.2f}")
    print(f"R²  : {r2:.2f}")

    return mae, mse, r2


def save_model(model, path: str = "models/random_forest_model.pkl"):
    """
    Sauvegarde le modèle entraîné dans un fichier .pkl à l'aide de pickle.
    
    Args:
        model: Le modèle entraîné (ex : RandomForestRegressor)
        path (str): Chemin du fichier de sortie (.pkl)
    """
    with open(path, "wb") as file:  # 'wb' = écriture binaire
        pickle.dump(model, file)

    print(f"\n Modèle sauvegardé au format .pkl sous : {path}")


def run_model():
    """
    Fonction principale pour exécuter le pipeline complet :
    - Préparation des données
    - Entraînement
    - Évaluation
    - Sauvegarde
    """
    print("Lancement du pipeline de modélisation...\n")

    # Préparation des données
    X_train, X_test, y_train, y_test = prepare_data()

    # Initialisation et entraînement
    model = initialize_model()
    model = train_model(model, X_train, y_train)

    # Évaluation et sauvegarde
    evaluate_model(model, X_test, y_test)
    save_model(model)

    print("\n Pipeline terminé avec succès.")


if __name__ == "__main__":
    run_model()

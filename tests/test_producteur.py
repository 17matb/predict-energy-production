import pandas as pd
from unittest.mock import patch
from productors.productors import ProducteurEolien 

#### Test sur le chargement de la data #####
# Vérifie que load_data() applique le filtre dates
# Usage de mock pour ne pas appeler la DB en ligne
@patch("productors.productors.DBHandler.fetch")
def test_load_data_filtre_dates(mock_fetch):
    # Simule les données retournées par la DB
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-02-01"]),
        "prod_eolienne": [10, 20, 30]
    })

    prod = ProducteurEolien("prod_eolienne")
    df = prod.load_data("2025-01-01", "2025-01-31")

    assert not df.empty
    assert df["date"].max() <= pd.Timestamp("2025-01-31")
    assert df.shape[0] == 2  # seules 2 dates sur janvier


##### Test sur le calcul de la production éolienne #####
# Vérifie que la méthode calculer_production() retourne bien les statistiques attendues
@patch("productors.productors.DBHandler.fetch")
def test_calculer_production_nominal(mock_fetch):
    # Données factices pour le test
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


##### Test sur le calcul de la production éolienne #####
# Vérifie que calculer_production() renvoie None si aucune donnée n’est disponible sur la période
@patch("productors.productors.DBHandler.fetch")
def test_calculer_production_aucune_donnee(mock_fetch):
    # Simule des données hors période demandée
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-02-01", "2025-02-10"]),
        "prod_eolienne": [10, 20]
    })

    prod = ProducteurEolien("prod_eolienne")
    df = prod.load_data("2025-01-01", "2025-01-31")
    result = prod.calculer_production()

    # Vérifie qu'aucune donnée n'a été chargée
    assert df.empty

    # Vérifie que le résultat contient des NaN (comportement actuel)
    assert pd.isna(result["moyenne"])
    assert pd.isna(result["max"])
    assert pd.isna(result["min"])




##### Test sur le calcul de la production éolienne #####
# Vérifie que calculer_production() retourne None si les dates ne correspondent à aucune donnée
@patch("productors.productors.DBHandler.fetch")
def test_calculer_production_dates_hors_limites(mock_fetch):
    # Données valides mais hors de la plage demandée
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2024-12-01", "2024-12-15", "2024-12-31"]),
        "prod_eolienne": [50, 60, 70]
    })

    prod = ProducteurEolien("prod_eolienne")
    df = prod.load_data("2025-01-01", "2025-01-31")  # DataFrame vide
    result = prod.calculer_production()

    # Vérifie que df est vide
    assert df.empty

    # Vérifie que les stats retournées contiennent des NaN
    assert pd.isna(result["moyenne"])
    assert pd.isna(result["max"])
    assert pd.isna(result["min"])



##### Test sur le calcul de la production éolienne #####
# Vérifie que calculer_production() retourne bien les statistiques à partir de self.df pré-chargé
@patch("productors.productors.DBHandler.fetch")
def test_calculer_production_depuis_df(mock_fetch):
    # Simule les données retournées par la DB
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-01-20"]),
        "prod_eolienne": [10, 20, 30]
    })

    prod = ProducteurEolien("prod_eolienne")
    # Charge self.df via load_data (dates arbitraires ici)
    prod.load_data("2025-01-01", "2025-01-31")
    
    # calculer_production() utilise self.df déjà rempli
    result = prod.calculer_production()

    assert result["moyenne"] == 20
    assert result["max"] == 30
    assert result["min"] == 10



# ##### Test sur le calcul de la production éolienne #####
# Cas sans start & end fournis
# Vérifie que load_data() renvoie toutes les données si aucun filtre de date n’est appliqué
@patch("productors.productors.DBHandler.fetch")
def test_load_data_sans_bornes(mock_fetch):
    # Simule un jeu de données complet
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01"]),
        "prod_eolienne": [10, 20, 30]
    })

    prod = ProducteurEolien("prod_eolienne")
    df = prod.load_data()  # Aucun start / end

    # Vérifie que toutes les lignes ont été récupérées
    assert df.shape[0] == 3
    # Optionnel : vérifier que les dates correspondent
    assert all(df["date"] == pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01"]))

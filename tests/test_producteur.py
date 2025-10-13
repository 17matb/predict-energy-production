import pandas as pd
from unittest.mock import patch
from productors.productors import ProducteurEolien 

##### Test sur le chargement de la data #####
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
    # Simule des données de production réalistes, toujours avec mock
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-01-20"]),
        "prod_eolienne": [10, 20, 30]
    })

    prod = ProducteurEolien("prod_eolienne")
    result = prod.calculer_production("2025-01-01", "2025-01-31")

    # Tcheck que la sortie est un dictionnaire avec les bonnes clés
    assert isinstance(result, dict)
    assert set(result.keys()) == {"moyenne", "max", "min"}

    # Tcheck valeurs calculées
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
    result = prod.calculer_production("2025-01-01", "2025-01-31")

    # Le résultat attendu est None car aucune donnée sur janvier
    assert result is None


##### Test sur le calcul de la production éolienne #####
# Vérifie que calculer_production() retourne None si les dates ne correspondent à aucune donnée
# @patch("productors.productors.DBHandler.fetch")
# def test_calculer_production_dates_hors_limites(mock_fetch):
#     # Simule des données valides mais en dehors de la plage demandée
#     mock_fetch.return_value = pd.DataFrame({
#         "date": pd.to_datetime(["2024-12-01", "2024-12-15", "2024-12-31"]),
#         "prod_eolienne": [50, 60, 70]
#     })

#     prod = ProducteurEolien("prod_eolienne")
#     result = prod.calculer_production("2025-01-01", "2025-01-31")

#     # Aucun enregistrement ne correspond à la plage de dates -> retourne None
#     assert result is None


# ##### Test sur l'intégration interne entre calculer_production() et load_data() #####
# # Vérifie que calculer_production() appelle bien load_data() avec les bons arguments
# @patch.object(ProducteurEolien, "load_data")
# def test_calculer_production_appelle_load_data(mock_load_data):
#     # Simule le retour de load_data() pour éviter tout accès à la DB
#     mock_load_data.return_value = None

#     prod = ProducteurEolien("prod_eolienne")
#     prod.calculer_production("2025-01-01", "2025-01-31")

#     # Vérifie que load_data a bien été appelée une fois
#     mock_load_data.assert_called_once_with("2025-01-01", "2025-01-31")


# Cas sans start & end fournis
# s’assurer que la méthode renvoie toutes les données si aucun filtre de date n’est appliqué
@patch("productors.productors.DBHandler.fetch")
def test_load_data_sans_bornes(mock_fetch):
    # Simule un jeu de données complet
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01"]),
        "prod_eolienne": [10, 20, 30]
    })

    prod = ProducteurEolien("prod_eolienne")
    df = prod.load_data()  # Aucun start / end

    # Vérifie qu'on a récupéré toutes les lignes
    assert df.shape[0] == 3
import pandas as pd
from unittest.mock import patch
from productors.productors import ProducteurEolien  # import corrigé

# Test sur le chargement de la data
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


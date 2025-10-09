from abc import ABC, abstractmethod
import pandas as pd 

from prepare_data.db_handler import DBHandler, supabase

class Producteur(ABC):
    def __init__(self, table_name):
        self.table_name = table_name        
    def load_data(self, start=None, end=None):
        self.df = DBHandler(client=supabase).fetch(table_name=self.table_name)
        
        # Convert 'date' column to datetime
        #self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Apply date filter
        mask = (self.df['date'] >= start) & (self.df['date'] <= end)
        
        data_filtered = self.df.loc[mask]
        
        if data_filtered.empty:
            print("there is no data between thses 2 dates")
        return data_filtered
    
    
    @abstractmethod
    def calculer_production(self, start, end):
        """Calculate statistics on the production between two dates"""
        pass
    
class ProducteurEolien(Producteur): 
    def calculer_production(self, start=None, end=None):
        data = self.load_data(start, end)
        print(f"Producteur: {self.table_name}")
        if data.empty:
            print("there is no data between thses 2 dates")
            return None
        # Ensure correct data types
        #data['prod_eolienne'] = pd.to_numeric(data['prod_eolienne'], errors='coerce')
        #data['date'] = pd.to_datetime(data['date'], errors='coerce')
        
        data_stats = {
            "moyenne": data['prod_eolienne'].mean(),
            "max": data['prod_eolienne'].max(),
            "min": data['prod_eolienne'].min()
        }
        print(f"this is the data from DB {data_stats}")
        return data_stats

        
class ProducteurSolaire(Producteur):
    def calculer_production(self, start, end):
        """Calculate solar production stats and show days with zero production"""
        data = self.load_data(start, end)
        print(f"Producteur: {self.table_name}")

        # Filter rows with zero production
        zero_prod = data[data["prod_solaire"] == 0.0]
        if not zero_prod.empty:
            print(f"\n Days without solar production:\n{zero_prod[['date', 'prod_solaire']]}")
        else:
            print("\n No days with zero solar production in this period.")
        data_solar = {
            "moyenne": data['prod_solaire'].mean(),
            "max": data['prod_solaire'].max(),
            "min": data['prod_solaire'].min()
        }
        # Return statistics
        print(data_solar)
        return data_solar


class ProducteurHydro(Producteur):
    def calculer_production(self, start, end):
        """Calculate Hydro production stats and show days with zero production"""
        data = self.load_data(start, end)
        print(f"Producteur: {self.table_name}")
        # Filter rows with zero production
        zero_prod = data[data["prod_hydro"] == 0.0]
        if not zero_prod.empty:
            print(f"\n Days without Hydro production:\n{zero_prod[['date', 'prod_hydro']]}")
        else:
            print("\n No days with zero Hydro production in this period.")
        data_hydro ={
            "moyenne": data['prod_hydro'].mean(),
            "max": data['prod_hydro'].max(),
            "min": data['prod_hydro'].min()
        }
        print(data_hydro)
        # Return statistics
        return data_hydro

from abc import ABC, abstractmethod
import pandas as pd 


class Producteur(ABC):
    def __init__(self, name, data_production):
        self.name = name
        # Pandas DataFrame contains the production
        self.data_production = data_production
        
    @abstractmethod
    def load_data(self, start, end):
        """Load production data between two dates"""
        pass
    
    
    @abstractmethod
    def calculer_production(self, start, end):
        """Calculate statistics on the production between two dates"""
        pass
    

class ProducteurEolien(Producteur):        
    def load_data(self, start, end):
        mask = (self.data_production['date'] >= start) & (self.data_production['date'] <= end)
        return self.data_production.loc[mask]

    def calculer_production(self, start, end):
        data = self.load_data(start, end)
        print(self.name)
        return {
            "moyenne": data['production'].mean(),
            "max": data['production'].max(),
            "min": data['production'].min()
        }
        
class ProducteurSolaire(Producteur):
    def load_data(self, start, end):
        """Return the production data between two dates"""
        
        mask = (self.data_production['date'] >= start) & (self.data_production['date'] <= end)
        return self.data_production.loc[mask]

    def calculer_production(self, start, end):
        """Calculate solar production stats and show days with zero production"""
        data = self.load_data(start, end)
        print(f"Producteur: {self.name}")

        # Filter rows with zero production
        zero_prod = data[data["production"] == 0.0]
        if not zero_prod.empty:
            print(f"\n Days without solar production:\n{zero_prod[['date', 'production']]}")
        else:
            print("\n No days with zero solar production in this period.")

        # Return statistics
        return {
            "moyenne": data['production'].mean(),
            "max": data['production'].max(),
            "min": data['production'].min()
        }


class ProducteurHydro(Producteur):
    def load_data(self, start, end):
        """Return the production data between two dates"""
        mask = (self.data_production['date'] >= start) & (self.data_production['date'] <= end)
        return self.data_production.loc[mask]

    def calculer_production(self, start, end):
        """Calculate Hydro production stats and show days with zero production"""
        data = self.load_data(start, end)
        print(f"Producteur: {self.name}")
        # Filter rows with zero production
        zero_prod = data[data["production"] == 0.0]
        if not zero_prod.empty:
            print(f"\n Days without Hydro production:\n{zero_prod[['date', 'production']]}")
        else:
            print("\n No days with zero Hydro production in this period.")
        # Return statistics
        return {
            "moyenne": data['production'].mean(),
            "max": data['production'].max(),
            "min": data['production'].min()
        }

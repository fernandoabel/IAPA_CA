import pandas as pd
import os

class CSVTable():
    file_path = ''
    
    def __init__(self, file_path: str, columns: list[str]):
        self.file_path = file_path
        self.columns = columns
        self._ensure_file_exists()
        self.data = self._load_table()
        pass

    def _ensure_file_exists(self):
        """Ensure CSV file exists with headers."""
        if not os.path.exists(self.file_path):
            pd.DataFrame(columns=self.columns).to_csv(self.file_path, index=False)    
    
    def _load_table(self):
        """Load table from CSV into a DataFrame, ensuring proper handling of empty files."""
        df = pd.read_csv(self.file_path, delimiter=',')
        if df.empty:
            df = pd.DataFrame(columns=self.columns)
        return df

    def save_changes(self):
        """Save the current state of DataFrames back to CSV files."""
        self.data.to_csv(self.file_path, index=False)

    def insert(self, data):
        """Insert a new record into the table."""
        if 'ID' not in data:
            data['ID'] = str(self.data.shape[0] + 1)
        self.data = pd.concat([self.data, pd.DataFrame([data], columns=self.columns)], ignore_index=True)
    
    def update(self, row_id, data):
        """Update a record in the table."""
        self.data.loc[self.data['ID'] == row_id, :] = pd.DataFrame([data], columns=self.columns)
    
    def delete(self, row_id):
        """Delete a record from the table."""
        self.data = self.data[self.data['ID'] != row_id]
    
    def save_changes(self):
        """Save the current state of the DataFrame back to CSV."""
        self.data.to_csv(self.file_path, index=False)
    


class CSVDatabase:
    prescriptions_file='database/prescriptions.csv'
    stock_file='database/stock_inventory.csv'
    regulations_file='database/regulatory_requirements.csv'

    def __init__(self):
        """Initialize the database."""
        self.prescriptions = CSVTable(self.prescriptions_file, ['ID','Patient Name','Healthcare Plan','Patient Email','Product Name','Quantity','Prescriber Name','Prescription Date', 'Prescriber Email','Approval Status','In Stock'])
        self.stock_inventory = CSVTable(self.stock_file, ['ID','Product Name','Category','Quantity','Unit','Price per Unit','Supplier','Batch Number','Expiry Date','Expiry Status','Reorder Level'])
        self.regulations = CSVTable(self.regulations_file, ['ID','Product Name','Batch Number','Date Manufactured','Meets Requirements'])
    
    def save_changes(self):
        """Save all tables."""
        self.prescriptions.save_changes()
        self.stock_inventory.save_changes()
        self.regulations.save_changes()



if __name__ == "__main__":
    # Example Usage
    db = CSVDatabase()

    print(db.prescriptions.data)
    print(db.stock_inventory.data)
    print(db.regulations.data)


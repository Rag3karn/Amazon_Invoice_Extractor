import pandas as pd
import os
from typing import List, Dict

class ExcelGenerator:
    def __init__(self, filename: str = "amazon_invoices.xlsx"):
        self.filename = filename
        self.filepath = os.path.join(os.getcwd(), filename)
    
    def create_or_append_excel(self, data_list: List[Dict]) -> str:
        """
        Create new Excel file or append to existing one
        """
        # Define the column order for the Excel file
        columns = [
            'filename', 'order_number', 'order_date', 'invoice_number', 
            'invoice_details', 'invoice_date', 'gst_registration_no', 
            'state_ut_code', 'place_of_supply', 'place_of_delivery',
            'seller_name', 'seller_address', 'billing_address', 
            'shipping_address', 'total_amount', 'descriptions', 
            'unit_prices', 'qtys', 'net_amounts', 'status'
        ]
        
        # Convert list of dictionaries to DataFrame
        new_df = pd.DataFrame(data_list)
        
        # Reorder columns to match our desired structure
        new_df = new_df.reindex(columns=columns, fill_value='')
        
        # Check if file exists
        if os.path.exists(self.filepath):
            # Read existing data
            existing_df = pd.read_excel(self.filepath)
            # Append new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        # Save to Excel
        combined_df.to_excel(self.filepath, index=False)
        
        return self.filepath
    
    def get_filepath(self) -> str:
        return self.filepath
    
    def file_exists(self) -> bool:
        return os.path.exists(self.filepath)
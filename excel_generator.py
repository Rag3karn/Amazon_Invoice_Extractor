import pandas as pd
import os
from typing import List, Dict
from datetime import datetime

class ExcelGenerator:
    def __init__(self, filename: str = None):
        if filename is None:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"amazon_invoices_{timestamp}.xlsx"
        else:
            self.filename = filename
        self.filepath = os.path.join(os.getcwd(), self.filename)
    
    def create_or_append_excel(self, data_list: List[Dict]) -> str:
        """
        Create new Excel file with the data
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
        df = pd.DataFrame(data_list)
        
        # Reorder columns to match our desired structure
        df = df.reindex(columns=columns, fill_value='')
        
        # Save to Excel (always create new file)
        df.to_excel(self.filepath, index=False)
        
        return self.filepath
    
    def get_filepath(self) -> str:
        return self.filepath
    
    def file_exists(self) -> bool:
        return os.path.exists(self.filepath)
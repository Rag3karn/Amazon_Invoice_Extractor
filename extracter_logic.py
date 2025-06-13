import re
import json
import os
from pdfminer.high_level import extract_text

def extract_invoice_data(pdf_path: str) -> dict:
    """
    Extract invoice data from PDF (first page only) and return as dictionary
    """
    try:
        # Extract text from first page only
        text = extract_text(pdf_path, page_numbers=[0])
    except Exception as e:
        return {"error": f"PDF extraction failed: {str(e)}", "status": "failed"}

    # Simple, direct patterns based on the exact text format
    result = {}
    
    # Order Number: 407-2126009-5587507
    order_match = re.search(r'Order Number:(\d{3}-\d{7}-\d{7})', text)
    result["order_number"] = order_match.group(1) if order_match else None
    
    # Order Date: 10.06.2025
    order_date_match = re.search(r'Order Date:(\d{2}\.\d{2}\.\d{4})', text)
    result["order_date"] = order_date_match.group(1) if order_date_match else None
    
    # Invoice Number: BOM7-556301
    invoice_match = re.search(r'Invoice Number :([A-Z0-9]+-[A-Z0-9]+)', text)
    result["invoice_number"] = invoice_match.group(1) if invoice_match else None
    
    # Invoice Details: MH-BOM7-1931441115-2526
    invoice_details_match = re.search(r'Invoice Details :([A-Z]{2}-[A-Z0-9]+-\d+-\d+|[A-Z0-9-]+)', text)
    result["invoice_details"] = invoice_details_match.group(1) if invoice_details_match else None
    
    # Invoice Date: 10.06.2025
    invoice_date_match = re.search(r'Invoice Date :(\d{2}\.\d{2}\.\d{4})', text)
    result["invoice_date"] = invoice_date_match.group(1) if invoice_date_match else None
    
    # GST Registration No: 27AALCR3173P1ZN
    gst_match = re.search(r'GST Registration No:([A-Z0-9]{15})', text)
    result["gst_registration_no"] = gst_match.group(1) if gst_match else None
    
    # State/UT Code: 27
    state_match = re.search(r'State/UT Code:(\d{2})', text)
    result["state_ut_code"] = state_match.group(1) if state_match else None
    
    # Place of supply: MAHARASHTRA
    supply_match = re.search(r'Place of supply:([A-Z]+)', text)
    result["place_of_supply"] = supply_match.group(1) if supply_match else None
    
    # Place of delivery: MAHARASHTRA
    delivery_match = re.search(r'Place of delivery:([A-Z]+)', text)
    result["place_of_delivery"] = delivery_match.group(1) if delivery_match else None
    
    # Updated Seller Name and Address extraction
    # Extract everything after "Sold By :" until "IN" or "*"
    seller_section_match = re.search(r'Sold By :\s*(.*?)(?:\s*IN|\s*\*)', text, re.DOTALL | re.IGNORECASE)
    if seller_section_match:
        seller_section = seller_section_match.group(1).strip()
        # Clean up whitespace and split into lines
        seller_lines = [line.strip() for line in seller_section.split('\n') if line.strip()]
        
        if seller_lines:
            # First line is the seller name
            result["seller_name"] = seller_lines[0]
            # Remaining lines form the seller address
            if len(seller_lines) > 1:
                result["seller_address"] = ' '.join(seller_lines[1:])
            else:
                result["seller_address"] = None
        else:
            result["seller_name"] = None
            result["seller_address"] = None
    else:
        # Fallback to original logic if the new pattern doesn't match
        seller_match = re.search(r'Sold By :\s*([A-Za-z][A-Za-z\s&.,()]+?)(?:\s*\*|\s*IN)', text)
        result["seller_name"] = seller_match.group(1).strip() if seller_match else None
        
        # Seller Address: Everything after * until PAN No
        seller_addr_match = re.search(r'(?:\*|IN)\s*(.*?)\s*PAN No:', text, re.DOTALL)
        if seller_addr_match:
            addr = seller_addr_match.group(1).strip()
            addr = re.sub(r'\s+', ' ', addr)  # Clean whitespace
            result["seller_address"] = addr
        else:
            result["seller_address"] = None
    
    # Billing Address: After "Billing Address :" until "State/UT Code"
    billing_match = re.search(r'Billing Address :\s*(.*?)\s*State/UT Code:', text, re.DOTALL)
    if billing_match:
        addr = billing_match.group(1).strip()
        addr = re.sub(r'\s+', ' ', addr)
        result["billing_address"] = addr
    else:
        result["billing_address"] = None
    
    # Shipping Address: After "Shipping Address :" until "State/UT Code"
    shipping_match = re.search(r'Shipping Address :\s*(.*?)\s*State/UT Code:', text, re.DOTALL)
    if shipping_match:
        addr = shipping_match.group(1).strip()
        addr = re.sub(r'\s+', ' ', addr)
        result["shipping_address"] = addr
    else:
        result["shipping_address"] = None
    
    # Total Amount: Find ₹764.00 (before "Amount in Words")
    total_match = re.search(r'₹(\d+\.\d{2})\s*Amount in Words:', text)
    result["total_amount"] = f"₹{total_match.group(1)}" if total_match else None
    
    # Extract table data
    table_data = extract_simple_table_data(text)
    result.update(table_data)
    
    # Add filename and status
    result["filename"] = os.path.basename(pdf_path)
    result["status"] = "success" if result.get("invoice_number") else "failed"
    
    return result

def extract_simple_table_data(text: str) -> dict:
    """Simple table data extraction"""
    
    result = {
        "descriptions": [],
        "unit_prices": [],
        "qtys": [],
        "net_amounts": []
    }
    
    # Find the product section - look for a line starting with a number and containing price information
    product_section = re.search(r'\d+\s+(.*?)(?=\s*TOTAL:|$)', text, re.DOTALL)
    
    if product_section:
        product_line = product_section.group(1)
        
        # Extract description (everything before first ₹)
        desc_match = re.search(r'(.*?)(?=₹)', product_line, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            description = re.sub(r'\s+', ' ', description)
            result["descriptions"] = [description]
        
        # Find all ₹ amounts in the product line
        amounts = re.findall(r'₹\s*([\d,]+\.\d{2})', product_line)
        
        if len(amounts) >= 2:
            result["unit_prices"] = [f"₹{amounts[0]}"]  # First amount is unit price
            result["net_amounts"] = [f"₹{amounts[1]}"]  # Second amount is net amount
        elif len(amounts) >= 1:
            result["unit_prices"] = [f"₹{amounts[0]}"]
            result["net_amounts"] = [f"₹{amounts[0]}"]
        
        # Extract quantity (look for a number between the amounts)
        qty_match = re.search(r'(\d+)\s*(?:PCS|QTY|NOS|UNIT|PCS\.|QTY\.|NOS\.|UNIT\.)?', product_line)
        if qty_match:
            result["qtys"] = [qty_match.group(1)]
        else:
            result["qtys"] = ["1"]
    
    return result

# Test locally
if __name__ == "__main__":
    result = extract_invoice_data("C:\\Users\\karng\\Desktop\\Amazon_Invoice_Extractor\\Data\\invoice_1.pdf")
    print(json.dumps(result, indent=2, ensure_ascii=False))
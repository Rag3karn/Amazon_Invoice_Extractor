from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from excel_generator import ExcelGenerator
import os

# Create a router instance
router = APIRouter()

# Global Excel generator instance
excel_gen = ExcelGenerator()

@router.get("/download-excel")
def download_excel():
    """Download the generated Excel file"""
    filepath = excel_gen.get_filepath()
    
    if not excel_gen.file_exists():
        raise HTTPException(status_code=404, detail="Excel file not found. Please process some invoices first.")
    
    return FileResponse(
        path=filepath,
        filename="amazon_invoices.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.post("/generate-excel")
def generate_excel(data: dict):
    """Generate or append to Excel file with processed invoice data"""
    try:
        # Extract the results from the data
        results = data.get("results", [])
        
        if not results:
            raise HTTPException(status_code=400, detail="No results provided")
        
        # Generate/append to Excel
        filepath = excel_gen.create_or_append_excel(results)
        
        return {
            "message": "Excel file generated/updated successfully",
            "filepath": filepath,
            "records_added": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")
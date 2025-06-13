from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from excel_generator import ExcelGenerator
import os

# Create a router instance
router = APIRouter()

# Store the latest Excel file path
latest_excel_path = None

@router.get("/download-excel")
def download_excel():
    """Download the generated Excel file"""
    global latest_excel_path
    
    if not latest_excel_path or not os.path.exists(latest_excel_path):
        raise HTTPException(status_code=404, detail="Excel file not found. Please process some invoices first.")
    
    return FileResponse(
        path=latest_excel_path,
        filename=os.path.basename(latest_excel_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.post("/generate-excel")
def generate_excel(data: dict):
    """Generate Excel file with processed invoice data"""
    try:
        global latest_excel_path
        
        # Extract the results from the data
        results = data.get("results", [])
        
        if not results:
            raise HTTPException(status_code=400, detail="No results provided")
        
        # Create new ExcelGenerator instance
        excel_gen = ExcelGenerator()
        
        # Generate Excel
        filepath = excel_gen.create_or_append_excel(results)
        
        # Store the latest file path
        latest_excel_path = filepath
        
        return {
            "message": "Excel file generated successfully",
            "filepath": filepath,
            "filename": excel_gen.filename,
            "records_added": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")
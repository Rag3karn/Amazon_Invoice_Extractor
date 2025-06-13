from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

# Create a router instance
router = APIRouter()

# In-memory cache for results (shared with main API)
result_cache = {}

@router.get("/download-excel")
def download_excel():
    if "excel" not in result_cache:
        raise HTTPException(404, "Excel not generated")
    
    return FileResponse(
        path=result_cache["excel"],
        filename="amazon_invoices.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) 
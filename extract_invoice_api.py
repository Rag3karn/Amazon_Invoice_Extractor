from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from extracter_logic import extract_invoice_data, extract_simple_table_data
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import uuid
from pdfminer.high_level import extract_text
from concurrent.futures import ThreadPoolExecutor
import asyncio
from excel_download_api import router as excel_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

app = FastAPI(title="Amazon Invoice Extractor API", version="1.0.0")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create thread pool executor for async operations
executor = ThreadPoolExecutor(max_workers=5)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the excel download router
app.include_router(excel_router)

# In-memory cache for results
result_cache = {}

async def process_pdf(file_path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, extract_invoice_data, file_path)

async def process_text(text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, extract_simple_table_data, text)

@app.post("/extract-invoice")
@limiter.limit("10/minute")
async def extract_invoice(request: Request, file: UploadFile = File(...)):
    """Extract data from a single invoice PDF"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file to temp location
        file_ext = file.filename.split(".")[-1]
        temp_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.{file_ext}"
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process invoice data asynchronously
        result = await process_pdf(temp_path)
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        # Cache result
        cache_id = str(uuid.uuid4())
        result_cache[cache_id] = result
        
        return {"cache_id": cache_id, "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/extract-multiple-invoices")
@limiter.limit("5/minute")
async def extract_multiple_invoices(request: Request, files: List[UploadFile] = File(...)):
    """Extract data from multiple invoice PDFs"""
    try:
        if len(files) > 10:  # Limit to 10 files at once
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed at once")
        
        results = []
        
        for file in files:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "Only PDF files are allowed"
                })
                continue
            
            try:
                # Save uploaded file to temp location
                file_ext = file.filename.split(".")[-1]
                temp_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.{file_ext}"
                
                with open(temp_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Process invoice data asynchronously
                result = await process_pdf(temp_path)
                result["original_filename"] = file.filename
                results.append(result)
                
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Cache results
        cache_id = str(uuid.uuid4())
        result_cache[cache_id] = results
        
        return {
            "cache_id": cache_id, 
            "results": results,
            "total_processed": len(results),
            "successful": len([r for r in results if r.get("status") == "success"]),
            "failed": len([r for r in results if r.get("status") == "failed"])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Amazon Invoice Extractor API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
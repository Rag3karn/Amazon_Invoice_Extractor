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

app = FastAPI()

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
    try:
        # Save uploaded file to temp location
        file_ext = file.filename.split(".")[-1]
        temp_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.{file_ext}"
        
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text from PDF
        text = extract_text(temp_path, page_numbers=[0])
        
        # Process invoice data asynchronously
        result = await process_pdf(temp_path)
        
        # Process table data asynchronously
        table_data = await process_text(text)
        result.update(table_data)
        
        # Cache result
        cache_id = str(uuid.uuid4())
        result_cache[cache_id] = result
        
        return {"cache_id": cache_id, "result": result}
    
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")
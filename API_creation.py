from fastapi import FastAPI, UploadFile, File, HTTPException
from extracter_logic import extract_invoice_data, extract_simple_table_data
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import uuid
from pdfminer.high_level import extract_text

app = FastAPI()

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for results
result_cache = {}

@app.post("/extract-invoice")
async def extract_invoice(file: UploadFile = File(...)):
    try:
        # Save uploaded file to temp location
        file_ext = file.filename.split(".")[-1]
        temp_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.{file_ext}"
        
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text from PDF
        text = extract_text(temp_path, page_numbers=[0])
        
        # Process invoice data
        result = extract_invoice_data(temp_path)
        
        # Add table data to the result
        table_data = extract_simple_table_data(text)
        result.update(table_data)
        
        # Cache result
        cache_id = str(uuid.uuid4())
        result_cache[cache_id] = result
        
        return {"cache_id": cache_id, "result": result}
    
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")
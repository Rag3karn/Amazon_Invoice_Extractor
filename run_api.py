#!/usr/bin/env python3
"""
Script to run the FastAPI server
"""
import uvicorn
import sys
import os

def main():
    """Run the FastAPI server"""
    print("🚀 Starting Amazon Invoice Extractor API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("🔄 Health Check: http://localhost:8000/health")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "extract_invoice_api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
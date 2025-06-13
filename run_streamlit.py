#!/usr/bin/env python3
"""
Script to run the Streamlit frontend
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    print("🎨 Starting Amazon Invoice Extractor Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("🌐 Alternative access: http://127.0.0.1:8501")
    print("\n" + "="*50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
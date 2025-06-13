import streamlit as st
import requests
import time
import os
from typing import List
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="InvoiceBlaze",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def process_invoices(files):
    """Process multiple invoice files"""
    files_data = []
    for file in files:
        files_data.append(("files", (file.name, file.getvalue(), "application/pdf")))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/extract-multiple-invoices",
            files=files_data,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def generate_excel(results):
    """Generate Excel file from results"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-excel",
            json={"results": results},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Excel Generation Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def download_excel():
    """Download the generated Excel file"""
    try:
        response = requests.get(f"{API_BASE_URL}/download-excel", timeout=30)
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 404:
            st.error("No Excel file available. Please process invoices and generate Excel first.")
            return None
        else:
            st.error(f"Download Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def main():
    # Header
    st.title("📄 Amazon Invoice Extractor")
    st.markdown("---")
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API Server is not running! Please start the FastAPI server first.")
        st.code("python extract_invoice_api.py")
        st.stop()
    
    st.success("✅ API Server is running")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload** multiple Amazon invoice PDF files
        2. **Process** the invoices to extract data
        3. **Download** the Excel file with extracted data
        
        **Note:** The Excel file will be created on first use and subsequent data will be appended to the same file.
        """)
        
        st.header("📊 Features")
        st.markdown("""
        - Extract invoice details
        - Process multiple files at once
        - Generate Excel reports
        - Append to existing data
        - Real-time progress tracking
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔄 Process Invoices")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose Amazon invoice PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Select one or more Amazon invoice PDF files to process"
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected")
            
            # Display file names
            with st.expander("View selected files"):
                for i, file in enumerate(uploaded_files, 1):
                    st.write(f"{i}. {file.name}")
        
        # Process button
        if st.button("🚀 Process Invoices", type="primary", disabled=not uploaded_files):
            if uploaded_files:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process files
                status_text.text("📤 Uploading files and processing...")
                progress_bar.progress(25)
                
                result = process_invoices(uploaded_files)
                progress_bar.progress(75)
                
                if result:
                    status_text.text("✅ Processing completed!")
                    progress_bar.progress(100)
                    
                    # Store results in session state
                    st.session_state.processing_results = result
                    
                    # Display results summary
                    st.success(f"🎉 Processing completed!")
                    
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    with col_stats1:
                        st.metric("Total Files", result['total_processed'])
                    with col_stats2:
                        st.metric("Successful", result['successful'])
                    with col_stats3:
                        st.metric("Failed", result['failed'])
                    
                    # Show detailed results
                    with st.expander("📋 View Detailed Results"):
                        for i, res in enumerate(result['results'], 1):
                            if res.get('status') == 'success':
                                st.success(f"✅ {i}. {res.get('filename', 'Unknown')} - Success")
                                with st.container():
                                    col_detail1, col_detail2 = st.columns(2)
                                    with col_detail1:
                                        st.write(f"**Order Number:** {res.get('order_number', 'N/A')}")
                                        st.write(f"**Invoice Number:** {res.get('invoice_number', 'N/A')}")
                                        st.write(f"**Order Date:** {res.get('order_date', 'N/A')}")
                                    with col_detail2:
                                        st.write(f"**Total Amount:** {res.get('total_amount', 'N/A')}")
                                        st.write(f"**Seller:** {res.get('seller_name', 'N/A')}")
                                        st.write(f"**Place of Supply:** {res.get('place_of_supply', 'N/A')}")
                            else:
                                st.error(f"❌ {i}. {res.get('filename', 'Unknown')} - Failed")
                                if 'error' in res:
                                    st.write(f"Error: {res['error']}")
                    
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                else:
                    progress_bar.empty()
                    status_text.empty()
    
    with col2:
        st.header("📥 Download Excel")
        
        # Generate Excel button
        if st.button("📊 Generate Excel File", type="secondary"):
            if 'processing_results' in st.session_state:
                with st.spinner("Generating Excel file..."):
                    excel_result = generate_excel(st.session_state.processing_results['results'])
                    
                    if excel_result:
                        st.success("✅ Excel file generated successfully!")
                        st.info(f"📈 {excel_result['records_added']} records added to Excel file")
                        st.session_state.excel_ready = True
                        st.session_state.excel_filename = excel_result['filename']
                    else:
                        st.error("❌ Failed to generate Excel file")
            else:
                st.warning("⚠️ Please process some invoices first!")
        
        # Download Excel button
        if st.button("⬇️ Download Excel File", type="primary"):
            with st.spinner("Preparing download..."):
                excel_content = download_excel()
                
                if excel_content:
                    filename = st.session_state.get('excel_filename', 'amazon_invoices.xlsx')
                    st.download_button(
                        label=f"💾 Download {filename}",
                        data=excel_content,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_button"
                    )
                    st.success("✅ Excel file ready for download!")
                else:
                    st.error("❌ No Excel file available. Please process invoices and generate Excel first.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Amazon Invoice Extractor v1.0 | Built with Streamlit & FastAPI</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
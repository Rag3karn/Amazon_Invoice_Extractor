# Amazon Invoice Extractor

A powerful tool to extract data from Amazon invoice PDFs and generate Excel reports with a user-friendly Streamlit interface.

## 🚀 Features

- **PDF Data Extraction**: Extract key information from Amazon invoice PDFs
- **Batch Processing**: Process multiple invoices simultaneously
- **Excel Generation**: Create and append data to Excel files
- **Web Interface**: User-friendly Streamlit frontend
- **REST API**: FastAPI backend with comprehensive endpoints
- **Progress Tracking**: Real-time processing updates
- **Error Handling**: Robust error handling and validation

## 📋 Extracted Data Fields

- Order Number & Date
- Invoice Number & Details
- GST Registration Information
- Seller Details & Address
- Billing & Shipping Addresses
- Product Descriptions & Pricing
- Total Amounts
- And more...

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Amazon_Invoice_Extractor.git
   cd Amazon_Invoice_Extractor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Method 1: Using the Web Interface (Recommended)

1. **Start the API server**
   ```bash
   python run_api.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   python run_streamlit.py
   ```
   The web interface will be available at `http://localhost:8501`

3. **Use the web interface**
   - Upload multiple Amazon invoice PDF files
   - Click "Process Invoices" to extract data
   - Generate and download Excel file

### Method 2: Using API Endpoints Directly

1. **Start the API server**
   ```bash
   python run_api.py
   ```

2. **API Endpoints**
   - `POST /extract-multiple-invoices` - Process multiple PDF files
   - `POST /generate-excel` - Generate Excel from processed data
   - `GET /download-excel` - Download the generated Excel file
   - `GET /health` - Health check

3. **API Documentation**
   Visit `http://localhost:8000/docs` for interactive API documentation

## 📁 Project Structure

```
Amazon_Invoice_Extractor/
├── streamlit_app.py          # Streamlit frontend
├── extract_invoice_api.py    # FastAPI backend
├── excel_download_api.py     # Excel generation endpoints
├── excel_generator.py       # Excel file handling logic
├── extracter_logic.py       # PDF data extraction logic
├── run_api.py               # API server launcher
├── run_streamlit.py         # Frontend launcher
├── requirements.txt         # Python dependencies
├── Data/                    # Sample invoice PDFs
│   ├── invoice_1.pdf
│   ├── invoice_2.pdf
│   ├── invoice_3.pdf
│   └── invoice_4.pdf
└── README.md
```

## 🔧 Configuration

- **API Server**: Runs on `http://localhost:8000`
- **Streamlit Frontend**: Runs on `http://localhost:8501`
- **File Limits**: Maximum 10 PDF files per batch
- **Rate Limiting**: 10 requests per minute for single file, 5 for batch

## 📊 Excel Output

The generated Excel file (`amazon_invoices.xlsx`) contains:
- All extracted invoice data in structured columns
- Automatic appending of new data to existing file
- Proper formatting and data validation

## 🛡️ Error Handling

- File type validation (PDF only)
- Size and quantity limits
- Comprehensive error messages
- Graceful failure handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

1. **API not starting**: Check if port 8000 is available
2. **Streamlit not connecting**: Ensure API server is running first
3. **PDF processing errors**: Verify PDF files are valid Amazon invoices
4. **Excel generation fails**: Check file permissions in the project directory

### Getting Help

- Check the API documentation at `http://localhost:8000/docs`
- Review error messages in the Streamlit interface
- Ensure all dependencies are installed correctly

## 🔮 Future Enhancements

- Support for other invoice formats
- Database integration
- Advanced filtering and search
- Email integration
- Automated scheduling
- Enhanced data validation
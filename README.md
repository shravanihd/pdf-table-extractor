# 📄 PDF Table Extractor

A Python project to extract **text and tables** from PDFs.  
Supports scanned PDFs (OCR), digital PDFs, and batch extraction from zip archives.

---

## ✨ Features
- 🔹 Extract **digital text** with PyMuPDF
- 🔹 Extract **scanned text** with Tesseract OCR
- 🔹 Extract **tables** with Camelot & pdfplumber
- 🔹 Batch process multiple PDFs from a `.zip` archive
- 🔹 Save results as **CSV + JSON**

---

## 🚀 Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/shravanihd/pdf-table-extractor.git
cd pdf-table-extractor
pip install -r requirements.txt

Usage
Process a Single PDF
from src.extractor import process_pdf

results = process_pdf("sample.pdf", output_prefix="outputs/sample")
print(results)

Process a Zip of PDFs
from src.extractor import process_zip

process_zip("documents.zip", output_dir="outputs")

https://colab.research.google.com/drive/1TD-3cZkwUqd1qEGL3UtfI2EfBfJh8zUc?usp=sharing
MIT License – free to use and modify

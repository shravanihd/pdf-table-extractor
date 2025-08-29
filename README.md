This project extracts text and tables from PDFs using PyMuPDF, Camelot, pdfplumber, and Tesseract OCR.
It works on both digital and scanned PDFs.

🛠️ Features

Extracts text from PDFs (OCR fallback for scanned)

Extracts tables with Camelot (primary) and pdfplumber (fallback)

Saves outputs in CSV + JSON

Supports batch processing of PDFs inside ZIP files

📦 Installation
!apt-get install -y tesseract-ocr poppler-utils ghostscript
!pip install pymupdf camelot-py[cv] pdf2image pandas pdfplumber tabula-py requests pytesseract

⚙️ Usage
from extractor import process_pdf, process_zip

# Single PDF
process_pdf("document.pdf", output_prefix="results/output")

# ZIP with multiple PDFs
process_zip("archive.zip", output_dir="outputs")


Outputs:

<pdf_name>_text.txt → Extracted text

<pdf_name>_camelot_table.csv / .json → Tables (Camelot)

<pdf_name>_plumber_table.csv / .json → Tables (pdfplumber)

🔹 Project 2: LLM-Powered PDF Analysis Pipeline
🚀 Overview

This version extends the basic extractor with AI-powered analysis using OpenAI GPT models.
It automatically generates summaries & structured insights in addition to CSV/JSON outputs.

🛠️ Features

Everything in Project 1 ✅

Detects table titles + page numbers

Generates AI summaries of the document

Extracts structured insights in JSON format with LLM

Saves CSV, JSON, and TXT outputs

📦 Installation
!apt-get install -y tesseract-ocr poppler-utils ghostscript
!pip install pymupdf camelot-py[cv] pdf2image pandas pdfplumber tabula-py requests pytesseract openai

⚙️ Usage
from extractor_ai import process_zip

# Process a ZIP archive of PDFs
process_zip("archive.zip", output_dir="processed_pdfs")


Outputs per PDF:

<pdf_name>_table_titles.csv → Tables + Titles + Page Numbers

<pdf_name>_table_titles.json → Same in JSON

<pdf_name>_ai_summary.txt → LLM-generated summary

<pdf_name>_ai_insights.txt → Structured insights (JSON-like)

🧠 LLM Integration

Set your OpenAI API key:

import openai
openai.api_key = "YOUR_API_KEY"


Models used:

gpt-4o-mini (fast, efficient)

gpt-4o (detailed insights, heavier)

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import camelot
import pandas as pd
import pdfplumber
import zipfile
import os
import json

def extract_text(pdf_path, ocr=False):
    """Extract text from PDF (OCR if needed)."""
    text = ""
    if ocr:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img)
    else:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    return text.strip()

def extract_tables(pdf_path, output_prefix="output"):
    """Extract tables using Camelot & pdfplumber, save as CSV + JSON."""
    tables_data = []

    # Try Camelot first
    try:
        camelot_tables = camelot.read_pdf(pdf_path, pages="all")
        for i, table in enumerate(camelot_tables):
            df = table.df
            csv_path = f"{output_prefix}_camelot_table{i+1}.csv"
            json_path = f"{output_prefix}_camelot_table{i+1}.json"
            df.to_csv(csv_path, index=False)
            df.to_json(json_path, orient="records")
            tables_data.append({"csv": csv_path, "json": json_path})
    except Exception as e:
        print("Camelot failed:", e)

    # Try pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                for table_num, table in enumerate(page.extract_tables()):
                    df = pd.DataFrame(table[1:], columns=table[0])
                    csv_path = f"{output_prefix}_plumber_p{page_num+1}_t{table_num+1}.csv"
                    json_path = f"{output_prefix}_plumber_p{page_num+1}_t{table_num+1}.json"
                    df.to_csv(csv_path, index=False)
                    df.to_json(json_path, orient="records")
                    tables_data.append({"csv": csv_path, "json": json_path})
    except Exception as e:
        print("pdfplumber failed:", e)

    return tables_data

def process_pdf(pdf_path, output_prefix="output"):
    """Process single PDF → extract text + tables."""
    text = extract_text(pdf_path)
    tables = extract_tables(pdf_path, output_prefix=output_prefix)

    result = {
        "pdf": pdf_path,
        "text_file": f"{output_prefix}_text.txt",
        "tables": tables
    }

    with open(result["text_file"], "w", encoding="utf-8") as f:
        f.write(text)

    return result

def process_zip(zip_path, output_dir="outputs"):
    """Process a zip file containing PDFs."""
    os.makedirs(output_dir, exist_ok=True)
    results = []

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    for file in os.listdir(output_dir):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(output_dir, file)
            output_prefix = os.path.join(output_dir, file.replace(".pdf", ""))
            results.append(process_pdf(pdf_path, output_prefix))

    return results

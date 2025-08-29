

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import camelot
import pandas as pd
import pdfplumber
import zipfile
import os
import json
import openai   # LLM API
import glob
import re # Import re for find_table_titles


openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Functions from Cell 1 (adapted) ---
def extract_text_pymupdf(pdf_path):
    """Extract text from digital PDF using PyMuPDF."""
    text_per_page = {}
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_per_page[page_num + 1] = page.get_text("text")
        return text_per_page
    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] PyMuPDF text extraction error: {e}")
        return {}

def extract_text_ocr(pdf_path):
    """Extract text from scanned PDF using OCR."""
    text_per_page = {}
    try:
        images = convert_from_path(pdf_path)
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            text_per_page[i + 1] = text
    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] OCR text extraction error: {e}")
    return text_per_page

def extract_tables_camelot(pdf_path):
    """Extract tables using Camelot."""
    tables_info = []
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
        for t in tables:
            tables_info.append({
                "page": t.page,
                "data": t.df.values.tolist()
            })
        return tables_info
    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] Camelot table extraction error: {e}")
        return []

def extract_tables_pdfplumber(pdf_path):
    """Extract tables using pdfplumber."""
    tables_info = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables()
                    for tbl in tables:
                        tables_info.append({
                            "page": i + 1,
                            "data": tbl
                        })
                except Exception as e:
                    print(f"[{os.path.basename(pdf_path)}] Pdfplumber table extraction error on page {i+1}: {e}")
        return tables_info
    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] Pdfplumber file error: {e}")
        return []

def find_table_titles(page_text, table_data):
    """Detect Table Titles based on keywords."""
    keywords = [
        "Table", "Schedule", "Statement", "Summary",
        "Balance Sheet", "Profit", "Loss", "Cash Flow",
        "Assets", "Liabilities", "Equity",
        "APPENDIX", "ANNEXURE"
    ]
    for line in page_text.split("\n"):
        if any(kw.lower() in line.lower() for kw in keywords):
            return line.strip()
    return "Unknown"

def analyze_with_llm(text, prompt="Summarize this PDF"):
    """Send extracted text to OpenAI LLM for analysis."""
    if not openai.api_key:
        return "LLM analysis skipped: OPENAI_API_KEY not set."
    try:
       
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a helpful PDF data assistant."},
                {"role": "user", "content": f"{prompt}:\n\n{text}"}
            ],
            max_tokens=1000 
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM request failed: {e}"

def process_single_pdf_for_titles_and_llm(pdf_path, output_prefix="output"):
    """Process a single PDF to extract table titles/page numbers and perform LLM analysis."""
    results = {}
    table_title_results = []

    # Ensure output directory exists
    output_dir = os.path.dirname(output_prefix)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Step 1: Extract text (digital first, then OCR)
    text_pages = extract_text_pymupdf(pdf_path)
    full_text = "\n".join(text_pages.values()) # Combine text from all pages for LLM
    if not full_text.strip(): # If no digital text, try OCR
        print(f"[{os.path.basename(pdf_path)}] No digital text found. Switching to OCR...")
        text_pages = extract_text_ocr(pdf_path)
        full_text = "\n".join(text_pages.values())

    # Step 2: Extract tables (Camelot first, then pdfplumber)
    tables = extract_tables_camelot(pdf_path)
    if not tables:
        print(f"[{os.path.basename(pdf_path)}] No tables found with Camelot. Trying pdfplumber...")
        tables = extract_tables_pdfplumber(pdf_path)

    # Step 3: Match tables to titles and collect results
    if tables:
        for tbl in tables:
            page_num = tbl["page"]
            page_text = text_pages.get(page_num, "")
            title = find_table_titles(page_text, tbl["data"])
            table_title_results.append({
                "Table Title": title,
                "Page Number": page_num,
                "Table Data (first few rows)": tbl["data"][:3] # Include a snippet of table data
            })

        # Save table title/page number results for this PDF
        if table_title_results:
            df = pd.DataFrame(table_title_results)
            csv_file = f"{output_prefix}_table_titles.csv"
            json_file = f"{output_prefix}_table_titles.json"
            df.to_csv(csv_file, index=False)
            with open(json_file, "w") as f:
                json.dump(table_title_results, f, indent=4)
            results["table_titles_csv"] = csv_file
            results["table_titles_json"] = json_file
            print(f"[{os.path.basename(pdf_path)}] Saved table titles to {csv_file} and {json_file}")
    else:
        print(f"[{os.path.basename(pdf_path)}] No tables found for title extraction.")


    # Step 4: Perform LLM analysis on the full text
    if full_text.strip():
        print(f"[{os.path.basename(pdf_path)}] Performing LLM analysis...")
        summary = analyze_with_llm(full_text, "Summarize this document clearly")
        insights = analyze_with_llm(full_text, "Extract key points or structured data in JSON-like format relevant to financial tables or data")

        # Save AI output for this PDF
        summary_file = f"{output_prefix}_ai_summary.txt"
        insights_file = f"{output_prefix}_ai_insights.txt"

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        with open(insights_file, "w", encoding="utf-8") as f:
            f.write(insights)

        results["ai_summary_file"] = summary_file
        results["ai_insights_file"] = insights_file
        print(f"[{os.path.basename(pdf_path)}] Saved LLM analysis to {summary_file} and {insights_file}")
    else:
        print(f"[{os.path.basename(pdf_path)}] No text extracted for LLM analysis.")


    print(f"[+] Finished processing {os.path.basename(pdf_path)}")
    return results

# --- Main Execution for Zip Archive ---
archive_path = "/content/sample-docs.zip"  # change to your zip file path
output_base_dir = "/content/processed_pdfs" # Directory to save all outputs

# Create base output directory
os.makedirs(output_base_dir, exist_ok=True)

# Directory to extract zip contents temporarily
extracted_dir = "/content/temp_extracted"
os.makedirs(extracted_dir, exist_ok=True)


processed_files_summary = {}

# Unzip the archive
if zipfile.is_zipfile(archive_path):
    print(f"[*] Extracting {archive_path} to {extracted_dir}...")
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        print("[+] Extraction complete.")

        # Process each PDF in the extracted directory
        print("\nProcessing all PDFs in the archive...")
        for root, _, files in os.walk(extracted_dir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_path = os.path.join(root, file)

                    # Define output prefix for this specific PDF within the base output directory
                    # Use the original filename (without extension) as a sub-directory name
                    file_name_without_ext = os.path.splitext(file)[0]
                    pdf_output_dir = os.path.join(output_base_dir, file_name_without_ext)
                    output_prefix = os.path.join(pdf_output_dir, file_name_without_ext) # Prefix includes the sub-directory

                    print(f"\n[*] Starting processing for {file}...")
                    processing_results = process_single_pdf_for_titles_and_llm(pdf_path, output_prefix=output_prefix)
                    processed_files_summary[file] = processing_results

        print("\n[+] Finished processing all PDFs in the zip archive.")

        # Print a final summary
        print("\n--- Processing Summary ---")
        print(json.dumps(processed_files_summary, indent=4))

    except Exception as e:
        print(f"[-] Error processing zip file {archive_path}: {e}")

else:
    print(f"[-] Error: {archive_path} is not a valid zip file.")

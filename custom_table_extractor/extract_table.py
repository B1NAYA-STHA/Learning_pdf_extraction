import pdfplumber
import json


def clean_table(table_data):

    """Remove empty rows and normalize spacing."""

    cleaned = []
    for row in table_data:
        if row and any(cell for cell in row if cell):
            cleaned_row = [' '.join(str(cell).split()) if cell else '' for cell in row]
            cleaned.append(cleaned_row)
    return cleaned



def extract_tables_from_pdf(pdf_path):

    """Extract all tables from a PDF using default settings."""

    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.find_tables()  
            for idx, table in enumerate(tables, start=1):
                cleaned = clean_table(table.extract())

                if cleaned:
                    all_tables.append({
                        "page": page_num,
                        "table_index": idx,
                        "data": cleaned
                    })

    return all_tables


def save_json(data, output_path):

    """Save data to JSON file."""

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


PDF_PATH = "learn_scraping\custom_table_extractor\\trademark_paper.pdf"
OUTPUT_JSON = "learn_scraping\custom_table_extractor\\all_tables_data.json"

tables = extract_tables_from_pdf(PDF_PATH)
save_json(tables, OUTPUT_JSON)


print(f"Extracted {len(tables)} tables")



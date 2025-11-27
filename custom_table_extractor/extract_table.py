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


def extract_tables(pdf_path):

    """Extract all tables using multiple detection strategies."""

    strategies = [
        {"name": "lines_strict", "settings": {
            "vertical_strategy": "lines_strict",
            "horizontal_strategy": "lines_strict",
            "snap_tolerance": 3,
            "join_tolerance": 3
        }},
        {"name": "lines", "settings": {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 5,
            "join_tolerance": 5
        }},
        {"name": "text", "settings": {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "text_tolerance": 3
        }},
        {"name": "explicit", "settings": {
            "vertical_strategy": "explicit",
            "horizontal_strategy": "explicit"
        }}
    ]

    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):

            for strategy in strategies:
                settings = strategy["settings"].copy()

                # Add explicit lines
                if strategy["name"] == "explicit":
                    settings["explicit_vertical_lines"] = page.vertical_edges
                    settings["explicit_horizontal_lines"] = page.horizontal_edges

                tables = page.find_tables(table_settings=settings)

                if tables:
                    for idx, table in enumerate(tables, start=1):
                        extracted = table.extract()
                        cleaned = clean_table(extracted)

                        if cleaned:
                            all_tables.append({
                                "page": page_num,
                                "table_index": idx,
                                "data": cleaned
                            })

                    # stop trying other straetgies for this page
                    break

    return all_tables

def save_json(data, output_path):

    """Save to JSON file."""

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


PDF_PATH = "learn_scraping\custom_table_extractor\\trademark_paper.pdf"
OUTPUT_JSON = "learn_scraping\custom_table_extractor\\all_tables_data.json"

tables = extract_tables(PDF_PATH)
save_json(tables, OUTPUT_JSON)

print(f"Extracted {len(tables)}")

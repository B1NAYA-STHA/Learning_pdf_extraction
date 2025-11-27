import json
import re

# Input and output paths
TABLES_JSON = "custom_table_extractor\\all_tables_data.json"
ENTRIES_JSON = "custom_table_extractor\\entries_from_tables.json"

# Load table data
with open(TABLES_JSON, "r", encoding="utf-8") as f:
    tables = json.load(f)

entries = []

# Regex patterns to extract fields
patterns = {
    "serial_no": r"^(\d+)\.",
    "applicant": r"Applicant\s*:\s*(.+?)(?=\sMark Name\s*:)",
    "mark_name": r"Mark Name\s*:\s*(.+?)(?=\sMark Type\s*:)",
    "mark_type": r"Mark Type\s*:\s*([A-Z])",
    "application_no": r"Application No\.?\s*:\s*([\d\s\w]+)",
    "filing_date": r"Filing Date\s*:\s*([\d./]+)",
    "nice_class": r"NICE Class\s*:\s*(\d+)",
    "goods_services": r"Goods\s*/\s*Services\s*:\s*(.+)"
}

for table in tables:
    page = table["page"]
    for row in table["data"]:
        text = row[0]  # Each row is a single cell with full text
        entry = {"page": page}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                entry[key] = match.group(1).strip()
            else:
                entry[key] = ""  # Fill empty if not found
        entries.append(entry)

with open(ENTRIES_JSON, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(entries)} entries ")

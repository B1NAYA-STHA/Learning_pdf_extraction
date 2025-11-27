import pdfplumber
import json
import re
from collections import defaultdict

pdf_file = "learn_scraping\\new_paper.pdf"
data = []

# Define expected fields
fields = [
    "applicant", "applicant_address", "mark_name", "mark_type",
    "application_no", "filing_date", "nice_class", "goods_services"
]

# Regex to detect new numbered entry (like 1., 2., ...)
entry_number_re = re.compile(r"^\d+\.")

with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        words = page.extract_words()
        # Group words by vertical position to form lines
        lines_dict = defaultdict(list)
        for w in words:
            line_key = round(w['top'], 1)  # approximate same line
            lines_dict[line_key].append((w['x0'], w['text']))

        # Sort lines vertically
        sorted_lines = [lines_dict[k] for k in sorted(lines_dict.keys())]

        # Sort words in each line horizontally
        table_rows = []
        for line in sorted_lines:
            line_sorted = [w[1] for w in sorted(line, key=lambda x: x[0])]
            table_rows.append(" ".join(line_sorted))

        # Parse each row into structured entries
        current_entry = {}
        current_key = None

        for row in table_rows:
            row = row.strip()
            if not row:
                continue

            # Check if new numbered entry
            if entry_number_re.match(row):
                if current_entry:
                    data.append(current_entry)
                current_entry = {}
                current_key = None
                continue  # skip the number

            # Match known fields by keyword
            matched = False
            for field in fields:
                keyword = field.replace("_", " ").lower()
                if row.lower().startswith(keyword):
                    current_key = field
                    value = row[len(keyword):].strip(" :")
                    current_entry[field] = value
                    matched = True
                    break

            # If no field matched, treat as continuation or notes
            if not matched:
                if current_key:
                    current_entry[current_key] += " " + row
                else:
                    current_entry.setdefault("notes", "")
                    current_entry["notes"] += " " + row

        # Append last entry on page
        if current_entry:
            data.append(current_entry)

# Save to JSON
with open("new_trademark_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Extraction complete!")

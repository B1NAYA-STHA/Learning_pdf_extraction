import pdfplumber
import json
import re


def parse_entry(text, page_num):

    #Parse a single trademark entry into a dict.
    entry = {"page": page_num}

    # Serial number
    serial = re.match(r"^(\d+)\.\s+", text)
    if not serial:
        return None
    entry["serial_no"] = serial.group(1)

    # Regex patterns
    patterns = {
        "applicant": r"A\s*p+\s*plicant\s*:\s*(.+?)(?=Mark\s*Name|Mark\s*Type|Application\s*No|Filing\s*Date|NICE\s*Class|Goods|$)",
        "mark_name": r"Mark\s*Name\s*:\s*(.+?)(?=Mark\s*Type|Application\s*No|Filing\s*Date|NICE\s*Class|Goods|$)",
        "mark_type": r"Mark\s*Type\s*:\s*([A-Za-z]+)",
        "application_no": r"Application\s*No\.?\s*:\s*([A-Za-z0-9\/]+)",
        "filing_date": r"Filing\s*Date\s*:\s*([\d./]+)",
        "nice_class": r"NICE\s*Class\s*:\s*(\d+)",
        "goods_services": r"Goods\s*/\s*Services\s*:\s*(.+?)(?=\s*\d{1,4}\.\s+|$)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = re.sub(r"\s+", " ", match.group(1)).strip()
            entry[key] = value

    return entry


def extract_entries(pdf_path, start_page=2):

    #Extract all trademark entries from the PDF.
    entries = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        for page_num in range(start_page, total_pages):
            page = pdf.pages[page_num]
            text = page.extract_text()

            if not text:
                continue

            # Split by lines starting with "number."
            raw_entries = re.split(r'\n(?=\d+\.\s+)', text)

            for raw in raw_entries:
                raw = raw.strip()
                if not raw:
                    continue

                entry = parse_entry(raw, page_num + 1)
                if entry and len(entry) > 2:
                    entries.append(entry)

    return entries


def save_json(data, output_path):

    #Save entries to JSON.
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    PDF_FILE = "custom_table_extractor\\trademark_paper.pdf"
    OUTPUT = "custom_table_extractor\\trademark_entries.json"

    try:
        entries = extract_entries(PDF_FILE)

        if entries:
            save_json(entries, OUTPUT)
            print(f"Extracted {len(entries)} entries")
        else:
            print("No entries found.")

    except Exception as e:
        print("[ERROR]", e)

if __name__ == "__main__":
    main()

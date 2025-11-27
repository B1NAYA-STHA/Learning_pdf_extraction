import pdfplumber

def extract_table(pdf_path):
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    # clean each cell
                    cleaned_table = [
                        [cell.replace("\n", " ").strip() if cell else "" for cell in row]
                        for row in table
                    ]

    return all_tables

pdf_file = "learn_scraping\paper.pdf"
tables = extract_table(pdf_file)

print("EXTRACTED TABLES")

for t in tables:
    for row in t:
        print(row)
    print("-----------")
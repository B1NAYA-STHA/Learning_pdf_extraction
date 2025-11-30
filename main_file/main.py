import json
from extract_entries import extract_entries
from extract_images import process_images_from_entries


def main():
    PDF_FILE = "main_file/trademark_paper.pdf"
    OUTPUT_JSON = "main_file/final_trademark_output.json"
    OUTPUT_IMAGE_DIR = "main_file/extracted_images"

    print("Extracting entries...")
    entries = extract_entries(PDF_FILE, start_page=2)
    print(f"Total entries extracted: {len(entries)}")

    print("\nExtracting + matching images...")
    final_entries = process_images_from_entries(entries, PDF_FILE, OUTPUT_IMAGE_DIR, start_page=2)

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_entries, f, ensure_ascii=False, indent=2)

    total_images = sum(len(e.get("image_paths", [])) for e in final_entries)

    print(f"Total extracted images: {total_images}")

if __name__ == "__main__":
    main()

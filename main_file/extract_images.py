import pdfplumber
import base64
import io
import re
from pathlib import Path


def extract_images_from_page(page, page_num):

    #Extract all images from a single PDF page with their positions.
    images = []
    
    if hasattr(page, 'images') and page.images:
        for idx, img in enumerate(page.images):
            # Extract image bounds
            x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                
            # Crop and convert to image
            cropped = page.within_bbox((x0, y0, x1, y1))
            pil_image = cropped.to_image(resolution=150)
                
            # Convert to base64
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
            images.append({
                'image_index': idx + 1,
                'y_position': round(y0, 2),  # Vertical position for matching
                'base64': img_base64
                })
    
    return images


def extract_text_positions(page, page_num):

    #Extract serial numbers with their vertical positions.
    text = page.extract_text()
    if not text:
        return []
    
    positions = []
    words = page.extract_words()
    
    # Find serial numbers (e.g., "1.", "2.", etc.)
    for word in words:
        if re.match(r'^\d+\.$', word['text']):
            serial_no = word['text'].rstrip('.')
            positions.append({
                'serial_no': serial_no,
                'y_position': word['top'],
                'page': page_num
            })
    
    return positions


def extract_all_images_and_positions(pdf_path, start_page=2):

    #Extract images and serial number positions from all PDF pages.
    images_by_page = {}
    positions_by_page = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(start_page, len(pdf.pages)):
            page = pdf.pages[page_num]
            
            # Extract images
            page_images = extract_images_from_page(page, page_num + 1)
            if page_images:
                images_by_page[page_num + 1] = page_images
            
            # Extract serial number positions
            positions = extract_text_positions(page, page_num + 1)
            if positions:
                positions_by_page[page_num + 1] = positions
    
    return images_by_page, positions_by_page


def match_images_to_serial_numbers(entries, images_by_page, positions_by_page):
   #Match images to entries based on serial number and proximity.
    
    # Group entries by page for better matching
    entries_by_page = {}
    for entry in entries:
        if isinstance(entry, dict):
            page = entry.get('page')
            if page:
                if page not in entries_by_page:
                    entries_by_page[page] = []
                entries_by_page[page].append(entry)
    
    # Process each page
    for page, page_entries in entries_by_page.items():
        page_images = images_by_page.get(page, [])
        page_positions = positions_by_page.get(page, [])
        
        if not page_images:
            for entry in page_entries:
                entry['images'] = []
            continue
        
        # Sort entries by serial number
        page_entries.sort(key=lambda x: int(x.get('serial_no', 0)))
        
        # Build ranges for each entry
        entry_ranges = []
        for i, entry in enumerate(page_entries):
            serial_no = entry.get('serial_no')
            
            # Find position of this serial number
            serial_pos = None
            for pos in page_positions:
                if pos['serial_no'] == serial_no:
                    serial_pos = pos['y_position']
                    break
        
            if serial_pos is None:
                entry_ranges.append(None)
                continue
            
            # Find next serial position
            if i + 1 < len(page_entries):
                next_serial_no = page_entries[i + 1].get('serial_no')
                next_pos = None
                for pos in page_positions:
                    if pos['serial_no'] == next_serial_no:
                        next_pos = pos['y_position']
                        break
                
                # Use midpoint between this and next serial
                if next_pos:
                    end_pos = serial_pos + (next_pos - serial_pos) * 0.95  # 95% to avoid overlap
                else:
                    end_pos = float('inf')
            else:
                end_pos = float('inf')
            
            entry_ranges.append((serial_pos, end_pos))
        
        # Track which images have been assigned
        assigned_images = set()
        
        # Assign images to entries
        for i, entry in enumerate(page_entries):
            entry_range = entry_ranges[i]
            
            if entry_range is None:
                entry['images'] = []
                continue
            
            start_pos, end_pos = entry_range
            matched_images = []
            
            for img_idx, img in enumerate(page_images):
                if img_idx in assigned_images:
                    continue
                
                img_y = img.get('y_position')
                if img_y is None:
                    continue
                
                # Check if image falls in this entry's range
                if start_pos <= img_y < end_pos:
                    img_copy = {k: v for k, v in img.items() if k != 'y_position'}
                    matched_images.append(img_copy)
                    assigned_images.add(img_idx)
            
            # Sort by image index
            matched_images.sort(key=lambda x: x['image_index'])
            
            entry['images'] = matched_images
    
    return entries


def save_images_to_files(entries, output_dir="extracted_images"):

    #Save images and store file paths in each entry's JSON.
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        serial_no = entry.get('serial_no', 'unknown')
        page = entry.get('page', 0)
        images = entry.get('images', [])

        entry['image_paths'] = []  # Add a new key for saved file paths

        for idx, img in enumerate(images, 1):
            try:
                img_data = base64.b64decode(img['base64'])
                filename = f"serial_{serial_no}_page_{page:03d}.png"
                filepath = output_path / filename

                with open(filepath, 'wb') as f:
                    f.write(img_data)

                # Store relative path in JSON
                entry['image_paths'].append(str(filepath))

            except Exception as e:
                print(f"Error saving image for serial {serial_no}: {e}")

    return entries

def process_images_from_entries(entries, pdf_path, output_dir, start_page=2):

    images_by_page, positions_by_page = extract_all_images_and_positions(pdf_path, start_page)

    entries_with_images = match_images_to_serial_numbers(entries, images_by_page, positions_by_page)
    
    entries_with_paths = save_images_to_files(entries_with_images, output_dir)

    return entries_with_paths

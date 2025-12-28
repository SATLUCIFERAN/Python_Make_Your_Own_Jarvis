# CODE LOCATION: jarvis-assistant/skills/pdf_ocr.py (UPDATED FOR PDF HANDLING)

import pytesseract
from PIL import Image
from pathlib import Path
from pdf2image import convert_from_path 

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def image_ocr(file_path: str) -> str:    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"OCR Error: Document file not found at {file_path}")
        return ""
        
    full_text = []

    try:
        if file_path_obj.suffix.lower() == '.pdf':            
            images = convert_from_path(file_path)
            
        elif file_path_obj.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff']:
            print(f"OCR: Processing image file directly...")
            images = [Image.open(file_path_obj)]
            
        else:
            print(f"OCR Error: Unsupported file type: {file_path_obj.suffix}")
            return ""

        # Process each image (page) found

        for i, img in enumerate(images):
            print(f"OCR: Processing page {i+1}/{len(images)}...")            
            ocr_text = pytesseract.image_to_string(
                img, 
                config='--psm 3 --oem 3 -l eng' 
            )
            full_text.append(ocr_text)
            
    except pytesseract.TesseractNotFoundError:
        print("CRITICAL OCR ERROR: " \
            "Tesseract is not installed or not in PATH. Please install it.")
        return ""
    except Exception as e:
        print(f"OCR FAILED on {file_path_obj.name}: {e}")        
        if "Poppler" in str(e):
             print("\nDEPENDENCY WARNING: " \
                   "The 'pdf2image' conversion requires the Poppler utility.")
             print("Please ensure Poppler is installed and " \
                   "its 'bin' directory is added to your system's PATH.")
        return ""    
    return "\n\n".join([t.strip() for t in full_text if t.strip()])
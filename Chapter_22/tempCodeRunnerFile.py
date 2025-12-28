
# CODE LOCATION: jarvis-assistant/skills/pdf.py (Initial Draft)
import fitz # This is the main module for PyMuPDF
import re
from pathlib import Path

def extract_raw_text(file_path: str) -> str:
    """[Temporarily] Extracts raw text from all pages of a PDF."""
    full_text = []
    
    try:
        # 1. Open the PDF Document using a context manager for safety
        with fitz.open(file_path) as doc:
            # 2. Loop Through Pages
            for page_num, page in enumerate(doc):
                # 3. Extract Text - Use the plain text output
                text = page.get_text()
                full_text.append(text)
                
        return "\n".join(full_text)
    
    except fitz.FileNotFoundError:
        print(f"ERROR: File not found at {file_path}")
        return ""
    except Exception as e:
        print(f"ERROR during extraction: {e}")
        return ""
    

output = extract_raw_text("sample.pdf")
print(output)

# CODE LOCATION: jarvis-assistant/skills/pdf.py (Initial Draft)

import fitz 
import re
from pathlib import Path

def extract_raw_text(file_path: str) -> str:
    
    full_text = []    
    try:        
        with fitz.open(file_path) as doc:            
            for page_num, page in enumerate(doc):                
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





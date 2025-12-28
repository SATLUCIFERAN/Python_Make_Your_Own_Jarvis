# CODE LOCATION: jarvis-assistant/skills/pdf.py (FIXED VERSION)

import fitz 
import re
from pathlib import Path

# --- Helper Functions (FIXED) ---

def _clean_hyphens(text: str) -> str:
    """Remove hyphens from split words (handles both 'word-\nword' and 'word- word')"""
    # Handle hyphen at end of word followed by whitespace and continuation
    text = re.sub(r'([a-zA-Z])-\s+([a-zA-Z])', r'\1\2', text)
    # Handle hyphen within words (no space) - for any remaining cases
    text = re.sub(r'([a-zA-Z])-([a-zA-Z])', r'\1\2', text)
    return text


def _clean_line_breaks(text: str) -> str:
    """Replaces single newlines with a space, preserves paragraph breaks."""
    text = text.replace("\\n", " ") 
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    return re.sub(r'\n{2,}', '\n\n', text)


def _is_header_footer_content(text: str) -> bool:
    """Detect common header/footer patterns to filter them out"""
    patterns = [
        r'Document ID:\s*[\w-]+',
        r'CONFIDENTIAL.*DRAFT',
        r'^\d+$',  # Page numbers alone
        r'^Page \d+',
    ]
    return any(re.search(pattern, text.strip(), re.IGNORECASE) for pattern in patterns)


# --- The Master Function: Column-Aware Line Parsing (FIXED) ---

def pdf_parse(file_path: str, header_footer_margin_percent: float = 0.08) -> str:
    """
    The Definitive Master PDF Parser: Extracts text by lines, sorts by columns, 
    filters content, and includes final clean-up logic.
    
    FIXED ISSUES:
    - Flaw 1: Better hyphen handling for "word- word" patterns
    - Flaw 2: Line break normalization (already working)
    - Flaw 3: Pattern-based header/footer filtering + increased margin
    - Flaw 4: Removed overly aggressive small text filtering
    """
    file_path = Path(file_path) 
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return ""
        
    all_clean_text = []
    
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text_data = page.get_text("dict")
                page_height = page.rect.height
                page_width = page.rect.width
                
                # --- Step 1: Collect, Tag, and Filter Lines ---
                all_lines = []
                column_divider_x = page_width * 0.5 
                
                for block in text_data.get("blocks", []):
                    if block.get("type", 0) == 0:
                        for line in block.get("lines", []):
                            y0 = line['bbox'][1]
                            y1 = line['bbox'][3]
                            x0 = line['bbox'][0]
                            line_text = "".join([span.get('text', '') for span in line.get('spans', [])]).strip()
                            
                            # Skip empty lines
                            if not line_text:
                                continue
                            
                            # Flaw 3 Fix: Header/Footer Filtering (position-based)
                            if y0 < page_height * header_footer_margin_percent or \
                               y1 > page_height * (1 - header_footer_margin_percent):
                                continue
                            
                            # Flaw 3 Fix: Header/Footer Filtering (pattern-based)
                            if _is_header_footer_content(line_text):
                                continue

                            # REMOVED: Overly aggressive tiny block filtering
                            # Small words like "If", "We", "an" are legitimate content

                            column_index = 0 if x0 < column_divider_x else 1
                            
                            all_lines.append((column_index, line))
                
                # --- Step 2: Column-Aware Sorting (Flaw 4 Fix) ---
                all_lines.sort(key=lambda item: (item[0], item[1]['bbox'][1])) 
                
                page_content_parts = []
                paragraph_break_threshold = 20 
                
                for index, (column_index, line) in enumerate(all_lines):
                    text_parts = [span.get('text', '') for span in line.get('spans', [])]
                    text = "".join(text_parts).strip()
                    y0 = line['bbox'][1]
                    
                    if text:
                        # Don't clean hyphens yet - wait until full page text is assembled
                        separator = ' '
                        
                        if index > 0:
                            prev_column_index, prev_line_dict = all_lines[index - 1] 
                            prev_y1 = prev_line_dict['bbox'][3] 
                            
                            # Guaranteed separation on column switch
                            if column_index != prev_column_index:
                                separator = '\n\n'
                            elif (y0 - prev_y1) > paragraph_break_threshold:
                                separator = '\n\n'
                            else:
                                separator = ' '
                        
                        if page_content_parts:
                            page_content_parts.append(separator)
                        
                        page_content_parts.append(text)
                
                # --- Step 3: Final Page Cleaning ---
                raw_page_content = "".join(page_content_parts).strip()
                
                # Apply hyphen cleaning BEFORE line break cleaning
                dehyphenated = _clean_hyphens(raw_page_content)
                final_page_content = _clean_line_breaks(dehyphenated)
                
                all_clean_text.append(final_page_content)
                
    except Exception as e:
        print(f"Critical Error during PDF reading: {e}")
        return ""

    # Final Polish
    raw_content = "\n\n".join(all_clean_text)
    clean_3 = re.sub(r'[ \t]+', ' ', raw_content) 
    final_clean = re.sub(r'\n{3,}', '\n\n', clean_3).strip() 
    
    return final_clean


# --- Test Harness ---

def jarvis_read_document_test(pdf_path: str):
    """Standalone test function for the reader to confirm the skill works."""
    clean_text = pdf_parse(pdf_path)
    
    if not clean_text:
        print("Jarvis found an empty or unreadable file. Test failed.")
        return
        
    print("\n" + "="*70)
    print("JARVIS PDF PARSING SUCCESS!")
    print("="*70)
    print(f"**Document Title: {fitz.open(pdf_path).metadata.get('title', 'Unknown')}**")
    print("---")
    print(f"**Cleaned Gist (Full Output):**")
    print(clean_text)
    print("---")
    
    if len(clean_text) > 100:
        print("\n*Jarvis Whispers:* 'Good Heavens, it's so **clean**! I can actually *read* this without getting a digital migraine. My NLP brain is going to love it.'")


if __name__ == "__main__":
    test_file_path = Path(__file__).parent / "data" / "sample.pdf"
    
    if not test_file_path.parent.exists():
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if test_file_path.exists():
        jarvis_read_document_test(str(test_file_path))
    else:
        print("\n\n*** TEST FAILED: Please create a folder named 'data' in your project root and place a PDF file named 'sample.pdf' inside it to run this module. ***")
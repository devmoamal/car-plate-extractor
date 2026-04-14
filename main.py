import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import easyocr
import os
import re

# Initialize EasyOCR Reader
# This will download models on first run
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader

def get_plate_numbers(image_path):
    """
    Returns a list of tuples containing (text, confidence, bounding_box)
    with advanced filtering to remove non-plate text like 'MOTOR' or 'TESLA'.
    """
    reader = get_reader()
    results = reader.readtext(image_path)
    
    # Advanced Plate Pattern:
    # 1. Length 4-10
    # 2. MUST contain at least one Digit (common in almost all world plates)
    # 3. No common car branding words
    plate_pattern = re.compile(r'^(?=.*[0-9])[A-Z0-9\s-]{4,10}$')
    blacklist = {"MOTOR", "TESLA", "DUAL", "TURBO", "HYBRID", "DIESEL", "4WD", "AWD"}
    
    found_plates = []
    
    for (bbox, text, prob) in results:
        clean_text = text.strip().upper()
        
        # Remove spaces for pattern matching but keep for display
        match_text = clean_text.replace(" ", "")
        
        if (plate_pattern.match(match_text) or plate_pattern.match(clean_text)) \
           and clean_text not in blacklist \
           and prob > 0.4:
            found_plates.append((clean_text, prob, bbox))
            
    # Sort by confidence: highest first
    found_plates.sort(key=lambda x: x[1], reverse=True)
    return found_plates

if __name__ == "__main__":
    # Internal dev-only testing without prints
    pass
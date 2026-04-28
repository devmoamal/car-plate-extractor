import easyocr
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
    """Returns a list of detected plate number strings."""
    reader = get_reader()
    results = reader.readtext(image_path)
    
    plate_pattern = re.compile(r'^(?=.*[0-9])[A-Z0-9\s-]{4,10}$')
    plates = []
    
    for (_, text, prob) in results:
        clean = text.strip().upper()
        if plate_pattern.match(clean.replace(" ", "")) and prob > 0.4:
            plates.append(clean)
    
    return plates
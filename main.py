import easyocr
import re

def get_plate_numbers(image_path):
    # تعريف المكتبة EasyOCR
    reader = easyocr.Reader(['en'])

    # قرائة الصورة من المسار وتحويلها الى نواتج مصفوفة
    results = reader.readtext(image_path)

    # يأخذ فقط النواتج المقاربة للوحات السيارات
    plate_pattern = re.compile(r'^(?=.*[0-9])[A-Z0-9\s-]{4,10}$')
    plates = []
    
    for (_, text, prob) in results:
        # تحويل جميع النواتج الى احرف كبيرة
        clean = text.strip().upper()
        # اخذ النواتج القريبة من اللوحات باستخدام palte_pattern
        if plate_pattern.match(clean.replace(" ", "")) and prob > 0.4:
            # اضافة النواتج القريبة الى مصفوفة
            plates.append(clean)
    
    # ارجاع المصفوفة
    return plates
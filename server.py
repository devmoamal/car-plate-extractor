import os
import tempfile
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

import main

# --- App ---
app = FastAPI(
    title="AutoPlate Pro API",
    description="AI-powered license plate extraction from images",
    version="1.0.0",
)


# --- Models ---
class PlateResult(BaseModel):
    text: str
    confidence: float
    bbox: list


class ExtractResponse(BaseModel):
    plates: list[PlateResult]
    total: int


# --- Routes ---
@app.post("/api/extract", response_model=ExtractResponse)
async def extract_plates(image: UploadFile = File(...)):
    """
    Upload an image and extract license plate numbers using EasyOCR.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {image.content_type}. Use JPEG, PNG, or WebP.",
        )

    # Save to temp file for EasyOCR processing
    suffix = os.path.splitext(image.filename or "upload.png")[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        shutil.copyfileobj(image.file, tmp)
        tmp.close()

        results = main.get_plate_numbers(tmp.name)

        plates = [
            PlateResult(
                text=text,
                confidence=round(prob, 4),
                bbox=[[float(c) for c in pt] for pt in bbox],
            )
            for text, prob, bbox in results
        ]

        return ExtractResponse(plates=plates, total=len(plates))
    finally:
        os.unlink(tmp.name)

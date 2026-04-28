import os
import tempfile
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException

import main

app = FastAPI(title="AutoPlate Pro API")


@app.post("/api/extract")
async def extract_plates(image: UploadFile = File(...)):
    """Upload an image and extract license plate numbers."""
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {image.content_type}. Use JPEG, PNG, or WebP.",
        )

    suffix = os.path.splitext(image.filename or "upload.png")[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        shutil.copyfileobj(image.file, tmp)
        tmp.close()
        plates = main.get_plate_numbers(tmp.name)
        return {"plates": plates, "total": len(plates)}
    finally:
        os.unlink(tmp.name)

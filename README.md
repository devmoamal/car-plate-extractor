# Car Plate Extractor

AI-powered web application that extracts and identifies license plate numbers from vehicle images using EasyOCR.

## 📦 Getting Started

### Backend (FastAPI)

```bash
pip3 install -r requirements.txt
python3 -m uvicorn server:app --reload
```

Runs on `http://localhost:8000`

### Frontend (React + Vite)

```bash
cd ui
npm install
npm run dev
```

Runs on `http://localhost:5173`

## 🛠️ Technical Stack

- **Python 3.10+**
- **FastAPI** — REST API server
- **EasyOCR** — PyTorch-based OCR engine
- **React** — Frontend UI
- **Vite** — Build tool
- **Tailwind CSS v4** — Styling

## 📁 Project Structure

```
├── main.py            # Core OCR logic (plate extraction)
├── server.py          # FastAPI server
├── requirements.txt   # Python dependencies
├── plates/            # Sample plate images
└── ui/                # React frontend
    ├── src/
    │   ├── App.jsx    # Main UI component
    │   └── index.css  # Tailwind styles
    └── vite.config.js
```

## 🔌 API

### `POST /api/extract`

Upload an image and extract license plate numbers.

**Request:** `multipart/form-data` with `image` field

**Response:**
```json
{
  "plates": [
    { "text": "ABC 1234", "confidence": 0.95, "bbox": [...] }
  ],
  "total": 1
}
```

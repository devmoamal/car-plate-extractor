# Car Plate Extractor ( GUI )

AI-powered desktop application designed to extract and identify license plate numbers from images with high precision.

## 🚀 Key Features

- **AI-Powered OCR**: Leverages `easyocr` for robust text detection and recognition across various environments.
- **Intelligent Filtering**: Advanced regex patterns and blacklist filtering (e.g., removing "TESLA", "MOTOR") ensure only valid plate numbers are identified.
- **Premium UI**: A sophisticated, dark-themed Tkinter interface with:
  - **Ultra-Focus Palette**: Midnight blue and electric sky blue aesthetics.
  - **Micro-Animations**: Custom animated rounded buttons.
  - **Responsive Preview**: Real-time image scaling with rounded corners.
- **Asynchronous Processing**: Background threading ensures the GUI remains stutter-free during heavy AI analysis.
- **Confidence Scoring**: Displays results sorted by AI confidence levels.

## 🛠️ Technical Stack

- **Python 3.10+**
- **EasyOCR** (PyTorch based)
- **Tkinter** (Standard GUI)
- **Pillow** (Image processing)

## 📦 Installation

```bash
pip install easyocr pillow
```

## 🖥️ Usage

Run the GUI version:

```bash
python3 gui.py
```

from PIL import Image

class OCREngine:
    """
    OCR Fallback Engine.
    Processes scanned or image-only PDF pages.
    """
    def __init__(self):
        self._available = False
        self._check_engine()

    def _check_engine(self):
        try:
            import pytesseract
            self._engine = "pytesseract"
            self._available = True
        except ImportError:
            self._engine = None
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def extract_text_from_image(self, image: Image.Image) -> str:
        if not self._available:
            return "[OCR unavailable: Tesseract/PaddleOCR not installed on system]"
        try:
            import pytesseract
            return pytesseract.image_to_string(image).strip()
        except Exception as e:
            return f"[OCR processing error: {e}]"

import fitz  # PyMuPDF
from PIL import Image
import io

class PageRenderer:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def render_page(self, page_num: int, dpi: int = 150) -> Image.Image:
        """
        Renders a specific page (1-indexed) to a PIL Image.
        """
        doc = fitz.open(self.file_path)
        if page_num < 1 or page_num > len(doc):
            raise ValueError(f"Invalid page number: {page_num}")
            
        page = doc[page_num - 1]
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert PyMuPDF pixmap to PIL Image
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        doc.close()
        return img

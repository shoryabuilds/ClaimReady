import io
import fitz  # PyMuPDF
from PIL import Image

class PageRenderer:
    """
    Renders high-fidelity raster images of PDF pages for side-by-side UI review.
    """
    def __init__(self, default_dpi: int = 150):
        self.default_dpi = default_dpi

    def render_page_to_image(
        self,
        file_path_or_bytes: str | bytes,
        page_number: int,
        dpi: int | None = None
    ) -> Image.Image:
        """
        Renders 1-indexed page_number to a PIL Image.
        """
        target_dpi = dpi or self.default_dpi
        zoom = target_dpi / 72.0  # 72 is standard PDF point resolution
        matrix = fitz.Matrix(zoom, zoom)

        if isinstance(file_path_or_bytes, bytes):
            doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
        else:
            doc = fitz.open(file_path_or_bytes)

        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise ValueError(f"Page {page_number} out of bounds (1-{len(doc)})")

        page = doc[page_number - 1]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img_bytes = pix.tobytes("png")
        doc.close()

        return Image.open(io.BytesIO(img_bytes))

    def render_page_to_bytes(
        self,
        file_path_or_bytes: str | bytes,
        page_number: int,
        dpi: int | None = None
    ) -> bytes:
        """
        Renders 1-indexed page_number to PNG bytes.
        """
        img = self.render_page_to_image(file_path_or_bytes, page_number, dpi)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

import fitz  # PyMuPDF
from typing import Dict, Any

class PDFReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> Dict[int, str]:
        """
        Extracts text from the PDF.
        Returns a dictionary mapping page number (1-indexed) to the extracted text.
        """
        doc = fitz.open(self.file_path)
        extracted_content = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            extracted_content[page_num + 1] = text
        doc.close()
        return extracted_content

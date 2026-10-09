import os
import fitz  # PyMuPDF
from pydantic import BaseModel, Field

class PageContent(BaseModel):
    page_number: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Extracted plain text")
    char_count: int = 0
    is_scanned: bool = False
    image_count: int = 0

class ParsedDocument(BaseModel):
    doc_name: str
    file_path: str | None = None
    page_count: int
    pages: list[PageContent]
    is_encrypted: bool = False
    is_corrupted: bool = False
    error_message: str | None = None
    metadata: dict = Field(default_factory=dict)

    def get_full_text(self) -> str:
        return "\n--- PAGE BREAK ---\n".join(
            f"[Page {p.page_number}]\n{p.text}" for p in self.pages
        )

    def get_page_text(self, page_number: int) -> str:
        for p in self.pages:
            if p.page_number == page_number:
                return p.text
        return ""

class PDFReader:
    """
    Robust PyMuPDF reader extracting embedded text, metadata, and page counts.
    Detects scanned pages where embedded text is minimal or absent.
    """
    def __init__(self, scanned_char_threshold: int = 40):
        self.scanned_char_threshold = scanned_char_threshold

    def read_file(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            return ParsedDocument(
                doc_name=os.path.basename(file_path),
                file_path=file_path,
                page_count=0,
                pages=[],
                is_corrupted=True,
                error_message=f"File not found: {file_path}"
            )
        try:
            doc = fitz.open(file_path)
            return self._parse_fitz_doc(doc, os.path.basename(file_path), file_path)
        except Exception as e:
            return ParsedDocument(
                doc_name=os.path.basename(file_path),
                file_path=file_path,
                page_count=0,
                pages=[],
                is_corrupted=True,
                error_message=str(e)
            )

    def read_bytes(self, data: bytes, doc_name: str) -> ParsedDocument:
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            return self._parse_fitz_doc(doc, doc_name, None)
        except Exception as e:
            return ParsedDocument(
                doc_name=doc_name,
                file_path=None,
                page_count=0,
                pages=[],
                is_corrupted=True,
                error_message=str(e)
            )

    def _parse_fitz_doc(self, doc: fitz.Document, doc_name: str, file_path: str | None) -> ParsedDocument:
        if doc.is_encrypted:
            return ParsedDocument(
                doc_name=doc_name,
                file_path=file_path,
                page_count=0,
                pages=[],
                is_encrypted=True,
                error_message="Document is password protected / encrypted."
            )

        page_count = len(doc)
        pages: list[PageContent] = []

        for idx, page in enumerate(doc):
            page_num = idx + 1
            text = page.get_text("text").strip()
            char_count = len(text)
            images = page.get_images()
            image_count = len(images) if images else 0
            
            # Scanned detection heuristic: very few text characters but contains images
            is_scanned = (char_count < self.scanned_char_threshold) and (image_count > 0 or char_count == 0)

            pages.append(PageContent(
                page_number=page_num,
                text=text,
                char_count=char_count,
                is_scanned=is_scanned,
                image_count=image_count
            ))

        metadata = dict(doc.metadata) if doc.metadata else {}
        doc.close()

        return ParsedDocument(
            doc_name=doc_name,
            file_path=file_path,
            page_count=page_count,
            pages=pages,
            is_encrypted=False,
            is_corrupted=False,
            metadata=metadata
        )

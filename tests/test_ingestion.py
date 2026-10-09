import os
import pytest
from ingestion.pdf_reader import PDFReader
from ingestion.page_renderer import PageRenderer

@pytest.fixture
def sample_pdf_path():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "sample_data", "synthetic_packet_01", "packet_advised_vs_performed.pdf")
    return path

def test_pdf_reader_parses_sample_packet(sample_pdf_path):
    assert os.path.exists(sample_pdf_path), f"Sample PDF not found at {sample_pdf_path}"
    reader = PDFReader()
    doc = reader.read_file(sample_pdf_path)

    assert not doc.is_corrupted
    assert not doc.is_encrypted
    assert doc.page_count == 3
    assert len(doc.pages) == 3

    # Check text content of Page 1
    p1 = doc.pages[0]
    assert p1.page_number == 1
    assert "Rahul Sharma" in p1.text
    assert "Advised Ultrasound Whole Abdomen" in p1.text
    assert not p1.is_scanned

    # Check Page 2
    p2 = doc.pages[1]
    assert "CANCELLED" in p2.text

def test_pdf_reader_handles_nonexistent_file():
    reader = PDFReader()
    doc = reader.read_file("non_existent_file.pdf")
    assert doc.is_corrupted
    assert doc.page_count == 0

def test_page_renderer_generates_image(sample_pdf_path):
    renderer = PageRenderer(default_dpi=100)
    img = renderer.render_page_to_image(sample_pdf_path, 1)
    assert img.width > 0
    assert img.height > 0

    img_bytes = renderer.render_page_to_bytes(sample_pdf_path, 1)
    assert len(img_bytes) > 1000
    assert img_bytes[:4] == b'\x89PNG'

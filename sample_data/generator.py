import fitz
import os

def create_pdf(filename, text_content):
    doc = fitz.open()
    page = doc.new_page()
    # Add text line by line
    p = fitz.Point(50, 50)
    for line in text_content.split('\n'):
        page.insert_text(p, line, fontsize=12)
        p.y += 15
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc.save(filename)
    doc.close()

def generate_packet_1():
    # Packet 1 (Advised vs. Performed)
    text = """ADMISSION NOTE
Patient: John Doe (MRN: 12345)
Date: 2023-10-01
Plan: Advised USG Abdomen. Advised ECG.

PROGRESS NOTE
Date: 2023-10-02
USG Abdomen was cancelled due to clinical improvement.
ECG was performed.
"""
    create_pdf("sample_data/packet1.pdf", text)

def generate_packet_2():
    # Packet 2 (Chronology & Ambiguous Dates)
    text = """DISCHARGE SUMMARY
Patient: Jane Smith (MRN: 67890)
Admission Date: 2023-10-05
Discharge Date: 2023-10-04  # Error: discharge before admission
Procedure Date: 04/05/26    # Ambiguous date format
"""
    create_pdf("sample_data/packet2.pdf", text)

def generate_packet_3():
    # Packet 3 (Diagnostic Evolution vs Contradiction)
    text = """ADMISSION NOTE
Patient: Alice Brown (MRN: 11111)
Provisional Diagnosis: Suspected acute appendicitis.

DISCHARGE SUMMARY
Final Diagnosis: Histopathologically confirmed gangrenous appendicitis.

NURSING NOTE
Patient admitted for right-knee pain.  # Contradiction: left-knee vs right-knee discrepancy
Wait, the bill says left-knee surgery.
"""
    create_pdf("sample_data/packet3.pdf", text)

if __name__ == "__main__":
    generate_packet_1()
    generate_packet_2()
    generate_packet_3()
    print("Synthetic PDFs generated successfully in sample_data/")

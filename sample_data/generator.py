import os
import fitz  # PyMuPDF

def create_synthetic_pdf(output_path: str, pages_content: list[dict]):
    """
    Creates a formatted synthetic PDF with headers, metadata, and body text.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = fitz.open()

    for p in pages_content:
        page = doc.new_page(width=595, height=842)  # Standard A4 size
        rect = page.rect

        # Draw clean header banner
        header_rect = fitz.Rect(36, 36, rect.width - 36, 85)
        page.draw_rect(header_rect, color=(0.1, 0.2, 0.4), fill=(0.95, 0.97, 1.0))
        page.insert_text(
            (48, 58),
            p.get("hospital_name", "METROPOLITAN MULTISPECIALTY HOSPITAL"),
            fontsize=13,
            color=(0.1, 0.2, 0.4),
            fontname="helv"
        )
        page.insert_text(
            (48, 74),
            f"Department: {p.get('department', 'General Medicine')} | Document: {p.get('doc_type', 'Medical Record')}",
            fontsize=9,
            color=(0.3, 0.3, 0.4),
            fontname="helv"
        )

        # Meta block
        meta_rect = fitz.Rect(36, 95, rect.width - 36, 145)
        page.draw_rect(meta_rect, color=(0.8, 0.8, 0.8), fill=(0.98, 0.98, 0.98))
        page.insert_text((48, 112), f"Patient Name: {p.get('patient_name', 'N/A')}", fontsize=10, fontname="helv")
        page.insert_text((48, 126), f"MRN / Patient ID: {p.get('mrn', 'N/A')}", fontsize=10, fontname="helv")
        page.insert_text((48, 140), f"Claim / Pre-Auth ID: {p.get('claim_id', 'N/A')}", fontsize=10, fontname="helv")
        
        page.insert_text((320, 112), f"Age / Gender: {p.get('age_gender', 'N/A')}", fontsize=10, fontname="helv")
        page.insert_text((320, 126), f"Date of Record: {p.get('date_of_record', 'N/A')}", fontsize=10, fontname="helv")
        page.insert_text((320, 140), f"Consultant: {p.get('physician', 'Dr. Staff MD')}", fontsize=10, fontname="helv")

        # Body text
        y = 175
        body_lines = p.get("body_lines", [])
        for line in body_lines:
            if line.startswith("### "):
                y += 6
                page.insert_text((48, y), line.replace("### ", ""), fontsize=11, color=(0.1, 0.2, 0.4), fontname="helv")
                y += 16
            elif line.startswith("- "):
                page.insert_text((60, y), line, fontsize=9.5, color=(0.15, 0.15, 0.15), fontname="helv")
                y += 14
            else:
                page.insert_text((48, y), line, fontsize=9.5, color=(0.15, 0.15, 0.15), fontname="helv")
                y += 14

        # Page Footer
        footer_text = f"Page {doc.page_count} | ClaimReady Synthetic Test Dataset | Confidential"
        page.insert_text((48, 810), footer_text, fontsize=8, color=(0.5, 0.5, 0.5), fontname="helv")

    doc.save(output_path)
    doc.close()
    return output_path

def generate_all_sample_packets(base_dir: str):
    """
    Generates synthetic packets for all cardinal edge cases.
    """
    os.makedirs(base_dir, exist_ok=True)

    # 1. Packet 1: Advised vs Performed (Missing ECG, Cancelled USG)
    p1_path = os.path.join(base_dir, "synthetic_packet_01", "packet_advised_vs_performed.pdf")
    create_synthetic_pdf(p1_path, [
        {
            "doc_type": "EMERGENCY ADMISSION RECORD",
            "department": "Emergency Medicine",
            "patient_name": "Rahul Sharma",
            "mrn": "CR-2026-9041",
            "claim_id": "CLM-84920",
            "age_gender": "42 Y / Male",
            "date_of_record": "12/08/2026",
            "physician": "Dr. K. Mehta, MD",
            "body_lines": [
                "### CHIEF COMPLAINTS & ADMISSION CLINICAL SUMMARY",
                "Patient presented with acute epigastric discomfort, nausea, and burning sensation.",
                "Vitals stable on arrival: BP 124/80 mmHg, Pulse 78 bpm, SpO2 99% on room air.",
                "Provisional Diagnosis: Acute Gastric Distress / Rule out cholelithiasis.",
                "Admission Date: 12/08/2026.",
                "",
                "### PHYSICIAN INVESTIGATION ORDERS",
                "- 1. Advised Ultrasound Whole Abdomen to rule out cholelithiasis and biliary pathology.",
                "- 2. Ordered 12-lead Electrocardiogram (ECG) stat to rule out atypical cardiac ischemia.",
                "- 3. Complete Blood Count (CBC) and Serum Amylase / Lipase.",
                "",
                "Plan: Start IV Pantoprazole 40mg, keep on light oral fluids."
            ]
        },
        {
            "doc_type": "CLINICAL PROGRESS NOTE",
            "department": "Inpatient Ward 3",
            "patient_name": "Rahul Sharma",
            "mrn": "CR-2026-9041",
            "claim_id": "CLM-84920",
            "age_gender": "42 Y / Male",
            "date_of_record": "13/08/2026",
            "physician": "Dr. K. Mehta, MD",
            "body_lines": [
                "### WARD ROUND & INVESTIGATION STATUS UPDATE",
                "Patient reports substantial symptomatic relief following IV PPI and antispasmodics.",
                "Epigastric tenderness significantly reduced. Abdomen soft, non-tender on palpation.",
                "",
                "### INVESTIGATION STATUS REVIEW",
                "- Ultrasound Abdomen advised on admission was subsequently CANCELLED due to complete clinical resolution.",
                "- 12-lead ECG was PERFORMED in emergency triage on 12/08/2026; rhythm noted as normal sinus rhythm.",
                "- Routine blood chemistry verified within normal biological limits.",
                "",
                "Decision: Transition to oral medications. Plan discharge in 48 hours."
            ]
        },
        {
            "doc_type": "FINAL DISCHARGE SUMMARY",
            "department": "General Medicine",
            "patient_name": "Rahul Sharma",
            "mrn": "CR-2026-9041",
            "claim_id": "CLM-84920",
            "age_gender": "42 Y / Male",
            "date_of_record": "15/08/2026",
            "physician": "Dr. K. Mehta, MD",
            "body_lines": [
                "### HOSPITAL COURSE & FINAL DIAGNOSIS",
                "Date of Admission: 12/08/2026 | Date of Discharge: 15/08/2026.",
                "Final Diagnosis: Acute Gastritis (fully resolved).",
                "",
                "### SUMMARY OF INVESTIGATIONS PERFORMED & ADAPTATIONS",
                "- 12-lead ECG: Performed on 12/08/2026; normal study without acute ischemic changes.",
                "- Ultrasound Whole Abdomen: Advised initially, subsequently cancelled as clinical symptoms subsided.",
                "",
                "Condition at Discharge: Stable, ambulatory, advised oral PPI for 14 days."
            ]
        }
    ])

    # Supplementary PDF for Packet 1: The Missing ECG Report
    p1_supp_path = os.path.join(base_dir, "synthetic_packet_01", "supplement_ecg_report.pdf")
    create_synthetic_pdf(p1_supp_path, [
        {
            "doc_type": "ELECTROCARDIOGRAM REPORT",
            "department": "Cardiology / Diagnostics",
            "patient_name": "Rahul Sharma",
            "mrn": "CR-2026-9041",
            "claim_id": "CLM-84920",
            "age_gender": "42 Y / Male",
            "date_of_record": "12/08/2026",
            "physician": "Dr. V. Rao, DM (Cardiology)",
            "body_lines": [
                "### 12-LEAD DIAGNOSTIC ECG REPORT",
                "Heart Rate: 76 bpm | Rhythm: Normal Sinus Rhythm | PR Interval: 142 ms | QRS: 84 ms",
                "ST-T Wave Analysis: No acute ST elevation or depression. T-waves normal throughout.",
                "Impression: Normal 12-lead ECG. No electrocardiographic evidence of acute myocardial ischemia.",
                "",
                "Verified and electronically signed by Dr. V. Rao, Consultant Cardiologist."
            ]
        }
    ])

    # 2. Packet 2: Chronology conflict & Ambiguous Date
    p2_path = os.path.join(base_dir, "synthetic_packet_02", "packet_chronology_and_ambiguous_dates.pdf")
    create_synthetic_pdf(p2_path, [
        {
            "doc_type": "ADMISSION NOTE",
            "department": "Orthopedics",
            "patient_name": "Ananya Sen",
            "mrn": "CR-2026-4412",
            "claim_id": "CLM-77192",
            "age_gender": "34 Y / Female",
            "date_of_record": "04/05/26",  # Ambiguous date convention!
            "physician": "Dr. S. Nair, MS",
            "body_lines": [
                "### INTAKE RECORD",
                "Patient admitted with acute left wrist sprain after fall.",
                "Admission Date recorded as: 04/05/26.",
                "Plan: Wrist immobilization and analgesics."
            ]
        },
        {
            "doc_type": "DISCHARGE SUMMARY",
            "department": "Orthopedics",
            "patient_name": "Ananya Sen",
            "mrn": "CR-2026-4412",
            "claim_id": "CLM-77192",
            "age_gender": "34 Y / Female",
            "date_of_record": "02/04/2026",  # Out of sequence date!
            "physician": "Dr. S. Nair, MS",
            "body_lines": [
                "### DISCHARGE SUMMARY (CHRONOLOGY CONFLICT TEST)",
                "Discharge Date recorded: 02/04/2026.",
                "Note: Chronology violation as discharge date precedes recorded admission.",
                "Condition at discharge: Stable."
            ]
        }
    ])

    # 3. Packet 3: Diagnostic Evolution vs Contradiction
    p3_path = os.path.join(base_dir, "synthetic_packet_03", "packet_diagnostic_evolution_and_conflict.pdf")
    create_synthetic_pdf(p3_path, [
        {
            "doc_type": "EMERGENCY ADMISSION NOTE",
            "department": "General Surgery",
            "patient_name": "Vikram Patel",
            "mrn": "CR-2026-1189",
            "claim_id": "CLM-33019",
            "age_gender": "29 Y / Male",
            "date_of_record": "20/09/2026",
            "physician": "Dr. R. Joshi, MS",
            "body_lines": [
                "### ADMISSION NOTE",
                "Admission Date: 20/09/2026.",
                "Right lower quadrant pain, tenderness at McBurney point.",
                "Provisional Diagnosis: Suspected acute appendicitis.",
                "Advised open/laparoscopic appendectomy."
            ]
        },
        {
            "doc_type": "DISCHARGE & OPERATIVE SUMMARY",
            "department": "General Surgery",
            "patient_name": "Vikram Patel",
            "mrn": "CR-2026-1189",
            "claim_id": "CLM-33019",
            "age_gender": "29 Y / Male",
            "date_of_record": "23/09/2026",
            "physician": "Dr. R. Joshi, MS",
            "body_lines": [
                "### DISCHARGE SUMMARY",
                "Admission Date: 20/09/2026 | Discharge Date: 23/09/2026.",
                "Procedure: Laparoscopic Appendectomy on 20/09/2026.",
                "Final Diagnosis: Acute suppurative appendicitis with localized peritonitis (Confirmed on Histopathology).",
                "",
                "### POST-OP NURSING NOTE ENTRY",
                "Note on 21/09: Dressing applied to LEFT KNEE arthroscopy port clean and dry.",
                "(Material Contradiction: Patient admitted for appendicitis; unexplained left knee entry)."
            ]
        }
    ])

    print("Synthetic test packets successfully generated.")

if __name__ == "__main__":
    generate_all_sample_packets(os.path.dirname(__file__))

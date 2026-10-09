import re
from schemas.common import (
    DocumentType, InvestigationStatus, ActionType, SeverityLevel, FindingCategory
)
from schemas.evidence import SourceEvidence
from schemas.extraction import (
    ExtractedFacts, PatientInfo, InvestigationRecord, ClinicalRecord, AttachmentReference
)
from schemas.findings import Finding
from schemas.resolution import ResolutionDraft
from extraction.base import BaseGemmaClient

class MockGemmaClient(BaseGemmaClient):
    """
    Deterministic client returning schema-validated extractions
    for synthetic packets and offline evaluation.
    """

    def extract_packet_facts(self, doc_name: str, pages_text: dict[int, str]) -> ExtractedFacts:
        full_text = " ".join(pages_text.values())

        # 1. Extract Patient Info
        patient_name = None
        mrn = None
        claim_id = None
        age = None
        gender = None
        patient_evidence = None

        for page_num, text in pages_text.items():
            name_m = re.search(r"Patient Name:\s*([A-Za-z\s]+?)(?=\s*MRN|\s*Age|\n|$)", text)
            if name_m and not patient_name:
                patient_name = name_m.group(1).strip()
                patient_evidence = SourceEvidence(
                    source_document=doc_name,
                    source_page=page_num,
                    evidence_quote=f"Patient Name: {patient_name}"
                )

            mrn_m = re.search(r"MRN\s*(?:/\s*Patient ID)?:\s*([A-Za-z0-9\-]+)", text)
            if mrn_m and not mrn:
                mrn = mrn_m.group(1).strip()

            claim_m = re.search(r"Claim\s*(?:/\s*Pre-Auth ID)?:\s*([A-Za-z0-9\-]+)", text)
            if claim_m and not claim_id:
                claim_id = claim_m.group(1).strip()

            age_gender_m = re.search(r"Age\s*/\s*Gender:\s*(\d+)\s*Y?\s*/\s*([A-Za-z]+)", text)
            if age_gender_m and not age:
                age = int(age_gender_m.group(1))
                gender = age_gender_m.group(2)

        patient = PatientInfo(
            name=patient_name or "Unknown Patient",
            patient_id=mrn,
            claim_id=claim_id,
            age=age,
            gender=gender,
            evidence=patient_evidence
        )

        # 2. Extract Clinical Record (Dates, Diagnoses)
        adm_date_raw = None
        adm_date_norm = None
        dis_date_raw = None
        dis_date_norm = None
        provisional_diag = None
        final_diag = None
        procedures = []
        clinical_evidences = []

        for page_num, text in pages_text.items():
            adm_m = re.search(r"Admission Date(?:\s*recorded as)?:\s*([0-9/\-]+)", text)
            if adm_m and not adm_date_raw:
                adm_date_raw = adm_m.group(1).strip()
                # Check ambiguous format: e.g. 04/05/26 (2-digit year or ambiguous day/month)
                if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", adm_date_raw):
                    adm_date_norm = None  # Format ambiguity flagged!
                elif re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", adm_date_raw):
                    parts = adm_date_raw.split("/")
                    adm_date_norm = f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
                clinical_evidences.append(SourceEvidence(
                    source_document=doc_name,
                    source_page=page_num,
                    evidence_quote=adm_m.group(0)
                ))

            dis_m = re.search(r"Discharge Date(?:\s*recorded)?:\s*([0-9/\-]+)", text)
            if dis_m and not dis_date_raw:
                dis_date_raw = dis_m.group(1).strip()
                if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", dis_date_raw):
                    parts = dis_date_raw.split("/")
                    dis_date_norm = f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
                clinical_evidences.append(SourceEvidence(
                    source_document=doc_name,
                    source_page=page_num,
                    evidence_quote=dis_m.group(0)
                ))

            prov_m = re.search(r"Provisional Diagnosis:\s*([^\.\n]+)", text)
            if prov_m and not provisional_diag:
                provisional_diag = prov_m.group(1).strip()

            final_m = re.search(r"Final Diagnosis:\s*([^\.\n]+)", text)
            if final_m and not final_diag:
                final_diag = final_m.group(1).strip()

            proc_m = re.search(r"Procedure:\s*([^\.\n]+)", text)
            if proc_m:
                procedures.append(proc_m.group(1).strip())

            # Detect left/right knee material mismatch if present
            knee_m = re.search(r"(Dressing applied to [A-Z\s]+port clean and dry)", text)
            if knee_m:
                procedures.append(knee_m.group(1).strip())
                clinical_evidences.append(SourceEvidence(
                    source_document=doc_name,
                    source_page=page_num,
                    evidence_quote=knee_m.group(1)
                ))

        clinical_record = ClinicalRecord(
            admission_date_raw=adm_date_raw,
            admission_date_normalized=adm_date_norm,
            discharge_date_raw=dis_date_raw,
            discharge_date_normalized=dis_date_norm,
            provisional_diagnosis=provisional_diag,
            final_diagnosis=final_diag,
            procedures=procedures,
            evidence=clinical_evidences
        )

        # 3. Extract Investigations & Invariant Statuses (Advised vs Performed vs Cancelled)
        investigations = []

        for page_num, text in pages_text.items():
            # Check USG status
            if "Ultrasound" in text or "USG" in text:
                usg_status = InvestigationStatus.UNKNOWN
                quote = ""
                if "CANCELLED" in text:
                    usg_status = InvestigationStatus.CANCELLED
                    quote = "Ultrasound Abdomen advised on admission was subsequently CANCELLED due to complete clinical resolution."
                elif "Advised Ultrasound" in text or "Advised USG" in text:
                    usg_status = InvestigationStatus.ADVISED
                    quote = "Advised Ultrasound Whole Abdomen to rule out cholelithiasis."
                
                # Check if we already have USG, update or append
                existing = next((inv for inv in investigations if "Ultrasound" in inv.name or "USG" in inv.name), None)
                if existing:
                    # Update to latest status (CANCELLED overrides earlier ADVISED)
                    if usg_status == InvestigationStatus.CANCELLED:
                        existing.status = InvestigationStatus.CANCELLED
                        existing.evidence = SourceEvidence(
                            source_document=doc_name,
                            source_page=page_num,
                            evidence_quote=quote
                        )
                elif quote:
                    investigations.append(InvestigationRecord(
                        investigation_id="INV-001",
                        name="Ultrasound Whole Abdomen",
                        status=usg_status,
                        evidence=SourceEvidence(
                            source_document=doc_name,
                            source_page=page_num,
                            evidence_quote=quote
                        )
                    ))

            # Check ECG status
            if "Electrocardiogram" in text or "ECG" in text:
                quote = ""
                ecg_status = InvestigationStatus.UNKNOWN
                if "PERFORMED" in text or "Performed on" in text:
                    ecg_status = InvestigationStatus.PERFORMED
                    quote = "12-lead ECG was PERFORMED in emergency triage on 12/08/2026; rhythm noted as normal sinus rhythm."
                elif "Ordered 12-lead" in text:
                    ecg_status = InvestigationStatus.ADVISED
                    quote = "Ordered 12-lead Electrocardiogram (ECG) stat to rule out atypical cardiac ischemia."
                
                existing = next((inv for inv in investigations if "ECG" in inv.name), None)
                if existing:
                    if ecg_status == InvestigationStatus.PERFORMED:
                        existing.status = InvestigationStatus.PERFORMED
                        existing.is_report_attached = ("Impression: Normal 12-lead ECG" in full_text)
                        existing.evidence = SourceEvidence(
                            source_document=doc_name,
                            source_page=page_num,
                            evidence_quote=quote
                        )
                elif quote:
                    is_attached = ("Impression: Normal 12-lead ECG" in full_text)
                    investigations.append(InvestigationRecord(
                        investigation_id="INV-002",
                        name="12-Lead Electrocardiogram (ECG)",
                        status=ecg_status,
                        date_raw="12/08/2026",
                        date_normalized="2026-08-12",
                        is_report_attached=is_attached,
                        evidence=SourceEvidence(
                            source_document=doc_name,
                            source_page=page_num,
                            evidence_quote=quote
                        )
                    ))

        # Check identified document types
        doc_types = {}
        for p_num, text in pages_text.items():
            if "ADMISSION" in text:
                doc_types[f"Page_{p_num}"] = DocumentType.ADMISSION_NOTE
            elif "DISCHARGE" in text:
                doc_types[f"Page_{p_num}"] = DocumentType.DISCHARGE_SUMMARY
            elif "ELECTROCARDIOGRAM REPORT" in text:
                doc_types[f"Page_{p_num}"] = DocumentType.LAB_REPORT
            else:
                doc_types[f"Page_{p_num}"] = DocumentType.PROGRESS_NOTE

        return ExtractedFacts(
            packet_id=claim_id or "PKT-DEFAULT",
            patient=patient,
            clinical_record=clinical_record,
            investigations=investigations,
            document_types=doc_types
        )

    def generate_resolution_draft(
        self,
        finding: Finding,
        patient_name: str | None,
        mrn: str | None
    ) -> ResolutionDraft:
        p_name = patient_name or "Patient"
        p_mrn = mrn or "N/A"

        if finding.category == FindingCategory.INVESTIGATION_GAP or finding.category == FindingCategory.MISSING_DOCUMENT:
            # Generate Retrieval Ticket
            return ResolutionDraft(
                draft_id=f"DRF-{finding.finding_id}",
                finding_id=finding.finding_id,
                action_type=ActionType.RETRIEVAL_TICKET,
                target_department="Cardiology / Diagnostic Records",
                subject=f"URGENT: Missing Diagnostic Report Retrieval - {p_name} ({p_mrn})",
                body=(
                    f"To: Diagnostic Records / Department Coordinator\n\n"
                    f"During pre-submission claim audit for patient {p_name} (MRN: {p_mrn}), "
                    f"the following mandatory report was identified as PERFORMED but missing from the packet:\n\n"
                    f"- Item: {finding.title}\n"
                    f"- Clinical Evidence: \"{finding.evidence[0].evidence_quote if finding.evidence else 'Documented in record'}\"\n"
                    f"- Cited Source: {finding.evidence[0].source_document} (Page {finding.evidence[0].source_page})\n\n"
                    f"Please retrieve and attach the signed diagnostic trace/report to prevent insurer rejection under Rule {finding.rule_id}."
                )
            )
        else:
            # Generate Clarification Memo
            return ResolutionDraft(
                draft_id=f"DRF-{finding.finding_id}",
                finding_id=finding.finding_id,
                action_type=ActionType.CLARIFICATION_MEMO,
                target_department="Treating Physician / Medical Records Committee",
                subject=f"CLINICAL CLARIFICATION REQUIRED: {finding.title} - {p_name} ({p_mrn})",
                body=(
                    f"Dear Doctor / Nursing Staff,\n\n"
                    f"A potential documentation discrepancy was identified during pre-submission claim verification for patient {p_name} (MRN: {p_mrn}):\n\n"
                    f"- Finding: {finding.description}\n"
                    f"- Evidence Quote: \"{finding.evidence[0].evidence_quote if finding.evidence else 'Documented'}\"\n"
                    f"- Source Reference: {finding.evidence[0].source_document} (Page {finding.evidence[0].source_page})\n\n"
                    f"Please provide an addendum or written clarification to rectify this before packet submission (Rule: {finding.rule_id}).\n\n"
                    f"Thank you,\nHospital Insurance Coordination Desk"
                )
            )

from typing import Dict, Any
from schemas.extraction import ExtractedFacts, PatientInfo, InvestigationRecord, ClinicalRecord, AttachmentReference
from schemas.common import InvestigationStatus
from schemas.evidence import SourceEvidence
from datetime import date
from .base import BaseGemmaClient

class MockGemmaClient(BaseGemmaClient):
    def extract_facts(self, extracted_text: Dict[int, str]) -> ExtractedFacts:
        text_concat = " ".join(extracted_text.values()).lower()
        
        # Simple heuristic to determine which packet this is
        if "advised usg abdomen" in text_concat:
            # Packet 1 Mock
            return ExtractedFacts(
                patient_info=PatientInfo(mrn="12345", name="John Doe"),
                investigations=[
                    InvestigationRecord(
                        name="USG Abdomen", 
                        status=InvestigationStatus.CANCELLED,
                        evidence=SourceEvidence(source_document="PROGRESS NOTE", source_page=1, evidence_quote="USG Abdomen was cancelled", confidence=0.9, is_uncertain=False)
                    ),
                    InvestigationRecord(
                        name="ECG", 
                        status=InvestigationStatus.PERFORMED,
                        evidence=SourceEvidence(source_document="PROGRESS NOTE", source_page=1, evidence_quote="ECG was performed.", confidence=0.9, is_uncertain=False)
                    )
                ]
            )
        elif "jane smith" in text_concat:
            # Packet 2 Mock
            return ExtractedFacts(
                patient_info=PatientInfo(mrn="67890", name="Jane Smith"),
                clinical_record=ClinicalRecord(
                    admission_date=date(2023, 10, 5),
                    discharge_date=date(2023, 10, 4),
                    procedure_dates=[date(2026, 5, 4)], # arbitrary parse of 04/05/26
                    evidence=SourceEvidence(source_document="DISCHARGE SUMMARY", source_page=1, evidence_quote="Admission Date: 2023-10-05\\nDischarge Date: 2023-10-04", confidence=0.9, is_uncertain=False)
                )
            )
        elif "alice brown" in text_concat:
            # Packet 3 Mock
            return ExtractedFacts(
                patient_info=PatientInfo(mrn="11111", name="Alice Brown"),
                clinical_record=ClinicalRecord(
                    provisional_diagnosis="Suspected acute appendicitis",
                    final_diagnosis="Histopathologically confirmed gangrenous appendicitis",
                    evidence=SourceEvidence(source_document="DISCHARGE SUMMARY", source_page=1, evidence_quote="Final Diagnosis: Histopathologically confirmed gangrenous appendicitis.", confidence=0.9, is_uncertain=False)
                )
            )
        else:
            # Fallback mock
            return ExtractedFacts()

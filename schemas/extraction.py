from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .common import InvestigationStatus
from .evidence import SourceEvidence

class PatientInfo(BaseModel):
    mrn: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    evidence: Optional[SourceEvidence] = None

class InvestigationRecord(BaseModel):
    name: str = Field(..., description="Name of the investigation (e.g. USG Abdomen, ECG)")
    status: InvestigationStatus = Field(..., description="Current status: ADVISED, PERFORMED, or CANCELLED")
    raw_date: Optional[str] = Field(None, description="The date as it appears in text")
    normalized_date: Optional[date] = Field(None, description="Parsed ISO date if unambiguous")
    ordering_doctor: Optional[str] = None
    evidence: Optional[SourceEvidence] = None

class ClinicalRecord(BaseModel):
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    provisional_diagnosis: Optional[str] = None
    final_diagnosis: Optional[str] = None
    procedure_dates: List[date] = Field(default_factory=list)
    evidence: Optional[SourceEvidence] = None

class AttachmentReference(BaseModel):
    reference_text: str = Field(..., description="Mention of the attachment in clinical notes")
    attachment_type: str = Field(..., description="Type of attachment (e.g. Scan, Report, Bill)")
    evidence: Optional[SourceEvidence] = None

class ExtractedFacts(BaseModel):
    patient_info: Optional[PatientInfo] = None
    clinical_record: Optional[ClinicalRecord] = None
    investigations: List[InvestigationRecord] = Field(default_factory=list)
    attachments: List[AttachmentReference] = Field(default_factory=list)

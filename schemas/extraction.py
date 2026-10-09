from pydantic import BaseModel, Field
from schemas.common import DocumentType, InvestigationStatus
from schemas.evidence import SourceEvidence

class PatientInfo(BaseModel):
    patient_id: str | None = Field(default=None, description="Patient MRN or Hospital ID")
    name: str | None = Field(default=None, description="Patient Full Name")
    age: int | None = Field(default=None, description="Patient Age")
    gender: str | None = Field(default=None, description="Patient Gender")
    claim_id: str | None = Field(default=None, description="Insurance Claim or Pre-auth ID")
    evidence: SourceEvidence | None = Field(default=None, description="Source citation for patient info")

class InvestigationRecord(BaseModel):
    investigation_id: str = Field(..., description="Unique investigation identifier (e.g. INV-001)")
    name: str = Field(..., description="Name of test or scan, e.g., USG Abdomen, ECG, CBC")
    status: InvestigationStatus = Field(
        default=InvestigationStatus.UNKNOWN,
        description="Clinical status: ADVISED, PERFORMED, CANCELLED, or UNKNOWN"
    )
    date_raw: str | None = Field(default=None, description="Raw date string from document (e.g. 12/08/26)")
    date_normalized: str | None = Field(default=None, description="ISO normalized date YYYY-MM-DD if unambiguous")
    ordering_physician: str | None = Field(default=None, description="Physician who ordered/advised test")
    is_report_attached: bool = Field(default=False, description="Whether the matching report document is present")
    evidence: SourceEvidence = Field(..., description="Evidence quote confirming the test and its status")

class ClinicalRecord(BaseModel):
    admission_date_raw: str | None = None
    admission_date_normalized: str | None = None
    discharge_date_raw: str | None = None
    discharge_date_normalized: str | None = None
    provisional_diagnosis: str | None = None
    final_diagnosis: str | None = None
    procedures: list[str] = Field(default_factory=list)
    procedure_dates_raw: list[str] = Field(default_factory=list)
    evidence: list[SourceEvidence] = Field(default_factory=list)

class AttachmentReference(BaseModel):
    attachment_name: str = Field(..., description="Name of referenced attachment or report")
    attachment_type: str = Field(default="report", description="Type of attachment")
    is_present: bool = Field(default=False, description="Whether attachment is verified in packet")
    evidence: SourceEvidence = Field(..., description="Citation where attachment is mentioned/referenced")

class ExtractedFacts(BaseModel):
    packet_id: str = Field(..., description="Packet identifier")
    patient: PatientInfo | None = None
    clinical_record: ClinicalRecord | None = None
    investigations: list[InvestigationRecord] = Field(default_factory=list)
    referenced_attachments: list[AttachmentReference] = Field(default_factory=list)
    document_types: dict[str, DocumentType] = Field(default_factory=dict)
    extraction_notes: list[str] = Field(default_factory=list)
    needs_human_verification: bool = Field(default=False)

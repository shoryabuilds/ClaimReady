from pydantic import BaseModel, Field
from datetime import datetime, timezone
from schemas.common import FindingCategory, FindingStatus, SeverityLevel
from schemas.evidence import SourceEvidence

class Finding(BaseModel):
    """
    Represents an audit discrepancy, missing record, ambiguity, or gap.
    """
    finding_id: str = Field(..., description="Unique finding ID (e.g. FND-001)")
    rule_id: str = Field(..., description="ID of the verification rule that triggered this (e.g. RULE-INV-01)")
    category: FindingCategory = Field(..., description="Category of finding")
    title: str = Field(..., description="Short explanatory title")
    description: str = Field(..., description="Detailed explanation of the issue and clinical context")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Finding severity/priority")
    status: FindingStatus = Field(default=FindingStatus.OPEN, description="Current lifecycle status")
    evidence: list[SourceEvidence] = Field(default_factory=list, description="Verifiable citations supporting finding")
    suggested_action: str = Field(..., description="Recommended human or resolution step")
    human_override_reason: str | None = Field(default=None, description="Staff justification if manually overridden")
    resolved_by_run_id: str | None = Field(default=None, description="Audit run ID that resolved this finding")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

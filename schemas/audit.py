from pydantic import BaseModel, Field
from datetime import datetime, timezone
from schemas.common import ReadinessStatus
from schemas.findings import Finding
from schemas.resolution import ResolutionDraft

class AuditRun(BaseModel):
    """
    Encapsulates a single audit evaluation iteration.
    """
    run_id: str = Field(..., description="Unique audit run ID (e.g. RUN-001)")
    packet_id: str = Field(..., description="Associated packet ID")
    run_number: int = Field(default=1, description="Iteration number (1 for initial, 2+ for re-audits)")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    readiness_status: ReadinessStatus = Field(default=ReadinessStatus.REVIEW_REQUIRED)
    readiness_explanation: str = Field(..., description="Transparent, human-readable justification for status")
    total_findings: int = 0
    open_findings: int = 0
    resolved_findings: int = 0
    overridden_findings: int = 0
    findings: list[Finding] = Field(default_factory=list)
    resolution_drafts: list[ResolutionDraft] = Field(default_factory=list)
    resolved_finding_ids: list[str] = Field(default_factory=list)
    new_finding_ids: list[str] = Field(default_factory=list)

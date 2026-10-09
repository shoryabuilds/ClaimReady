from pydantic import BaseModel, Field
from datetime import datetime, timezone
from schemas.common import ActionType

class ResolutionDraft(BaseModel):
    """
    Agentic resolution draft (Retrieval Ticket or Clarification Memo)
    grounded in findings and evidence.
    """
    draft_id: str = Field(..., description="Unique draft identifier (e.g. DRF-001)")
    finding_id: str = Field(..., description="ID of the finding this draft resolves")
    action_type: ActionType = Field(..., description="RETRIEVAL_TICKET or CLARIFICATION_MEMO")
    target_department: str = Field(..., description="Recipient department or role (e.g. Radiology, Lab, Physician)")
    subject: str = Field(..., description="Email/memo subject line")
    body: str = Field(..., description="Detailed, professional, evidence-backed communication draft")
    is_approved: bool = Field(default=False, description="True once approved by hospital staff")
    approved_by: str | None = Field(default=None, description="Username or staff identifier who approved")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

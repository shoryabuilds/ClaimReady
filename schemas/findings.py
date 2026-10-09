from pydantic import BaseModel, Field
from typing import List, Optional
from .common import SeverityLevel, FindingStatus, FindingCategory
from .evidence import SourceEvidence

class RuleFinding(BaseModel):
    id: str = Field(..., description="Unique identifier for the finding")
    rule_code: str = Field(..., description="The code of the rule that generated this finding (e.g. REQ-01)")
    category: FindingCategory
    severity: SeverityLevel
    status: FindingStatus = FindingStatus.OPEN
    description: str = Field(..., description="Human readable description of the issue")
    primary_evidence: Optional[SourceEvidence] = None
    conflicting_evidence: Optional[SourceEvidence] = None

from pydantic import BaseModel, Field
from typing import Optional

class SourceEvidence(BaseModel):
    source_document: str = Field(..., description="Name or identifier of the source document")
    source_page: int = Field(..., description="Page number where the evidence is found")
    evidence_quote: str = Field(..., description="Exact quote from the document supporting this fact")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the extraction (0.0 to 1.0)")
    is_uncertain: bool = Field(False, description="Flag indicating if the evidence is ambiguous or uncertain")

from pydantic import BaseModel, Field

class SourceEvidence(BaseModel):
    """
    Evidence Contract model: Every extracted fact and audit finding must carry
    verifiable source citations.
    """
    source_document: str = Field(..., description="Filename or identifier of the source PDF document")
    source_page: int = Field(..., ge=1, description="1-indexed page number within the source document")
    evidence_quote: str = Field(..., description="Verbatim text quote from the document supporting the fact")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score (0.0 to 1.0)")
    is_uncertain: bool = Field(default=False, description="True if text was partially illegible, ambiguous, or low-confidence")
    bounding_box: list[float] | None = Field(default=None, description="Optional bounding box coordinates [x0, y0, x1, y1]")

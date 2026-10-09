from pydantic import BaseModel, Field
from typing import List

class RetrievalTicket(BaseModel):
    ticket_id: str
    finding_id: str
    missing_document_name: str
    reason: str = Field(..., description="Why this document is needed")
    suggested_source: str = Field(..., description="Where the hospital should look for this document (e.g. Lab Dept)")

class ClarificationMemo(BaseModel):
    memo_id: str
    finding_id: str
    issue_description: str
    question_for_doctor: str = Field(..., description="Drafted question for the clinician to clarify the discrepancy")

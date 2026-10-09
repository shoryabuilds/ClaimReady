from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from .common import ReadinessStatus
from .findings import RuleFinding
from .resolution import RetrievalTicket, ClarificationMemo

class PacketReadiness(BaseModel):
    status: ReadinessStatus
    readiness_score: float = Field(..., ge=0.0, le=100.0, description="0 to 100 score based on severity of findings")
    summary: str = Field(..., description="High level summary of packet readiness")

class AuditRun(BaseModel):
    audit_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    packet_id: str
    findings: List[RuleFinding] = Field(default_factory=list)
    retrieval_tickets: List[RetrievalTicket] = Field(default_factory=list)
    clarification_memos: List[ClarificationMemo] = Field(default_factory=list)
    readiness: PacketReadiness

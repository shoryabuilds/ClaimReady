from schemas.findings import Finding
from schemas.resolution import ResolutionDraft
from extraction.base import BaseGemmaClient
from extraction.gemma_client import GemmaClient

class ResolutionDraftGenerator:
    """
    Transforms audit findings into evidence-grounded action drafts
    (Retrieval Tickets & Clarification Memos).
    """

    def __init__(self, client: BaseGemmaClient | None = None):
        self.client = client or GemmaClient()

    def generate_draft_for_finding(
        self,
        finding: Finding,
        patient_name: str | None = None,
        mrn: str | None = None
    ) -> ResolutionDraft:
        return self.client.generate_resolution_draft(finding, patient_name, mrn)

    def generate_all_drafts(
        self,
        findings: list[Finding],
        patient_name: str | None = None,
        mrn: str | None = None
    ) -> list[ResolutionDraft]:
        return [
            self.generate_draft_for_finding(f, patient_name, mrn)
            for f in findings
        ]

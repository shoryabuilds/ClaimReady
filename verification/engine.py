from schemas.extraction import ExtractedFacts
from schemas.findings import Finding
from verification.investigation_status import verify_investigation_statuses
from verification.chronology import verify_chronology_and_dates
from verification.consistency import verify_clinical_consistency
from verification.required_docs import verify_required_documents

class VerificationEngine:
    """
    Pure deterministic verification engine.
    Executes all registered rules against extracted facts without AI guessing.
    """

    def __init__(self):
        self.rules = [
            verify_required_documents,
            verify_investigation_statuses,
            verify_chronology_and_dates,
            verify_clinical_consistency,
        ]

    def verify(self, facts: ExtractedFacts) -> list[Finding]:
        findings: list[Finding] = []
        for rule in self.rules:
            res = rule(facts)
            findings.extend(res)
        return findings

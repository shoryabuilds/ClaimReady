from typing import List
from schemas.extraction import ExtractedFacts
from schemas.findings import RuleFinding
from .investigation_status import verify_investigations
from .chronology import verify_chronology

class VerificationEngine:
    def __init__(self):
        self.rules = [
            verify_investigations,
            verify_chronology
        ]

    def run_all_rules(self, facts: ExtractedFacts) -> List[RuleFinding]:
        all_findings = []
        for rule in self.rules:
            findings = rule(facts)
            all_findings.extend(findings)
        return all_findings

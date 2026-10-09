from schemas.extraction import ExtractedFacts
from schemas.findings import RuleFinding, FindingCategory, SeverityLevel
from typing import List

def verify_investigations(facts: ExtractedFacts) -> List[RuleFinding]:
    findings = []
    # If investigation was advised and NOT explicitly cancelled, it should have a report.
    # If it was cancelled, it's fine.
    # If it was performed, we need a report.
    for inv in facts.investigations:
        if inv.status == "PERFORMED" and not _has_report(inv.name, facts):
            findings.append(RuleFinding(
                id=f"inv-{inv.name}-missing",
                rule_code="INV-01",
                category=FindingCategory.MISSING_DOCUMENT,
                severity=SeverityLevel.CRITICAL,
                description=f"Investigation '{inv.name}' was PERFORMED but the report is missing.",
                primary_evidence=inv.evidence
            ))
    return findings

def _has_report(inv_name: str, facts: ExtractedFacts) -> bool:
    # Dummy check for now. In reality, check if attachment exists.
    return False

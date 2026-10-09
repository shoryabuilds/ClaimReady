from schemas.common import InvestigationStatus, FindingCategory, SeverityLevel
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding

def verify_investigation_statuses(facts: ExtractedFacts) -> list[Finding]:
    """
    Rule RULE-INV-01: Advised vs Performed Verification.
    
    CARDINAL INVARIANT:
    - If status == ADVISED or CANCELLED: Do NOT demand or flag a missing report.
    - If status == PERFORMED and is_report_attached == False: Flag HIGH severity missing report.
    - If status == UNKNOWN: Flag UNCERTAIN_EXTRACTION for human review.
    """
    findings: list[Finding] = []

    for idx, inv in enumerate(facts.investigations, start=1):
        if inv.status == InvestigationStatus.PERFORMED and not inv.is_report_attached:
            findings.append(Finding(
                finding_id=f"FND-INV-{idx:03d}",
                rule_id="RULE-INV-01",
                category=FindingCategory.INVESTIGATION_GAP,
                title=f"Missing Diagnostic Report: {inv.name}",
                description=(
                    f"Investigation '{inv.name}' is documented as PERFORMED, but no corresponding "
                    f"diagnostic report or trace was found attached in the claim packet."
                ),
                severity=SeverityLevel.HIGH,
                evidence=[inv.evidence],
                suggested_action=f"Generate retrieval ticket to obtain signed {inv.name} report."
            ))
        elif inv.status == InvestigationStatus.UNKNOWN:
            findings.append(Finding(
                finding_id=f"FND-INV-{idx:03d}",
                rule_id="RULE-INV-01",
                category=FindingCategory.UNCERTAIN_EXTRACTION,
                title=f"Uncertain Status for {inv.name}",
                description=(
                    f"Investigation '{inv.name}' was mentioned in records, but its status "
                    f"(performed vs advised vs cancelled) cannot be determined with certainty."
                ),
                severity=SeverityLevel.MEDIUM,
                evidence=[inv.evidence],
                suggested_action=f"Verify with treating ward whether {inv.name} was conducted."
            ))
        # Case A: status in (ADVISED, CANCELLED) -> Intentionally no finding generated!

    return findings

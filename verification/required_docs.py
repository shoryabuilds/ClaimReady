from schemas.common import DocumentType, FindingCategory, SeverityLevel
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding

def verify_required_documents(facts: ExtractedFacts) -> list[Finding]:
    """
    Rule RULE-REQ-01: Verifies presence of mandatory claim documents.
    """
    findings: list[Finding] = []
    present_types = set(facts.document_types.values())

    # Discharge summary is mandatory for inpatient discharge claim packets
    if DocumentType.DISCHARGE_SUMMARY not in present_types:
        findings.append(Finding(
            finding_id=f"FND-REQ-{len(findings)+1:03d}",
            rule_id="RULE-REQ-01",
            category=FindingCategory.MISSING_DOCUMENT,
            title="Missing Mandatory Document: Discharge Summary",
            description="The claim packet does not contain a verified Discharge Summary.",
            severity=SeverityLevel.HIGH,
            evidence=[],
            suggested_action="Obtain signed discharge summary from treating department."
        ))

    return findings

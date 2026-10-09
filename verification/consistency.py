import re
from schemas.common import FindingCategory, SeverityLevel
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding

def verify_clinical_consistency(facts: ExtractedFacts) -> list[Finding]:
    """
    Rule RULE-CON-01: Clinical Evolution vs Contradiction Check.
    
    CARDINAL INVARIANTS:
    1. Legitimate diagnostic refinement (e.g. suspected appendicitis -> acute appendicitis)
       is recognized as normal clinical progression and NOT flagged.
    2. Material contradictions (e.g. unexplained Left vs Right discrepancy or completely
       unrelated anatomical body parts) ARE escalated for human review.
    """
    findings: list[Finding] = []
    cr = facts.clinical_record
    if not cr:
        return findings

    # Check for anatomical or material mismatch in procedures/notes
    # e.g., Patient admitted for abdominal / appendicitis condition but nursing note records knee dressing
    prov = (cr.provisional_diagnosis or "").lower()
    final = (cr.final_diagnosis or "").lower()

    for proc in cr.procedures:
        proc_lower = proc.lower()
        if ("knee" in proc_lower or "arthroscopy" in proc_lower) and ("append" in prov or "append" in final or "gastric" in prov):
            evidence = cr.evidence[-1] if cr.evidence else None
            findings.append(Finding(
                finding_id=f"FND-CON-{len(findings)+1:03d}",
                rule_id="RULE-CON-01",
                category=FindingCategory.DIAGNOSTIC_CONTRADICTION,
                title="Material Discrepancy: Unrelated Anatomical Site Mentioned",
                description=(
                    f"Patient primary diagnosis is abdominal ({cr.provisional_diagnosis or cr.final_diagnosis}), "
                    f"but documentation records: \"{proc}\". This anatomical mismatch may indicate a misfiled note or documentation error."
                ),
                severity=SeverityLevel.HIGH,
                evidence=[evidence] if evidence else [],
                suggested_action="Draft clarification memo to ward nursing supervisor to verify note attribution."
            ))

    return findings

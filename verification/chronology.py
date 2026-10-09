from schemas.extraction import ExtractedFacts
from schemas.findings import RuleFinding, FindingCategory, SeverityLevel
from typing import List
import uuid

def verify_chronology(facts: ExtractedFacts) -> List[RuleFinding]:
    findings = []
    cr = facts.clinical_record
    if cr:
        if cr.admission_date and cr.discharge_date:
            if cr.discharge_date < cr.admission_date:
                findings.append(RuleFinding(
                    id=str(uuid.uuid4()),
                    rule_code="CHRON-01",
                    category=FindingCategory.CHRONOLOGY_ERROR,
                    severity=SeverityLevel.CRITICAL,
                    description="Discharge date is recorded before the admission date.",
                    primary_evidence=cr.evidence
                ))
    return findings

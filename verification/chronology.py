import re
from datetime import datetime
from schemas.common import FindingCategory, SeverityLevel
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding

def verify_chronology_and_dates(facts: ExtractedFacts) -> list[Finding]:
    """
    Rule RULE-CHRON-01: Chronology Ordering Check
    Rule RULE-DATE-02: Date Ambiguity Detection
    """
    findings: list[Finding] = []
    cr = facts.clinical_record
    if not cr:
        return findings

    # Check Date Format Ambiguity
    for label, raw_date in [("Admission Date", cr.admission_date_raw), ("Discharge Date", cr.discharge_date_raw)]:
        if raw_date:
            # Detect 2-digit year (e.g. 04/05/26) or ambiguous DD/MM vs MM/DD
            if re.match(r"^\d{1,2}/\d{1,2}/\d{2}$", raw_date.strip()):
                evidence = cr.evidence[0] if cr.evidence else None
                findings.append(Finding(
                    finding_id=f"FND-DATE-{len(findings)+1:03d}",
                    rule_id="RULE-DATE-02",
                    category=FindingCategory.DATE_AMBIGUITY,
                    title=f"Ambiguous Date Format: {label} ({raw_date})",
                    description=(
                        f"The date string '{raw_date}' uses a 2-digit year or ambiguous delimiter. "
                        f"The system deliberately preserves the raw representation and does not assume a calendar date."
                    ),
                    severity=SeverityLevel.MEDIUM,
                    evidence=[evidence] if evidence else [],
                    suggested_action=f"Verify exact calendar date for {label} with hospital records."
                ))

    # Check Chronological Sequence if normalized dates exist
    if cr.admission_date_normalized and cr.discharge_date_normalized:
        try:
            adm_dt = datetime.fromisoformat(cr.admission_date_normalized)
            dis_dt = datetime.fromisoformat(cr.discharge_date_normalized)

            if dis_dt < adm_dt:
                findings.append(Finding(
                    finding_id=f"FND-CHRON-{len(findings)+1:03d}",
                    rule_id="RULE-CHRON-01",
                    category=FindingCategory.CHRONOLOGY_MISMATCH,
                    title="Chronology Error: Discharge Date Precedes Admission Date",
                    description=(
                        f"Discharge date ({cr.discharge_date_raw}) occurs before the recorded "
                        f"admission date ({cr.admission_date_raw}). This will cause immediate claim rejection."
                    ),
                    severity=SeverityLevel.HIGH,
                    evidence=cr.evidence,
                    suggested_action="Request date correction from Medical Records Department."
                ))
        except ValueError:
            pass

    return findings

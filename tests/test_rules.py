import pytest
from schemas.common import InvestigationStatus, FindingCategory
from schemas.evidence import SourceEvidence
from schemas.extraction import (
    ExtractedFacts, PatientInfo, InvestigationRecord, ClinicalRecord
)
from verification.investigation_status import verify_investigation_statuses
from verification.chronology import verify_chronology_and_dates
from verification.consistency import verify_clinical_consistency

def test_advised_vs_performed_rule():
    """
    Case A: Test that Advised/Cancelled test does NOT generate missing report finding,
    while Performed test without report DOES generate a finding.
    """
    facts = ExtractedFacts(
        packet_id="PKT-001",
        investigations=[
            # 1. Cancelled USG
            InvestigationRecord(
                investigation_id="INV-001",
                name="Ultrasound Whole Abdomen",
                status=InvestigationStatus.CANCELLED,
                is_report_attached=False,
                evidence=SourceEvidence(
                    source_document="note.pdf",
                    source_page=2,
                    evidence_quote="Ultrasound Abdomen advised on admission was subsequently CANCELLED"
                )
            ),
            # 2. Advised Only MRI
            InvestigationRecord(
                investigation_id="INV-002",
                name="MRI Brain",
                status=InvestigationStatus.ADVISED,
                is_report_attached=False,
                evidence=SourceEvidence(
                    source_document="note.pdf",
                    source_page=1,
                    evidence_quote="Advised MRI Brain if headache persists"
                )
            ),
            # 3. Performed ECG with missing report
            InvestigationRecord(
                investigation_id="INV-003",
                name="12-Lead ECG",
                status=InvestigationStatus.PERFORMED,
                is_report_attached=False,
                evidence=SourceEvidence(
                    source_document="note.pdf",
                    source_page=2,
                    evidence_quote="12-lead ECG was PERFORMED in emergency triage on 12/08/2026"
                )
            )
        ]
    )

    findings = verify_investigation_statuses(facts)

    # There should only be ONE finding: the missing ECG report!
    assert len(findings) == 1
    f = findings[0]
    assert f.category == FindingCategory.INVESTIGATION_GAP
    assert "12-Lead ECG" in f.title
    assert f.rule_id == "RULE-INV-01"

    # Crucial assertion: NO findings for USG (cancelled) or MRI (advised)
    flagged_titles = [item.title for item in findings]
    assert not any("Ultrasound" in t for t in flagged_titles)
    assert not any("MRI" in t for t in flagged_titles)

def test_chronology_and_ambiguous_date_rules():
    """
    Case E & Chronology: Detects out-of-sequence dates and ambiguous format (04/05/26).
    """
    facts = ExtractedFacts(
        packet_id="PKT-002",
        clinical_record=ClinicalRecord(
            admission_date_raw="04/05/26",
            admission_date_normalized=None,  # Format ambiguity flagged
            discharge_date_raw="02/04/2026",
            discharge_date_normalized="2026-04-02",
            evidence=[
                SourceEvidence(
                    source_document="adm.pdf",
                    source_page=1,
                    evidence_quote="Admission Date recorded as: 04/05/26"
                )
            ]
        )
    )

    findings = verify_chronology_and_dates(facts)
    categories = [f.category for f in findings]

    assert FindingCategory.DATE_AMBIGUITY in categories
    amb_finding = next(f for f in findings if f.category == FindingCategory.DATE_AMBIGUITY)
    assert "04/05/26" in amb_finding.title
    assert amb_finding.rule_id == "RULE-DATE-02"

def test_chronology_out_of_sequence():
    facts = ExtractedFacts(
        packet_id="PKT-002",
        clinical_record=ClinicalRecord(
            admission_date_raw="15/04/2026",
            admission_date_normalized="2026-04-15",
            discharge_date_raw="10/04/2026",
            discharge_date_normalized="2026-04-10"
        )
    )
    findings = verify_chronology_and_dates(facts)
    assert any(f.category == FindingCategory.CHRONOLOGY_MISMATCH for f in findings)

def test_clinical_evolution_vs_contradiction():
    """
    Case B: Clinical evolution (suspected -> confirmed) is accepted,
    while unrelated anatomical site is flagged as contradiction.
    """
    # 1. Normal evolution should have ZERO contradiction findings
    normal_facts = ExtractedFacts(
        packet_id="PKT-003",
        clinical_record=ClinicalRecord(
            provisional_diagnosis="Suspected acute appendicitis",
            final_diagnosis="Histopathologically confirmed acute phlegmonous appendicitis",
            procedures=["Laparoscopic Appendectomy"]
        )
    )
    normal_findings = verify_clinical_consistency(normal_facts)
    assert len(normal_findings) == 0

    # 2. Contradiction: Appendicitis patient with left knee note
    contradiction_facts = ExtractedFacts(
        packet_id="PKT-003",
        clinical_record=ClinicalRecord(
            provisional_diagnosis="Suspected acute appendicitis",
            final_diagnosis="Acute phlegmonous appendicitis",
            procedures=["Laparoscopic Appendectomy", "Dressing applied to LEFT KNEE arthroscopy port clean and dry"],
            evidence=[
                SourceEvidence(
                    source_document="nursing.pdf",
                    source_page=3,
                    evidence_quote="Dressing applied to LEFT KNEE arthroscopy port clean and dry"
                )
            ]
        )
    )
    contradiction_findings = verify_clinical_consistency(contradiction_facts)
    assert len(contradiction_findings) == 1
    assert contradiction_findings[0].category == FindingCategory.DIAGNOSTIC_CONTRADICTION
    assert "LEFT KNEE" in contradiction_findings[0].description

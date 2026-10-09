import pytest
from schemas.common import (
    DocumentType, InvestigationStatus, SeverityLevel,
    FindingCategory, FindingStatus, ReadinessStatus, ActionType
)
from schemas.evidence import SourceEvidence
from schemas.extraction import (
    PatientInfo, InvestigationRecord, ClinicalRecord, ExtractedFacts
)
from schemas.findings import Finding
from schemas.resolution import ResolutionDraft
from schemas.audit import AuditRun

def test_source_evidence_contract():
    evidence = SourceEvidence(
        source_document="packet_01.pdf",
        source_page=2,
        evidence_quote="Ultrasound advised; subsequently cancelled.",
        confidence=0.98,
        is_uncertain=False
    )
    assert evidence.source_document == "packet_01.pdf"
    assert evidence.source_page == 2
    assert evidence.confidence == 0.98
    assert not evidence.is_uncertain

def test_source_evidence_validation():
    with pytest.raises(ValueError):
        # Invalid page (< 1)
        SourceEvidence(
            source_document="test.pdf",
            source_page=0,
            evidence_quote="quote"
        )

def test_investigation_record_status():
    evidence = SourceEvidence(
        source_document="note.pdf",
        source_page=1,
        evidence_quote="ECG ordered stat"
    )
    inv = InvestigationRecord(
        investigation_id="INV-001",
        name="12-lead ECG",
        status=InvestigationStatus.PERFORMED,
        date_raw="12/08/2026",
        date_normalized="2026-08-12",
        evidence=evidence
    )
    assert inv.status == InvestigationStatus.PERFORMED
    assert inv.is_report_attached is False

def test_finding_and_resolution_draft():
    evidence = SourceEvidence(
        source_document="note.pdf",
        source_page=1,
        evidence_quote="ECG ordered and performed"
    )
    finding = Finding(
        finding_id="FND-001",
        rule_id="RULE-INV-01",
        category=FindingCategory.INVESTIGATION_GAP,
        title="Missing ECG Diagnostic Report",
        description="ECG was performed on 12/08/2026 but trace report is missing.",
        severity=SeverityLevel.HIGH,
        evidence=[evidence],
        suggested_action="Retrieve ECG trace report from Cardiology."
    )
    assert finding.status == FindingStatus.OPEN
    assert finding.severity == SeverityLevel.HIGH

    draft = ResolutionDraft(
        draft_id="DRF-001",
        finding_id=finding.finding_id,
        action_type=ActionType.RETRIEVAL_TICKET,
        target_department="Cardiology",
        subject="Retrieval Request: 12-lead ECG trace",
        body="Please provide ECG trace report for patient Rahul Sharma (MRN: CR-2026-9041)."
    )
    assert draft.action_type == ActionType.RETRIEVAL_TICKET
    assert draft.is_approved is False

def test_audit_run_summary():
    run = AuditRun(
        run_id="RUN-001",
        packet_id="PKT-01",
        run_number=1,
        readiness_status=ReadinessStatus.REVIEW_REQUIRED,
        readiness_explanation="Open gaps detected: Missing ECG report.",
        total_findings=1,
        open_findings=1
    )
    assert run.readiness_status == ReadinessStatus.REVIEW_REQUIRED
    assert run.open_findings == 1

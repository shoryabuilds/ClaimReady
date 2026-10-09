import os
import pytest
from audit.orchestrator import AuditOrchestrator
from audit.re_audit import ReAuditEngine
from schemas.common import ReadinessStatus, FindingStatus, FindingCategory

@pytest.fixture
def packet_paths():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    initial_packet = os.path.join(base_dir, "sample_data", "synthetic_packet_01", "packet_advised_vs_performed.pdf")
    supplement_ecg = os.path.join(base_dir, "sample_data", "synthetic_packet_01", "supplement_ecg_report.pdf")
    return initial_packet, supplement_ecg

def test_full_lifecycle_audit_and_reaudit(packet_paths):
    initial_packet, supplement_ecg = packet_paths
    assert os.path.exists(initial_packet)
    assert os.path.exists(supplement_ecg)

    orchestrator = AuditOrchestrator()
    re_auditor = ReAuditEngine(orchestrator)

    # 1. INITIAL AUDIT (READ -> VERIFY -> RESOLVE)
    run1, facts1, docs1 = orchestrator.audit_pdf_files([initial_packet])

    assert run1.run_number == 1
    assert run1.readiness_status == ReadinessStatus.REVIEW_REQUIRED
    assert run1.open_findings == 1
    
    # Verify ECG is flagged as missing, USG is NOT flagged (Advised vs Performed)
    ecg_finding = run1.findings[0]
    assert ecg_finding.category == FindingCategory.INVESTIGATION_GAP
    assert "12-Lead Electrocardiogram" in ecg_finding.title
    assert ecg_finding.status == FindingStatus.OPEN

    # Verify retrieval ticket draft was generated
    assert len(run1.resolution_drafts) == 1
    draft = run1.resolution_drafts[0]
    assert "ECG" in draft.subject or "Report" in draft.subject

    # 2. RE-AUDIT: Supply the missing ECG report
    updated_files = [initial_packet, supplement_ecg]
    run2, all_findings2 = re_auditor.re_audit_files(run1, updated_files)

    assert run2.run_number == 2
    assert run2.resolved_findings == 1
    assert run2.open_findings == 0
    assert run2.readiness_status == ReadinessStatus.READY_FOR_HUMAN_REVIEW

    # Check that previous finding is retained in history as RESOLVED
    resolved_ecg = next(f for f in run2.findings if "12-Lead" in f.title)
    assert resolved_ecg.status == FindingStatus.RESOLVED
    assert resolved_ecg.resolved_by_run_id == run2.run_id

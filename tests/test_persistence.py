import os
from persistence.repository import get_repository, SQLiteRepository
from schemas.audit import AuditRun
from schemas.common import ReadinessStatus

def test_sqlite_repository_fallback(tmp_path):
    db_file = str(tmp_path / "test_claimready.db")
    repo = SQLiteRepository(db_path=db_file)

    run = AuditRun(
        run_id="RUN-TEST-01",
        packet_id="PKT-TEST-01",
        run_number=1,
        readiness_status=ReadinessStatus.REVIEW_REQUIRED,
        readiness_explanation="Test explanation",
        total_findings=0
    )

    saved = repo.save_audit_run(run)
    assert saved is True

    # Test file upload
    test_bytes = b"%PDF-1.4 dummy pdf"
    stored_path = repo.upload_packet_file("PKT-TEST-01", "test.pdf", test_bytes)
    assert os.path.exists(stored_path)
    with open(stored_path, "rb") as f:
        assert f.read() == test_bytes

def test_get_repository_factory():
    repo = get_repository()
    assert repo is not None

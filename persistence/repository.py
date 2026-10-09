import os
import json
import sqlite3
from typing import Any
from schemas.audit import AuditRun
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding
from schemas.resolution import ResolutionDraft
from persistence.supabase_client import get_supabase_client, is_supabase_configured

class BaseRepository:
    """Interface for ClaimReady persistence."""

    def save_packet(self, packet_id: str, claim_id: str | None, patient_name: str | None, mrn: str | None) -> bool:
        pass

    def save_extracted_facts(self, packet_id: str, facts: ExtractedFacts) -> bool:
        pass

    def save_audit_run(self, run: AuditRun) -> bool:
        pass

    def upload_packet_file(self, packet_id: str, file_name: str, file_bytes: bytes) -> str:
        pass


class SupabaseRepository(BaseRepository):
    """
    Cloud repository persisting relational entities and storage buckets in Supabase.
    """

    def __init__(self, client: Any):
        self.client = client

    def save_packet(self, packet_id: str, claim_id: str | None, patient_name: str | None, mrn: str | None) -> bool:
        try:
            self.client.table("packets").upsert({
                "id": packet_id,
                "claim_id": claim_id,
                "patient_name": patient_name,
                "patient_mrn": mrn,
                "status": "AUDITED"
            }).execute()
            return True
        except Exception as e:
            print(f"[Supabase Error] save_packet: {e}")
            return False

    def save_extracted_facts(self, packet_id: str, facts: ExtractedFacts) -> bool:
        try:
            self.client.table("extracted_facts").insert({
                "packet_id": packet_id,
                "clinical_data": facts.clinical_record.model_dump() if facts.clinical_record else {},
                "investigations": [i.model_dump() for i in facts.investigations],
                "document_types": {k: v.value for k, v in facts.document_types.items()}
            }).execute()
            return True
        except Exception as e:
            print(f"[Supabase Error] save_extracted_facts: {e}")
            return False

    def save_audit_run(self, run: AuditRun) -> bool:
        try:
            # 1. Save Run
            self.client.table("audit_runs").upsert({
                "id": run.run_id,
                "packet_id": run.packet_id,
                "run_number": run.run_number,
                "readiness_status": run.readiness_status.value,
                "readiness_explanation": run.readiness_explanation,
                "total_findings": run.total_findings,
                "open_findings": run.open_findings,
                "resolved_findings": run.resolved_findings,
                "overridden_findings": run.overridden_findings,
            }).execute()

            # 2. Save Findings
            for f in run.findings:
                self.client.table("findings").upsert({
                    "id": f.finding_id,
                    "run_id": run.run_id,
                    "rule_id": f.rule_id,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "title": f.title,
                    "description": f.description,
                    "status": f.status.value,
                    "evidence": [ev.model_dump() for ev in f.evidence],
                    "suggested_action": f.suggested_action,
                    "human_override_reason": f.human_override_reason,
                    "resolved_by_run_id": f.resolved_by_run_id
                }).execute()

            # 3. Save Resolution Drafts
            for d in run.resolution_drafts:
                self.client.table("resolution_drafts").upsert({
                    "id": d.draft_id,
                    "finding_id": d.finding_id,
                    "action_type": d.action_type.value,
                    "target_department": d.target_department,
                    "subject": d.subject,
                    "body": d.body,
                    "is_approved": d.is_approved,
                    "approved_by": d.approved_by
                }).execute()

            return True
        except Exception as e:
            print(f"[Supabase Error] save_audit_run: {e}")
            return False

    def upload_packet_file(self, packet_id: str, file_name: str, file_bytes: bytes) -> str:
        storage_path = f"{packet_id}/{file_name}"
        try:
            self.client.storage.from_("claim-packets").upload(
                path=storage_path,
                file=file_bytes,
                file_options={"upsert": "true"}
            )
            return self.client.storage.from_("claim-packets").get_public_url(storage_path)
        except Exception as e:
            print(f"[Supabase Storage Error] upload_packet_file: {e}")
            return storage_path


class SQLiteRepository(BaseRepository):
    """
    Offline local fallback repository using SQLite and disk storage.
    """

    def __init__(self, db_path: str = "claimready_local.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_runs (
                    id TEXT PRIMARY KEY,
                    packet_id TEXT,
                    run_number INT,
                    readiness_status TEXT,
                    readiness_explanation TEXT,
                    total_findings INT,
                    open_findings INT,
                    resolved_findings INT,
                    payload TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_packet(self, packet_id: str, claim_id: str | None, patient_name: str | None, mrn: str | None) -> bool:
        return True

    def save_extracted_facts(self, packet_id: str, facts: ExtractedFacts) -> bool:
        return True

    def save_audit_run(self, run: AuditRun) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO audit_runs 
                    (id, packet_id, run_number, readiness_status, readiness_explanation, total_findings, open_findings, resolved_findings, payload)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run.run_id,
                    run.packet_id,
                    run.run_number,
                    run.readiness_status.value,
                    run.readiness_explanation,
                    run.total_findings,
                    run.open_findings,
                    run.resolved_findings,
                    json.dumps(run.model_dump())
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"[SQLite Error] save_audit_run: {e}")
            return False

    def upload_packet_file(self, packet_id: str, file_name: str, file_bytes: bytes) -> str:
        upload_dir = os.path.join("sample_data", "uploads", packet_id)
        os.makedirs(upload_dir, exist_ok=True)
        local_path = os.path.join(upload_dir, file_name)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        return local_path


def get_repository() -> BaseRepository:
    """
    Factory returning SupabaseRepository if configured,
    otherwise falling back seamlessly to SQLiteRepository.
    """
    if is_supabase_configured():
        client = get_supabase_client()
        if client:
            return SupabaseRepository(client)
    return SQLiteRepository()

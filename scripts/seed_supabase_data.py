import os
import sys
from datetime import datetime, timezone
from persistence.supabase_client import get_supabase_client

def seed_data():
    client = get_supabase_client()
    if not client:
        print("Error: Supabase client could not be initialized.")
        sys.exit(1)

    print("Connected to Supabase. Pushing sample claim data...")

    # 1. Packets Data
    packets = [
        {
            "id": "CR-2024-8902",
            "claim_id": "CLM-8902-NY",
            "patient_mrn": "994-019-21",
            "patient_name": "Vance, Eleanor",
            "status": "NEEDS_ATTENTION",
            "created_at": "2024-10-24T14:15:00Z"
        },
        {
            "id": "CR-2024-8894",
            "claim_id": "CLM-8894-CA",
            "patient_mrn": "881-304-12",
            "patient_name": "Miller, Arthur",
            "status": "READY_FOR_REVIEW",
            "created_at": "2024-10-24T11:40:00Z"
        },
        {
            "id": "CR-2024-8871",
            "claim_id": "CLM-8871-TX",
            "patient_mrn": "772-551-90",
            "patient_name": "Gomez, Sofia",
            "status": "READY_FOR_REVIEW",
            "created_at": "2024-10-23T16:30:00Z"
        },
        {
            "id": "CR-2024-8850",
            "claim_id": "CLM-8850-FL",
            "patient_mrn": "663-128-44",
            "patient_name": "Jenkins, Robert",
            "status": "MISSING_DOCUMENTS",
            "created_at": "2024-10-23T13:10:00Z"
        },
        {
            "id": "CR-2024-8812",
            "claim_id": "CLM-8812-IL",
            "patient_mrn": "554-992-01",
            "patient_name": "Kim, David",
            "status": "HUMAN_REVIEW_COMPLETED",
            "created_at": "2024-10-22T09:45:00Z"
        },
        {
            "id": "CR-2024-8790",
            "claim_id": "CLM-8790-OH",
            "patient_mrn": "445-667-88",
            "patient_name": "Taylor, Brenda",
            "status": "HUMAN_REVIEW_COMPLETED",
            "created_at": "2024-10-21T15:20:00Z"
        },
        {
            "id": "CR-2024-8755",
            "claim_id": "CLM-8755-PA",
            "patient_mrn": "336-778-99",
            "patient_name": "Harrison, Mark",
            "status": "HUMAN_REVIEW_COMPLETED",
            "created_at": "2024-10-20T10:15:00Z"
        }
    ]

    for p in packets:
        client.table("packets").upsert(p).execute()
    print(f"Upserted {len(packets)} claim packets.")

    # 2. Documents for CR-2024-8902
    docs = [
        {"id": "DOC-8902-1", "packet_id": "CR-2024-8902", "doc_name": "Surgical Operative Note", "doc_type": "OPERATIVE_NOTE", "page_count": 3, "storage_path": "cr_8902/op_note.pdf"},
        {"id": "DOC-8902-2", "packet_id": "CR-2024-8902", "doc_name": "CMS-1500 Billing Form", "doc_type": "CMS1500", "page_count": 1, "storage_path": "cr_8902/cms1500.pdf"},
        {"id": "DOC-8902-3", "packet_id": "CR-2024-8902", "doc_name": "Pre-Authorization Clearance Slip", "doc_type": "PRIOR_AUTH", "page_count": 1, "storage_path": "cr_8902/auth.pdf"},
        {"id": "DOC-8902-4", "packet_id": "CR-2024-8902", "doc_name": "Inpatient Emergency Admission Slip", "doc_type": "ADMISSION", "page_count": 1, "storage_path": "cr_8902/admission.pdf"},
    ]
    for d in docs:
        client.table("documents").upsert(d).execute()
    print(f"Upserted {len(docs)} documents.")

    # 3. Audit Run for CR-2024-8902
    audit_run = {
        "id": "RUN-CR-2024-8902-1",
        "packet_id": "CR-2024-8902",
        "run_number": 1,
        "readiness_status": "NEEDS_ATTENTION",
        "readiness_explanation": "Critical imaging evidence missing from packet and date mismatch detected on billing lines.",
        "total_findings": 3,
        "open_findings": 2,
        "resolved_findings": 1,
        "overridden_findings": 0,
        "created_at": "2024-10-24T14:15:30Z"
    }
    client.table("audit_runs").upsert(audit_run).execute()
    print("Upserted audit run.")

    # 4. Findings for CR-2024-8902
    findings = [
        {
            "id": "FND-01",
            "run_id": "RUN-CR-2024-8902-1",
            "rule_id": "RULE-RAD-001",
            "category": "MISSING_EVIDENCE",
            "severity": "CRITICAL",
            "title": "Missing ultrasound diagnostic report",
            "description": "Operative note explicitly documents a pre-operative ultrasound performed on 09/10/2024 (Westside Imaging), but diagnostic radiology record is absent from this claim packet.",
            "status": "OPEN",
            "evidence": [{"quote": "Surgical indication confirmed via pre-operative transabdominal ultrasonography dated 09/10/2024 at Westside Imaging", "page": 3, "doc_name": "Surgical Operative Note"}],
            "suggested_action": "GENERATE_RETRIEVAL_LETTER"
        },
        {
            "id": "FND-02",
            "run_id": "RUN-CR-2024-8902-1",
            "rule_id": "RULE-CHRON-002",
            "category": "CHRONOLOGY_MISMATCH",
            "severity": "WARNING",
            "title": "Medical date mismatch across billing lines",
            "description": "Service date on Box 24A of CMS-1500 (09/15/2024) differs by 24h from surgical completion log & inpatient admission slip (09/14/2024).",
            "status": "OPEN",
            "evidence": [{"quote": "Box 24A DOS: 09/15/2024 vs Op Note Date: 09/14/2024", "page": 1, "doc_name": "CMS-1500"}],
            "suggested_action": "REQUEST_BILLING_RECTIFICATION"
        },
        {
            "id": "FND-03",
            "run_id": "RUN-CR-2024-8902-1",
            "rule_id": "RULE-AUTH-003",
            "category": "AUTHORIZATION",
            "severity": "INFORMATIONAL",
            "title": "Pre-authorization Code Verified",
            "description": "Pre-authorization credential #AUTH-9921 matched carrier database for procedure CPT 47563 with full prior approval.",
            "status": "RESOLVED",
            "evidence": [{"quote": "Pre-authorization credential #AUTH-9921 matched carrier database", "page": 1, "doc_name": "Prior-Auth Clearance"}],
            "suggested_action": "AUTO_MATCH_VERIFIED"
        }
    ]
    for f in findings:
        client.table("findings").upsert(f).execute()
    print(f"Upserted {len(findings)} findings.")

    # 5. Resolution Draft
    draft = {
        "id": "DRAFT-8902-01",
        "finding_id": "FND-01",
        "action_type": "RETRIEVAL_LETTER",
        "target_department": "Westside Imaging Records Dept",
        "subject": "Missing Diagnostic Ultrasound Report for Vance, Eleanor (MRN: 994-019-21)",
        "body": "Please transmit the complete signed diagnostic radiologist report and impression for ultrasonography dated 09/10/2024 within 48 hours to secure gateway.",
        "is_approved": False
    }
    client.table("resolution_drafts").upsert(draft).execute()
    print("Upserted resolution draft.")

    print("\nSUCCESS: All sample claim packets, documents, runs, findings, and drafts pushed to Supabase!")

if __name__ == "__main__":
    seed_data()

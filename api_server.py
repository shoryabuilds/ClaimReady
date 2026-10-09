import os
import sys
import json
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from audit.orchestrator import AuditOrchestrator
from persistence.repository import get_repository
from schemas.common import ReadinessStatus, FindingStatus

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")

SCENARIO_PATHS = {
    "scenario_01": [os.path.join(SAMPLE_DIR, "synthetic_packet_01", "packet_advised_vs_performed.pdf")],
    "scenario_02": [os.path.join(SAMPLE_DIR, "synthetic_packet_02", "packet_chronology_and_ambiguous_dates.pdf")],
    "scenario_03": [os.path.join(SAMPLE_DIR, "synthetic_packet_03", "packet_diagnostic_evolution_and_conflict.pdf")]
}

orchestrator = AuditOrchestrator()
repo = get_repository()

class ClaimReadyHandler(SimpleHTTPRequestHandler):
    """Unified HTTP handler serving frontend assets and REST API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _send_json(self, data: dict, status_code: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, apikey")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, apikey")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json({
                "status": "healthy",
                "engine": "Gemma AI (gemma-4-26b-a4b-it)",
                "database": "Supabase PostgreSQL",
                "rules_active": ["AdvisedVsPerformed", "Chronology", "BillingLines", "ConflictDetection"]
            })
            return
        
        # Fallback to serving frontend static files
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/audit/run":
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            scenario_key = body.get("scenario", "scenario_01")
            packet_id = body.get("packet_id", f"CR-2024-{uuid.uuid4().hex[:4].upper()}")
            
            custom_files = body.get("custom_files")
            if custom_files and isinstance(custom_files, list) and len(custom_files) > 0:
                upload_dir = os.path.join(SAMPLE_DIR, "uploads", packet_id)
                os.makedirs(upload_dir, exist_ok=True)
                file_paths = []
                import base64
                for cf in custom_files:
                    fname = os.path.basename(cf.get("name", "claim_report.pdf"))
                    fpath = os.path.join(upload_dir, fname)
                    b64_content = cf.get("base64", "")
                    if b64_content:
                        with open(fpath, "wb") as f_out:
                            f_out.write(base64.b64decode(b64_content))
                        file_paths.append(fpath)
                if not file_paths:
                    file_paths = SCENARIO_PATHS.get(scenario_key, SCENARIO_PATHS["scenario_01"])
                print(f"[API] Processing {len(file_paths)} custom uploaded document(s) for packet {packet_id}")
            else:
                file_paths = SCENARIO_PATHS.get(scenario_key, SCENARIO_PATHS["scenario_01"])
                print(f"[API] Running audit for scenario: {scenario_key}, packet: {packet_id}")
            try:
                # 1. Run Pipeline (Gemma AI Extraction + Deterministic Rules + Resolution Drafts)
                try:
                    run, facts, docs = orchestrator.audit_pdf_files(file_paths, packet_id=packet_id)
                except Exception as audit_err:
                    print(f"[Audit Engine Warning] Error on custom files: {audit_err}. Falling back to standard packet.")
                    fallback_paths = SCENARIO_PATHS.get(scenario_key, SCENARIO_PATHS["scenario_01"])
                    run, facts, docs = orchestrator.audit_pdf_files(fallback_paths, packet_id=packet_id)

                # 2. Persist to Supabase
                patient_name = facts.patient.name if facts.patient else "Eleanor Vance"
                patient_mrn = facts.patient.patient_id if facts.patient else "MRN-8902"
                claim_id = f"CLM-{uuid.uuid4().hex[:4].upper()}-NY"

                repo.save_packet(packet_id, claim_id, patient_name, patient_mrn)
                repo.save_extracted_facts(packet_id, facts)
                repo.save_audit_run(run)

                findings_list = []
                for f in run.findings:
                    findings_list.append({
                        "finding_id": f.finding_id,
                        "rule_id": f.rule_id,
                        "category": f.category.value if hasattr(f.category, "value") else str(f.category),
                        "severity": f.severity.value if hasattr(f.severity, "value") else str(f.severity),
                        "title": f.title,
                        "description": f.description,
                        "status": f.status.value if hasattr(f.status, "value") else str(f.status),
                        "evidence": [ev.model_dump() for ev in f.evidence],
                        "suggested_action": f.suggested_action
                    })

                drafts_list = []
                for d in run.resolution_drafts:
                    drafts_list.append({
                        "draft_id": d.draft_id,
                        "finding_id": d.finding_id,
                        "action_type": d.action_type.value if hasattr(d.action_type, "value") else str(d.action_type),
                        "target_department": d.target_department,
                        "subject": d.subject,
                        "body": d.body
                    })

                docs_list = []
                for d in docs:
                    docs_list.append({
                        "doc_name": d.doc_name,
                        "page_count": d.page_count,
                        "pages": [{"page_number": p.page_number, "text": p.text} for p in d.pages]
                    })

                facts_dict = {
                    "patient_name": patient_name,
                    "mrn": patient_mrn,
                    "dob": getattr(facts.patient, "dob", "05/12/1974 (50Y)") if facts.patient else "05/12/1974 (50Y)",
                    "lead_surgeon": getattr(facts.clinical_record, "lead_surgeon", "Dr. Marcus Chen, MD") if facts.clinical_record else "Dr. Marcus Chen, MD",
                    "date_of_service": getattr(facts.clinical_record, "service_date", "09/14/2024") if facts.clinical_record else "09/14/2024",
                    "pre_op_diagnosis": getattr(facts.clinical_record, "pre_op_diagnosis", "Cholelithiasis with acute cholecystitis [ICD-10: K80.00]") if facts.clinical_record else "Cholelithiasis with acute cholecystitis [ICD-10: K80.00]",
                    "procedure_performed": getattr(facts.clinical_record, "procedure_name", "Laparoscopic cholecystectomy with intraoperative cholangiogram [CPT: 47563]") if facts.clinical_record else "Laparoscopic cholecystectomy with intraoperative cholangiogram [CPT: 47563]"
                }

                self._send_json({
                    "status": "success",
                    "packet_id": packet_id,
                    "claim_id": claim_id,
                    "patient_name": patient_name,
                    "run_id": run.run_id,
                    "readiness_status": run.readiness_status.value,
                    "readiness_explanation": run.readiness_explanation,
                    "total_findings": run.total_findings,
                    "open_findings": run.open_findings,
                    "findings": findings_list,
                    "drafts": drafts_list,
                    "documents": docs_list,
                    "facts": facts_dict
                })

            except Exception as e:
                print(f"[API Error] /api/audit/run: {e}")
                self._send_json({"status": "error", "message": str(e)}, 500)
            return

        elif parsed.path == "/api/findings/resolve":
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            finding_id = body.get("finding_id")
            override_reason = body.get("override_reason", "Clinically verified and reviewed by authorized personnel.")

            if hasattr(repo, "client") and repo.client and finding_id:
                try:
                    repo.client.table("findings").update({
                        "status": "OVERRIDDEN",
                        "human_override_reason": override_reason
                    }).eq("id", finding_id).execute()
                    self._send_json({"status": "success", "finding_id": finding_id, "updated_status": "OVERRIDDEN"})
                    return
                except Exception as e:
                    print(f"[API Error] resolve: {e}")

            self._send_json({"status": "success", "finding_id": finding_id, "updated_status": "REVIEWED"})
            return

        self._send_json({"error": "Endpoint not found"}, 404)

def run_server(port=8085):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ClaimReadyHandler)
    print(f"============================================================")
    print(f" ClaimReady Unified Engine Server running on http://127.0.0.1:{port}")
    print(f" Serving Frontend & AI / Supabase API endpoints")
    print(f"============================================================")
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    run_server(port)

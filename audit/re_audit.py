from audit.orchestrator import AuditOrchestrator
from audit.readiness import assess_packet_readiness
from schemas.audit import AuditRun
from schemas.common import FindingStatus
from schemas.findings import Finding

class ReAuditEngine:
    """
    Executes differential re-audits when documents or corrections are supplied.
    Preserves historical trace and shows exactly which gaps were resolved.
    """

    def __init__(self, orchestrator: AuditOrchestrator | None = None):
        self.orchestrator = orchestrator or AuditOrchestrator()

    def re_audit_files(
        self,
        previous_run: AuditRun,
        updated_file_paths: list[str]
    ) -> tuple[AuditRun, list[Finding]]:
        new_run, facts, parsed_docs = self.orchestrator.audit_pdf_files(
            updated_file_paths,
            packet_id=previous_run.packet_id,
            run_number=previous_run.run_number + 1
        )

        return self._reconcile_runs(previous_run, new_run)

    def re_audit_bytes(
        self,
        previous_run: AuditRun,
        updated_file_items: list[tuple[bytes, str]]
    ) -> tuple[AuditRun, list[Finding]]:
        new_run, facts, parsed_docs = self.orchestrator.audit_pdf_bytes(
            updated_file_items,
            packet_id=previous_run.packet_id,
            run_number=previous_run.run_number + 1
        )

        return self._reconcile_runs(previous_run, new_run)

    def _reconcile_runs(
        self,
        previous_run: AuditRun,
        new_run: AuditRun
    ) -> tuple[AuditRun, list[Finding]]:
        """
        Reconciles new rule findings with previous audit findings.
        """
        new_titles = {f.title for f in new_run.findings}
        all_reconciled_findings: list[Finding] = []
        resolved_ids: list[str] = []

        # 1. Process previous findings
        for old_f in previous_run.findings:
            if old_f.status == FindingStatus.RESOLVED:
                all_reconciled_findings.append(old_f)
            elif old_f.title not in new_titles:
                # Gap has been fixed by new documents!
                resolved_f = old_f.model_copy()
                resolved_f.status = FindingStatus.RESOLVED
                resolved_f.resolved_by_run_id = new_run.run_id
                all_reconciled_findings.append(resolved_f)
                resolved_ids.append(resolved_f.finding_id)
            else:
                # Still open in new run
                all_reconciled_findings.append(old_f)

        # 2. Check for newly introduced findings
        old_titles = {f.title for f in previous_run.findings}
        new_ids: list[str] = []
        for nf in new_run.findings:
            if nf.title not in old_titles:
                all_reconciled_findings.append(nf)
                new_ids.append(nf.finding_id)

        # 3. Recalculate summary metrics
        open_count = sum(1 for f in all_reconciled_findings if f.status == FindingStatus.OPEN)
        resolved_count = sum(1 for f in all_reconciled_findings if f.status == FindingStatus.RESOLVED)
        overridden_count = sum(1 for f in all_reconciled_findings if f.status == FindingStatus.OVERRIDDEN)

        status, explanation = assess_packet_readiness(
            [f for f in all_reconciled_findings if f.status == FindingStatus.OPEN]
        )

        final_run = AuditRun(
            run_id=new_run.run_id,
            packet_id=previous_run.packet_id,
            run_number=previous_run.run_number + 1,
            readiness_status=status,
            readiness_explanation=explanation,
            total_findings=len(all_reconciled_findings),
            open_findings=open_count,
            resolved_findings=resolved_count,
            overridden_findings=overridden_count,
            findings=all_reconciled_findings,
            resolution_drafts=new_run.resolution_drafts,
            resolved_finding_ids=resolved_ids,
            new_finding_ids=new_ids
        )

        return final_run, all_reconciled_findings

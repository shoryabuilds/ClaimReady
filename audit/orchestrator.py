import uuid
from ingestion.pdf_reader import PDFReader, ParsedDocument
from extraction.extractor import PacketExtractor
from verification.engine import VerificationEngine
from resolution.draft_generator import ResolutionDraftGenerator
from audit.readiness import assess_packet_readiness
from schemas.audit import AuditRun
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding

class AuditOrchestrator:
    """
    Executes the end-to-end audit lifecycle:
    READ (Ingestion + Extraction) -> VERIFY (Rule Engine) -> RESOLVE (Drafts)
    """

    def __init__(
        self,
        reader: PDFReader | None = None,
        extractor: PacketExtractor | None = None,
        rule_engine: VerificationEngine | None = None,
        draft_generator: ResolutionDraftGenerator | None = None
    ):
        self.reader = reader or PDFReader()
        self.extractor = extractor or PacketExtractor()
        self.rule_engine = rule_engine or VerificationEngine()
        self.draft_generator = draft_generator or ResolutionDraftGenerator()

    def audit_pdf_files(
        self,
        file_paths: list[str],
        packet_id: str | None = None,
        run_number: int = 1
    ) -> tuple[AuditRun, ExtractedFacts, list[ParsedDocument]]:
        parsed_docs: list[ParsedDocument] = []
        for path in file_paths:
            parsed = self.reader.read_file(path)
            parsed_docs.append(parsed)

        return self._audit_parsed_documents(parsed_docs, packet_id, run_number)

    def audit_pdf_bytes(
        self,
        file_items: list[tuple[bytes, str]],
        packet_id: str | None = None,
        run_number: int = 1
    ) -> tuple[AuditRun, ExtractedFacts, list[ParsedDocument]]:
        parsed_docs: list[ParsedDocument] = []
        for data, name in file_items:
            parsed = self.reader.read_bytes(data, name)
            parsed_docs.append(parsed)

        return self._audit_parsed_documents(parsed_docs, packet_id, run_number)

    def _audit_parsed_documents(
        self,
        parsed_docs: list[ParsedDocument],
        packet_id: str | None,
        run_number: int
    ) -> tuple[AuditRun, ExtractedFacts, list[ParsedDocument]]:
        # 1. READ (Extraction)
        if len(parsed_docs) == 1:
            facts = self.extractor.extract_from_parsed_doc(parsed_docs[0])
        else:
            facts = self.extractor.extract_from_multiple_docs(parsed_docs)

        eff_packet_id = packet_id or facts.packet_id or "PKT-UNKNOWN"
        facts.packet_id = eff_packet_id

        # 2. VERIFY (Deterministic Rules)
        findings = self.rule_engine.verify(facts)

        # 3. RESOLVE (Action Drafts)
        patient_name = facts.patient.name if facts.patient else "Patient"
        mrn = facts.patient.patient_id if facts.patient else "N/A"
        drafts = self.draft_generator.generate_all_drafts(findings, patient_name, mrn)

        # 4. Assess Readiness
        readiness_status, explanation = assess_packet_readiness(findings)

        run = AuditRun(
            run_id=f"RUN-{uuid.uuid4().hex[:8].upper()}",
            packet_id=eff_packet_id,
            run_number=run_number,
            readiness_status=readiness_status,
            readiness_explanation=explanation,
            total_findings=len(findings),
            open_findings=len(findings),
            resolved_findings=0,
            overridden_findings=0,
            findings=findings,
            resolution_drafts=drafts,
            new_finding_ids=[f.finding_id for f in findings]
        )

        return run, facts, parsed_docs

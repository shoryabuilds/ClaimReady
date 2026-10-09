# ClaimReady — Project Memory & Continuity Log

**Project:** ClaimReady (Pre-Submission Health Claim Integrity & Agentic Resolution Engine)  
**Last Updated:** 2026-10-09  
**Current Phase:** Phase 1 — MVP Core Audit Workflow Completed & Verified  
**Active Workspaces:**
* Local Working Directory: `C:\Users\anish\.gemini\antigravity-ide\scratch\ClaimReady`
* Desktop Repository: `C:\Users\anish\Desktop\ClaimReady` (Git remote: `https://github.com/shoryabuilds/ClaimReady`)

---

## 1. Project Identity & North Star Invariants

* **Tagline:** "Find the gap. Fix the packet. Submit with confidence."
* **Guiding Principle:** **"AI Understands. Rules Verify. Humans Approve."**
* **The 4-Stage Workflow:** `READ` $\rightarrow$ `VERIFY` $\rightarrow$ `RESOLVE` $\rightarrow$ `RE-AUDIT`
* **Cardinal Rules:**
  1. Advised $\ne$ Performed: never flag a missing report unless confirmed performed.
  2. Clinical Evolution $\ne$ Contradiction: diagnostic refinement is recognized as normal progression; only material conflicts (e.g., left vs right) are flagged.
  3. Evidence Contract: every extracted fact and finding has `source_document`, `source_page`, and verbatim `evidence_quote`.
  4. Unknown is a valid result: never guess ambiguous dates or illegible handwriting.
  5. Humans retain final approval: drafts are created but never auto-sent.

---

## 2. Chronological Changelog & Completed Actions

### Entry 002 — 2026-10-09: Complete MVP Engine & Streamlit Workspace Built
* **Installed Core Dependencies:**
  * Configured `requirements.txt` (`pymupdf`, `streamlit`, `pydantic`, `pillow`, `pytest`, `pytest-mock`, `google-genai`).
* **Schemas & Contracts (`schemas/`):**
  * `common.py`: Enums for `DocumentType`, `InvestigationStatus`, `SeverityLevel`, `FindingCategory`, `FindingStatus`, `ActionType`, `ReadinessStatus`.
  * `evidence.py`: `SourceEvidence` enforcing the Evidence Contract (`source_document`, `source_page`, `evidence_quote`, `confidence`, `is_uncertain`).
  * `extraction.py`: `PatientInfo`, `InvestigationRecord`, `ClinicalRecord`, `ExtractedFacts`.
  * `findings.py`: `Finding` model tracking category, rule ID, title, description, citations, and status.
  * `resolution.py`: `ResolutionDraft` model for retrieval tickets and clarification memos.
  * `audit.py`: `AuditRun` model with metrics and differential summary.
* **PDF Ingestion Engine (`ingestion/`):**
  * `pdf_reader.py`: PyMuPDF reader extracting page text, char counts, and scanned page detection.
  * `page_renderer.py`: High-fidelity rasterizer rendering PDF pages to PIL Images/PNG bytes.
  * `ocr.py`: OCR fallback interface.
* **Synthetic Data Generator (`sample_data/generator.py`):**
  * Generated 3 realistic test packets covering all cardinal edge cases:
    * `synthetic_packet_01/`: Advised vs. Performed (Cancelled USG, Performed ECG with missing report, plus supplementary ECG report for re-audit).
    * `synthetic_packet_02/`: Date chronology conflict and ambiguous date format (`04/05/26`).
    * `synthetic_packet_03/`: Diagnostic evolution (suspected appendicitis $\rightarrow$ confirmed appendicitis) vs. left knee contradiction.
* **Gemma Extraction Adapter (`extraction/`):**
  * `base.py`: `BaseGemmaClient` abstract interface.
  * `prompts.py`: Structured clinical extraction prompts enforcing page citations and evidence binding.
  * `gemma_client.py`: Live GenAI/Gemma client with seamless fallback.
  * `mock_client.py`: Deterministic mock client providing instant, reproducible extractions for offline testing and CI.
  * `extractor.py`: Multi-document packet extractor coordinator.
* **Deterministic Verification Engine (`verification/`):**
  * `investigation_status.py`: Rule `RULE-INV-01` strictly enforcing Advised vs. Performed logic.
  * `chronology.py`: Rule `RULE-CHRON-01` and `RULE-DATE-02` checking date sequences and flagging format ambiguity.
  * `consistency.py`: Rule `RULE-CON-01` accepting diagnostic refinement while flagging material anatomical mismatches.
  * `required_docs.py`: Rule `RULE-REQ-01` checking mandatory discharge summary.
  * `engine.py`: Orchestrates all rule executions.
* **Resolution & Re-Audit Engine (`resolution/`, `audit/`):**
  * `draft_generator.py`: Generates pre-filled, grounded Retrieval Tickets and Clarification Memos.
  * `readiness.py`: Computes transparent packet readiness (`INCOMPLETE`, `REVIEW_REQUIRED`, `READY_FOR_HUMAN_REVIEW`).
  * `orchestrator.py`: Coordinates the full READ $\rightarrow$ VERIFY $\rightarrow$ RESOLVE pipeline.
  * `re_audit.py`: Differential engine that re-evaluates updated packets, marks resolved findings, and preserves audit history.
* **Automated Test Suite (`tests/`):**
  * `test_schemas.py`, `test_ingestion.py`, `test_rules.py`, `test_reaudit.py`: All 13 tests passing in pytest!
* **Streamlit UI Workspace (`app.py`, `ui/styles.py`):**
  * Built complete human-supervised audit workspace with split-screen PDF preview, jump-to-citation buttons, findings cards, editable draft workspace, staff override dialogs, and one-click re-audit triggers.
* **Documentation (`README.md`):**
  * Updated README with system architecture, edge case explanations, and quickstart commands.

### Entry 001 — 2026-10-09: Repository Cloning & Specification Baseline
* Cloned upstream repo `https://github.com/shoryabuilds/ClaimReady` to Desktop.
* Authored `rules.md`, `prd.md`, `design.md`, `architecture.md`, `memory.md`.

---

## 3. Current System State & File Tree

```
ClaimReady/
├── README.md               # Upstream repository description & quickstart
├── app.py                  # Interactive Streamlit Audit Workspace
├── rules.md                # Operating handbook & file usage rules
├── memory.md               # Persistent context log (this file)
├── prd.md                  # Comprehensive Product Requirements Document
├── design.md               # UI/UX & Interaction Design specification
├── architecture.md         # Technical architecture & schemas
├── requirements.txt        # Python dependencies
├── schemas/                # Pydantic data contracts
├── ingestion/              # PyMuPDF ingestion & page rendering
├── extraction/             # Gemma AI adapter & prompts
├── verification/           # Deterministic verification rules engine
├── resolution/             # Agentic draft generator
├── audit/                  # Audit orchestrator & differential re-audit
├── ui/                     # UI styles and components
├── sample_data/            # Synthetic test packets
└── tests/                  # 13 passing automated unit & integration tests
```

---

## 4. Next Steps
1. Synchronize all newly created files to `C:\Users\anish\Desktop\ClaimReady`.
2. Commit and push changes to GitHub (`origin/main`).
3. Run live Streamlit preview or browser verification.

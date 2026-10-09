import os
import streamlit as st
from ingestion.pdf_reader import PDFReader
from ingestion.page_renderer import PageRenderer
from audit.orchestrator import AuditOrchestrator
from audit.re_audit import ReAuditEngine
from schemas.common import ReadinessStatus, FindingStatus, SeverityLevel, ActionType
from ui.styles import CUSTOM_CSS

# Page Configuration
st.set_page_config(
    page_title="ClaimReady — Health Claim Integrity & Resolution Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
P1_PATH = os.path.join(SAMPLE_DIR, "synthetic_packet_01", "packet_advised_vs_performed.pdf")
P1_SUPP_PATH = os.path.join(SAMPLE_DIR, "synthetic_packet_01", "supplement_ecg_report.pdf")
P2_PATH = os.path.join(SAMPLE_DIR, "synthetic_packet_02", "packet_chronology_and_ambiguous_dates.pdf")
P3_PATH = os.path.join(SAMPLE_DIR, "synthetic_packet_03", "packet_diagnostic_evolution_and_conflict.pdf")

# Session State Initialization
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AuditOrchestrator()
    st.session_state.re_auditor = ReAuditEngine(st.session_state.orchestrator)
    st.session_state.page_renderer = PageRenderer()
    st.session_state.current_run = None
    st.session_state.facts = None
    st.session_state.parsed_docs = []
    st.session_state.active_doc_idx = 0
    st.session_state.active_page = 1
    st.session_state.active_file_paths = []

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 📋 Claim Packet Intake")
    scenario = st.selectbox(
        "Select Test Scenario / Packet:",
        [
            "Scenario 1: Advised vs Performed (Missing ECG, Cancelled USG)",
            "Scenario 2: Chronology Mismatch & Ambiguous Date (04/05/26)",
            "Scenario 3: Diagnostic Evolution vs Left Knee Contradiction",
            "Custom PDF Upload"
        ]
    )

    uploaded_files = []
    if scenario == "Custom PDF Upload":
        uploaded_files = st.file_uploader(
            "Upload Claim PDFs:",
            type=["pdf"],
            accept_multiple_files=True
        )

    if st.button("🚀 Run Pre-Submission Audit", use_container_width=True, type="primary"):
        with st.spinner("Executing READ -> VERIFY -> RESOLVE pipeline..."):
            if scenario.startswith("Scenario 1"):
                paths = [P1_PATH]
                run, facts, docs = st.session_state.orchestrator.audit_pdf_files(paths)
                st.session_state.active_file_paths = paths
            elif scenario.startswith("Scenario 2"):
                paths = [P2_PATH]
                run, facts, docs = st.session_state.orchestrator.audit_pdf_files(paths)
                st.session_state.active_file_paths = paths
            elif scenario.startswith("Scenario 3"):
                paths = [P3_PATH]
                run, facts, docs = st.session_state.orchestrator.audit_pdf_files(paths)
                st.session_state.active_file_paths = paths
            elif uploaded_files:
                file_items = [(f.read(), f.name) for f in uploaded_files]
                run, facts, docs = st.session_state.orchestrator.audit_pdf_bytes(file_items)
                st.session_state.active_file_paths = []
            else:
                st.warning("Please upload a PDF file first.")
                run, facts, docs = None, None, []

            if run:
                st.session_state.current_run = run
                st.session_state.facts = facts
                st.session_state.parsed_docs = docs
                st.session_state.active_doc_idx = 0
                st.session_state.active_page = 1
                st.success("Audit complete!")

    st.markdown("---")
    st.markdown("### 🔄 Re-Audit Engine")
    st.info("Upload supplementary reports to re-audit and resolve gaps.")

    if scenario.startswith("Scenario 1") and st.session_state.current_run:
        if st.button("➕ Add Missing ECG Report & Re-Audit", use_container_width=True):
            with st.spinner("Re-auditing with supplementary cardiology trace..."):
                updated_paths = [P1_PATH, P1_SUPP_PATH]
                new_run, _ = st.session_state.re_auditor.re_audit_files(
                    st.session_state.current_run,
                    updated_paths
                )
                _, facts, docs = st.session_state.orchestrator.audit_pdf_files(updated_paths)
                st.session_state.current_run = new_run
                st.session_state.facts = facts
                st.session_state.parsed_docs = docs
                st.session_state.active_file_paths = updated_paths
                st.success("Re-audit complete! ECG Report verified.")

    re_audit_uploads = st.file_uploader(
        "Upload Supplement PDF:",
        type=["pdf"],
        accept_multiple_files=True,
        key="re_audit_custom_uploader"
    )
    if re_audit_uploads and st.session_state.current_run:
        if st.button("Run Custom Re-Audit", use_container_width=True):
            with st.spinner("Re-evaluating verification rules..."):
                file_items = [(f.read(), f.name) for f in re_audit_uploads]
                new_run, _ = st.session_state.re_auditor.re_audit_bytes(
                    st.session_state.current_run,
                    file_items
                )
                _, facts, docs = st.session_state.orchestrator.audit_pdf_bytes(file_items)
                st.session_state.current_run = new_run
                st.session_state.facts = facts
                st.session_state.parsed_docs = docs
                st.success("Custom re-audit complete!")

    st.markdown("---")
    st.caption("🛡️ **System Core:** AI understands. Rules verify. Humans approve.")
    st.caption("⚙️ **Engine:** Gemma Adapter + Pure Python Rules Engine")

# --- AUTO-INITIALIZE ON FIRST LOAD ---
if st.session_state.current_run is None and os.path.exists(P1_PATH):
    run, facts, docs = st.session_state.orchestrator.audit_pdf_files([P1_PATH])
    st.session_state.current_run = run
    st.session_state.facts = facts
    st.session_state.parsed_docs = docs
    st.session_state.active_file_paths = [P1_PATH]

current_run = st.session_state.current_run
facts = st.session_state.facts
docs = st.session_state.parsed_docs

# --- MAIN CONTENT AREA ---
if current_run and facts:
    # Top Header & Status Bar
    patient_name = facts.patient.name if facts.patient and facts.patient.name else "Rahul Sharma"
    mrn = facts.patient.patient_id if facts.patient and facts.patient.patient_id else "CR-2026-9041"
    claim_id = facts.patient.claim_id if facts.patient and facts.patient.claim_id else facts.packet_id

    readiness = current_run.readiness_status
    if readiness == ReadinessStatus.READY_FOR_HUMAN_REVIEW:
        badge_html = '<span class="badge-ready">🟢 READY FOR HUMAN REVIEW</span>'
    elif readiness == ReadinessStatus.REVIEW_REQUIRED:
        badge_html = '<span class="badge-review">🟡 REVIEW REQUIRED (OPEN GAPS)</span>'
    else:
        badge_html = '<span class="badge-incomplete">🔴 INCOMPLETE AUDIT</span>'

    st.markdown(
        f"""
        <div class="cr-header">
            <div>
                <h1 class="cr-title">🛡️ ClaimReady &mdash; Pre-Submission Claim Integrity</h1>
                <div class="cr-tagline">Packet: <strong>{claim_id}</strong> | Patient: <strong>{patient_name}</strong> (MRN: {mrn}) | Audit Run: #{current_run.run_number}</div>
            </div>
            <div>
                {badge_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Explanation Banner
    st.info(f"**Readiness Assessment:** {current_run.readiness_explanation}")

    # Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Findings", current_run.total_findings)
    m_col2.metric("Open Gaps", current_run.open_findings, delta=None if current_run.open_findings == 0 else "- Action Required")
    m_col3.metric("Resolved Gaps", current_run.resolved_findings, delta=f"+{current_run.resolved_findings}" if current_run.resolved_findings > 0 else None)
    m_col4.metric("Staff Overrides", current_run.overridden_findings)

    st.markdown("---")

    # SPLIT-SCREEN WORKSPACE (Left: Viewer, Right: Findings & Resolution)
    col_left, col_right = st.columns([0.48, 0.52])

    # --- LEFT PANEL: INTERACTIVE DOCUMENT VIEWER ---
    with col_left:
        st.subheader("📄 Interactive Document Viewer")
        if docs:
            doc_names = [d.doc_name for d in docs]
            active_idx = st.selectbox(
                "Document:",
                range(len(doc_names)),
                format_func=lambda i: doc_names[i],
                index=st.session_state.active_doc_idx,
                key="doc_selector"
            )
            st.session_state.active_doc_idx = active_idx
            active_doc = docs[active_idx]

            # Page navigation controls
            max_pages = max(1, active_doc.page_count)
            p_col1, p_col2, p_col3 = st.columns([0.2, 0.6, 0.2])
            with p_col1:
                if st.button("◀ Prev", disabled=(st.session_state.active_page <= 1)):
                    st.session_state.active_page -= 1
                    st.rerun()
            with p_col2:
                page_sel = st.slider("Page", 1, max_pages, st.session_state.active_page, key="page_slider")
                if page_sel != st.session_state.active_page:
                    st.session_state.active_page = page_sel
                    st.rerun()
            with p_col3:
                if st.button("Next ▶", disabled=(st.session_state.active_page >= max_pages)):
                    st.session_state.active_page += 1
                    st.rerun()

            # Render Page Preview
            try:
                if active_doc.file_path and os.path.exists(active_doc.file_path):
                    page_img = st.session_state.page_renderer.render_page_to_image(
                        active_doc.file_path,
                        st.session_state.active_page,
                        dpi=140
                    )
                    st.image(page_img, use_container_width=True)
                else:
                    # Digital plain text view fallback
                    page_text = active_doc.get_page_text(st.session_state.active_page)
                    st.text_area("Extracted Page Text:", page_text, height=500)
            except Exception as e:
                st.error(f"Error rendering page: {e}")
        else:
            st.info("No documents loaded.")

    # --- RIGHT PANEL: AUDIT FINDINGS & AGENTIC RESOLUTION ---
    with col_right:
        st.subheader("🔍 Audit Findings & Action Workspace")

        tab_all, tab_open, tab_resolved = st.tabs([
            f"All ({len(current_run.findings)})",
            f"Open ({current_run.open_findings})",
            f"Resolved ({current_run.resolved_findings})"
        ])

        def render_finding_item(finding, idx):
            is_open = finding.status == FindingStatus.OPEN
            card_border = "#EF4444" if finding.severity == SeverityLevel.HIGH else "#F59E0B"
            if finding.status == FindingStatus.RESOLVED:
                card_border = "#10B981"

            sev_class = "severity-pill-high" if finding.severity == SeverityLevel.HIGH else "severity-pill-med"

            st.markdown(
                f"""
                <div class="finding-card" style="border-left: 4px solid {card_border};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <span class="{sev_class}">{finding.severity.value}</span>
                            <span class="rule-tag" style="margin-left: 6px;">{finding.rule_id}</span>
                            <strong style="margin-left: 8px; font-size: 14px;">{finding.title}</strong>
                        </div>
                        <div>
                            <span style="font-size: 12px; font-weight: 600; color: {'#10B981' if finding.status == FindingStatus.RESOLVED else '#DC2626'};">
                                {finding.status.value}
                            </span>
                        </div>
                    </div>
                    <div style="font-size: 13px; color: #475569; margin-bottom: 8px;">
                        {finding.description}
                    </div>
                """,
                unsafe_allow_html=True
            )

            # Evidence Box
            if finding.evidence:
                ev = finding.evidence[0]
                st.markdown(
                    f"""
                    <div class="evidence-quote">
                        &ldquo;{ev.evidence_quote}&rdquo;
                        <br><span style="font-size: 11px; color: #64748B;">&mdash; Source: {ev.source_document} (Page {ev.source_page})</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Jump to Page button
                btn_col1, _ = st.columns([0.4, 0.6])
                with btn_col1:
                    if st.button(f"🔎 View on Page {ev.source_page}", key=f"jump_{finding.finding_id}_{idx}"):
                        st.session_state.active_page = ev.source_page
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Resolution Workspace (if finding is OPEN)
            if is_open:
                # Find matching draft
                matching_draft = next((d for d in current_run.resolution_drafts if d.finding_id == finding.finding_id), None)
                if matching_draft:
                    with st.expander(f"✉️ Action Draft: {matching_draft.action_type.value} ({matching_draft.target_department})", expanded=False):
                        draft_body = st.text_area(
                            "Editable Draft Content:",
                            matching_draft.body,
                            height=160,
                            key=f"draft_body_{finding.finding_id}"
                        )
                        d_col1, d_col2 = st.columns([0.5, 0.5])
                        with d_col1:
                            if st.button("✅ Approve Action Draft", key=f"app_{finding.finding_id}"):
                                matching_draft.is_approved = True
                                matching_draft.body = draft_body
                                st.success(f"Draft approved for dispatch to {matching_draft.target_department}.")
                        with d_col2:
                            st.caption(f"Status: {'Approved' if matching_draft.is_approved else 'Pending Staff Review'}")

                # Manual Override
                with st.expander("🛡️ Staff Manual Override (Justification Required)", expanded=False):
                    override_reason = st.text_input("Reason for Override:", key=f"ov_reason_{finding.finding_id}")
                    if st.button("Confirm Override", key=f"btn_ov_{finding.finding_id}"):
                        if override_reason.strip():
                            finding.status = FindingStatus.OVERRIDDEN
                            finding.human_override_reason = override_reason
                            # Recalculate open findings
                            current_run.open_findings = sum(1 for f in current_run.findings if f.status == FindingStatus.OPEN)
                            current_run.overridden_findings = sum(1 for f in current_run.findings if f.status == FindingStatus.OVERRIDDEN)
                            st.success("Finding overridden with documented reason.")
                            st.rerun()
                        else:
                            st.error("Please provide a valid justification reason before overriding.")

        with tab_all:
            if not current_run.findings:
                st.success("No findings flagged! Packet documentation is clean.")
            else:
                for idx, f in enumerate(current_run.findings):
                    render_finding_item(f, idx)

        with tab_open:
            open_list = [f for f in current_run.findings if f.status == FindingStatus.OPEN]
            if not open_list:
                st.success("Zero open issues! All gaps have been resolved or staff-verified.")
            else:
                for idx, f in enumerate(open_list):
                    render_finding_item(f, idx)

        with tab_resolved:
            resolved_list = [f for f in current_run.findings if f.status in (FindingStatus.RESOLVED, FindingStatus.OVERRIDDEN)]
            if not resolved_list:
                st.info("No resolved findings yet. Upload missing documents to trigger re-audit.")
            else:
                for idx, f in enumerate(resolved_list):
                    render_finding_item(f, idx)
else:
    st.info("Click 'Run Pre-Submission Audit' in the sidebar to begin inspecting claim documentation.")

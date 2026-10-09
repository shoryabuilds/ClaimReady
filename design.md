# ClaimReady — UI/UX & Interaction Design Document

**Product:** ClaimReady  
**Interface Paradigm:** Human-Supervised Medical Audit Workspace  
**Framework:** Streamlit (Python) with custom CSS styling  

---

## 1. Design Philosophy & User Experience Principles

ClaimReady is an operational audit tool used by busy hospital billing executives and insurance desk personnel. The interface must prioritize **operational clarity**, **instant traceability**, and **cognitive comfort** over decorative marketing gimmicks.

### Core Experience Principles
1. **Side-by-Side Traceability:** Never display a finding in isolation. Every finding must immediately map to the source PDF document and page.
2. **Zero Ambiguity State Indicators:** Clear, high-contrast badges for finding severity and packet readiness.
3. **Frictionless Drafting:** Retrieval tickets and clarification memos are pre-populated with exact clinical context so staff can review, adjust, and approve in seconds.
4. **Calm Clinical Aesthetic:** Deep indigo/slate base, clean crisp cards, accessible contrast ratios, and purposeful alert colors.

---

## 2. Design System & Tokens

### 2.1 Color Palette
* **Brand Primary:** `#1E293B` (Slate Navy) / `#2563EB` (Cobalt Blue)
* **Surface Background:** `#F8FAFC` (Off-White / Cool Gray 50)
* **Card Surface:** `#FFFFFF` (Pure White) with subtle `#E2E8F0` border
* **Typography Primary:** `#0F172A` (Slate 900)
* **Typography Secondary:** `#475569` (Slate 600)
* **Status Badges & Alerts:**
  * **Critical / Missing:** `#EF4444` (Rose / Red 500) | Background: `#FEF2F2`
  * **Warning / Needs Review / Ambiguous:** `#F59E0B` (Amber 500) | Background: `#FFFBEB`
  * **Resolved / Verified:** `#10B981` (Emerald 500) | Background: `#ECFDF5`
  * **Gemma AI / Agentic Action:** `#6366F1` (Indigo 500) | Background: `#EEF2FF`

### 2.2 Typography & Hierarchy
* **Font Family:** Inter, system-ui, -apple-system, sans-serif
* **Header Hierarchy:**
  * H1: 24px, Bold — Page title & Claim Identifier
  * H2: 18px, Semi-Bold — Panel Headers (Findings, Document Viewer, Resolution)
  * H3: 15px, Medium — Card Titles & Action Types
  * Body: 13px–14px, Regular — Evidence text, memos, descriptions
  * Monospace / Meta: 12px — Rule IDs, timestamps, document file names

---

## 3. Screen Structure & Layout

The UI uses an efficient split-screen or multi-panel arrangement:

```
+---------------------------------------------------------------------------------------+
|  CLAIMREADY  |  Packet: CLM-84920 (Patient: Jane Doe)  |  Status: [REVIEW_REQUIRED]    |
+---------------------------------------------------------------------------------------+
|   LEFT PANEL (45% Width)               |   RIGHT PANEL (55% Width)                    |
|   Interactive Document Viewer          |   Audit Findings & Agentic Resolution        |
|                                        |                                              |
|  [Doc Selector: Discharge_Summary.pdf] |  [Filter: All (4) | Open (3) | Resolved (1)]  |
|  [Page < 2 of 4 >] [Zoom: 100%]        |                                              |
|                                        |  +-----------------------------------------+ |
|  +----------------------------------+  |  | [CRITICAL] Missing Investigation Report | |
|  |                                  |  |  | Investigation: Ultrasound Abdomen       | |
|  |  ...                             |  |  | Status: PERFORMED (Dated 14/08/2026)   | |
|  |  Patient was advised USG Abdomen |  |  | Evidence: "USG Abdomen performed on..." | |
|  |  which was performed on 14/08... |  |  | Source: Discharge Summary (Page 2)      | |
|  |  ...                             |  |  | [Rule: REQ-DOC-002]                     | |
|  |  [Highlit Evidence Snippet]      |  |  |                                         | |
|  |                                  |  |  | [Draft Retrieval Ticket] [Resolve/Edit] | |
|  +----------------------------------+  |  +-----------------------------------------+ |
|                                        |                                              |
|  [Upload Replacement/Additional PDF]  |  +-----------------------------------------+ |
|                                        |  | [RESOLVE WORKSPACE]                     | |
|                                        |  | Draft Request for Radiology Department: | |
|                                        |  | "Please provide USG report for..."      | |
|                                        |  | [Approve Ticket] [Override with Reason] | |
|                                        |  +-----------------------------------------+ |
+---------------------------------------------------------------------------------------+
|  FOOTER: Re-Audit Action Bar | [Run Re-Audit Engine] | Audit Run #2 (1 issue fixed)    |
+---------------------------------------------------------------------------------------+
```

---

## 4. Key Interactive Components

### 4.1 Claim Intake & Packet Uploader
* Multi-file drag and drop supporting single merged PDF or individual PDF files.
* Immediate client-side validation:
  * File size check ($\le 25\text{MB}$).
  * Corrupted PDF check.
  * Page count summary.
* "Start Audit" primary button triggering the READ $\rightarrow$ VERIFY pipeline with progress spinner.

### 4.2 Interactive Document Viewer
* Renders current PDF page using PyMuPDF image conversion (`pixmap.tobytes()`).
* Document tab switcher (`Admission Note`, `Discharge Summary`, `Lab Reports`, `Bills`).
* Page stepper (`< Prev`, `Next >`, `Jump to cited page`).
* Direct hyperlink from finding cards: clicking "View Evidence" automatically switches the document selector and jumps to the cited page.

### 4.3 Findings Panel
Each finding is rendered as an interactive card containing:
1. **Severity Badge:** High / Medium / Low / Escalation.
2. **Category Icon & Title:** e.g., `Missing Document`, `Date Chronology Conflict`, `Advised vs Performed Escalation`.
3. **Evidence Snippet Block:** Blockquote with the verbatim quote extracted by Gemma.
4. **Source Locator:** Document name and page number.
5. **Rule Annotation:** Rule ID (e.g. `RULE-CHRON-01`).
6. **Action Triggers:**
   * `Generate Draft Action`
   * `Mark as Human Overridden` (prompts for justification)

### 4.4 Agentic Resolution Workspace
When an action is triggered:
* Displays an editable card with pre-formatted draft:
  * **Retrieval Ticket** (targeted at Records/Lab/Radiology): Contains patient MRN, date of service, requested item, and reason.
  * **Clarification Memo** (targeted at Doctor/Nursing): Contains ambiguous phrasing and requests specific confirmation.
* Includes **Approve**, **Copy to Clipboard**, and **Save to Audit Record** controls.

### 4.5 Re-Audit & Readiness Dashboard
* Displays summary counters:
  * Total Findings Flagged
  * Open Issues
  * Human-Overridden Issues
  * Auto-Resolved Issues (after uploading supplement)
* Readiness banner:
  * 🔴 `INCOMPLETE` (Missing mandatory document or unreadable pages)
  * 🟡 `REVIEW_REQUIRED` (Uncertain extractions, open discrepancy)
  * 🟢 `READY_FOR_HUMAN_REVIEW` (All checks passed; ready for final human sign-off)
* Audit version switcher (e.g., Audit Run 1 vs. Audit Run 2) to see before-and-after progress.

---

## 5. Responsive Design & Usability Guidelines

* Built with Streamlit wide mode (`st.set_page_config(layout="wide")`).
* CSS styles cleanly isolated in custom CSS injection.
* Accessible color contrasts complying with WCAG AA standards.
* Fast rendering by caching rendered PDF pages using `@st.cache_data`.

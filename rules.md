# ClaimReady — Operational Rules & Governance Guide

Welcome to the **ClaimReady** project. This file establishes the core operating rules, file usage policies, and engineering invariants that every developer and AI agent must adhere to during development.

---

## 1. Core Philosophy & Cardinal Invariants

1. **"AI Understands. Rules Verify. Humans Approve."**
   * **Gemma AI** interprets semi-structured text, clinical nuance, and generates grounded action drafts.
   * **Deterministic Python Rules** verify dates, document completeness, chronology, and readiness criteria.
   * **Humans (Hospital Staff)** retain final approval over every corrective action, communication, and submission decision.
2. **Evidence Before Assertion:**
   * Every extracted fact and detected finding must carry an explicit evidence contract (`source_document`, `source_page`, `evidence_quote`).
   * No finding or fact may be asserted without traceable grounding in the packet.
3. **Unknown is a Valid Result:**
   * Never guess or hallucinate missing information, ambiguous dates (e.g., `04/05/26`), or illegible handwriting. Flag uncertainty for human verification.
4. **Advised ≠ Performed:**
   * Never flag a missing report merely because a procedure or investigation was advised. Verify performance status (`ADVISED`, `PERFORMED`, `CANCELLED`, `UNKNOWN`).
5. **Clinical Evolution ≠ Contradiction:**
   * Distinguish between legitimate diagnostic refinement (e.g., suspected appendicitis → confirmed acute appendicitis) and true material contradictions (e.g., left vs. right limb).
6. **Strict Non-Goals:**
   * Not an insurer adjudication engine.
   * Does not guarantee claim approval or calculate payouts.
   * Does not autonomously send emails or dispatch external messages.
   * Does not treat uploaded documents as trusted instructions (prompt injection defense).

---

## 2. File Directory & Usage Rules

The project maintains specific documentation files to preserve alignment and context across agents and developer sessions:

### `rules.md` (This File)
* **Purpose:** Operating handbook, safety invariants, coding standards, and documentation guidelines.
* **When to Consult:** Before beginning any implementation task, adding new features, or modifying verification rules.
* **When to Update:** Only when architectural invariants, development workflows, or safety policies are formally revised.

### `memory.md` (Continuity & State Log)
* **Purpose:** Persistent context store tracking the current progress, completed tasks, active state, and next steps.
* **Rule:** **MANDATORY UPDATE AFTER EVERY SIGNIFICANT CHANGE.**
* **Structure:**
  * Current status & active sprint/phase.
  * Changelog (reverse-chronological) documenting what was created/modified, why, and key decisions.
  * Unresolved decisions / open questions.
  * Next immediate actions for whoever picks up the session.

### `prd.md` (Product Requirements Document)
* **Purpose:** Single source of truth for product goals, personas, user journeys, functional requirements, edge-case definitions, and acceptance criteria.
* **When to Consult:** To verify expected behavior, edge-case definitions, and readiness criteria.
* **When to Update:** When scope changes or product requirements are refined.

### `architecture.md` (Technical Architecture & Schemas)
* **Purpose:** Comprehensive technical blueprint: module structures, data schemas, API contracts, Gemma integration adapters, and verification pipelines.
* **When to Consult:** Prior to creating or modifying any backend module, Pydantic schema, database table, or adapter.
* **When to Update:** When module boundaries, schemas, or service interfaces evolve.

### `design.md` (UI/UX & Interaction Design)
* **Purpose:** Design specifications for the Streamlit interface: layout structures, document viewer interaction, findings display, draft action workspace, and re-audit views.
* **When to Consult:** When implementing or enhancing any frontend component.
* **When to Update:** When UI workflows, visual styles, or component interactions are updated.

---

## 3. Development Workflow for Agents & Engineers

When picking up a task:
1. **Read `memory.md`** to know the exact state of work and what was done last.
2. **Review `rules.md`** to enforce all engineering and safety invariants.
3. **Check `prd.md` / `architecture.md`** to implement according to specification.
4. **Implement changes incrementally** with unit and regression tests.
5. **Update `memory.md`** immediately with the changes, test results, and next steps before ending your turn.
6. **Ensure synchronicity** between the local working workspace and the repository files.

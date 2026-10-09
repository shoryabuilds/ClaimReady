-- =====================================================================
-- ClaimReady — Supabase PostgreSQL Schema & Storage Setup Script
-- Run this script in your Supabase Project -> SQL Editor -> New Query
-- =====================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Claim Packets Table
CREATE TABLE IF NOT EXISTS packets (
    id TEXT PRIMARY KEY,
    claim_id TEXT,
    patient_mrn TEXT,
    patient_name TEXT,
    status TEXT DEFAULT 'PENDING_AUDIT',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Ingested Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    packet_id TEXT REFERENCES packets(id) ON DELETE CASCADE,
    doc_name TEXT NOT NULL,
    doc_type TEXT DEFAULT 'UNKNOWN',
    page_count INT DEFAULT 1,
    storage_path TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Extracted Facts Table (Native JSONB for clinical data & evidence)
CREATE TABLE IF NOT EXISTS extracted_facts (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    packet_id TEXT REFERENCES packets(id) ON DELETE CASCADE,
    clinical_data JSONB DEFAULT '{}'::JSONB,
    investigations JSONB DEFAULT '[]'::JSONB,
    document_types JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Audit Runs Table
CREATE TABLE IF NOT EXISTS audit_runs (
    id TEXT PRIMARY KEY,
    packet_id TEXT REFERENCES packets(id) ON DELETE CASCADE,
    run_number INT DEFAULT 1,
    readiness_status TEXT NOT NULL,
    readiness_explanation TEXT NOT NULL,
    total_findings INT DEFAULT 0,
    open_findings INT DEFAULT 0,
    resolved_findings INT DEFAULT 0,
    overridden_findings INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Audit Findings Table (Evidence JSONB with quote & page citations)
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES audit_runs(id) ON DELETE CASCADE,
    rule_id TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'OPEN',
    evidence JSONB DEFAULT '[]'::JSONB,
    suggested_action TEXT NOT NULL,
    human_override_reason TEXT,
    resolved_by_run_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Resolution Drafts Table (Retrieval Tickets & Clarification Memos)
CREATE TABLE IF NOT EXISTS resolution_drafts (
    id TEXT PRIMARY KEY,
    finding_id TEXT REFERENCES findings(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    target_department TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Storage Bucket for PDF Packets
INSERT INTO storage.buckets (id, name, public) 
VALUES ('claim-packets', 'claim-packets', true)
ON CONFLICT (id) DO NOTHING;

-- Storage Policy to Allow Public Read (or Authenticated)
CREATE POLICY "Public Read Claim Packets" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'claim-packets');

CREATE POLICY "Allow Upload Claim Packets" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'claim-packets');

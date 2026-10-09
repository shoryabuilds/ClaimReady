"""Custom CSS styles implementing ClaimReady clinical slate navy design tokens."""

CUSTOM_CSS = """
<style>
/* Main typography and container spacing */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Header Banner */
.cr-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: white;
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.cr-title {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #FFFFFF;
    margin: 0;
}

.cr-tagline {
    font-size: 13px;
    color: #94A3B8;
    margin-top: 4px;
}

/* Status Badges */
.badge-ready {
    background-color: #ECFDF5;
    color: #065F46;
    border: 1px solid #10B981;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-review {
    background-color: #FFFBEB;
    color: #92400E;
    border: 1px solid #F59E0B;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-incomplete {
    background-color: #FEF2F2;
    color: #991B1B;
    border: 1px solid #EF4444;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Finding Cards */
.finding-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
    transition: all 0.2s ease;
}

.finding-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.evidence-quote {
    background-color: #F8FAFC;
    border-left: 3px solid #6366F1;
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 13px;
    color: #334155;
    font-style: italic;
    border-radius: 0 6px 6px 0;
}

.rule-tag {
    background-color: #EEF2FF;
    color: #4F46E5;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: monospace;
}

.severity-pill-high {
    background-color: #FEE2E2;
    color: #DC2626;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
}

.severity-pill-med {
    background-color: #FEF3C7;
    color: #D97706;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
}

.draft-box {
    background: #F8FAFC;
    border: 1px dashed #6366F1;
    border-radius: 8px;
    padding: 14px;
    margin-top: 10px;
}
</style>
"""

from schemas.common import ReadinessStatus, FindingStatus, SeverityLevel
from schemas.findings import Finding

def assess_packet_readiness(findings: list[Finding]) -> tuple[ReadinessStatus, str]:
    """
    Computes packet readiness state and transparent explanation.
    
    CARDINAL INVARIANT:
    Never report ready if open gaps or unverified findings remain.
    """
    open_findings = [f for f in findings if f.status == FindingStatus.OPEN]
    high_sev = [f for f in open_findings if f.severity in (SeverityLevel.HIGH, SeverityLevel.ESCALATION)]

    if not findings:
        return (
            ReadinessStatus.READY_FOR_HUMAN_REVIEW,
            "All deterministic and clinical documentation checks passed. Packet is ready for final staff sign-off."
        )

    if not open_findings:
        return (
            ReadinessStatus.READY_FOR_HUMAN_REVIEW,
            f"All {len(findings)} identified findings have been resolved or staff-verified. Packet is ready for final submission review."
        )

    if high_sev:
        titles = ", ".join(f.title for f in high_sev[:2])
        return (
            ReadinessStatus.REVIEW_REQUIRED,
            f"Action Required: {len(high_sev)} critical documentation gap(s) detected ({titles}). Must be resolved before submission."
        )

    return (
        ReadinessStatus.REVIEW_REQUIRED,
        f"Review Required: {len(open_findings)} open documentation finding(s) or ambiguities require staff attention."
    )

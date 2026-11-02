from typing import Dict, Any, List


def get_color(verdict: str) -> str:
    """Maps verdict to formal institutional color."""
    mapping = {
        "Verified": "#15803D",
        "Contradicted": "#B91C1C",
        "Arithmetic Discrepancy": "#B91C1C",
        "Selective Disclosure": "#C2410C",
        "Unverified": "#475569"
    }
    return mapping.get(verdict, "#475569")


def get_status_badge(verdict: str) -> str:
    """Returns formal textual status badge (zero emojis)."""
    mapping = {
        "Verified": "[VERIFIED]",
        "Unverified": "[UNVERIFIED]",
        "Contradicted": "[CONTRADICTED]",
        "Arithmetic Discrepancy": "[ARITHMETIC DISCREPANCY]",
        "Selective Disclosure": "[SELECTIVE DISCLOSURE]"
    }
    return mapping.get(verdict, "[UNVERIFIED]")


def get_risk_level(verdict: str, confidence: int) -> str:
    """Computes formal risk severity tier (zero emojis)."""
    if verdict in ["Contradicted", "Arithmetic Discrepancy", "Selective Disclosure"]:
        if confidence >= 75:
            return "CRITICAL RISK"
        else:
            return "HIGH RISK"
    elif verdict == "Unverified":
        if confidence >= 75:
            return "MEDIUM RISK"
        else:
            return "MODERATE RISK"
    else:  # Verified
        return "LOW RISK"


def compute_corporate_scores(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes institutional portfolio metrics:
    - Greenwashing Exposure Score (0-100: Higher = Severe Misstatement Risk)
    - Assurance Readiness Index (0-100%: Higher = Audit Compliant)
    """
    if not results:
        return {
            "exposure_score": 0,
            "readiness_index": 0,
            "rating": "NO DATA",
            "findings_summary": {}
        }

    total = len(results)
    verified = sum(1 for r in results if r["verdict"] == "Verified")
    contradicted = sum(1 for r in results if r["verdict"] == "Contradicted")
    arithmetic_flaws = sum(1 for r in results if r["verdict"] == "Arithmetic Discrepancy")
    selective_disc = sum(1 for r in results if r["verdict"] == "Selective Disclosure")
    unverified = sum(1 for r in results if r["verdict"] == "Unverified")

    penalty_points = (contradicted * 30) + (arithmetic_flaws * 25) + (selective_disc * 20) + (unverified * 5)
    max_possible_penalty = total * 30
    exposure_score = min(100, round((penalty_points / max_possible_penalty) * 100)) if max_possible_penalty > 0 else 0
    readiness_index = round((verified / total) * 100) if total > 0 else 0

    if exposure_score >= 60:
        rating = "CRITICAL EXPOSURE / ADVERSE OPINION"
    elif exposure_score >= 35:
        rating = "HIGH REGULATORY EXPOSURE / QUALIFIED OPINION"
    elif exposure_score >= 15:
        rating = "MODERATE COMPLIANCE GAPS"
    else:
        rating = "STRONG ASSURANCE READINESS / UNQUALIFIED OPINION"

    return {
        "exposure_score": exposure_score,
        "readiness_index": readiness_index,
        "rating": rating,
        "total_claims": total,
        "verified_count": verified,
        "contradicted_count": contradicted,
        "arithmetic_flaw_count": arithmetic_flaws,
        "selective_disclosure_count": selective_disc,
        "unverified_count": unverified
    }


def build_result_object(
    claim: Dict[str, Any],
    judgment: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    math_audit: Dict[str, Any] = None,
    sbti_record: Dict[str, Any] = None,
    typology: Dict[str, Any] = None,
    taxonomy: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Assembles a complete, forensic audit workpaper record.
    """
    verdict = judgment["verdict"]
    confidence = judgment["confidence"]
    risk = get_risk_level(verdict, confidence)
    badge = get_status_badge(verdict)
    color = get_color(verdict)

    return {
        "claim_id": claim.get("claim_id", f"CLM-{claim.get('page', 1)}-{hash(claim.get('claim_text', '')) % 10000:04d}"),
        "claim_text": claim.get("claim_text", ""),
        "metric_type": claim.get("metric_type", "other"),
        "value": claim.get("value", "N/A"),
        "unit": claim.get("unit"),
        "year": claim.get("year", "N/A"),
        "page": claim.get("page", 1),
        "bbox": claim.get("bbox"),
        "verdict": verdict,
        "confidence": confidence,
        "risk_level": risk,
        "badge": badge,
        "color": color,
        "assurance_opinion": judgment.get("assurance_opinion", "Qualified / Material Findings"),
        "reasoning": judgment.get("reasoning", ""),
        "workpaper_action": judgment.get("workpaper_action", "Review raw supplier data."),
        "sources": evidence,
        "math_audit": math_audit or {},
        "sbti_record": sbti_record or {},
        "typology": typology or {},
        "taxonomy": taxonomy or {}
    }

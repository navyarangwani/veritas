import re
from typing import Dict, Any, List, Optional, Tuple


def parse_clean_number(val: Any) -> Optional[float]:
    """
    Parses numbers supporting Western (1,234,567.89) and Indian (1,23,45,678) comma notations,
    as well as percentage symbols and suffixes (k, M, Cr, Lakh).
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    if not s:
        return None

    # Handle negative in parentheses: (12,345) -> -12345
    is_negative = False
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()

    # Match multipliers
    multiplier = 1.0
    s_lower = s.lower()
    if "crore" in s_lower or " cr" in s_lower:
        multiplier = 1e7
    elif "lakh" in s_lower:
        multiplier = 1e5
    elif "billion" in s_lower or " bn" in s_lower:
        multiplier = 1e9
    elif "million" in s_lower or " mn" in s_lower:
        multiplier = 1e6

    # Extract digits, decimal point, commas
    clean = re.sub(r"[^\d.,\-+]", "", s)
    if not clean:
        return None

    # Strip commas
    clean = clean.replace(",", "")
    try:
        num = float(clean) * multiplier
        return -num if is_negative else num
    except ValueError:
        return None


def verify_ghg_scope_summation(
    scope1_val: Optional[float],
    scope2_val: Optional[float],
    reported_total: Optional[float],
    tolerance_pct: float = 2.0
) -> Dict[str, Any]:
    """
    Audits Scope 1 + Scope 2 = Total Reported Scope 1+2.
    Returns audit status, difference, and discrepancy alert.
    """
    if scope1_val is None or scope2_val is None or reported_total is None:
        return {
            "test_name": "GHG Scope 1+2 Summation Audit",
            "status": "Inconclusive",
            "detail": "Missing one or more required scope metrics for mathematical audit.",
            "is_discrepancy": False
        }

    calculated_total = scope1_val + scope2_val
    diff = abs(reported_total - calculated_total)
    pct_diff = (diff / calculated_total * 100) if calculated_total > 0 else 0.0

    if pct_diff <= tolerance_pct:
        return {
            "test_name": "GHG Scope 1+2 Summation Audit",
            "status": "Reconciled",
            "calculated_total": calculated_total,
            "reported_total": reported_total,
            "discrepancy_pct": round(pct_diff, 2),
            "is_discrepancy": False,
            "detail": f"Scope 1 ({scope1_val:,.1f}) + Scope 2 ({scope2_val:,.1f}) = {calculated_total:,.1f}, matching reported {reported_total:,.1f} (variance: {pct_diff:.2f}%)."
        }
    else:
        return {
            "test_name": "GHG Scope 1+2 Summation Audit",
            "status": "Failed / Discrepancy",
            "calculated_total": calculated_total,
            "reported_total": reported_total,
            "discrepancy_pct": round(pct_diff, 2),
            "is_discrepancy": True,
            "detail": f"Arithmetic Inconsistency: Reported total ({reported_total:,.1f}) diverges from calculated sum ({calculated_total:,.1f}) by {pct_diff:.2f}%."
        }


def verify_yoy_reduction_percentage(
    prior_year_val: Optional[float],
    current_year_val: Optional[float],
    claimed_reduction_pct: Optional[float],
    tolerance_pct: float = 2.5
) -> Dict[str, Any]:
    """
    Validates claimed percentage reduction against actual delta.
    Detects inflated progress or false claims.
    """
    if prior_year_val is None or current_year_val is None or claimed_reduction_pct is None:
        return {
            "test_name": "Year-over-Year Delta Verification",
            "status": "Inconclusive",
            "is_discrepancy": False,
            "detail": "Insufficient historical data points to recalculate percentage."
        }

    if prior_year_val <= 0:
        return {
            "test_name": "Year-over-Year Delta Verification",
            "status": "Inconclusive",
            "is_discrepancy": False,
            "detail": "Baseline value is zero or negative."
        }

    actual_pct_change = ((prior_year_val - current_year_val) / prior_year_val) * 100.0
    variance = abs(claimed_reduction_pct - actual_pct_change)

    if variance <= tolerance_pct:
        return {
            "test_name": "Year-over-Year Delta Verification",
            "status": "Reconciled",
            "actual_reduction_pct": round(actual_pct_change, 2),
            "claimed_reduction_pct": round(claimed_reduction_pct, 2),
            "variance": round(variance, 2),
            "is_discrepancy": False,
            "detail": f"Claimed reduction of {claimed_reduction_pct:.1f}% matches recalculated reduction of {actual_pct_change:.1f}%."
        }
    else:
        return {
            "test_name": "Year-over-Year Delta Verification",
            "status": "Exaggeration / Calculation Flaw",
            "actual_reduction_pct": round(actual_pct_change, 2),
            "claimed_reduction_pct": round(claimed_reduction_pct, 2),
            "variance": round(variance, 2),
            "is_discrepancy": True,
            "detail": f"Claimed {claimed_reduction_pct:.1f}% reduction, but arithmetic shows only {actual_pct_change:.1f}% (Variance: {variance:.1f}%)."
        }


def audit_claim_mathematics(claim: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forensic arithmetic pass on a single extracted claim object.
    Extracts embedded formulas, YoY percentages, and verifies sanity.
    """
    claim_text = claim.get("claim_text", "")
    val_raw = claim.get("value", "")
    
    # 1. Check for percentage claim in text
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:reduction|decrease|decline|drop|cut)", claim_text, re.IGNORECASE)
    prior_curr_match = re.search(
        r"(?:from|of)\s+([\d,]+(?:\.\d+)?)\s*(?:.*?)to\s+([\d,]+(?:\.\d+)?)",
        claim_text,
        re.IGNORECASE
    )

    if pct_match and prior_curr_match:
        claimed_pct = parse_clean_number(pct_match.group(1))
        prior_val = parse_clean_number(prior_curr_match.group(1))
        curr_val = parse_clean_number(prior_curr_match.group(2))
        
        return verify_yoy_reduction_percentage(prior_val, curr_val, claimed_pct)

    # 2. Scope 1 + 2 summation verification if data contains scope keywords
    if "scope 1" in claim_text.lower() and "scope 2" in claim_text.lower() and "total" in claim_text.lower():
        numbers = [parse_clean_number(n) for n in re.findall(r"[\d,]+(?:\.\d+)?", claim_text)]
        numbers = [n for n in numbers if n is not None and n > 0]
        if len(numbers) >= 3:
            # Assume two smaller are S1 & S2, largest is reported total
            numbers.sort()
            return verify_ghg_scope_summation(numbers[0], numbers[1], numbers[2])

    return {
        "test_name": "Forensic Arithmetic Scan",
        "status": "Nominal",
        "is_discrepancy": False,
        "detail": "No direct arithmetic claim formula detected; claim passes baseline sanity."
    }


def audit_extracted_tables_math(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Performs deterministic row-by-row and column-by-column reconciliations
    on extracted ESG tables (e.g. Scope 1 + Scope 2 + Scope 3 sums).
    """
    audit_findings = []
    
    for t in tables:
        category = t.get("category", "")
        rows = t.get("rows", [])
        headers = t.get("headers", [])
        table_id = t.get("table_id", "")
        page = t.get("page", 1)

        if category == "GHG_Emissions":
            scope1_val = None
            scope2_val = None
            total_val = None
            
            for row in rows:
                if not row:
                    continue
                row_label = str(row[0]).lower()
                # Find the first numerical cell in the row
                nums = [parse_clean_number(cell) for cell in row[1:] if parse_clean_number(cell) is not None]
                if not nums:
                    continue
                first_num = nums[0]

                if "scope 1" in row_label and "scope 2" not in row_label:
                    scope1_val = first_num
                elif "scope 2" in row_label:
                    scope2_val = first_num
                elif "total" in row_label and ("ghg" in row_label or "scope" in row_label or "emission" in row_label):
                    total_val = first_num

            if scope1_val and scope2_val and total_val:
                res = verify_ghg_scope_summation(scope1_val, scope2_val, total_val)
                res["table_id"] = table_id
                res["page"] = page
                res["evidence_type"] = "Table Deterministic Recalculation"
                audit_findings.append(res)

    return audit_findings

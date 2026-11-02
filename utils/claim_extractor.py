import json
import re
import os
import sys
import site
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.prompts import CLAIM_EXTRACTION_PROMPT
from utils.llm_provider import get_extraction_llm
from utils.math_integrity import parse_clean_number


def get_llm():
    return get_extraction_llm()


def clean_json_response(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)

    start = raw.find('[')
    end = raw.rfind(']')
    if start != -1 and end != -1 and end > start:
        return raw[start:end+1]

    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1 and end > start:
        return f"[{raw[start:end+1]}]"

    return "[]"


def extract_claims_from_chunk(chunk: dict, llm) -> List[Dict[str, Any]]:
    prompt = CLAIM_EXTRACTION_PROMPT.format(
        text=chunk["text"],
        page=chunk["page"]
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content if hasattr(response, "content") else str(response)
        cleaned = clean_json_response(raw)
        claims = json.loads(cleaned)

        if not isinstance(claims, list):
            return []

        valid_claims = []
        for idx, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            if "claim_text" not in claim or "value" not in claim:
                continue
            if not str(claim["claim_text"]).strip():
                continue
            
            page_num = chunk["page"]
            claim["claim_id"] = f"CLM-P{page_num}-{idx+1}"
            claim["page"] = page_num
            claim.setdefault("metric_type", "other")
            claim.setdefault("unit", None)
            claim.setdefault("year", None)
            claim.setdefault("scope_tag", "N/A")
            valid_claims.append(claim)

        return valid_claims

    except Exception as e:
        print(f"[Brain 2 — Extractor] Extraction error on page {chunk.get('page', 1)}: {e}")
        return []


def extract_claims_from_tables(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Forensic tabular claim extraction.
    Generates verified claim records directly from structured ESG tables.
    """
    table_claims = []
    
    for t in tables:
        page = t.get("page", 1)
        headers = t.get("headers", [])
        rows = t.get("rows", [])
        category = t.get("category", "General_ESG")
        bbox = t.get("bbox")
        table_id = t.get("table_id", f"TBL-P{page}")

        for r_idx, row in enumerate(rows):
            if not row or len(row) < 2:
                continue
            
            row_label = str(row[0]).strip()
            if not row_label or len(row_label) < 3:
                continue

            # Check if this row represents a meaningful metric
            for c_idx, cell in enumerate(row[1:], start=1):
                clean_num = parse_clean_number(cell)
                if clean_num is not None:
                    col_header = headers[c_idx] if c_idx < len(headers) else f"Col {c_idx}"
                    claim_text = f"Reported {row_label} for {col_header}: {cell} (Source: Table {table_id})."
                    
                    # Determine scope tag
                    scope_tag = "N/A"
                    if "scope 1" in row_label.lower():
                        scope_tag = "Scope 1"
                    elif "scope 2" in row_label.lower():
                        scope_tag = "Scope 2"
                    elif "scope 3" in row_label.lower():
                        scope_tag = "Scope 3"

                    metric_type = "emissions" if "GHG" in category else ("energy" if "Energy" in category else "other")
                    
                    table_claims.append({
                        "claim_id": f"CLM-{table_id}-R{r_idx+1}C{c_idx}",
                        "claim_text": claim_text,
                        "metric_type": metric_type,
                        "value": str(cell),
                        "unit": "tCO2e" if "GHG" in category else None,
                        "year": col_header if re.search(r"20\d\d|FY\d\d", col_header) else None,
                        "page": page,
                        "bbox": bbox,
                        "scope_tag": scope_tag,
                        "is_tabular": True
                    })

    print(f"[Brain 2 — Table Extractor] Extracted {len(table_claims)} claims directly from structured tables.")
    return table_claims


def extract_all_claims(chunks: list, tables: list = None) -> list:
    llm = get_llm()
    all_claims = []

    # 1. Text chunk extraction
    for i, chunk in enumerate(chunks):
        claims = extract_claims_from_chunk(chunk, llm)
        all_claims.extend(claims)

    # 2. Tabular claim extraction (merging forensic table data)
    if tables:
        table_claims = extract_claims_from_tables(tables)
        all_claims.extend(table_claims)

    print(f"[Brain 2 — Extractor] Aggregated {len(all_claims)} total raw and tabular claims.")
    return all_claims

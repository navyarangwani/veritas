import os
import time
import sys
import site
from typing import List, Dict, Any, Callable, Optional

# Ensure user site-packages are loaded in all execution environments
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.pdf_parser import extract_pages
from utils.table_parser import extract_tables_from_pdf
from utils.cleaner import clean_pages
from utils.chunker import chunk_pages
from utils.claim_extractor import extract_all_claims
from utils.claim_normalizer import normalize_claims
from utils.math_integrity import audit_claim_mathematics, audit_extracted_tables_math
from utils.registry_verifier import lookup_sbti_status, classify_greenwashing_risk, map_framework_taxonomy
from utils.strategy_brain import get_verification_plan
from utils.evidence_brain import get_evidence
from utils.judgment_brain import judge_claim
from utils.confidence_engine import build_result_object, compute_corporate_scores
from utils.llm_provider import get_llm as get_provider_llm
from langchain_core.messages import HumanMessage


def safe_print(msg: str):
    """Safely prints message avoiding encoding exceptions."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def detect_company_name(pages: list, llm) -> str:
    """
    Identifies company name from header pages.
    Falls back gracefully if LLM returns complex response.
    """
    sample_text = " ".join([p["text"] for p in pages[:2]])[:2000]

    company = ""
    prompt = f"""Read this excerpt from the first pages of a corporate sustainability / ESG report.
Extract ONLY the legal entity or company name (e.g. 'Tata Motors Limited', 'Infosys Limited', 'Apple Inc.').
Return just the company name, nothing else. No punctuation.

TEXT:
{sample_text}

Company name:"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content if hasattr(response, "content") else str(response)
        company = raw.strip().split("\n")[0].replace("Company name:", "").strip()
        if company and "{" not in company and len(company) < 60:
            safe_print(f"[INIT] Detected company: {company}")
            return company
    except Exception as e:
        safe_print(f"[INIT] Company detection notice: {e}")

    # Heuristic fallback parsing
    for line in sample_text.split("\n"):
        line_clean = line.strip()
        if any(term in line_clean.lower() for term in ["limited", "ltd", "inc", "corp", "industries", "plc"]):
            company = line_clean[:50]
            break

    if not company or "{" in company:
        lines = [l.strip() for l in sample_text.split("\n") if len(l.strip()) > 3]
        company = lines[0][:40] if lines else "Enterprise Entity Under Audit"

    safe_print(f"[INIT] Resolved Subject Entity: {company}")
    return company


def run_pipeline(
    pdf_path: str,
    progress_callback: Optional[Callable[[str], None]] = None,
    max_claims_to_audit: int = 15
) -> Dict[str, Any]:
    """
    Enterprise-grade autonomous ESG Forensic Assurance & Greenwashing Detection Pipeline.
    """
    def log(msg: str):
        safe_print(msg)
        if progress_callback:
            progress_callback(msg)

    start_time = time.time()
    log("[STAGE 1] Initializing Veritas ESG Enterprise Assurance Pipeline...")
    llm = get_provider_llm()

    # 1. Multi-modal Ingestion & Table Extraction
    log("[STAGE 1] Ingesting document layouts and bounding coordinates...")
    pages = extract_pages(pdf_path)
    if not pages:
        log("[ERROR] Unable to extract readable pages from PDF.")
        return {"results": [], "corporate_scores": {}, "tables": [], "sbti_status": {}}

    log(f"[STAGE 1] Extracting structured ESG tables & footnotes across {len(pages)} pages...")
    tables = extract_tables_from_pdf(pdf_path)
    cleaned_pages = clean_pages(pages)

    # 2. Company Identity & SBTi Registry Verification
    log("[STAGE 2] Resolving corporate entity & querying SBTi Target Registry...")
    company_name = detect_company_name(cleaned_pages, llm)
    sbti_record = lookup_sbti_status(company_name)
    log(f"   Entity: {company_name} | SBTi Status: {sbti_record.get('status', 'Unverified')}")

    # 3. Table Forensic Math Reconciliation
    log("[STAGE 2] Executing deterministic GHG Scope 1+2 & accounting sum checks...")
    table_math_audits = audit_extracted_tables_math(tables)
    log(f"   Reconciled {len(table_math_audits)} tabular accounting matrices.")

    # High-materiality scoping for large enterprise documents (50+ pages)
    if len(cleaned_pages) > 12:
        esg_keywords = [
            "emissions", "ghg", "scope 1", "scope 2", "scope 3", "renewable", 
            "mwh", "tco2", "tco2e", "water", "waste", "diversity", "workforce", 
            "brsr", "gri", "esrs", "intensity", "net zero", "carbon"
        ]
        scoped_pages = [
            p for p in cleaned_pages 
            if any(kw in p.get("text", "").lower() for kw in esg_keywords)
        ]
        if scoped_pages:
            log(f"[STAGE 2] Scoped {len(scoped_pages)} high-materiality disclosure pages out of {len(cleaned_pages)} total pages.")
            cleaned_pages = scoped_pages

    # 4. Claim Extraction & Deduplication
    log("[STAGE 3] Ingesting text segments & generating structured claim objects...")
    chunks = chunk_pages(cleaned_pages)
    raw_claims = extract_all_claims(chunks, tables=tables)

    if not raw_claims:
        log("[WARNING] No quantitative ESG disclosures detected.")
        return {
            "results": [],
            "corporate_scores": compute_corporate_scores([]),
            "tables": tables,
            "sbti_status": sbti_record,
            "company_name": company_name
        }

    claims = normalize_claims(raw_claims)
    log(f"[STAGE 3] Deduplicated {len(raw_claims)} raw entries into {len(claims)} verifiable claims.")

    # Filter to priority ESG domains and cap at max_claims_to_audit
    priority_metrics = ["emissions", "energy", "water", "waste", "diversity", "governance"]
    claims = [c for c in claims if c.get("metric_type") in priority_metrics or c.get("is_tabular")]
    claims = claims[:max_claims_to_audit]
    log(f"[STAGE 3] Prioritized {len(claims)} high-materiality claims for forensic testing.")

    # 5. Multi-Agent Cross-Examination Loop
    results = []
    for idx, claim in enumerate(claims, start=1):
        claim["company"] = company_name
        claim_text = claim.get("claim_text", "")
        metric_type = claim.get("metric_type", "other")
        log(f"[STAGE 4] Auditing Claim {idx}/{len(claims)}: {claim_text[:60]}...")

        # A. Deterministic Math Audit
        math_audit = audit_claim_mathematics(claim)
        math_flag = math_audit.get("is_discrepancy", False)

        # B. Statutory Framework Mapping (CSRD, GRI, SEBI, GHG Protocol)
        taxonomy = map_framework_taxonomy(metric_type, claim_text)

        # C. Greenwashing Typology Analysis
        typology = classify_greenwashing_risk(claim_text, metric_type, math_flag, sbti_record)

        # D. Strategy Brain: Targeted Search Planning
        plan = get_verification_plan(claim, llm)
        queries = plan.get("search_queries", [f"{company_name} {metric_type} report"])

        # E. Evidence Brain: Multi-Source Retrieval (PR wires filtered)
        evidence = get_evidence(queries, company=company_name)

        # F. Judgment Brain: Senior Assurance Partner Verdict
        pre_audit_summary = f"Math Status: {math_audit.get('status', 'Nominal')}. SBTi Status: {sbti_record.get('status')}. Typology: {typology.get('typology') if typology else 'None'}."
        judgment = judge_claim(claim, evidence, pre_audit_summary=pre_audit_summary)

        # G. Assemble Complete Audit Workpaper Object
        result_obj = build_result_object(
            claim=claim,
            judgment=judgment,
            evidence=evidence,
            math_audit=math_audit,
            sbti_record=sbti_record,
            typology=typology,
            taxonomy=taxonomy
        )
        results.append(result_obj)

    # 6. Corporate Risk Scoring & Executive Portfolio Analytics
    corporate_scores = compute_corporate_scores(results)
    elapsed = round(time.time() - start_time, 1)
    log(f"[COMPLETE] Assurance audit completed in {elapsed}s. Overall Rating: {corporate_scores.get('rating')}")

    return {
        "results": results,
        "corporate_scores": corporate_scores,
        "tables": tables,
        "table_math_audits": table_math_audits,
        "sbti_status": sbti_record,
        "company_name": company_name,
        "audit_metadata": {
            "elapsed_seconds": elapsed,
            "total_pages": len(pages),
            "total_tables": len(tables),
            "standard_applied": "ISSA 5000 / ISAE 3000 Pre-Assurance"
        }
    }

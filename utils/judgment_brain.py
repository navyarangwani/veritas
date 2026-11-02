import json
import re
import os
import sys
import site
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.prompts import JUDGMENT_PROMPT
from utils.llm_provider import get_llm as get_provider_llm


def get_llm():
    return get_provider_llm()


def format_evidence_for_prompt(evidence: List[Dict[str, Any]]) -> str:
    if not evidence:
        return "No independent external evidence retrieved."

    formatted = []
    for i, e in enumerate(evidence, 1):
        cred = e.get("credibility", "Tier 3")
        formatted.append(
            f"[Source {i} — {cred}]\n"
            f"Title: {e.get('title', 'Unknown')}\n"
            f"URL: {e.get('url', 'Unknown')}\n"
            f"Snippet: {e.get('snippet', 'No content available')}\n"
        )
    return "\n---\n".join(formatted)


def extract_json_from_response(raw: str) -> dict:
    """Aggressively extracts and parses JSON from LLM response."""
    raw = raw.strip()
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)

    start = raw.find('{')
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    end = -1
    for i in range(start, len(raw)):
        if raw[i] == '{':
            depth += 1
        elif raw[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        end = raw.rfind('}')
        if end == -1 or end <= start:
            raise ValueError("Malformed JSON in response")

    json_str = raw[start:end+1]
    return json.loads(json_str)


def judge_claim(
    claim: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    pre_audit_summary: str = "Standard pre-audit check nominal."
) -> Dict[str, Any]:
    """
    Brain 5 — Senior Assurance Partner Agent.
    Issues formal audit opinion, confidence rating, and workpaper action.
    """
    llm = get_llm()
    formatted_evidence = format_evidence_for_prompt(evidence)
    company = claim.get("company", "the company")

    prompt = JUDGMENT_PROMPT.format(
        claim_text=claim.get("claim_text", ""),
        company=company,
        evidence_text=formatted_evidence,
        pre_audit_summary=pre_audit_summary
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content if hasattr(response, "content") else str(response)
        judgment = extract_json_from_response(raw)

        # Sanitize fields
        verdict = judgment.get("verdict", "Unverified")
        if verdict not in ["Verified", "Contradicted", "Unverified", "Selective Disclosure", "Arithmetic Discrepancy"]:
            if "contradict" in verdict.lower() or "discrepan" in verdict.lower():
                verdict = "Contradicted"
            elif "verif" in verdict.lower():
                verdict = "Verified"
            else:
                verdict = "Unverified"

        confidence = judgment.get("confidence", 70)
        try:
            confidence = int(confidence)
            confidence = max(0, min(100, confidence))
        except (ValueError, TypeError):
            confidence = 70

        return {
            "verdict": verdict,
            "confidence": confidence,
            "assurance_opinion": judgment.get("assurance_opinion", "Qualified / Material Findings"),
            "reasoning": judgment.get("reasoning", "Evidence inconclusive; requires further testing."),
            "workpaper_action": judgment.get("workpaper_action", "Request primary source documentation.")
        }

    except Exception as e:
        print(f"[Brain 5 — Judgment] Evaluation notice: {e}. Generating fallback audit assessment.")
        
        # Smart heuristic fallback based on pre-audit findings
        if "Discrepancy" in pre_audit_summary:
            return {
                "verdict": "Arithmetic Discrepancy",
                "confidence": 92,
                "assurance_opinion": "Adverse / High Greenwashing Exposure",
                "reasoning": f"Mathematical audit failed: {pre_audit_summary}",
                "workpaper_action": "Flag as material misstatement for Engagement Partner review."
            }
        elif "Unsubstantiated" in pre_audit_summary:
            return {
                "verdict": "Contradicted",
                "confidence": 85,
                "assurance_opinion": "Qualified / Material Exception",
                "reasoning": f"Target not validated by authoritative registries: {pre_audit_summary}",
                "workpaper_action": "Request official validation certificate from management."
            }

        return {
            "verdict": "Unverified",
            "confidence": 55,
            "assurance_opinion": "Inconclusive / Insufficient Evidence",
            "reasoning": "External corroboration unavailable from primary statutory repositories.",
            "workpaper_action": "Issue confirmation letter to client ESG steering committee."
        }

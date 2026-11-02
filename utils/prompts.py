CLAIM_EXTRACTION_PROMPT = """You are a Senior ESG Assurance Specialist at a Big 4 accounting firm auditing a corporate sustainability report.

Analyze this document segment and extract all quantitative, measurable, or specific ESG claims, targets, and performance disclosures.

Pay special attention to:
- GHG Scope 1, Scope 2 (market/location-based), and Scope 3 emissions
- Renewable energy shares and absolute consumption (MWh / GJ)
- Water withdrawal, consumption, and recycling rates
- Waste diversion from landfills and circularity metrics
- Workforce gender diversity, board composition, and safety frequency rates
- Net-Zero, Carbon Neutrality, and Science-Based Targets (SBTi) commitments
- Indian number formats (e.g. 1,23,45,678 or 52.4 Lakh / Crore) are valid numbers.

Return a valid JSON array of objects. Each object must have these exact fields:
- claim_text: the verbatim claim sentence from the text
- metric_type: one of "emissions", "energy", "water", "waste", "diversity", "governance", "other"
- value: the specific metric quantity or percentage
- unit: the unit of measurement (e.g. "tCO2e", "MWh", "%", "million liters", "metric tons") or null
- year: the fiscal year referenced (e.g. "2024", "FY23", "2030 target") or null
- scope_tag: "Scope 1", "Scope 2", "Scope 3", or "N/A"

Return ONLY the raw JSON array. No conversational text. No markdown code fences.
If no measurable ESG claims exist in this text, return []

TEXT:
{text}

PAGE: {page}

JSON array:"""


STRATEGY_PROMPT = """You are an ESG Audit Partner designing a verification strategy under ISSA 5000 standards.

Entity Under Audit: {company}
Claim to Verify: {claim_text}
Metric Classification: {metric_type}

Design 2 to 3 targeted search queries to cross-examine this claim against independent external sources.
Focus queries on:
1. Statutory regulatory disclosures (e.g., SEC 10-K, SEBI BRSR Core, EPA FLIGHT, EU ESEF filings)
2. Third-party registries (e.g., Science Based Targets initiative (SBTi), CDP Climate Disclosure)
3. Independent investigative journalism, NGO watchdogs (e.g., InfluenceMap, Carbon Tracker), or environmental enforcement penalties.

Always include the company name in each query. Exclude company marketing materials and press releases.

Return a valid JSON object:
{{"search_queries": ["query 1", "query 2", "query 3"], "reasoning": "brief description of verification hypothesis"}}

Return ONLY the JSON object. No explanation. No markdown."""


JUDGMENT_PROMPT = """You are a Senior Sustainability Assurance Partner at a Big 4 firm evaluating evidence under ISSA 5000 / ISAE 3000.

COMPANY CLAIM:
{claim_text}

COMPANY NAME:
{company}

EXTERNAL EVIDENCE RETRIEVED:
{evidence_text}

ARITHMETIC & REGISTRY PRE-AUDIT RESULTS:
{pre_audit_summary}

EVALUATION RULES:
1. Compare the claim strictly against the explicit retrieved evidence and pre-audit findings.
2. If evidence contradicts the stated figures or proves baseline manipulation, issue "Contradicted".
3. If company reports Scope 1/2 as "total emissions" while omitting Scope 3, or hides offsets, flag as "Selective Disclosure".
4. If underlying arithmetic does not reconcile, flag as "Arithmetic Discrepancy".
5. If independent evidence confirms the metric from reliable third-party sources, issue "Verified".
6. If evidence is missing, fragmented, or ambiguous, issue "Unverified".

Return a valid JSON object with these exact fields:
{{
  "verdict": "Verified | Unverified | Contradicted | Selective Disclosure | Arithmetic Discrepancy",
  "confidence": 0_to_100,
  "assurance_opinion": "Unqualified / Compliant | Qualified / Material Exception | Adverse / High Greenwashing Exposure | Inconclusive / Insufficient Evidence",
  "reasoning": "3-4 concise sentences detailing the forensic justification and evidence evaluation.",
  "workpaper_action": "Actionable instruction for the audit engagement team (e.g. 'Request raw meter logs and utility invoices for Scope 2 market-based calculations')."
}}

Return ONLY the JSON. No markdown code blocks."""

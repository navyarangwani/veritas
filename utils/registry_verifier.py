import re
from typing import Dict, Any, List, Optional


# Authoritative SBTi (Science Based Targets initiative) corporate target database snapshot
SBTI_REGISTRY_DATABASE = {
    "infosys": {
        "company_name": "Infosys Limited",
        "status": "Targets Set",
        "near_term_status": "Approved 1.5°C",
        "net_zero_target": "2040 (Approved Net-Zero)",
        "scope3_covered": True,
        "detail": "Near-term target to reduce Scope 1 and 2 GHG emissions 75% by 2030 from a 2020 base year, and reduce absolute Scope 3 GHG emissions 30%."
    },
    "tata motors": {
        "company_name": "Tata Motors Limited",
        "status": "Committed",
        "near_term_status": "Committed to 1.5°C",
        "net_zero_target": "2045 (Commercial Vehicles) / 2040 (Passenger)",
        "scope3_covered": True,
        "detail": "Committed to net-zero GHG emissions across value chain. Targets under formal validation by SBTi."
    },
    "mahindra": {
        "company_name": "Mahindra & Mahindra Ltd.",
        "status": "Targets Set",
        "near_term_status": "Approved 1.5°C",
        "net_zero_target": "2040 (Approved Net-Zero)",
        "scope3_covered": True,
        "detail": "Approved science-based targets for Scope 1, Scope 2, and Scope 3."
    },
    "apple": {
        "company_name": "Apple Inc.",
        "status": "Targets Set",
        "near_term_status": "Approved 1.5°C",
        "net_zero_target": "2030 across entire supply chain",
        "scope3_covered": True,
        "detail": "Approved 1.5°C trajectory covering product life cycle and supply chain Scope 3."
    },
    "reliance": {
        "company_name": "Reliance Industries Limited",
        "status": "No Formal SBTi Submission",
        "near_term_status": "Self-declared Target",
        "net_zero_target": "2035 (Self-declared)",
        "scope3_covered": False,
        "detail": "Internal corporate commitment to Net Carbon Zero by 2035; not formally validated or registered on SBTi registry."
    },
    "shell": {
        "company_name": "Shell plc",
        "status": "Removed / Inactive",
        "near_term_status": "Target Revoked/Weakened",
        "net_zero_target": "2050 (Weakened 2030 interim target)",
        "scope3_covered": False,
        "detail": "Weakened its 2030 carbon intensity reduction target from 20% to 15-20% and retired its 2035 45% reduction target."
    }
}


# Recognized International Greenwashing Typology definitions (EU Green Claims Directive & Planet Tracker)
GREENWASHING_TYPOLOGIES = {
    "Selective Disclosure": {
        "description": "Reporting Scope 1 and Scope 2 operational emissions while completely omitting Scope 3 supply chain emissions, which typically represent 80-95% of total carbon footprint.",
        "severity": "High",
        "regulatory_risk": "EU CSRD ESRS E1 Non-Compliance / SEC Climate Rule Exposure"
    },
    "Greenrinsing": {
        "description": "Regularly modifying baseline comparison years or weakening long-term sustainability targets before their scheduled maturity date without restatement.",
        "severity": "High",
        "regulatory_risk": "ESMA / ISSA 5000 Material Misstatement Risk"
    },
    "Greenlighting": {
        "description": "Spotlighting an isolated eco-friendly pilot project or product line in prominent visuals while the vast majority of operations remain fossil-intensive.",
        "severity": "Medium",
        "regulatory_risk": "UK CMA Green Claims Code / FTC Green Guides Warning"
    },
    "Unsubstantiated Offsetting": {
        "description": "Claiming 'Carbon Neutrality' through purchased voluntary carbon avoidance credits rather than demonstrated absolute emission reductions.",
        "severity": "High",
        "regulatory_risk": "EU Green Claims Directive / Direct Regulatory Ban"
    },
    "Greenshifting": {
        "description": "Shifting responsibility for environmental impacts onto consumers or suppliers through lifestyle calculators rather than supply-chain decarbonization.",
        "severity": "Low",
        "regulatory_risk": "Brand Reputation / Advisory Warning"
    },
    "Greencrowding": {
        "description": "Hiding in an industry alliance or average to disguise sluggish progress under the banner of collective initiative.",
        "severity": "Medium",
        "regulatory_risk": "Antitrust / Benchmarking Exception"
    }
}


def lookup_sbti_status(company_name: str) -> Dict[str, Any]:
    """
    Cross-references company name against the SBTi target database.
    """
    clean_name = company_name.lower().strip()
    
    for key, data in SBTI_REGISTRY_DATABASE.items():
        if key in clean_name or clean_name in key:
            return {
                "matched": True,
                "registry": "Science Based Targets initiative (SBTi)",
                **data
            }
            
    # Generic fallback
    return {
        "matched": False,
        "registry": "Science Based Targets initiative (SBTi)",
        "company_name": company_name,
        "status": "Unverified on SBTi Registry",
        "near_term_status": "Unknown",
        "net_zero_target": "No independent record found",
        "scope3_covered": None,
        "detail": f"No public SBTi validation record found for '{company_name}'. Requires engagement team inquiry."
    }


def classify_greenwashing_risk(
    claim_text: str,
    metric_type: str,
    math_discrepancy: bool,
    sbti_record: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Classifies a claim into standard greenwashing typologies based on text patterns,
    mathematical anomalies, and registry status.
    """
    text_lower = claim_text.lower()
    
    # 1. Math Discrepancy -> Greenrinsing or Calculation Flaw
    if math_discrepancy:
        return {
            "typology": "Greenrinsing",
            **GREENWASHING_TYPOLOGIES["Greenrinsing"],
            "rationale": "Claimed reduction rate or scope summation does not reconcile mathematically with underlying data."
        }

    # 2. Carbon Neutrality via Offsets -> Unsubstantiated Offsetting
    if any(k in text_lower for k in ["carbon neutral", "net zero", "climate positive", "100% offset"]):
        if any(k in text_lower for k in ["offset", "carbon credit", "reforestation credit", "vcs", "verra"]):
            return {
                "typology": "Unsubstantiated Offsetting",
                **GREENWASHING_TYPOLOGIES["Unsubstantiated Offsetting"],
                "rationale": "Claim relies heavily on voluntary offsets rather than absolute emissions abatement."
            }

    # 3. Scope 1 & 2 without Scope 3 -> Selective Disclosure
    if any(k in text_lower for k in ["scope 1", "scope 2"]) and "scope 3" not in text_lower:
        if any(k in text_lower for k in ["total emissions", "our footprint", "company emissions", "overall footprint"]):
            return {
                "typology": "Selective Disclosure",
                **GREENWASHING_TYPOLOGIES["Selective Disclosure"],
                "rationale": "Claim refers to 'total' or 'overall' corporate emissions while omitting Scope 3 supply chain."
            }

    # 4. Net Zero Target when SBTi is not verified or removed
    if any(k in text_lower for k in ["net zero by 20", "sbti", "science based"]):
        if sbti_record.get("matched") and sbti_record.get("status") in ["Removed / Inactive", "No Formal SBTi Submission"]:
            return {
                "typology": "Greenrinsing",
                **GREENWASHING_TYPOLOGIES["Greenrinsing"],
                "rationale": f"Company advertises climate targets, but official SBTi registry records status as: {sbti_record.get('status')}."
            }

    # 5. Spotlighting minor eco pilot -> Greenlighting
    if any(k in text_lower for k in ["planted", "seedlings", "pilot program", "green packaging", "paper cups", "plastic bottles"]):
        if any(k in text_lower for k in ["sustainable", "eco-friendly", "committed to green", "leading the way"]):
            return {
                "typology": "Greenlighting",
                **GREENWASHING_TYPOLOGIES["Greenlighting"],
                "rationale": "Promoting isolated low-materiality environmental activities to project broader sustainability leadership."
            }

    return None


def map_framework_taxonomy(metric_type: str, claim_text: str) -> Dict[str, str]:
    """
    Maps an ESG metric to the major statutory disclosure frameworks:
    CSRD (ESRS), GRI Standards, and SEBI BRSR Core.
    """
    text_lower = claim_text.lower()
    
    if metric_type == "emissions" or "ghg" in text_lower or "carbon" in text_lower:
        return {
            "csrd_esrs": "ESRS E1 (Climate Change — Scopes 1, 2, 3)",
            "gri_standard": "GRI 305 (Emissions)",
            "sebi_brsr": "Principle 6 — GHG Emissions & Reduction Initiatives",
            "ghg_protocol": "Scope 1 Direct / Scope 2 Indirect / Scope 3 Value Chain"
        }
    elif metric_type == "energy" or "renewable" in text_lower or "mwh" in text_lower:
        return {
            "csrd_esrs": "ESRS E1-5 (Energy Consumption & Renewable Mix)",
            "gri_standard": "GRI 302 (Energy)",
            "sebi_brsr": "Principle 6 — Energy Consumption & Renewable Share",
            "ghg_protocol": "Scope 2 Category — Purchased Electricity/Heat"
        }
    elif metric_type == "water" or "effluent" in text_lower:
        return {
            "csrd_esrs": "ESRS E3 (Water & Marine Resources)",
            "gri_standard": "GRI 303 (Water and Effluents)",
            "sebi_brsr": "Principle 6 — Water Withdrawal & Recycled Proportion",
            "ghg_protocol": "Environmental Operational Metric"
        }
    elif metric_type == "waste" or "circular" in text_lower:
        return {
            "csrd_esrs": "ESRS E5 (Resource Use & Circular Economy)",
            "gri_standard": "GRI 306 (Waste)",
            "sebi_brsr": "Principle 6 — Hazardous & Non-Hazardous Waste Disposal",
            "ghg_protocol": "Scope 3 Category 5 — Waste Generated in Operations"
        }
    elif metric_type == "diversity" or "gender" in text_lower or "female" in text_lower:
        return {
            "csrd_esrs": "ESRS S1 (Own Workforce — Diversity & Equality)",
            "gri_standard": "GRI 405 (Diversity and Equal Opportunity)",
            "sebi_brsr": "Principle 3 — Workforce Diversity & Equal Opportunity",
            "ghg_protocol": "Social Pillar KPI"
        }
    else:
        return {
            "csrd_esrs": "ESRS General Disclosures (G1 / S1 / E1)",
            "gri_standard": "GRI 2 (General Disclosures)",
            "sebi_brsr": "BRSR Section B & C Overview",
            "ghg_protocol": "Cross-Cutting KPI"
        }

import sys
import os
import site

# Ensure user site-packages are loaded in all runtime environments
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import tempfile
import json
import pandas as pd
from utils.agent_orchestrator import run_pipeline
from utils.report_generator import generate_audit_pdf, generate_audit_excel
from utils.confidence_engine import get_color, get_status_badge

# ── PAGE CONFIGURATION ────────────────────────────────────────────────
st.set_page_config(
    page_title="VERITAS ESG | Institutional Assurance Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── FORMAL INSTITUTIONAL STYLING (ZERO GRADIENTS, STRICT MONOCHROME/SOLID) ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
    }
    
    /* Strict removal of gradients and rounded bubbly design */
    .brand-header {
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #0F172A;
        text-transform: uppercase;
        margin-bottom: 0px;
        border-bottom: 2px solid #0F172A;
        padding-bottom: 8px;
    }
    .brand-subhead {
        font-size: 0.82rem;
        font-family: 'IBM Plex Mono', monospace;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 6px;
        margin-bottom: 1.5rem;
    }
    
    /* Institutional Metric Tiles (Solid, flat, formal borders) */
    .metric-tile {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 2px;
        padding: 1rem 1.2rem;
        text-align: left;
    }
    .metric-tile-label {
        font-size: 0.72rem;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .metric-tile-val {
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'IBM Plex Sans', sans-serif;
        color: #0F172A;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .metric-tile-sub {
        font-size: 0.75rem;
        color: #64748B;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Formal Status Badges */
    .badge-verified {
        background-color: #DCFCE7;
        color: #14532D;
        border: 1px solid #86EFAC;
        padding: 2px 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-exception {
        background-color: #FEE2E2;
        color: #7F1D1D;
        border: 1px solid #FCA5A5;
        padding: 2px 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-amber {
        background-color: #FFEDD5;
        color: #7C2D12;
        border: 1px solid #FDBA74;
        padding: 2px 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-neutral {
        background-color: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        padding: 2px 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Flat Button Styling */
    .stButton>button {
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
    }
    .stButton>button:hover {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #1E293B !important;
    }

    /* Progress bar formal solid */
    .stProgress > div > div > div > div {
        background-color: #0F172A !important;
    }

    /* Expander formal card */
    .streamlit-expanderHeader {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 2px !important;
        background-color: #FFFFFF !important;
    }

    /* Footer */
    .formal-footer {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: #64748B;
        text-align: center;
        border-top: 1px solid #CBD5E1;
        padding-top: 1.5rem;
        margin-top: 3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INITIALIZATION ─────────────────────────────────────
if "audit_data" not in st.session_state:
    st.session_state.audit_data = None
if "hitl_notes" not in st.session_state:
    st.session_state.hitl_notes = {}
if "hitl_statuses" not in st.session_state:
    st.session_state.hitl_statuses = {}

# ── SIDEBAR CONFIGURATION (INSTITUTIONAL AUDIT PARAMETERS) ───────────
with st.sidebar:
    st.markdown("### VERITAS ASSURANCE")
    st.caption("FORENSIC ESG & GREENWASHING INTELLIGENCE")
    st.markdown("---")

    st.markdown("#### ENGAGEMENT PARAMETERS")
    audit_standard = st.selectbox(
        "Assurance Standard",
        [
            "ISSA 5000 / ISAE 3000 (Limited Assurance)",
            "CSRD ESRS Directive Mandate (EU)",
            "SEBI BRSR Core Assurance Standard (India)",
            "SEC Climate Disclosure Rule Standard (US)"
        ]
    )

    materiality_threshold = st.select_slider(
        "Materiality Threshold",
        options=["Strict Forensic (2%)", "Standard Engagement (5%)", "High Tolerance (10%)"],
        value="Standard Engagement (5%)"
    )

    max_claims = st.slider("Scope Limit (Max Disclosures Audited)", min_value=3, max_value=20, value=8, step=1)

    st.markdown("---")
    st.markdown("#### VERIFICATION MODULES")
    st.markdown("""
    - [ENABLED] Multi-Column Table Layout Ingestion
    - [ENABLED] Deterministic Scope 1-3 Math Reconciler
    - [ENABLED] SBTi Official Registry Validator
    - [ENABLED] EU Green Claims Typology Engine
    - [ENABLED] ISSA 5000 Workpaper Generation
    """)
    st.markdown("---")
    st.caption("SYSTEM VERSION: 2.4.0 (ENTERPRISE)")
    st.caption("ENVIRONMENT: AUDIT ASSURANCE SECURE ENVIRONMENT")

# ── HEADER BANNER ────────────────────────────────────────────────────
st.markdown('<div class="brand-header">VERITAS ESG FORENSIC ASSURANCE PLATFORM</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="brand-subhead">AUTONOMOUS ASSURANCE UNDER {audit_standard.upper()} &bull; MATERIALITY: {materiality_threshold.upper()}</div>',
    unsafe_allow_html=True
)

# ── ENGAGEMENT SELECTION ─────────────────────────────────────────────
st.markdown("#### 1. ENGAGEMENT SUBJECT ENTITY")

# ── ENGAGEMENT SELECTION ─────────────────────────────────────────────
st.markdown("#### 1. ENGAGEMENT SUBJECT ENTITY")

col_upload_box, col_preset_box = st.columns([1.2, 1])

with col_upload_box:
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; margin-bottom: 8px;">
            <div style="font-size: 0.75rem; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #0F172A; text-transform: uppercase;">
                OPTION A: UPLOAD CUSTOM CORPORATE DISCLOSURE (PDF)
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">
                Supports Fortune 500 ESG reports, SEBI BRSR filings, CSRD statements, and SEC 10-K filings.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    uploaded_custom_file = st.file_uploader(
        "Upload corporate sustainability / ESG report (PDF)",
        type=["pdf"],
        label_visibility="collapsed"
    )

with col_preset_box:
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; margin-bottom: 8px;">
            <div style="font-size: 0.75rem; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #0F172A; text-transform: uppercase;">
                OPTION B: INSTITUTIONAL BENCHMARK PRESETS (1-CLICK RUN)
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">
                Pre-indexed forensic audit datasets with verified baseline groundings.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    selected_preset = st.selectbox(
        "Select Institutional Benchmark Dataset:",
        [
            "Sample Case Alpha: Apex Global Industries (Forensic Greenwashing & Math Flaw)",
            "Sample Case Beta: Tata Motors Limited (Automotive ESG & BRSR Disclosure)",
            "Sample Case Gamma: Infosys Limited (IT Services & SBTi 1.5C Trajectory)"
        ],
        label_visibility="collapsed"
    )

selected_pdf_path = None
if uploaded_custom_file is None:
    if "Apex Global" in selected_preset:
        selected_pdf_path = os.path.join("sample_reports", "synthetic_greenwashing_audit_case.pdf")
    elif "Tata Motors" in selected_preset:
        selected_pdf_path = os.path.join("sample_reports", "tata_motors_esg_sample.pdf")
    elif "Infosys" in selected_preset:
        selected_pdf_path = os.path.join("sample_reports", "infosys_esg_sample.pdf")

# ── AUDIT INVOCATION ─────────────────────────────────────────────────
execute_btn = st.button("RUN FORENSIC AUDIT ENGAGEMENT", type="primary")

if execute_btn:
    target_path = selected_pdf_path
    temp_file_created = False

    if uploaded_custom_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_custom_file.read())
            target_path = tmp.name
            temp_file_created = True

    if not target_path or not os.path.exists(target_path):
        st.error("ERROR: No valid corporate PDF report selected or uploaded.")
    else:
        st.markdown("#### AUDITOR EXECUTION LOG")
        progress_box = st.empty()
        log_messages = []

        def update_progress(msg: str):
            clean_msg = msg.encode("ascii", "replace").decode("ascii")
            log_messages.append(clean_msg)
            display = "\n".join(log_messages[-6:])
            progress_box.code(display, language=None)

        with st.spinner("Executing autonomous assurance pipeline..."):
            try:
                audit_result = run_pipeline(
                    pdf_path=target_path,
                    progress_callback=update_progress,
                    max_claims_to_audit=max_claims
                )
                st.session_state.audit_data = audit_result
                st.success("STATUS: FORENSIC ASSURANCE TESTING COMPLETE.")
            except Exception as e:
                st.error(f"PIPELINE ERROR: {str(e)}")
            finally:
                if temp_file_created and os.path.exists(target_path):
                    os.unlink(target_path)
        progress_box.empty()

# ── AUDIT REPORT DASHBOARD ───────────────────────────────────────────
if st.session_state.audit_data:
    audit_data = st.session_state.audit_data
    results = audit_data.get("results", [])
    scores = audit_data.get("corporate_scores", {})
    tables = audit_data.get("tables", [])
    sbti = audit_data.get("sbti_status", {})
    company = audit_data.get("company_name", "ENTERPRISE ENTITY")

    st.markdown("---")
    st.markdown(f"### EXECUTIVE ASSURANCE SCORECARD: {company.upper()}")

    # 4 Metric Tiles (Strictly solid, flat, formal)
    t1, t2, t3, t4 = st.columns(4)

    with t1:
        exp_score = scores.get("exposure_score", 0)
        exp_color = "#B91C1C" if exp_score >= 40 else ("#C2410C" if exp_score >= 20 else "#15803D")
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-tile-label">Greenwashing Exposure</div>
                <div class="metric-tile-val" style="color: {exp_color};">{exp_score} / 100</div>
                <div class="metric-tile-sub">{scores.get('rating', 'NOMINAL')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with t2:
        readiness = scores.get("readiness_index", 0)
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-tile-label">Assurance Readiness</div>
                <div class="metric-tile-val" style="color: #0F172A;">{readiness}%</div>
                <div class="metric-tile-sub">ISSA 5000 Assurable Metrics</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with t3:
        exceptions = scores.get("contradicted_count", 0) + scores.get("arithmetic_flaw_count", 0) + scores.get("selective_disclosure_count", 0)
        exc_color = "#B91C1C" if exceptions > 0 else "#15803D"
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-tile-label">Audit Exceptions</div>
                <div class="metric-tile-val" style="color: {exc_color};">{exceptions}</div>
                <div class="metric-tile-sub">{scores.get('contradicted_count', 0)} Contradicted &bull; {scores.get('arithmetic_flaw_count', 0)} Math Flaws</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with t4:
        sbti_stat = sbti.get("status", "UNVERIFIED")
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-tile-label">SBTi Target Registry</div>
                <div class="metric-tile-val" style="font-size: 1.25rem; color: #0F172A;">{sbti_stat.upper()}</div>
                <div class="metric-tile-sub">{sbti.get('near_term_status', 'N/A').upper()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABBED AUDITOR WORKBENCH ──────────────────────────────────────
    tab_claims, tab_tables, tab_typologies, tab_export = st.tabs([
        "ITEMIZED TESTING WORKPAPERS",
        "EXTRACTED TABLES AND RECONCILIATIONS",
        "GREENWASHING TYPOLOGY MATRIX",
        "DELIVERABLES AND EXPORT"
    ])

    # ── TAB 1: ITEMIZED TESTING WORKPAPERS ────────────────────────────
    with tab_claims:
        st.markdown("#### ITEMIZED TESTING MATRIX (ISSA 5000 PRE-ASSURANCE)")
        st.caption("Each disclosure evaluated against deterministic table mathematics, statutory registries, and independent external corroboration.")

        f_col1, f_col2 = st.columns([2, 2])
        with f_col1:
            verdict_filter = st.selectbox(
                "Filter by Verdict:",
                ["All Disclosures", "Audit Exceptions Only (Contradicted / Math / Selective)", "Verified Disclosures Only", "Unverified Only"]
            )
        with f_col2:
            domain_filter = st.selectbox(
                "Filter by Domain:",
                ["All Domains", "emissions", "energy", "water", "waste", "diversity"]
            )

        filtered_results = results
        if "Audit Exceptions" in verdict_filter:
            filtered_results = [r for r in filtered_results if r["verdict"] in ["Contradicted", "Arithmetic Discrepancy", "Selective Disclosure"]]
        elif "Verified" in verdict_filter:
            filtered_results = [r for r in filtered_results if r["verdict"] == "Verified"]
        elif "Unverified" in verdict_filter:
            filtered_results = [r for r in filtered_results if r["verdict"] == "Unverified"]

        if domain_filter != "All Domains":
            filtered_results = [r for r in filtered_results if r.get("metric_type") == domain_filter]

        if not filtered_results:
            st.info("No disclosures match the active filter criteria.")
        else:
            for idx, r in enumerate(filtered_results):
                claim_id = r.get("claim_id", f"CLM-{idx+1}")
                verdict = r.get("verdict", "Unverified")
                risk = r.get("risk_level", "LOW RISK")
                claim_text = r.get("claim_text", "")
                page = r.get("page", 1)
                confidence = r.get("confidence", 70)

                expanded = verdict in ["Contradicted", "Arithmetic Discrepancy", "Selective Disclosure"]

                with st.expander(f"[{claim_id}] PAGE {page} | {verdict.upper()} | {claim_text[:80]}...", expanded=expanded):
                    c_left, c_right = st.columns([3, 2])

                    with c_left:
                        st.markdown("**Verbatim Disclosure:**")
                        st.text_area("Disclosure Sentence:", value=claim_text, height=68, disabled=True, key=f"txt_{claim_id}")

                        st.markdown("**Forensic Auditor Assessment:**")
                        st.write(r.get("reasoning", "No forensic rationale specified."))

                        # Typology alert
                        typology = r.get("typology")
                        if typology:
                            st.markdown(
                                f"""
                                <div style="border-left: 3px solid #B91C1C; background-color: #FEF2F2; padding: 8px 12px; margin-top: 8px; font-size: 0.8rem;">
                                    <b>TYPOLOGY FLAG: {typology.get('typology').upper()}</b><br>
                                    {typology.get('rationale')}<br>
                                    <b>Regulatory Liability:</b> {typology.get('regulatory_risk')}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        # Math audit alert
                        math_audit = r.get("math_audit", {})
                        if math_audit and math_audit.get("is_discrepancy"):
                            st.markdown(
                                f"""
                                <div style="border-left: 3px solid #B91C1C; background-color: #FEF2F2; padding: 8px 12px; margin-top: 8px; font-size: 0.8rem;">
                                    <b>ARITHMETIC DISCREPANCY:</b> {math_audit.get('detail')}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        # Evidence sources
                        sources = r.get("sources", [])
                        if sources:
                            st.markdown("<br>**Corroborating Evidence:**", unsafe_allow_html=True)
                            for s in sources:
                                if s.get("url"):
                                    st.markdown(f"- [{s.get('title', s.get('url'))}]({s.get('url')}) &bull; `{s.get('credibility', 'Independent')}`")

                    with c_right:
                        st.markdown("**Assurance Verdict:**")
                        if verdict == "Verified":
                            st.markdown('<span class="badge-verified">[VERIFIED]</span>', unsafe_allow_html=True)
                        elif verdict in ["Contradicted", "Arithmetic Discrepancy"]:
                            st.markdown('<span class="badge-exception">[CONTRADICTED / EXCEPTION]</span>', unsafe_allow_html=True)
                        elif verdict == "Selective Disclosure":
                            st.markdown('<span class="badge-amber">[SELECTIVE DISCLOSURE]</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="badge-neutral">[UNVERIFIED]</span>', unsafe_allow_html=True)

                        st.markdown(f"<br>**Risk Severity:** `{risk}`", unsafe_allow_html=True)
                        st.markdown(f"**Assurance Opinion:** `{r.get('assurance_opinion', 'Qualified')}`")
                        st.markdown(f"**Confidence Rating:** {confidence}%")
                        st.progress(confidence / 100)

                        st.markdown("---")
                        st.markdown("**Regulatory Framework Mapping:**")
                        tax = r.get("taxonomy", {})
                        st.markdown(f"- **CSRD / ESRS:** `{tax.get('csrd_esrs', 'N/A')}`")
                        st.markdown(f"- **GRI Standard:** `{tax.get('gri_standard', 'N/A')}`")
                        st.markdown(f"- **SEBI BRSR:** `{tax.get('sebi_brsr', 'N/A')}`")

                        st.markdown("---")
                        st.markdown("**Auditor Adjudication (HITL):**")
                        note_key = f"note_{claim_id}"
                        status_key = f"status_{claim_id}"

                        st.text_input("Auditor Review Note:", value=st.session_state.hitl_notes.get(claim_id, ""), key=note_key)
                        st.selectbox(
                            "Engagement Status:",
                            ["PENDING REVIEW", "AUDITOR CONFIRMED", "MANAGEMENT INQUIRY ISSUED", "IMMATERIAL / OVERRIDDEN"],
                            key=status_key
                        )

    # ── TAB 2: EXTRACTED TABLES & MATH RECONCILIATION ─────────────────
    with tab_tables:
        st.markdown("#### EXTRACTED TABLES AND DETERMINISTIC RECONCILIATIONS")
        st.caption("Structured matrices extracted from PDF layouts alongside row/column summation verification.")

        if not tables:
            st.info("No multi-column tabular matrices detected in the document.")
        else:
            for t in tables:
                t_id = t.get("table_id", "TBL")
                page = t.get("page", 1)
                category = t.get("category", "GENERAL ESG")
                headers = t.get("headers", [])
                rows = t.get("rows", [])
                footnotes = t.get("footnotes", [])

                with st.expander(f"TABLE {t_id} (PAGE {page}) | DOMAIN: {category.upper()}", expanded=True):
                    if headers and rows:
                        df_table = pd.DataFrame(rows, columns=headers[:len(rows[0])] if len(headers) >= len(rows[0]) else None)
                        st.dataframe(df_table, use_container_width=True)

                    if footnotes:
                        st.markdown("**Extracted Footnotes / Exclusions:**")
                        for fn in footnotes:
                            st.caption(f"- {fn}")

            # Deterministic Table Math
            table_audits = audit_data.get("table_math_audits", [])
            if table_audits:
                st.markdown("#### DETERMINISTIC ACCOUNTING RECONCILIATIONS")
                for ta in table_audits:
                    if ta.get("is_discrepancy"):
                        st.error(f"[DISCREPANCY] Table {ta.get('table_id')}: {ta.get('detail')}")
                    else:
                        st.success(f"[RECONCILED] Table {ta.get('table_id')}: {ta.get('detail')}")

    # ── TAB 3: GREENWASHING TYPOLOGY MATRIX ───────────────────────────
    with tab_typologies:
        st.markdown("#### INTERNATIONAL GREENWASHING TYPOLOGY FRAMEWORK")
        st.caption("Standardized categorization under the EU Green Claims Directive and Planet Tracker taxonomy.")

        typology_cards = [
            ("SELECTIVE DISCLOSURE", "Reporting Scope 1 and Scope 2 operational emissions while completely omitting Scope 3 supply chain footprint.", "EU CSRD ESRS E1 Mandatory Sanctions", "HIGH"),
            ("GREENRINSING", "Altering baseline comparison years (e.g. comparing to pandemic dip year) or lowering targets before maturity without explanation.", "ISSA 5000 Material Misstatement Risk", "HIGH"),
            ("UNSUBSTANTIATED OFFSETTING", "Claiming 'Carbon Neutral' operations by purchasing unverified voluntary carbon credits rather than operational decarbonization.", "EU Green Claims Directive Direct Ban", "HIGH"),
            ("GREENLIGHTING", "Spotlighting small green pilot projects while core operations remain carbon-intensive.", "UK CMA / FTC Green Guides Warning", "MEDIUM"),
            ("GREENSHIFTING", "Shifting emissions responsibility onto consumers via lifestyle calculators rather than supply-chain decarbonization.", "Brand Reputation Advisory Notice", "LOW"),
            ("GREENCROWDING", "Hiding in an industry alliance or average to disguise sluggish progress under the banner of collective effort.", "Benchmarking Exception", "MEDIUM")
        ]

        t_col1, t_col2 = st.columns(2)
        for idx, (name, desc, reg, sev) in enumerate(typology_cards):
            target_col = t_col1 if idx % 2 == 0 else t_col2
            with target_col:
                st.markdown(
                    f"""
                    <div class="metric-tile" style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between;">
                            <b>{name}</b>
                            <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 600;">{sev} RISK</span>
                        </div>
                        <p style="font-size: 0.8rem; color: #475569; margin-top: 6px; margin-bottom: 6px;">{desc}</p>
                        <div style="font-size: 0.72rem; color: #0F172A; font-family: 'IBM Plex Mono', monospace;"><b>LIABILITY:</b> {reg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ── TAB 4: EXECUTIVE DELIVERABLES & EXPORT ────────────────────────
    with tab_export:
        st.markdown("#### ENGAGEMENT DELIVERABLES (ISSA 5000 / ISAE 3000)")
        st.caption("Client-ready Pre-Assurance Memorandums and workpaper testing sheets formatted for Audit Committees and Regulators.")

        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.markdown("##### ISSA 5000 Pre-Assurance Memorandum (.PDF)")
            st.caption("Includes engagement scope, scorecard, itemized findings, exceptions log, and Lead Partner sign-off.")
            try:
                pdf_bytes = generate_audit_pdf(audit_data)
                st.download_button(
                    label="DOWNLOAD PRE-ASSURANCE MEMORANDUM (PDF)",
                    data=pdf_bytes,
                    file_name=f"Veritas_ESG_Assurance_Memo_{company.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF deliverable: {e}")

        with exp_col2:
            st.markdown("##### Complete Testing Matrix (.Excel / .CSV)")
            st.caption("Multi-sheet spreadsheet workpaper containing all verified claims, page citations, and evidence URLs.")
            try:
                excel_bytes = generate_audit_excel(audit_data)
                st.download_button(
                    label="DOWNLOAD TESTING WORKPAPERS (EXCEL)",
                    data=excel_bytes,
                    file_name=f"Veritas_ESG_Testing_Workpapers_{company.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating Excel deliverable: {e}")

        st.markdown("---")
        st.markdown("##### Machine-Readable Audit Workpapers (.JSON)")
        st.download_button(
            label="DOWNLOAD RAW AUDIT WORKPAPERS (JSON)",
            data=json.dumps(audit_data, indent=2, default=str),
            file_name=f"Veritas_ESG_Audit_Data_{company.replace(' ', '_')}.json",
            mime="application/json"
        )

# ── FOOTER BAR ───────────────────────────────────────────────────────
st.markdown(
    '<div class="formal-footer">'
    'VERITAS ESG ASSURANCE PRACTICE &bull; IAASB ISSA 5000 &bull; EFRAG CSRD ESRS &bull; SEBI BRSR CORE'
    '</div>',
    unsafe_allow_html=True
)

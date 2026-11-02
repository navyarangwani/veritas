import React, { useState, useEffect } from 'react';
import { 
  FileText, Shield, AlertTriangle, CheckCircle, Search, Filter, 
  Download, Upload, RefreshCw, ChevronRight, X, Play, Layers,
  ExternalLink, Check, Sliders, ArrowRight
} from 'lucide-react';

// Benchmark Cases with Full Institutional Audit Data
const BENCHMARK_CASES = {
  apex: {
    id: "apex",
    company_name: "Apex Global Manufacturing",
    engagement_id: "ENG-2024-ESG-0891",
    badgeText: "[DISCREPANCY DETECTED]",
    badgeClass: "bg-red-50 text-red-800 border-red-200",
    discrepancyIndex: "74 / 100",
    discrepancySub: "High Forensic Risk",
    discrepancyColor: "text-red-600",
    baselineDrift: "+14.2%",
    driftSub: "Exceeds 5.0% Limit",
    driftColor: "text-amber-600",
    mathStatus: "FAILED",
    mathSub: "+5,000 MT CO2e Delta",
    mathColor: "text-red-600",
    targetFeasibility: "OFF-TRACK",
    targetSub: "Requires 2.4x Rate",
    targetColor: "text-amber-600",
    breakdownTotal: "Reported: 45,000 | Verified: 50,000 MT CO2e",
    scope1: "20,000",
    scope2: "25,000",
    delta: "+5,000",
    scope3: "15,000",
    w1: "38%",
    w2: "32%",
    wDelta: "10%",
    w3: "20%",
    opinion: "Based on the substantive analytical procedures performed under ISSA 5000, the practitioner has identified material arithmetic discrepancies in the entity's reported Scope 1 and Scope 2 aggregate totals, representing an unverified omission of +5,000 MT CO2e. Furthermore, the entity restated historical 2019 baseline emissions with an upward drift of +14.2% without disclosing methodological recalculation notes required under ESRS E1-6. Management must remediate these exceptions before limited assurance sign-off.",
    findings: [
      {
        id: "FND-001",
        category: "math",
        metric: "Scope 1 + Scope 2 Aggregate",
        reported: "45,000 MT CO2e",
        calculated: "50,000 MT CO2e",
        status: "[DISCREPANCY]",
        statusClass: "bg-red-50 text-red-800 border-red-200",
        citation: "ISSA 5000 para 42(a) / GHG Protocol Corporate Standard",
        page: "Page 14, Table 3.2",
        bbox: "[bbox: x0=72.0, top=312.4, x1=540.0, bottom=384.2]",
        rawText: "TABLE 3.2: GHG DISCLOSURES\nScope 1 Operations: 20,000 MT CO2e\nScope 2 Electricity: 25,000 MT CO2e\nTotal Scope 1+2 Disclosed: 45,000 MT CO2e\n[ARITHMETIC ERROR: 20,000 + 25,000 = 50,000 != 45,000]",
        action: "Issue formal Management Representation Letter requesting arithmetic restatement. Discrepancy exceeds 5% materiality threshold."
      },
      {
        id: "FND-002",
        category: "typology",
        metric: "Baseline Recalculation (2019)",
        reported: "120,000 MT CO2e",
        calculated: "137,040 MT CO2e (+14.2%)",
        status: "[EXCEPTION]",
        statusClass: "bg-amber-50 text-amber-800 border-amber-200",
        citation: "Planet Tracker: Greencrowding / ESRS E1-6",
        page: "Page 22, Footnote 4",
        bbox: "[bbox: x0=68.5, top=580.0, x1=530.0, bottom=610.5]",
        rawText: "Footnote 4: 'Historical baseline emissions recalculated due to structural operational updates.' [No restatement threshold policy cited].",
        action: "Require entity to disclose recalculation trigger policy and external verification certificates for acquired assets."
      },
      {
        id: "FND-003",
        category: "typology",
        metric: "SBTi Net-Zero Target Alignment",
        reported: "1.5°C Paris Aligned",
        calculated: "Commitment Inactive",
        status: "[DISCREPANCY]",
        statusClass: "bg-red-50 text-red-800 border-red-200",
        citation: "EU Green Claims Directive Art. 3",
        page: "Page 4, Executive Letter",
        bbox: "[bbox: x0=70.0, top=140.0, x1=520.0, bottom=220.0]",
        rawText: "Statement: 'Our emissions reduction targets are aligned with the Science Based Targets initiative (SBTi) 1.5°C framework.'\nSBTi Registry Check: Expired / Target Not Validated.",
        action: "Remove public SBTi alignment claims from disclosure until formal target validation is published by SBTi Secretariat."
      }
    ]
  },
  tata: {
    id: "tata",
    company_name: "Tata Motors Limited",
    engagement_id: "ENG-2024-BRSR-0412",
    badgeText: "[STATUTORY BRSR VERIFIED]",
    badgeClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
    discrepancyIndex: "14 / 100",
    discrepancySub: "Low Forensic Risk",
    discrepancyColor: "text-emerald-700",
    baselineDrift: "+1.2%",
    driftSub: "Within Materiality (<5%)",
    driftColor: "text-emerald-700",
    mathStatus: "PASSED",
    mathSub: "Scope 1 + 2 Reconciled",
    mathColor: "text-emerald-700",
    targetFeasibility: "ON-TRACK",
    targetSub: "SBTi Targets Active",
    targetColor: "text-emerald-700",
    breakdownTotal: "Reported: 777,150 | Verified: 777,150 MT CO2e",
    scope1: "264,810",
    scope2: "512,340",
    delta: "0.00",
    scope3: "2,410,000",
    w1: "34%",
    w2: "66%",
    wDelta: "0%",
    w3: "0%",
    opinion: "Substantive analytical procedures performed on the Tata Motors FY2023-24 BRSR disclosure demonstrate arithmetic integrity in Scope 1 and Scope 2 emissions accounting. Energy intensity disclosures and Scope 3 transport boundary assumptions adhere to SEBI Core assurance frameworks with zero mathematical deviations.",
    findings: [
      {
        id: "FND-001",
        category: "math",
        metric: "Scope 1 (Direct GHG)",
        reported: "264,810 MT CO2e",
        calculated: "264,810 MT CO2e",
        status: "[VERIFIED]",
        statusClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
        citation: "SEBI BRSR Principle 6 / GHG Protocol",
        page: "Page 78, Section C",
        bbox: "[bbox: x0=50.0, top=210.0, x1=550.0, bottom=340.0]",
        rawText: "Scope 1 direct emissions calculated from fuel consumption across manufacturing facilities in Pune, Sanand, Jamshedpur, and Pantnagar.",
        action: "Document testing procedures in working paper; no adjustments required."
      },
      {
        id: "FND-002",
        category: "math",
        metric: "Scope 2 (Electricity)",
        reported: "512,340 MT CO2e",
        calculated: "512,340 MT CO2e",
        status: "[VERIFIED]",
        statusClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
        citation: "Central Electricity Authority (CEA) Factor v19",
        page: "Page 81, Section C",
        bbox: "[bbox: x0=50.0, top=350.0, x1=550.0, bottom=480.0]",
        rawText: "Scope 2 grid electricity consumption reconciled with state electricity board invoices using official CEA emission factors.",
        action: "Cross-check utility invoices on sample basis."
      },
      {
        id: "FND-003",
        category: "typology",
        metric: "RE100 Renewable Integration",
        reported: "41.2% Total Power",
        calculated: "40.8% Verified",
        status: "[VERIFIED]",
        statusClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
        citation: "SBTi Corporate Manual / ISO 14064-3",
        page: "Page 83, Section C",
        bbox: "[bbox: x0=50.0, top=500.0, x1=550.0, bottom=590.0]",
        rawText: "Renewable energy procurement verified via long-term Power Purchase Agreements (PPAs) and on-site solar installations.",
        action: "Accept disclosure as materially compliant."
      }
    ]
  },
  infosys: {
    id: "infosys",
    company_name: "Infosys Limited",
    engagement_id: "ENG-2023-SBTI-0109",
    badgeText: "[SBTI APPROVED NET-ZERO]",
    badgeClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
    discrepancyIndex: "08 / 100",
    discrepancySub: "Institutional Gold Standard",
    discrepancyColor: "text-emerald-700",
    baselineDrift: "+0.4%",
    driftSub: "Strict Restatement Policy",
    driftColor: "text-emerald-700",
    mathStatus: "PASSED",
    mathSub: "Dual-Engine Reconciled",
    mathColor: "text-emerald-700",
    targetFeasibility: "VALIDATED",
    targetSub: "SBTi Net-Zero Standard",
    targetColor: "text-emerald-700",
    breakdownTotal: "Reported: 18,920 | Verified: 18,920 MT CO2e",
    scope1: "5,410",
    scope2: "13,510",
    delta: "0.00",
    scope3: "240,100",
    w1: "28%",
    w2: "72%",
    wDelta: "0%",
    w3: "0%",
    opinion: "Practitioner testing confirms that Infosys Limited has maintained carbon neutrality for operations and verified Science Based Targets across Scope 1, 2, and 3 categories. Offset retirement certificates match Gold Standard registry serial numbers with zero evidence of greenshifting or uncredited claims.",
    findings: [
      {
        id: "FND-001",
        category: "math",
        metric: "Scope 1 + Scope 2 (Market-based)",
        reported: "18,920 MT CO2e",
        calculated: "18,920 MT CO2e",
        status: "[VERIFIED]",
        statusClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
        citation: "ISSA 5000 / ISAE 3410 Reasonable",
        page: "Page 42, ESG Data Book",
        bbox: "[bbox: x0=60.0, top=180.0, x1=540.0, bottom=290.0]",
        rawText: "Scope 1 (Diesel generators & refrigerant losses): 5,410 MT CO2e; Scope 2 (Market-based green tariffs): 13,510 MT CO2e.",
        action: "Zero exceptions noted; sign off on arithmetic accuracy."
      },
      {
        id: "FND-002",
        category: "typology",
        metric: "Gold Standard Carbon Offsets",
        reported: "100% Retired via Registry",
        calculated: "Registry Serial Matches",
        status: "[VERIFIED]",
        statusClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
        citation: "Gold Standard Registry Verifier v3",
        page: "Page 55, Carbon Portfolio",
        bbox: "[bbox: x0=60.0, top=310.0, x1=540.0, bottom=420.0]",
        rawText: "Retirement certificates cross-checked against Gold Standard public registry; matching vintage 2021-2023.",
        action: "Retain serial certificates in engagement file."
      },
      {
        id: "FND-003",
        category: "typology",
        metric: "SBTi Target Progress (2030)",
        reported: "Scope 3 Supply Chain -45%",
        calculated: "Active SBTi Progress Track",
        status: "[VERIFIED]",
        statusClass: "bg-emerald-50 text-emerald-800 border-emerald-200",
        citation: "SBTi Target Registry v2.4",
        page: "Page 58, Value Chain",
        bbox: "[bbox: x0=60.0, top=440.0, x1=540.0, bottom=550.0]",
        rawText: "Target validation status: Net-Zero Standard approved by SBTi technical review committee.",
        action: "Cross-referenced with SBTi published dashboard."
      }
    ]
  }
};

export default function App() {
  const [view, setView] = useState('landing'); // 'landing' | 'workbench'
  const [activeCaseKey, setActiveCaseKey] = useState('apex');
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'math' | 'typology' | 'opinion'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFinding, setSelectedFinding] = useState(null); // for slide-over evidence drawer
  const [showTelemetryModal, setShowTelemetryModal] = useState(false);
  const [telemetryStep, setTelemetryStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const activeCase = BENCHMARK_CASES[activeCaseKey] || BENCHMARK_CASES.apex;

  useEffect(() => {
    const formData = new FormData();
    formData.append('sample_id', 'apex_global');
    fetch('/api/audit/sample', { method: 'POST', body: formData }).catch(() => {});
  }, []);

  // Telemetry Stepper Simulation
  const runPipelineTelemetry = () => {
    setShowTelemetryModal(true);
    setIsProcessing(true);
    setTelemetryStep(1);

    setTimeout(() => setTelemetryStep(2), 700);
    setTimeout(() => setTelemetryStep(3), 1400);
    setTimeout(() => {
      setTelemetryStep(4);
      setIsProcessing(false);
    }, 2100);
  };

  const handleCaseSelect = (caseKey) => {
    setActiveCaseKey(caseKey);
    setSelectedFinding(null);
    const formData = new FormData();
    formData.append('sample_id', caseKey === 'tata' ? 'tata_motors' : (caseKey === 'infosys' ? 'infosys' : 'apex_global'));
    fetch('/api/audit/sample', { method: 'POST', body: formData }).catch(() => {});
  };

  const handleLaunchSample = (caseKey) => {
    setActiveCaseKey(caseKey);
    setSelectedFinding(null);
    setView('workbench');
    const formData = new FormData();
    formData.append('sample_id', caseKey === 'tata' ? 'tata_motors' : (caseKey === 'infosys' ? 'infosys' : 'apex_global'));
    fetch('/api/audit/sample', { method: 'POST', body: formData }).catch(() => {});
  };

  const handleExport = (type) => {
    const caseParam = activeCaseKey || 'apex';
    window.open(`/api/export/${type}?case_id=${caseParam}`, '_blank');
  };

  // Filter findings based on active tab and search query
  let filteredFindings = activeCase.findings;
  if (activeTab === 'math') {
    filteredFindings = filteredFindings.filter(f => f.category === 'math');
  } else if (activeTab === 'typology') {
    filteredFindings = filteredFindings.filter(f => f.category === 'typology');
  }

  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    filteredFindings = filteredFindings.filter(f => 
      f.id.toLowerCase().includes(q) ||
      f.metric.toLowerCase().includes(q) ||
      f.citation.toLowerCase().includes(q) ||
      f.status.toLowerCase().includes(q)
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAFC] text-[#0F172A] relative selection:bg-[#ECFDF5] selection:text-[#064E3B]">
      
      {/* Top Institutional Header */}
      <header className="bg-[#064E3B] text-white border-b border-[#043327] px-6 py-3 flex items-center justify-between sticky top-0 z-40 shadow-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Shield className="w-6 h-6 text-[#34D399]" />
            <span className="font-bold text-lg tracking-wide uppercase font-mono">Veritas ESG</span>
          </div>
          <span className="text-xs font-mono uppercase bg-[#022C22] text-[#34D399] px-2.5 py-0.5 rounded border border-[#065F46] hidden sm:inline-block">
            ISSA 5000 Forensic Assurance Suite
          </span>
        </div>

        {/* View Switcher & Figma Deep Link */}
        <div className="flex items-center space-x-3 text-sm">
          <button 
            onClick={() => setView('landing')} 
            className={`px-3.5 py-1.5 rounded font-medium transition-colors ${
              view === 'landing' 
                ? 'text-white bg-[#022C22] border border-[#059669]' 
                : 'text-emerald-100 hover:text-white hover:bg-[#043E2F] border border-transparent'
            }`}
          >
            Platform Overview
          </button>
          
          <button 
            onClick={() => setView('workbench')} 
            className={`px-3.5 py-1.5 rounded font-medium transition-colors flex items-center space-x-1.5 ${
              view === 'workbench' 
                ? 'text-white bg-[#022C22] border border-[#059669]' 
                : 'text-emerald-100 hover:text-white hover:bg-[#043E2F] border border-transparent'
            }`}
          >
            <span>Auditor Workbench</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          </button>
        </div>
      </header>

      {/* ============================================================ */}
      {/* VIEW 1: EXECUTIVE LANDING PAGE                              */}
      {/* ============================================================ */}
      {view === 'landing' && (
        <div className="flex-1 block">
          
          {/* Executive Hero */}
          <section className="bg-white border-b border-slate-200 py-16 px-6 sm:px-12">
            <div className="max-w-5xl mx-auto">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold uppercase tracking-wider mb-6">
                <FileText className="w-4 h-4 text-emerald-600" />
                <span>Automated Pre-Assurance Intelligence for Big 4 & Institutional Audit Engagements</span>
              </div>
              
              <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight mb-4">
                Independent Forensic Verification for Corporate Sustainability Disclosures
              </h1>
              
              <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-3xl mb-8">
                Veritas ESG replaces superficial checklist audits with deterministic arithmetic verification, statutory greenwashing classification, and automated evidence reconciliation aligned with <strong className="text-slate-800">ISSA 5000</strong>, <strong className="text-slate-800">EU Green Claims Directive</strong>, and <strong className="text-slate-800">SBTi Target Registries</strong>.
              </p>

              {/* Primary Action Buttons */}
              <div className="flex flex-wrap items-center gap-4">
                <button 
                  onClick={() => setView('workbench')} 
                  className="px-6 py-3 bg-[#064E3B] hover:bg-[#022C22] text-white font-semibold rounded-md shadow-sm border border-[#043327] flex items-center space-x-2 transition-all cursor-pointer"
                >
                  <span>Launch Auditor Workbench</span>
                  <ArrowRight className="w-4 h-4 text-emerald-400" />
                </button>
                <button 
                  onClick={() => handleLaunchSample('apex')} 
                  className="px-5 py-3 bg-white hover:bg-slate-50 text-slate-700 font-medium rounded-md border border-slate-300 shadow-sm flex items-center space-x-2 transition-all cursor-pointer"
                >
                  <FileText className="w-4 h-4 text-slate-500" />
                  <span>Run Benchmark Discrepancy Case</span>
                </button>
              </div>

              {/* Forensic Metrics Strip */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-12 pt-8 border-t border-slate-200 text-slate-700 text-xs">
                <div>
                  <div className="text-xl font-bold text-slate-900 font-mono">100%</div>
                  <div className="text-slate-500 uppercase mt-0.5">Deterministic Arithmetic Audit</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-slate-900 font-mono">ISSA 5000</div>
                  <div className="text-slate-500 uppercase mt-0.5">Global Assurance Standard</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-slate-900 font-mono">12+</div>
                  <div className="text-slate-500 uppercase mt-0.5">Greenwashing Typologies</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-slate-900 font-mono">0.00%</div>
                  <div className="text-slate-500 uppercase mt-0.5">PR Wire Hallucination Risk</div>
                </div>
              </div>
            </div>
          </section>

          {/* Four Audit Pillars */}
          <section className="py-14 px-6 sm:px-12 max-w-5xl mx-auto">
            <div className="mb-8">
              <h2 className="text-xs font-bold text-emerald-800 uppercase tracking-wider">Four Audit Pillars</h2>
              <p className="text-2xl font-bold text-slate-900 mt-1">Institutional Assurance Architecture</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Pillar 1 */}
              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm hover:border-emerald-300 transition-all">
                <div className="w-10 h-10 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-sm mb-4 font-mono">
                  P1
                </div>
                <h3 className="font-bold text-slate-900 text-base mb-2">Deterministic Math Integrity & Table Parsing</h3>
                <p className="text-slate-600 text-sm leading-relaxed mb-4">
                  Zero LLM guesswork for math. Direct tabular bounding-box coordinate extraction of Scope 1, 2, and 3 disclosures with verified Scope 1 + 2 summation, historical baseline recalculation drift, and year-over-year rate variance testing.
                </p>
                <div className="text-xs font-mono text-emerald-800 bg-emerald-50 p-2.5 rounded border border-emerald-200">
                  Rule: Scope 1 + Scope 2 = Reported Total & Baseline Drift &lt; Materiality Threshold
                </div>
              </div>

              {/* Pillar 2 */}
              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm hover:border-emerald-300 transition-all">
                <div className="w-10 h-10 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-sm mb-4 font-mono">
                  P2
                </div>
                <h3 className="font-bold text-slate-900 text-base mb-2">Statutory Greenwashing Typology Tagging</h3>
                <p className="text-slate-600 text-sm leading-relaxed mb-4">
                  Automatic categorization under the <strong>EU Green Claims Directive</strong> and <strong>Planet Tracker Framework</strong> (Greencrowding, Greenlighting, Greenshifting, Greenrinsing, Greenbleaching) with statutory penalties risk rating.
                </p>
                <div className="text-xs font-mono text-emerald-800 bg-emerald-50 p-2.5 rounded border border-emerald-200">
                  Classification: Greencrowding, Greenshifting, Ambiguity Without Verification
                </div>
              </div>

              {/* Pillar 3 */}
              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm hover:border-emerald-300 transition-all">
                <div className="w-10 h-10 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-sm mb-4 font-mono">
                  P3
                </div>
                <h3 className="font-bold text-slate-900 text-base mb-2">Global Registry & Evidence Cross-Verification</h3>
                <p className="text-slate-600 text-sm leading-relaxed mb-4">
                  Reconciles stated corporate net-zero and emissions commitments directly against official Science Based Targets initiative (SBTi) registries. Filters out PR newswires (PR Newswire, Business Wire) to preserve forensic credibility.
                </p>
                <div className="text-xs font-mono text-emerald-800 bg-emerald-50 p-2.5 rounded border border-emerald-200">
                  Evidence Tiering: Primary Filings &gt; Statutory Registries &gt; Verified Media
                </div>
              </div>

              {/* Pillar 4 */}
              <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm hover:border-emerald-300 transition-all">
                <div className="w-10 h-10 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-sm mb-4 font-mono">
                  P4
                </div>
                <h3 className="font-bold text-slate-900 text-base mb-2">ISSA 5000 / ISAE 3000 Pre-Assurance Memorandums</h3>
                <p className="text-slate-600 text-sm leading-relaxed mb-4">
                  Synthesizes forensic discrepancies into institutional audit deliverables: formal Pre-Assurance Opinion Memorandums (.PDF) and substantive Testing Matrices (.XLSX) ready for Big 4 engagement partner sign-off.
                </p>
                <div className="text-xs font-mono text-emerald-800 bg-emerald-50 p-2.5 rounded border border-emerald-200">
                  Outputs: Formal Partner Memorandum (.PDF) & Detailed Test Matrix (.XLSX)
                </div>
              </div>

            </div>
          </section>

          {/* Benchmark Showcase Section */}
          <section className="bg-slate-100 border-t border-slate-200 py-14 px-6 sm:px-12">
            <div className="max-w-5xl mx-auto">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Pre-Configured Benchmark Audit Engagements</h2>
                  <p className="text-sm text-slate-600 mt-1">Test the forensic engine against verified corporate reports and synthetic stress tests.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Case 1 */}
                <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                        DISCREPANCY DETECTED
                      </span>
                      <span className="text-xs text-slate-500 font-mono">FY2023-24</span>
                    </div>
                    <h4 className="font-bold text-slate-900 text-base">Apex Global Manufacturing</h4>
                    <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                      Synthetic institutional stress test. Scope 1 + 2 summation math error of +5,000 MT CO2e and unannounced baseline drift of +14.2%.
                    </p>
                  </div>
                  <button 
                    onClick={() => handleLaunchSample('apex')} 
                    className="mt-6 w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded text-center transition-colors cursor-pointer"
                  >
                    Execute Apex Audit
                  </button>
                </div>

                {/* Case 2 */}
                <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                        STATUTORY BRSR
                      </span>
                      <span className="text-xs text-slate-500 font-mono">FY2023-24</span>
                    </div>
                    <h4 className="font-bold text-slate-900 text-base">Tata Motors Limited</h4>
                    <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                      Official Business Responsibility & Sustainability Report (BRSR). Scope 1, 2, and 3 disclosure verification against SEBI Core Framework.
                    </p>
                  </div>
                  <button 
                    onClick={() => handleLaunchSample('tata')} 
                    className="mt-6 w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded text-center transition-colors cursor-pointer"
                  >
                    Execute Tata Motors Audit
                  </button>
                </div>

                {/* Case 3 */}
                <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        SBTI ALIGNED
                      </span>
                      <span className="text-xs text-slate-500 font-mono">FY2022-23</span>
                    </div>
                    <h4 className="font-bold text-slate-900 text-base">Infosys Limited</h4>
                    <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                      Science-Based Targets initiative (SBTi) net-zero validation report. Carbon neutrality verification against official registry data.
                    </p>
                  </div>
                  <button 
                    onClick={() => handleLaunchSample('infosys')} 
                    className="mt-6 w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded text-center transition-colors cursor-pointer"
                  >
                    Execute Infosys Audit
                  </button>
                </div>

              </div>
            </div>
          </section>

        </div>
      )}

      {/* ============================================================ */}
      {/* VIEW 2: AUDITOR WORKBENCH (10/10 ENTERPRISE EXPERIENCE)     */}
      {/* ============================================================ */}
      {view === 'workbench' && (
        <div className="flex-1 p-6 sm:p-8 max-w-7xl mx-auto w-full">
          
          {/* Engagement Header & Meta Strip */}
          <div className="bg-white rounded-lg border border-slate-200 p-4 mb-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="p-2.5 bg-[#064E3B] text-white rounded shadow-sm">
                <FileText className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-lg font-bold text-slate-900">{activeCase.company_name}</h2>
                  <span className={`text-[11px] font-mono px-2 py-0.5 rounded font-bold uppercase border ${activeCase.badgeClass}`}>
                    {activeCase.badgeText}
                  </span>
                </div>
                <div className="text-xs text-slate-500 font-mono mt-0.5 flex items-center space-x-2">
                  <span>Engagement: {activeCase.engagement_id}</span>
                  <span>&bull;</span>
                  <span>Standard: ISSA 5000 / ISAE 3000</span>
                  <span>&bull;</span>
                  <span>Materiality: 5.0%</span>
                </div>
              </div>
            </div>

            {/* Quick Export Suite Actions */}
            <div className="flex items-center space-x-3">
              <button 
                onClick={() => handleExport('pdf')} 
                className="px-3.5 py-1.5 bg-[#064E3B] hover:bg-[#022C22] text-white text-xs font-semibold rounded border border-[#043327] flex items-center space-x-1.5 transition-colors cursor-pointer"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
                <span>Export ISSA 5000 Memo (.PDF)</span>
              </button>
              <button 
                onClick={() => handleExport('excel')} 
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded border border-slate-300 flex items-center space-x-1.5 transition-colors cursor-pointer"
              >
                <Download className="w-3.5 h-3.5 text-slate-500" />
                <span>Testing Matrix (.XLSX)</span>
              </button>
            </div>
          </div>

          {/* Dual-Pane Grid Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* LEFT PANE: Benchmark Switcher & Upload (4 Cols) */}
            <div className="lg:col-span-4 space-y-5">
              
              {/* Benchmark Case Selector */}
              <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Benchmark Engagements</h3>
                  <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    Verified Presets
                  </span>
                </div>
                
                <div className="space-y-2">
                  <button 
                    onClick={() => handleCaseSelect('apex')} 
                    className={`w-full text-left p-3 rounded border text-xs font-medium transition-all cursor-pointer ${
                      activeCaseKey === 'apex' 
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-900 shadow-sm' 
                        : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="font-bold flex items-center justify-between">
                      <span>Apex Global Manufacturing</span>
                      <span className="font-mono text-[10px] text-red-600 font-bold">[MATH ERROR]</span>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">Scope 1+2 mismatch & +14.2% baseline drift</div>
                  </button>

                  <button 
                    onClick={() => handleCaseSelect('tata')} 
                    className={`w-full text-left p-3 rounded border text-xs font-medium transition-all cursor-pointer ${
                      activeCaseKey === 'tata' 
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-900 shadow-sm' 
                        : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="font-bold flex items-center justify-between">
                      <span>Tata Motors Limited</span>
                      <span className="font-mono text-[10px] text-amber-600 font-bold">[BRSR FY24]</span>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">Statutory SEBI BRSR Core compliance</div>
                  </button>

                  <button 
                    onClick={() => handleCaseSelect('infosys')} 
                    className={`w-full text-left p-3 rounded border text-xs font-medium transition-all cursor-pointer ${
                      activeCaseKey === 'infosys' 
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-900 shadow-sm' 
                        : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="font-bold flex items-center justify-between">
                      <span>Infosys Limited</span>
                      <span className="font-mono text-[10px] text-emerald-600 font-bold">[SBTI NET-ZERO]</span>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">Science Based Targets Net-Zero track</div>
                  </button>
                </div>
              </div>

              {/* Custom Upload Card */}
              <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Custom Disclosure Intake</h3>
                
                <label className="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-lg p-5 text-center cursor-pointer bg-slate-50 transition-colors block">
                  <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <div className="text-xs font-semibold text-slate-700">
                    {uploadedFile ? uploadedFile.name : "Upload Sustainability Report (.PDF)"}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">Supports BRSR, GRI, CSRD, CDP (Up to 200 pages)</div>
                  <input 
                    type="file" 
                    accept=".pdf" 
                    className="hidden" 
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setUploadedFile(e.target.files[0]);
                      }
                    }} 
                  />
                </label>

                <div className="mt-4 space-y-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 uppercase mb-1">Assurance Scope</label>
                    <select className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-700 font-medium">
                      <option>Scope 1 + Scope 2 + Scope 3 (Comprehensive)</option>
                      <option>Scope 1 + Scope 2 (Core Assurance)</option>
                      <option>SBTi Net-Zero Target Alignment Only</option>
                    </select>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-600 uppercase mb-1">Baseline Year</label>
                      <input type="text" defaultValue="2019" className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white font-mono text-slate-700" />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-600 uppercase mb-1">Materiality Threshold</label>
                      <input type="text" defaultValue="5.0%" className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white font-mono text-slate-700" />
                    </div>
                  </div>
                </div>

                {/* Telemetry Stepper Launcher */}
                <button 
                  onClick={runPipelineTelemetry}
                  className="mt-5 w-full py-2.5 bg-[#064E3B] hover:bg-[#022C22] text-white text-xs font-bold rounded shadow-sm transition-colors flex items-center justify-center space-x-1.5 cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 text-emerald-400 fill-current" />
                  <span>Execute Forensic Pipeline</span>
                </button>
              </div>

            </div>

            {/* RIGHT PANE: KPI Ribbon, Emissions Bar, Finding Matrix (8 Cols) */}
            <div className="lg:col-span-8 space-y-6">
              
              {/* 4 Metric KPI Ribbon */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                
                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="text-[11px] font-bold uppercase text-slate-500">Discrepancy Index</div>
                  <div className={`text-2xl font-bold font-mono mt-1 ${activeCase.discrepancyColor}`}>
                    {activeCase.discrepancyIndex}
                  </div>
                  <div className={`text-[11px] font-semibold mt-0.5 ${activeCase.discrepancyColor}`}>
                    {activeCase.discrepancySub}
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="text-[11px] font-bold uppercase text-slate-500">Baseline Drift</div>
                  <div className={`text-2xl font-bold font-mono mt-1 ${activeCase.driftColor}`}>
                    {activeCase.baselineDrift}
                  </div>
                  <div className={`text-[11px] font-semibold mt-0.5 ${activeCase.driftColor}`}>
                    {activeCase.driftSub}
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="text-[11px] font-bold uppercase text-slate-500">Math Reconciliation</div>
                  <div className={`text-2xl font-bold font-mono mt-1 ${activeCase.mathColor}`}>
                    {activeCase.mathStatus}
                  </div>
                  <div className={`text-[11px] font-semibold mt-0.5 ${activeCase.mathColor}`}>
                    {activeCase.mathSub}
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                  <div className="text-[11px] font-bold uppercase text-slate-500">Target Feasibility</div>
                  <div className={`text-2xl font-bold font-mono mt-1 ${activeCase.targetColor}`}>
                    {activeCase.targetFeasibility}
                  </div>
                  <div className={`text-[11px] font-semibold mt-0.5 ${activeCase.targetColor}`}>
                    {activeCase.targetSub}
                  </div>
                </div>

              </div>

              {/* Scope 1/2/3 Breakdown Visualizer (Zero Gradients, Pure Institutional Proportions) */}
              <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Emissions Accounting Reconciled Breakdown (MT CO2e)
                  </div>
                  <div className="text-xs font-mono font-bold text-slate-900">
                    {activeCase.breakdownTotal}
                  </div>
                </div>
                
                {/* Segmented Flat Bar */}
                <div className="h-4 w-full bg-slate-100 rounded flex overflow-hidden border border-slate-200">
                  <div style={{ width: activeCase.w1 }} className="bg-[#064E3B]" title="Scope 1 Direct"></div>
                  <div style={{ width: activeCase.w2 }} className="bg-[#059669]" title="Scope 2 Electricity"></div>
                  {activeCase.wDelta !== '0%' && (
                    <div style={{ width: activeCase.wDelta }} className="bg-[#DC2626]" title="Math Discrepancy Delta"></div>
                  )}
                  {activeCase.w3 !== '0%' && (
                    <div style={{ width: activeCase.w3 }} className="bg-[#94A3B8]" title="Scope 3 Value Chain"></div>
                  )}
                </div>

                <div className="flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-600 mt-2">
                  <div className="flex items-center space-x-1.5">
                    <span className="w-2.5 h-2.5 bg-[#064E3B] rounded-sm inline-block"></span>
                    <span>Scope 1 Direct ({activeCase.scope1})</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="w-2.5 h-2.5 bg-[#059669] rounded-sm inline-block"></span>
                    <span>Scope 2 Purchased ({activeCase.scope2})</span>
                  </div>
                  {activeCase.delta !== '0.00' && (
                    <div className="flex items-center space-x-1.5 text-red-600 font-bold">
                      <span className="w-2.5 h-2.5 bg-[#DC2626] rounded-sm inline-block"></span>
                      <span>Discrepancy Delta ({activeCase.delta})</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1.5">
                    <span className="w-2.5 h-2.5 bg-[#94A3B8] rounded-sm inline-block"></span>
                    <span>Scope 3 Disclosed ({activeCase.scope3})</span>
                  </div>
                </div>
              </div>

              {/* Substantive Findings Grid Container */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
                
                {/* Tab Navigation & Live Search Input */}
                <div className="border-b border-slate-200 px-4 pt-3 pb-2 flex flex-wrap items-center justify-between bg-slate-50 gap-2">
                  <div className="flex space-x-1">
                    <button 
                      onClick={() => setActiveTab('all')} 
                      className={`px-3 py-1.5 text-xs font-bold rounded-t cursor-pointer ${
                        activeTab === 'all' 
                          ? 'text-slate-900 border-b-2 border-[#064E3B] bg-white' 
                          : 'text-slate-600 hover:text-slate-900 border-b-2 border-transparent'
                      }`}
                    >
                      All Findings ({activeCase.findings.length})
                    </button>
                    <button 
                      onClick={() => setActiveTab('math')} 
                      className={`px-3 py-1.5 text-xs font-semibold rounded-t cursor-pointer ${
                        activeTab === 'math' 
                          ? 'text-slate-900 border-b-2 border-[#064E3B] bg-white' 
                          : 'text-slate-600 hover:text-slate-900 border-b-2 border-transparent'
                      }`}
                    >
                      Arithmetic Integrity ({activeCase.findings.filter(f => f.category === 'math').length})
                    </button>
                    <button 
                      onClick={() => setActiveTab('typology')} 
                      className={`px-3 py-1.5 text-xs font-semibold rounded-t cursor-pointer ${
                        activeTab === 'typology' 
                          ? 'text-slate-900 border-b-2 border-[#064E3B] bg-white' 
                          : 'text-slate-600 hover:text-slate-900 border-b-2 border-transparent'
                      }`}
                    >
                      SBTi & Typology ({activeCase.findings.filter(f => f.category === 'typology').length})
                    </button>
                    <button 
                      onClick={() => setActiveTab('opinion')} 
                      className={`px-3 py-1.5 text-xs font-semibold rounded-t cursor-pointer ${
                        activeTab === 'opinion' 
                          ? 'text-slate-900 border-b-2 border-[#064E3B] bg-white' 
                          : 'text-slate-600 hover:text-slate-900 border-b-2 border-transparent'
                      }`}
                    >
                      ISSA 5000 Opinion
                    </button>
                  </div>

                  {/* Instant Search Box */}
                  <div className="relative">
                    <input 
                      type="text" 
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Filter findings..." 
                      className="text-xs border border-slate-300 rounded pl-7 pr-3 py-1 bg-white font-mono text-slate-700 w-44 focus:outline-none focus:border-emerald-600"
                    />
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2 top-2" />
                  </div>
                </div>

                {/* Table View */}
                {activeTab !== 'opinion' && (
                  <div className="p-4 overflow-x-auto">
                    <div className="text-[11px] text-slate-500 mb-2 italic">
                      Tip: Click on any finding row to slide over the substantive audit evidence, raw PDF coordinates, and statutory cross-check.
                    </div>
                    
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 text-slate-500 uppercase font-mono text-[11px]">
                          <th className="py-2.5 px-3">Finding ID</th>
                          <th className="py-2.5 px-3">Metric Disclosed</th>
                          <th className="py-2.5 px-3">Reported</th>
                          <th className="py-2.5 px-3">Calculated / Verified</th>
                          <th className="py-2.5 px-3">Forensic Status</th>
                          <th className="py-2.5 px-3">Statutory Citation</th>
                          <th className="py-2.5 px-3 text-right">Evidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {filteredFindings.map((f) => (
                          <tr 
                            key={f.id} 
                            onClick={() => setSelectedFinding(f)}
                            className="hover:bg-slate-50 transition-colors cursor-pointer group"
                          >
                            <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{f.id}</td>
                            <td className="py-2.5 px-3 font-semibold text-slate-800">{f.metric}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-600">{f.reported}</td>
                            <td className="py-2.5 px-3 font-mono text-slate-800 font-semibold">{f.calculated}</td>
                            <td className="py-2.5 px-3">
                              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold border ${f.statusClass}`}>
                                {f.status}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-mono text-[11px] text-slate-500">{f.citation}</td>
                            <td className="py-2.5 px-3 text-right">
                              <span className="text-xs text-emerald-800 font-bold group-hover:underline inline-flex items-center space-x-1">
                                <span>Inspect</span>
                                <ChevronRight className="w-3.5 h-3.5 text-emerald-600" />
                              </span>
                            </td>
                          </tr>
                        ))}
                        {filteredFindings.length === 0 && (
                          <tr>
                            <td colSpan="7" className="py-6 text-center text-slate-400 font-mono text-xs">
                              No findings match the current filter criteria.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Opinion Summary View */}
                {activeTab === 'opinion' && (
                  <div className="p-6">
                    <div className="border-l-4 border-emerald-800 pl-4 py-1 mb-4">
                      <h4 className="text-sm font-bold text-slate-900 uppercase">
                        Independent Assurance Practitioner Pre-Assessment Memorandum
                      </h4>
                      <div className="text-xs text-slate-600 font-mono mt-0.5">
                        Engagement standard: ISSA 5000 / ISAE 3000 Limited Assurance Procedures
                      </div>
                    </div>
                    
                    <p className="text-xs text-slate-700 leading-relaxed font-serif bg-slate-50 p-5 rounded border border-slate-200">
                      "{activeCase.opinion}"
                    </p>
                  </div>
                )}

              </div>

            </div>

          </div>

        </div>
      )}

      {/* ============================================================ */}
      {/* NEW 10/10 FEATURE: SLIDE-OVER EVIDENCE DRAWER               */}
      {/* ============================================================ */}
      {selectedFinding && (
        <>
          {/* Backdrop */}
          <div 
            onClick={() => setSelectedFinding(null)} 
            className="fixed inset-0 bg-slate-900 bg-opacity-40 z-50 transition-opacity"
          />

          {/* Drawer Body */}
          <div className="fixed inset-y-0 right-0 w-full sm:w-[520px] bg-white border-l border-slate-200 shadow-2xl z-50 flex flex-col animate-slide-in">
            
            {/* Drawer Header */}
            <div className="bg-[#064E3B] text-white p-5 flex items-center justify-between border-b border-[#043327]">
              <div>
                <div className="text-[11px] font-mono text-emerald-300 uppercase tracking-wider">
                  Substantive Evidence Dossier
                </div>
                <div className="text-base font-bold text-white mt-0.5">
                  {selectedFinding.id} &bull; {selectedFinding.metric}
                </div>
              </div>
              <button 
                onClick={() => setSelectedFinding(null)} 
                className="text-emerald-200 hover:text-white p-1 rounded hover:bg-[#043E2F] transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scrollable Content */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6 text-xs text-slate-700">
              
              {/* Classification Card */}
              <div className="bg-slate-50 p-4 rounded border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 uppercase">Finding Classification</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase border ${selectedFinding.statusClass}`}>
                    {selectedFinding.status}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-3 pt-2 text-[11px] font-mono">
                  <div>
                    <span className="text-slate-500 block">Reported in Filing:</span>
                    <span className="font-bold text-slate-900">{selectedFinding.reported}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Independently Verified:</span>
                    <span className="font-bold text-red-600">{selectedFinding.calculated}</span>
                  </div>
                </div>
              </div>

              {/* Statutory Framework */}
              <div>
                <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px] mb-1.5 text-slate-500">
                  Statutory Framework & Standard Citation
                </h4>
                <div className="p-3 bg-red-50 text-red-900 border border-red-200 rounded font-mono text-[11px] leading-relaxed">
                  {selectedFinding.citation}
                </div>
              </div>

              {/* Bounding Box & Document Extraction */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px] text-slate-500">
                    Source Document Bounding Box Extraction
                  </h4>
                  <span className="font-mono text-[10px] text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    {selectedFinding.page}
                  </span>
                </div>
                
                {/* Monospace Code / Excerpt Preview */}
                <div className="p-4 bg-slate-900 text-slate-200 font-mono text-[11px] rounded border border-slate-800 leading-relaxed overflow-x-auto space-y-1">
                  <div className="text-slate-500 text-[10px] border-b border-slate-800 pb-1">
                    pdfplumber coordinate track: {selectedFinding.bbox}
                  </div>
                  <pre className="pt-1 whitespace-pre-wrap font-mono text-emerald-400">
                    {selectedFinding.rawText}
                  </pre>
                </div>
              </div>

              {/* Remediation Action */}
              <div className="border-t border-slate-200 pt-4">
                <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px] mb-1 text-slate-500">
                  Recommended Practitioner Action
                </h4>
                <p className="text-slate-600 leading-relaxed">
                  {selectedFinding.action}
                </p>
              </div>

            </div>

            {/* Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-500">
                Audit Trail Hash: SHA256:d8a9f4c0...
              </span>
              <button 
                onClick={() => setSelectedFinding(null)} 
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-semibold transition-colors cursor-pointer"
              >
                Dismiss Evidence
              </button>
            </div>

          </div>
        </>
      )}

      {/* ============================================================ */}
      {/* NEW 10/10 FEATURE: PIPELINE EXECUTION STEPPER MODAL          */}
      {/* ============================================================ */}
      {showTelemetryModal && (
        <div className="fixed inset-0 bg-slate-900 bg-opacity-60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg border border-slate-200 shadow-2xl max-w-lg w-full overflow-hidden animate-fade-in">
            
            {/* Modal Header */}
            <div className="bg-[#064E3B] text-white p-4 flex items-center justify-between border-b border-[#043327]">
              <div className="flex items-center space-x-2">
                <RefreshCw className={`w-5 h-5 text-emerald-400 ${isProcessing ? 'animate-spin' : ''}`} />
                <span className="font-bold text-sm">Veritas ESG Pipeline Telemetry</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-200 bg-[#022C22] px-2 py-0.5 rounded border border-[#065F46]">
                {isProcessing ? 'RUNNING' : 'COMPLETED'}
              </span>
            </div>

            {/* Stepper Body */}
            <div className="p-6 space-y-4 text-xs">
              
              {/* Step 1 */}
              <div className="flex items-start space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${
                  telemetryStep >= 1 ? 'bg-[#064E3B] text-white' : 'bg-slate-100 text-slate-400'
                }`}>
                  {telemetryStep > 1 ? <Check className="w-3.5 h-3.5" /> : '1'}
                </div>
                <div className="flex-1">
                  <div className="font-bold text-slate-900">PDF Table Extraction & Materiality Scoping</div>
                  <div className={`text-[11px] ${telemetryStep >= 1 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}`}>
                    {telemetryStep >= 1 ? 'Tables isolated via pdfplumber with bounding boxes [DONE]' : 'Pending execution...'}
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${
                  telemetryStep >= 2 ? 'bg-[#064E3B] text-white' : 'bg-slate-100 text-slate-400'
                }`}>
                  {telemetryStep > 2 ? <Check className="w-3.5 h-3.5" /> : '2'}
                </div>
                <div className="flex-1">
                  <div className="font-bold text-slate-900">Deterministic Arithmetic Verification</div>
                  <div className={`text-[11px] ${telemetryStep >= 2 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}`}>
                    {telemetryStep >= 2 ? 'Arithmetic reconciled: Scope 1 + Scope 2 calculated [DONE]' : 'Awaiting table extraction...'}
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${
                  telemetryStep >= 3 ? 'bg-[#064E3B] text-white' : 'bg-slate-100 text-slate-400'
                }`}>
                  {telemetryStep > 3 ? <Check className="w-3.5 h-3.5" /> : '3'}
                </div>
                <div className="flex-1">
                  <div className="font-bold text-slate-900">SBTi Registry & Greenwashing Typology Tagging</div>
                  <div className={`text-[11px] ${telemetryStep >= 3 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}`}>
                    {telemetryStep >= 3 ? 'SBTi target matching complete. EU Claims tagged [DONE]' : 'Awaiting math verification...'}
                  </div>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex items-start space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${
                  telemetryStep >= 4 ? 'bg-[#064E3B] text-white' : 'bg-slate-100 text-slate-400'
                }`}>
                  {telemetryStep >= 4 ? <Check className="w-3.5 h-3.5" /> : '4'}
                </div>
                <div className="flex-1">
                  <div className="font-bold text-slate-900">ISSA 5000 Opinion & Working Paper Synthesis</div>
                  <div className={`text-[11px] ${telemetryStep >= 4 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}`}>
                    {telemetryStep >= 4 ? 'Pre-Assurance Memorandum & Testing Matrix ready [DONE]' : 'Awaiting typology tagging...'}
                  </div>
                </div>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="bg-slate-50 p-3 border-t border-slate-200 text-right">
              <button 
                onClick={() => setShowTelemetryModal(false)}
                disabled={isProcessing}
                className={`px-4 py-1.5 rounded text-xs font-semibold transition-colors ${
                  isProcessing 
                    ? 'bg-slate-300 text-slate-500 cursor-not-allowed' 
                    : 'bg-[#064E3B] hover:bg-[#022C22] text-white cursor-pointer'
                }`}
              >
                {isProcessing ? 'Processing Pipeline...' : 'View Findings Dossier'}
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

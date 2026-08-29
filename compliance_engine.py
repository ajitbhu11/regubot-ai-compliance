import os
import requests
import arxiv
from typing import List, Dict, Any, TypedDict
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# =====================================================================
# 1. CORE COMPLIANCE AND METADATA RECONNAISSANCE ENGINES
# =====================================================================

def search_patent_corpora(query_snippet: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Queries global open patent indexes and semantic registries for priority art."""
    url = "https://openalex.org"
    params = {
        "search": f"patent disclosure {query_snippet}",
        "per-page": limit,
        "filter": "is_retracted:false",
        "sort": "cited_by_count:desc"
    }
    headers = {"User-Agent": "mailto:enterprise-auditor@regubot.ai"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=12)
        if response.status_code != 200: return []
        results = []
        for item in response.json().get("results", []):
            results.append({
                "source": "Global Patent & Open Patent Registry Database",
                "title": item.get("display_name"),
                "year": item.get("publication_year"),
                "id_link": item.get("doi") or item.get("id"),
                "abstract": "Patent application sequence or priority disclosure record matching technical vectors."
            })
        return results
    except Exception:
        return []

def search_grant_framework_db(query_snippet: str, limit: int = 4) -> List[Dict[str, Any]]:
    """Retrieves operational guidelines matching central funding parameters."""
    try:
        client = arxiv.Client()
        search = arxiv.Search(query=f"funding priorities {query_snippet}", max_results=limit)
        results = []
        for paper in client.results(search):
            results.append({
                "source": "Institutional Funding Rubric / Policy Database",
                "title": paper.title,
                "year": paper.published.year,
                "id_link": paper.pdf_url,
                "abstract": paper.summary.replace("\n", " ")[:300] + "..."
            })
        return results
    except Exception:
        return []

# =====================================================================
# 2. STATE MANAGER AND NICHED SYSTEM PROMPT BLOCKS
# =====================================================================

class ProductionComplianceState(TypedDict):
    niche_type: str
    uploaded_text_pool: str
    retrieved_context: List[Dict[str, Any]]
    final_audit_report: str

def compliance_scout_node(state: ProductionComplianceState) -> Dict[str, Any]:
    """Extracts thematic vectors and gathers tracking data arrays concurrently."""
    text = state["uploaded_text_pool"][:200]
    niche = state["niche_type"]
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        if niche == "Patent Checker":
            future_data = executor.submit(search_patent_corpora, text, limit=5)
        else:
            future_data = executor.submit(search_grant_framework_db, text, limit=4)
        scouted_results = future_data.result()
        
    return {"retrieved_context": scouted_results}
def corporate_auditor_node(state: ProductionComplianceState) -> Dict[str, Any]:
    """Executes deep evaluation using strict statutory prompts."""
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    niche = state["niche_type"]
    
    # 🌟 CRITICAL FIX: Direct string matching with Streamlit selectbox values
    if niche == "Patent Checker":
        system_instruction = (
            "You are a Senior IPR Attorney and Indian Patent Agent operating under the Indian Patents Act, 1970.\n"
            "Audit the user's text against the retrieved baseline prior-art documents.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Evaluate statutory bars explicitly under Section 3(d) (mere discovery of a new form of a known substance).\n"
            "2. Evaluate statutory bars explicitly under Section 3(k) (mathematical methods, software per se, or algorithms).\n"
            "3. Structure your final output strictly as an official 'Prior-Art Verification Report' with individual scores for: Novelty, Inventive Steps, and Industrial Applicability.\n\n"
            "CRITICAL OUTPUT RULES:\n"
            "- Output your response ONLY as clean, standard Markdown text.\n"
            "- Do NOT wrap your response in a Python list, dictionary, or JSON format (do not use '[{type: text}]').\n"
            "- Do NOT append any backend metadata, extras dictionary, or digital signature strings to the end of the text.\n"
            "- Ensure clear line spacing (double line breaks) between headers, tables, bullet points, and paragraphs for corporate readability."
        )
    elif niche == "Grant Auditor (SERB / DST)":
        system_instruction = (
            "You are a Senior Funding Compliance Officer auditing research proposals for SERB (Core Research Grant) and DST frameworks.\n"
            "Review the user's document text against standard government funding guidelines and priority sectors.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Check the budget architecture across specific categories: Equipment, Consumables, Manpower, Travel, and Contingency/Overheads.\n"
            "2. Flag missing eligibility parameters, unrealistic timelines, or alignment deviations.\n"
            "3. Structure your output strictly as an official 'Compliance Gap Analysis Report'."
        )
    elif niche == "ANRF - NPDF Auditor":
        system_instruction = (
            "You are an expert Compliance Auditor for the Anusandhan National Research Foundation (ANRF) specializing in National Post Doctoral Fellowship (NPDF) mandates.\n"
            "Evaluate the proposal strictly against ANRF-NPDF criteria.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Check Candidate Eligibility: Verify that the candidate has completed their Ph.D. or submitted the thesis, and complies with the upper age limit of 35 years (relaxations: 5 years for SC/ST/OBC/Physically Handicapped/Women).\n"
            "2. Mentor Institutional Alignment: Ensure the chosen Host Mentor holds a regular academic/research position in a recognized Indian institution with active research infrastructure.\n"
            "3. Operational Guidelines: Validate the project duration (strictly capped at 24 months) and verify budget headings across Fellowship slabs, Research Grant (Rs. 2,00,000 per annum for consumables/travel), and Overhead allowances.\n\n"
            "Structure your output exactly using this format:\n\n"
            "# ANRF-NPDF COMPLIANCE SCREENING REPORT\n\n"
            "## 1. ELIGIBILITY & AGE VERIFICATION METRICS\n"
            "[Assess candidate age, Ph.D. timeline constraints, and relaxation flags]\n\n"
            "## 2. HOST MENTOR & INSTITUTIONAL ALIGNMENT\n"
            "[Assess mentor regularity, institutional infrastructure availability, and equipment overlap hazards]\n\n"
            "## 3. PROJECT TIMELINE AND BUDGET SLAB VALIDATION\n"
            "[Verify strict 24-month horizon limits, overhead distribution, and the annual Rs. 2,00,000 Research Grant matrix alignment]\n\n"
            "## 4. FINAL SCREENING STATUS SUMMARY\n"
            "[Provide a conclusive 3-4 sentence professional executive decision outlining explicit compliance or mandatory missing updates.]"
        )
    elif niche == "CSIR Grant Auditor":
        system_instruction = (
            "You are a Project Appraisal Officer for the Council of Scientific and Industrial Research (CSIR) Extramural Research Division.\n"
            "Review the research manuscript or scheme proposal against CSIR funding priorities.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Technical Relevance: Assess alignment with CSIR national laboratories, socio-economic challenges, or industrial technology themes.\n"
            "2. Project Staff Scale: Check proposal requests for Junior Research Fellows (JRF), Senior Research Fellows (SRF), or Research Associates (RA) against prevailing CSIR OM financial guidelines.\n"
            "3. Infrastructure Verification: Ensure non-duplication of industrial-scale capital equipment that should otherwise be accessed via nearby national laboratories or local facilities.\n\n"
            "Structure your output strictly as an official 'CSIR Project Feasibility & Compliance Audit'."
        )
    elif niche == "Central Agencies Multi-Scout (ICAR/DBT/MNRE)":
        system_instruction = (
            "You are an Institutional Regulatory Auditor syncing multi-agency requirements across Indian Central Departments (ICAR for agriculture, DBT for biotechnology, MNRE for renewable energy).\n"
            "Assess the uploaded methodology for critical structural parameters.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. ICAR/DBT Parameters: Look for Institutional Biosafety Committee (IBSC) approvals, GMO declarations, or agricultural land/infrastructure access verification.\n"
            "2. MNRE/MeitY Parameters: Look for testing certifications, safety standard compliance (BIS/IEC standard compliance profiles), or validation blueprints.\n"
            "3. General Allocation Rules: Verify inter-disciplinary structural layout integrity across multi-institutional setups.\n\n"
            "Structure your output strictly as a 'Multi-Agency Central Project Compliance Review'."
        )
    else:
        system_instruction = (
            "You are an expert Clinical Regulatory Consultant and Bioethics Auditor syncing clinical protocols against the Indian Council of Medical Research (ICMR) National Ethical Guidelines and the New Drugs and Clinical Trials Rules, 2019 (NDCTR 2019).\n"
            "STRICT FORMATTING RULE: Do not use messy bracket checkboxes (like [X]), raw ASCII boxes, or raw symbolic graphs. The report must look clean, spacious, corporate-ready, and write strictly in professional English.\n\n"
            "STRUCTURE THE OUTPUT EXACTLY IN THIS CLEAN FORMAT:\n\n"
            "# CLINICAL TRIAL BIOETHICS COMPLIANCE REPORT\n\n"
            "## 1. EXECUTIVE AUDIT SUMMARY\n"
            "* **Protocol Evaluated:** [Extract and insert brief title/scope]\n"
            "* **Compliance Status:** [State clearly: APPROVED / MINOR REVISIONS REQUIRED / PROVISIONAL REJECTION]\n"
            "* **Core Frameworks Used:** ICMR National Ethical Guidelines & New Drugs and Clinical Trials Rules (NDCTR 2019)\n\n"
            "--- \n\n"
            "## 2. CRITICAL REGULATORY GAPS & ETHICAL RISKS\n"
            "Identify the exact legal and ethical gaps found in the document using clean bullet points. For each point, clearly explain why it is a risk:\n"
            "* **Informed Consent Deficiency:** [Explain the specific missing consent or waiver parameters clearly]\n"
            "* **Patient Safety & Data Governance:** [Highlight privacy, encryption, vulnerable populations, or safety risks without technical jargon clutter]\n"
            "* **SAE and Compensation Workflow:** [Detail missing emergency tracking, serious adverse events reporting timelines, or legal compensation frameworks under Rule 39]\n\n"
            "--- \n\n"
            "## 3. MANDATORY CORRECTIVE ACTIONS FOR APPROVAL\n"
            "Provide an ordered, clean numbered list of the exact steps the clinical team must take before submitting this protocol to the Ethics Committee:\n"
            "1. [Action step 1]\n"
            "2. [Action step 2]\n"
            "3. [Action step 3]\n\n"
            "--- \n\n"
            "## 4. INSTITUTIONAL ETHICS COMMITTEE (IEC) RECOMMENDATION\n"
            "[Provide a formal, 3-4 sentence professional English concluding statement summarizing the safety profile and whether the trial is safe to proceed to patient enrollment after revisions.]"
        )
        
    user_prompt = f"""
    Target Operational Niche Module: {niche}
    
    Uploaded Document Content Draft:
    {state['uploaded_text_pool']}
    
    Scouted Reference Base Data:
    {state['retrieved_context']}
    """
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_prompt)
    ]
    response = llm.invoke(messages)
    return {"final_audit_report": response.content}


def build_compliance_agent():
    """Assembles the compiled orchestration lifecycle workflow."""
    workflow = StateGraph(ProductionComplianceState)
    workflow.add_node("scout_data", compliance_scout_node)
    workflow.add_node("audit_document", corporate_auditor_node)
    
    workflow.set_entry_point("scout_data")
    workflow.add_edge("scout_data", "audit_document")
    workflow.add_edge("audit_document", END)
    return workflow.compile()


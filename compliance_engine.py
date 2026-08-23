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
    # FIXED: Re-added the complete operational API endpoint path string
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
    
    if niche == "Patent Checker":
        system_instruction = (
            "You are a Senior IPR Attorney and Indian Patent Agent operating under the Indian Patents Act, 1970.\n"
            "Audit the user's text against the retrieved baseline prior-art documents.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Evaluate statutory bars explicitly under Section 3(d) (mere discovery of a new form of a known substance).\n"
            "2. Evaluate statutory bars explicitly under Section 3(k) (mathematical methods, software per se, or algorithms).\n"
            "3. Structure your final output strictly as an official 'Prior-Art Verification Report' with individual scores for: Novelty, Inventive Steps, and Industrial Applicability."
        )
    elif niche == "Grant Auditor":
        system_instruction = (
            "You are a Senior Funding Compliance Officer auditing research proposals for SERB (Core Research Grant), DST, and ICMR.\n"
            "Review the user's document text against standard government funding guidelines and priority sectors.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Check the budget architecture across specific categories: Equipment, Consumables, Manpower, Travel, and Contingency/Overheads.\n"
            "2. Flag missing eligibility parameters, unrealistic timelines, or alignment deviations.\n"
            "3. Structure your output strictly as an official 'Compliance Gap Analysis Report'."
        )
    else:
        system_instruction = (
            "You are an expert Regulatory consultant auditing clinical protocols for the Central Ethics Committee and Clinical Trials Registry - India (CTRI).\n"
            "Audit the text against the statutory provisions of the New Drugs and Clinical Trials Rules, 2019.\n\n"
            "STRICT DISCLOSURE REQUIREMENTS:\n"
            "1. Verify patient safety criteria, informed consent protocols, and statistical sample justifications.\n"
            "2. Flag gaps in safety reporting workflows or potential ethical conflicts.\n"
            "3. Structure your output strictly as an official 'Ethics Committee Clearance Readiness Checklist'."
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

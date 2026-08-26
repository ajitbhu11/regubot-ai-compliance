import os
import io
import re
import pandas as pd  # Data visualization dependency for the analytics tracking system
import streamlit as st
from docx import Document
from pypdf import PdfReader
from compliance_engine import build_compliance_agent

# =====================================================================
# 1. COMMERCIAL APPLICATION LAYOUT CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="ReguBot AI Compliance Suite (Beta Testing)",
    page_icon="🛡️",
    layout="wide"
)

# Initialize persistent session state matrices to track background data logs
if "metrics_log" not in st.session_state:
    st.session_state["metrics_log"] = []
if "feedback_submitted" not in st.session_state:
    st.session_state["feedback_submitted"] = False

# =====================================================================
# 2. CLERK USER REGISTRATION GATEWAY LOGIC
# =====================================================================
if "user_authenticated" not in st.session_state:
    st.session_state["user_authenticated"] = False

if not st.session_state["user_authenticated"]:
    st.title("🔐 ReguBot Institutional Authentication")
    st.write("Please sign in or register your academic email address below to access the multi-agent compliance pipeline.")
    
    CLERK_SIGN_IN_URL = "https://accounts.dev"
    st.components.v1.iframe(CLERK_SIGN_IN_URL, height=550, scrolling=True)
    
    st.markdown("---")
    if st.button("✅ I have successfully signed into my Clerk Account", type="primary"):
        st.session_state["user_authenticated"] = True
        st.rerun()
    st.stop()

# =====================================================================
# 3. SIDEBAR WORKSPACE WITH INTEGRATED FEEDBACK TOOL
# =====================================================================
with st.sidebar:
    st.header("🏢 Beta Test Environment")
    st.success("👑 Testing Tier Unlocked: Report Download Feature is Active.")
    
    st.markdown("---")
    st.header("🔑 Bring-Your-Own-Key (BYOK)")
    st.info("This application runs using your personal account tokens. No server fees are charged to the host.")
    
    user_gemini_key = st.text_input("Enter Your Google Gemini API Key:", type="password", placeholder="AIzaSy...")
    st.caption("🔗 [Get a free Gemini key from Google AI Studio](https://google.com)")

    st.markdown("---")
    st.subheader("⚡ Bounding Filters")
    selected_years = st.slider("Select Publication Year Range:", min_value=2010, max_value=2026, value=(2022, 2026))
    start_year, end_year = selected_years

    # 🌟 NEW INTEGRATION: ANONYMOUS BETA TESTER FEEDBACK WIDGET
    st.markdown("---")
    st.subheader("💬 Anonymous Tester Feedback")
    if not st.session_state["feedback_submitted"]:
        with st.form("feedback_form", clear_on_submit=True):
            rating = st.selectbox("Rate Report Accuracy:", ["⭐⭐⭐⭐⭐ (Excellent)", "⭐⭐⭐⭐ (Good)", "⭐⭐⭐ (Average)", "⭐⭐ (Poor)", "⭐ (Broken)"])
            comments = st.text_area("What features or rules should we add?", placeholder="e.g., Add Section 3(e) check for patents, modify ICMR timeline validation...")
            submit_feedback = st.form_submit_button("Submit Feedback")
            if submit_feedback:
                st.session_state["feedback_submitted"] = True
                st.toast("Thank you for your valuable response!", icon="🚀")
                st.rerun()
    else:
        st.success("🎉 Thank you! Feedback logged successfully.")
        if st.button("Submit another response"):
            st.session_state["feedback_submitted"] = False
            st.rerun()

    st.markdown("---")
    st.subheader("🗒️ Legal & Compliance")
    with st.expander("⚖️ Terms of Service"):
        st.caption("Usage Profile: This application functions purely under a Bring-Your-Own-Key (BYOK) paradigm.")
    with st.expander("🔒 Privacy Policy"):
        st.caption("Data Custody: Uploaded manuscripts are processed purely in-memory during active loops.")

# Main app tabs configuration separating execution and analytics panels
st.title("🛡️ ReguBot AI: Institutional Compliance & IPR Suite")
st.caption("Beta Sandbox Mode: Auditing academic manuscripts for Patents, Grants, and Ethics board approval.")

main_tab, dashboard_tab = st.tabs(["🚀 Execution Pipeline", "📊 Tracking Analytics Dashboard"])
# =====================================================================
# 4. EXECUTION PIPELINE TAB LAYOUT & PROCESSING LOOP
# =====================================================================
with main_tab:
    niche_selection = st.selectbox(
        "Select Target Compliance Evaluation Module:",
        ["Patent Checker", "Grant Auditor", "Bioethics Scout"]
    )

    if niche_selection == "Patent Checker":
        st.info("🎯 Module active: Indian Patent (IPR) & Prior-Art Agent. Auditing criteria under the Indian Patents Act, 1970.")
    elif niche_selection == "Grant Auditor":
        st.info("💰 Module active: SERB / DST Government Grant Alignment Auditor framework.")
    else:
        st.info("🔬 Module active: Bioethics & Clinical Trial Regulatory Scout synced against regional CTRI and Live ICMR profiles.")

    uploaded_file = st.file_uploader(
        "📤 Drag and drop your research manuscript, grant proposal draft, or clinical methodology document:",
        type=["pdf", "docx"],
        help="Supports complete academic drafts in PDF or Microsoft Word formatting."
    )

    parsed_manuscript_text = ""

    # Document Extraction Layer (PDF and DOCX)
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "pdf":
            try:
                pdf_reader = PdfReader(uploaded_file)
                extracted_pages = [page.extract_text() for page in pdf_reader.pages]
                parsed_manuscript_text = "\n".join(filter(None, extracted_pages))
                st.success(f"📊 Successfully parsed PDF: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error parsing PDF file: {e}")
        elif file_extension == "docx":
            try:
                doc = Document(uploaded_file)
                extracted_paras = [p.text for p in doc.paragraphs]
                parsed_manuscript_text = "\n".join(filter(None, extracted_paras))
                st.success(f"📊 Successfully parsed Word Document: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error parsing Word file: {e}")

    # Helper function to convert AI Markdown responses seamlessly into an MS Word Document
    def convert_markdown_to_docx(markdown_text):
        doc = Document()
        for line in markdown_text.split('\n'):
            cleaned = line.strip()
            if not cleaned: continue
            if line.startswith('# '): doc.add_heading(line[2:], level=1)
            elif line.startswith('## '): doc.add_heading(line[3:], level=2)
            elif line.startswith('* ') or line.startswith('- '): doc.add_paragraph(line[2:], style='List Bullet')
            else: doc.add_paragraph(line)
        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    # Core Execution Lifecycle Trigger Block
    if st.button("🚀 Initiate Complete Compliance Evaluation", type="primary"):
        if not user_gemini_key.strip():
            st.error("🔑 Access Denied: Please provide your personal Gemini API key in the sidebar to power the evaluation loop.")
        elif not parsed_manuscript_text.strip():
            st.error("Please upload a valid PDF or DOCX file to execute the compliance evaluation loop.")
        else:
            os.environ["GOOGLE_API_KEY"] = user_gemini_key
            status_flag = "Success"
            
            try:
                with st.status("🕵️ Executive Agent auditing compliance vectors...", expanded=True) as status_box:
                    st.write("🔍 Extracting technical vectors and scanning tracking registers...")
                    compliance_engine = build_compliance_agent()
                    initial_state = {
                        "niche_type": niche_selection,
                        "uploaded_text_pool": parsed_manuscript_text,
                        "retrieved_context": [],
                        "final_audit_report": ""
                    }
                    final_output = compliance_engine.invoke(initial_state)
                    status_box.update(label="✅ Analysis completion reached!", state="complete")
                
                audit_report = final_output.get("final_audit_report", "")
                actual_text = str(audit_report)
                
            except Exception as e:
                status_flag = "Failed"
                actual_text = f"An execution error occurred during processing loops: {e}"
                st.error(actual_text)
            
            # 🌟 TELEMETRY REGISTRY UPDATES: Append document run statistics to session state memory cache
            st.session_state["metrics_log"].append({
                "Document Name": uploaded_file.name if uploaded_file else "Unknown_Draft",
                "Evaluation Module": niche_selection,
                "Status": status_flag,
                "Length (Chars)": len(parsed_manuscript_text)
            })
            
            if status_flag == "Success":
                st.success("✨ Regulatory document synthesis successful!")
                docx_bytes = convert_markdown_to_docx(actual_text)
                safe_niche = niche_selection.replace(' ', '_')
                raw_filename = uploaded_file.name if uploaded_file else "Manuscript"
                clean_filename_base = re.sub(r'[^a-zA-Z0-9_]', '_', raw_filename)
                dynamic_filename = f"{safe_niche}_{clean_filename_base}_Audit_Report.docx"
                
                # Unlocked Testing Download Layer Output
                st.download_button(
                    label="📄 Download Official Audit Report as MS Word (.docx)",
                    data=docx_bytes,
                    file_name=dynamic_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
                st.markdown("---")
                st.markdown(actual_text)

# =====================================================================
# 5. TRACKING ANALYTICS DASHBOARD ENGINE TAB
# =====================================================================
with dashboard_tab:
    st.header("📊 Real-Time Operations Analytics")
    st.caption("Live statistical execution summary tracking of document auditing workflows across the current testing cycle.")
    
    if len(st.session_state["metrics_log"]) > 0:
        df_metrics = pd.DataFrame(st.session_state["metrics_log"])
        
        # Upper level high-density metrics summary scorecard metrics cards row layout
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Files Evaluated", len(df_metrics))
        with kpi2:
            success_count = len(df_metrics[df_metrics["Status"] == "Success"])
            success_rate = (success_count / len(df_metrics)) * 100
            st.metric("Processing Success Rate", f"{success_rate:.1f}%")
        with kpi3:
            most_used_module = str(df_metrics["Evaluation Module"].mode()[0])
            st.metric("Peak Operational Niche", most_used_module)
            
        st.markdown("---")
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.subheader("📁 Module Allocation Share")
            module_counts = df_metrics["Evaluation Module"].value_counts()
            st.bar_chart(module_counts, color="#2e7d32")
            
        with col_graph2:
            st.subheader("📋 Document Audit Process Registry")
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
    else:
        st.info("📉 No telemetry tracking records found. Audit your first manuscript document inside the Execution Pipeline tab to generate data visualizations.")


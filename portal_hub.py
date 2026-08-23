import os
import io
import re
import streamlit as st
from docx import Document
from pypdf import PdfReader
from compliance_engine import build_compliance_agent

# =====================================================================
# 1. COMMERCIAL APPLICATION LAYOUT CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="ReguBot AI Compliance Suite",
    page_icon="🛡️",
    layout="wide")

PREMIUM_CHECKOUT_URL = "https://stripe.com"
STRIPE_CUSTOMER_PORTAL = "https://stripe.com"
INDIVIDUAL_PASS_URL = "https://stripe.com"

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
# 3. PRIMARY BACKEND SAAS INTERFACE PORTAL WORKSPACE
# =====================================================================
st.title("🛡️ ReguBot AI: Institutional Compliance & IPR Suite")
st.caption("Enterprise-tier evaluation engine auditing academic manuscripts for Patents, Grants, and Ethics board approval.")

with st.sidebar:
    st.header("🏢 Enterprise Portal")
    is_premium = st.checkbox("⭐ Unlock Corporate Tier Access", value=False)
    
    if not is_premium:
        st.warning("🔒 Running on the Free Preview Tier.")
        st.markdown(f"### **Institutional Pro Tier**")
        st.markdown(f"**Price:** ₹25,000/month (Billed Annually)")
        st.markdown(f"[✨ Upgrade Campus License Now]({PREMIUM_CHECKOUT_URL})")
        st.markdown("---")
        st.markdown(f"### **Individual Scholar Pass**")
        st.markdown(f"**Price:** ₹499/month (Cancel Anytime)")
        st.markdown(f"[✨ Buy Single User Pass]({INDIVIDUAL_PASS_URL})")
    else:
        st.success("👑 Corporate features unlocked successfully!")
        st.markdown(f"[⚙️ Manage Billing / Cancel Subscription]({STRIPE_CUSTOMER_PORTAL})")
        
    st.markdown("---")
    st.header("🔑 AI Brain Authorization")
    st.info("To maintain zero server fees for you, this app utilizes the Bring-Your-Own-Key (BYOK) model.")
    
    user_gemini_key = st.text_input("Enter Your Google Gemini API Key:", type="password", placeholder="AIzaSy...")
    st.caption("🔗 [Get a free Gemini key from Google AI Studio](https://google.com)")

    st.markdown("---")
    st.subheader("⚡ Bounding Filters")
    
    if is_premium:
        selected_years = st.slider("Select Publication Year Range:", min_value=2010, max_value=2026, value=(2022, 2026))
        start_year, end_year = selected_years
    else:
        st.caption("📅 Publication Range Locked: Defaulting to 2020-2026 (Upgrade to unlock slider)")
        start_year, end_year = 2020, 2026

    st.markdown("---")
    st.subheader("🗒️ Legal & Compliance")
    
    with st.expander("⚖️ Terms of Service"):
        st.caption("Usage Profile: This application functions purely under a Bring-Your-Own-Key (BYOK) paradigm. All computing operations are funded by the API tokens managed directly under your personal or institutional Google account keys.")
        
    with st.expander("🔒 Privacy Policy"):
        st.caption("Data Custody: Uploaded manuscripts are processed purely in-memory during active loops. We maintain zero local database persistence.")
# Choose the active operations niche layout framework
niche_selection = st.selectbox(
    "Select Target Compliance Evaluation Module:",
    ["Patent Checker", "Grant Auditor", "Bioethics Scout"]
)

if niche_selection == "Patent Checker":
    st.info("🎯 Module active: Indian Patent (IPR) & Prior-Art Agent. Auditing criteria under the Indian Patents Act, 1970.")
elif niche_selection == "Grant Auditor":
    st.info("💰 Module active: SERB / DST Government Grant Alignment Auditor framework.")
else:
    st.info("🔬 Module active: Bioethics & Clinical Trial Regulatory Scout synced against regional CTRI profiles.")

uploaded_file = st.file_uploader(
    "📤 Drag and drop your research manuscript, grant proposal draft, or clinical methodology document:",
    type=["pdf", "docx"],
    help="Supports complete academic drafts in PDF or Microsoft Word formatting."
)

parsed_manuscript_text = ""

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

if st.button("🚀 Initiate Complete Compliance Evaluation", type="primary"):
    if not user_gemini_key.strip():
        st.error("🔑 Access Denied: Please provide your personal Gemini API key in the sidebar to power the app.")
    elif not parsed_manuscript_text.strip():
        st.error("Please upload a valid PDF or DOCX file to execute the compliance evaluation loop.")
    else:
        os.environ["GOOGLE_API_KEY"] = user_gemini_key
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
        if isinstance(audit_report, list) and len(audit_report) > 0:
            actual_text = str(audit_report.get("text", audit_report)) if isinstance(audit_report, dict) else str(audit_report)
        else:
            actual_text = str(audit_report)
                          
        st.success("✨ Regulatory document synthesis successful!")
        
        if is_premium:
            docx_bytes = convert_markdown_to_docx(actual_text)
            safe_niche = niche_selection.replace(' ', '_')
            raw_filename = uploaded_file.name
            clean_filename_base = re.sub(r'[^a-zA-Z0-9_]', '_', raw_filename)
            dynamic_filename = f"{safe_niche}_{clean_filename_base}_Audit_Report.docx"
            
            st.download_button(
                label="📄 Download Official Audit Report as MS Word (.docx)",
                data=docx_bytes,
                file_name=dynamic_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        else:
            st.info("🔒 Microsoft Word (.docx) Official Export feature is locked. Upgrade to Corporate Tier to save files.")
        
        st.markdown("---")
        st.markdown(actual_text)

import streamlit as st
import requests
import io
import base64

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Data Audit Pro | Enterprise SaaS",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS FOR CORPORATE SAAS LOOK
st.markdown("""
    <style>
        /* Hide Streamlit default headers and footers */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Typography */
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            color: #1E3A8A; 
            text-align: center;
            margin-bottom: 0px;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #64748B;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 400;
        }
        .feature-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# 3. INITIALIZE SYSTEM MEMORY (SESSION STATE)
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'user_role' not in st.session_state:
    st.session_state.user_role = None # Can be 'user' or 'guest'
if 'cleaning_results' not in st.session_state:
    st.session_state.cleaning_results = None # Holds data so downloads don't disappear

# Navigation Helper
def change_page(new_page, role=None):
    st.session_state.page = new_page
    if role:
        st.session_state.user_role = role
    if new_page == "login":
        st.session_state.user_role = None
        st.session_state.cleaning_results = None

# ==========================================
# PAGE 1: THE AUTHENTICATION PORTAL
# ==========================================
def render_login_page():
    st.markdown('<div class="hero-title">Data Audit Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Sign in to access the Enterprise Data Quality Engine.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2, tab3 = st.tabs(["🔒 Sign In", "📝 Create Account", "👤 Continue as Guest"])
        
        with tab1:
            st.text_input("Work Email", placeholder="name@company.com")
            st.text_input("Password", type="password")
            # For Phase 1, we let any input pass to simulate authentication
            if st.button("Log In", use_container_width=True, type="primary"):
                change_page("landing", role="user")
                st.rerun()
                
        with tab2:
            st.text_input("Full Name")
            st.text_input("Corporate Email")
            st.text_input("Choose Password", type="password")
            if st.button("Create Account", use_container_width=True):
                st.success("Account created! Logging you in...")
                import time
                time.sleep(1)
                change_page("landing", role="user")
                st.rerun()
                
        with tab3:
            st.info("Guests can view the platform features, but data processing is disabled.")
            if st.button("Enter as Guest", use_container_width=True):
                change_page("landing", role="guest")
                st.rerun()

# ==========================================
# PAGE 2: THE LANDING & INFORMATION PAGE
# ==========================================
def render_landing_page():
    # Top Navigation Bar
    nav1, nav2 = st.columns([4, 1])
    with nav2:
        if st.button("Logout", use_container_width=True):
            change_page("login")
            st.rerun()

    st.markdown('<div class="hero-title">Welcome to the Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">The fastest way to scrub, sanitize, and audit your corporate data.</div>', unsafe_allow_html=True)
    
    # Feature Showcase
    st.markdown("### 🚀 Platform Features")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-box">
            <h4>🧹 Automated Scrubbing</h4>
            <p>Instantly strip hidden whitespaces, standardize date formats (ISO 8601), and deduplicate records with zero coding.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-box">
            <h4>📈 Outlier Filtering</h4>
            <p>Utilize mathematical Z-Score and Interquartile Range (IQR) detection to automatically hunt down impossible anomalies.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-box">
            <h4>📑 Compliance Audits</h4>
            <p>Every transformation is logged. Instantly generate professional PDF audit reports for management and stakeholders.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # The Gatekeeper Logic
    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
    with c_btn2:
        if st.session_state.user_role == "guest":
            st.error("🔒 Guest Accounts cannot process data. Please create a free account to unlock the engine.")
            if st.button("Create Account", use_container_width=True, type="primary"):
                change_page("login")
                st.rerun()
        else:
            if st.button("Launch Dashboard", use_container_width=True, type="primary"):
                change_page("core")
                st.rerun()

# ==========================================
# PAGE 3: THE CORE APPLICATION (Kitchen)
# ==========================================
def render_core_app():
    # Navigation
    nav1, nav2 = st.columns([4, 1])
    with nav1:
        if st.button("← Back to Home"):
            st.session_state.cleaning_results = None # Clear memory on exit
            change_page("landing")
            st.rerun()
    with nav2:
        if st.button("Logout", use_container_width=True):
            change_page("login")
            st.rerun()
            
    st.markdown('<div class="hero-title" style="font-size: 2.2rem;">Data Cleaning Pipeline</div>', unsafe_allow_html=True)
    st.write("")
    
    # MAIN LAYOUT ARCHITECTURE
    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        st.markdown("### 📄 1. Upload Dataset")
        st.info("Supported formats: .CSV, .XLSX (Max size: 200MB)")
        uploaded_file = st.file_uploader("Drop your messy data here", type=["csv", "xlsx"], label_visibility="collapsed")

    with col_right:
        st.markdown("### ⚙️ 2. Pipeline Configurations")
        tab1, tab2, tab3 = st.tabs(["🧹 Cleaning Rules", "📈 Outliers", "💾 Export"])
        
        with tab1:
            remove_duplicates = st.toggle("Remove Exact Duplicates", value=True)
            type_casting = st.toggle("Strip Hidden Whitespace (Text)", value=True)
            standardize_dates = st.toggle("Standardize Date Formats", value=True)
            
            st.markdown("---")
            st.markdown("**Handling Missing Data**")
            null_action = st.selectbox("Text Data Action", ["Do Nothing", "Drop Rows with Missing Values", "Fill Missing Values with Text"])
            fill_value = "Unknown"
            if null_action == "Fill Missing Values with Text":
                fill_value = st.text_input("Imputation Text", value="Unknown")
                
            numeric_null_action = st.selectbox("Numeric Data Action", ["Do Nothing", "Fill with Zero", "Fill with Mean", "Fill with Median"])

        with tab2:
            outlier_detection = st.toggle("Enable Outlier Filtering", value=False)
            outlier_method = "Z-Score"
            if outlier_detection:
                outlier_method = st.selectbox("Detection Methodology", ["Z-Score", "IQR (Interquartile Range)"])
                st.caption("Z-Score removes data 3 standard deviations from the mean.")

        with tab3:
            output_format = st.radio("Final Output Format", ["CSV", "Excel"], horizontal=True)

    # SUBMISSION BUTTON
    st.markdown("---")
    col_button1, col_button2, col_button3 = st.columns([1, 2, 1])

    with col_button2:
        if st.button("🚀 Initialize Cleaning Pipeline", use_container_width=True, type="primary"):
            if uploaded_file is None:
                st.error("⚠️ Please upload a dataset first!")
            else:
                with st.spinner("Analyzing and scrubbing data in the cloud..."):
                    try:
                        # THE BRIDGE
                        API_URL = "http://localhost:8000/upload"
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {
                            "remove_duplicates": remove_duplicates,
                            "null_action": null_action, "fill_value": fill_value,
                            "numeric_null_action": numeric_null_action, "output_format": output_format,
                            "standardize_dates": standardize_dates, "type_casting": type_casting,
                            "outlier_detection": outlier_detection, "outlier_method": outlier_method
                        }
                        
                        response = requests.post(API_URL, files=files, data=data)
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result["status"] == "Success":
                                # MEMORY BANK: Save the result to session state!
                                st.session_state.cleaning_results = {
                                    "metrics": result["metrics"],
                                    "file_data": result["file_data"],
                                    "pdf_data": result["pdf_data"],
                                    "ext": result["file_extension"],
                                    "mime": result["file_mime"],
                                    "name": uploaded_file.name.split('.')[0]
                                }
                            else:
                                st.error(f"⚠️ Engine Error: {result['message']}")
                        else:
                            st.error(f"⚠️ Server offline (Code: {response.status_code})")
                    except Exception as e:
                        st.error(f"⚠️ Critical System Failure: {str(e)}")

    # THE DOWNLOAD FIX: Render results from Memory Bank (Survives Reruns!)
    if st.session_state.cleaning_results is not None:
        res = st.session_state.cleaning_results
        st.success("✅ Cleaned successfully! Check the Audit PDF for details.")
        
        st.markdown("### 📊 Pipeline Results")
        m1, m2, m3 = st.columns(3)
        m1.metric("Final Row Count", res["metrics"]["total_rows"])
        m2.metric("Final Column Count", res["metrics"]["total_columns"])
        m3.metric("System Status", "Pass", delta="Optimized", delta_color="normal")
        
        st.markdown("---")
        st.markdown("### 📥 Download Assets")
        
        dl_col1, dl_col2 = st.columns(2)
        file_bytes = base64.b64decode(res["file_data"])
        pdf_bytes = base64.b64decode(res["pdf_data"])
        
        with dl_col1:
            st.download_button(
                label=f"💾 Download Cleaned Data ({res['ext'].upper()})",
                data=file_bytes,
                file_name=f"cleaned_{res['name']}{res['ext']}",
                mime=res["mime"],
                use_container_width=True
            )
            
        with dl_col2:
            st.download_button(
                label="📄 Download Audit Report (PDF)",
                data=pdf_bytes,
                file_name=f"Audit_Report_{res['name']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ==========================================
# ROUTER: Controls which page to show
# ==========================================
if st.session_state.page == "login":
    render_login_page()
elif st.session_state.page == "landing":
    render_landing_page()
elif st.session_state.page == "core":
    # Extra security check just in case
    if st.session_state.user_role == "guest":
        st.warning("Access Denied.")
        change_page("landing")
        st.rerun()
    else:
        render_core_app()
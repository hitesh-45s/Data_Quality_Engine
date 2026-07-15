import streamlit as st
import requests
import io
import base64
import time
import json
import os

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Data Audit Pro | Enterprise SaaS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS
st.markdown("""
    <style>
        /* Hide Streamlit's default chrome */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        :root {
            --ink: #0F172A;
            --slate: #5B6478;
            --line: #E1E4EC;
            --ledger: #1B3A6B;
            --ledger-dark: #142C52;
            --teal: #0EA37A;
            --teal-dark: #0B8A67;
            --surface: #FFFFFF;
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation: none !important; transition: none !important; }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ---------- Hero band (login + landing) ---------- */
        .hero-band {
            position: relative;
            overflow: hidden;
            background: var(--surface);
            background-image:
                linear-gradient(var(--line) 1px, transparent 1px),
                linear-gradient(90deg, var(--line) 1px, transparent 1px);
            background-size: 28px 28px;
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 52px 32px 44px;
            margin-bottom: 2rem;
        }
        .hero-band::before {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at center, transparent 25%, var(--surface) 88%);
            pointer-events: none;
        }
        .hero-eyebrow-wrap { text-align: center; position: relative; z-index: 1; }
        .hero-eyebrow {
            display: inline-flex; align-items: center; gap: 6px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.72rem;
            letter-spacing: .08em; text-transform: uppercase;
            color: var(--teal-dark); background: rgba(14, 163, 122, 0.10);
            border: 1px solid rgba(14, 163, 122, 0.28);
            padding: 6px 14px; border-radius: 999px; margin-bottom: 18px;
        }
        .hero-title {
            font-family: 'Space Grotesk', sans-serif; font-weight: 700;
            font-size: 2.6rem; letter-spacing: -0.02em; line-height: 1.12;
            color: var(--ink); text-align: center; margin: 0;
            position: relative; z-index: 1;
            animation: fadeInUp .5s ease both;
        }
        .hero-subtitle {
            font-family: 'Inter', sans-serif; font-size: 1.08rem; font-weight: 400;
            color: var(--slate); text-align: center; margin: 14px auto 0; max-width: 560px;
            position: relative; z-index: 1;
            animation: fadeInUp .5s ease .08s both;
        }
        .hero-divider {
            width: 52px; height: 3px; background: var(--teal);
            margin: 22px auto 0; border-radius: 2px; position: relative; z-index: 1;
        }

        /* Compact left-aligned variant for working screens (core app) */
        .page-title {
            font-family: 'Space Grotesk', sans-serif; font-weight: 700;
            font-size: 2rem; letter-spacing: -0.01em; color: var(--ink);
            margin: 0 0 1.5rem 0;
        }
        
        .section-header {
            font-family: 'Space Grotesk', sans-serif; font-weight: 600;
            font-size: 1.25rem; color: var(--ledger);
            margin-bottom: 0.75rem;
        }

        /* ---------- Feature cards ---------- */
        .feature-box {
            padding: 26px 24px; border-radius: 16px; background: var(--surface);
            border: 1px solid var(--line); height: 100%;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .feature-box:hover {
            transform: translateY(-4px);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.09);
            border-color: var(--ledger);
        }
        .feature-icon-badge {
            width: 42px; height: 42px; border-radius: 11px;
            background: linear-gradient(135deg, var(--ledger), var(--teal));
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; margin-bottom: 14px;
        }
        .feature-box h4 {
            font-family: 'Space Grotesk', sans-serif; font-weight: 600;
            font-size: 1.05rem; color: var(--ink); margin: 0 0 8px 0;
        }
        .feature-box p {
            font-family: 'Inter', sans-serif; font-size: 0.92rem; color: var(--slate);
            line-height: 1.6; margin: 0;
        }

        /* ---------- Targeted widget accents ---------- */
        /* Metrics read like ledger figures, not UI copy */
        [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }
        [data-testid="stMetricLabel"] {
            font-family: 'Inter', sans-serif; text-transform: uppercase;
            letter-spacing: .04em; font-size: 0.72rem;
        }
        
        /* Dashboard App Bar */
        .app-bar {
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--line);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .app-bar-title {
            font-family: 'Space Grotesk', sans-serif; 
            font-weight: 700; 
            font-size: 1.4rem; 
            color: var(--ledger);
            text-align: center;
        }

        /* Download buttons get the "verified" teal */
        [data-testid="stDownloadButton"] button {
            background: var(--teal) !important; border-color: var(--teal) !important; color: #fff !important;
        }
        [data-testid="stDownloadButton"] button:hover {
            background: var(--teal-dark) !important; border-color: var(--teal-dark) !important;
        }
        /* Visible keyboard focus (accessibility) */
        button:focus-visible, [role="tab"]:focus-visible, input:focus-visible {
            outline: 2px solid var(--ledger) !important; outline-offset: 2px;
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

# 4. JSON FILE DATABASE HANDLERS (Permanent Local Storage)
DB_FILE = "users_db.json"

def load_users():
    """Reads users from the physical JSON file."""
    if not os.path.exists(DB_FILE):
        default_users = {"admin@company.com": "password123"}
        with open(DB_FILE, "w") as f:
            json.dump(default_users, f)
        return default_users
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_user(email, password):
    """Saves a new user permanently to the JSON file."""
    users = load_users()
    users[email] = password
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

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
    st.markdown("""
        <div class="hero-band">
            <div class="hero-eyebrow-wrap"><span class="hero-eyebrow">🛡️ Data Quality &amp; Compliance</span></div>
            <div class="hero-title">Data Audit Pro</div>
            <div class="hero-subtitle">Sign in to access the Enterprise Data Quality Engine.</div>
            <div class="hero-divider"></div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            tab1, tab2, tab3 = st.tabs(["🔒 Sign In", "📝 Create Account", "👤 Continue as Guest"])

            with tab1:
                # Use .strip() to automatically remove accidental blank spaces!
                login_email = st.text_input("Work Email", placeholder="name@company.com", key="login_email").strip()
                login_pass = st.text_input("Password", type="password", key="login_pass")
                
                if st.button("Log In", use_container_width=True, type="primary"):
                    users_db = load_users() # Load from physical file!
                    if not login_email or not login_pass:
                        st.error("⚠️ Please enter both your email and password.")
                    elif login_email in users_db and users_db[login_email] == login_pass:
                        change_page("landing", role="user")
                        st.rerun()
                    else:
                        st.error("⚠️ Invalid email or password. Please try again.")

            with tab2:
                reg_name = st.text_input("Full Name", key="reg_name").strip()
                reg_email = st.text_input("Corporate Email", key="reg_email").strip()
                reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
                
                if st.button("Create Account", use_container_width=True):
                    users_db = load_users() # Load from physical file!
                    if not reg_name or not reg_email or not reg_pass:
                        st.error("⚠️ Please fill out all required fields.")
                    elif reg_email in users_db:
                        st.error("⚠️ An account with this email already exists!")
                    else:
                        # Save the new user permanently to the hard drive!
                        save_user(reg_email, reg_pass)
                        st.success("✅ Account created successfully! Logging you in...")
                        time.sleep(1.5)
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

    st.markdown("""
        <div class="hero-band">
            <div class="hero-eyebrow-wrap"><span class="hero-eyebrow">🛡️ Data Quality &amp; Compliance</span></div>
            <div class="hero-title">Welcome to the Engine</div>
            <div class="hero-subtitle">The fastest way to scrub, sanitize, and audit your corporate data.</div>
            <div class="hero-divider"></div>
        </div>
    """, unsafe_allow_html=True)

    # Feature Showcase
    st.markdown("### 🚀 Platform Features")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon-badge">🧹</div>
            <h4>Automated Scrubbing</h4>
            <p>Instantly strip hidden whitespaces, standardize date formats (ISO 8601), and deduplicate records with zero coding.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon-badge">📈</div>
            <h4>Outlier Filtering</h4>
            <p>Utilize mathematical Z-Score and Interquartile Range (IQR) detection to automatically hunt down impossible anomalies.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon-badge">📑</div>
            <h4>Compliance Audits</h4>
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
    # 1. Custom Top App Bar
    st.markdown("<div class='app-bar'>", unsafe_allow_html=True)
    nav1, nav2, nav3 = st.columns([1, 6, 1])
    with nav1:
        if st.button("← Home", use_container_width=True):
            st.session_state.cleaning_results = None # Clear memory on exit
            change_page("landing")
            st.rerun()
    with nav2:
        st.markdown("<div class='app-bar-title'>Data Quality Dashboard</div>", unsafe_allow_html=True)
    with nav3:
        if st.button("Logout 🚪", use_container_width=True):
            change_page("login")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # MAIN LAYOUT ARCHITECTURE
    col_left, col_right = st.columns([1, 1.3], gap="large")

    with col_left:
        st.markdown("<div class='section-header'>📄 1. Data Ingestion</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<p style='font-size:0.9rem; color: var(--slate);'>Upload your raw dataset securely. Supported formats include .CSV and .XLSX (Max size: 200MB).</p>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Drop your messy data here", type=["csv", "xlsx"], label_visibility="collapsed")
            if uploaded_file:
                st.success(f"System Ready: {uploaded_file.name}", icon="✅")

    with col_right:
        st.markdown("<div class='section-header'>⚙️ 2. Pipeline Configurations</div>", unsafe_allow_html=True)
        with st.container(border=True):
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

    # SUBMISSION BUTTON (Centered Action Zone)
    st.markdown("<br>", unsafe_allow_html=True)
    col_space1, col_button, col_space2 = st.columns([1.5, 2, 1.5])

    with col_button:
        if st.button("🚀 Initialize Cleaning Pipeline", use_container_width=True, type="primary"):
            if uploaded_file is None:
                st.error("⚠️ Please upload a dataset to begin processing.")
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
        
        st.markdown("<hr style='margin: 3rem 0; border-color: var(--line);'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>📊 Audit & Transformation Results</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.success("✅ Dataset successfully cleaned and standardized. Audit report generated.")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Final Row Count", res["metrics"]["total_rows"], delta="Processed", delta_color="normal")
            m2.metric("Final Column Count", res["metrics"]["total_columns"], delta="Standardized", delta_color="normal")
            m3.metric("System Status", "Pass", delta="Ready for Export", delta_color="normal")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📥 Download Assets")

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
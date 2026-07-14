import streamlit as st
import requests 
import base64    

# 1. Set up the page configuration
st.set_page_config(page_title="Data Quality Engine", layout="wide")

st.title("⚙️ Automated Data Quality Engine")
st.write("Welcome! This microservice automatically ingests, sanitizes, and profiles datasets.")
st.divider()

# --- NEW: INITIALIZE MEMORY VAULT ---
# This prevents our download buttons from disappearing when clicked!
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None

st.header("1. Data Ingestion")
uploaded_file = st.file_uploader("Upload your messy dataset (CSV or Excel)", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' successfully loaded into UI memory!")
    st.divider()
    
    st.header("2. Data Cleaning Rules (The Pipeline)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Standard Operations")
        remove_duplicates = st.checkbox("Remove Duplicate Rows", value=True)
        
        st.write("Text Missing Values (Nulls) Strategy:")
        null_action = st.radio(
            "Choose an action for text:",
            ("Do Nothing", "Drop Rows with Missing Values", "Fill Missing Values with Text"),
            label_visibility="collapsed"
        )
        fill_value = ""
        if null_action == "Fill Missing Values with Text":
            fill_value = st.text_input("Fill empty cells with this text:", value="Unknown")
            
        st.write("Numeric Missing Values Strategy:")
        numeric_null_action = st.radio(
            "How should we handle missing numbers?",
            ("Do Nothing", "Fill with Zero", "Fill with Mean", "Fill with Median"),
            label_visibility="collapsed"
        )
        
        st.write("Download Format:")
        output_format = st.radio(
            "Choose your cleaned output format:",
            ("CSV", "Excel"),
            label_visibility="collapsed"
        )

    with col2:
        st.subheader("Advanced Operations")
        standardize_dates = st.checkbox("Standardize Date Formats")
        type_casting = st.checkbox("Fix Data Types (e.g., text to numbers)")
        outlier_detection = st.checkbox("Detect & Flag Outliers")
        if outlier_detection:
            outlier_method = st.radio("Outlier Method:", ("Z-Score", "IQR (Interquartile Range)"))
            
    st.divider()
    
    # --- NETWORK BRIDGE LOGIC ---
    if st.button("🚀 Run Cleaning Engine", type="primary"):
        with st.spinner("Transmitting data to the Kitchen (FastAPI)..."):
            
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            cleaning_rules = {
                "remove_duplicates": remove_duplicates,
                "null_action": null_action,
                "fill_value": fill_value,
                "numeric_null_action": numeric_null_action,
                "output_format": output_format,
                "standardize_dates": standardize_dates,
                "type_casting": type_casting,
                "outlier_detection": outlier_detection,
                "outlier_method": outlier_method if outlier_detection else "Z-Score"
            }
            
            try:
                response = requests.post("http://localhost:8000/upload", files=files, data=cleaning_rules)
                
                if response.status_code == 200:
                    api_reply = response.json()
                    if api_reply.get("status") == "Success":
                        # Save the results securely into the memory vault!
                        st.session_state.pipeline_results = api_reply
                    else:
                        st.error(f"Backend Error: {api_reply.get('message')}")
                else:
                    st.error("The API received the request but something went wrong.")
            
            except requests.exceptions.ConnectionError:
                st.error("🚨 CRITICAL ERROR: Could not connect to FastAPI. Is your uvicorn server running?")

    # --- RENDER RESULTS FROM VAULT ---
    # Because we use the vault, these buttons will survive being clicked!
    if st.session_state.pipeline_results and st.session_state.pipeline_results.get("status") == "Success":
        api_reply = st.session_state.pipeline_results
        
        st.success(f"Backend Server Reply: {api_reply['message']}")
        
        st.divider()
        st.subheader("3. Delivery & Audit")
        dl_col1, dl_col2 = st.columns(2)
        
        with dl_col1:
            file_bytes = base64.b64decode(api_reply["file_data"])
            file_name = f"cleaned_data{api_reply['file_extension']}"
            st.download_button(
                label=f"⬇️ Download Cleaned Data ({api_reply['file_extension']})",
                data=file_bytes,
                file_name=file_name,
                mime=api_reply["file_mime"],
                type="primary"
            )
            
        with dl_col2:
            pdf_bytes = base64.b64decode(api_reply["pdf_data"])
            st.download_button(
                label="📑 Download Compliance Audit Report (.pdf)",
                data=pdf_bytes,
                file_name="data_audit_report.pdf",
                mime="application/pdf",
                type="secondary"
            )

else:
    # Clear the vault if the user removes the file
    st.session_state.pipeline_results = None
    st.info("Awaiting file upload... Please drop a CSV file to begin.")
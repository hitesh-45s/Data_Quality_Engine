import streamlit as st

# 1. Set up the page configuration
st.set_page_config(page_title="Data Quality Engine", layout="wide")

# 2. Main Header
st.title("⚙️ Automated Data Quality Engine")
st.write("Welcome! This microservice automatically ingests, sanitizes, and profiles datasets.")
st.divider()

# 3. Data Ingestion Section
st.header("1. Data Ingestion")
uploaded_file = st.file_uploader("Upload your messy dataset (CSV format)", type=["csv"])

# 4. The Engineering Pipeline UI
if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' successfully loaded into memory!")
    st.divider()
    
    st.header("2. Data Cleaning Rules (The Pipeline)")
    st.write("Configure the operations you want the engine to apply:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Standard Operations")
        # Duplicates is an independent toggle
        remove_duplicates = st.checkbox("Remove Duplicate Rows", value=True)
        
        # Null handling has mutually exclusive choices, so we use a radio button inside the step
        st.write("Missing Values (Nulls) Strategy:")
        null_action = st.radio(
            "Choose an action:",
            ("Do Nothing", "Drop Rows with Missing Values", "Fill Missing Values with Text"),
            label_visibility="collapsed"
        )
        if null_action == "Fill Missing Values with Text":
            fill_value = st.text_input("Fill empty cells with this text:", value="Unknown")

    with col2:
        st.subheader("Advanced Operations")
        # These are the new enterprise features you requested!
        standardize_dates = st.checkbox("Standardize Date Formats")
        type_casting = st.checkbox("Fix Data Types (e.g., text to numbers)")
        outlier_detection = st.checkbox("Detect & Flag Outliers")
        
        # If they turn on Outliers, we ask them WHICH advanced math method they want to use
        if outlier_detection:
            outlier_method = st.radio("Outlier Method:", ("Z-Score", "IQR (Interquartile Range)"))

    st.divider()
    
    if st.button("🚀 Run Cleaning Engine", type="primary"):
        st.info("Pipeline configured! We will connect this UI to the Polars Data Engine in Week 3.")

else:
    st.info("Awaiting file upload... Please drop a CSV file to begin.")
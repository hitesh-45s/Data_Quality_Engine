import streamlit as st

# 1. Set up the page configuration
st.set_page_config(page_title="Data Quality Engine", layout="wide")

# 2. Main Header
st.title("⚙️ Automated Data Quality Engine")
st.write("Welcome! This microservice automatically ingests, sanitizes, and profiles datasets.")

st.divider() # Adds a clean visual line across the webpage

# 3. Data Ingestion Section (The Doorway)
st.header("1. Data Ingestion")

# Create the drag-and-drop file uploader widget
uploaded_file = st.file_uploader(
    label="Upload your messy dataset (CSV format)", 
    type=["csv"]
)

# 4. Verification & Cleaning Rules UI
if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' successfully loaded into memory!")
    
    st.divider()
    
    st.header("2. Data Cleaning Rules")
    st.write("Select the sanitization operations you want the engine to apply:")
    
    # We use columns to make the UI look professional and organized
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Standard Operations")
        remove_duplicates = st.checkbox("Remove Duplicate Rows", value=True) # Checked by default
        remove_nulls = st.checkbox("Drop Rows with Missing Values")
        
    with col2:
        st.subheader("Advanced Operations")
        fill_nulls = st.checkbox("Fill Missing Values (Imputation)")
        
        # If the user checks the box above, show them a text input!
        if fill_nulls:
            fill_value = st.text_input("Fill empty cells with this text:", value="Unknown")

    st.divider()
    
    # The final trigger button
    if st.button("🚀 Run Cleaning Engine", type="primary"):
        st.info("Awesome! The UI is working perfectly. We will connect this button to the backend engine in Week 3.")
   

else:
    st.info("Awaiting file upload... Please drop a CSV file to begin.")
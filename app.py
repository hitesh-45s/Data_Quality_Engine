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

# 4. Verification Logic
if uploaded_file is not None:
    # If a file is detected, display a success success status
    st.success("File successfully uploaded to buffer memory!")
    
    # Display the file metadata to prove the system reads it
    st.subheader("File Metadata Log")
    st.text(f"File Name: {uploaded_file.name}")
    st.text(f"File Size: {uploaded_file.size} Bytes")
    st.text(f"File Type: {uploaded_file.type}")
else:
    # If no file is uploaded yet, show an informational warning
    st.info("Awaiting file upload... Please drop a CSV file to begin.")
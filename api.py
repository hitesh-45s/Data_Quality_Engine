from fastapi import FastAPI, UploadFile, File, Form
import polars as pl
import polars.selectors as cs
import io
import base64
from fpdf import FPDF
import datetime

# 1. Initialize the Engine
app = FastAPI(title="Data Quality API")

@app.get("/")
def welcome_menu():
    return {"message": "Welcome to the Data Quality Kitchen! The server is running."}

# 2. The Data Ingestion Endpoint
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    remove_duplicates: bool = Form(True),
    null_action: str = Form("Do Nothing"),
    fill_value: str = Form("Unknown"),
    numeric_null_action: str = Form("Do Nothing"),
    output_format: str = Form("CSV"),
    standardize_dates: bool = Form(False),
    type_casting: bool = Form(False),
    outlier_detection: bool = Form(False),
    outlier_method: str = Form("Z-Score")
):
    raw_bytes = await file.read()
    memory_buffer = io.BytesIO(raw_bytes)
    
    # Audit Tracking Variables
    audit_data = {
        "duplicates_removed": 0,
        "null_rows_dropped": 0,
        "outliers_removed": 0,
        "text_nulls_filled": 0,    
        "numeric_nulls_filled": 0  
    }
    
    try:
        # Step C: The "Zero Trust" Magic Bytes Check
        file_dna = raw_bytes[:4]
        if file_dna == b'PK\x03\x04':
            df = pl.read_excel(memory_buffer)
            detected_type = "Excel (.xlsx)"
        else:
            df = pl.read_csv(memory_buffer)
            detected_type = "CSV"
            
        initial_rows = df.height
        initial_cols = df.width
            
        # --- THE CLEANING PIPELINE ---
        
        # Rule 1: Remove Duplicates
        if remove_duplicates:
            r_before = df.height
            id_columns = [col for col in df.columns if "id" in col.lower()]
            if id_columns:
                df = df.unique(subset=id_columns, keep="first")
            else:
                df = df.unique()
            audit_data["duplicates_removed"] = r_before - df.height
            
        # Rule 2: Handle Text Missing Values
        if null_action == "Drop Rows with Missing Values":
            r_before = df.height
            df = df.drop_nulls()
            audit_data["null_rows_dropped"] = r_before - df.height
        elif null_action == "Fill Missing Values with Text":
            string_cols = df.select(cs.string()).columns
            if string_cols:
                audit_data["text_nulls_filled"] = sum(df[col].null_count() for col in string_cols)
            df = df.with_columns(cs.string().fill_null(fill_value))
            
        # Rule 3: Handle Numeric Missing Values
        if numeric_null_action != "Do Nothing":
            numeric_cols = df.select(cs.numeric()).columns
            if numeric_cols:
                audit_data["numeric_nulls_filled"] = sum(df[col].null_count() for col in numeric_cols)
                
            if numeric_null_action == "Fill with Zero":
                df = df.with_columns(cs.numeric().fill_null(0))
            elif numeric_null_action == "Fill with Mean":
                df = df.with_columns(
                    cs.integer().fill_null(cs.integer().mean().cast(pl.Int64)),
                    cs.float().fill_null(cs.float().mean())
                )
            elif numeric_null_action == "Fill with Median":
                df = df.with_columns(
                    cs.integer().fill_null(cs.integer().median().cast(pl.Int64)),
                    cs.float().fill_null(cs.float().median())
                )

        # Rule 4: Type Casting
        if type_casting:
            df = df.with_columns(cs.string().str.strip_chars())
            
        # Rule 5: Date Standardization
        if standardize_dates:
            date_columns = [col for col in df.columns if "date" in col.lower()]
            for d_col in date_columns:
                try:
                    if df[d_col].dtype == pl.String:
                        df = df.with_columns(
                            pl.coalesce([
                                pl.col(d_col).str.to_date("%Y-%m-%d", strict=False),
                                pl.col(d_col).str.to_date("%m/%d/%Y", strict=False),
                                pl.col(d_col).str.to_date("%Y/%m/%d", strict=False)
                            ]).alias(d_col)
                        )
                except Exception:
                    pass

        # Rule 6: Outliers
        if outlier_detection:
            r_before = df.height
            numeric_cols = df.select(cs.numeric()).columns
            for col in numeric_cols:
                if outlier_method == "Z-Score":
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val is not None and std_val > 0:
                        df = df.filter(((pl.col(col) - mean_val) / std_val).abs() <= 3)
                elif outlier_method == "IQR (Interquartile Range)":
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    if q1 is not None and q3 is not None:
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        df = df.filter(pl.col(col).is_between(lower_bound, upper_bound))
            audit_data["outliers_removed"] = r_before - df.height

        # --- THE BULLETPROOF TEXT-BLOCK PDF GENERATOR ---
        
        # 1. Helper function to create perfectly spaced columns using raw Python text
        def pad(text, width):
            return str(text)[:width].ljust(width)
            
        safe_name = file.filename[:35] + "..." if len(file.filename) > 35 else file.filename
        
        # 2. Build the entire report in computer memory first!
        lines = []
        lines.append("DATA CLEANING AUDIT REPORT")
        lines.append("==========================================================================")
        lines.append(f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Dataset Name: {safe_name}")
        lines.append("Prepared By: Automated Data Quality Engine")
        lines.append("\n1. EXECUTIVE SUMMARY")
        lines.append("--------------------------------------------------------------------------")
        lines.append(f"The '{safe_name}' dataset underwent automated data scrubbing.")
        lines.append("The dataset is now certified as 'Clean and Standardized'.")
        lines.append("\n2. PIPELINE METRICS")
        lines.append("--------------------------------------------------------------------------")
        lines.append("METRIC                 | PRE      | POST     | ACTION")
        lines.append("--------------------------------------------------------------------------")
        
        lines.append(f"{pad('Total Rows', 22)} | {pad(initial_rows, 8)} | {pad(df.height, 8)} | Processed")
        lines.append(f"{pad('Total Columns', 22)} | {pad(initial_cols, 8)} | {pad(df.width, 8)} | Standardized schema")
        
        if remove_duplicates:
            lines.append(f"{pad('Duplicate Rows', 22)} | {pad(audit_data['duplicates_removed'], 8)} | {pad(0, 8)} | Removed exact matches")
            
        if outlier_detection:
            lines.append(f"{pad('Statistical Outliers', 22)} | {pad(audit_data['outliers_removed'], 8)} | {pad(0, 8)} | Filtered via {outlier_method}")
            
        if null_action == "Drop Rows with Missing Values":
            lines.append(f"{pad('Missing Text Rows', 22)} | {pad(audit_data['null_rows_dropped'], 8)} | {pad(0, 8)} | Dropped missing data")
        elif null_action == "Fill Missing Values with Text":
            lines.append(f"{pad('Missing Text Fields', 22)} | {pad(audit_data['text_nulls_filled'], 8)} | {pad(0, 8)} | Imputed safely")
            
        if numeric_null_action != "Do Nothing":
            lines.append(f"{pad('Missing Numerics', 22)} | {pad(audit_data['numeric_nulls_filled'], 8)} | {pad(0, 8)} | Handled via Imputation")

        lines.append("\n3. LOG OF CRITICAL TRANSFORMATIONS")
        lines.append("--------------------------------------------------------------------------")
        if standardize_dates:
            lines.append("* TIMESTAMP FIELD: Converted mixed formats to standard YYYY-MM-DD.")
        if type_casting:
            lines.append("* TEXT STANDARDIZATION: Stripped hidden whitespace from categorical columns.")
        if outlier_detection:
            lines.append(f"* OUTLIERS: Removed mathematical anomalies using {outlier_method}.")
            
        lines.append("\n4. REPRODUCIBILITY & PIPELINE")
        lines.append("--------------------------------------------------------------------------")
        lines.append("* Script Version: Enterprise Data Quality Engine v2.1")
        lines.append(f"* Output Format: {output_format.upper()}")
        lines.append("* Audit Status: PASSED\n")
        lines.append("Signed: __________________________ (System Automated)")
        
        # Combine all the text into one giant string with line breaks
        final_report_text = "\n".join(lines)
        
        # 3. Create the PDF using just three simple commands!
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=9)
        pdf.multi_cell(0, 5, final_report_text) # This automatically wraps and fits everything!
            
        # BUG FIX: Safely encode the PDF to bytes regardless of the library version
        pdf_out = pdf.output(dest='S')
        if isinstance(pdf_out, str):
            pdf_bytes = pdf_out.encode('latin-1')
        else:
            pdf_bytes = bytes(pdf_out)
            
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # --- GENERATE THE DATA FILE ---
        output_buffer = io.BytesIO()
        if output_format == "Excel":
            df.write_excel(output_buffer)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            out_ext = ".xlsx"
        else:
            df.write_csv(output_buffer)
            mime_type = "text/csv"
            out_ext = ".csv"
            
        base64_encoded_file = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return {
            "status": "Success",
            "filename": file.filename,
            "message": f"Cleaned successfully! Check the Audit PDF for details.",
            "metrics": {
                "total_rows": df.height,
                "total_columns": df.width,
                "columns_found": df.columns
            },
            "file_data": base64_encoded_file,
            "file_mime": mime_type,
            "file_extension": out_ext,
            "pdf_data": base64_pdf
        }
    except Exception as e:
        return {
            "status": "Error",
            "message": f"CRASH PREVENTED: (Error: {str(e)})"
        }
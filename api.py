from fastapi import FastAPI, UploadFile, File


# 1. Hire the Kitchen Manager
app = FastAPI(title="Data Quality API")

# 2. Open a doorway (Create an Endpoint)
@app.get("/")
def welcome_menu():
    # 3. What the kitchen hands you when you knock on the door
    return {"message": "Welcome to the Data Quality Kitchen! The server is running."}

# 3. Open the Loading Dock (To receive files from Streamlit)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # This reads the name of the file the Waiter just handed us
    file_name = file.filename
    
    # In the real world, we would send this to Polars now. 
    # For today, we just send a success message back to the Waiter!
    return {
        "status": "Success",
        "message": f"Kitchen received '{file_name}' perfectly!",
        "filename": file_name
    }
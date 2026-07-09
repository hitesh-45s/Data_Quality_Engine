from fastapi import FastAPI

# 1. Hire the Kitchen Manager
app = FastAPI(title="Data Quality API")

# 2. Open a doorway (Create an Endpoint)
@app.get("/")
def welcome_menu():
    # 3. What the kitchen hands you when you knock on the door
    return {"message": "Welcome to the Data Quality Kitchen! The server is running."}
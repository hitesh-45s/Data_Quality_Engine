import csv
import random
from datetime import datetime, timedelta

def generate_messy_data(filename="messy_enterprise_data.csv", num_records=500):
    departments = ["Sales", "IT", "Marketing", "HR", "Finance", "Engineering"]
    
    # We will hold our generated rows here
    data = []
    
    # 1. Generate Base Records
    for i in range(1, num_records + 1):
        customer_id = f"CUST-{i:04d}"
        
        # Base realistic logic
        age = random.randint(22, 65)
        income = random.randint(40000, 120000)
        credit_score = random.randint(500, 850)
        department = random.choice(departments)
        
        # Generate a clean date first
        start_date = datetime(2020, 1, 1)
        random_days = random.randint(0, 1500)
        clean_date = start_date + timedelta(days=random_days)
        date_str = clean_date.strftime("%Y-%m-%d") # Standard format
        
        # --- INJECTING "MESSY" DATA TRAPS FOR YOUR ENGINE TO CATCH ---
        
        # Trap 1: Outliers (Z-Score & IQR testing)
        if random.random() < 0.03:
            age = random.choice([999, -15, 1000]) # Impossible ages
        if random.random() < 0.03:
            income = random.choice([5000000, -5000]) # Impossible incomes
            
        # Trap 2: Missing Numeric Values (Null Math testing)
        if random.random() < 0.05:
            age = "" # Engine should fill with Mean/Median
        if random.random() < 0.05:
            credit_score = "" 
            
        # Trap 3: Missing Text Values (String Null testing)
        if random.random() < 0.05:
            department = "" # Engine should fill with "Unknown"
            
        # Trap 4: Hidden Whitespace in Text (Type Casting testing)
        if random.random() < 0.10 and department != "":
            department = f"   {department}  " # Engine should strip this to clean text
            
        # Trap 5: Messy Date Formats (Date Standardization testing)
        trap_chance = random.random()
        if trap_chance < 0.05:
            # Change format from YYYY-MM-DD to MM/DD/YYYY
            date_str = clean_date.strftime("%m/%d/%Y") 
        elif trap_chance < 0.10:
            # Change format from YYYY-MM-DD to YYYY/MM/DD
            date_str = clean_date.strftime("%Y/%m/%d")
            
        data.append([customer_id, age, income, credit_score, department, date_str])

    # Trap 6: Inject Duplicates (Smart ID Deduplication testing)
    # Grab 25 random rows we already made and duplicate them exactly
    duplicates = random.choices(data, k=25)
    data.extend(duplicates)

    # Shuffle the data so duplicates are scattered randomly, not just at the bottom
    random.shuffle(data)
    
    # 2. Write to CSV
    headers = ["Customer_ID", "Age", "Income", "Credit_Score", "Department", "Join_Date"]
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
        
    print(f"✅ Success! Generated {len(data)} rows in '{filename}'!")
    print("This dataset includes hidden nulls, extreme outliers, bad dates, and whitespace traps.")

if __name__ == "__main__":
    generate_messy_data()
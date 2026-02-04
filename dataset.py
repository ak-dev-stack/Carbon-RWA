import pandas as pd
import numpy as np

# --- 1. SETUP & REPRODUCIBILITY ---
# Setting a seed ensures your 'random' numbers are the same every time you show it.
np.random.seed(42)
n_loans = 2000 # Representative of a specific commercial banking portfolio (~$50B)

# --- 2. SYSTEM A: CORE BANKING SYSTEM (Financial Data) ---
# Simulating the bank's main ledger. 
# We focus on Indian heavy industries where Transition Risk is highest.
sectors = ['Power (Thermal)', 'Steel & Cement', 'Infra & Roads', 'IT Services', 'Pharma']

df_fin = pd.DataFrame({
    'Loan_ID': range(10001, 10001 + n_loans),
    'Borrower_ID': range(1, n_loans + 1),
    'Sector': np.random.choice(sectors, n_loans, p=[0.25, 0.20, 0.25, 0.15, 0.15]),
    'Exposure_INR_Cr': np.random.lognormal(5, 1.2, n_loans), # Log-normal distribution matches real loan sizes
    'Maturity_Years': np.random.uniform(1, 10, n_loans),
    'Interest_Rate': np.random.uniform(0.08, 0.14, n_loans), # 8-14% is typical for Indian Corp credit
    'LGD': 0.45 # Standard Basel Foundation Loss Given Default
})

# --- 3. SYSTEM B: EXTERNAL ESG VENDOR (Climate Data) ---
# Simulating data from a provider like S&P or MSCI.
# Logic: 'Brown' sectors (Power) have high emissions; 'Green' (IT) have low.
def get_esg_profile(sector):
    if sector == 'Power (Thermal)': 
        # High Carbon, Variable Readiness (some old plants, some modern)
        return np.random.normal(950, 100), np.random.beta(2, 5) 
    elif sector == 'Steel & Cement': 
        # Hard-to-abate sector
        return np.random.normal(1800, 200), np.random.beta(3, 4) 
    elif sector == 'IT Services': 
        # Low Carbon, High Readiness
        return np.random.normal(20, 5), np.random.beta(8, 2)    
    else: 
        # General Economy
        return np.random.normal(200, 50), np.random.beta(5, 5) 

esg_metrics = df_fin['Sector'].apply(get_esg_profile)

df_esg = pd.DataFrame({
    'Borrower_ID': df_fin['Borrower_ID'],
    'Carbon_Intensity_Scope1_2': [x[0] for x in esg_metrics], # Metric: tCO2e / $ Revenue
    'Transition_Readiness_Score': [x[1] for x in esg_metrics] # 0.0 (Bad) to 1.0 (Good)
})

# --- 4. EXPORT TO CSV (Simulating Database Tables) ---
df_fin.to_csv('raw_financial_table.csv', index=False)
df_esg.to_csv('raw_esg_table.csv', index=False)

print("✅ Data Generation Complete.")
print("   - 'raw_financial_table.csv' created (System A)")
print("   - 'raw_esg_table.csv' created (System B)")
import pandas as pd
import numpy as np
import sqlite3
from scipy.stats import norm
from scipy.optimize import linprog

# ==============================================================================
# PART A: SQL DATA ENGINEERING (The "1 Year Experience" Layer)
# ==============================================================================
print("🔄 Loading Data into In-Memory SQL Database...")
conn = sqlite3.connect(':memory:')
try:
    pd.read_csv('raw_financial_table.csv').to_sql('raw_financial_table', conn, index=False)
    pd.read_csv('raw_esg_table.csv').to_sql('raw_esg_table', conn, index=False)
except FileNotFoundError:
    print("❌ Error: Raw CSVs not found. Run '1_data_gen.py' first.")
    exit()

# Executing the Advanced Join & Rename Logic
sql_query = """
SELECT 
    f.Sector, 
    f.Exposure_INR_Cr, 
    f.Maturity_Years, 
    f.Interest_Rate, 
    f.LGD,
    e.Carbon_Intensity_Scope1_2 AS Carbon_Intensity, 
    e.Transition_Readiness_Score AS Transition_Readiness
FROM raw_financial_table f
JOIN raw_esg_table e ON f.Borrower_ID = e.Borrower_ID
"""
df = pd.read_sql_query(sql_query, conn)
print(f"✅ SQL Join Successful. Loaded {len(df)} facilities.")

# ==============================================================================
# PART B: BASEL III RISK ENGINE (The "Quant" Layer)
# ==============================================================================
# 1. Calibrate Base Probability of Default (PD)
# Logic: Dirty companies are inherently riskier in the long term
df['Base_PD'] = np.random.beta(1.5, 30, len(df)) + (df['Carbon_Intensity'] / 100000)

# 2. Basel III AIRB Formula (Asymptotic Single Risk Factor)
# This calculates the Regulatory Capital (K) required for each loan
def calculate_rwa(exposure, pd_val, lgd, maturity):
    # Regulatory Floor: PD cannot be 0
    pd_val = np.maximum(pd_val, 0.0003)
    
    # Asset Correlation (R) for Corporates (Basel Formula)
    r = 0.12 * ((1 - np.exp(-50 * pd_val)) / (1 - np.exp(-50))) + \
        0.24 * (1 - ((1 - np.exp(-50 * pd_val)) / (1 - np.exp(-50))))
    
    # Maturity Adjustment (b)
    b = (0.11852 - 0.05478 * np.log(pd_val)) ** 2
    
    # Capital Charge (K) - The "Worst Case" Loss at 99.9% Confidence
    term1 = norm.ppf(pd_val)
    term2 = norm.ppf(0.999) 
    k = (lgd * norm.cdf((term1 + np.sqrt(r) * term2) / np.sqrt(1 - r)) - (pd_val * lgd)) * \
        (1 + (maturity - 2.5) * b) / (1 - 1.5 * b)
        
    return exposure * k * 12.5 # Convert to RWA

# Calculate Baseline State
df['Current_RWA'] = calculate_rwa(df['Exposure_INR_Cr'], df['Base_PD'], df['LGD'], df['Maturity_Years'])
df['Current_Capital'] = df['Current_RWA'] * 0.105 # 10.5% CET1 Ratio

# ==============================================================================
# PART C: STRESS TESTING & OPTIMIZATION (The "Consultant" Layer)
# ==============================================================================
print("⚡ Applying NGFS Disorderly Transition Scenario ($50/ton Carbon Tax)...")

# 1. Apply Shock
# High Carbon + Low Readiness = PD Spikes massively
carbon_tax = 4200 # INR per ton
shock_impact = (df['Carbon_Intensity'] * carbon_tax) / 1000000 
df['Stressed_PD'] = df['Base_PD'] * (1 + (shock_impact * (1 - df['Transition_Readiness'])))

# IMPORTANT: Cap PD at 99.9% to prevent math errors (Infinity)
df['Stressed_PD'] = np.minimum(df['Stressed_PD'], 0.999)

# 2. Recalculate Financials under Stress
df['Stressed_RWA'] = calculate_rwa(df['Exposure_INR_Cr'], df['Stressed_PD'], df['LGD'], df['Maturity_Years'])
df['Stressed_Capital'] = df['Stressed_RWA'] * 0.105
df['Net_Income'] = (df['Exposure_INR_Cr'] * df['Interest_Rate']) - (df['Exposure_INR_Cr'] * df['Stressed_PD'] * df['LGD'])
df.fillna(0, inplace=True) # Handle any math anomalies

# 3. Run Optimization (SciPy Linear Programming)
# Goal: Maximize Profit
# Constraint 1: Capital Check (Can't raise infinite capital)
# Constraint 2: Volume Check (Must keep 85% of business - The "Realistic" Constraint)

print("⚙️ Running Linear Optimization Solver...")
c = -1 * df['Net_Income'].values # Negative because we Minimize

A_ub = [
    df['Stressed_Capital'].values,          # Capital Constraint
    -1 * df['Exposure_INR_Cr'].values       # Volume Constraint (Negative for >=)
]
b_ub = [
    df['Current_Capital'].sum() * 1.10,     # Max Capital: 110% of current
    -1 * df['Exposure_INR_Cr'].sum() * 0.85 # Min Volume: 85% of current
]
bounds = [(0, 1) for _ in range(len(df))]   # Keep or Exit (Continuous)

res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

if res.success:
    df['Optimized_Retention'] = res.x
    df['Strategy'] = np.where(df['Optimized_Retention'] < 0.1, 'Exit', 'Hold')
    
    # Calculate ROE Impact
    base_roe = df['Net_Income'].sum() / df['Stressed_Capital'].sum()
    opt_roe = (df['Net_Income'] * res.x).sum() / (df['Stressed_Capital'] * res.x).sum()
    
    print("-" * 40)
    print(f"✅ Optimization Successful")
    print(f"📉 Stressed ROE (Baseline): {base_roe:.2%}")
    print(f"📈 Optimized ROE (Target):  {opt_roe:.2%} (Capital Efficient)")
    print("-" * 40)
    
    df.to_csv('final_strategy_output.csv', index=False)
else:
    print("❌ Optimization Failed:", res.message)
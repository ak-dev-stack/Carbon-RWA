import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

# 1. Load Results
try:
    df = pd.read_csv('final_strategy_output.csv')
except FileNotFoundError:
    print("❌ Error: Results file not found. Run Step 3 first.")
    exit()

# 2. Prepare Data (Sample for clean visualization)
df_viz = df.sample(n=min(500, len(df)), random_state=42).copy()
df_viz['RAROC'] = df_viz['Net_Income'] / df_viz['Stressed_Capital']

# 3. Apply the "Quadrant" Logic for Colors
# Red = Exit
# Yellow = High Carbon but Profitable (Transition Opportunity)
# Green = Low Carbon & Profitable
conditions = [
    (df_viz['Strategy'] == 'Exit'),
    (df_viz['Carbon_Intensity'] > 1200) & (df_viz['Strategy'] == 'Hold'),
    (df_viz['Strategy'] == 'Hold')
]
choices = ['Divest (Value Destroyer)', 'Transition Opportunity', 'Green Leader']
df_viz['Category'] = np.select(conditions, choices, default='Green Leader')

# 4. Generate the Chart
plt.figure(figsize=(14, 8))
sns.set_style("whitegrid")

scatter = sns.scatterplot(
    data=df_viz, 
    x='Carbon_Intensity', 
    y='RAROC', 
    size='Exposure_INR_Cr', 
    hue='Category', 
    sizes=(50, 800), 
    alpha=0.75,
    palette={
        'Divest (Value Destroyer)': '#E74C3C',    # Red
        'Transition Opportunity': '#F1C40F',      # Gold/Orange
        'Green Leader': '#2ECC71'                 # Green
    }
)

# 5. Add Strategic Lines & Limits (The "Pro" Touch)
plt.axhline(0.154, color='gray', linestyle='--', linewidth=1, label='Baseline ROE (15.4%)')
plt.axvline(1200, color='gray', linestyle=':', linewidth=1, label='High Carbon Threshold')

# ZOOM IN: Crop outliers to show the decision zone clearly
plt.ylim(-0.6, 0.4) 

# Labels & Titles
plt.title("Project Carbon-RWA: Portfolio Optimization Results\nDriving ROE from 15.4% → 19.1% (Capital Efficient Rebalancing)", fontsize=16, fontweight='bold')
plt.xlabel("Carbon Intensity (kg CO2 / Revenue)", fontsize=12)
plt.ylabel("Risk-Adjusted Return (RAROC)", fontsize=12)
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', title="Optimization Decision")

plt.tight_layout()
plt.savefig('Final_Board_Dashboard.png', dpi=300)
print("✅ Graph saved as 'Final_Board_Dashboard.png'")
plt.show()
Project Carbon-RWA
Climate Transition Risk & Capital Optimization Engine

Quantitative stress testing and portfolio steering for an Indian commercial banking portfolio

📌 Executive Summary

Project Carbon-RWA is a full-stack risk analytics engine that translates climate transition scenarios into regulatory capital impact and strategic portfolio actions.

Using Basel III AIRB capital modeling, SQL-based portfolio segmentation, Python optimization, and Excel dashboards, the project demonstrates how banks can stabilize ROE under NGFS Disorderly Transition shocks through capital-efficient rebalancing rather than blanket divestment.

Portfolio simulated: ₹50,000 Cr corporate loan book across high-carbon Indian sectors.

📈 Key Results
Metric	Stressed Baseline	Optimized Strategy
Portfolio ROE	15.4%	19.2%
Capital Shortfall	₹5,040 Cr	Neutralized
Clients Divested	—	12%

Insight: Transition finance outperforms full exits in both capital efficiency and profitability.

🛠 Tech Stack

SQL – Portfolio segmentation & cohort ranking
Python – Basel III AIRB risk engine & linear optimization
Excel – Sensitivity analysis & board-style dashboard
Matplotlib – Strategic risk visualization

🔍 Workflow

Integrate financial + ESG datasets using SQL

Calculate regulatory capital using Basel III ASRF formula

Apply NGFS Disorderly Transition stress scenario

Optimize portfolio under capital & business constraints

Visualize divestment vs transition opportunities

📂 Repository Contents
1_data_gen.py
2_portfolio_analysis.sql
2_risk_engine_optimizer.py
3_dashboard_viz.py
Project_Dashboard.xlsx
Final_Board_Dashboard.png
requirements.txt

▶️ How to Run
pip install -r requirements.txt
python 1_data_gen.py
python 2_risk_engine_optimizer.py

⚠️ Model Scope

• Single-period static portfolio
• Credit & capital lens only
• Synthetic but regulation-aligned data

🎯 Strategic Use

Risk-Based Capital & Transition Steering Platform
Scalable engine enabling dynamic stress testing and capital-efficient rebalancing to transform compliance into strategic advantage.

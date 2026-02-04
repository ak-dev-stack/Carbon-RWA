/* 
   PROJECT CARBON-RWA: PORTFOLIO SEGMENTATION & RISK RANKING
   ---------------------------------------------------------
   Objective: Join Credit Data with ESG Data and rank clients relative to peers.
   Author: [Your Name]
*/

WITH Sector_Benchmarks AS (
    -- CTE 1: Calculate the "Average" Carbon Intensity per sector.
    -- This prevents us from unfairly flagging all Steel companies as bad just because Steel is dirty.
    SELECT 
        f.Sector,
        AVG(e.Carbon_Intensity_Scope1_2) AS Sector_Avg_Carbon
    FROM raw_financial_table f
    JOIN raw_esg_table e ON f.Borrower_ID = e.Borrower_ID
    GROUP BY f.Sector
),

Ranked_Portfolio AS (
    -- CTE 2: Apply Window Functions to Rank Borrowers
    SELECT 
        f.Loan_ID,
        f.Borrower_ID,
        f.Sector,
        f.Exposure_INR_Cr,
        e.Carbon_Intensity_Scope1_2,
        e.Transition_Readiness_Score,
        
        -- ADVANCED SQL: Percent Rank Window Function
        -- Returns 0 to 1. (1 = Dirtiest company in that specific sector)
        PERCENT_RANK() OVER (
            PARTITION BY f.Sector 
            ORDER BY e.Carbon_Intensity_Scope1_2 ASC
        ) as Sector_Efficiency_Rank
        
    FROM raw_financial_table f
    JOIN raw_esg_table e ON f.Borrower_ID = e.Borrower_ID
)

-- Final Selection
SELECT 
    *,
    CASE 
        WHEN Sector_Efficiency_Rank > 0.80 THEN 'Laggard'
        WHEN Sector_Efficiency_Rank < 0.20 THEN 'Leader'
        ELSE 'Average'
    END as Climate_Performance_Tier
FROM Ranked_Portfolio;
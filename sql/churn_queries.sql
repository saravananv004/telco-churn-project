-- Assumption:
-- Load outputs/churn_scores.csv into a SQL table named telco_churn_scores.
-- Columns: customer_id, churn_actual, churn_flag, churn_risk_score, churn_risk_band,
-- tenure, contract, payment_method, internet_service, monthly_charges, total_charges

-- 1) Overall churn KPIs
SELECT
	COUNT(*) AS total_customers,
	SUM(churn_flag) AS churned_customers,
	ROUND(AVG(churn_flag)::numeric, 4) AS churn_rate,
	SUM(CASE WHEN churn_risk_band = 'High' THEN 1 ELSE 0 END) AS predicted_high_risk_customers,
	ROUND(AVG(churn_risk_score)::numeric, 4) AS avg_predicted_risk
FROM telco_churn_scores;

-- 2) Churn and risk by contract type
SELECT
	contract,
	COUNT(*) AS customers,
	ROUND(AVG(churn_flag)::numeric, 4) AS historical_churn_rate,
	ROUND(AVG(churn_risk_score)::numeric, 4) AS avg_predicted_risk,
	SUM(CASE WHEN churn_risk_band = 'High' THEN 1 ELSE 0 END) AS high_risk_customers
FROM telco_churn_scores
GROUP BY contract
ORDER BY avg_predicted_risk DESC;

-- 3) Churn and risk by payment method
SELECT
	payment_method,
	COUNT(*) AS customers,
	ROUND(AVG(churn_flag)::numeric, 4) AS historical_churn_rate,
	ROUND(AVG(churn_risk_score)::numeric, 4) AS avg_predicted_risk,
	SUM(CASE WHEN churn_risk_band = 'High' THEN 1 ELSE 0 END) AS high_risk_customers
FROM telco_churn_scores
GROUP BY payment_method
ORDER BY avg_predicted_risk DESC;

-- 4) Revenue at risk (monthly)
SELECT
	ROUND(SUM(monthly_charges)::numeric, 2) AS total_monthly_revenue,
	ROUND(SUM(CASE WHEN churn_risk_band = 'High' THEN monthly_charges ELSE 0 END)::numeric, 2) AS monthly_revenue_at_risk,
	ROUND(
		SUM(CASE WHEN churn_risk_band = 'High' THEN monthly_charges ELSE 0 END)
		/ NULLIF(SUM(monthly_charges), 0)::numeric,
		4
	) AS revenue_at_risk_ratio
FROM telco_churn_scores;

-- 5) Top high-risk customers for retention operations
SELECT
	customer_id,
	churn_risk_score,
	churn_risk_band,
	contract,
	tenure,
	monthly_charges,
	payment_method
FROM telco_churn_scores
ORDER BY churn_risk_score DESC
LIMIT 100;

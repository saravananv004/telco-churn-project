# Customer Churn Dashboard Wireframe (Power BI/Tableau)

## Goal
Build a business-first dashboard that helps stakeholders:
- Monitor churn and predicted risk at a glance
- Identify high-risk customer segments
- Quantify monthly revenue at risk
- Trigger retention actions using a prioritized customer list

Primary dataset: `outputs/churn_scores.csv`  
Supporting datasets: `outputs/model_metrics.csv`, `outputs/feature_importance.csv`

## Page 1: Executive Overview
Purpose: high-level health and risk snapshot.

Top KPI cards:
- Total Customers = COUNT(customer_id)
- Historical Churn Rate = AVG(churn_flag)
- High-Risk Customers = COUNT(churn_risk_band = "High")
- High-Risk Share = High-Risk Customers / Total Customers
- Monthly Revenue at Risk = SUM(monthly_charges where churn_risk_band = "High")

Visuals:
- Donut: customers by churn_risk_band
- Column chart: avg churn_risk_score by contract
- Column chart: avg churn_risk_score by payment_method
- Histogram: churn_risk_score distribution

Layout suggestion:
- Row 1: KPI cards
- Row 2 left: risk-band donut
- Row 2 center: risk by contract
- Row 2 right: risk by payment method
- Row 3 full width: score distribution

## Page 2: Segment Analysis
Purpose: understand where churn risk is concentrated.

Visuals:
- Heatmap/table: contract x payment_method with avg churn_risk_score
- Bar chart: avg churn_risk_score by internet_service
- Bar chart: avg churn_risk_score by tenure bucket
- Box plot: monthly_charges by churn_risk_band

Recommended calculated field:
- Tenure Bucket
  - 0-6
  - 7-12
  - 13-24
  - 25-48
  - 49-72

## Page 3: Retention Action Center
Purpose: provide an operational list of customers to contact first.

Table columns:
- customer_id
- churn_risk_score (descending sort)
- churn_risk_band
- contract
- tenure
- monthly_charges
- payment_method
- internet_service

KPI cards:
- High-Risk Customers (filtered view)
- Revenue at Risk in Current Filter
- Avg Risk Score in Current Filter

Optional action fields:
- Suggested Offer
  - If contract = Month-to-month and tenure <= 6 -> "Early loyalty discount"
  - If payment_method = Electronic check -> "Billing support outreach"
  - Else -> "Retention callback"

## Page 4: Model Explainability
Purpose: build trust in the model output.

Visuals:
- Bar chart (Top 15): feature importance from `outputs/feature_importance.csv`
- Scorecard/table: roc_auc, precision, recall, f1 from `outputs/model_metrics.csv`
- Model selector table (logistic vs random forest)

Narrative box:
- Explain that churn_risk_score is a probability from 0 to 1.
- Clarify that risk band thresholds are:
  - High: score >= 0.70
  - Medium: 0.40 to 0.69
  - Low: < 0.40

## Global Filters (All Pages)
- contract
- payment_method
- internet_service
- churn_risk_band
- tenure bucket

## Interactions
- Clicking a bar segment cross-filters all visuals
- Clicking a risk band filters the retention table instantly
- Add drill-through from segment charts to Retention Action Center

## Power BI Calculated Measures (DAX-style)
- Total Customers = DISTINCTCOUNT(churn_scores[customer_id])
- Historical Churn Rate = AVERAGE(churn_scores[churn_flag])
- High-Risk Customers = CALCULATE(COUNTROWS(churn_scores), churn_scores[churn_risk_band] = "High")
- High-Risk Share = DIVIDE([High-Risk Customers], [Total Customers])
- Monthly Revenue at Risk = CALCULATE(SUM(churn_scores[monthly_charges]), churn_scores[churn_risk_band] = "High")
- Avg Predicted Risk = AVERAGE(churn_scores[churn_risk_score])

## Tableau Calculated Fields (Equivalent)
- High Risk Flag: IF [churn_risk_band] = "High" THEN 1 ELSE 0 END
- High-Risk Customers: SUM([High Risk Flag])
- Churn Rate: AVG([churn_flag])
- Revenue at Risk: SUM(IF [churn_risk_band] = "High" THEN [monthly_charges] END)
- Avg Predicted Risk: AVG([churn_risk_score])

## Final Presentation Checklist
- Number format: percentages for rates, currency for charges
- Consistent color palette:
  - High risk = red
  - Medium risk = amber
  - Low risk = green
- Default sort: descending by churn_risk_score for action tables
- Add data refresh timestamp on executive page
- Validate KPI totals against SQL outputs in `sql/churn_queries.sql`
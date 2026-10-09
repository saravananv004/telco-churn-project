# Telco Customer Churn Project

A data science and analytics project to predict customer churn, analyze churn drivers, and build business-facing reporting assets.

## Project Goals
- Clean and prepare the Telco Customer Churn dataset
- Perform EDA to identify churn drivers
- Engineer predictive features
- Train and compare churn prediction models
- Produce SQL business queries and dashboard-ready outputs

## Planned Deliverables
- EDA notebook
- Modeling notebook
- SQL query file
- Trained model artifact
- Customer churn score output
- Dashboard assets
- Business recommendations summary

## Pipeline Flow
Raw customer data -> Data cleaning -> EDA -> Feature engineering -> Model training -> Risk scoring -> Dashboard insights

## Run End-to-End
Run these commands from the project root:

1. `python src/preprocess_data.py`
2. `python src/run_eda.py`
3. `python src/train_and_score.py`

## Output Files
- `data/processed/telco_churn_processed.csv`: cleaned dataset with original labels
- `data/processed/telco_churn_features.csv`: model-ready feature table
- `outputs/eda/`: churn EDA charts and summary tables
- `models/best_churn_model.joblib`: best-performing trained model
- `outputs/model_metrics.csv`: model comparison metrics (AUC, F1, etc.)
- `outputs/churn_scores.csv`: per-customer churn risk scores and risk bands
- `outputs/feature_importance.csv`: top model drivers
- `outputs/business_recommendations.md`: business action bullets
- `sql/churn_queries.sql`: dashboard SQL for KPIs, segmentation, and revenue-at-risk

## Dashboard Build Guide
Use `outputs/churn_scores.csv` as the primary dashboard dataset.

Recommended pages:
- Executive KPI page: total customers, churn rate, high-risk customers, monthly revenue at risk
- Segmentation page: churn and risk by contract type, payment method, internet service, and tenure
- Retention action page: top high-risk customers with score, contract, tenure, and monthly charges
- Model explainability page: top churn drivers from `outputs/feature_importance.csv` and model metrics from `outputs/model_metrics.csv`

Use `docs/dashboard_column_mapping.csv` to map fields directly into Power BI or Tableau visuals.

## Resume-Ready Project Summary
Built an end-to-end churn prediction analytics product on 7,043 telecom customers, combining data cleaning, EDA, feature engineering, classification modeling, and dashboard-ready scoring outputs.

Project outcomes:
- Trained and compared Logistic Regression and Random Forest models with ROC-AUC based selection
- Generated customer-level churn risk scores and risk bands for operational retention targeting
- Quantified monthly revenue at risk and delivered business recommendations in `outputs/business_recommendations.md`
- Produced SQL-ready KPI and segmentation queries for BI dashboard integration

## Recruiter-Focused Highlights
- Business impact first: identifies high-risk customers before churn happens and supports retention actioning
- Full-stack analytics depth: SQL + ML + dashboard pipeline in one project
- Clear communication assets: reproducible scripts, notebooks, model metrics, and recommendation outputs

import json
import warnings
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


INPUT_PATH = Path("data/processed/telco_churn_features.csv")
FULL_INPUT_PATH = Path("data/processed/telco_churn_processed.csv")
MODEL_DIR = Path("models")
OUTPUT_DIR = Path("outputs")


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not INPUT_PATH.exists() or not FULL_INPUT_PATH.exists():
        raise FileNotFoundError(
            "Processed files are missing. Run src/preprocess_data.py before training."
        )
    feature_df = pd.read_csv(INPUT_PATH)
    full_df = pd.read_csv(FULL_INPUT_PATH)
    return feature_df, full_df


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numeric_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ]
    )


def get_models() -> Dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            solver="liblinear",
            class_weight="balanced",
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
    }


def evaluate_model(y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def extract_feature_importance(
    fitted_pipeline: Pipeline, X: pd.DataFrame, top_n: int = 20
) -> pd.DataFrame:
    preprocessor = fitted_pipeline.named_steps["preprocessor"]
    model = fitted_pipeline.named_steps["model"]

    feature_names = preprocessor.get_feature_names_out()

    if hasattr(model, "coef_"):
        importance = np.abs(model.coef_[0])
    elif hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    else:
        return pd.DataFrame(columns=["feature", "importance"])

    fi_df = pd.DataFrame({"feature": feature_names, "importance": importance})
    fi_df = fi_df.sort_values("importance", ascending=False).head(top_n)
    return fi_df


def assign_risk_band(score: float) -> str:
    if score >= 0.7:
        return "High"
    if score >= 0.4:
        return "Medium"
    return "Low"


def write_business_insights(scores_df: pd.DataFrame, full_df: pd.DataFrame, path: Path) -> None:
    churn_rate = full_df["ChurnFlag"].mean()
    high_risk_rate = (scores_df["churn_risk_band"] == "High").mean()

    high_risk = scores_df[scores_df["churn_risk_band"] == "High"]
    avg_monthly_at_risk = high_risk["monthly_charges"].sum()

    top_contract = (
        scores_df.groupby("contract")["churn_risk_score"].mean().sort_values(ascending=False).index[0]
    )
    top_payment = (
        scores_df.groupby("payment_method")["churn_risk_score"].mean().sort_values(ascending=False).index[0]
    )

    lines = [
        "# Business Recommendations",
        "",
        f"- Overall historical churn rate is {churn_rate:.1%}; prioritize retention segments above this baseline.",
        f"- {high_risk_rate:.1%} of customers are predicted as high risk; create a weekly save campaign list from the scoring output.",
        f"- Estimated monthly revenue at risk from high-risk customers is {avg_monthly_at_risk:.2f} (sum of MonthlyCharges).",
        f"- Customers with {top_contract} contracts show the highest predicted churn risk; offer early loyalty incentives.",
        f"- {top_payment} customers are a high-risk payment segment; test payment-experience and billing-clarity interventions.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="sklearn")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    feature_df, full_df = load_data()
    X = feature_df.drop(columns=["ChurnFlag"])
    y = feature_df["ChurnFlag"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor(X)
    models = get_models()

    metrics_rows = []
    fitted_pipelines: Dict[str, Pipeline] = {}

    for model_name, model in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )
        pipeline.fit(X_train, y_train)

        y_prob = pipeline.predict_proba(X_test)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)
        metrics = evaluate_model(y_test, y_pred, y_prob)
        metrics_rows.append({"model": model_name, **metrics})
        fitted_pipelines[model_name] = pipeline

    metrics_df = pd.DataFrame(metrics_rows).sort_values("roc_auc", ascending=False)
    best_model_name = metrics_df.iloc[0]["model"]
    best_pipeline = fitted_pipelines[str(best_model_name)]

    joblib.dump(best_pipeline, MODEL_DIR / "best_churn_model.joblib")
    metrics_df.to_csv(OUTPUT_DIR / "model_metrics.csv", index=False)
    (OUTPUT_DIR / "model_metrics.json").write_text(
        json.dumps(metrics_rows, indent=2), encoding="utf-8"
    )

    full_scores = best_pipeline.predict_proba(X)[:, 1]
    scores_df = pd.DataFrame(
        {
            "customer_id": full_df["customerID"],
            "churn_actual": full_df["Churn"],
            "churn_flag": full_df["ChurnFlag"],
            "churn_risk_score": full_scores,
            "churn_risk_band": [assign_risk_band(s) for s in full_scores],
            "tenure": full_df["tenure"],
            "contract": full_df["Contract"],
            "payment_method": full_df["PaymentMethod"],
            "internet_service": full_df["InternetService"],
            "monthly_charges": full_df["MonthlyCharges"],
            "total_charges": full_df["TotalCharges"],
        }
    )
    scores_df.sort_values("churn_risk_score", ascending=False).to_csv(
        OUTPUT_DIR / "churn_scores.csv", index=False
    )

    fi_df = extract_feature_importance(best_pipeline, X, top_n=25)
    fi_df.to_csv(OUTPUT_DIR / "feature_importance.csv", index=False)

    write_business_insights(scores_df, full_df, OUTPUT_DIR / "business_recommendations.md")

    print(f"Best model: {best_model_name}")
    print(f"Saved model metrics to {OUTPUT_DIR / 'model_metrics.csv'}")
    print(f"Saved churn scores to {OUTPUT_DIR / 'churn_scores.csv'}")


if __name__ == "__main__":
    main()

from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_CSV_PATH = PROCESSED_DIR / "telco_churn_processed.csv"
FEATURES_CSV_PATH = PROCESSED_DIR / "telco_churn_features.csv"


def load_raw_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {path}")
    return pd.read_csv(path)


def clean_telco_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    # Remove trailing and leading spaces in all text columns.
    object_cols = cleaned.select_dtypes(include=["object"]).columns
    for col in object_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # TotalCharges may contain blank strings for new customers.
    cleaned["TotalCharges"] = pd.to_numeric(cleaned["TotalCharges"], errors="coerce")
    cleaned["TotalCharges"] = cleaned["TotalCharges"].fillna(0.0)

    # Create a binary target column while keeping the original label.
    cleaned["ChurnFlag"] = cleaned["Churn"].map({"Yes": 1, "No": 0})

    # Ensure numeric columns have stable dtypes.
    cleaned["SeniorCitizen"] = cleaned["SeniorCitizen"].astype("int64")
    cleaned["tenure"] = cleaned["tenure"].astype("int64")
    cleaned["MonthlyCharges"] = cleaned["MonthlyCharges"].astype("float64")

    return cleaned


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = df.copy()
    if "customerID" in feature_df.columns:
        feature_df = feature_df.drop(columns=["customerID"])
    if "Churn" in feature_df.columns:
        feature_df = feature_df.drop(columns=["Churn"])
    return feature_df


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data(RAW_PATH)
    cleaned_df = clean_telco_data(raw_df)
    features_df = build_model_features(cleaned_df)

    cleaned_df.to_csv(PROCESSED_CSV_PATH, index=False)
    features_df.to_csv(FEATURES_CSV_PATH, index=False)

    print(f"Saved cleaned dataset: {PROCESSED_CSV_PATH}")
    print(f"Saved model features: {FEATURES_CSV_PATH}")
    print(f"Rows: {len(cleaned_df)}, Columns: {cleaned_df.shape[1]}")


if __name__ == "__main__":
    main()
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


INPUT_PATH = Path("data/processed/telco_churn_processed.csv")
OUTPUT_DIR = Path("outputs/eda")


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Processed file not found at {path}. Run src/preprocess_data.py first."
        )
    return pd.read_csv(path)


def add_tenure_bucket(df: pd.DataFrame) -> pd.DataFrame:
    labeled = df.copy()
    labeled["TenureBucket"] = pd.cut(
        labeled["tenure"],
        bins=[-1, 6, 12, 24, 48, 72],
        labels=["0-6", "7-12", "13-24", "25-48", "49-72"],
    )
    return labeled


def save_summary_tables(df: pd.DataFrame, output_dir: Path) -> None:
    overview = pd.DataFrame(
        {
            "metric": ["total_customers", "churned_customers", "churn_rate"],
            "value": [
                len(df),
                int(df["ChurnFlag"].sum()),
                round(float(df["ChurnFlag"].mean()), 4),
            ],
        }
    )
    overview.to_csv(output_dir / "overview_metrics.csv", index=False)

    contract_churn = (
        df.groupby("Contract", as_index=False)["ChurnFlag"]
        .mean()
        .rename(columns={"ChurnFlag": "churn_rate"})
        .sort_values("churn_rate", ascending=False)
    )
    contract_churn.to_csv(output_dir / "churn_by_contract.csv", index=False)

    payment_churn = (
        df.groupby("PaymentMethod", as_index=False)["ChurnFlag"]
        .mean()
        .rename(columns={"ChurnFlag": "churn_rate"})
        .sort_values("churn_rate", ascending=False)
    )
    payment_churn.to_csv(output_dir / "churn_by_payment_method.csv", index=False)

    tenure_churn = (
        df.groupby("TenureBucket", as_index=False, observed=False)["ChurnFlag"]
        .mean()
        .rename(columns={"ChurnFlag": "churn_rate"})
    )
    tenure_churn.to_csv(output_dir / "churn_by_tenure_bucket.csv", index=False)


def save_plots(df: pd.DataFrame, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x="Churn", order=["No", "Yes"])
    plt.title("Churn Distribution")
    plt.tight_layout()
    plt.savefig(output_dir / "churn_distribution.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4))
    order = (
        df.groupby("Contract")["ChurnFlag"]
        .mean()
        .sort_values(ascending=False)
        .index
    )
    sns.barplot(data=df, x="Contract", y="ChurnFlag", order=order)
    plt.title("Churn Rate by Contract")
    plt.ylabel("Churn Rate")
    plt.tight_layout()
    plt.savefig(output_dir / "churn_by_contract.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 4))
    order = (
        df.groupby("PaymentMethod")["ChurnFlag"]
        .mean()
        .sort_values(ascending=False)
        .index
    )
    sns.barplot(data=df, x="PaymentMethod", y="ChurnFlag", order=order)
    plt.title("Churn Rate by Payment Method")
    plt.ylabel("Churn Rate")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "churn_by_payment_method.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x="TenureBucket", y="ChurnFlag")
    plt.title("Churn Rate by Tenure Bucket")
    plt.ylabel("Churn Rate")
    plt.tight_layout()
    plt.savefig(output_dir / "churn_by_tenure_bucket.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x="Churn", y="MonthlyCharges", order=["No", "Yes"])
    plt.title("Monthly Charges by Churn")
    plt.tight_layout()
    plt.savefig(output_dir / "monthly_charges_by_churn.png", dpi=150)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data(INPUT_PATH)
    df = add_tenure_bucket(df)

    save_summary_tables(df, OUTPUT_DIR)
    save_plots(df, OUTPUT_DIR)

    print(f"EDA outputs saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

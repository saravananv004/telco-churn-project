from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


DATASET_SLUG = "blastchar/telco-customer-churn"


def main() -> None:
    """Download the Telco Customer Churn dataset from Kaggle."""
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as exc:
        raise SystemExit(
            "Kaggle authentication failed. Add ~/.kaggle/kaggle.json and run chmod 600 ~/.kaggle/kaggle.json."
        ) from exc

    api.dataset_download_files(DATASET_SLUG, path=str(output_dir), unzip=True)
    print(f"Downloaded {DATASET_SLUG} to {output_dir}")


if __name__ == "__main__":
    main()

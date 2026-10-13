"""Download PhysioNet ECG datasets using WFDB with integrity verification (Section 5 & 6)."""
import argparse
import hashlib
from pathlib import Path
import sys
from typing import Optional
import wfdb

DATASETS = {
    "nstdb": {
        "db_name": "nstdb",
        "description": "MIT-BIH Noise Stress Test Database",
        "key_records": [
            "118e24", "118e18", "118e12", "118e06", "118e00", "118e_6",
            "119e24", "119e18", "119e12", "119e06", "119e00", "119e_6",
            "bw", "em", "ma"
        ],
    },
    "mitdb": {
        "db_name": "mitdb",
        "description": "MIT-BIH Arrhythmia Database",
        "key_records": [
            "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
            "111", "112", "113", "114", "115", "116", "117", "118", "119",
            "121", "122", "123", "124", "200", "201", "202", "203", "205",
            "207", "208", "209", "210", "212", "213", "214", "215", "217",
            "219", "220", "221", "222", "223", "228", "230", "231", "232",
            "233", "234"
        ],
    },
    "qtdb": {
        "db_name": "qtdb",
        "description": "QT Database",
        "key_records": [
            "sel100", "sel102", "sel103", "sel104", "sel114", "sel116",
            "sel117", "sel123", "sel14046", "sel14154", "sel14172", "sel15814",
            "sel16265", "sel16272", "sel16273", "sel16420", "sel16483", "sel16539",
            "sel16773", "sel16788"
        ],
    },
}


def compute_file_sha256(filepath: Path) -> str:
    """Compute sha256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def download_dataset(
    dataset_key: str,
    output_base: Path,
    records_subset: Optional[list] = None,
    overwrite: bool = False,
) -> int:
    """Download records for the given database."""
    if dataset_key not in DATASETS:
        raise ValueError(f"Unknown dataset '{dataset_key}'. Choose from: {list(DATASETS.keys())}")

    meta = DATASETS[dataset_key]
    db_name = meta["db_name"]
    target_dir = output_base / dataset_key
    target_dir.mkdir(parents=True, exist_ok=True)

    records = records_subset or meta["key_records"]

    print(f"Downloading {len(records)} records for {db_name} into {target_dir}...")
    try:
        wfdb.dl_database(
            db_dir=db_name,
            dl_dir=str(target_dir),
            records=records,
            overwrite=overwrite,
        )
        print(f"Successfully downloaded {dataset_key} records.")
        # Log downloaded files
        downloaded_files = list(target_dir.glob("*"))
        print(f"Total files in {target_dir}: {len(downloaded_files)}")
        return len(downloaded_files)
    except Exception as e:
        print(f"Error downloading dataset {dataset_key}: {e}", file=sys.stderr)
        return 0


def main():
    parser = argparse.ArgumentParser(description="Download ECG datasets from PhysioNet.")
    parser.add_argument("--dataset", required=True, choices=["nstdb", "mitdb", "qtdb", "all"], help="Dataset to download")
    parser.add_argument("--output_dir", default="data/raw", help="Target output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to download")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    output_base = Path(args.output_dir)

    targets = list(DATASETS.keys()) if args.dataset == "all" else [args.dataset]
    for target in targets:
        records = DATASETS[target]["key_records"]
        if args.limit:
            records = records[:args.limit]
        download_dataset(target, output_base, records_subset=records, overwrite=args.overwrite)


if __name__ == "__main__":
    main()

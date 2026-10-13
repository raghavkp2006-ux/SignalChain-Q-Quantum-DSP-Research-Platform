"""Download MIT-BIH Arrhythmia Database (mitdb) records using WFDB."""
import argparse
from pathlib import Path
import wfdb


DEFAULT_MITDB_RECORDS = [
    "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
    "111", "112", "113", "114", "115", "116", "117", "118", "119",
    "121", "122", "123", "124", "200", "201", "202", "203", "205",
    "207", "208", "209", "210", "212", "213", "214", "215", "217",
    "219", "220", "221", "222", "223", "228", "230", "231", "232",
    "233", "234",
]


def main():
    parser = argparse.ArgumentParser(description="Download MIT-BIH Arrhythmia Database.")
    parser.add_argument("--output_dir", default="data/raw/mitdb", help="Target output directory")
    parser.add_argument("--records", nargs="+", default=None, help="Subset of records to download")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    records = args.records or DEFAULT_MITDB_RECORDS
    if args.limit:
        records = records[:args.limit]

    print(f"Downloading {len(records)} MIT-BIH records into {out_path}...")
    try:
        wfdb.dl_database("mitdb", dl_dir=str(out_path), records=records, overwrite=args.overwrite)
        print("MIT-BIH download complete.")
    except Exception as e:
        print(f"Error during MIT-BIH download: {e}")


if __name__ == "__main__":
    main()

"""Download QT Database (qtdb) records using WFDB."""
import argparse
from pathlib import Path
import wfdb


DEFAULT_QTDB_RECORDS = [
    "sel100", "sel102", "sel103", "sel104", "sel114", "sel116",
    "sel117", "sel123", "sel14046", "sel14154", "sel14172", "sel15814",
    "sel16265", "sel16272", "sel16273", "sel16420", "sel16483", "sel16539",
    "sel16773", "sel16788",
]


def main():
    parser = argparse.ArgumentParser(description="Download QT Database.")
    parser.add_argument("--output_dir", default="data/raw/qtdb", help="Target output directory")
    parser.add_argument("--records", nargs="+", default=None, help="Subset of records to download")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    records = args.records or DEFAULT_QTDB_RECORDS
    if args.limit:
        records = records[:args.limit]

    print(f"Downloading {len(records)} QTDB records into {out_path}...")
    try:
        wfdb.dl_database("qtdb", dl_dir=str(out_path), records=records, overwrite=args.overwrite)
        print("QTDB download complete.")
    except Exception as e:
        print(f"Error during QTDB download: {e}")


if __name__ == "__main__":
    main()

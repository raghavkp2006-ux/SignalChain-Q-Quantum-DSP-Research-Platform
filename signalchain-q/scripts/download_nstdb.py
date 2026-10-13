"""Download MIT-BIH Noise Stress Test Database (nstdb) records using WFDB."""
import argparse
from pathlib import Path
import wfdb


DEFAULT_NSTDB_RECORDS = [
    "118e24", "118e18", "118e12", "118e06", "118e00", "118e_6",
    "119e24", "119e18", "119e12", "119e06", "119e00", "119e_6",
    "bw", "em", "ma",
]


def main():
    parser = argparse.ArgumentParser(description="Download MIT-BIH Noise Stress Test Database.")
    parser.add_argument("--output_dir", default="data/raw/nstdb", help="Target output directory")
    parser.add_argument("--records", nargs="+", default=None, help="Subset of records to download")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    records = args.records or DEFAULT_NSTDB_RECORDS
    if args.limit:
        records = records[:args.limit]

    print(f"Downloading {len(records)} NSTDB records into {out_path}...")
    try:
        wfdb.dl_database("nstdb", dl_dir=str(out_path), records=records, overwrite=args.overwrite)
        print("NSTDB download complete.")
    except Exception as e:
        print(f"Error during NSTDB download: {e}")


if __name__ == "__main__":
    main()

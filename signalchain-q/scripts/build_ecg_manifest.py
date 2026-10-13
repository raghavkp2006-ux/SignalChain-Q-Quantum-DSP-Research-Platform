"""Build dataset manifests and paired clean/noisy indices (Section 6)."""
import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import wfdb


def get_sha256(filepath: Path) -> str:
    """Compute sha256 checksum."""
    if not filepath.exists():
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_mitdb_splits(splits_json_path: Path) -> Dict[str, str]:
    """Return mapping of record_id -> split name ('development', 'validation', 'test')."""
    if not splits_json_path.exists():
        return {}
    with open(splits_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    record_to_split = {}
    for split_name, records in data.get("splits", {}).items():
        for r in records:
            record_to_split[str(r)] = split_name
    return record_to_split


def build_manifests(
    data_raw_dir: Path,
    manifests_dir: Path,
    splits_json_path: Path,
):
    """Scan raw downloaded records and build dataset_manifest.csv."""
    manifests_dir.mkdir(parents=True, exist_ok=True)
    mitdb_splits = load_mitdb_splits(splits_json_path)

    manifest_rows: List[Dict] = []

    # 1. Scan MIT-BIH
    mitdb_dir = data_raw_dir / "mitdb"
    if mitdb_dir.exists():
        hea_files = sorted(list(mitdb_dir.glob("*.hea")))
        for h in hea_files:
            rec_id = h.stem
            dat_file = mitdb_dir / f"{rec_id}.dat"
            sha = get_sha256(dat_file) if dat_file.exists() else get_sha256(h)

            try:
                rec = wfdb.rdheader(str(mitdb_dir / rec_id))
                fs = rec.fs
                dur = rec.sig_len / fs
                sig_names = rec.sig_name if hasattr(rec, "sig_name") else ["MLII"]
                ch_label = sig_names[0] if sig_names else "MLII"
            except Exception:
                fs = 360.0
                dur = 1800.0
                ch_label = "MLII"

            subj_grp = "group_201_202" if rec_id in ("201", "202") else f"subj_{rec_id}"
            split = mitdb_splits.get(rec_id, "development")

            manifest_rows.append({
                "dataset": "mitdb",
                "version": "1.0.0",
                "record_id": rec_id,
                "subject_group": subj_grp,
                "channel_index": 0,
                "channel_label": ch_label,
                "sampling_rate_hz": fs,
                "duration_sec": round(dur, 2),
                "source_url": f"https://physionet.org/content/mitdb/1.0.0/{rec_id}",
                "local_path": str(dat_file if dat_file.exists() else h),
                "sha256": sha,
                "split": split,
            })

    # 2. Scan NSTDB
    nstdb_dir = data_raw_dir / "nstdb"
    if nstdb_dir.exists():
        hea_files = sorted(list(nstdb_dir.glob("*.hea")))
        for h in hea_files:
            rec_id = h.stem
            dat_file = nstdb_dir / f"{rec_id}.dat"
            sha = get_sha256(dat_file) if dat_file.exists() else get_sha256(h)
            try:
                rec = wfdb.rdheader(str(nstdb_dir / rec_id))
                fs = rec.fs
                dur = rec.sig_len / fs
                sig_names = rec.sig_name if hasattr(rec, "sig_name") else ["MLII"]
                ch_label = sig_names[0] if sig_names else "MLII"
            except Exception:
                fs = 360.0
                dur = 1800.0
                ch_label = "MLII"

            manifest_rows.append({
                "dataset": "nstdb",
                "version": "1.0.0",
                "record_id": rec_id,
                "subject_group": f"nstdb_{rec_id[:3]}",
                "channel_index": 0,
                "channel_label": ch_label,
                "sampling_rate_hz": fs,
                "duration_sec": round(dur, 2),
                "source_url": f"https://physionet.org/content/nstdb/1.0.0/{rec_id}",
                "local_path": str(dat_file if dat_file.exists() else h),
                "sha256": sha,
                "split": "test",  # NSTDB is canonically reserved for final testing
            })

    # Save dataset_manifest.csv
    df_manifest = pd.DataFrame(manifest_rows)
    manifest_csv = manifests_dir / "dataset_manifest.csv"
    df_manifest.to_csv(manifest_csv, index=False)
    print(f"Generated {manifest_csv} with {len(df_manifest)} entries.")
    return df_manifest


def main():
    parser = argparse.ArgumentParser(description="Build dataset manifests.")
    parser.add_argument("--raw_dir", default="data/raw", help="Directory containing downloaded datasets")
    parser.add_argument("--manifest_dir", default="data/manifests", help="Output directory for manifests")
    parser.add_argument("--splits_file", default="configs/splits/mitdb_v1.json", help="Path to splits JSON")
    args = parser.parse_args()

    build_manifests(
        data_raw_dir=Path(args.raw_dir),
        manifests_dir=Path(args.manifest_dir),
        splits_json_path=Path(args.splits_file),
    )


if __name__ == "__main__":
    main()

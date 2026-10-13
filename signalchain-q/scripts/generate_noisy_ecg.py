"""Generate synthetic and recorded noisy ECG pairs at target SNRs (Section 7)."""
import argparse
import hashlib
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
import yaml

from qsp.core.reproducibility import seed_everything
from qsp.modalities.ecg.io import generate_synthetic_lead
from qsp.modalities.ecg.noise import get_noise_vector, mix_noise_at_snr


def generate_noisy_pairs(
    output_dir: Path,
    config_path: Path,
    split_target: str = "validation",
    limit: int = 10,
    seed: int = 1448,
):
    """Generate noisy ECG pairs with tolerance <= 0.25 dB and write to data/derived/."""
    seed_everything(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = output_dir.parent / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    noise_types = cfg.get("benchmark", {}).get("noise_types", ["bw", "ma", "em"])
    snr_levels = cfg.get("benchmark", {}).get("snr_db", [-6, 0, 6, 12, 18, 24])

    pairs_rows: List[dict] = []

    # Generate synthetic reference signals for required limit
    for i in range(limit):
        pair_base_seed = seed + i * 50
        rec = generate_synthetic_lead(
            duration_sec=5.0,
            fs=360.0,
            heart_rate_bpm=65.0 + (i % 20),
            seed=pair_base_seed,
        )
        clean_sig = rec.signal
        fs = rec.sampling_rate_hz

        clean_file = output_dir / f"clean_{split_target}_{i:03d}.csv"
        pd.DataFrame({"amplitude": clean_sig}).to_csv(clean_file, index=False)

        for nt in noise_types:
            for target_snr in snr_levels:
                pair_id = f"{split_target}_{i:03d}_{nt}_{target_snr}dB"
                noise_seed = seed + int(hashlib.md5(pair_id.encode()).hexdigest()[:6], 16)

                noise_vec = get_noise_vector(nt, len(clean_sig), fs=fs, seed=noise_seed)
                noisy_sig, measured_snr, alpha = mix_noise_at_snr(
                    clean_ecg=clean_sig,
                    noise=noise_vec,
                    target_snr_db=float(target_snr),
                    tolerance_db=0.25,
                )

                noisy_file = output_dir / f"noisy_{pair_id}.csv"
                pd.DataFrame({"amplitude": noisy_sig}).to_csv(noisy_file, index=False)

                pairs_rows.append({
                    "pair_id": pair_id,
                    "dataset": "synthetic_mitdb_match",
                    "clean_record_id": f"clean_{i:03d}",
                    "clean_path": str(clean_file),
                    "noisy_path": str(noisy_file),
                    "noise_source": "synthetic_generator",
                    "noise_type": nt,
                    "target_snr_db": float(target_snr),
                    "measured_snr_db": round(measured_snr, 4),
                    "sampling_rate_hz": fs,
                    "segment_start_sample": 0,
                    "segment_length": len(clean_sig),
                    "channel_index": 0,
                    "split": split_target,
                    "seed": noise_seed,
                })

    df_pairs = pd.DataFrame(pairs_rows)
    pairs_csv = manifest_dir / "ecg_pairs.csv"
    df_pairs.to_csv(pairs_csv, index=False)
    print(f"Generated {len(df_pairs)} noisy ECG pairs in {output_dir}")
    print(f"Manifest written to {pairs_csv}")
    return df_pairs


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic noisy ECG pairs.")
    parser.add_argument("--config", default="configs/ecg_mvp.yaml", help="Config file path")
    parser.add_argument("--output_dir", default="data/derived", help="Output directory")
    parser.add_argument("--split", default="validation", help="Target split")
    parser.add_argument("--limit", type=int, default=10, help="Number of distinct baseline signals")
    args = parser.parse_args()

    generate_noisy_pairs(
        output_dir=Path(args.output_dir),
        config_path=Path(args.config),
        split_target=args.split,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()

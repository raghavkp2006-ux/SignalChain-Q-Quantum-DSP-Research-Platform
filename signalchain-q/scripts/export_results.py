"""Export benchmark results into LaTeX tables and publication summaries."""
import argparse
from pathlib import Path
import pandas as pd


def export_publication_tables(results_dir: Path, output_dir: Path):
    """Read method_summary.csv and statistics.csv and format publication tables."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_file = results_dir / "method_summary.csv"

    if summary_file.exists():
        df = pd.read_csv(summary_file)
        latex_str = df.to_latex(index=False, float_format="%.3f")
        with open(output_dir / "method_summary_table.tex", "w") as f:
            f.write(latex_str)
        print(f"Exported LaTeX table to {output_dir / 'method_summary_table.tex'}")


def main():
    parser = argparse.ArgumentParser(description="Export publication tables.")
    parser.add_argument("--results_dir", required=True, help="Directory containing benchmark results")
    parser.add_argument("--output_dir", default="results/publication", help="Output directory")
    args = parser.parse_args()

    export_publication_tables(Path(args.results_dir), Path(args.output_dir))


if __name__ == "__main__":
    main()

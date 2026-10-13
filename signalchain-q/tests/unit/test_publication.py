"""Unit tests for Phase 11 publication artifacts and build pipeline."""

import os
from pathlib import Path
import pytest
import yaml

from qsp.publication.build import PublicationBuilder


@pytest.fixture(scope="module")
def repo_root():
    return Path(__file__).resolve().parent.parent.parent


def test_frozen_config_integrity(repo_root):
    """Verify that configs/ecg_frozen_v1.yaml matches required frozen parameters."""
    cfg_path = repo_root / "configs" / "ecg_frozen_v1.yaml"
    assert cfg_path.exists(), "configs/ecg_frozen_v1.yaml must exist"

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert cfg["adaptive_filter"]["f_high_min"] == 30.0
    assert cfg["adaptive_filter"]["f_high_max"] == 45.0
    assert cfg["quantum"]["segment_size"] == 64
    assert cfg["quantum"]["grover_iterations"] == 2
    assert cfg["selection"]["frozen"] is True


def test_publication_builder_execution(repo_root):
    """Test that PublicationBuilder runs to completion and generates all artifacts."""
    builder = PublicationBuilder(base_dir=repo_root)
    builder.build_all()
    assert builder.tables_dir.exists()
    assert builder.figures_dir.exists()


def test_all_publication_tables_exist_and_nonempty(repo_root):
    """Verify that all required publication LaTeX tables exist and contain content."""
    tables_dir = repo_root / "paper" / "tables"
    required_tables = [
        "table_dataset_summary.tex",
        "table_validation_parameters.tex",
        "table_main_results.tex",
        "table_statistics.tex",
        "table_quantum_resources.tex",
        "table_grover_ablation.tex",
        "table_segment_ablation.tex",
        "table_oracle_ablation.tex",
        "table_qtdb_morphology.tex",
        "table_noise_type_results.tex",
        "table_snr_level_results.tex",
    ]
    for table_name in required_tables:
        table_path = tables_dir / table_name
        assert table_path.exists(), f"Table {table_name} missing in {tables_dir}"
        content = table_path.read_text(encoding="utf-8")
        assert len(content) > 50, f"Table {table_name} appears empty"
        assert "\\begin{table" in content or "\\begin{tabular" in content
        assert "\\end{table" in content or "\\end{tabular}" in content


def test_table_latex_escaping_and_arrows(repo_root):
    """Verify that main results table has arrows and proper percent escaping."""
    main_table = repo_root / "paper" / "tables" / "table_main_results.tex"
    content = main_table.read_text(encoding="utf-8")
    assert "\\uparrow" in content
    assert "\\downarrow" in content
    assert "\\%" in content
    assert "Wavelet DB6" in content
    assert "QFT-Grover Adaptive" in content


def test_all_publication_figures_exist(repo_root):
    """Verify that publication vector PDFs and PNGs exist."""
    fig_dir = repo_root / "paper" / "figures"
    required_stems = [
        "noise_type_snr",
        "noise_type_prd",
        "noise_type_f1",
        "snr_input_vs_improvement",
        "snr_input_vs_prd",
        "snr_input_vs_f1",
        "grover_tradeoff",
        "circuit_scaling",
        "qtdb_preservation",
    ]
    for stem in required_stems:
        pdf_path = fig_dir / f"{stem}.pdf"
        png_path = fig_dir / f"{stem}.png"
        assert pdf_path.exists(), f"Vector PDF {pdf_path} missing"
        assert png_path.exists(), f"Raster PNG {png_path} missing"
        assert pdf_path.stat().st_size > 1000
        assert png_path.stat().st_size > 1000


def test_diagram_sources_exist(repo_root):
    """Verify that architecture diagram source files exist."""
    src_dir = repo_root / "paper" / "figures" / "source"
    assert (src_dir / "architecture.mmd").exists()
    assert (src_dir / "architecture.dot").exists()
    dot_content = (src_dir / "architecture.dot").read_text(encoding="utf-8")
    assert "digraph SignalChainQ" in dot_content
    assert "QFT" in dot_content


def test_manuscript_and_bibliography_exist(repo_root):
    """Verify that paper/main.tex and paper/references.bib are present and properly formed."""
    main_tex = repo_root / "paper" / "main.tex"
    ref_bib = repo_root / "paper" / "references.bib"
    assert main_tex.exists()
    assert ref_bib.exists()

    tex_content = main_tex.read_text(encoding="utf-8")
    assert "\\documentclass" in tex_content
    assert "\\bibliography{references}" in tex_content
    assert "Wavelet DB6" in tex_content
    assert "Grover" in tex_content

    bib_content = ref_bib.read_text(encoding="utf-8")
    assert "@article{goldberger2000physiobank" in bib_content
    assert "@inproceedings{grover1996" in bib_content


def test_audited_documentation_files(repo_root):
    """Verify that all Phase 11 analytical and audit docs exist."""
    docs_dir = repo_root / "docs"
    required_docs = [
        "PUBLICATION_RESULT_AUDIT.md",
        "QTDB_METRIC_AUDIT.md",
        "COMPLEXITY_ANALYSIS.md",
        "GROVER_DSP_ANALYSIS.md",
        "ORACLE_RESOURCE_ANALYSIS.md",
        "PAPER_CLAIMS.md",
    ]
    for doc in required_docs:
        doc_path = docs_dir / doc
        assert doc_path.exists(), f"Document {doc} missing in docs/"
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) > 200, f"Document {doc} is too short"


def test_claims_categorization(repo_root):
    """Verify that docs/PAPER_CLAIMS.md contains all four required categories."""
    claims_path = repo_root / "docs" / "PAPER_CLAIMS.md"
    content_upper = claims_path.read_text(encoding="utf-8").upper()
    assert "SUPPORTED CLAIMS" in content_upper
    assert "PARTIALLY SUPPORTED CLAIMS" in content_upper
    assert "REFUTED CLAIMS" in content_upper
    assert "CLAIMS NOT TESTED" in content_upper

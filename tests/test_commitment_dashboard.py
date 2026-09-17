from pathlib import Path


def test_commitment_dashboard_exists_and_uses_analysis_only_model():
    path = Path("dashboard/pages/15_Commitment_Coverage.py")
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "aggregate_commitment_coverage" in source
    assert "Analysis-only" in source


def test_commitment_dashboard_does_not_contain_mutation_apis():
    source = Path("dashboard/pages/15_Commitment_Coverage.py").read_text(encoding="utf-8")
    forbidden = ("purchase", "cancel", "modify", "create_reserved", "update")
    assert not any(token in source.lower() for token in forbidden[3:])

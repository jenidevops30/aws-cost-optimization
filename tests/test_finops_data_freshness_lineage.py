import pytest
from src.finops_data_freshness_lineage import FinOpsEvidenceLineage, lineage_rows, lineage_summary

def test_lineage_available():
    row=lineage_rows([FinOpsEvidenceLineage("billing","2026-08","csv","2026-09-01",10)])[0]
    assert row["lineage_status"]=="available"

def test_zero_records_requires_review():
    row=lineage_rows([FinOpsEvidenceLineage("billing","2026-08","csv","2026-09-01",0)])[0]
    assert row["lineage_status"]=="review"

def test_incomplete_requires_review():
    row=lineage_rows([FinOpsEvidenceLineage("billing","2026-08","csv","2026-09-01",10,False)])[0]
    assert row["lineage_status"]=="review"

def test_summary():
    rows=[
      FinOpsEvidenceLineage("a","2026-08","x","t",1),
      FinOpsEvidenceLineage("b","2026-08","y","t",0),
    ]
    assert lineage_summary(rows)=={"datasets":2,"available":1,"review":1}

def test_negative_record_count_rejected():
    with pytest.raises(ValueError):
        FinOpsEvidenceLineage("a","2026-08","x","t",-1)

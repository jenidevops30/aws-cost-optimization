from pathlib import Path


APP = Path("dashboard/app.py")


def test_dashboard_source_compiles():
    source = APP.read_text(encoding="utf-8")
    compile(source, str(APP), "exec")


def test_dashboard_preserves_read_only_controls():
    source = APP.read_text(encoding="utf-8")
    assert "AWS Cost Explorer" in source
    assert "get_readonly_summary" in source
    assert "no AWS resource mutations" in source
    assert "no AWS secrets stored in the repository" in source

from datetime import datetime
import pytest
from git_pulse.models import CommitRecord
from git_pulse.survival import analyze_code_survival


def test_analyze_code_survival():
    commits = [
        CommitRecord(
            hash="c1",
            author_name="Alice",
            author_email="alice@example.com",
            timestamp=datetime(2026, 1, 1),
            message="feat: initial module",
            insertions=100,
            deletions=10,
            files_changed=["module.py"],
        ),
        CommitRecord(
            hash="c2",
            author_name="Bob",
            author_email="bob@example.com",
            timestamp=datetime(2026, 1, 2),
            message="refactor: complete rewrite",
            insertions=30,
            deletions=25,
            files_changed=["experimental.py"],
        ),
    ]

    report = analyze_code_survival(commits, min_insertions_threshold=5, volatility_threshold=50.0)
    assert report.total_insertions == 130
    assert report.total_deletions == 35
    assert report.net_lines == 95
    assert report.overall_survival_rate_pct == pytest.approx(73.08, rel=1e-2)

    # Alice should have 90% survival
    alice = next(a for a in report.author_metrics if a.author == "Alice")
    assert alice.survival_rate_pct == 90.0

    # Experimental file should be marked volatile (survival = 5/30 = 16.67% < 50%)
    assert any(f.file_path == "experimental.py" for f in report.volatile_files)

from datetime import datetime
import pytest
from git_pulse.models import CommitRecord
from git_pulse.coupling import analyze_temporal_coupling


def test_temporal_coupling_detection():
    # Simulate commit history where api.py and auth.py always change together
    commits = [
        CommitRecord(
            hash="c1",
            author_name="Alice",
            author_email="alice@example.com",
            timestamp=datetime(2026, 1, 1),
            message="feat: auth endpoint",
            files_changed=["src/api.py", "src/auth.py"],
        ),
        CommitRecord(
            hash="c2",
            author_name="Bob",
            author_email="bob@example.com",
            timestamp=datetime(2026, 1, 2),
            message="fix: token validation",
            files_changed=["src/api.py", "src/auth.py", "src/utils.py"],
        ),
        CommitRecord(
            hash="c3",
            author_name="Alice",
            author_email="alice@example.com",
            timestamp=datetime(2026, 1, 3),
            message="refactor: auth flow",
            files_changed=["src/api.py", "src/auth.py"],
        ),
        CommitRecord(
            hash="c4",
            author_name="Charlie",
            author_email="charlie@example.com",
            timestamp=datetime(2026, 1, 4),
            message="docs: readme update",
            files_changed=["README.md"],
        ),
    ]

    report = analyze_temporal_coupling(commits, min_co_changes=2, min_confidence=0.6)
    assert report.total_file_pairs >= 1
    assert len(report.coupled_pairs) >= 1

    top = report.coupled_pairs[0]
    assert {top.file_a, top.file_b} == {"src/api.py", "src/auth.py"}
    assert top.co_changes == 3
    assert top.confidence == 1.0
    assert top.jaccard == 1.0


def test_temporal_coupling_filters_lockfiles():
    commits = [
        CommitRecord(
            hash="c1",
            author_name="Alice",
            author_email="alice@example.com",
            timestamp=datetime(2026, 1, 1),
            message="update deps",
            files_changed=["poetry.lock", "pyproject.toml"],
        ),
        CommitRecord(
            hash="c2",
            author_name="Alice",
            author_email="alice@example.com",
            timestamp=datetime(2026, 1, 2),
            message="update deps 2",
            files_changed=["poetry.lock", "pyproject.toml"],
        ),
    ]

    report = analyze_temporal_coupling(commits, min_co_changes=2)
    # poetry.lock is excluded by default so no paired co-changes
    assert len(report.coupled_pairs) == 0

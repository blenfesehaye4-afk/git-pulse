from datetime import datetime
import pytest
from git_pulse.models import CommitRecord
from git_pulse.standup import generate_standup


def test_generate_standup():
    commits = [
        CommitRecord(
            hash="c1",
            author_name="Alice",
            author_email="alice@corp.com",
            timestamp=datetime(2026, 1, 1),
            message="feat: add OAuth login",
            insertions=50,
            deletions=5,
        ),
        CommitRecord(
            hash="c2",
            author_name="Alice",
            author_email="alice@corp.com",
            timestamp=datetime(2026, 1, 2),
            message="fix: handle expired tokens",
            insertions=10,
            deletions=2,
        ),
        CommitRecord(
            hash="c3",
            author_name="Bob",
            author_email="bob@corp.com",
            timestamp=datetime(2026, 1, 3),
            message="chore: bump dependencies",
            insertions=5,
            deletions=5,
        ),
    ]

    report = generate_standup(commits)
    assert report.total_commits == 3
    assert len(report.entries) == 2

    alice = next(e for e in report.entries if e.author_name == "Alice")
    assert alice.total_commits == 2
    assert alice.net_lines == 53
    assert len(alice.features) == 1
    assert len(alice.fixes) == 1
    assert "add OAuth login" in alice.features[0]

    md = report.to_markdown()
    assert "# 📋 Developer Standup Digest" in md
    assert "OAuth login" in md


def test_generate_standup_author_filter():
    commits = [
        CommitRecord(
            hash="c1",
            author_name="Alice",
            author_email="alice@corp.com",
            timestamp=datetime(2026, 1, 1),
            message="feat: add UI modal",
        ),
        CommitRecord(
            hash="c2",
            author_name="Bob",
            author_email="bob@corp.com",
            timestamp=datetime(2026, 1, 2),
            message="fix: resolve race condition",
        ),
    ]

    report = generate_standup(commits, author_filter="Bob")
    assert report.total_commits == 1
    assert len(report.entries) == 1
    assert report.entries[0].author_name == "Bob"

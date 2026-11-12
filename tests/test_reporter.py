"""Tests for Reporter output generation."""

import json
from datetime import datetime
from git_pulse.models import AuthorStats, ChurnMetric, RepoSummary
from git_pulse.reporter import Reporter


def test_reporter_markdown():
    summary = RepoSummary(
        repo_path="/test/repo",
        branch="main",
        total_commits=10,
        total_authors=2,
        first_commit_date=datetime(2025, 1, 1),
        last_commit_date=datetime(2025, 1, 10),
        top_authors=[
            AuthorStats(name="Alice", email="alice@test.com", commit_count=7, insertions=100, deletions=20, active_days=3),
            AuthorStats(name="Bob", email="bob@test.com", commit_count=3, insertions=30, deletions=5, active_days=1),
        ],
        top_churn_files=[
            ChurnMetric(file_path="main.py", change_count=5, insertions=80, deletions=15)
        ],
        commits_by_day_of_week={"Mon": 5, "Tue": 5, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0},
        commits_by_hour={h: (1 if h == 14 else 0) for h in range(24)},
        total_insertions=130,
        total_deletions=25,
    )
    reporter = Reporter()
    md = reporter.to_markdown(summary)
    assert "# ⚡ Git Pulse Repository Report" in md
    assert "Alice" in md
    assert "Bob" in md
    assert "`main.py`" in md


def test_reporter_json():
    summary = RepoSummary(
        repo_path="/test/repo",
        branch="main",
        total_commits=5,
        total_authors=1,
        first_commit_date=datetime(2025, 1, 1),
        last_commit_date=datetime(2025, 1, 5),
        top_authors=[
            AuthorStats(name="Moa", email="moa@test.com", commit_count=5, insertions=50, deletions=10, active_days=2)
        ],
        top_churn_files=[
            ChurnMetric(file_path="app.py", change_count=3, insertions=40, deletions=5)
        ],
        commits_by_day_of_week={"Mon": 5, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0},
        commits_by_hour={h: 0 for h in range(24)},
        total_insertions=50,
        total_deletions=10,
    )
    reporter = Reporter()
    raw_json = reporter.to_json(summary)
    data = json.loads(raw_json)
    assert data["total_commits"] == 5
    assert data["branch"] == "main"
    assert data["authors"][0]["name"] == "Moa"
    assert data["churn_hotspots"][0]["file"] == "app.py"


def test_reporter_html():
    summary = RepoSummary(
        repo_path="/test/repo",
        branch="main",
        total_commits=15,
        total_authors=2,
        first_commit_date=datetime(2025, 1, 1),
        last_commit_date=datetime(2025, 1, 10),
        top_authors=[
            AuthorStats(name="Alice", email="alice@test.com", commit_count=10, insertions=200, deletions=40, active_days=5)
        ],
        top_churn_files=[
            ChurnMetric(file_path="engine.py", change_count=8, insertions=150, deletions=30)
        ],
        commits_by_day_of_week={"Monday": 10, "Tuesday": 5},
        commits_by_hour={12: 15},
        total_insertions=200,
        total_deletions=40,
    )
    reporter = Reporter()
    html = reporter.to_html(summary)
    assert "<!DOCTYPE html>" in html
    assert "⚡ Git Pulse Analytics Dashboard" in html
    assert "<svg" in html
    assert "Alice" in html
    assert "engine.py" in html

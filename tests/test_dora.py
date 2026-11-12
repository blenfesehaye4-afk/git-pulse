from datetime import datetime, timedelta
import pytest
from git_pulse.models import CommitRecord
from git_pulse.dora import analyze_dora_metrics, DoraTier


def test_dora_metrics_empty():
    report = analyze_dora_metrics([])
    assert report.total_commits == 0
    assert report.deployment_frequency_per_week == 0.0
    assert report.overall_tier == DoraTier.LOW


def test_dora_metrics_calculation():
    base_time = datetime(2026, 1, 1, 10, 0, 0)
    commits = [
        CommitRecord(
            hash="c1",
            author_name="Alice",
            author_email="alice@test.com",
            timestamp=base_time,
            message="feat: user registration",
        ),
        CommitRecord(
            hash="c2",
            author_name="Alice",
            author_email="alice@test.com",
            timestamp=base_time + timedelta(hours=2),
            message="feat: password hashing",
        ),
        CommitRecord(
            hash="c3",
            author_name="Bob",
            author_email="bob@test.com",
            timestamp=base_time + timedelta(hours=4),
            message="fix: resolve hashing salt validation",
        ),
        CommitRecord(
            hash="c4",
            author_name="Alice",
            author_email="alice@test.com",
            timestamp=base_time + timedelta(hours=6),
            message="feat: email notifications",
        ),
    ]

    report = analyze_dora_metrics(commits)
    assert report.total_commits == 4
    # 1 fix out of 4 commits = 25% change failure rate
    assert report.change_failure_rate_pct == 25.0
    assert report.failure_rate_rating == DoraTier.HIGH
    assert report.avg_lead_time_hours == 2.0
    assert report.lead_time_rating == DoraTier.ELITE
    assert report.mean_time_to_recovery_hours == 2.0
    assert report.overall_tier in (DoraTier.ELITE, DoraTier.HIGH)

from datetime import datetime
import pytest
from git_pulse.models import BusFactorReport, ConventionalAuditResult, RepoSummary
from git_pulse.gate import evaluate_quality_gate


def test_quality_gate_passed():
    summary = RepoSummary(
        repo_path="/repo",
        branch="main",
        total_commits=50,
        total_authors=4,
        first_commit_date=datetime(2026, 1, 1),
        last_commit_date=datetime(2026, 1, 10),
        top_authors=[],
        top_churn_files=[],
        commits_by_day_of_week={},
        commits_by_hour={},
        total_insertions=500,
        total_deletions=100,
        bus_factor=BusFactorReport(total_analyzed_files=20, at_risk_files_count=2, overall_risk_pct=10.0),
        conventional_audit=ConventionalAuditResult(total_commits=50, compliant_commits=45, compliance_rate=90.0),
    )

    result = evaluate_quality_gate(
        summary,
        min_conventional_compliance_pct=80.0,
        max_bus_factor_risk_pct=30.0,
        max_hotspots_allowed=5,
    )

    assert result.passed
    assert result.failed_rules == 0
    assert result.passed_rules == 3
    assert "Quality Gate PASSED" in result.summary()


def test_quality_gate_failed():
    summary = RepoSummary(
        repo_path="/repo",
        branch="main",
        total_commits=20,
        total_authors=1,
        first_commit_date=datetime(2026, 1, 1),
        last_commit_date=datetime(2026, 1, 10),
        top_authors=[],
        top_churn_files=[],
        commits_by_day_of_week={},
        commits_by_hour={},
        total_insertions=100,
        total_deletions=10,
        bus_factor=BusFactorReport(total_analyzed_files=10, at_risk_files_count=8, overall_risk_pct=80.0),
        conventional_audit=ConventionalAuditResult(total_commits=20, compliant_commits=10, compliance_rate=50.0),
    )

    result = evaluate_quality_gate(
        summary,
        min_conventional_compliance_pct=80.0,
        max_bus_factor_risk_pct=40.0,
    )

    assert not result.passed
    assert result.failed_rules >= 1
    assert "Quality Gate FAILED" in result.summary()

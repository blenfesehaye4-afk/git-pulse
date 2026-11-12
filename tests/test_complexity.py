from pathlib import Path
import pytest
from git_pulse.models import ChurnMetric
from git_pulse.complexity import analyze_churn_complexity, RiskQuadrant


def test_analyze_churn_complexity(tmp_path: Path):
    # Create mock files
    hotspot_file = tmp_path / "big_engine.py"
    hotspot_file.write_text("\n".join(f"line_{i} = {i}" for i in range(250)))

    simple_file = tmp_path / "config.json"
    simple_file.write_text('{"key": "val"}\n')

    churn_metrics = [
        ChurnMetric(file_path="big_engine.py", change_count=30, insertions=300, deletions=50),
        ChurnMetric(file_path="config.json", change_count=2, insertions=5, deletions=1),
    ]

    report = analyze_churn_complexity(
        repo_path=tmp_path,
        churn_metrics=churn_metrics,
        churn_threshold=10,
        loc_threshold=50,
    )

    assert report.total_files_analyzed == 2
    assert report.hotspots_count == 1
    assert len(report.top_refactoring_targets) == 1

    target = report.top_refactoring_targets[0]
    assert target.file_path == "big_engine.py"
    assert target.risk_quadrant == RiskQuadrant.HOTSPOT
    assert target.lines_of_code >= 200
    assert target.refactoring_priority_score > 0

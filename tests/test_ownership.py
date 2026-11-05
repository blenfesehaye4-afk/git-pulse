from datetime import datetime
from git_pulse.models import CommitRecord
from git_pulse.ownership import analyze_ownership


def test_analyze_ownership_bus_factor():
    now = datetime.now()
    commits = [
        CommitRecord("c1", "Alice", "alice@example.com", now, "feat: a", files_changed=["core.py", "utils.py"]),
        CommitRecord("c2", "Alice", "alice@example.com", now, "fix: b", files_changed=["core.py"]),
        CommitRecord("c3", "Alice", "alice@example.com", now, "refactor: c", files_changed=["core.py"]),
        CommitRecord("c4", "Bob", "bob@example.com", now, "docs: d", files_changed=["utils.py"]),
    ]

    report = analyze_ownership(commits, min_commits_threshold=2)
    assert report.total_analyzed_files >= 1
    # core.py has 3 commits all by Alice -> 100% ownership -> high risk
    core_ownership = next((f for f in report.file_ownerships if f.file_path == "core.py"), None)
    assert core_ownership is not None
    assert core_ownership.primary_author == "Alice"
    assert core_ownership.primary_ownership_pct == 100.0
    assert core_ownership.is_at_risk is True

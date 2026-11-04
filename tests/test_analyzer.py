"""Tests for GitAnalyzer."""

import os
import subprocess
import tempfile
from pathlib import Path
import pytest

from git_pulse.analyzer import GitAnalyzer


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository with simulated commit history."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test Author"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)

        # First commit
        f1 = repo_path / "hello.py"
        f1.write_text("print('hello world')\n")
        subprocess.run(["git", "add", "hello.py"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

        # Second commit
        f1.write_text("print('hello world')\nprint('second line')\n")
        subprocess.run(["git", "add", "hello.py"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Add second line"], cwd=repo_path, check=True)

        yield repo_path


def test_analyzer_detects_git_repo(temp_git_repo):
    analyzer = GitAnalyzer(repo_path=str(temp_git_repo))
    assert analyzer._is_git_repo() is True
    assert analyzer.get_current_branch() == "main"


def test_analyzer_parses_commits(temp_git_repo):
    analyzer = GitAnalyzer(repo_path=str(temp_git_repo))
    commits = analyzer.parse_commits()
    assert len(commits) == 2
    assert commits[0].author_name == "Test Author"
    assert commits[0].author_email == "test@example.com"
    assert "hello.py" in commits[0].files_changed


def test_analyzer_generates_summary(temp_git_repo):
    analyzer = GitAnalyzer(repo_path=str(temp_git_repo))
    summary = analyzer.analyze()
    assert summary.total_commits == 2
    assert summary.total_authors == 1
    assert summary.branch == "main"
    assert len(summary.top_authors) == 1
    assert summary.top_authors[0].commit_count == 2
    assert len(summary.top_churn_files) >= 1
    assert summary.top_churn_files[0].file_path == "hello.py"
    assert summary.total_insertions > 0


def test_analyzer_invalid_path():
    with tempfile.TemporaryDirectory() as empty_dir:
        with pytest.raises(ValueError):
            GitAnalyzer(repo_path=empty_dir)

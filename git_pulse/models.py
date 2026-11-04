"""Data models for git-pulse."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class CommitRecord:
    hash: str
    author_name: str
    author_email: str
    timestamp: datetime
    message: str
    insertions: int = 0
    deletions: int = 0
    files_changed: List[str] = field(default_factory=list)


@dataclass
class AuthorStats:
    name: str
    email: str
    commit_count: int = 0
    insertions: int = 0
    deletions: int = 0
    first_commit: Optional[datetime] = None
    last_commit: Optional[datetime] = None
    active_days: int = 0


@dataclass
class ChurnMetric:
    file_path: str
    change_count: int
    insertions: int = 0
    deletions: int = 0


@dataclass
class RepoSummary:
    repo_path: str
    branch: str
    total_commits: int
    total_authors: int
    first_commit_date: Optional[datetime]
    last_commit_date: Optional[datetime]
    top_authors: List[AuthorStats]
    top_churn_files: List[ChurnMetric]
    commits_by_day_of_week: Dict[str, int]
    commits_by_hour: Dict[int, int]
    total_insertions: int
    total_deletions: int

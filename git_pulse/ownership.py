"""Code ownership and Bus Factor risk analysis."""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Mapping, Sequence
from .models import CommitRecord


@dataclass
class FileOwnership:
    file_path: str
    primary_author: str
    primary_ownership_pct: float
    total_commits: int
    authors_count: int
    is_at_risk: bool  # True if single author owns >= 80% with >= 3 commits


@dataclass
class BusFactorReport:
    total_analyzed_files: int
    at_risk_files_count: int
    overall_risk_pct: float
    file_ownerships: list[FileOwnership] = field(default_factory=list)


def analyze_ownership(
    commits: Sequence[CommitRecord],
    risk_threshold_pct: float = 80.0,
    min_commits_threshold: int = 2,
) -> BusFactorReport:
    """Analyze author distribution across files to identify key-person dependencies."""
    file_author_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for c in commits:
        for f in c.files_changed:
            file_author_counts[f][c.author_name] += 1

    file_ownerships: list[FileOwnership] = []
    at_risk_count = 0

    for file_path, author_counts in file_author_counts.items():
        total_file_commits = sum(author_counts.values())
        if total_file_commits < min_commits_threshold:
            continue

        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        primary_author, primary_count = sorted_authors[0]
        ownership_pct = round((primary_count / total_file_commits) * 100.0, 1)

        is_risk = ownership_pct >= risk_threshold_pct
        if is_risk:
            at_risk_count += 1

        file_ownerships.append(
            FileOwnership(
                file_path=file_path,
                primary_author=primary_author,
                primary_ownership_pct=ownership_pct,
                total_commits=total_file_commits,
                authors_count=len(author_counts),
                is_at_risk=is_risk,
            )
        )

    file_ownerships.sort(key=lambda x: (x.is_at_risk, x.total_commits), reverse=True)
    total_files = len(file_ownerships)
    risk_pct = round((at_risk_count / total_files) * 100.0, 1) if total_files > 0 else 0.0

    return BusFactorReport(
        total_analyzed_files=total_files,
        at_risk_files_count=at_risk_count,
        overall_risk_pct=risk_pct,
        file_ownerships=file_ownerships,
    )

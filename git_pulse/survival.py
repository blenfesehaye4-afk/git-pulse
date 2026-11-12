"""Code survival and line longevity analysis."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .models import CommitRecord


@dataclass
class AuthorSurvivalMetric:
    author: str
    total_insertions: int
    total_deletions: int
    net_lines: int
    survival_rate_pct: float  # (net_lines / total_insertions) * 100


@dataclass
class FileSurvivalMetric:
    file_path: str
    total_insertions: int
    total_deletions: int
    net_lines: int
    survival_rate_pct: float
    is_volatile: bool  # Deletions close to or greater than insertions


@dataclass
class CodeSurvivalReport:
    total_insertions: int
    total_deletions: int
    net_lines: int
    overall_survival_rate_pct: float
    author_metrics: List[AuthorSurvivalMetric] = field(default_factory=list)
    volatile_files: List[FileSurvivalMetric] = field(default_factory=list)


def analyze_code_survival(
    commits: List[CommitRecord],
    min_insertions_threshold: int = 10,
    volatility_threshold: float = 40.0,
) -> CodeSurvivalReport:
    """
    Computes code survival and stability across contributors and files.
    Identifies high-volatility files where code is rewritten or discarded quickly.
    """
    total_ins = sum(c.insertions for c in commits)
    total_del = sum(c.deletions for c in commits)
    net_total = total_ins - total_del
    overall_survival = (net_total / total_ins * 100.0) if total_ins > 0 else 100.0

    # Aggregate by author
    author_ins: Dict[str, int] = defaultdict(int)
    author_del: Dict[str, int] = defaultdict(int)
    for c in commits:
        author_ins[c.author_name] += c.insertions
        author_del[c.author_name] += c.deletions

    author_metrics: List[AuthorSurvivalMetric] = []
    for author, ins in author_ins.items():
        dels = author_del[author]
        net = ins - dels
        rate = (net / ins * 100.0) if ins > 0 else 0.0
        author_metrics.append(
            AuthorSurvivalMetric(
                author=author,
                total_insertions=ins,
                total_deletions=dels,
                net_lines=net,
                survival_rate_pct=round(rate, 2),
            )
        )
    author_metrics.sort(key=lambda x: x.net_lines, reverse=True)

    # Aggregate by file
    file_ins: Dict[str, int] = defaultdict(int)
    file_del: Dict[str, int] = defaultdict(int)
    # Estimate file-level stats from commits
    for c in commits:
        num_files = len(c.files_changed)
        if num_files == 0:
            continue
        # Allocate insertions/deletions equally among changed files if per-file stat isn't granular
        avg_ins = c.insertions // num_files
        avg_del = c.deletions // num_files
        for f in c.files_changed:
            file_ins[f] += avg_ins
            file_del[f] += avg_del

    volatile_files: List[FileSurvivalMetric] = []
    for f, ins in file_ins.items():
        if ins < min_insertions_threshold:
            continue
        dels = file_del[f]
        net = ins - dels
        rate = (net / ins * 100.0) if ins > 0 else 0.0
        is_vol = rate < volatility_threshold
        metric = FileSurvivalMetric(
            file_path=f,
            total_insertions=ins,
            total_deletions=dels,
            net_lines=net,
            survival_rate_pct=round(rate, 2),
            is_volatile=is_vol,
        )
        if is_vol:
            volatile_files.append(metric)

    volatile_files.sort(key=lambda x: x.survival_rate_pct)

    return CodeSurvivalReport(
        total_insertions=total_ins,
        total_deletions=total_del,
        net_lines=net_total,
        overall_survival_rate_pct=round(overall_survival, 2),
        author_metrics=author_metrics,
        volatile_files=volatile_files,
    )

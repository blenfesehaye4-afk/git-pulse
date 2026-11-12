"""Temporal file co-change coupling analysis."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import itertools
from typing import Dict, List, Set, Tuple

from .models import CommitRecord


@dataclass
class FileCoupling:
    """Represents a coupled pair of files frequently committed together."""
    file_a: str
    file_b: str
    co_changes: int
    commits_a: int
    commits_b: int
    confidence: float  # P(B|A) = co_changes / commits_a
    jaccard: float     # co_changes / (commits_a + commits_b - co_changes)


@dataclass
class TemporalCouplingReport:
    """Report detailing architectural temporal coupling risks."""
    total_file_pairs: int
    coupled_pairs: List[FileCoupling] = field(default_factory=list)


def analyze_temporal_coupling(
    commits: List[CommitRecord],
    min_co_changes: int = 2,
    min_confidence: float = 0.5,
    exclude_patterns: Tuple[str, ...] = (".lock", "package-lock.json", "poetry.lock"),
) -> TemporalCouplingReport:
    """
    Analyzes commit history to detect files that frequently change together (temporal coupling).
    High coupling between distinct components indicates hidden dependencies and refactoring targets.
    """
    file_commit_counts: Dict[str, int] = defaultdict(int)
    co_change_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for commit in commits:
        # Filter out noisy or generated lockfiles
        files = sorted(list({
            f for f in commit.files_changed
            if not any(f.endswith(pat) for pat in exclude_patterns)
        }))

        # Increment individual commit counts
        for f in files:
            file_commit_counts[f] += 1

        # Increment pairwise co-change counts (files sorted to ensure consistent key)
        for f1, f2 in itertools.combinations(files, 2):
            co_change_counts[(f1, f2)] += 1

    coupled: List[FileCoupling] = []

    for (f1, f2), count in co_change_counts.items():
        if count < min_co_changes:
            continue

        c1 = file_commit_counts[f1]
        c2 = file_commit_counts[f2]
        union = c1 + c2 - count
        jaccard = count / union if union > 0 else 0.0

        # Confidence is max directional conditional probability
        conf1 = count / c1 if c1 > 0 else 0.0
        conf2 = count / c2 if c2 > 0 else 0.0
        max_conf = max(conf1, conf2)

        if max_conf >= min_confidence:
            coupled.append(
                FileCoupling(
                    file_a=f1,
                    file_b=f2,
                    co_changes=count,
                    commits_a=c1,
                    commits_b=c2,
                    confidence=round(max_conf, 3),
                    jaccard=round(jaccard, 3),
                )
            )

    # Sort descending by co_changes and jaccard similarity
    coupled.sort(key=lambda x: (x.co_changes, x.jaccard), reverse=True)

    return TemporalCouplingReport(
        total_file_pairs=len(co_change_counts),
        coupled_pairs=coupled,
    )

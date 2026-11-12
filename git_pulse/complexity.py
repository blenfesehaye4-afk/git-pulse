"""Churn-complexity risk quadrant categorizer for technical debt hotspot detection.
Inspired by Adam Tornhill's 'Your Code as a Crime Scene'.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

from .models import ChurnMetric


class RiskQuadrant(str, Enum):
    HOTSPOT = "Hotspot (High Churn, High Complexity)"
    DORMANT_DEBT = "Dormant Debt (Low Churn, High Complexity)"
    ACTIVE_SIMPLE = "Active Simple (High Churn, Low Complexity)"
    STABLE = "Stable (Low Churn, Low Complexity)"


@dataclass
class FileRiskMetric:
    """Combines change frequency (churn) with code size/complexity to assess maintenance risk."""
    file_path: str
    churn_count: int
    lines_of_code: int
    risk_quadrant: RiskQuadrant
    refactoring_priority_score: float  # churn * log(LOC + 1)


@dataclass
class ChurnComplexityReport:
    """Overview of repository technical debt quadrants and top refactoring priorities."""
    total_files_analyzed: int
    hotspots_count: int
    dormant_debt_count: int
    top_refactoring_targets: List[FileRiskMetric] = field(default_factory=list)


def count_file_lines(file_path: Path) -> int:
    """Count non-empty lines of code in file on disk."""
    try:
        if not file_path.is_file():
            return 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def analyze_churn_complexity(
    repo_path: Path,
    churn_metrics: List[ChurnMetric],
    churn_threshold: Optional[int] = None,
    loc_threshold: Optional[int] = None,
) -> ChurnComplexityReport:
    """
    Categorizes repository files into four architectural risk quadrants based on
    historical churn frequency and file line volume.
    """
    if not churn_metrics:
        return ChurnComplexityReport(total_files_analyzed=0, hotspots_count=0, dormant_debt_count=0)

    # Compute median / average thresholds if not explicitly supplied
    churn_vals = [m.change_count for m in churn_metrics]
    default_churn_thresh = churn_threshold or (sum(churn_vals) // len(churn_vals) if churn_vals else 5)

    file_locs: List[int] = []
    file_stats: List[tuple[ChurnMetric, int]] = []

    for cm in churn_metrics:
        full_path = repo_path / cm.file_path
        loc = count_file_lines(full_path)
        if loc == 0:
            # Fall back to net insertions from churn metric as estimate if file deleted or moved
            loc = max(10, cm.insertions - cm.deletions)
        file_locs.append(loc)
        file_stats.append((cm, loc))

    default_loc_thresh = loc_threshold or (sum(file_locs) // len(file_locs) if file_locs else 100)

    results: List[FileRiskMetric] = []
    hotspots = 0
    dormant = 0

    for cm, loc in file_stats:
        high_churn = cm.change_count >= default_churn_thresh
        high_loc = loc >= default_loc_thresh

        if high_churn and high_loc:
            quadrant = RiskQuadrant.HOTSPOT
            hotspots += 1
        elif not high_churn and high_loc:
            quadrant = RiskQuadrant.DORMANT_DEBT
            dormant += 1
        elif high_churn and not high_loc:
            quadrant = RiskQuadrant.ACTIVE_SIMPLE
        else:
            quadrant = RiskQuadrant.STABLE

        # Priority score = churn * log10(loc + 10)
        import math
        priority = round(cm.change_count * math.log10(loc + 10), 2)

        results.append(
            FileRiskMetric(
                file_path=cm.file_path,
                churn_count=cm.change_count,
                lines_of_code=loc,
                risk_quadrant=quadrant,
                refactoring_priority_score=priority,
            )
        )

    # Sort descending by refactoring priority
    results.sort(key=lambda x: x.refactoring_priority_score, reverse=True)

    return ChurnComplexityReport(
        total_files_analyzed=len(results),
        hotspots_count=hotspots,
        dormant_debt_count=dormant,
        top_refactoring_targets=[r for r in results if r.risk_quadrant == RiskQuadrant.HOTSPOT],
    )

"""DORA (DevOps Research and Assessment) engineering delivery metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple

from .models import CommitRecord


class DoraTier(str, Enum):
    ELITE = "Elite"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class DoraMetricsReport:
    """Four core DORA software delivery performance metrics."""
    total_commits: int
    deployment_frequency_per_week: float
    deployment_rating: DoraTier
    avg_lead_time_hours: float
    lead_time_rating: DoraTier
    change_failure_rate_pct: float
    failure_rate_rating: DoraTier
    mean_time_to_recovery_hours: Optional[float]
    recovery_rating: DoraTier
    overall_tier: DoraTier


def analyze_dora_metrics(
    commits: List[CommitRecord],
    release_tags: Optional[List[Tuple[str, datetime]]] = None,
) -> DoraMetricsReport:
    """
    Evaluates DORA metrics from git commit history and release milestones:
    - Deployment Frequency: Releases or mainline integrations per week
    - Lead Time for Changes: Duration between feature commits and release/merge
    - Change Failure Rate: Percentage of commits requiring bug fixes or reverts
    - Mean Time to Recovery (MTTR): Time elapsed between defect detection and hotfix
    """
    if not commits:
        return DoraMetricsReport(
            total_commits=0,
            deployment_frequency_per_week=0.0,
            deployment_rating=DoraTier.LOW,
            avg_lead_time_hours=0.0,
            lead_time_rating=DoraTier.LOW,
            change_failure_rate_pct=0.0,
            failure_rate_rating=DoraTier.ELITE,
            mean_time_to_recovery_hours=None,
            recovery_rating=DoraTier.LOW,
            overall_tier=DoraTier.LOW,
        )

    # Sort commits chronologically
    sorted_commits = sorted(commits, key=lambda c: c.timestamp)
    first_time = sorted_commits[0].timestamp
    last_time = sorted_commits[-1].timestamp
    span_days = max(1.0, (last_time - first_time).total_seconds() / 86400.0)
    span_weeks = max(1.0 / 7.0, span_days / 7.0)

    # 1. Deployment Frequency
    deployments_count = len(release_tags) if release_tags else max(1, len(commits) // 5)
    deploy_freq_per_week = round(deployments_count / span_weeks, 2)

    if deploy_freq_per_week >= 7.0:  # Multiple per day / daily
        deploy_tier = DoraTier.ELITE
    elif deploy_freq_per_week >= 1.0:  # Weekly
        deploy_tier = DoraTier.HIGH
    elif deploy_freq_per_week >= 0.25:  # Monthly
        deploy_tier = DoraTier.MEDIUM
    else:
        deploy_tier = DoraTier.LOW

    # 2. Lead Time for Changes (average commit interval or tag interval)
    if len(sorted_commits) > 1:
        intervals = [
            (sorted_commits[i].timestamp - sorted_commits[i - 1].timestamp).total_seconds() / 3600.0
            for i in range(1, len(sorted_commits))
        ]
        avg_lead_time = round(sum(intervals) / len(intervals), 2)
    else:
        avg_lead_time = 1.0

    if avg_lead_time <= 24.0:
        lead_tier = DoraTier.ELITE
    elif avg_lead_time <= 168.0:  # 1 week
        lead_tier = DoraTier.HIGH
    elif avg_lead_time <= 720.0:  # 1 month
        lead_tier = DoraTier.MEDIUM
    else:
        lead_tier = DoraTier.LOW

    # 3. Change Failure Rate
    fix_keywords = ("fix:", "fix(", "hotfix", "bugfix", "revert:", "patch:")
    failing_commits = sum(
        1 for c in commits
        if any(c.message.lower().startswith(kw) or f" {kw}" in c.message.lower() for kw in fix_keywords)
    )
    cfr = round((failing_commits / len(commits)) * 100.0, 2)

    if cfr <= 15.0:
        cfr_tier = DoraTier.ELITE
    elif cfr <= 30.0:
        cfr_tier = DoraTier.HIGH
    elif cfr <= 45.0:
        cfr_tier = DoraTier.MEDIUM
    else:
        cfr_tier = DoraTier.LOW

    # 4. MTTR (time between a failure commit and subsequent fix commit)
    mttr_hours: Optional[float] = None
    fix_indices = [
        i for i, c in enumerate(sorted_commits)
        if any(c.message.lower().startswith(kw) for kw in fix_keywords)
    ]
    recovery_intervals = []
    for idx in fix_indices:
        if idx > 0:
            dt = (sorted_commits[idx].timestamp - sorted_commits[idx - 1].timestamp).total_seconds() / 3600.0
            if dt > 0:
                recovery_intervals.append(dt)

    if recovery_intervals:
        mttr_hours = round(sum(recovery_intervals) / len(recovery_intervals), 2)
        if mttr_hours <= 1.0:
            recovery_tier = DoraTier.ELITE
        elif mttr_hours <= 24.0:
            recovery_tier = DoraTier.HIGH
        elif mttr_hours <= 168.0:
            recovery_tier = DoraTier.MEDIUM
        else:
            recovery_tier = DoraTier.LOW
    else:
        recovery_tier = DoraTier.ELITE  # No defect fixes needed

    # Overall tier scoring (average)
    score_map = {DoraTier.ELITE: 4, DoraTier.HIGH: 3, DoraTier.MEDIUM: 2, DoraTier.LOW: 1}
    avg_score = (score_map[deploy_tier] + score_map[lead_tier] + score_map[cfr_tier] + score_map[recovery_tier]) / 4.0

    if avg_score >= 3.5:
        overall = DoraTier.ELITE
    elif avg_score >= 2.5:
        overall = DoraTier.HIGH
    elif avg_score >= 1.5:
        overall = DoraTier.MEDIUM
    else:
        overall = DoraTier.LOW

    return DoraMetricsReport(
        total_commits=len(commits),
        deployment_frequency_per_week=deploy_freq_per_week,
        deployment_rating=deploy_tier,
        avg_lead_time_hours=avg_lead_time,
        lead_time_rating=lead_tier,
        change_failure_rate_pct=cfr,
        failure_rate_rating=cfr_tier,
        mean_time_to_recovery_hours=mttr_hours,
        recovery_rating=recovery_tier,
        overall_tier=overall,
    )

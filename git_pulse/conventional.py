"""Conventional Commits auditor for git-pulse."""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Sequence

CONVENTIONAL_REGEX = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\((?P<scope>[a-zA-Z0-9_\-\.\/]+)\))?"
    r"(?P<breaking>!)?"
    r":\s+(?P<description>.+)$"
)


@dataclass
class ConventionalAuditResult:
    total_commits: int
    compliant_commits: int
    compliance_rate: float
    type_counts: dict[str, int] = field(default_factory=dict)
    breaking_changes: int = 0
    non_compliant_samples: list[str] = field(default_factory=list)


def audit_commits(messages: Sequence[str]) -> ConventionalAuditResult:
    """Audit a list of commit subject lines for Conventional Commits adherence."""
    total = len(messages)
    if total == 0:
        return ConventionalAuditResult(
            total_commits=0, compliant_commits=0, compliance_rate=100.0
        )

    compliant = 0
    type_counts: dict[str, int] = {}
    breaking_count = 0
    non_compliant: list[str] = []

    for msg in messages:
        subject = msg.strip().splitlines()[0] if msg.strip() else ""
        if not subject:
            continue

        match = CONVENTIONAL_REGEX.match(subject)
        if match:
            compliant += 1
            ctype = match.group("type")
            type_counts[ctype] = type_counts.get(ctype, 0) + 1
            if match.group("breaking"):
                breaking_count += 1
        else:
            if len(non_compliant) < 5:
                non_compliant.append(subject)

    rate = round((compliant / total) * 100.0, 1) if total > 0 else 0.0

    return ConventionalAuditResult(
        total_commits=total,
        compliant_commits=compliant,
        compliance_rate=rate,
        type_counts=dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
        breaking_changes=breaking_count,
        non_compliant_samples=non_compliant,
    )

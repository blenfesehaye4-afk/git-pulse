"""Developer daily standup and weekly digest generator."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .models import CommitRecord


@dataclass
class StandupEntry:
    """Individual author's work activity breakdown for standup meetings."""
    author_name: str
    author_email: str
    features: List[str] = field(default_factory=list)
    fixes: List[str] = field(default_factory=list)
    chores: List[str] = field(default_factory=list)
    total_commits: int = 0
    insertions: int = 0
    deletions: int = 0

    @property
    def net_lines(self) -> int:
        return self.insertions - self.deletions

    def to_markdown(self) -> str:
        lines = [f"### 👤 {self.author_name} ({self.total_commits} commits, +{self.insertions}/-{self.deletions})"]
        if self.features:
            lines.append("**✨ Features & Enhancements:**")
            lines.extend(f"- {msg}" for msg in self.features)
        if self.fixes:
            lines.append("**🐛 Bug Fixes:**")
            lines.extend(f"- {msg}" for msg in self.fixes)
        if self.chores:
            lines.append("**🔧 Maintenance & Chores:**")
            lines.extend(f"- {msg}" for msg in self.chores)
        return "\n".join(lines)


@dataclass
class StandupReport:
    """Consolidated standup digest across active authors."""
    total_commits: int
    entries: List[StandupEntry] = field(default_factory=list)

    def to_markdown(self) -> str:
        header = f"# 📋 Developer Standup Digest\n**Total Commits:** {self.total_commits}\n\n"
        body = "\n\n".join(e.to_markdown() for e in self.entries)
        return header + body


def generate_standup(
    commits: List[CommitRecord],
    author_filter: Optional[str] = None,
) -> StandupReport:
    """
    Parses commit history into categorized features, fixes, and chores
    ready for daily standup updates or weekly engineering digests.
    """
    author_map: Dict[str, StandupEntry] = {}

    for c in commits:
        if author_filter and author_filter.lower() not in c.author_name.lower() and author_filter.lower() not in c.author_email.lower():
            continue

        key = c.author_name
        if key not in author_map:
            author_map[key] = StandupEntry(author_name=c.author_name, author_email=c.author_email)

        entry = author_map[key]
        entry.total_commits += 1
        entry.insertions += c.insertions
        entry.deletions += c.deletions

        msg = c.message.strip()
        low_msg = msg.lower()

        if low_msg.startswith("feat") or "feature" in low_msg:
            entry.features.append(msg)
        elif low_msg.startswith("fix") or "bug" in low_msg or "hotfix" in low_msg:
            entry.fixes.append(msg)
        else:
            entry.chores.append(msg)

    entries = sorted(list(author_map.values()), key=lambda e: e.total_commits, reverse=True)
    return StandupReport(total_commits=sum(e.total_commits for e in entries), entries=entries)

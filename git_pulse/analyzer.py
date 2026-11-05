"""Git repository analyzer engine."""

import os
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import (
    AuthorStats,
    ChurnMetric,
    CommitRecord,
    RepoSummary,
)
from .ownership import analyze_ownership
from .conventional import audit_commits


class GitAnalyzer:
    """Extracts and analyzes git repository history and metrics."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        if not self._is_git_repo():
            raise ValueError(f"Path '{self.repo_path}' is not a valid Git repository.")

    def _is_git_repo(self) -> bool:
        """Check whether the directory is a git repository."""
        git_dir = self.repo_path / ".git"
        if git_dir.exists():
            return True
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            return res.returncode == 0 and res.stdout.strip() == "true"
        except Exception:
            return False

    def _run_git(self, args: List[str]) -> str:
        """Execute a git command within the target repo."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: git {' '.join(args)}\n{result.stderr}")
        return result.stdout

    def get_current_branch(self) -> str:
        """Retrieve the currently checked out branch name."""
        try:
            out = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
            return out if out else "HEAD"
        except Exception:
            return "unknown"

    def parse_commits(self, max_count: Optional[int] = None, since: Optional[str] = None) -> List[CommitRecord]:
        """Parse git commits with author, timestamp, changes, and files."""
        cmd = ["log", "--pretty=format:COMMIT_START%n%H%n%an%n%ae%n%aI%n%s", "--numstat"]
        if max_count:
            cmd.extend(["-n", str(max_count)])
        if since:
            cmd.extend(["--since", since])

        output = self._run_git(cmd)
        commits: List[CommitRecord] = []
        raw_blocks = output.split("COMMIT_START\n")

        for block in raw_blocks:
            lines = [l for l in block.splitlines() if l.strip()]
            if len(lines) < 4:
                continue

            commit_hash = lines[0].strip()
            author_name = lines[1].strip()
            author_email = lines[2].strip()
            iso_time = lines[3].strip()
            message = lines[4].strip() if len(lines) > 4 else ""

            try:
                dt = datetime.fromisoformat(iso_time)
            except Exception:
                dt = datetime.now()

            insertions = 0
            deletions = 0
            files_changed = []

            for stat_line in lines[5:]:
                parts = stat_line.split("\t")
                if len(parts) == 3:
                    ins_str, del_str, file_name = parts
                    ins = int(ins_str) if ins_str.isdigit() else 0
                    dels = int(del_str) if del_str.isdigit() else 0
                    insertions += ins
                    deletions += dels
                    files_changed.append(file_name)

            commits.append(
                CommitRecord(
                    hash=commit_hash,
                    author_name=author_name,
                    author_email=author_email,
                    timestamp=dt,
                    message=message,
                    insertions=insertions,
                    deletions=deletions,
                    files_changed=files_changed,
                )
            )

        return commits

    def analyze(self, max_count: Optional[int] = None, since: Optional[str] = None) -> RepoSummary:
        """Run full analytics on the repository."""
        commits = self.parse_commits(max_count=max_count, since=since)
        branch = self.get_current_branch()

        if not commits:
            return RepoSummary(
                repo_path=str(self.repo_path),
                branch=branch,
                total_commits=0,
                total_authors=0,
                first_commit_date=None,
                last_commit_date=None,
                top_authors=[],
                top_churn_files=[],
                commits_by_day_of_week={d: 0 for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
                commits_by_hour={h: 0 for h in range(24)},
                total_insertions=0,
                total_deletions=0,
                bus_factor=None,
                conventional_audit=None,
            )

        author_map: Dict[str, AuthorStats] = {}
        author_dates: Dict[str, set] = defaultdict(set)
        churn_map: Dict[str, Tuple[int, int, int]] = defaultdict(lambda: (0, 0, 0)) # changes, ins, del
        day_map = {d: 0 for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
        hour_map = {h: 0 for h in range(24)}
        days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        total_ins = 0
        total_del = 0

        for c in commits:
            key = f"{c.author_name} <{c.author_email}>"
            if key not in author_map:
                author_map[key] = AuthorStats(
                    name=c.author_name,
                    email=c.author_email,
                    first_commit=c.timestamp,
                    last_commit=c.timestamp,
                )

            author = author_map[key]
            author.commit_count += 1
            author.insertions += c.insertions
            author.deletions += c.deletions

            if author.first_commit is None or c.timestamp < author.first_commit:
                author.first_commit = c.timestamp
            if author.last_commit is None or c.timestamp > author.last_commit:
                author.last_commit = c.timestamp

            author_dates[key].add(c.timestamp.date())

            total_ins += c.insertions
            total_del += c.deletions

            for f in c.files_changed:
                cnt, ins_c, del_c = churn_map[f]
                churn_map[f] = (cnt + 1, ins_c + c.insertions, del_c + c.deletions)

            day_str = days_order[c.timestamp.weekday()]
            day_map[day_str] += 1
            hour_map[c.timestamp.hour] += 1

        for key, author in author_map.items():
            author.active_days = len(author_dates[key])

        top_authors = sorted(author_map.values(), key=lambda a: a.commit_count, reverse=True)
        top_churn = [
            ChurnMetric(file_path=k, change_count=v[0], insertions=v[1], deletions=v[2])
            for k, v in sorted(churn_map.items(), key=lambda item: item[1][0], reverse=True)[:15]
        ]

        dates = [c.timestamp for c in commits]
        first_date = min(dates) if dates else None
        last_date = max(dates) if dates else None

        # Analyze bus factor and conventional commits compliance
        bus_factor_report = analyze_ownership(commits)
        conventional_report = audit_commits([c.message for c in commits])

        return RepoSummary(
            repo_path=str(self.repo_path),
            branch=branch,
            total_commits=len(commits),
            total_authors=len(author_map),
            first_commit_date=first_date,
            last_commit_date=last_date,
            top_authors=top_authors,
            top_churn_files=top_churn,
            commits_by_day_of_week=day_map,
            commits_by_hour=hour_map,
            total_insertions=total_ins,
            total_deletions=total_del,
            bus_factor=bus_factor_report,
            conventional_audit=conventional_report,
        )

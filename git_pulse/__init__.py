"""
git-pulse: Modern repository intelligence & developer analytics CLI.
"""

__version__ = "0.1.0"
__author__ = "Blen Fesehaye"

from .analyzer import GitAnalyzer
from .models import AuthorStats, ChurnMetric, CommitRecord, RepoSummary

__all__ = ["GitAnalyzer", "AuthorStats", "ChurnMetric", "CommitRecord", "RepoSummary"]

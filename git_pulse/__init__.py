"""
git-pulse: Modern developer repository intelligence & analytics CLI.
"""

from .analyzer import GitAnalyzer
from .reporter import Reporter
from .coupling import analyze_temporal_coupling, FileCoupling, TemporalCouplingReport
from .survival import analyze_code_survival, CodeSurvivalReport, AuthorSurvivalMetric, FileSurvivalMetric
from .dora import analyze_dora_metrics, DoraMetricsReport, DoraTier
from .complexity import analyze_churn_complexity, ChurnComplexityReport, RiskQuadrant, FileRiskMetric
from .standup import generate_standup, StandupReport, StandupEntry
from .gate import evaluate_quality_gate, QualityGateResult, GateRuleResult
from .ownership import analyze_ownership
from .conventional import audit_commits
from .models import (
    AuthorStats,
    BusFactorReport,
    ChurnMetric,
    CommitRecord,
    ConventionalAuditResult,
    FileOwnership,
    RepoSummary,
)
try:
    from .server import app as server_app
except ImportError:  # pragma: no cover
    server_app = None  # type: ignore

__version__ = "0.3.0"
__author__ = "Blen Fesehaye"

__all__ = [
    "GitAnalyzer",
    "Reporter",
    "analyze_temporal_coupling",
    "FileCoupling",
    "TemporalCouplingReport",
    "analyze_code_survival",
    "CodeSurvivalReport",
    "AuthorSurvivalMetric",
    "FileSurvivalMetric",
    "analyze_dora_metrics",
    "DoraMetricsReport",
    "DoraTier",
    "analyze_churn_complexity",
    "ChurnComplexityReport",
    "RiskQuadrant",
    "FileRiskMetric",
    "generate_standup",
    "StandupReport",
    "StandupEntry",
    "evaluate_quality_gate",
    "QualityGateResult",
    "GateRuleResult",
    "analyze_ownership",
    "audit_commits",
    "AuthorStats",
    "BusFactorReport",
    "ChurnMetric",
    "CommitRecord",
    "ConventionalAuditResult",
    "FileOwnership",
    "RepoSummary",
    "server_app",
]

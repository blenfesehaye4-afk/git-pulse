"""CI/CD Quality Gate auditor with configurable threshold rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .models import RepoSummary


@dataclass
class GateRuleResult:
    rule_name: str
    target_threshold: float
    actual_value: float
    comparator: str  # '>=' or '<='
    passed: bool
    description: str


@dataclass
class QualityGateResult:
    """Overall outcome of the CI/CD quality gate check."""
    passed: bool
    total_rules: int
    passed_rules: int
    failed_rules: int
    rule_results: List[GateRuleResult] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        return f"Quality Gate {status} ({self.passed_rules}/{self.total_rules} rules met)"


def evaluate_quality_gate(
    summary: RepoSummary,
    min_conventional_compliance_pct: float = 80.0,
    max_bus_factor_risk_pct: float = 50.0,
    max_change_failure_rate_pct: float = 35.0,
    max_hotspots_allowed: int = 10,
) -> QualityGateResult:
    """
    Evaluates repository metrics against strict CI/CD quality gate criteria.
    Fails build if key health indicators breach agreed standards.
    """
    results: List[GateRuleResult] = []

    # 1. Conventional Commits Compliance
    if summary.conventional_audit:
        actual_conv = summary.conventional_audit.compliance_rate
        conv_pass = actual_conv >= min_conventional_compliance_pct
        results.append(
            GateRuleResult(
                rule_name="Conventional Commits Compliance",
                target_threshold=min_conventional_compliance_pct,
                actual_value=actual_conv,
                comparator=">=",
                passed=conv_pass,
                description=f"Requires at least {min_conventional_compliance_pct}% conventional commits; found {actual_conv}%.",
            )
        )

    # 2. Bus Factor Risk
    if summary.bus_factor:
        actual_risk = summary.bus_factor.overall_risk_pct
        risk_pass = actual_risk <= max_bus_factor_risk_pct
        results.append(
            GateRuleResult(
                rule_name="Bus Factor Ownership Concentration",
                target_threshold=max_bus_factor_risk_pct,
                actual_value=actual_risk,
                comparator="<=",
                passed=risk_pass,
                description=f"Max allowable single-author risk is {max_bus_factor_risk_pct}%; found {actual_risk}%.",
            )
        )

    # 3. Churn Hotspots
    actual_hotspots = len(summary.top_churn_files)
    hotspots_pass = actual_hotspots <= max_hotspots_allowed
    results.append(
        GateRuleResult(
            rule_name="Code Churn Hotspot Limit",
            target_threshold=float(max_hotspots_allowed),
            actual_value=float(actual_hotspots),
            comparator="<=",
            passed=hotspots_pass,
            description=f"Max allowed critical churn files is {max_hotspots_allowed}; found {actual_hotspots}.",
        )
    )

    all_passed = all(r.passed for r in results) if results else True
    passed_count = sum(1 for r in results if r.passed)

    return QualityGateResult(
        passed=all_passed,
        total_rules=len(results),
        passed_rules=passed_count,
        failed_rules=len(results) - passed_count,
        rule_results=results,
    )

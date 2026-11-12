"""FastAPI REST API service for Git Pulse repository intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .analyzer import GitAnalyzer
from .dora import analyze_dora_metrics
from .coupling import analyze_temporal_coupling
from .standup import generate_standup
from .reporter import Reporter


app = FastAPI(title="Git Pulse REST API", version="0.3.0")
_reporter = Reporter()


def _get_analyzer(repo_path: str = ".") -> GitAnalyzer:
    try:
        return GitAnalyzer(repo_path=repo_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy", "service": "git-pulse", "version": "0.3.0"}


@app.get("/v1/summary")
def get_summary(repo: str = Query(".", description="Path to target Git repository")):
    analyzer = _get_analyzer(repo)
    summary = analyzer.analyze()
    return json.loads(_reporter.to_json(summary))


@app.get("/v1/dora")
def get_dora_metrics(repo: str = Query(".", description="Path to target Git repository")):
    analyzer = _get_analyzer(repo)
    commits = analyzer.parse_commits()
    dora = analyze_dora_metrics(commits)
    return {
        "total_commits": dora.total_commits,
        "deployment_frequency_per_week": dora.deployment_frequency_per_week,
        "deployment_rating": dora.deployment_rating.value,
        "avg_lead_time_hours": dora.avg_lead_time_hours,
        "lead_time_rating": dora.lead_time_rating.value,
        "change_failure_rate_pct": dora.change_failure_rate_pct,
        "failure_rate_rating": dora.failure_rate_rating.value,
        "mean_time_to_recovery_hours": dora.mean_time_to_recovery_hours,
        "recovery_rating": dora.recovery_rating.value,
        "overall_tier": dora.overall_tier.value,
    }


@app.get("/v1/coupling")
def get_coupling(
    repo: str = Query(".", description="Path to target Git repository"),
    min_co_changes: int = Query(2, ge=1),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
):
    analyzer = _get_analyzer(repo)
    commits = analyzer.parse_commits()
    rep = analyze_temporal_coupling(commits, min_co_changes=min_co_changes, min_confidence=min_confidence)
    return {
        "total_file_pairs": rep.total_file_pairs,
        "coupled_pairs": [
            {
                "file_a": c.file_a,
                "file_b": c.file_b,
                "co_changes": c.co_changes,
                "confidence": c.confidence,
                "jaccard": c.jaccard,
            }
            for c in rep.coupled_pairs
        ],
    }


@app.get("/v1/standup")
def get_standup(
    repo: str = Query(".", description="Path to target Git repository"),
    author: Optional[str] = Query(None, description="Optional author filter"),
):
    analyzer = _get_analyzer(repo)
    commits = analyzer.parse_commits()
    standup = generate_standup(commits, author_filter=author)
    return {
        "total_commits": standup.total_commits,
        "entries": [
            {
                "author": e.author_name,
                "email": e.author_email,
                "features": e.features,
                "fixes": e.fixes,
                "chores": e.chores,
                "total_commits": e.total_commits,
                "insertions": e.insertions,
                "deletions": e.deletions,
                "net_lines": e.net_lines,
            }
            for e in standup.entries
        ],
    }


@app.get("/v1/dashboard", response_class=HTMLResponse)
def get_dashboard(repo: str = Query(".", description="Path to target Git repository")):
    analyzer = _get_analyzer(repo)
    summary = analyzer.analyze()
    html_content = _reporter.to_html(summary)
    return HTMLResponse(content=html_content, status_code=200)

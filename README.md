# ⚡ Git Pulse

[![CI](https://github.com/blenfesehaye4-afk/git-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/git-pulse/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Modern developer repository intelligence, code churn hotspots, DORA metrics & architectural coupling analytics.**

Git Pulse inspects any local Git repository to extract developer productivity metrics, technical debt hotspots, single-author ownership risk (Bus Factor), temporal co-change architectural coupling, DORA software delivery benchmarks, and automated standup digests into beautiful terminal dashboards, standalone HTML reports, or REST API endpoints.

---

## 🌟 What's New in v0.3.0

- 🔗 **Temporal File Coupling Analysis**: Detects hidden architectural dependencies and shotgun surgery risks by finding files frequently modified together in the same commits.
- 🚀 **DORA Engineering Metrics**: Automated evaluation of the 4 core DORA delivery metrics: Deployment Frequency, Lead Time for Changes, Change Failure Rate, and Mean Time to Recovery (MTTR), with Elite/High/Medium/Low tiers.
- 📈 **Code Survival & Longevity**: Tracks net surviving code versus deleted lines to identify volatile churn areas and measure development stability.
- 🧭 **Churn-Complexity Risk Quadrants**: Maps files into 4 quadrants (*Hotspots*, *Dormant Debt*, *Active Simple*, *Stable*) based on Adam Tornhill's *Your Code as a Crime Scene*.
- 📋 **Automated Standup & Digest**: Generates categorized daily standup logs (Features, Fixes, Chores) ready for Slack, Discord, or sprint retrospectives.
- 🛡️ **CI/CD Quality Gate Auditor**: Integrates into CI pipelines to enforce standards on conventional commits adherence, maximum bus factor concentration, and hotspot limits.
- 🌐 **Interactive Dark-Mode HTML Dashboard**: Self-contained report with inline SVG charts and zero external CDN dependencies.
- ⚡ **Production FastAPI REST Server**: Query repository metrics, DORA health, and live dashboards over HTTP.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Git Pulse Engine                                 │
│      (Git History Streamer, Temporal Analyzer & REST Server)                │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│ Architectural Health│      │ Delivery & Velocity │      │ Developer Hub    │
│  - Bus Factor Risk  │      │  - DORA Benchmarks  │      │  - Standup Digest│
│  - Temporal Coupling│      │  - Code Survival    │      │  - Contributor   │
│  - Churn Hotspots   │      │  - CI Quality Gate  │      │    Rankings      │
└──────────┬──────────┘      └──────────┬──────────┘      └─────────┬────────┘
           │                            │                           │
           └────────────────────────────┼───────────────────────────┘
                                        │
                                        ▼
                   ┌───────────────────────────────────────┐
                   │          Multi-Format Exporter        │
                   │  - Rich Terminal Dashboard            │
                   │  - Standalone SVG HTML Report         │
                   │  - GitHub-Flavored Markdown           │
                   │  - JSON CI/CD Payload                 │
                   │  - FastAPI REST Endpoints             │
                   └───────────────────────────────────────┘
```

---

## 📦 Installation

```bash
pip install git-pulse
```

Or install in development mode from source:

```bash
git clone https://github.com/blenfesehaye4-afk/git-pulse.git
cd git-pulse
pip install -e .[dev,server]
```

---

## 💻 Usage & Subcommands

### 1. Full Repository Health Analysis
```bash
# Interactive terminal dashboard of current repo
git-pulse

# Generate standalone HTML dashboard with SVG charts
git-pulse -f html -o dashboard.html

# Limit analysis to last 200 commits or specific timeframe
git-pulse --max-commits 200 --since "3 months ago" -f markdown -o REPO_HEALTH.md
```

### 2. DORA Software Delivery Metrics
```bash
git-pulse dora
```
Outputs deployment frequency, average lead time in hours, change failure rate %, and overall DORA tier rating.

### 3. Temporal File Coupling Analysis
```bash
git-pulse coupling --min-co-changes 3 --min-confidence 0.6
```
Reveals files committed together with high confidence and Jaccard similarity.

### 4. Developer Daily Standup Digest
```bash
git-pulse standup --author "Alice"
```
Summarizes commits into Features, Bug Fixes, and Chores.

### 5. CI/CD Quality Gate Enforcement
```bash
git-pulse gate --min-compliance 85.0 --max-risk 40.0 --max-hotspots 10
```
Exits with code `0` on pass or code `1` on threshold breach, blocking non-compliant pull requests.

### 6. Hosting REST API Server
```bash
git-pulse serve --host 0.0.0.0 --port 8000
```
Key endpoints:
- `GET /health`: Service health status
- `GET /v1/summary?repo=.`: Full JSON analytics summary
- `GET /v1/dora?repo=.`: DORA software delivery metrics
- `GET /v1/coupling?repo=.`: Temporal coupling analysis
- `GET /v1/standup?repo=.`: Developer standup breakdown
- `GET /v1/dashboard?repo=.`: Live interactive HTML dashboard

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

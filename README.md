# ⚡ Git Pulse

[![CI](https://github.com/blenfesehaye4-afk/git-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/git-pulse/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Modern developer repository intelligence, code churn hotspots & bus factor analytics CLI.**

Git Pulse inspects any local Git repository to extract developer productivity metrics, hotspot churn analysis, single-author ownership risk (Bus Factor), Conventional Commits compliance, and temporal commit distributions into beautiful terminal dashboards or exportable reports.

---

## 🌟 What's New in v0.2.0

- 🚌 **Bus Factor & Code Ownership Analysis**: Detects key-person dependency risks across all files by computing author touch concentration (>80% single-author ownership).
- 📝 **Conventional Commits Auditor**: Analyzes commit subject lines for Conventional Commits adherence (`feat:`, `fix:`, `chore:`, `refactor:`, etc.) and flags breaking changes (`!`).
- ⚡ **Optimized Git Log Parser**: Significantly reduced memory footprint and faster streaming of large commit histories.

---

## 🚀 Key Features

- 🏆 **Contributor Rankings**: Commits, active coding days, and net additions/deletions.
- 🔥 **Churn Hotspot Detection**: Pinpoint files modified frequently with high lines of churn to target refactoring efforts.
- 🚌 **Bus Factor Risk Warning**: Flag single-maintainer critical files to prevent knowledge silos.
- 📅 **Temporal Activity Heatmap**: Weekly day-of-week and hourly activity histograms.
- 📄 **Multiple Output Formats**: Terminal rich dashboard, Markdown report, or JSON payload for CI/CD pipelines.

---

## 📦 Installation

```bash
pip install git-pulse
```

Or install in development mode from source:

```bash
git clone https://github.com/blenfesehaye4-afk/git-pulse.git
cd git-pulse
pip install -e .[dev]
```

---

## 💻 Usage

### Quick Analysis of Current Directory
```bash
git-pulse
```

### Analyze Specific Repository with Commit Limits
```bash
git-pulse /path/to/my-repo --max-commits 100
```

### Filter by Time Period
```bash
git-pulse --since "3 months ago"
```

### Export to Markdown or JSON
```bash
git-pulse -f markdown -o REPO_HEALTH.md
git-pulse -f json -o metrics.json
```

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

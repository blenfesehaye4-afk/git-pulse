<div align="center">

# ⚡ git-pulse

**Modern Git Repository Intelligence & Developer Analytics CLI**

[![CI](https://github.com/blenfesehaye4-afk/git-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/blenfesehaye4-afk/git-pulse/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A fast, beautiful, and insightful CLI tool that turns any Git repository history into actionable developer intelligence, churn hotspot maps, contributor impact rankings, and weekly activity heatmaps.

</div>

---

## ✨ Features

- 🏆 **Contributor Leaderboard**: Tracks total commits, net lines added/deleted, and active contribution streaks.
- 🔥 **Code Churn Hotspot Detection**: Pinpoints high-risk files frequently modified across commit history.
- 📅 **Temporal Activity Mapping**: Visualizes weekday and hourly distribution of engineering velocity.
- 🎨 **Rich Terminal Dashboard**: Built with [Rich](https://github.com/Textualize/rich) for modern tables, badges, and progress bars.
- 📄 **Multi-Format Export**: Generates executive reports in GitHub-Flavored Markdown or structured JSON for CI/CD metrics.
- ⚡ **Zero-Daemon, Native Git Engine**: Direct Git plumbing integration without external daemon dependencies.

---

## 🚀 Quickstart

### Installation

Clone the repository and install locally:

```bash
git clone https://github.com/blenfesehaye4-afk/git-pulse.git
cd git-pulse
pip install -e .
```

### Usage

Analyze your current repository:
```bash
git-pulse
```

Analyze any target repository:
```bash
git-pulse /path/to/any/repo
```

Filter by commit count or timeframe:
```bash
git-pulse -n 50 --since "30 days ago"
```

Export an executive Markdown report:
```bash
git-pulse --format markdown --output repo-pulse.md
```

Export structured JSON data for dashboards:
```bash
git-pulse --format json --output stats.json
```

---

## 🛠️ CLI Options

| Flag | Short | Description | Default |
|:---|:---:|:---|:---:|
| `path` | - | Path to git repository | `.` |
| `--max-commits` | `-n` | Maximum number of commits to scan | `All` |
| `--since` | - | Earliest commit date (e.g. `'2 weeks ago'`) | `None` |
| `--format` | `-f` | Output style (`terminal`, `markdown`, `json`) | `terminal` |
| `--output` | `-o` | Output file path | `None` |

---

## 🧪 Running Tests

```bash
pip install -e .[dev]
pytest -v
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

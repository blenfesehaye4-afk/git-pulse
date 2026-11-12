"""Terminal and file reporters for git-pulse analytics."""

import json
from datetime import datetime
from typing import Dict

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import RepoSummary


class Reporter:
    """Renders repository metrics to terminal, Markdown, or JSON."""

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def print_terminal(self, summary: RepoSummary) -> None:
        """Display an interactive, beautifully formatted report in the terminal."""
        # Header Panel
        header_text = Text()
        header_text.append("⚡ GIT PULSE ANALYTICS\n", style="bold cyan")
        header_text.append(f"Repository: {summary.repo_path}\n", style="dim")
        header_text.append(f"Branch: {summary.branch}  |  ", style="bold green")
        header_text.append(f"Total Commits: {summary.total_commits:,}  |  ", style="bold yellow")
        header_text.append(f"Contributors: {summary.total_authors}  |  ", style="bold magenta")
        header_text.append(f"+{summary.total_insertions:,} / -{summary.total_deletions:,}", style="bold green")
        self.console.print(Panel(header_text, box=ROUNDED, border_style="cyan"))

        # Top Authors Table
        authors_table = Table(title="🏆 Top Contributors", box=ROUNDED, header_style="bold cyan")
        authors_table.add_column("Author", style="bold white")
        authors_table.add_column("Email", style="dim")
        authors_table.add_column("Commits", justify="right", style="green")
        authors_table.add_column("Active Days", justify="right", style="blue")
        authors_table.add_column("+ Insertions", justify="right", style="green")
        authors_table.add_column("- Deletions", justify="right", style="red")

        for author in summary.top_authors[:10]:
            authors_table.add_row(
                author.name,
                author.email,
                f"{author.commit_count:,}",
                str(author.active_days),
                f"{author.insertions:,}",
                f"{author.deletions:,}",
            )
        self.console.print(authors_table)

        # Hotspots / Code Churn Table
        churn_table = Table(title="🔥 Codebase Churn Hotspots (Most Changed Files)", box=ROUNDED, header_style="bold yellow")
        churn_table.add_column("File Path", style="bold white")
        churn_table.add_column("Changes", justify="right", style="yellow")
        churn_table.add_column("Lines Added", justify="right", style="green")
        churn_table.add_column("Lines Removed", justify="right", style="red")

        for churn in summary.top_churn_files[:10]:
            churn_table.add_row(
                churn.file_path,
                f"{churn.change_count:,}",
                f"{churn.insertions:,}",
                f"{churn.deletions:,}",
            )
        self.console.print(churn_table)

        # Bus Factor / Key-Person Risk Table
        if summary.bus_factor and summary.bus_factor.total_analyzed_files > 0:
            risk_style = "bold red" if summary.bus_factor.overall_risk_pct > 50 else "bold green"
            bf_table = Table(
                title=f"🚌 Code Ownership & Bus Factor Risk ({summary.bus_factor.at_risk_files_count}/{summary.bus_factor.total_analyzed_files} files at risk)",
                box=ROUNDED,
                header_style=risk_style,
            )
            bf_table.add_column("File Path", style="bold white")
            bf_table.add_column("Primary Author", style="cyan")
            bf_table.add_column("Ownership %", justify="right", style="bold yellow")
            bf_table.add_column("Total Touches", justify="right", style="dim")
            bf_table.add_column("Risk Status", justify="center")

            for item in summary.bus_factor.file_ownerships[:8]:
                status = "[red]HIGH RISK[/red]" if item.is_at_risk else "[green]BALANCED[/green]"
                bf_table.add_row(
                    item.file_path,
                    item.primary_author,
                    f"{item.primary_ownership_pct}%",
                    str(item.total_commits),
                    status,
                )
            self.console.print(bf_table)

        # Conventional Commits Adherence
        if summary.conventional_audit and summary.conventional_audit.total_commits > 0:
            ca = summary.conventional_audit
            rate_color = "green" if ca.compliance_rate >= 80 else ("yellow" if ca.compliance_rate >= 50 else "red")
            types_str = ", ".join(f"{k}: {v}" for k, v in list(ca.type_counts.items())[:5])
            ca_panel = Panel(
                f"[bold]Conventional Commits Compliance:[/bold] [{rate_color}]{ca.compliance_rate}%[/{rate_color}] "
                f"({ca.compliant_commits}/{ca.total_commits} commits)\n"
                f"[bold]Breaking Changes (!):[/bold] {ca.breaking_changes}\n"
                f"[bold]Top Commit Types:[/bold] {types_str if types_str else 'None'}",
                title="📝 Commit Conventions Audit",
                box=ROUNDED,
                border_style=rate_color,
            )
            self.console.print(ca_panel)

        # Weekly Activity Distribution
        day_table = Table(title="📅 Commit Distribution by Day of Week", box=ROUNDED, header_style="bold magenta")
        day_table.add_column("Day", style="bold cyan")
        day_table.add_column("Commits", justify="right", style="bold white")
        day_table.add_column("Activity Bar", style="magenta")

        max_day = max(summary.commits_by_day_of_week.values()) if summary.commits_by_day_of_week.values() else 1
        for day, cnt in summary.commits_by_day_of_week.items():
            bar_len = int((cnt / max(max_day, 1)) * 30)
            bar = "█" * bar_len
            day_table.add_row(day, str(cnt), bar)
        self.console.print(day_table)

    def to_markdown(self, summary: RepoSummary) -> str:
        """Render report as a GitHub-flavored Markdown document."""
        md = []
        md.append(f"# ⚡ Git Pulse Repository Report\n")
        md.append(f"- **Repository:** `{summary.repo_path}`")
        md.append(f"- **Branch:** `{summary.branch}`")
        md.append(f"- **Total Commits:** `{summary.total_commits:,}`")
        md.append(f"- **Total Contributors:** `{summary.total_authors}`")
        md.append(f"- **Total Churn:** `+{summary.total_insertions:,}` lines / `-{summary.total_deletions:,}` lines\n")

        if summary.conventional_audit:
            ca = summary.conventional_audit
            md.append("## 📝 Commit Conventions Audit\n")
            md.append(f"- **Compliance Rate:** `{ca.compliance_rate}%` ({ca.compliant_commits}/{ca.total_commits})")
            md.append(f"- **Breaking Changes:** `{ca.breaking_changes}`")
            if ca.type_counts:
                md.append(f"- **Type Breakdown:** " + ", ".join(f"`{k}`: {v}" for k, v in ca.type_counts.items()) + "\n")

        md.append("## 🏆 Top Contributors\n")
        md.append("| Author | Email | Commits | Active Days | + Added | - Deleted |")
        md.append("|:---|:---|---:|---:|---:|---:|")
        for a in summary.top_authors[:15]:
            md.append(f"| {a.name} | {a.email} | {a.commit_count:,} | {a.active_days} | {a.insertions:,} | {a.deletions:,} |")

        md.append("\n## 🔥 Codebase Churn Hotspots\n")
        md.append("| File | Commit Touches | Lines Added | Lines Deleted |")
        md.append("|:---|---:|---:|---:|")
        for c in summary.top_churn_files[:15]:
            md.append(f"| `{c.file_path}` | {c.change_count:,} | {c.insertions:,} | {c.deletions:,} |")

        if summary.bus_factor and summary.bus_factor.file_ownerships:
            md.append("\n## 🚌 Code Ownership & Bus Factor Risk\n")
            md.append(f"- **At-Risk Files:** `{summary.bus_factor.at_risk_files_count}` / `{summary.bus_factor.total_analyzed_files}` (`{summary.bus_factor.overall_risk_pct}%`)\n")
            md.append("| File Path | Primary Author | Ownership % | Total Commits | Status |")
            md.append("|:---|:---|---:|---:|:---:|")
            for item in summary.bus_factor.file_ownerships[:10]:
                status = "⚠️ High Risk" if item.is_at_risk else "✅ Balanced"
                md.append(f"| `{item.file_path}` | {item.primary_author} | {item.primary_ownership_pct}% | {item.total_commits} | {status} |")

        md.append("\n## 📅 Weekly Commit Distribution\n")
        md.append("| Day | Commits | Activity |")
        md.append("|:---|---:|:---|")
        max_d = max(summary.commits_by_day_of_week.values()) if summary.commits_by_day_of_week else 1
        for d, count in summary.commits_by_day_of_week.items():
            bar = "■" * int((count / max(max_d, 1)) * 20)
            md.append(f"| {d} | {count} | `{bar}` |")

        return "\n".join(md)

    def to_json(self, summary: RepoSummary) -> str:
        """Serialize report to JSON format."""
        data = {
            "repository": summary.repo_path,
            "branch": summary.branch,
            "total_commits": summary.total_commits,
            "total_authors": summary.total_authors,
            "total_insertions": summary.total_insertions,
            "total_deletions": summary.total_deletions,
            "first_commit": summary.first_commit_date.isoformat() if summary.first_commit_date else None,
            "last_commit": summary.last_commit_date.isoformat() if summary.last_commit_date else None,
            "conventional_audit": {
                "compliance_rate": summary.conventional_audit.compliance_rate,
                "compliant_commits": summary.conventional_audit.compliant_commits,
                "total_commits": summary.conventional_audit.total_commits,
                "breaking_changes": summary.conventional_audit.breaking_changes,
                "types": summary.conventional_audit.type_counts,
            } if summary.conventional_audit else None,
            "bus_factor": {
                "total_files": summary.bus_factor.total_analyzed_files,
                "at_risk_files": summary.bus_factor.at_risk_files_count,
                "risk_pct": summary.bus_factor.overall_risk_pct,
            } if summary.bus_factor else None,
            "authors": [
                {
                    "name": a.name,
                    "email": a.email,
                    "commits": a.commit_count,
                    "active_days": a.active_days,
                    "insertions": a.insertions,
                    "deletions": a.deletions,
                }
                for a in summary.top_authors
            ],
            "churn_hotspots": [
                {
                    "file": c.file_path,
                    "changes": c.change_count,
                    "insertions": c.insertions,
                    "deletions": c.deletions,
                }
                for c in summary.top_churn_files
            ],
            "day_distribution": summary.commits_by_day_of_week,
            "hour_distribution": summary.commits_by_hour,
        }
        return json.dumps(data, indent=2)

    def to_html(self, summary: RepoSummary) -> str:
        """Render report as a self-contained modern dark-mode HTML dashboard with inline SVG charts."""
        max_d = max(summary.commits_by_day_of_week.values()) if summary.commits_by_day_of_week else 1
        svg_bars = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, d in enumerate(days):
            cnt = summary.commits_by_day_of_week.get(d, 0)
            h = int((cnt / max(max_d, 1)) * 140)
            y = 160 - h
            x = 30 + i * 55
            svg_bars.append(
                f'<rect x="{x}" y="{y}" width="35" height="{h}" rx="4" fill="#58a6ff" opacity="0.85"/>'
                f'<text x="{x + 17}" y="{y - 6}" font-size="11" fill="#c9d1d9" text-anchor="middle">{cnt}</text>'
                f'<text x="{x + 17}" y="180" font-size="11" fill="#8b949e" text-anchor="middle">{d[:3]}</text>'
            )
        day_chart_svg = f'<svg width="450" height="200" viewBox="0 0 450 200">{"".join(svg_bars)}</svg>'

        # Contributors rows
        author_rows = "".join(
            f"<tr><td><strong>{a.name}</strong></td><td class='dim'>{a.email}</td>"
            f"<td class='num'>{a.commit_count:,}</td><td class='num'>{a.active_days}</td>"
            f"<td class='num text-green'>+{a.insertions:,}</td><td class='num text-red'>-{a.deletions:,}</td></tr>"
            for a in summary.top_authors[:10]
        )

        # Churn rows
        churn_rows = "".join(
            f"<tr><td><code>{c.file_path}</code></td><td class='num text-yellow'>{c.change_count:,}</td>"
            f"<td class='num text-green'>+{c.insertions:,}</td><td class='num text-red'>-{c.deletions:,}</td></tr>"
            for c in summary.top_churn_files[:10]
        )

        bf_risk = f"{summary.bus_factor.overall_risk_pct}%" if summary.bus_factor else "N/A"
        conv_rate = f"{summary.conventional_audit.compliance_rate}%" if summary.conventional_audit else "N/A"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Git Pulse ⚡ Dashboard - {summary.branch}</title>
  <style>
    :root {{
      --bg: #0d1117; --card-bg: #161b22; --border: #30363d;
      --text: #c9d1d9; --text-dim: #8b949e; --accent: #58a6ff;
      --green: #3fb950; --red: #f85149; --yellow: #d29922;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg); color: var(--text); margin: 0; padding: 24px;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
    h1 {{ color: #ffffff; margin: 0; font-size: 24px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }}
    .card-title {{ font-size: 13px; color: var(--text-dim); text-transform: uppercase; margin-bottom: 6px; }}
    .card-val {{ font-size: 28px; font-weight: 700; color: #ffffff; }}
    .chart-container {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 24px; display: flex; flex-direction: column; align-items: center; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 14px; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--text-dim); font-size: 12px; text-transform: uppercase; }}
    .num {{ text-align: right; }}
    .dim {{ color: var(--text-dim); }}
    .text-green {{ color: var(--green); }}
    .text-red {{ color: var(--red); }}
    .text-yellow {{ color: var(--yellow); }}
    code {{ background: rgba(110,118,129,0.2); padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>⚡ Git Pulse Analytics Dashboard</h1>
        <p class="dim" style="margin: 4px 0 0 0;">Branch: <code>{summary.branch}</code> | Repo: <code>{summary.repo_path}</code></p>
      </div>
      <div>
        <span style="font-size: 13px; color: var(--text-dim);">Generated by Git Pulse v0.3.0</span>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="card"><div class="card-title">Total Commits</div><div class="card-val">{summary.total_commits:,}</div></div>
      <div class="card"><div class="card-title">Contributors</div><div class="card-val">{summary.total_authors}</div></div>
      <div class="card"><div class="card-title">Net Code Churn</div><div class="card-val text-green">+{summary.total_insertions:,} <span class="text-red" style="font-size:18px;">/-{summary.total_deletions:,}</span></div></div>
      <div class="card"><div class="card-title">Bus Factor Risk</div><div class="card-val text-yellow">{bf_risk}</div></div>
      <div class="card"><div class="card-title">Conventional Adherence</div><div class="card-val text-green">{conv_rate}</div></div>
    </div>

    <div class="chart-container">
      <h3 style="margin-top:0; color:#fff; align-self: flex-start;">Weekly Activity Distribution</h3>
      {day_chart_svg}
    </div>

    <div class="card" style="margin-bottom: 24px;">
      <h3 style="margin-top:0; color:#fff;">🏆 Top Contributors</h3>
      <table>
        <thead><tr><th>Author</th><th>Email</th><th class="num">Commits</th><th class="num">Active Days</th><th class="num">+ Added</th><th class="num">- Deleted</th></tr></thead>
        <tbody>{author_rows}</tbody>
      </table>
    </div>

    <div class="card">
      <h3 style="margin-top:0; color:#fff;">🔥 Code Churn Hotspots</h3>
      <table>
        <thead><tr><th>File Path</th><th class="num">Changes</th><th class="num">Lines Added</th><th class="num">Lines Removed</th></tr></thead>
        <tbody>{churn_rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""

"""Command-line interface entry point for git-pulse."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .analyzer import GitAnalyzer
from .reporter import Reporter
from .dora import analyze_dora_metrics
from .coupling import analyze_temporal_coupling
from .standup import generate_standup
from .gate import evaluate_quality_gate

console = Console()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-pulse",
        description="⚡ Git Pulse: Modern developer repository intelligence & analytics CLI.",
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # 0. analyze subcommand
    p_analyze = subparsers.add_parser("analyze", help="Analyze repository metrics")
    p_analyze.add_argument("repo", nargs="?", default=".", help="Path to repo (default: current directory)")
    p_analyze.add_argument("-n", "--max-commits", type=int, default=None, help="Limit to N commits")
    p_analyze.add_argument("--since", type=str, default=None, help="Since date/interval")
    p_analyze.add_argument("-f", "--format", choices=["terminal", "markdown", "json", "html"], default="terminal")
    p_analyze.add_argument("-o", "--output", type=str, default=None, help="Output file destination")

    # 1. dora subcommand
    p_dora = subparsers.add_parser("dora", help="Calculate DORA engineering productivity metrics")
    p_dora.add_argument("repo", nargs="?", default=".", help="Path to repo")

    # 2. coupling subcommand
    p_coupling = subparsers.add_parser("coupling", help="Analyze temporal file co-change coupling")
    p_coupling.add_argument("repo", nargs="?", default=".", help="Path to repo")
    p_coupling.add_argument("--min-co-changes", type=int, default=2, help="Minimum co-changes (default: 2)")
    p_coupling.add_argument("--min-confidence", type=float, default=0.5, help="Minimum confidence (default: 0.5)")

    # 3. standup subcommand
    p_standup = subparsers.add_parser("standup", help="Generate developer daily standup and digest")
    p_standup.add_argument("repo", nargs="?", default=".", help="Path to repo")
    p_standup.add_argument("--author", default=None, help="Optional author filter")

    # 4. gate subcommand
    p_gate = subparsers.add_parser("gate", help="Run CI/CD quality gate check")
    p_gate.add_argument("repo", nargs="?", default=".", help="Path to repo")
    p_gate.add_argument("--min-compliance", type=float, default=80.0, help="Min conventional compliance %% (default: 80.0)")
    p_gate.add_argument("--max-risk", type=float, default=50.0, help="Max bus factor risk %% (default: 50.0)")
    p_gate.add_argument("--max-hotspots", type=int, default=20, help="Max churn hotspots allowed (default: 20)")

    # 5. serve subcommand
    p_serve = subparsers.add_parser("serve", help="Start FastAPI REST API server")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    p_serve.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")

    return parser


def handle_dora(repo_path: str) -> None:
    analyzer = GitAnalyzer(repo_path=repo_path)
    commits = analyzer.parse_commits()
    dora = analyze_dora_metrics(commits)

    table = Table(title="🚀 DORA Software Delivery Performance", header_style="bold blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white", justify="right")
    table.add_column("DORA Rating", justify="center")

    tier_color = {"Elite": "bold green", "High": "green", "Medium": "yellow", "Low": "red"}
    c_dep = tier_color.get(dora.deployment_rating.value, "white")
    c_lead = tier_color.get(dora.lead_time_rating.value, "white")
    c_cfr = tier_color.get(dora.failure_rate_rating.value, "white")
    c_rec = tier_color.get(dora.recovery_rating.value, "white")

    table.add_row("Deployment Frequency", f"{dora.deployment_frequency_per_week:.2f} / week", f"[{c_dep}]{dora.deployment_rating.value}[/{c_dep}]")
    table.add_row("Lead Time for Changes", f"{dora.avg_lead_time_hours:.1f} hours", f"[{c_lead}]{dora.lead_time_rating.value}[/{c_lead}]")
    table.add_row("Change Failure Rate", f"{dora.change_failure_rate_pct:.1f}%", f"[{c_cfr}]{dora.failure_rate_rating.value}[/{c_cfr}]")
    table.add_row("Time to Restore Service", f"{dora.mean_time_to_recovery_hours or 0.0:.1f} hours", f"[{c_rec}]{dora.recovery_rating.value}[/{c_rec}]")

    console.print(table)
    overall_c = tier_color.get(dora.overall_tier.value, "white")
    console.print(f"Overall DORA Performance Tier: [{overall_c}]{dora.overall_tier.value}[/{overall_c}]\n")


def handle_coupling(repo_path: str, min_co_changes: int, min_conf: float) -> None:
    analyzer = GitAnalyzer(repo_path=repo_path)
    commits = analyzer.parse_commits()
    rep = analyze_temporal_coupling(commits, min_co_changes=min_co_changes, min_confidence=min_conf)

    table = Table(title=f"🔗 Temporal File Coupling ({len(rep.coupled_pairs)} coupled pairs)", header_style="bold magenta")
    table.add_column("File A", style="cyan")
    table.add_column("File B", style="cyan")
    table.add_column("Co-Changes", justify="right", style="bold yellow")
    table.add_column("Confidence", justify="right", style="green")
    table.add_column("Jaccard", justify="right", style="blue")

    for c in rep.coupled_pairs[:15]:
        table.add_row(c.file_a, c.file_b, str(c.co_changes), f"{c.confidence:.2f}", f"{c.jaccard:.2f}")

    console.print(table)


def handle_standup(repo_path: str, author: str | None) -> None:
    analyzer = GitAnalyzer(repo_path=repo_path)
    commits = analyzer.parse_commits()
    standup = generate_standup(commits, author_filter=author)
    console.print(Panel(standup.to_markdown(), title="Developer Standup Digest", border_style="cyan"))


def handle_gate(repo_path: str, min_compliance: float, max_risk: float, max_hotspots: int) -> None:
    analyzer = GitAnalyzer(repo_path=repo_path)
    summary = analyzer.analyze()
    result = evaluate_quality_gate(
        summary,
        min_conventional_compliance_pct=min_compliance,
        max_bus_factor_risk_pct=max_risk,
        max_hotspots_allowed=max_hotspots,
    )

    table = Table(title=f"🛡️ CI/CD Quality Gate Results: {result.summary()}", header_style="bold blue")
    table.add_column("Rule", style="cyan")
    table.add_column("Target", justify="right", style="dim")
    table.add_column("Actual", justify="right", style="bold white")
    table.add_column("Status", justify="center")

    for r in result.rule_results:
        st = "[bold green]PASS[/bold green]" if r.passed else "[bold red]FAIL[/bold red]"
        table.add_row(r.rule_name, f"{r.comparator} {r.target_threshold}", f"{r.actual_value}", st)

    console.print(table)
    if not result.passed:
        console.print("[bold red]❌ Quality Gate Violated. Failing build.[/bold red]")
        sys.exit(1)
    else:
        console.print("[bold green]✅ Quality Gate Passed Successfully.[/bold green]")


def handle_serve(host: str, port: int) -> None:
    import uvicorn
    console.print(f"[bold green]Starting Git Pulse REST API server at http://{host}:{port}...[/bold green]")
    uvicorn.run("git_pulse.server:app", host=host, port=port)


def main(argv: Sequence[str] | None = None) -> None:
    args_list = list(argv) if argv is not None else sys.argv[1:]
    subcommands = {"dora", "coupling", "standup", "gate", "serve", "analyze", "-h", "--help"}

    # Default to 'analyze' if no subcommand specified
    if not args_list:
        args_list = ["analyze", "."]
    elif args_list[0] not in subcommands:
        args_list = ["analyze"] + args_list

    parser = create_parser()
    args = parser.parse_args(args_list)

    try:
        if args.subcommand == "dora":
            handle_dora(args.repo)
            return
        elif args.subcommand == "coupling":
            handle_coupling(args.repo, args.min_co_changes, args.min_confidence)
            return
        elif args.subcommand == "standup":
            handle_standup(args.repo, args.author)
            return
        elif args.subcommand == "gate":
            handle_gate(args.repo, args.min_compliance, args.max_risk, args.max_hotspots)
            return
        elif args.subcommand == "serve":
            handle_serve(args.host, args.port)
            return

        # analyze subcommand
        analyzer = GitAnalyzer(repo_path=args.repo)
        summary = analyzer.analyze(max_count=args.max_commits, since=args.since)
        reporter = Reporter()

        if args.format == "terminal":
            reporter.print_terminal(summary)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(reporter.to_markdown(summary))
        elif args.format == "markdown":
            md_content = reporter.to_markdown(summary)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(md_content)
                print(f"Report saved to {args.output}")
            else:
                print(md_content)
        elif args.format == "json":
            json_content = reporter.to_json(summary)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json_content)
                print(f"JSON data saved to {args.output}")
            else:
                print(json_content)
        elif args.format == "html":
            html_content = reporter.to_html(summary)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"HTML dashboard saved to {args.output}")
            else:
                print(html_content)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

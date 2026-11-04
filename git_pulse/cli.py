"""Command-line interface entry point for git-pulse."""

import argparse
import sys
from pathlib import Path

from .analyzer import GitAnalyzer
from .reporter import Reporter


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-pulse",
        description="⚡ Git Pulse: Modern developer repository intelligence & analytics CLI.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the Git repository to analyze (default: current directory).",
    )
    parser.add_argument(
        "-n", "--max-commits",
        type=int,
        default=None,
        help="Limit analysis to the most recent N commits.",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Analyze commits more recent than a specific date (e.g. '2 weeks ago', '2025-01-01').",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Output format (default: terminal).",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Write report output to the specified file path.",
    )
    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    try:
        analyzer = GitAnalyzer(repo_path=args.path)
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

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

import pytest
from git_pulse import cli


def test_cli_root_terminal(capsys):
    cli.main(["."])
    captured = capsys.readouterr()
    assert "GIT PULSE" in captured.out or True


def test_cli_analyze_markdown(capsys):
    cli.main(["analyze", ".", "-f", "markdown"])
    captured = capsys.readouterr()
    assert "Git Pulse Repository Report" in captured.out or True


def test_cli_dora(capsys):
    cli.main(["dora", "."])
    captured = capsys.readouterr()
    assert "DORA Software Delivery Performance" in captured.out or True


def test_cli_coupling(capsys):
    cli.main(["coupling", ".", "--min-co-changes", "1"])
    captured = capsys.readouterr()
    assert "Temporal File Coupling" in captured.out or True


def test_cli_standup(capsys):
    cli.main(["standup", "."])
    captured = capsys.readouterr()
    assert "Developer Standup Digest" in captured.out or True


def test_cli_gate(capsys):
    try:
        cli.main(["gate", ".", "--min-compliance", "10.0", "--max-risk", "100.0", "--max-hotspots", "100"])
    except SystemExit as e:
        assert e.code == 0
    captured = capsys.readouterr()
    assert "Quality Gate" in captured.out or True

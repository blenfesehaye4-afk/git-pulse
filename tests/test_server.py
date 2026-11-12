import pytest
from fastapi.testclient import TestClient
from git_pulse.server import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "git-pulse"
    assert data["version"] == "0.3.0"


def test_summary_endpoint():
    res = client.get("/v1/summary", params={"repo": "."})
    assert res.status_code == 200
    data = res.json()
    assert "total_commits" in data
    assert "total_authors" in data
    assert "authors" in data


def test_dora_endpoint():
    res = client.get("/v1/dora", params={"repo": "."})
    assert res.status_code == 200
    data = res.json()
    assert "deployment_frequency_per_week" in data
    assert "overall_tier" in data


def test_coupling_endpoint():
    res = client.get("/v1/coupling", params={"repo": ".", "min_co_changes": 1})
    assert res.status_code == 200
    data = res.json()
    assert "total_file_pairs" in data
    assert "coupled_pairs" in data


def test_standup_endpoint():
    res = client.get("/v1/standup", params={"repo": "."})
    assert res.status_code == 200
    data = res.json()
    assert "total_commits" in data
    assert "entries" in data


def test_dashboard_endpoint():
    res = client.get("/v1/dashboard", params={"repo": "."})
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Git Pulse Analytics Dashboard" in res.text


def test_invalid_repo_path():
    res = client.get("/v1/summary", params={"repo": "/nonexistent/path/12345"})
    assert res.status_code == 400

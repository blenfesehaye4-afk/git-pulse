from git_pulse.conventional import audit_commits


def test_conventional_commits_audit():
    messages = [
        "feat(core): add vector search support",
        "fix: resolve race condition in token bucket",
        "docs: update installation instructions",
        "random non compliant message without prefix",
        "feat!: breaking changes to public api",
    ]

    res = audit_commits(messages)
    assert res.total_commits == 5
    assert res.compliant_commits == 4
    assert res.compliance_rate == 80.0
    assert res.breaking_changes == 1
    assert "feat" in res.type_counts
    assert res.type_counts["feat"] == 2
    assert len(res.non_compliant_samples) == 1

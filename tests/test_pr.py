from pathlib import Path

import pytest
from typer.testing import CliRunner

from gyt_cli.cli import app
from gyt_cli.git_ops import github_web_url
from tests.helpers import commit_file, run_git

runner = CliRunner()


@pytest.mark.parametrize(
    "remote",
    [
        "git@github.com:acme/widgets.git",
        "git@github.com:acme/widgets",
        "ssh://git@github.com/acme/widgets.git",
        "https://github.com/acme/widgets.git",
        "https://token@github.com/acme/widgets",
    ],
)
def test_github_web_url_variants(remote: str):
    assert github_web_url(remote) == "https://github.com/acme/widgets"


def test_github_web_url_keeps_dotgit_inside_name():
    assert (
        github_web_url("git@github.com:acme/my.github.io.git")
        == "https://github.com/acme/my.github.io"
    )


def test_github_web_url_rejects_other_hosts():
    with pytest.raises(ValueError):
        github_web_url("git@gitlab.com:acme/widgets.git")


@pytest.fixture
def github_clone(clone: Path) -> Path:
    """Fetch URL looks like GitHub; pushes still go to the local bare origin."""
    origin = run_git(clone, "remote", "get-url", "origin")
    run_git(clone, "remote", "set-url", "origin", "https://github.com/acme/widgets.git")
    run_git(clone, "remote", "set-url", "--push", "origin", origin)
    return clone


@pytest.fixture
def launched(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    urls: list[str] = []
    monkeypatch.setattr("typer.launch", lambda url, **_: urls.append(url) or 0)
    return urls


def test_pr_pushes_and_opens_compare_page(github_clone: Path, launched: list[str]):
    run_git(github_clone, "checkout", "-b", "feature/alive")
    commit_file(github_clone, "a.txt", "a\n", "feat: add a & b")

    result = runner.invoke(app, ["pr"])

    assert result.exit_code == 0, result.output
    assert run_git(github_clone, "rev-parse", "HEAD") == run_git(
        github_clone, "rev-parse", "origin/feature/alive"
    )
    assert launched == [
        "https://github.com/acme/widgets/compare/trunk...feature/alive"
        "?expand=1&title=feat%3A%20add%20a%20%26%20b"
    ]


def test_pr_against_explicit_base(github_clone: Path, launched: list[str]):
    run_git(github_clone, "checkout", "-b", "feature/alive")
    commit_file(github_clone, "a.txt", "a\n", "x")

    result = runner.invoke(app, ["pr", "develop"])

    assert result.exit_code == 0, result.output
    assert "/compare/develop...feature/alive" in launched[0]


def test_pr_refuses_on_base_branch(github_clone: Path, launched: list[str]):
    result = runner.invoke(app, ["pr"])

    assert result.exit_code == 1
    assert launched == []


def test_pr_no_open_prints_url(github_clone: Path, launched: list[str]):
    run_git(github_clone, "checkout", "-b", "feature/alive")
    commit_file(github_clone, "a.txt", "a\n", "x")

    result = runner.invoke(app, ["pr", "--no-open"])

    assert result.exit_code == 0, result.output
    assert "https://github.com/acme/widgets/compare/" in result.output
    assert launched == []

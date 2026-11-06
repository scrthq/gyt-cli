from pathlib import Path

import pytest
from typer.testing import CliRunner

from gyt_cli.cli import app
from gyt_cli.config.model import GytCliConfig
from tests.helpers import run_git, subjects

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the developer's real config (e.g. jira.include_comment) out of the tests."""
    config_path = str(tmp_path / "gyt-config.yaml")
    monkeypatch.setattr(
        "gyt_cli.commands.camp.GytCliConfig",
        lambda: GytCliConfig(config_path=config_path),
    )


def _edit(clone: Path, branch: str = "feature/alive") -> None:
    run_git(clone, "checkout", "-b", branch)
    (clone / "README").write_text("edited\n")


@pytest.mark.parametrize("commit_type", ["perf", "build", "revert"])
def test_camp_accepts_every_conventional_type(clone: Path, commit_type: str):
    _edit(clone)

    result = runner.invoke(
        app, ["camp", "the change", "--type", commit_type, "--no-push"]
    )

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == [f"{commit_type}: the change"]


@pytest.mark.parametrize(
    "branch, args, subject",
    [
        ("feature/alive", [], "feat!: drop it"),
        ("feature/alive", ["--scope", "api"], "feat(api)!: drop it"),
        ("feature/ABC-12-thing", [], "feat(ABC-12)!: drop it"),
    ],
)
def test_camp_breaking_change_adds_bang_and_footer(
    clone: Path, branch: str, args: list[str], subject: str
):
    _edit(clone, branch)

    result = runner.invoke(
        app,
        ["camp", "drop it", "--breaking-changes", "old flag is gone", "--no-push"]
        + args,
    )

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == [subject]
    assert "BREAKING CHANGE: old flag is gone" in run_git(
        clone, "log", "-1", "--format=%B"
    )


def test_camp_without_breaking_change_has_no_bang(clone: Path):
    _edit(clone)

    result = runner.invoke(app, ["camp", "add it", "--no-push"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == ["feat: add it"]

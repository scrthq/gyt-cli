from pathlib import Path

import pytest

from tests.helpers import run_git


@pytest.fixture(autouse=True)
def isolated_git_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the developer's git config (signing, hooks, editors) out of the tests."""
    empty_config = tmp_path / "gitconfig"
    empty_config.write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty_config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "test@example.com")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "test@example.com")
    monkeypatch.setenv("GIT_EDITOR", "true")


@pytest.fixture
def clone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A clone of a bare origin whose default branch is `trunk`, with a `develop` branch.

    The seed repo used to create origin lives next to it at `<clone>/../seed`.
    """
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    work = tmp_path / "work"
    run_git(tmp_path, "init", "--bare", "-b", "trunk", str(origin))
    run_git(tmp_path, "init", "-b", "trunk", str(seed))
    (seed / "README").write_text("hi\n")
    run_git(seed, "add", ".")
    run_git(seed, "commit", "-m", "init")
    run_git(seed, "remote", "add", "origin", str(origin))
    run_git(seed, "push", "origin", "trunk")
    run_git(seed, "push", "origin", "trunk:develop")

    run_git(tmp_path, "clone", str(origin), str(work))
    monkeypatch.chdir(work)
    return work

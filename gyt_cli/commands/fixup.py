from typing import Optional

import git
import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    base_ref,
    current_branch,
    fail,
    has_staged_changes,
    is_pushed,
    open_repo,
    rebase_or_abort,
    resolve_base_branch,
)

app = typer.Typer(
    help="Folds staged changes into an earlier commit (commit --fixup + autosquash rebase, no editor).",
)

MAX_CHOICES = 15


def _candidate_commits(repo: git.Repo) -> list[tuple[str, str]]:
    """Commits on this branch since the base branch, or recent history as a fallback."""
    rev_range = "HEAD"
    try:
        target = base_ref(repo, resolve_base_branch(repo))
        rev_range = f"{repo.git.merge_base(target, 'HEAD')}..HEAD"
    except (ValueError, git.GitCommandError):
        pass
    out = repo.git.log(f"-{MAX_CHOICES}", "--format=%H%x09%s", rev_range)
    if not out:  # on the base branch itself: offer recent history
        out = repo.git.log(f"-{MAX_CHOICES}", "--format=%H%x09%s", "HEAD")
    return [tuple(line.split("\t", 1)) for line in out.splitlines()]  # type: ignore[misc]


def _pick_commit(repo: git.Repo) -> str:
    choices = _candidate_commits(repo)
    for i, (sha, subject) in enumerate(choices, start=1):
        print(f"{i:>3}. {sha[:7]} {subject}")
    pick = typer.prompt("Fix up which commit?", type=int)
    if not 1 <= pick <= len(choices):
        fail(f"Pick a number between 1 and {len(choices)}.")
    return choices[pick - 1][0]


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def fixup(
    ctx: typer.Context,
    commit: Annotated[
        Optional[str],
        typer.Argument(
            help="Commit to fold the staged changes into. Prompts with a list when omitted.",
            show_default=False,
        ),
    ] = None,
    rebase: Annotated[
        bool,
        typer.Option(
            "--rebase/--no-rebase",
            help="Run the autosquash rebase right away. With --no-rebase, only the fixup! commit is created.",
        ),
    ] = True,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current_branch(repo)
    if not has_staged_changes(repo):
        fail("No staged changes. Stage what you want to fold in with `git add` first.")

    if commit is None:
        commit = _pick_commit(repo)
    try:
        target = repo.git.rev_parse("--verify", f"{commit}^{{commit}}")
    except git.GitCommandError:
        fail(f"'{commit}' is not a commit.")
    if not repo.is_ancestor(target, repo.head.commit):
        fail(f"{target[:7]} is not part of the current branch's history.")
    target_commit = repo.commit(target)
    target_subject = str(target_commit.summary)
    if not target_commit.parents:
        fail("Cannot fix up the repository's first commit.")

    repo.git.commit(f"--fixup={target}")
    print(f"Created fixup! commit for {target[:7]} '{target_subject}'.")
    if not rebase:
        return

    print("Squashing it into place...")
    rebase_or_abort(
        repo,
        f"{target}~1",
        "--interactive",
        "--autosquash",
        "--autostash",
        # Accept the autosquash todo list as-is instead of opening an editor.
        env={"GIT_SEQUENCE_EDITOR": "true"},
        hint=(
            "The fixup! commit is kept on top; run "
            f"`git rebase -i --autosquash {target[:7]}~1` to resolve it manually."
        ),
    )
    print(f"Folded the changes into {target[:7]} '{target_subject}'.")
    if is_pushed(repo, f"{target}"):
        print(
            "That commit was already pushed; update the remote with `git push --force-with-lease`."
        )


if __name__ == "__main__":
    app()

"""Shared git helpers for gyt commands.

Kept outside ``gyt_cli.commands`` on purpose: every module in that package is
registered as a git alias by ``gyt conf aliases``.
"""

import re
from pathlib import Path
from typing import NoReturn, Optional

import git
import typer

# gyt commands are Typer groups (add_typer + callback). Click groups stop parsing
# options at the first positional argument, so `gyt cleant develop --rebase` would
# treat `--rebase` as a subcommand. Allowing interspersed args fixes the ordering.
COMMAND_CONTEXT_SETTINGS = {"allow_interspersed_args": True}

# Branches that are never deleted or treated as feature branches.
PROTECTED_BRANCHES = {"main", "master"}

# Subject written by `gyt wip`. It is a valid Conventional Commit, so a WIP commit
# that slips through a rebase merge doesn't break the history's format.
WIP_SUBJECT = "chore: wip"

# Matches WIP_SUBJECT, "chore(ui): wip ...", and the older "WIP" / "wip: ..." forms,
# but not "Wipe ..." or "chore: wipe ...".
_WIP_SUBJECT = re.compile(r"(?i)^(chore(\([^)]*\))?!?:\s*)?wip\b")


def is_wip_subject(subject: str) -> bool:
    """True if a commit subject marks a work-in-progress snapshot."""
    return bool(_WIP_SUBJECT.match(subject))


def fail(message: str) -> NoReturn:
    """Print an error to stderr and exit with status 1."""
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


def open_repo() -> git.Repo:
    try:
        return git.Repo(".", search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        fail("Not inside a git repository.")


def current_branch(repo: git.Repo) -> str:
    if repo.head.is_detached:
        fail("HEAD is detached; check out a branch first.")
    return repo.active_branch.name


def remote_branch_exists(repo: git.Repo, branch: str, remote: str = "origin") -> bool:
    try:
        return any(ref.remote_head == branch for ref in repo.remote(remote).refs)
    except ValueError:  # remote does not exist
        return False


def branch_exists(repo: git.Repo, branch: str) -> bool:
    """True if the branch exists locally or on origin (checkout can create it from origin)."""
    return branch in repo.heads or remote_branch_exists(repo, branch)


def resolve_base_branch(repo: git.Repo, branch: Optional[str] = None) -> str:
    """Return the base branch to work against.

    An explicit branch must exist locally or on origin. Without one, use origin's
    default branch (refs/remotes/origin/HEAD), falling back to a local main or master.
    Raises ValueError when no base branch can be found.
    """
    if branch:
        if not branch_exists(repo, branch):
            raise ValueError(f"Branch '{branch}' was not found locally or on origin.")
        return branch

    try:
        # e.g. "origin/main". Set by `git clone`, or by `git remote set-head origin -a`.
        origin_head = repo.git.symbolic_ref("--short", "refs/remotes/origin/HEAD")
        return origin_head.split("/", 1)[1]
    except git.GitCommandError:
        pass

    for fallback in ("main", "master"):
        if fallback in repo.heads:
            return fallback

    raise ValueError(
        "Could not determine the default branch. Pass one explicitly, "
        "or run `git remote set-head origin --auto`."
    )


def base_branch_or_fail(repo: git.Repo, branch: Optional[str] = None) -> str:
    try:
        return resolve_base_branch(repo, branch)
    except ValueError as e:
        fail(str(e))


def base_ref(repo: git.Repo, base_branch: str) -> str:
    """Prefer origin's copy of the base branch, which is what a PR merges into."""
    return (
        f"origin/{base_branch}"
        if remote_branch_exists(repo, base_branch)
        else base_branch
    )


def is_dirty(repo: git.Repo) -> bool:
    return repo.is_dirty(untracked_files=True)


def has_staged_changes(repo: git.Repo) -> bool:
    return bool(repo.git.diff("--cached", "--name-only"))


def is_pushed(repo: git.Repo, rev: str = "HEAD") -> bool:
    """True if any remote-tracking branch already contains the commit."""
    return bool(repo.git.branch("-r", "--contains", rev).strip())


def has_upstream(repo: git.Repo) -> bool:
    try:
        repo.git.rev_parse("--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        return True
    except git.GitCommandError:
        return False


def gone_branches(repo: git.Repo) -> set[str]:
    """Local branches whose upstream branch no longer exists (shown as `[gone]` by git)."""
    out = repo.git.for_each_ref(
        "--format=%(refname:short)%09%(upstream:track)", "refs/heads"
    )
    return {
        name
        for name, _, track in (line.partition("\t") for line in out.splitlines())
        if track == "[gone]"
    }


def worktree_branches(repo: git.Repo) -> dict[str, str]:
    """Map each branch checked out in another worktree to that worktree's path."""
    own_path = Path(str(repo.working_tree_dir)).resolve()
    result: dict[str, str] = {}
    path = ""
    for line in repo.git.worktree("list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree ") :]
        elif line.startswith("branch refs/heads/"):
            if Path(path).resolve() != own_path:
                result[line[len("branch refs/heads/") :]] = path
    return result


def rebase_in_progress(repo: git.Repo) -> bool:
    git_dir = Path(repo.git_dir)
    return (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()


def merge_in_progress(repo: git.Repo) -> bool:
    return (Path(repo.git_dir) / "MERGE_HEAD").exists()


def rebase_or_abort(
    repo: git.Repo,
    onto: str,
    *args: str,
    env: Optional[dict] = None,
    hint: Optional[str] = None,
) -> None:
    """Run ``git rebase <args> <onto>``; abort and exit(1) if it fails part-way."""
    try:
        repo.git.rebase(*args, onto, env=env)
    except git.GitCommandError as e:
        if rebase_in_progress(repo):
            # Stopped on conflicts: restore the branch to its pre-rebase state.
            repo.git.rebase("--abort")
            fail(
                f"Rebase onto {onto} hit conflicts and was aborted. "
                + (hint or f"Run `git rebase {onto}` manually to resolve them.")
            )
        # Refused to start (e.g. uncommitted changes): nothing to abort.
        fail(f"Rebase onto {onto} could not start:\n{e.stderr.strip()}")


def merge_or_abort(repo: git.Repo, ref: str) -> None:
    """Run ``git merge <ref>``; abort and exit(1) if it stops on conflicts."""
    try:
        repo.git.merge("--no-edit", ref)
    except git.GitCommandError as e:
        if merge_in_progress(repo):
            repo.git.merge("--abort")
            fail(
                f"Merge of {ref} hit conflicts and was aborted. "
                f"Run `git merge {ref}` manually to resolve them."
            )
        fail(f"Merge of {ref} could not start:\n{e.stderr.strip()}")


def push_current_branch(repo: git.Repo, branch: str, *args: str) -> None:
    """Push the branch, setting origin as its upstream when it has none."""
    try:
        if has_upstream(repo):
            repo.git.push(*args)
        else:
            repo.git.push("-u", "origin", branch, *args)
    except git.GitCommandError as e:
        fail(f"Push of {branch} failed:\n{e.stderr.strip()}")


_GITHUB_REMOTE = re.compile(
    r"^(?:git@github\.com:|ssh://git@github\.com/|https://(?:[^@/]+@)?github\.com/)"
    r"(?P<path>[^/]+/[^/]+?)(?:\.git)?/?$"
)


def github_web_url(remote_url: str) -> str:
    """Convert a GitHub remote URL (SSH or HTTPS) to its https://github.com/owner/repo page."""
    match = _GITHUB_REMOTE.match(remote_url.strip())
    if not match:
        raise ValueError(f"Remote '{remote_url}' is not a GitHub repository.")
    return f"https://github.com/{match.group('path')}"


def conventional_prefix(commit_type: str, scope: Optional[str], branch: str) -> str:
    """Build ``type(scope)``; without a scope, use Jira keys found in the branch name."""
    if scope:
        return f"{commit_type}({scope})"
    keys = re.findall(r"[A-Z]+-\d+", branch)
    return f"{commit_type}({','.join(keys)})" if keys else commit_type

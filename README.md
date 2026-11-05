# gyt-cli

A Python CLI abstracting common Git interactions like Conventional Commit and Atlassian Smart Commit helpers.

## Installation

### From PyPI

```bash
pip install gyt-cli
```

### From Source

```bash
git clone https://github.com/your-username/gyt-cli.git
cd gyt-cli
uv sync
uv run pip install -e .
```

## Usage

After installation, the `gyt` command will be available:

```bash
gyt --help
```

Run `gyt conf aliases` to also expose every command as a git alias (`git sync`, `git wip`, ...).

### Commands

Commands that take an optional `BRANCH` use it as the base branch. Without it, they use the
remote's default branch (`refs/remotes/origin/HEAD`), falling back to a local `main` or `master`.

| Command | What it does |
| --- | --- |
| `gyt fresh NAME` | Create a feature branch from HEAD and push it with an upstream. |
| `gyt camp MESSAGE` | Commit with a Conventional Commit / Atlassian Smart Commit message, then push. |
| `gyt sync [BRANCH] [--merge]` | Fetch and rebase (or merge) the current branch onto `origin/BRANCH`, stashing and restoring uncommitted work. Aborts cleanly on conflicts. |
| `gyt cleant [BRANCH] [--rebase] [--all] [--force]` | Check out and pull the base branch, delete local branches whose upstream is gone (merged and deleted on origin), then return to your branch (optionally rebasing it). `--all` also deletes branches that were never pushed. |
| `gyt branches [BRANCH] [--fetch]` | List local branches with ahead/behind counts vs. the base branch and their upstream state (`gone`, `no upstream`, ...). |
| `gyt undo [--force]` | Undo the last commit, keeping its changes staged. Refuses if it is already pushed unless `--force`. |
| `gyt squash [BRANCH] [-m MESSAGE] [--type] [--scope] [--push]` | Squash all commits since the branch left the base into one. Reuses the first commit's message, or formats `-m` like `camp`. |
| `gyt fixup [COMMIT] [--no-rebase]` | Fold staged changes into an earlier commit via `commit --fixup` and a non-interactive autosquash rebase. Prompts for the commit when omitted. |
| `gyt rename NEW [--local]` | Rename the current branch locally and on origin, and repoint its upstream. |
| `gyt wip [--no-push]` | Commit everything, including untracked files, as `WIP` (skipping hooks) and push it. |
| `gyt unwip` | Turn the consecutive `WIP` commits on top of the branch back into uncommitted changes. |
| `gyt pr [BRANCH] [--no-open]` | Push the branch if needed and open GitHub's new pull request page, titled from the last commit. |
| `gyt tree BRANCH [--path] [--from]` | Check out a branch in a new worktree at `<repo>-<branch>` next to the repo. Creates the branch from the base if it doesn't exist. |
| `gyt repo` / `gyt ci` / `gyt jira` | Open the branch, CI, or Jira issue in the browser. |

## Development

### Prerequisites

- Python 3.10 or higher
- [UV](https://docs.astral.sh/uv/) package manager

### Setup Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/gyt-cli.git
   cd gyt-cli
   ```

2. Install dependencies using UV:
   ```bash
   uv sync
   ```

   This will create a virtual environment and install all production and development dependencies.

### Development Workflow

#### Adding Dependencies

To add a new production dependency:
```bash
uv add <package-name>
```

To add a development dependency:
```bash
uv add --dev <package-name>
```

#### Running Tests

Run the test suite:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=gyt_cli
```

#### Code Quality

Format code with Black:
```bash
uv run black .
```

Run type checking with MyPy:
```bash
uv run mypy gyt_cli
```

#### Running the CLI During Development

Execute the CLI directly from source:
```bash
uv run gyt --help
```

Or run specific commands:
```bash
uv run gyt <command> <args>
```

### Project Structure

```
gyt-cli/
├── gyt_cli/           # Main package
│   ├── __init__.py
│   ├── cli.py         # CLI entry point
│   ├── commands/      # Command modules
│   ├── config/        # Configuration handling
│   └── utils.py       # Utility functions
├── tests/             # Test suite
├── pyproject.toml     # Project configuration
├── uv.lock           # Dependency lock file
└── README.md         # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `uv run pytest`
5. Run code quality checks: `uv run black .` and `uv run mypy gyt_cli`
6. Commit your changes using conventional commits
7. Push to your fork and submit a pull request

## License

This project is licensed under the Apache-2.0 License - see the LICENSE file for details.

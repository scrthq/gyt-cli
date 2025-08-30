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

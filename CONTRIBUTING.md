# Contributing to classic-yr

Thank you for your interest in contributing to classic-yr!

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/steinhh/classic-yr.git
cd classic-yr
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install the package in development mode

```bash
pip install -e ".[dev]"
```

### 4. Install pre-commit hooks

```bash
pre-commit install
```

## Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatter
- **Ruff**: Fast Python linter
- **Mypy**: Static type checker
- **Pytest**: Testing framework

### Running checks manually

```bash
# Format code
make format

# Run all linters
make lint

# Run tests with coverage
make test
```

Or run individual tools:

```bash
black src tests
ruff check src tests
mypy src
pytest
```

## Pre-commit Hooks

Pre-commit hooks are automatically installed and will run before each commit:

- YAML/TOML validation
- Trailing whitespace removal
- End-of-file fixer
- Black formatting
- Ruff linting
- Mypy type checking

To run pre-commit hooks manually:

```bash
pre-commit run --all-files
```

## Testing

Write tests in the `tests/` directory. Test files should start with `test_` or end with `_test.py`.

Run tests with:

```bash
pytest
```

View coverage report in `htmlcov/index.html` after running tests.

## Building and Publishing

### Build the package

```bash
make build
```

This creates distribution files in the `dist/` directory.

### Validate the build

```bash
twine check dist/*
```

### Publish to PyPI

**Test PyPI (recommended first):**

```bash
twine upload --repository testpypi dist/*
```

**Production PyPI:**

```bash
make publish
```

Or use GitHub Actions by creating a release on GitHub.

## GitHub Actions

This project includes CI/CD workflows:

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request:

- Linting (Black, Ruff, Mypy)
- Testing on multiple Python versions (3.9-3.13)
- Testing on multiple OS (Ubuntu, macOS, Windows)
- Build validation

### Publish Workflow (`.github/workflows/publish.yml`)

Automatically publishes to PyPI when you create a GitHub release.

To publish a new version:

1. Update version in `pyproject.toml`
2. Create a git tag: `git tag v0.1.0`
3. Push the tag: `git push origin v0.1.0`
4. Create a GitHub release from the tag

The package will be automatically published to PyPI.

## Project Structure

```text
classic-yr/
??? .github/
?   ??? workflows/       # CI/CD workflows
??? src/
?   ??? classic_yr/      # Main package code
?       ??? __init__.py
?       ??? py.typed     # PEP 561 marker for type hints
??? tests/               # Test files
??? pyproject.toml       # Project metadata and tool config
??? .pre-commit-config.yaml
??? .gitignore
??? LICENSE
??? README.md
??? CONTRIBUTING.md
??? Makefile
??? MANIFEST.in
```

## Making Changes

1. Create a new branch for your feature/fix
2. Make your changes
3. Add tests for new functionality
4. Run the test suite and linters
5. Commit your changes (pre-commit hooks will run)
6. Push and create a pull request

## Code Style

- Use type hints for all function arguments and return values
- Follow PEP 8 (enforced by Black and Ruff)
- Write docstrings for public APIs
- Keep functions small and focused
- Aim for 100% test coverage

## Questions?

Feel free to open an issue for any questions or concerns.

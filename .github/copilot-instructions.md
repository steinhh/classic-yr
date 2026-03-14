# Copilot Instructions for classic-yr

## Project Overview

This is a Python package for classic yr weather data plotting. The package follows modern Python packaging standards and maintains strict code quality requirements.

## Code Style & Formatting

- **Line length**: 100 characters (enforced by Black)
- **Type hints**: Required for all function parameters and return values
- **Docstrings**: Use Google style for all public functions and classes
- **Imports**: Use absolute imports, organized by isort (via Ruff)
- **Formatting**: Black is the authoritative formatter

## Python Standards

- **Python version**: Support Python 3.9+
- **Type checking**: All code must pass mypy in strict mode
- **Naming**: Follow PEP 8 conventions
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`

## Project Structure

```text
src/classic_yr/    # All package code goes here
tests/             # Mirror the src structure for tests
```

- Keep modules in `src/classic_yr/`
- Use relative imports within the package
- Export public APIs in `__init__.py`

## Testing Requirements

- Write pytest tests for all new functions
- Test files: `test_*.py` or `*_test.py`
- Use type hints in test functions
- Aim for 100% code coverage
- Use fixtures for shared test setup
- Mock external dependencies

## Dependencies

- Minimize external dependencies
- Add runtime dependencies to `dependencies` in `pyproject.toml`
- Add dev dependencies to `[project.optional-dependencies] dev`
- Specify minimum versions: `package>=X.Y.Z`

## Common Patterns

### Function with Type Hints

```python
def process_weather_data(
    data: list[dict[str, float]], threshold: float = 0.0
) -> dict[str, list[float]]:
    """Process weather data and group by threshold.

    Args:
        data: List of weather data dictionaries.
        threshold: Minimum value threshold.

    Returns:
        Dictionary mapping categories to values.
    """
    # Implementation
    return result
```

### Error Handling

- Use specific exceptions, not bare `except:`
- Provide helpful error messages
- Use custom exceptions for domain-specific errors

### File Operations

- Use `pathlib.Path` instead of `os.path`
- Use context managers for file operations

```python
from pathlib import Path

def read_data(filepath: Path) -> str:
    """Read data from file."""
    with filepath.open() as f:
        return f.read()
```

## Git Commit Messages

- Use conventional commits format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Keep first line under 72 characters

## Pre-commit Checks

Before committing, the following run automatically:
- Black formatting
- Ruff linting
- Mypy type checking
- YAML/TOML validation
- Trailing whitespace removal

Fix any issues before committing.

## Documentation

- Update README.md for user-facing changes
- Update CONTRIBUTING.md for developer workflow changes
- Add inline comments for complex logic only
- Prefer clear code over comments when possible

## Developer-added instructions (do not modify or delete)

When creating binary executable files, use file extension `.exe` to avoid confusion with source files.

Use a terse style for the README files, try to avoid duplication of information.

Use redirect to top-level file dev_null.txt instead of redirecting to /dev/null, since such redirects cannot be auto-approved by copilot.

Warn me when I'm introducing new features that warrant an increment of the major version number.

Warn me if I'm changing the public API in a way that is not backward compatible.

Favour replace_string_in_file/multi_replace_string_in_file over sed for string replacements in files, since replace_string_in_file is auto-approved by copilot.

Log all prompts, questions and queries completely verbatim into `chats/log.md`, using a header "\n\n\n-------PROMPT YYYY-MM-DD HH:MM : " with the current date and time. Do not leave out any details, do not change the wording of the prompts at all. Then add a single-line summary of your response or actions, as a quote (i.e. line starting with "> "). When my prompts refer to previous prompts, make sure the log file contains enough context to understand the references. When my prompts refer to options you have given (as in "do 1 and 2"), add those options to the log file for context. Summarise your response/actions in a single line after the prompt. Always append the prompt and response summary to `chats/log.md`, even for purely informational questions. Don't print the log entry in the chat, and do not show any echo statement to put the log entry there. Never modify what is already in the log file unless I explicitly ask you to do so.

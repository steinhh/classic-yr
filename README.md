# classic-yr

[![CI](https://github.com/steinhh/classic-yr/actions/workflows/ci.yml/badge.svg)](https://github.com/steinhh/classic-yr/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/classic-yr.svg)](https://pypi.org/project/classic-yr/)
[![Python Version](https://img.shields.io/pypi/pyversions/classic-yr.svg)](https://pypi.org/project/classic-yr/)
[![License](https://img.shields.io/pypi/l/classic-yr.svg)](https://github.com/steinhh/classic-yr/blob/main/LICENSE)

The classic yr weather data plot

## Installation

```bash
pip install classic-yr
```

## Development

Install the package in development mode with all dependencies:

```bash
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
pytest
```

Or use the Makefile:

```bash
make test
```

## Code Quality

Format code:

```bash
make format
```

Run linters:

```bash
make lint
```

## Building and Publishing

Build the package:

```bash
make build
```

Publish to PyPI (requires credentials):

```bash
make publish
```

Or use GitHub Actions for automated publishing on releases.

## License

MIT License - see [LICENSE](LICENSE) file for details.

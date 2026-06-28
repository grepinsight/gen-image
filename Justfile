# Justfile for gen-image

# Install dependencies
install:
    uv sync

# Run tests
test:
    uv run python -m pytest

# Run linter and formatter
lint:
    uv run ruff check src/ tests/
    uv run ruff format src/ tests/

# Build the package
build:
    uv build

# Run the CLI (for testing)
run *ARGS:
    uv run gen-image {{ARGS}}

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} +

# Show available commands
help:
    @just --list

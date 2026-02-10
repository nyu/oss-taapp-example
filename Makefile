# Development setup and common tasks

.PHONY: setup sync install-hooks lint test check

# Full development setup - run this after cloning
setup: sync install-hooks

# Sync all dependencies
sync:
	uv sync --all-packages --all-extras

# Install pre-commit hooks
install-hooks:
	uv run pre-commit install --hook-type commit-msg --hook-type pre-commit

# Run linting and formatting
lint:
	uv run pre-commit run --all-files

# Run tests
test:
	uv run pytest

# Run all checks (lint + test)
check: lint test

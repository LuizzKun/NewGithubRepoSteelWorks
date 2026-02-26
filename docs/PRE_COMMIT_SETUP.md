# Pre-commit Setup Guide

This project uses pre-commit hooks to ensure code quality before commits.

## Installation

After cloning the repository:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install
```

## What Runs on Every Commit

1. **ruff format** - Ensures consistent code formatting
2. **ruff check** - Linting for code issues
3. **mypy** - Static type checking
4. **pytest** - Unit tests

## Common Scenarios

### Pre-commit skips the mypy hook

If you see mypy warnings about missing dependencies, install SQLAlchemy:

```bash
pip install sqlalchemy
```

### I want to skip pre-commit

To commit without running hooks (not recommended):

```bash
git commit --no-verify
```

### Running hooks manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff-format --all-files
pre-commit run ruff --all-files
pre-commit run mypy --all-files
pre-commit run pytest --all-files
```

### Updating hooks

```bash
pre-commit autoupdate
```

## Troubleshooting

**Issue**: Pre-commit hook failed on ruff format

**Solution**: Ruff will automatically fix most formatting issues. Re-stage the changes:

```bash
git add .
git commit -m "Your message"
```

**Issue**: Mypy errors about type issues

**Solution**: Add type annotations or use `type: ignore` comments as appropriate. See [mypy documentation](https://mypy.readthedocs.io/).

**Issue**: Tests fail in pre-commit

**Solution**: Run `pytest tests/ -v` locally to debug, then recommit.

## GitHub Actions CI

In addition to local pre-commit hooks, GitHub Actions runs the same checks on:
- Pull request creation
- Updates to pull requests
- Pushes to main/develop branches

View workflows in `.github/workflows/code-quality.yml`

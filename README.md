# SteelWorks Operations Reporting Tool

A Python-based operations reporting system for SteelWorks to analyze production, inspection, and shipment data.

## Tech Stack

- **Language**: Python 3.9+
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Testing**: pytest with coverage
- **Code Quality**: ruff (formatter & linter), mypy (type checker)
- **CI/CD**: GitHub Actions

## Project Structure

```
steelworks-operations/
├── src/steelworks/          # Main application code
│   ├── models.py            # SQLAlchemy ORM models
│   ├── repositories.py       # Repository pattern for data access
│   └── __init__.py
├── tests/                    # Unit tests
│   ├── test_repositories.py  # Repository tests
│   ├── conftest.py          # Pytest fixtures
│   └── __init__.py
├── db/                       # Database schemas and scripts
│   ├── schema.sql           # PostgreSQL schema
│   └── sample_queries.sql   # Example queries
├── docs/                     # Documentation
│   ├── architecture_decision_records.md
│   ├── assumptions_scope.md
│   ├── data_design.md
│   └── tech_stack_decision_records.md
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── .github/workflows/        # GitHub Actions CI/CD
├── pyproject.toml           # Poetry dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip or Poetry
- PostgreSQL (for production database)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd steelworks-operations
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/steelworks --cov-report=term-missing
```

### Code Quality Checks

```bash
# Format code with ruff
python -m ruff format src tests

# Run linter
python -m ruff check src tests

# Run type checker
python -m mypy src tests --ignore-missing-imports
```

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit:
- **ruff format**: Code formatting
- **ruff check**: Linting
- **mypy**: Type checking
- **pytest**: Unit tests

To run all hooks manually:
```bash
pre-commit run --all-files
```

To skip hooks on a commit:
```bash
git commit --no-verify
```

## CI/CD Pipeline

GitHub Actions automatically runs on:
- Pull request creation/updates
- Pushes to main or develop branches

The pipeline runs:
- Code formatting check
- Linting
- Type checking
- Unit tests with coverage
- Coverage reporting to Codecov

## Database

### Schema

See [data_design.md](docs/data_design.md) for the complete data model.

### Test Database

Tests use in-memory SQLite for isolation. Create the schema:

```bash
python -c "from src.steelworks.models import Base, engine; Base.metadata.create_all(engine)"
```

## Documentation

- [Architecture Decision Records](docs/architecture_decision_records.md)
- [Assumptions & Scope](docs/assumptions_scope.md)
- [Data Design](docs/data_design.md)
- [Tech Stack Decision Records](docs/tech_stack_decision_records.md)

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and ensure all tests pass
3. Pre-commit hooks will validate code quality
4. Create a pull request

## Test Coverage

Current coverage: **97%**

```
Name                             Stmts   Miss  Cover
------------------------------------------------------
src/steelworks/__init__.py           0      0   100%
src/steelworks/models.py            46      0   100%
src/steelworks/repositories.py      20      2    90%
------------------------------------------------------
TOTAL                               66      2    97%
```

## License

MIT
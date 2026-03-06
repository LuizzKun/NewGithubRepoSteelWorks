# Testing Guide for SteelWorks Operations Reporting Tool

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Running Tests](#running-tests)
5. [Docker Setup](#docker-setup)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.10+** (required for pattern matching syntax)
- **PostgreSQL** (for test and production databases)
- **Docker Desktop** (optional, for containerized testing)
- **Git** (for version control)

### Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (for E2E tests)
playwright install chromium
```

## Environment Setup

### 1. Production Environment (.env)

Create a `.env` file in the project root with your **Render.com production database URL**:

```bash
# Copy from example
cp .env.example .env

# Edit .env and add your Render PostgreSQL URL
# Found in: Render Dashboard → PostgreSQL Instance → Connection Details
DATABASE_URL=postgresql://user:password@dpg-xxxxx.render.com/steelworks_db?sslmode=require
```

### 2. Test Environment (.env.test)

The `.env.test` file should point to a **separate test database**:

```bash
# Local test database (recommended)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/steelworks_test_db

# OR use a separate Render test database
DATABASE_URL=postgresql://user:password@dpg-yyyyy.render.com/steelworks_test_db?sslmode=require
```

**Important:** Never use your production database for testing!

### 3. Create Test Database

```bash
# PostgreSQL command line
createdb steelworks_test_db

# Or using psql
psql -U postgres
CREATE DATABASE steelworks_test_db;
\q
```

## Database Configuration

### Initialize Production Database

```bash
# Load schema and seed data into production database
python init_db.py
```

### Initialize Test Database

```bash
# Set test environment and initialize
export $(cat .env.test | xargs)  # Linux/Mac
# or
Get-Content .env.test | ForEach-Object { $_.Split('=')[0] = $_.Split('=')[1] }  # PowerShell

python init_db.py
```

## Running Tests

### Unit Tests

Test individual components (models, repositories):

```bash
# Run all unit tests
pytest tests/test_repositories.py -v

# Run with coverage
pytest tests/test_repositories.py --cov=src/steelworks --cov-report=html
```

### Integration Tests

Test service layer with real database operations:

```bash
# Run integration tests (uses .env.test)
pytest tests/test_integration.py -v

# Run specific test class
pytest tests/test_integration.py::TestOperationsReportingServiceIntegration -v

# Run specific test
pytest tests/test_integration.py::TestOperationsReportingServiceIntegration::test_get_lines_with_most_defects -v
```

### End-to-End (E2E) Tests

Test complete user workflows using Playwright:

```bash
# Run E2E tests headless (background mode)
pytest tests/test_e2e_playwright.py -v

# Run E2E tests with visible browser (debugging)
pytest tests/test_e2e_playwright.py -v --headed

# Run specific E2E test class
pytest tests/test_e2e_playwright.py::TestDashboardPage -v

# Slow down test execution for debugging
pytest tests/test_e2e_playwright.py -v --slowmo=1000
```

### Run All Tests

```bash
# Run entire test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/steelworks --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

### Test Markers

```bash
# Run only integration tests
pytest -m integration -v

# Run only e2e tests
pytest -m e2e -v

# Skip slow tests
pytest -m "not slow" -v
```

## Docker Setup

### Install Docker Desktop

#### Windows
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Run the installer
3. Restart your computer
4. Verify: `docker --version`

#### Mac
1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. Drag to Applications folder
3. Launch Docker Desktop
4. Verify: `docker --version`

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker --version
```

### Docker Test Database Setup

Create a PostgreSQL container for testing:

```bash
# Start PostgreSQL container
docker run -d \
  --name steelworks-test-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=steelworks_test_db \
  -p 5433:5432 \
  postgres:15

# Verify container is running
docker ps

# Update .env.test to use Docker database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/steelworks_test_db
```

### Docker Compose (Optional)

Create `docker-compose.test.yml`:

```yaml
version: '3.8'

services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: steelworks_test_db
    ports:
      - "5433:5432"
    volumes:
      - test-db-data:/var/lib/postgresql/data

volumes:
  test-db-data:
```

Usage:
```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest tests/test_integration.py -v

# Stop test database
docker-compose -f docker-compose.test.yml down
```

## Continuous Integration

### GitHub Actions

Tests run automatically on push/PR. See `.github/workflows/code-quality.yml`:

```yaml
- name: Run unit tests
  run: pytest tests/test_repositories.py -v

- name: Run integration tests
  run: pytest tests/test_integration.py -v
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

- name: Run E2E tests
  run: |
    playwright install chromium
    pytest tests/test_e2e_playwright.py -v
```

### Add Test Database Secret to GitHub

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add secret: `TEST_DATABASE_URL`
3. Value: Your test database connection string

## Troubleshooting

### Issue: ModuleNotFoundError

```bash
# Solution: Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/Mac
$env:PYTHONPATH += ";$(pwd)\src"  # PowerShell
```

### Issue: Database connection refused

```bash
# Check PostgreSQL is running
pg_isready

# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list  # Mac

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # Mac
```

### Issue: Playwright tests fail

```bash
# Reinstall browsers
playwright install chromium --force

# Check Streamlit is accessible
curl http://localhost:8501

# Run with debug logs
PWDEBUG=1 pytest tests/test_e2e_playwright.py -v
```

### Issue: Test database has stale data

```bash
# Drop and recreate test database
dropdb steelworks_test_db
createdb steelworks_test_db

# Re-run integration tests (they create schema automatically)
pytest tests/test_integration.py -v
```

### Issue: Permission denied on .env files

```bash
# Fix file permissions
chmod 600 .env .env.test  # Linux/Mac
```

## Test Coverage Goals

- **Unit Tests:** > 90% coverage
- **Integration Tests:** All 6 acceptance criteria covered
- **E2E Tests:** All user workflows tested

### Current Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src/steelworks --cov-report=term-missing

# View detailed HTML report
pytest tests/ --cov=src/steelworks --cov-report=html
open htmlcov/index.html
```

## Best Practices

1. **Always use .env.test for testing** - Never test against production
2. **Run tests before committing** - Use pre-commit hooks
3. **Keep tests independent** - Each test should set up its own data
4. **Use fixtures for common setup** - DRY principle
5. **Test edge cases** - Empty data, invalid inputs, etc.
6. **Document test scenarios** - Clear docstrings for each test

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Python Documentation](https://playwright.dev/python/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_basics.html#session-frequently-asked-questions)
- [Streamlit Testing Guide](https://docs.streamlit.io/library/advanced-features/testing)

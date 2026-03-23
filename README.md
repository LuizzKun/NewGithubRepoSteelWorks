# SteelWorks Operations Reporting Tool

A Python-based operations reporting system with comprehensive security scanning, code quality checks, and automated CI/CD pipeline.

> **CI/CD Test**: Testing deployment pipeline with Docker build and Render deployment (March 23, 2026)

## 🛡️ Security Features

### Software Bill of Materials (SBOM)
- **Automated SBOM Generation**: Exports dependency lists in multiple formats
- **License Compliance**: Automatic scanning for GPL/AGPL/LGPL copyleft licenses
- **Vulnerability Tracking**: GitHub Dependabot integration for security alerts

### Code Scanning
- **CodeQL Analysis**: GitHub Advanced Security scanning for vulnerabilities
- **Pre-commit Hooks**: Automated checks before every commit
- **Security-Extended Queries**: Comprehensive security rule set

## 📋 Project Overview

This system helps SteelWorks analyze production, inspection, and shipment data with:
- **SQLAlchemy ORM**: Type-safe database access
- **Repository Pattern**: Clean architecture with data access layer
- **Comprehensive Testing**: 97% code coverage with pytest
- **Automated Quality Checks**: Ruff, mypy, and custom license scanning

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or Poetry

### Installation

```bash
# Clone the repository
git clone https://github.com/LuizzKun/NewGithubRepoSteelWorks.git
cd NewGithubRepoSteelWorks

# Install dependencies
pip install -r requirements.txt

# Or with Poetry
poetry install

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/steelworks --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🔒 Security & Compliance

### Pre-commit Hooks

Every commit automatically runs:

1. **Ruff Format**: Code formatting (PEP 8)
2. **Ruff Lint**: Code quality checks
3. **MyPy**: Static type checking
4. **Pytest**: Full test suite
5. **License Check**: Scans for prohibited copyleft licenses

### Manual Security Checks

```bash
# Run all pre-commit hooks manually
pre-commit run --all-files

# Generate SBOM
python -m piplicenses --format=json --output-file=sbom.json

# Check for copyleft licenses
python scripts/check_copyleft_licenses.py

# Run CodeQL locally (requires GitHub CLI)
gh codeql database create --language=python
```

### License Compliance

This project follows a strict license policy:

- ✅ **Approved**: MIT, Apache 2.0, BSD
- ⚠️ **Review Required**: LGPL (transitive dependencies only)
- ❌ **Prohibited**: GPL, AGPL

See [SBOM Report](docs/SBOM_REPORT.md) for detailed license analysis.

## 📊 CI/CD Pipeline

GitHub Actions workflows:

### Code Quality (`code-quality.yml`)
- Runs on: PR creation/updates, pushes to main/develop
- Matrix testing: Python 3.9, 3.10, 3.11
- Steps: Format check → Lint → Type check → Tests → Coverage

### SBOM Generation (`sbom.yml`)
- Generates Software Bill of Materials
- Exports in JSON, Markdown, CSV formats
- Uploads artifacts for download

### CodeQL Security Scanning (`codeql.yml`)
- Runs on: PR, push, weekly schedule
- Detects: SQL injection, XSS, code injection, insecure patterns
- Results visible in Security tab

## 📁 Project Structure

```
steelworks-operations/
├── .github/workflows/       # CI/CD pipelines
│   ├── code-quality.yml     # Ruff, mypy, pytest
│   ├── codeql.yml           # Security scanning
│   └── sbom.yml             # Dependency tracking
├── docs/                    # Documentation
│   ├── SBOM_REPORT.md       # License compliance report
│   ├── PRE_COMMIT_SETUP.md  # Pre-commit guide
│   └── *.md                 # Architecture, design docs
├── scripts/                 # Utility scripts
│   ├── check_copyleft_licenses.py
│   └── check_gpl_license.py
├── src/steelworks/          # Application code
│   ├── models.py            # SQLAlchemy models
│   └── repositories.py      # Data access layer
├── tests/                   # Unit tests
├── .pre-commit-config.yaml  # Pre-commit configuration
├── pyproject.toml           # Poetry dependencies & tool config
└── sbom-*.{json,md,csv}     # Generated SBOM files
```

## 🛠️ Development

### Code Quality Tools

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests --fix

# Type check
mypy src tests --ignore-missing-imports

# Run security checks
python scripts/check_copyleft_licenses.py
```

### Pre-commit Hook Configuration

See [.pre-commit-config.yaml](.pre-commit-config.yaml) for detailed hook configuration with extensive comments explaining the mental model.

### Skipping Hooks (Emergency Only)

```bash
# Skip all hooks (not recommended)
git commit --no-verify

# Skip specific hooks
SKIP=pytest-tests git commit -m "message"
```

## 📈 Code Coverage

Current: **97%** (66/66 statements)

| Module | Coverage |
|--------|----------|
| models.py | 100% |
| repositories.py | 90% |
| Overall | 97% |

## 🔐 GitHub Security Features

### Enabling Security Features

1. **Dependency Graph**:
   - Settings → Security & Analysis → Enable Dependency graph
   
2. **Dependabot Alerts**:
   - Settings → Security & Analysis → Enable Dependabot alerts
   
3. **Code Scanning**:
   - Automatically enabled via `.github/workflows/codeql.yml`
   - View results: Security tab → Code scanning alerts

### Exporting SBOM from GitHub

```bash
# Via GitHub UI
Repository → Insights → Dependency graph → Export SBOM

# Via API
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/LuizzKun/NewGithubRepoSteelWorks/dependency-graph/sbom
```

## 📚 Documentation

- [Architecture Decision Records](docs/architecture_decision_records.md)
- [Data Design](docs/data_design.md)
- [SBOM & License Report](docs/SBOM_REPORT.md)
- [Pre-commit Setup Guide](docs/PRE_COMMIT_SETUP.md)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes (pre-commit hooks will run automatically)
3. Ensure all tests pass: `pytest tests/`
4. Push and create a Pull Request
5. Wait for CI/CD checks to pass
6. Request review

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- **Repository**: https://github.com/LuizzKun/NewGithubRepoSteelWorks
- **Issues**: https://github.com/LuizzKun/NewGithubRepoSteelWorks/issues
- **Security Advisories**: https://github.com/LuizzKun/NewGithubRepoSteelWorks/security

---

**Last Updated**: March 4, 2026  
**Version**: 1.0.0
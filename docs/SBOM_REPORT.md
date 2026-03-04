# Software Bill of Materials (SBOM) Report

**Project**: SteelWorks Operations Reporting Tool  
**Generated**: March 4, 2026  
**Tool**: pip-licenses v5.0+  

---

## Executive Summary

This report documents all third-party dependencies and their licenses used in the SteelWorks Operations project. A comprehensive analysis has been performed to identify potential licensing conflicts, particularly copyleft licenses (GPL/AGPL/LGPL).

---

## SBOM Files Generated

1. **sbom-pip-licenses.json** - Machine-readable JSON format
2. **sbom-pip-licenses.md** - Human-readable Markdown table
3. **sbom-pip-licenses.csv** - Spreadsheet-compatible format

---

## License Distribution

The project uses dependencies under the following license types:

- **MIT License**: Majority of dependencies (most permissive)
- **Apache Software License**: Several core packages
- **BSD License**: Multiple variants (BSD-2-Clause, BSD-3-Clause)
- **Python Software Foundation License**: Standard library components
- **Mozilla Public License 2.0**: Limited use
- **⚠️ LGPL**: 2 transitive dependencies (see issues below)

---

## ⚠️ Copyleft License Issues Detected

### Critical Findings

During automated license scanning, the following packages with copyleft licenses were identified:

| Package | Version | License | Risk Level |
|---------|---------|---------|------------|
| chardet | 5.2.0 | GNU LGPLv2+ | Medium |
| frozendict | 2.4.7 | GNU LGPLv3 | Medium |

### Impact Analysis

**LGPL (Lesser GPL)** requires:
- Dynamically linked libraries can be used without source disclosure requirements
- If statically linked or modified, derivative works must be distributed under compatible licenses
- Runtime usage (Python imports) is generally considered safe

**Current Status**: ⚠️  
These are transitive dependencies (dependencies of dependencies), not directly installed by this project.

### Recommended Actions

1. **Immediate**: Document the presence of LGPL dependencies (✅ Done via this report)
2. **Short-term**: Identify which packages require chardet/frozendict
3. **Long-term**: Consider alternatives:
   - `chardet` → `charset-normalizer` (MIT license)
   - `frozendict` → `frozendict-fast` or standard dict + tuple patterns

### Dependency Tree Analysis

To identify which packages brought in these LGPL dependencies:

```bash
pip show chardet
pip show frozendict
```

Common sources:
- chardet: Often a dependency of `requests`, `beautifulsoup4`
- frozendict: Often used by `cyclonedx-bom`, JSON libraries

---

## License Compliance Strategy

### ✅ Approved Licenses (Permissive)

- MIT License
- Apache License 2.0
- BSD (2-Clause, 3-Clause)
- Python Software Foundation License
- ISC License

### ⚠️ Conditional Approval (Review Required)

- LGPL (Lesser GPL) - Allowed for runtime dependencies only
- Mozilla Public License 2.0 - Generally compatible

### ❌ Prohibited Licenses

- GPL (General Public License)
- AGPL (Affero General Public License)
- Proprietary licenses without explicit permission

---

## Pre-commit Hook Configuration

A pre-commit hook has been configured to automatically scan for prohibited licenses:

```yaml
- id: license-check-gpl
  name: block copyleft licenses (GPL/AGPL/LGPL) in runtime deps
  entry: python scripts/check_copyleft_licenses.py
```

This hook:
- ✅ Runs automatically before each commit
- ✅ Scans all installed dependencies
- ✅ Blocks commits if GPL/AGPL licenses found
- ⚠️ Warns about LGPL licenses

---

## GitHub Dependency Graph

To enable and use GitHub's Dependency Graph:

### Enabling Dependency Graph

1. Go to repository Settings
2. Navigate to Security & Analysis
3. Enable **Dependency graph**
4. Enable **Dependabot alerts** (recommended)

### Exporting SBOM from GitHub

Once enabled, GitHub provides:
- Automatic dependency tracking
- Security vulnerability alerts
- SBOM export in SPDX format

**Export URL**:
```
https://github.com/LuizzKun/NewGithubRepoSteelWorks/network/dependencies
```

---

## Code Scanning Setup

### GitHub CodeQL

CodeQL security scanning has been configured in `.github/workflows/codeql.yml`:

- **Languages**: Python
- **Triggers**: Push, PR, Weekly schedule
- **Queries**: security-extended, security-and-quality
- **Analysis**: Automatic on every PR

### Security Scan Coverage

- ✅ SQL injection detection
- ✅ Path traversal vulnerabilities
- ✅ Insecure randomness
- ✅ Code injection risks
- ✅ Hardcoded credentials
- ✅ Insecure deserialization

---

## Maintenance

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Regenerate SBOM after updates
python -m piplicenses --format=json --output-file=sbom-pip-licenses.json
```

### Periodic License Audits

- **Frequency**: Every sprint or monthly
- **Process**: 
  1. Regenerate SBOM
  2. Run license checker
  3. Review new dependencies
  4. Update this document

---

## References

- [OSI Approved Licenses](https://opensource.org/licenses/)
- [LGPL Compliance Guidelines](https://www.gnu.org/licenses/lgpl-3.0.en.html)
- [GitHub Dependency Graph Documentation](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain)
- [CycloneDX SBOM Specification](https://cyclonedx.org/)

---

## Approval Status

- [x] SBOM Generated
- [x] License Scan Completed
- [x] Copyleft Dependencies Identified
- [x] Mitigation Strategy Documented
- [ ] Legal Review (if required by organization)

**Approved for Development Use**: Yes (with documented LGPL dependencies)  
**Production Deployment**: Requires review of LGPL implications

---

**Document Version**: 1.0  
**Last Updated**: March 4, 2026  
**Next Review**: April 2026

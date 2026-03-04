#!/usr/bin/env python3
"""
Check for copyleft licenses (GPL/AGPL/LGPL) in dependencies.

This script is used as a pre-commit hook to ensure no copyleft licenses
are present in runtime dependencies, which could create licensing conflicts.
"""

import sys
import json
import subprocess
import re


def check_licenses():
    """Check installed packages for copyleft licenses."""
    try:
        # Run pip-licenses to get all package licenses in JSON format
        result = subprocess.run(
            ["python", "-m", "piplicenses", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        licenses_data = json.loads(result.stdout)
        
        # Define copyleft license patterns
        copyleft_patterns = [
            r"^GPL",
            r"^AGPL",
            r"^LGPL",
            r"GNU\s+General\s+Public\s+License",
            r"GNU\s+Affero\s+General\s+Public\s+License",
            r"GNU\s+Lesser\s+General\s+Public\s+License",
        ]
        
        copyleft_found = []
        
        # Check each package
        for package in licenses_data:
            license_name = package.get("License", "")
            package_name = package.get("Name", "")
            version = package.get("Version", "")
            
            for pattern in copyleft_patterns:
                if re.search(pattern, license_name, re.IGNORECASE):
                    copyleft_found.append({
                        "package": package_name,
                        "version": version,
                        "license": license_name
                    })
                    break
        
        if copyleft_found:
            print("=" * 70)
            print("ERROR: Copyleft licenses detected in dependencies!")
            print("=" * 70)
            print()
            print("The following packages have copyleft licenses (GPL/AGPL/LGPL):")
            print()
            
            for pkg in copyleft_found:
                print(f"  ❌ {pkg['package']} ({pkg['version']})")
                print(f"     License: {pkg['license']}")
                print()
            
            print("=" * 70)
            print("Action Required:")
            print("  - Remove these dependencies, OR")
            print("  - Replace with alternatives that have permissive licenses (MIT, Apache, BSD)")
            print("=" * 70)
            print()
            
            return 1
        else:
            print("✅ No copyleft licenses detected in dependencies.")
            return 0
            
    except subprocess.CalledProcessError as e:
        print(f"Error running pip-licenses: {e}", file=sys.stderr)
        print("Make sure pip-licenses is installed: pip install pip-licenses")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing pip-licenses output: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(check_licenses())

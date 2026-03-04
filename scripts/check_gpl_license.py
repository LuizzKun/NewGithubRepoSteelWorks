#!/usr/bin/env python3
"""
GPL License Checker for Pre-commit Hook

This script checks Python files for GPL license headers and fails if found.
GPL licenses require derivative works to also be GPL-licensed, which may
conflict with proprietary or more permissive open-source licenses.
"""

import sys
import re
from pathlib import Path

# GPL license patterns to detect
GPL_PATTERNS = [
    r"GNU\s+General\s+Public\s+License",
    r"GPL-?\d+\.?\d*",
    r"GPLv\d+",
    r"licensed\s+under\s+the\s+GPL",
    r"GNU\s+GPL",
    r"www\.gnu\.org/licenses/gpl",
    r"Free\s+Software\s+Foundation.*GPL",
]


def check_file_for_gpl(filepath: str) -> tuple[bool, list[str]]:
    """
    Check a single file for GPL license references.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        Tuple of (has_gpl, matches) where has_gpl is True if GPL found
        and matches is a list of matched patterns
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = []
        for pattern in GPL_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                matches.append(pattern)
                
        return len(matches) > 0, matches
        
    except UnicodeDecodeError:
        # Skip binary files
        return False, []
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False, []


def main():
    """Main function to check all provided files."""
    if len(sys.argv) < 2:
        print("Usage: check_gpl_license.py <file1> <file2> ...", file=sys.stderr)
        sys.exit(0)
    
    files_to_check = sys.argv[1:]
    gpl_found = False
    
    for filepath in files_to_check:
        has_gpl, matches = check_file_for_gpl(filepath)
        if has_gpl:
            gpl_found = True
            print(f"❌ GPL license detected in: {filepath}")
            print(f"   Matched patterns: {', '.join(matches)}")
            print(f"   Please use MIT, Apache 2.0, or another permissive license.\n")
    
    if gpl_found:
        print("=" * 70)
        print("FAIL: GPL licenses detected in one or more files.")
        print("=" * 70)
        print("\nGPL licenses enforce copyleft requirements that may conflict")
        print("with this project's licensing goals. Consider using:")
        print("  - MIT License (most permissive)")
        print("  - Apache License 2.0 (patent protection)")
        print("  - BSD 3-Clause License (permissive)")
        print()
        sys.exit(1)
    else:
        print("✅ No GPL licenses detected in checked files.")
        sys.exit(0)


if __name__ == "__main__":
    main()

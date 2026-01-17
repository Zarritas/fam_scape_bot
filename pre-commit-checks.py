#!/usr/bin/env python3
"""
Pre-commit quality checks script.

This script runs Ruff linting and formatting checks on staged Python files.
Run this before committing to ensure code quality.

Usage:
    python pre-commit-checks.py
    # or just run it from the project root
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, capture_output=True, text=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=text,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Main quality check logic."""
    print("🔍 Running pre-commit quality checks...", file=sys.stderr)

    # Check if we're in a git repository
    success, _, _ = run_command("git rev-parse --git-dir")
    if not success:
        print("❌ Error: Not in a git repository", file=sys.stderr)
        return 1

    # Check if Ruff is available
    ruff_available, _, _ = run_command("ruff --version")
    if not ruff_available:
        print("⚠️  Warning: ruff is not installed. Skipping quality checks.", file=sys.stderr)
        print("   Install ruff with: pip install ruff", file=sys.stderr)
        print("   Or run: pip install -r requirements-dev.txt", file=sys.stderr)
        return 0

    # Get list of staged Python files
    success, stdout, _ = run_command("git diff --cached --name-only --diff-filter=ACM")
    if not success:
        print("❌ Error: Could not get staged files from git", file=sys.stderr)
        return 1

    staged_files = [f for f in stdout.strip().split('\n') if f.strip() and f.endswith('.py')]

    if not staged_files:
        print("ℹ️  No Python files staged for commit. Skipping checks.", file=sys.stderr)
        return 0

    print("📁 Checking staged Python files:", file=sys.stderr)
    for file in staged_files:
        print(f"   {file}", file=sys.stderr)
    print(file=sys.stderr)

    # Convert to space-separated string for ruff
    files_str = ' '.join(f'"{f}"' for f in staged_files)

    # Run Ruff format check
    print("🎨 Checking code formatting...", file=sys.stderr)
    success, _, stderr = run_command(f"ruff format --check --quiet {files_str}")
    if not success:
        print(file=sys.stderr)
        print("❌ Code formatting issues found!", file=sys.stderr)
        print("Run 'ruff format' to fix formatting issues, then stage the changes.", file=sys.stderr)
        print(file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  ruff format .                    # Format all files", file=sys.stderr)
        print("  ruff format --check .           # Check formatting without fixing", file=sys.stderr)
        print("  git add .                       # Stage the formatted files", file=sys.stderr)
        if stderr:
            print(file=sys.stderr)
            print("Details:", file=sys.stderr)
            print(stderr, file=sys.stderr)
        return 1

    # Run Ruff linting check
    print("🔍 Running linting checks...", file=sys.stderr)
    success, _, stderr = run_command(f"ruff check --quiet {files_str}")
    if not success:
        print(file=sys.stderr)
        print("❌ Linting issues found!", file=sys.stderr)
        print("Fix the issues manually or run 'ruff check --fix' to auto-fix what can be fixed.", file=sys.stderr)
        print(file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  ruff check .                    # Check all files", file=sys.stderr)
        print("  ruff check --fix .             # Auto-fix issues", file=sys.stderr)
        print("  git add .                      # Stage the fixed files", file=sys.stderr)
        if stderr:
            print(file=sys.stderr)
            print("Details:", file=sys.stderr)
            print(stderr, file=sys.stderr)
        return 1

    print("✅ All quality checks passed! Safe to commit.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
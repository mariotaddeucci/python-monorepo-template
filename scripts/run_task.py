"""Monorepo task dispatcher with progress reporting.

Scans packages for taskipy tasks and runs them with a tqdm progress bar.

Usage (from repo root):
    uv run python scripts/run_task.py <task> [package]

Examples:
    uv run python scripts/run_task.py test              # runs 'test' in all packages that define it
    uv run python scripts/run_task.py test core          # runs 'test' only in packages matching 'core'
    uv run python scripts/run_task.py lint
    uv run python scripts/run_task.py autofix
"""

import subprocess
import sys
import tomllib
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = ROOT / "packages"

# ANSI colors
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


def find_packages_with_task(task: str) -> list[Path]:
    """Find all packages that define a given taskipy task."""
    matches: list[Path] = []
    for pyproject_path in sorted(PACKAGES_DIR.glob("*/pyproject.toml")):
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        if task in data.get("tool", {}).get("taskipy", {}).get("tasks", {}):
            matches.append(pyproject_path.parent)
    return matches


def filter_packages(packages: list[Path], target: str) -> list[Path]:
    """Filter packages by a substring match on the directory name."""
    matched = [p for p in packages if target in p.name]
    if not matched:
        print(f"{RED}No package matching '{target}' found.{RESET}")
        print(f"Available: {', '.join(p.name for p in packages)}")
        sys.exit(1)
    return matched


def run_task_in_package(task: str, package_dir: Path) -> tuple[bool, str, str]:
    """Run a taskipy task in a package directory. Returns (success, stdout, stderr)."""
    result = subprocess.run(
        ["uv", "run", "--directory", str(package_dir), "task", task],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout, result.stderr


def run_task(task: str, target: str | None) -> int:
    """Run a task across packages with progress bar."""
    all_packages = find_packages_with_task(task)
    if not all_packages:
        print(f"{RED}No packages define task '{task}'.{RESET}")
        return 1

    packages = filter_packages(all_packages, target) if target else all_packages

    print(f"\n{BOLD}Running '{task}' across {len(packages)} package(s){RESET}\n")

    results: dict[str, tuple[bool, str, str]] = {}
    failed: list[str] = []

    progress = tqdm(packages, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=80)
    for pkg in progress:
        progress.set_description(f"  {pkg.name}")
        success, stdout, stderr = run_task_in_package(task, pkg)
        results[pkg.name] = (success, stdout, stderr)
        if not success:
            failed.append(pkg.name)

    # Summary
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{BOLD}Results for '{task}':{RESET}\n")

    for name, (success, stdout, stderr) in results.items():
        icon = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
        print(f"  [{icon}] {name}")
        if not success:
            output = (stderr or stdout).strip()
            if output:
                for line in output.splitlines()[-10:]:
                    print(f"         {line}")
            print()

    passed = len(packages) - len(failed)
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"  {GREEN}{passed} passed{RESET}, {RED}{len(failed)} failed{RESET} out of {len(packages)} packages\n")

    return 1 if failed else 0


def main() -> None:
    """Entry point."""
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} <task> [package]")
        print("\nAvailable tasks (vary by package): test, lint, autofix, format, docs")
        sys.exit(1)

    task_name = args[0]
    target_filter = args[1] if len(args) > 1 else None
    sys.exit(run_task(task_name, target_filter))


if __name__ == "__main__":
    main()

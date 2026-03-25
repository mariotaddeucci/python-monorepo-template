"""
Monorepo task dispatcher.

Usage (from repo root):
    uv run task <task> [package]

Examples:
    uv run task test              # runs in all packages
    uv run task test core         # runs only in packages/core
    uv run task lint app
"""

import subprocess
import sys
import tomllib
from pathlib import Path


def find_packages_with_task(root: Path, task: str) -> list[Path]:
    packages_dir = root / "packages"
    matches: list[Path] = []
    for pyproject_path in sorted(packages_dir.glob("*/pyproject.toml")):
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        if task in data.get("tool", {}).get("taskipy", {}).get("tasks", {}):
            matches.append(pyproject_path.parent)
    return matches


def run_task(task: str, target: str | None) -> int:
    root = Path(__file__).parent.parent

    if target:
        pkg = root / "packages" / target
        if not pkg.is_dir():
            print(f"Package '{target}' not found in packages/.")
            return 1
        packages = [pkg]
    else:
        packages = find_packages_with_task(root, task)
        if not packages:
            print(f"No packages define task '{task}'.")
            return 1

    failed = []
    for pkg in packages:
        result = subprocess.run(
            ["uv", "run", "--directory", str(pkg), "task", task],
            cwd=root,
        )
        if result.returncode != 0:
            failed.append(pkg.name)

    if failed:
        print(f"\nFailed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} <task> [package]")
        sys.exit(1)
    sys.exit(run_task(args[0], args[1] if len(args) > 1 else None))

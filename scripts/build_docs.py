"""Build or serve documentation for the monorepo.

Usage:
    uv run python scripts/build_docs.py build    # Build all docs (root + packages)
    uv run python scripts/build_docs.py serve    # Build packages, then serve root portal
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES_DIR = ROOT / "packages"
SITE_DIR = ROOT / "site"


def find_packages() -> list[Path]:
    """Find all packages that have a mkdocs.yml file."""
    return sorted(p.parent for p in PACKAGES_DIR.glob("*/mkdocs.yml"))


def build_root() -> None:
    """Build the root documentation site."""
    print("Building root documentation...")
    subprocess.run(
        ["uv", "run", "mkdocs", "build", "--config-file", str(ROOT / "mkdocs.yml")],
        cwd=str(ROOT),
        check=True,
    )


def build_package(package_dir: Path) -> None:
    """Build documentation for a single package."""
    print(f"Building docs for {package_dir.name}...")
    subprocess.run(
        ["uv", "run", "mkdocs", "build"],
        cwd=str(package_dir),
        check=True,
    )


def build_all() -> None:
    """Build all documentation sites."""
    build_root()
    for package_dir in find_packages():
        build_package(package_dir)
    print(f"\nAll docs built successfully in {SITE_DIR}/")


def serve_root() -> None:
    """Start the MkDocs dev server for the root portal."""
    subprocess.run(
        ["uv", "run", "mkdocs", "serve", "--config-file", str(ROOT / "mkdocs.yml")],
        cwd=str(ROOT),
        check=True,
    )


def serve() -> None:
    """Build all package docs, then serve the root portal."""
    packages = find_packages()
    for package_dir in packages:
        build_package(package_dir)
    print(f"\nAll {len(packages)} package docs built. Starting server for root portal...\n")
    print("Note: To serve a specific package individually, run:")
    print("  uv run --directory packages/<name> task docs\n")
    serve_root()


def main() -> None:
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/build_docs.py [build|serve]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "build":
        build_all()
    elif command == "serve":
        serve()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python scripts/build_docs.py [build|serve]")
        sys.exit(1)


if __name__ == "__main__":
    main()

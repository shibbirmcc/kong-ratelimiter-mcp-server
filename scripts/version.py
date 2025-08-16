#!/usr/bin/env python3
"""Version management script for Kong MCP Server."""

import re
import sys
from pathlib import Path


def get_current_version() -> str:
    """Get current version from __init__.py."""
    init_file = Path("src/kong_mcp_server/__init__.py")
    content = init_file.read_text()
    match = re.search(r'__version__ = "([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in __init__.py")
    return match.group(1)


def update_version(new_version: str) -> None:
    """Update version in __init__.py and pyproject.toml."""
    # Update __init__.py
    init_file = Path("src/kong_mcp_server/__init__.py")
    content = init_file.read_text()
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    init_file.write_text(content)
    
    # Update pyproject.toml
    pyproject_file = Path("pyproject.toml")
    content = pyproject_file.read_text()
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    pyproject_file.write_text(content)
    
    print(f"Version updated to {new_version}")


def main() -> None:
    """Main entry point for version management."""
    if len(sys.argv) == 1:
        print(f"Current version: {get_current_version()}")
    elif len(sys.argv) == 2:
        new_version = sys.argv[1]
        update_version(new_version)
    else:
        print("Usage: python scripts/version.py [new_version]")
        sys.exit(1)


if __name__ == "__main__":
    main()
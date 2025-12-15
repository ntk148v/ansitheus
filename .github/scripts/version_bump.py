#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from version_common import (  # noqa: E402
    REPO_ROOT,
    VersionUpdateError,
    get_current_version,
    update_references,
)

REPORT_PATH = REPO_ROOT / ".github" / "version-bump-report.md"


def build_report(role: str, current: str, new: str) -> None:
    lines = [
        "## Version Update Report",
        "",
        f"Run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
        f"- `{role}`: `{current}` → `{new}`",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update a single role to a new version."
    )
    parser.add_argument("--role", required=True, help="Role name to update")
    parser.add_argument("--new-version", required=True, help="New version to set")
    args = parser.parse_args()

    role = args.role
    new_version = args.new_version

    current_version = get_current_version(role)
    if current_version == new_version:
        print(f"::notice::{role} already at requested version {new_version}")
        return 0

    update_references(role, new_version)
    build_report(role, current_version, new_version)
    print(f"::notice::Updated {role} from {current_version} to {new_version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VersionUpdateError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise SystemExit(1)

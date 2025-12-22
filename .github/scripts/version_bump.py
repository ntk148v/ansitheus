#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from version_common import (  # noqa: E402
    VersionUpdateError,
    get_current_version,
    update_references,
)


def build_report(role: str, current: str, new: str, repo: str) -> None:
    lines = [
        f"The upstream [{role}]({repo}): `{current}` → `{new}`!",
        "",
        "This automated PR updates code to bring new version into repository."
    ]
    Path(f"/tmp/version-bump-report-{role}-{new}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update a single role to a new version."
    )
    parser.add_argument("--role", required=True, help="Role name to update")
    parser.add_argument("--new-version", required=True, help="New version to set")
    parser.add_argument("--repo", required=True, help="Repository URL")
    args = parser.parse_args()

    role = args.role
    new_version = args.new_version
    repo = args.repo

    current_version = get_current_version(role)
    if current_version == new_version:
        print(f"::notice::{role} already at requested version {new_version}")
        return 0

    update_references(role, new_version)
    build_report(role, current_version, new_version, repo)
    print(f"::notice::Updated {role} from {current_version} to {new_version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VersionUpdateError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise SystemExit(1)

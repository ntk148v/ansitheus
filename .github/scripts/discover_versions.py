#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from version_common import (  # noqa: E402
    VersionUpdateError,
    discover_latest_version,
    get_current_version,
    load_role_metadata,
)


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise VersionUpdateError("GITHUB_TOKEN environment variable is required")

    roles = load_role_metadata()
    updates: List[dict] = []

    for meta in roles:
        try:
            current_version = get_current_version(meta.name)
        except VersionUpdateError as exc:
            print(f"::warning::{exc}", file=sys.stderr)
            continue

        latest = discover_latest_version(meta, token)
        if not latest:
            continue

        if latest == current_version:
            print(f"::notice::{meta.name} already at latest version {latest}")
            continue

        print(
            f"::notice::{meta.name} -> update available {current_version} -> {latest}"
        )
        updates.append(
            {
                "role": meta.name,
                "repo": meta.repo_path,
                "host": meta.host,
                "current_version": current_version,
                "new_version": latest,
            }
        )

    matrix = json.dumps(updates)
    print(matrix)

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"matrix={matrix}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VersionUpdateError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""
Automated component version updater.

For each role that defines `<role>_repo` in `ansible/roles/<role>/defaults/main.yml`,
this script:
1. Discovers the latest upstream release (GitHub hosts are supported today).
2. Compares it against the currently pinned version in the repository.
3. Updates every known reference when a newer release is available.
4. Produces a concise markdown report for the GitHub Action run.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLES_DIR = REPO_ROOT / "ansible" / "roles"
REPORT_PATH = REPO_ROOT / ".github" / "version-bump-report.md"

SIMPLE_TARGETS = [
    Path("ansible/group_vars/all.yml"),
    Path("etc/ansitheus/config.yml"),
    Path("docs/quickstart.md"),
]


class VersionUpdateError(Exception):
    """Custom wrapper for recoverable update errors."""


@dataclass
class RoleMetadata:
    name: str
    repo_raw: str
    host: str
    repo_path: str


def extract_scalar_value(content: str, key: str) -> Optional[str]:
    pattern = re.compile(
        rf'^\s*{re.escape(key)}:\s*(?P<value>.+)$',
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        return None
    value = match.group("value").strip()
    if not value:
        return None
    if "#" in value:
        value = value.split("#", 1)[0].rstrip()
    if (
        len(value) >= 2
        and value[0] in {"'", '"'}
        and value[-1] == value[0]
    ):
        value = value[1:-1]
    return value.strip()


def normalize_repo_reference(raw: str) -> Tuple[str, str]:
    if not raw:
        raise VersionUpdateError("Repository reference is empty")
    value = raw.strip()
    # Remove protocol prefixes
    if "://" in value:
        value = value.split("://", 1)[1]
    value = value.strip()
    if value.startswith("git@"):
        value = value.replace("git@", "", 1)
        host_part, _, remainder = value.partition(":")
    else:
        host_part, _, remainder = value.partition("/")
    host_part = host_part.strip().lower()
    remainder = remainder.strip().lstrip("/")
    if remainder.endswith(".git"):
        remainder = remainder[:-4]
    if not host_part or not remainder:
        raise VersionUpdateError(f"Invalid repository reference '{raw}'")

    host_map = {
        "github.com": "github",
    }
    host = host_map.get(host_part, host_part)
    return host, remainder


def load_role_metadata() -> List[RoleMetadata]:
    roles: List[RoleMetadata] = []
    if not ROLES_DIR.exists():
        return roles
    for role_dir in sorted(p for p in ROLES_DIR.iterdir() if p.is_dir()):
        defaults_path = role_dir / "defaults" / "main.yml"
        if not defaults_path.exists():
            continue
        content, exists = read_file(defaults_path)
        if not exists:
            continue
        role_name = role_dir.name
        repo_key = f"{role_name}_repo"
        repo_value = extract_scalar_value(content, repo_key)
        if not repo_value:
            continue
        try:
            host, repo_path = normalize_repo_reference(repo_value)
        except VersionUpdateError as exc:
            print(f"::warning::Skipping {role_name}: {exc}", file=sys.stderr)
            continue
        roles.append(
            RoleMetadata(
                name=role_name,
                repo_raw=repo_value,
                host=host,
                repo_path=repo_path,
            )
        )
    return roles


def fetch_latest_github_release(repo: str, token: str) -> Optional[str]:
    """Return the latest non-prerelease tag from GitHub releases."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {token}",
            "User-Agent": "ansitheus-version-bot",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:  # pragma: no cover - network failure
        print(f"::warning::Failed to pull release info for {repo}: {exc}", file=sys.stderr)
        return None
    except urllib.error.URLError as exc:  # pragma: no cover - network failure
        print(f"::warning::Network issue while calling GitHub for {repo}: {exc}", file=sys.stderr)
        return None

    tag_name = payload.get("tag_name")
    if not tag_name:
        print(f"::warning::Release payload for {repo} missing tag_name", file=sys.stderr)
        return None
    return tag_name.lstrip("v")


def discover_latest_version(role_meta: RoleMetadata, token: str) -> Optional[str]:
    if role_meta.host == "github":
        return fetch_latest_github_release(role_meta.repo_path, token)
    print(f"::warning::Unsupported githost '{role_meta.host}' for role {role_meta.name}", file=sys.stderr)
    return None


def read_file(path: Path) -> Tuple[str, bool]:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "", False
    return content, True


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def replace_simple_var(path: Path, key: str, new_value: str) -> bool:
    """
    Replace occurrences of `<key>: value` in YAML-like files while preserving
    indentation, quotes, and inline comments.
    """
    import re

    content, exists = read_file(path)
    if not exists:
        return False

    pattern = re.compile(
        rf'^(\s*{re.escape(key)}:\s*)(?P<quote>["\']?)(?P<value>[^\n#]+?)(?P=quote)'
        rf'(?P<suffix>\s*(?:#.*)?)$',
        re.MULTILINE,
    )
    changed = False

    def _repl(match: re.Match[str]) -> str:
        nonlocal changed
        current_value = match.group("value").strip()
        quote = match.group("quote")
        suffix = match.group("suffix") or ""
        # Normalise whitespace around the value
        if current_value == new_value:
            return match.group(0)
        changed = True
        return f"{match.group(1)}{quote}{new_value}{quote}{suffix}"

    updated = pattern.sub(_repl, content)
    if changed:
        write_file(path, updated)
    return changed


def replace_argument_spec_default(path: Path, key: str, new_value: str) -> bool:
    """
    Update the `default:` value that belongs to `<key>:` inside argument_specs files
    without destroying formatting or comments.
    """
    content, exists = read_file(path)
    if not exists:
        return False

    lines = content.splitlines()
    changed = False
    target_header = f"{key}:"
    inside_block = False
    block_indent = 0

    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped:
            continue
        current_indent = len(line) - len(stripped)

        if stripped.startswith(target_header):
            inside_block = True
            block_indent = current_indent
            continue

        if inside_block and current_indent <= block_indent and not stripped.startswith("default:"):
            inside_block = False

        if inside_block and stripped.startswith("default:"):
            prefix = line[:len(line) - len(stripped)]
            remainder = stripped[len("default:"):].strip()

            comment = ""
            if "#" in remainder:
                value_part, comment_part = remainder.split("#", 1)
                remainder = value_part.strip()
                comment = f" #{comment_part.strip()}" if comment_part.strip() else " #"

            quote = ""
            old_value = remainder
            if remainder.startswith(("'", '"')) and remainder.endswith(remainder[0]) and len(remainder) > 1:
                quote = remainder[0]
                old_value = remainder[1:-1]

            if old_value == new_value:
                inside_block = False
                continue

            lines[idx] = f"{prefix}default: {quote}{new_value}{quote}{comment}"
            changed = True
            inside_block = False

    if changed:
        ending = "\n" if content.endswith("\n") else ""
        write_file(path, "\n".join(lines) + ending)
    return changed


def get_current_version(role: str) -> str:
    defaults_path = REPO_ROOT / "ansible" / "roles" / role / "defaults" / "main.yml"
    key = f"{role}_version"
    content, exists = read_file(defaults_path)
    if not exists:
        raise VersionUpdateError(f"Defaults file missing for role '{role}'")

    pattern = re.compile(
        rf'^\s*{re.escape(key)}:\s*(?:["\']?)(?P<value>[^\s"#]+)',
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        raise VersionUpdateError(f"Unable to determine current version for '{role}'")
    return match.group("value").strip().strip('"').strip("'")


def update_references(role: str, new_version: str) -> None:
    key = f"{role}_version"
    files_to_update = set(SIMPLE_TARGETS)
    files_to_update.add(Path(f"ansible/roles/{role}/defaults/main.yml"))
    arg_spec_path = Path(f"ansible/roles/{role}/meta/argument_specs.yml")

    for relative_path in files_to_update:
        replace_simple_var(REPO_ROOT / relative_path, key, new_version)

    replace_argument_spec_default(REPO_ROOT / arg_spec_path, key, new_version)


def build_report(updates: List[Tuple[str, str, str]]) -> None:
    lines = [
        "## Version Update Report",
        "",
        f"Run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
    ]
    if updates:
        for role, old, new in updates:
            lines.append(f"- `{role}`: `{old}` → `{new}`")
    else:
        lines.append("No updates were required this run.")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise VersionUpdateError("GITHUB_TOKEN environment variable is required")

    roles = load_role_metadata()
    if not roles:
        print("::warning::No roles found with *_repo variable defined.")
        return 0

    updates: List[Tuple[str, str, str]] = []

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

        print(f"::notice::{meta.name} -> updating {current_version} to {latest}")
        update_references(meta.name, latest)
        updates.append((meta.name, current_version, latest))

    if updates:
        print(f"::notice::Updated {len(updates)} component(s).")
    else:
        print("::notice::No updates were necessary.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VersionUpdateError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise SystemExit(1)

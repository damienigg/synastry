#!/usr/bin/env python3
"""
Bump the version across VERSION.md and index.html.

Usage:
    python3 bump_version.py 10.4.0          # set explicit version
    python3 bump_version.py patch           # 10.3.0 → 10.3.1
    python3 bump_version.py minor           # 10.3.0 → 10.4.0
    python3 bump_version.py major           # 10.3.0 → 11.0.0
    python3 bump_version.py                 # show current version
"""

import re, sys, datetime
from pathlib import Path

ROOT = Path(__file__).parent
VERSION_MD = ROOT / 'VERSION.md'
INDEX_HTML = ROOT / 'index.html'


def read_current():
    text = VERSION_MD.read_text()
    m = re.search(r'\*\*(.+?)\*\*', text)
    if not m:
        raise ValueError("Cannot parse version from VERSION.md")
    return m.group(1)


def write_version_md(version):
    today = datetime.date.today().isoformat()
    VERSION_MD.write_text(f"# Version\n\n**{version}**\n\nReleased: {today}\n")


def write_index_html(version):
    text = INDEX_HTML.read_text()
    text = re.sub(
        r"const APP_VERSION='[^']*'",
        f"const APP_VERSION='{version}'",
        text,
    )
    INDEX_HTML.write_text(text)


def bump(current, kind):
    parts = list(map(int, current.split('.')))
    if kind == 'major':
        parts = [parts[0] + 1, 0, 0]
    elif kind == 'minor':
        parts = [parts[0], parts[1] + 1, 0]
    elif kind == 'patch':
        parts = [parts[0], parts[1], parts[2] + 1]
    return '.'.join(map(str, parts))


def main():
    current = read_current()

    if len(sys.argv) < 2:
        print(f"Current version: {current}")
        return

    arg = sys.argv[1]
    if arg in ('major', 'minor', 'patch'):
        new = bump(current, arg)
    else:
        new = arg

    write_version_md(new)
    write_index_html(new)
    print(f"{current} → {new}")
    print(f"  Updated: VERSION.md, index.html")
    print(f"  Remember to update CHANGELOG.md and test_structural.py version badge check")


if __name__ == '__main__':
    main()

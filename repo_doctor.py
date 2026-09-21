#!/usr/bin/env python3
"""repo-doctor: a tiny repository health checker."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".c", ".cc", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".sh", ".md", ".tex", ".yml", ".yaml", ".toml", ".json"
}
LANGUAGES = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".go": "Go",
    ".rs": "Rust",
    ".sh": "Shell",
    ".tex": "LaTeX",
}


def walk_files(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(current)
        for name in files:
            yield base / name


def count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
    except OSError:
        return 0


def scan_repository(root: Path) -> dict:
    files = list(walk_files(root))
    language_lines: dict[str, int] = {}
    todo_count = 0
    large_files: list[tuple[str, int]] = []

    for path in files:
        rel = path.relative_to(root)
        try:
            size = path.stat().st_size
        except OSError:
            continue

        if size >= 5 * 1024 * 1024:
            large_files.append((str(rel), size))

        suffix = path.suffix.lower()
        if suffix in LANGUAGES:
            language_lines[LANGUAGES[suffix]] = language_lines.get(LANGUAGES[suffix], 0) + count_lines(path)

        if suffix in TEXT_EXTENSIONS and size <= 2 * 1024 * 1024:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                todo_count += text.count("TODO") + text.count("FIXME")
            except OSError:
                pass

    checks = {
        "README": any((root / name).exists() for name in ["README.md", "README.rst", "README.txt"]),
        "LICENSE": any((root / name).exists() for name in ["LICENSE", "LICENSE.md", "COPYING"]),
        ".gitignore": (root / ".gitignore").exists(),
        "tests": any((root / name).exists() for name in ["tests", "test"]),
        "CI": (root / ".github" / "workflows").exists(),
        "package config": any((root / name).exists() for name in ["pyproject.toml", "setup.py", "package.json", "Cargo.toml", "go.mod"]),
    }

    score = round(100 * sum(checks.values()) / len(checks))
    return {
        "root": root,
        "file_count": len(files),
        "checks": checks,
        "score": score,
        "languages": language_lines,
        "todos": todo_count,
        "large_files": sorted(large_files, key=lambda x: x[1], reverse=True),
    }


def human_size(num: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(num)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{num} B"


def render_report(report: dict) -> str:
    lines = [
        "Repo Doctor",
        "===========",
        f"Path: {report['root']}",
        f"Health score: {report['score']}/100",
        f"Files scanned: {report['file_count']}",
        "",
        "Repository essentials:",
    ]

    for name, ok in report["checks"].items():
        lines.append(f"  {'[OK]' if ok else '[!!]'} {name}")

    lines.extend(["", "Languages by lines:"])
    if report["languages"]:
        for lang, loc in sorted(report["languages"].items(), key=lambda item: item[1], reverse=True):
            lines.append(f"  {lang:<12} {loc:>6}")
    else:
        lines.append("  No recognized source files found.")

    lines.extend(["", f"TODO/FIXME markers: {report['todos']}"])

    if report["large_files"]:
        lines.append("",)
        lines.append("Large files (>= 5 MB):")
        for path, size in report["large_files"][:10]:
            lines.append(f"  {human_size(size):>9}  {path}")
    else:
        lines.append("Large files: none >= 5 MB")

    missing = [name for name, ok in report["checks"].items() if not ok]
    lines.append("")
    if missing:
        lines.append("Suggestions: add " + ", ".join(missing) + ".")
    else:
        lines.append("Nice! Your repository has all basic hygiene items.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quickly check the health of a Git repository.")
    parser.add_argument("path", nargs="?", default=".", help="Repository path (default: current directory)")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    print(render_report(scan_repository(root)))


if __name__ == "__main__":
    main()

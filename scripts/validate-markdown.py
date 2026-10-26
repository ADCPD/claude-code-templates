#!/usr/bin/env python3
"""
Validate markdown files for common parsing errors.

Checks for:
- HTML comments breaking tables
- Unclosed code blocks (``` and ~~~ fences, CommonMark closing rules)
- Missing table separator (delimiter) rows
- Delimiter rows whose column count differs from the header (table won't render)
- Inconsistent column counts in table data rows
- Files that cannot be read as UTF-8

Usage:
    python scripts/validate-markdown.py [PATH ...] [--path PATH] [--check]
                                        [--format {text,json,github}]

Exit codes:
    0  no issues
    1  issues found
    2  usage error (e.g. path does not exist)
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
import re
import sys

MARKDOWN_SUFFIXES = {".md", ".markdown"}
EXCLUDED_DIRS = {"node_modules", "__pycache__", "venv", ".venv"}

FENCE_OPEN_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
DELIMITER_CELL_RE = re.compile(r"^:?-+:?$")


class IssueType(StrEnum):
    HTML_IN_TABLE = "html-in-table"
    UNCLOSED_CODE_BLOCK = "unclosed-code-block"
    MISSING_SEPARATOR = "missing-table-separator"
    DELIMITER_MISMATCH = "delimiter-column-mismatch"
    COLUMN_MISMATCH = "column-count-mismatch"
    UNREADABLE_FILE = "unreadable-file"


@dataclass(frozen=True)
class MarkdownIssue:
    file: Path
    line: int
    issue_type: IssueType
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: [{self.issue_type}] {self.message}"

    def to_dict(self) -> dict[str, object]:
        return {
            "file": str(self.file),
            "line": self.line,
            "type": str(self.issue_type),
            "message": self.message,
        }


@dataclass(frozen=True)
class Fence:
    char: str
    length: int
    line: int


# --------------------------------------------------------------------------- #
# Line helpers
# --------------------------------------------------------------------------- #


def leading_spaces(line: str) -> int:
    """Number of leading spaces (tabs count as 4, as in CommonMark)."""
    expanded = line.expandtabs(4)
    return len(expanded) - len(expanded.lstrip(" "))


def open_fence(line: str, line_no: int) -> Fence | None:
    """Return a Fence if the line opens a fenced code block."""
    match = FENCE_OPEN_RE.match(line.rstrip("\n"))
    if not match:
        return None
    fence = match.group("fence")
    # A backtick fence's info string may not contain backticks.
    if fence[0] == "`" and "`" in match.group("info"):
        return None
    return Fence(char=fence[0], length=len(fence), line=line_no)


def closes_fence(line: str, fence: Fence) -> bool:
    """A closing fence uses the same char, is at least as long, and has nothing after it."""
    if leading_spaces(line) > 3:
        return False
    stripped = line.strip()
    run = len(stripped) - len(stripped.lstrip(fence.char))
    return run >= fence.length and stripped == fence.char * run


def split_cells(line: str) -> list[str]:
    """Split a table row into cells, honouring escaped pipes and optional outer pipes."""
    s = line.strip()
    cells: list[str] = []
    buf: list[str] = []
    escaped = False
    ends_with_pipe = False

    for ch in s:
        ends_with_pipe = False
        if escaped:
            buf.append(ch)
            escaped = False
        elif ch == "\\":
            buf.append(ch)
            escaped = True
        elif ch == "|":
            cells.append("".join(buf))
            buf = []
            ends_with_pipe = True
        else:
            buf.append(ch)
    cells.append("".join(buf))

    if s.startswith("|"):
        cells = cells[1:]
    if ends_with_pipe and cells:
        cells = cells[:-1]
    return [c.strip() for c in cells]


def has_unescaped_pipe(line: str) -> bool:
    return len(split_cells(line)) > 1 or line.strip().startswith("|")


def is_blank(line: str) -> bool:
    return not line.strip()


def is_delimiter_row(line: str) -> bool:
    """A valid GFM delimiter row, e.g. `| --- | :-: |` or `---|---`."""
    if "|" not in line or leading_spaces(line) > 3:
        return False
    cells = split_cells(line)
    return bool(cells) and all(DELIMITER_CELL_RE.match(c) for c in cells)


def is_pipe_row(line: str) -> bool:
    """A line that explicitly looks like a table row (starts with a pipe)."""
    stripped = line.strip()
    return stripped.startswith("|") and len(stripped) > 1 and leading_spaces(line) <= 3


def has_html_comment(line: str) -> bool:
    return "<!--" in line


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #


def starts_table(lines: list[str], i: int) -> bool:
    """A table starts on a pipe-prefixed row, or on any piped line followed by a delimiter row."""
    line = lines[i]
    if leading_spaces(line) > 3 or is_delimiter_row(line):
        return False
    if is_pipe_row(line):
        return True
    return i + 1 < len(lines) and has_unescaped_pipe(line) and is_delimiter_row(lines[i + 1])


def check_table(path: Path, lines: list[str], start: int, issues: list[MarkdownIssue]) -> int:
    """Validate the table starting at `start`. Returns the index of the first line after it."""
    n = len(lines)
    header_line = start + 1
    header_cols = len(split_cells(lines[start]))
    j = start + 1

    # HTML comment between header and delimiter row.
    if j < n and has_html_comment(lines[j]):
        issues.append(
            MarkdownIssue(path, j + 1, IssueType.HTML_IN_TABLE, "HTML comment interrupts table structure")
        )
        j += 1
        while j < n and is_pipe_row(lines[j]):
            j += 1
        return j

    # Missing delimiter row: report once, and consume the rest of the broken table
    # so each following row is not reported again.
    if j >= n or not is_delimiter_row(lines[j]):
        issues.append(
            MarkdownIssue(
                path,
                header_line,
                IssueType.MISSING_SEPARATOR,
                f"Table header at line {header_line} is not followed by a separator row",
            )
        )
        while j < n and is_pipe_row(lines[j]):
            j += 1
        return j

    # Delimiter row must have exactly as many cells as the header, or GFM won't render it.
    delimiter_cols = len(split_cells(lines[j]))
    if delimiter_cols != header_cols:
        issues.append(
            MarkdownIssue(
                path,
                j + 1,
                IssueType.DELIMITER_MISMATCH,
                f"Separator row has {delimiter_cols} columns but header has {header_cols} "
                "(table will not render)",
            )
        )

    # Data rows.
    j += 1
    while j < n:
        row = lines[j]
        if is_blank(row) or open_fence(row, j + 1):
            break

        if has_html_comment(row):
            # A comment right after a table just ends it; it only breaks the
            # table when more rows follow it.
            if j + 1 < n and is_pipe_row(lines[j + 1]):
                issues.append(
                    MarkdownIssue(path, j + 1, IssueType.HTML_IN_TABLE, "HTML comment interrupts table structure")
                )
                j += 1
                continue
            if not has_unescaped_pipe(row):
                break

        if not has_unescaped_pipe(row):
            break

        cols = len(split_cells(row))
        if cols != header_cols:
            issues.append(
                MarkdownIssue(
                    path,
                    j + 1,
                    IssueType.COLUMN_MISMATCH,
                    f"Expected {header_cols} columns, got {cols}",
                )
            )
        j += 1

    return j


def validate_lines(path: Path, lines: list[str]) -> list[MarkdownIssue]:
    """Validate markdown content in a single pass."""
    issues: list[MarkdownIssue] = []
    fence: Fence | None = None
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        if fence is not None:
            if closes_fence(line, fence):
                fence = None
            i += 1
            continue

        opened = open_fence(line, i + 1)
        if opened is not None:
            fence = opened
            i += 1
            continue

        if starts_table(lines, i):
            i = check_table(path, lines, i, issues)
            continue

        i += 1

    if fence is not None:
        issues.append(
            MarkdownIssue(
                path,
                fence.line,
                IssueType.UNCLOSED_CODE_BLOCK,
                f"Code block ({fence.char * fence.length}) opened at line {fence.line} is never closed",
            )
        )

    return issues


def validate_file(path: Path) -> list[MarkdownIssue]:
    """Validate a single markdown file for issues."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [MarkdownIssue(path, 0, IssueType.UNREADABLE_FILE, f"Cannot read file: {exc}")]
    return validate_lines(path, text.splitlines())


def iter_markdown_files(root: Path) -> Iterator[Path]:
    """Yield markdown files under root, skipping hidden and vendored directories."""
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*")):
        rel_parts = path.relative_to(root).parts[:-1]
        if any(part.startswith(".") or part in EXCLUDED_DIRS for part in rel_parts):
            continue
        if path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES:
            yield path


def validate_paths(paths: Iterable[Path]) -> tuple[list[MarkdownIssue], int]:
    """Validate every markdown file under the given paths. Returns (issues, files_checked)."""
    issues: list[MarkdownIssue] = []
    seen: set[Path] = set()
    for root in paths:
        for md_file in iter_markdown_files(root):
            resolved = md_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            issues.extend(validate_file(md_file))
    return issues, len(seen)


# Kept for backwards compatibility with code importing this module.
def validate_directory(root: Path) -> list[MarkdownIssue]:
    return validate_paths([root])[0]


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def print_text(issues: list[MarkdownIssue], files_checked: int, compact: bool) -> None:
    if compact:
        for issue in issues:
            print(issue)
        return

    if not issues:
        print(f"No markdown issues found ({files_checked} files checked).")
        return

    by_type: dict[IssueType, list[MarkdownIssue]] = {}
    for issue in issues:
        by_type.setdefault(issue.issue_type, []).append(issue)

    for issue_type, type_issues in sorted(by_type.items()):
        print(f"\n{issue_type.upper()} ({len(type_issues)} issues):")
        for issue in type_issues:
            print(f"  {issue}")

    print(f"\nTotal: {len(issues)} issues found in {files_checked} files checked")


def print_github(issues: list[MarkdownIssue]) -> None:
    """GitHub Actions workflow annotations."""
    for issue in issues:
        message = issue.message.replace("%", "%25").replace("\n", "%0A")
        print(f"::error file={issue.file},line={max(issue.line, 1)},title={issue.issue_type}::{message}")


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Returns exit code."""
    parser = argparse.ArgumentParser(description="Validate markdown files for parsing errors")
    parser.add_argument("paths", nargs="*", type=Path, help="Files or directories to validate")
    parser.add_argument(
        "--path",
        type=Path,
        action="append",
        default=[],
        help="Path to validate (repeatable; default: skills/)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: print one line per issue, no headings or summary",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "github"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args(argv)
    paths: list[Path] = [*args.paths, *args.path] or [Path("skills")]

    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"Error: Path does not exist: {p}", file=sys.stderr)
        return 2

    issues, files_checked = validate_paths(paths)
    issues.sort(key=lambda i: (str(i.file), i.line))

    if args.format == "json":
        print(json.dumps([i.to_dict() for i in issues], indent=2))
    elif args.format == "github":
        print_github(issues)
    else:
        print_text(issues, files_checked, compact=args.check)

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())

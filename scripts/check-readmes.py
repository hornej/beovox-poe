#!/usr/bin/env python3
from __future__ import annotations

import bisect
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import unquote


FENCE_RE = re.compile(r"^(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")
WIKI_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}
SKIP_DIRS = {".git"}


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    message: str


class HeadingIndex:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.anchors = self._build_anchor_index(path)

    @staticmethod
    def _slugify(heading_text: str) -> str:
        text = heading_text.strip().lower()
        text = re.sub(r"[ \t]+#+[ \t]*$", "", text)
        text = re.sub(r"[^a-z0-9 _-]", "", text)
        return text.replace(" ", "-")

    def _build_anchor_index(self, path: Path) -> set[str]:
        anchors: set[str] = set()
        seen: dict[str, int] = {}
        in_fence = False

        for line in path.read_text(encoding="utf-8").splitlines():
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            match = HEADING_RE.match(line)
            if not match:
                continue

            base = self._slugify(match.group(2))
            count = seen.get(base, 0)
            seen[base] = count + 1
            slug = base if count == 0 else f"{base}-{count}"
            anchors.add(f"#{slug}")

        return anchors

    def has_anchor(self, anchor: str) -> bool:
        return anchor in self.anchors


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def iter_readmes(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("README*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def find_closing_bracket(text: str, open_index: int) -> int:
    depth = 0
    index = open_index

    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return index
        index += 1

    return -1


def parse_link_target(text: str, start_index: int) -> tuple[str | None, int]:
    if start_index >= len(text):
        return None, -1

    if text[start_index] == "<":
        index = start_index + 1
        while index < len(text):
            if text[index] == ">" and index + 1 < len(text) and text[index + 1] == ")":
                return text[start_index + 1 : index], index + 1
            index += 1
        return None, -1

    depth = 0
    index = start_index

    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                return text[start_index:index].strip(), index
            depth -= 1
        index += 1

    return None, -1


def extract_markdown_links(line: str) -> list[tuple[int, str]]:
    links: list[tuple[int, str]] = []
    index = 0

    while index < len(line):
        bracket_index = line.find("[", index)
        if bracket_index == -1:
            break

        if bracket_index > 0 and line[bracket_index - 1] == "\\":
            index = bracket_index + 1
            continue

        label_end = find_closing_bracket(line, bracket_index)
        if label_end == -1 or label_end + 1 >= len(line) or line[label_end + 1] != "(":
            index = bracket_index + 1
            continue

        target, target_end = parse_link_target(line, label_end + 2)
        if target is None or target_end == -1:
            index = bracket_index + 1
            continue

        link_column = bracket_index if bracket_index == 0 or line[bracket_index - 1] != "!" else bracket_index - 1
        links.append((link_column + 1, target))
        index = target_end + 1

    return links


def normalize_relative_target(source_path: Path, target: str, root: Path) -> tuple[list[str], str] | None:
    normalized = unquote(target.strip())
    if normalized.startswith("/"):
        return None

    source_rel = source_path.relative_to(root)
    base_parts = list(source_rel.parent.parts)
    target_parts = PurePosixPath(normalized.replace("\\", "/")).parts

    parts = base_parts[:]
    for part in target_parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)

    return parts, "/".join(parts)


def resolve_exact_path(root: Path, relative_parts: list[str]) -> Path | None:
    current = root
    for part in relative_parts:
        if not current.is_dir():
            return None
        children = {child.name: child for child in current.iterdir()}
        if part not in children:
            return None
        current = children[part]
    return current


def split_target_anchor(target: str) -> tuple[str, str | None]:
    if "#" not in target:
        return target, None
    path_part, anchor = target.split("#", 1)
    return path_part, f"#{anchor}"


def validate_anchor(
    heading_cache: dict[Path, HeadingIndex],
    target_path: Path,
    anchor: str,
    source_path: Path,
    line_number: int,
) -> Issue | None:
    heading_index = heading_cache.get(target_path)
    if heading_index is None:
        heading_index = HeadingIndex(target_path)
        heading_cache[target_path] = heading_index

    if heading_index.has_anchor(anchor):
        return None

    return Issue(source_path, line_number, f"missing anchor '{anchor}' in {target_path.relative_to(repo_root()).as_posix()}")


def validate_link_target(
    heading_cache: dict[Path, HeadingIndex],
    source_path: Path,
    line_number: int,
    target: str,
) -> list[Issue]:
    issues: list[Issue] = []
    cleaned = target.strip()
    if not cleaned:
        issues.append(Issue(source_path, line_number, "empty link target"))
        return issues

    if cleaned.startswith(("http://", "https://", "mailto:")):
        return issues

    if cleaned.startswith("#"):
        issue = validate_anchor(heading_cache, source_path, cleaned, source_path, line_number)
        if issue:
            issues.append(issue)
        return issues

    path_part, anchor = split_target_anchor(cleaned)
    normalized = normalize_relative_target(source_path, path_part.strip("<>"), repo_root())
    if normalized is None:
        issues.append(Issue(source_path, line_number, f"unsupported absolute or out-of-repo path '{cleaned}'"))
        return issues

    relative_parts, relative_display = normalized
    resolved_path = resolve_exact_path(repo_root(), relative_parts)
    if resolved_path is None:
        issues.append(Issue(source_path, line_number, f"missing path '{relative_display}'"))
        return issues

    if anchor:
        if resolved_path.is_dir():
            issues.append(Issue(source_path, line_number, f"anchor '{anchor}' targets directory '{relative_display}'"))
            return issues

        if resolved_path.suffix.lower() not in MARKDOWN_EXTENSIONS:
            issues.append(Issue(source_path, line_number, f"anchor '{anchor}' targets non-Markdown file '{relative_display}'"))
            return issues

        issue = validate_anchor(heading_cache, resolved_path, anchor, source_path, line_number)
        if issue:
            issues.append(issue)

    return issues


def validate_readme(path: Path, heading_cache: dict[Path, HeadingIndex]) -> list[Issue]:
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8")
    in_fence = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in WIKI_RE.finditer(line):
            issues.append(Issue(path, line_number, f"wiki-style link/embed is not GitHub-friendly: {match.group(0)}"))

        for _, target in extract_markdown_links(line):
            issues.extend(validate_link_target(heading_cache, path, line_number, target))

    return issues


def main() -> int:
    root = repo_root()
    heading_cache: dict[Path, HeadingIndex] = {}
    issues: list[Issue] = []
    readmes = list(iter_readmes(root))

    for readme in readmes:
        issues.extend(validate_readme(readme, heading_cache))

    if issues:
        for issue in sorted(issues, key=lambda item: (item.path.as_posix(), item.line, item.message)):
            rel_path = issue.path.relative_to(root).as_posix()
            print(f"{rel_path}:{issue.line}: {issue.message}", file=sys.stderr)
        print(
            f"README validation failed: {len(issues)} issue(s) across {len(readmes)} README file(s).",
            file=sys.stderr,
        )
        return 1

    print(f"README validation passed: {len(readmes)} README file(s) checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

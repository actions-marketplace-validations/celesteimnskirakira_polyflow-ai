"""Build the {{context}} string from inject_cwd and inject_files config."""
from __future__ import annotations
import os
from pathlib import Path

_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache"}
_CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".cs", ".rb", ".php", ".swift", ".kt",
    ".yaml", ".yml", ".json", ".toml", ".md", ".sql", ".sh",
}


def _parse_size(size_str: str) -> int:
    """Parse '50kb', '1mb', '4096' into bytes."""
    s = size_str.strip().lower()
    if s.endswith("kb"):
        return int(s[:-2]) * 1024
    if s.endswith("mb"):
        return int(s[:-2]) * 1024 * 1024
    return int(s)


def build_context(
    inject_cwd: bool = False,
    inject_files: list[str] | None = None,
    max_file_size: str = "50kb",
    cwd: Path | None = None,
) -> str:
    """Build context string to inject into {{context}} template variable."""
    if not inject_cwd and not inject_files:
        return ""

    root = cwd or Path.cwd()
    max_bytes = _parse_size(max_file_size)
    parts: list[str] = []

    if inject_cwd:
        parts.append(_build_cwd_tree(root, max_bytes))

    if inject_files:
        for pattern in inject_files:
            for filepath in sorted(root.glob(pattern)):
                if filepath.is_file():
                    parts.append(_read_file(filepath, max_bytes))

    return "\n\n".join(p for p in parts if p)


def _build_cwd_tree(root: Path, max_bytes: int) -> str:
    """Build a directory tree + file content summary."""
    lines = [f"## Project: {root.name}\n"]

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in _SKIP_DIRS]
        rel = Path(dirpath).relative_to(root)
        depth = len(rel.parts)
        indent = "  " * depth
        folder = rel.parts[-1] if rel.parts else "."
        lines.append(f"{indent}{folder}/")

        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if fpath.suffix in _CODE_EXTENSIONS:
                size = fpath.stat().st_size
                size_str = f"{size // 1024}kb" if size >= 1024 else f"{size}b"
                lines.append(f"{indent}  {fname} ({size_str})")

    return "\n".join(lines)


def _read_file(filepath: Path, max_bytes: int) -> str:
    """Read a file up to max_bytes."""
    size = filepath.stat().st_size
    if size > max_bytes:
        content = filepath.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
        return f"## {filepath.name} (truncated at {max_bytes // 1024}kb)\n```\n{content}\n```"
    content = filepath.read_text(errors="replace")
    return f"## {filepath.name}\n```\n{content}\n```"

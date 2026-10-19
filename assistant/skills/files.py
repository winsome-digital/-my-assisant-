"""Real file search across the user's home directory.

Walks the home folder with sensible skips (hidden dirs, caches, VCS metadata,
huge dependency trees), a scan cap, and a time deadline so it always returns
promptly. Never follows symlinks.
"""

import os
import re
import time
from pathlib import Path

from .. import config
from .base import Skill


def _iter_files(roots, deadline):
    """Yield file Paths under roots, respecting skips, caps, and the deadline."""
    stack = [Path(r) for r in roots]
    scanned = 0
    while stack:
        if time.monotonic() > deadline or scanned >= config.MAX_FILES_SCANNED:
            return
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except (PermissionError, FileNotFoundError, OSError):
            continue
        for entry in entries:
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    name = entry.name
                    if name.startswith(".") or name in config.SKIP_DIR_NAMES:
                        continue
                    stack.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    scanned += 1
                    yield Path(entry.path)
            except OSError:
                continue


class FindFileSkill(Skill):
    name = "find_file"
    description = "Find files by name on this computer."
    examples = [
        "find file report",
        "find my budget spreadsheet",
        "locate vacation photo",
    ]

    def run(self, args):
        query = (args.get("query") or "").strip().lower()
        if not query:
            return "Tell me the file name to search for."
        words = [w for w in re.sub(r"[^\w\s]", " ", query).split() if w]
        if not words:
            return "Tell me the file name to search for."

        deadline = time.monotonic() + config.MAX_SEARCH_SECONDS
        scored = []
        for path in _iter_files(config.SEARCH_ROOTS, deadline):
            fname = path.name.lower()
            score = sum(1 for w in words if w in fname)
            if score:
                scored.append((score, str(path)))

        if not scored:
            return f"I couldn't find any file matching '{query}'."

        scored.sort(key=lambda item: (-item[0], item[1]))
        top = scored[: config.MAX_RESULTS]
        lines = [f"{i + 1}. {p}" for i, (_, p) in enumerate(top)]
        extra = (
            f" (showing {len(top)} of {len(scored)} matches)"
            if len(scored) > len(top)
            else ""
        )
        noun = "match" if len(scored) == 1 else "matches"
        return f"Found {len(scored)} {noun}{extra}:\n" + "\n".join(lines)

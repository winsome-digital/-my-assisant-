"""Timestamped notes stored as plain text in the user's home folder.

No cloud, no account, no database — ~/assistant-notes/notes.txt.
"""

from datetime import datetime

from .. import config
from .base import Skill


class TakeNoteSkill(Skill):
    name = "take_note"
    description = "Save a timestamped note."
    examples = ["take note buy milk", "remember to call Ali at 5"]

    def run(self, args):
        text = (args.get("text") or "").strip().rstrip(".")
        if not text:
            return "What should I note down?"
        config.NOTES_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(config.NOTES_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"[{stamp}] {text}\n")
        return f"Noted: {text}."


class ListNotesSkill(Skill):
    name = "list_notes"
    description = "Read back your saved notes."
    examples = ["list my notes", "show notes"]

    def run(self, args):
        if not config.NOTES_FILE.exists():
            return (
                "You don't have any notes yet. "
                "Say 'take note' followed by what to remember."
            )
        lines = config.NOTES_FILE.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            return "Your notes file is empty."
        recent = lines[-5:]
        out = "Here are your recent notes:\n" + "\n".join(
            f"{i + 1}. {line}" for i, line in enumerate(recent)
        )
        if len(lines) > 5:
            out += f"\n(Showing 5 of {len(lines)}.)"
        return out

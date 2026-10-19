"""System skills: open apps, open websites, tell the time/date.

Windows-only calls (os.startfile) are guarded by platform checks; on other
platforms the skills degrade to xdg-open / honest 'not available' messages.
"""

import os
import shutil
import subprocess
import sys
import webbrowser
from datetime import datetime

from .base import Skill

# Friendly names -> Windows executable. Used only on Windows.
APP_ALIASES_WIN = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "terminal": "wt.exe",
    "command prompt": "cmd.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
}


class OpenAppSkill(Skill):
    name = "open_app"
    description = "Open an installed application by name."
    examples = ["open notepad", "open calculator", "open file explorer"]

    def run(self, args):
        target = (args.get("target") or "").strip().rstrip(".")
        if not target:
            return "Which app should I open?"
        low = target.lower()
        if low in ("browser", "web browser"):
            webbrowser.open("https://www.google.com")
            return "Opening your web browser."

        if sys.platform == "win32":
            resolved = APP_ALIASES_WIN.get(low, target)
            try:
                os.startfile(resolved)  # noqa: SLF001 — Windows-only API, guarded above
                return f"Opening {target}."
            except OSError as exc:
                return f"I couldn't open {target}: {exc.strerror or exc}"

        # macOS / Linux: only launch things that actually exist.
        exe = shutil.which(target) or shutil.which(low)
        if not exe:
            return f"I couldn't find an app called '{target}' on this system."
        opener = shutil.which("xdg-open") or shutil.which("open")
        if not opener:
            return f"Found {target}, but I don't know how to launch apps on {sys.platform}."
        try:
            subprocess.Popen(
                [opener, exe],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"Opening {target}."
        except Exception as exc:
            return f"I couldn't open {target}: {exc}"


class OpenWebsiteSkill(Skill):
    name = "open_website"
    description = "Open a website in the default browser."
    examples = ["open youtube.com", "open website github.com"]

    def run(self, args):
        site = (args.get("site") or "").strip().rstrip(".")
        if not site:
            return "Which website should I open?"
        url = site if site.startswith(("http://", "https://")) else "https://" + site
        try:
            opened = webbrowser.open(url)
        except Exception:
            opened = False
        if opened:
            return f"Opening {url}."
        return (
            f"I couldn't open a browser here. "
            f"Open this yourself: {url}"
        )


class TellTimeSkill(Skill):
    name = "tell_time"
    description = "Tell the current time and date."
    examples = ["what time is it", "what's the date today"]

    def run(self, args):
        now = datetime.now()
        return now.strftime("It's %I:%M %p on %A, %B %d, %Y.")

"""Local reminders: parse simple times, store as JSON, list due/upcoming.

No cloud, no account, no background daemon — reminders live in
~/assistant-reminders/reminders.json and are checked when you ask
(and announced at startup when any are due).

Understood time expressions:
    in 10 minutes / in 2 hours
    tomorrow at 9am / tomorrow at 9:30pm
    today at 5pm / at 5pm   (rolls to tomorrow if the time already passed)
"""

import json
import re
from datetime import datetime, timedelta

from .. import config
from .base import Skill

_TIME_RE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", re.IGNORECASE)
_IN_RE = re.compile(r"\bin\s+(\d+)\s*(minutes?|hours?)\b", re.IGNORECASE)


def _parse_dt(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def parse_reminder(text):
    """Parse '<task> <time-expr>' into (task, due_datetime).

    Returns (None, None) when no time expression is understood.
    """
    original = (text or "").strip()
    t = " " + original.lower() + " "
    now = datetime.now()

    def clean(match):
        # t has one leading space, so shift indices back by one
        start = max(0, match.start() - 1)
        end = match.end() - 1
        # Swallow a preceding "tomorrow at" / "today at" / "at" so the task
        # reads cleanly: "remind me tomorrow at 9am to submit X" -> "submit X".
        prefix = original[:start]
        pm = re.search(r"\b(tomorrow|today)\s+at\s*$", prefix, re.IGNORECASE)
        if pm:
            start = pm.start()
        else:
            pm = re.search(r"\bat\s*$", prefix, re.IGNORECASE)
            if pm:
                start = pm.start()
        task = (original[:start] + " " + original[end:]).strip()
        task = re.sub(r"^remind me\s+", "", task, flags=re.IGNORECASE)
        task = re.sub(r"^(to|that)\s+", "", task, flags=re.IGNORECASE)
        task = re.sub(r"\b(tomorrow|today)\b", "", task, flags=re.IGNORECASE)
        task = re.sub(r"\s+", " ", task).strip(" ,.")
        return task or "something"

    m = _IN_RE.search(t)
    if m:
        n = int(m.group(1))
        delta = (
            timedelta(minutes=n)
            if m.group(2).lower().startswith("minute")
            else timedelta(hours=n)
        )
        return clean(m), now + delta

    m = _TIME_RE.search(t)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2) or 0)
        ampm = m.group(3).lower()
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        base = now.date()
        if "tomorrow" in t:
            base += timedelta(days=1)
        due = datetime(base.year, base.month, base.day, hour, minute)
        if due <= now:
            due += timedelta(days=1)
        return clean(m), due

    return None, None


def describe_due(due):
    """Short human description of when a reminder is due."""
    now = datetime.now()
    delta = due - now
    if delta < timedelta(0):
        return "overdue"
    if delta < timedelta(hours=1):
        mins = max(1, int(delta.total_seconds() // 60))
        return f"in {mins} minute{'s' if mins != 1 else ''}"
    stamp = due.strftime("%I:%M %p").lstrip("0")
    if due.date() == now.date():
        return f"today at {stamp}"
    if due.date() == (now + timedelta(days=1)).date():
        return f"tomorrow at {stamp}"
    return f"on {due.strftime('%b %d')} at {stamp}"


def _load():
    try:
        if config.REMINDERS_FILE.exists():
            data = json.loads(config.REMINDERS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def _save(reminders):
    config.REMINDERS_DIR.mkdir(parents=True, exist_ok=True)
    config.REMINDERS_FILE.write_text(
        json.dumps(reminders, indent=2), encoding="utf-8"
    )


def due_reminders(now=None):
    """Reminders whose time has passed and that aren't done yet."""
    now = now or datetime.now()
    out = []
    for r in _load():
        due = _parse_dt(r.get("due"))
        if not r.get("done") and due and due <= now:
            out.append(r)
    return out


class SetReminderSkill(Skill):
    name = "set_reminder"
    description = "Set a reminder for later."
    examples = [
        "remind me to call mom in 2 hours",
        "remind me tomorrow at 9am to submit the report",
    ]

    def run(self, args):
        text = (args.get("text") or "").strip().rstrip(".")
        task, due = parse_reminder(text)
        if not task or not due:
            return (
                "I couldn't understand the time. Try: "
                "'remind me to call mom in 2 hours' or "
                "'remind me tomorrow at 9am to submit the report'."
            )
        reminders = _load()
        reminders.append(
            {
                "id": int(datetime.now().timestamp() * 1000),
                "text": task,
                "due": due.isoformat(timespec="minutes"),
                "created": datetime.now().isoformat(timespec="minutes"),
                "done": False,
            }
        )
        _save(reminders)
        return f"Reminder set: {task}, {describe_due(due)}."


class CheckRemindersSkill(Skill):
    name = "check_reminders"
    description = "List due and upcoming reminders."
    examples = ["what are my reminders", "check reminders"]

    def run(self, args):
        reminders = [r for r in _load() if not r.get("done")]
        if not reminders:
            return "You have no reminders set."
        now = datetime.now()
        reminders.sort(key=lambda r: r.get("due") or "")
        lines = []
        for r in reminders:
            due = _parse_dt(r.get("due"))
            when = describe_due(due) if due else "no time set"
            flag = "OVERDUE: " if due and due <= now else ""
            lines.append(f"{flag}{r.get('text')} ({when})")
        return "Your reminders:\n" + "\n".join(
            f"{i + 1}. {line}" for i, line in enumerate(lines)
        )

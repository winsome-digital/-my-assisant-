"""Rule-based intent router.

Each entry maps a skill name to a list of (regex, arg_names). The first
pattern that matches wins; named groups are passed to the skill as args.
Matching is case-insensitive and order matters — specific patterns first.
"""

import re

# (skill_name, [(pattern, [arg_names])])
_PATTERNS = [
    ("exit", [
        (r"^\s*(exit|quit|goodbye|bye|stop)\s*$", []),
    ]),
    ("help", [
        (r"\bhelp\b", []),
        (r"\bwhat can you do\b", []),
    ]),
    ("take_note", [
        (r"(?:take a note|take note|note that|remember)\s+(.+)", ["text"]),
    ]),
    ("list_notes", [
        (r"\b(?:list|show|read)(?: my)? notes\b", []),
    ]),
    ("check_email", [
        (r"\bread my last (\d+) emails?\b", ["count"]),
        (r"\bread my (?:latest )?emails?\b", []),
        (r"\bcheck my email\b", []),
        (r"\bany new emails?\b", []),
    ]),
    ("send_email", [
        (r"\bsend\s+(?:an\s+)?email\s+to\s+(\S+)\s+about\s+(.+?)\s+saying\s+(.+)", ["to", "subject", "body"]),
        (r"\bemail\s+(\S+)\s+about\s+(.+?)\s+saying\s+(.+)", ["to", "subject", "body"]),
        (r"\bsend\s+(?:an\s+)?email\s+to\s+(\S+)\s+about\s+(.+)", ["to", "subject"]),
        (r"\bemail\s+(\S+)\s+about\s+(.+)", ["to", "subject"]),
    ]),
    ("send_whatsapp", [
        (r"\bmessage\s+(\S+)\s+on\s+whatsapp\s+saying\s+(.+)", ["name", "message"]),
        (r"\bsend\s+(?:a\s+)?whatsapp\s+(?:to\s+)?(\S+)\s+saying\s+(.+)", ["name", "message"]),
        (r"\bwhatsapp\s+(\S+)\s+saying\s+(.+)", ["name", "message"]),
        (r"\bwhatsapp\s+(\S+)\s*:\s*(.+)", ["name", "message"]),
    ]),
    ("check_reminders", [
        (r"\bwhat are my reminders\b", []),
        (r"\bcheck (?:my )?reminders\b", []),
        (r"\blist reminders\b", []),
        (r"\bany reminders\b", []),
    ]),
    ("set_reminder", [
        (r"\bset (?:a )?reminder to (.+)", ["text"]),
        (r"\bremind me to (.+)", ["text"]),
        (r"\bset (?:a )?reminder\s+(.+)", ["text"]),
        (r"\bremind me\s+(.+)", ["text"]),
    ]),
    ("find_file", [
        (r"\bfind\s+(?:the\s+|my\s+)?(?:file\s+)?(.+)", ["query"]),
        (r"\b(?:locate|search for file)\s+(.+)", ["query"]),
    ]),
    ("open_website", [
        (r"\bopen\s+(?:website\s+|site\s+)?([\w\-]+\.[\w.]{2,}\S*)", ["site"]),
    ]),
    ("open_app", [
        (r"\bopen\s+(.+)", ["target"]),
    ]),
    ("web_search", [
        (r"\bsearch\s+(?:the web\s+)?for\s+(.+)", ["query"]),
        (r"\bgoogle\s+(.+)", ["query"]),
    ]),
    ("tell_time", [
        (r"\bwhat time\b", []),
        (r"\bthe time\b", []),
        (r"\bwhat date\b", []),
        (r"\bwhat day is it\b", []),
        (r"\btoday'?s date\b", []),
    ]),
]


def route(text):
    """Return (skill_name, args_dict). Returns (None, {}) when nothing matches."""
    t = " " + (text or "").strip().lower() + " "
    for skill_name, rules in _PATTERNS:
        for pattern, arg_names in rules:
            m = re.search(pattern, t)
            if m:
                args = {}
                for i, name in enumerate(arg_names):
                    args[name] = (m.group(i + 1) or "").strip()
                return skill_name, args
    return None, {}

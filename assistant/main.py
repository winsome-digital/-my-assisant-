"""Jarvis entry point — the personal desktop assistant.

Usage:
    python -m assistant.main                      # voice loop (push-to-talk)
    python -m assistant.main --text "find file report"   # single headless command
    python -m assistant.main --list-skills         # show all skills and exit
    python -m assistant.main --help                # this help
"""

import argparse
import sys

from . import config, personality
from .nlu import intents
from .skills.email import CheckEmailSkill, SendEmailSkill
from .skills.files import FindFileSkill
from .skills.messaging import SendWhatsAppSkill
from .skills.notes import ListNotesSkill, TakeNoteSkill
from .skills.reminders import CheckRemindersSkill, SetReminderSkill, due_reminders
from .skills.system import OpenAppSkill, OpenWebsiteSkill, TellTimeSkill
from .skills.web import WebSearchSkill
from .voice.listen import listen_loop
from .voice.tts import speak


def build_skills():
    """Instantiate every skill and index by name."""
    skills = [
        FindFileSkill(),
        OpenAppSkill(),
        OpenWebsiteSkill(),
        TellTimeSkill(),
        TakeNoteSkill(),
        ListNotesSkill(),
        WebSearchSkill(),
        SendEmailSkill(),
        CheckEmailSkill(),
        SendWhatsAppSkill(),
        SetReminderSkill(),
        CheckRemindersSkill(),
    ]
    return {s.name: s for s in skills}


def print_skills(skills):
    print(f"{config.APP_NAME} v{config.VERSION} — skills:\n")
    for skill in skills.values():
        print(f"* {skill.name} — {skill.description}")
        for ex in skill.examples:
            print(f'    try: "{ex}"')
    print()


def handle_command(text, skills):
    """Route text to a skill and speak the result. Returns "exit" to quit."""
    text = (text or "").strip()
    if not text:
        return None
    skill_name, args = intents.route(text)
    if skill_name == "exit":
        speak(personality.farewell())
        return "exit"
    if skill_name == "help":
        print_skills(skills)
        speak("I printed the list of things I can do.")
        return None
    if skill_name is None:
        speak("I didn't catch that. Say 'help' to hear what I can do.")
        return None
    skill = skills.get(skill_name)
    try:
        result = skill.run(args)
    except Exception as exc:  # a skill must never crash the loop
        result = f"Something went wrong running {skill_name}: {exc}"
    speak(result)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m assistant.main",
        description="Jarvis — your personal voice-controlled desktop assistant.",
    )
    parser.add_argument(
        "--text",
        metavar='"command"',
        help="Run one command headless (no microphone or audio needed).",
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="Print all skills with example phrases and exit.",
    )
    args = parser.parse_args(argv)

    skills = build_skills()

    if args.list_skills:
        print_skills(skills)
        return 0
    if args.text is not None:
        handle_command(args.text, skills)
        return 0
    # Interactive session: greet by name, then flag any due reminders.
    speak(personality.greeting())
    due = due_reminders()
    if due:
        n = len(due)
        names = "; ".join(r.get("text", "something") for r in due[:3])
        extra = f", and {n - 3} more" if n > 3 else ""
        speak(f"You have {n} reminder{'s' if n != 1 else ''} due: {names}{extra}.")
    listen_loop(lambda t: handle_command(t, skills))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Skill base class — every capability is a Skill."""


class Skill:
    """A skill has a name, a description, example phrases, and a run() method.

    run(args) must return the string the assistant speaks back to the user.
    It must never raise for ordinary input — main.py guards it anyway.
    """

    name = "base"
    description = "Base skill — do not use directly."
    examples = []

    def run(self, args):
        raise NotImplementedError

    def __repr__(self):
        return f"<Skill {self.name}>"


def ask_yes_no(prompt):
    """Confirm-before-it-counts: speak the question, read a typed yes/no.

    Returns True only for an explicit yes. Empty input, EOF, or anything
    else counts as no. Never raises. Used before sending email or any other
    action that leaves the machine.
    """
    from ..voice.tts import speak  # lazy import: avoids an import cycle

    speak(f"{prompt} (yes/no)")
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("yes", "y", "yeah", "yep", "sure", "ok", "okay")

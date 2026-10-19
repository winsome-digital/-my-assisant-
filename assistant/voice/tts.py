"""Spoken replies via pyttsx3 (uses SAPI5 automatically on Windows).

Every reply is also printed, so the assistant stays fully usable on machines
with no audio stack — the printout is the fallback, never an afterthought.
"""

_engine = None


def speak(text):
    """Print the reply and, when possible, say it aloud. Never raises."""
    print(f"Assistant: {text}")
    try:
        import pyttsx3
    except ImportError:
        return
    try:
        global _engine
        if _engine is None:
            _engine = pyttsx3.init()
        _engine.say(text)
        _engine.runAndWait()
    except Exception:
        # The printed reply above is the fallback; audio must never crash us.
        pass

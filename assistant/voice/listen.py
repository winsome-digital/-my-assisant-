"""Push-to-talk voice loop.

Sprint 1 uses push-to-talk (press Enter, then speak). The wake-word hook point
for Sprint 2 (e.g. openWakeWord) is config.WAKE_WORD — the loop is structured
so a wake-word watcher can replace the Enter prompt later.
"""

from .. import config, personality


def listen_loop(handle):
    """Run the interactive loop.

    `handle(text)` processes one command string and returns "exit" to quit.
    Falls back to typed commands when no microphone/audio stack is available.
    """
    from .stt import transcribe_from_mic

    print(f"{config.APP_NAME} v{config.VERSION}")
    print("Push-to-talk: press Enter, then speak into your mic.")
    print("No mic? Just type your command instead. Type 'quit' to exit.\n")

    try:
        import sounddevice  # noqa: F401
        from faster_whisper import WhisperModel  # noqa: F401
        mic_ok = True
    except ImportError:
        mic_ok = False
        print("(Audio libraries not installed — running in typed mode.)\n")

    while True:
        try:
            line = input("You (Enter=talk, or type a command): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in ("quit", "exit", "goodbye", "bye"):
            print(f"Assistant: {personality.farewell()}")
            break
        if line:
            if handle(line) == "exit":
                break
            continue
        if not mic_ok:
            print("Assistant: No microphone support here — type your command instead.")
            continue
        try:
            text = transcribe_from_mic()
        except RuntimeError as exc:
            print(f"Assistant: {exc}")
            mic_ok = False
            continue
        if text:
            print(f"Heard: {text}")
            if handle(text) == "exit":
                break
        else:
            print("Assistant: I didn't hear anything — try again.")

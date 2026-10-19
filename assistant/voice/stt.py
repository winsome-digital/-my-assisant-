"""Speech-to-text via faster-whisper.

All heavy imports are lazy (inside functions) so that headless modes like
`python -m assistant.main --text "..."` work on machines without any audio
libraries installed.
"""

from .. import config

_model_cache = {}


def _get_model(model_size=None):
    """Load (once) and return the faster-whisper model."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError(
            "Speech recognition needs 'faster-whisper' — run: pip install faster-whisper"
        )
    size = model_size or config.WHISPER_MODEL
    if size not in _model_cache:
        _model_cache[size] = WhisperModel(size, device="cpu", compute_type="int8")
    return _model_cache[size]


def transcribe_from_mic(seconds=None, model_size=None):
    """Record from the default microphone and return the transcribed text.

    Raises RuntimeError with a helpful message if the audio stack is missing.
    Returns an empty string if nothing intelligible was heard.
    """
    try:
        import sounddevice as sd
    except ImportError:
        raise RuntimeError(
            "Microphone support needs 'sounddevice' — run: pip install sounddevice"
        )
    import numpy as np

    seconds = seconds or config.RECORD_SECONDS
    print(f"Listening for {seconds} seconds — speak now...")
    audio = sd.rec(
        int(seconds * config.SAMPLE_RATE),
        samplerate=config.SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()

    model = _get_model(model_size)
    segments, _info = model.transcribe(audio.flatten(), language=config.WHISPER_LANGUAGE)
    return " ".join(seg.text for seg in segments).strip()

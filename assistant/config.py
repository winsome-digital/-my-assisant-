"""Configuration for Jarvis, the personal desktop assistant.

Public settings live here. Secrets live ONLY in environment variables
(JARVIS_*) or assistant/config.local.json (gitignored) — never in this file,
never printed, never logged.
"""

import json
import os
from pathlib import Path

APP_NAME = "Jarvis"
VERSION = "0.2.0"

# --- Identity ---
ASSISTANT_NAME = "Jarvis"

# Wake word is a hook point for a future release (openWakeWord).
# This build uses push-to-talk.
WAKE_WORD = "hey jarvis"

# --- Local overrides: assistant/config.local.json (gitignored) ---
# Copy config.local.example.json -> assistant/config.local.json and fill in
# your details. Environment variables (JARVIS_*) override the file.
_LOCAL_CONFIG_PATH = Path(__file__).with_name("config.local.json")


def _load_local_config():
    try:
        if _LOCAL_CONFIG_PATH.exists():
            data = json.loads(_LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


_LOCAL = _load_local_config()

USER_NAME = os.environ.get("JARVIS_USER_NAME", _LOCAL.get("user_name", "Mohsin"))

# Email (Gmail via app password). Never printed or logged.
_EMAIL_CFG = _LOCAL.get("email", {})
if not isinstance(_EMAIL_CFG, dict):
    _EMAIL_CFG = {}
EMAIL_ADDRESS = os.environ.get("JARVIS_EMAIL") or _EMAIL_CFG.get("address")
EMAIL_APP_PASSWORD = os.environ.get("JARVIS_EMAIL_APP_PASSWORD") or _EMAIL_CFG.get(
    "app_password"
)

# Contacts: alias -> {"phone": "+92...", "email": "..."} (phone-only string ok).
_CONTACTS_CFG = _LOCAL.get("contacts", {})
CONTACTS = _CONTACTS_CFG if isinstance(_CONTACTS_CFG, dict) else {}

# Reminders live in the user's home folder as JSON — no cloud, no account.
REMINDERS_DIR = Path.home() / "assistant-reminders"
REMINDERS_FILE = REMINDERS_DIR / "reminders.json"

# faster-whisper model size: tiny / base / small / medium / large-v3.
# "small" is a good accuracy/speed balance on CPU.
WHISPER_MODEL = "small"
WHISPER_LANGUAGE = "en"
RECORD_SECONDS = 5
SAMPLE_RATE = 16000

# Notes live in the user's home folder as plain text — no cloud, no account.
NOTES_DIR = Path.home() / "assistant-notes"
NOTES_FILE = NOTES_DIR / "notes.txt"

# File search settings
SEARCH_ROOTS = [Path.home()]
MAX_RESULTS = 5
MAX_FILES_SCANNED = 30000
MAX_SEARCH_SECONDS = 12.0

# Directories never descended into during file search (noise, caches, huge trees).
SKIP_DIR_NAMES = {
    ".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv",
    ".cache", ".mozilla", ".config", ".npm", ".cargo", ".rustup", "snap",
    ".vscode", ".idea", "AppData", "Local Settings",
}

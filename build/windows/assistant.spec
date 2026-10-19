# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Jarvis.

Build this on the Windows CI runner (see .github/workflows/windows-build.yml),
NOT on Linux — PyInstaller cannot cross-compile to Windows.

Run from the project root:
    pyinstaller build/windows/assistant.spec
"""

import os

# Directory containing this spec file: build/windows/
SPECPATH_DIR = SPECPATH  # noqa: F821 - provided by PyInstaller at build time
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH_DIR, "..", ".."))

a = Analysis(  # noqa: F821 - provided by PyInstaller at build time
    [os.path.join(PROJECT_ROOT, "assistant", "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[
        "faster_whisper",
        "pyttsx3",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "sounddevice",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Jarvis",
    debug=False,
    strip=False,
    upx=False,
    # v1 keeps the console window visible so users can see what's happening
    # and report errors. A windowed (console=False) build is a Sprint 2 item.
    console=True,
    # Request administrator rights at launch (Windows UAC prompt).
    # The user explicitly asked for this so the assistant can perform
    # privileged tasks (install software, change system settings, etc.).
    # SECURITY NOTE: every voice command then runs as admin — a misheard
    # command or stray audio could trigger a privileged action. The app
    # still asks for confirmation before destructive actions (see skills).
    uac_admin=True,
)

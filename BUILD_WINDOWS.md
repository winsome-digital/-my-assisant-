# Building the Windows 11 .exe — step by step

PyInstaller cannot cross-compile, so the `.exe` is built on a real Windows 11
machine provided free by GitHub Actions. Total hands-on time: ~10 minutes
(most of it is waiting for the build).

## Prerequisites

- A GitHub account (free).
- Git installed on your PC.
- This project folder (`desktop-assistant/`).

## Steps

### 1. Put the project on GitHub

```powershell
cd desktop-assistant
git init
git add .
git commit -m "Jarvis Sprint 1"
# create an empty repo on github.com first, then:
git remote add origin https://github.com/YOUR-USERNAME/voice-assistant.git
git push -u origin main
```

### 2. Run the build workflow

1. Open your repo on github.com.
2. Click the **Actions** tab.
3. Click **"Build Windows EXE"** in the left sidebar.
4. Click **"Run workflow"** → **"Run workflow"** (green button).
5. Wait ~5–8 minutes for the green checkmark.

(The workflow also runs automatically every time you push a version tag
like `v0.1.0`.)

### 3. Download the .exe

1. Click the finished workflow run.
2. Scroll to **Artifacts** → download **Jarvis-windows**.
3. Unzip it. Inside is `Jarvis.exe` (~60–80 MB — it bundles Python
   and the speech libraries, so it runs on any Windows 11 PC with nothing
   installed).

### 4. First run

- Double-click `Jarvis.exe`. A console window opens (kept visible in
  v1 on purpose, so you can see what it's doing).
- **SmartScreen warning:** Windows will likely show "Windows protected your
  PC" because the file is unsigned. This is expected for any unsigned
  `.exe`. Click **More info → Run anyway**.
- **First mic use** downloads the speech-recognition model (~500 MB, one
  time, from Hugging Face). Needs internet that once; afterwards it works
  offline.
- **Admin rights:** the app requests administrator rights at launch, so
  Windows will show a UAC elevation prompt every time you start it. Only
  click Yes if you launched it yourself.

## About code signing (optional, costs money)

An unsigned `.exe` always shows the SmartScreen warning on first run on a
new PC. To remove it permanently you buy a **code-signing certificate**
(~$70–300/year from a Certificate Authority), then sign the file:

```powershell
signtool sign /fd SHA256 /a Jarvis.exe
```

This is standard practice for distributed Windows software and is entirely
optional for personal use.

## Troubleshooting

| Problem | Fix |
|---|---|
| Workflow fails at "Install dependencies" | Check the log — usually a transient PyPI hiccup; re-run the workflow. |
| `.exe` flagged by Defender after download | Expected for unsigned PyInstaller builds; "Allow" / "Run anyway". If you distribute it, get it signed. |
| "No module named faster_whisper" at runtime | The spec's `hiddenimports` covers this; if you edited the spec, check them. |
| Mic not heard | Check Windows Settings → Privacy → Microphone → allow desktop apps. |

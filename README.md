# Jarvis — Your Personal Desktop Assistant

A voice-controlled desktop assistant you talk to — now with a name and a
personality. Say what you want in plain words: it finds files, opens apps and
websites, searches the web, takes notes, tells the time, **sends email**,
**messages on WhatsApp**, and **sets reminders**. Replies are spoken aloud
(and always printed), briefly, in a confident butler tone.

This is **Jarvis v0.2.0**, evolved from the working Sprint 1 prototype.
Sprint 1 uses push-to-talk (press Enter, then speak); the wake-word
("hey jarvis") is a hook point for a later release.

## Quickstart (Windows 11)

Requirements: Windows 11, Python 3.12 (from python.org), a microphone.

```powershell
# 1. Get the code
git clone <your-repo-url>
cd desktop-assistant

# 2. Install dependencies
py -3.12 -m pip install -r requirements.txt

# 3. Run it
py -3.12 -m assistant.main
```

Press **Enter**, speak your command when it says "Listening…", and it replies
out loud. No microphone? Just type your command at the prompt instead.

Try headless (no mic/audio needed — also how automated tests run it):

```powershell
py -3.12 -m assistant.main --text "find file report"
py -3.12 -m assistant.main --list-skills
```

## What it can do (example commands)

| Say | It does |
|---|---|
| "find file report" | Searches your home folder by file name, lists top matches |
| "open notepad" | Opens the app (Windows: Notepad, Calculator, …) |
| "open youtube.com" | Opens the site in your default browser |
| "search for weather in Karachi" | Opens a web search for it |
| "what time is it" | Speaks the time and date |
| "take note buy milk" | Saves a timestamped note to `~/assistant-notes/` |
| "list my notes" | Reads your recent notes back |
| "email sara about dinner saying I'll be there at 8" | Sends an email via Gmail (asks you to confirm first) |
| "check my email" | Reads back your latest email subjects |
| "message sara on whatsapp saying I'll be late" | Opens WhatsApp with the message prefilled (you tap send) |
| "remind me to call mom in 2 hours" | Sets a reminder, stored locally |
| "what are my reminders" | Lists due and upcoming reminders |
| "help" | Lists everything it can do |

## Setting up email (Gmail)

Jarvis sends and reads email through your Gmail account. You need a
**Google app password** (never your real password):

1. Google Account → Security → turn on **2-Step Verification**.
2. Security → **App passwords** → generate one for Mail.
3. Copy `config.local.example.json` to `assistant/config.local.json`
   (this file is gitignored — it never leaves your machine) and fill in:
   ```json
   { "email": { "address": "you@gmail.com", "app_password": "xxxx xxxx xxxx xxxx" } }
   ```
   Or set the `JARVIS_EMAIL` and `JARVIS_EMAIL_APP_PASSWORD` environment
   variables instead.
4. Say "email sara about dinner saying I'll be there at 8" — Jarvis shows
   the draft and asks **"Should I send this email?"** before sending.

## Setting up WhatsApp contacts

In the same `assistant/config.local.json`, add people under `contacts`:

```json
{ "contacts": { "sara": { "phone": "+923001234567", "email": "sara@example.com" } } }
```

Then "message sara on whatsapp saying I'll be late" opens the chat with your
text prefilled. **You tap send** — Jarvis never sends messages behind your
back, and says so out loud.

## Getting the .exe

The `.exe` is built automatically on a real Windows 11 machine in the cloud —
see **[BUILD_WINDOWS.md](BUILD_WINDOWS.md)** for the step-by-step (about
10 minutes: push to GitHub → Actions → Run workflow → download the artifact).

Why not just build it here? PyInstaller **cannot cross-compile**: a Windows
`.exe` has to be produced on Windows. The GitHub Actions workflow in
`build/windows/` does exactly that.

## Security notes (please read)

- **Runs as administrator (your choice).** The `.exe` requests admin rights
  at launch, so Windows will show a UAC prompt ("Do you want to allow this
  app to make changes?") every time you start it. This lets the assistant
  perform privileged tasks (installing software, changing system settings).
  **Trade-off:** every voice command then runs with full system privileges —
  a misheard command or stray background audio could trigger a privileged
  action. The app still asks for confirmation before destructive actions,
  and you can read every line of `assistant/` to verify what it does.
- **Nothing shady inside.** No keylogging, no screen capture, no network
  exfiltration, no obfuscated code. It only: listens to the mic when you press
  Enter, transcribes locally with faster-whisper, opens apps/websites **you**
  asked for, and reads/writes files **you** asked about. You can read every
  line of `assistant/` to verify.
- **Windows Defender.** A locally-built, unsigned `.exe` can trigger a
  SmartScreen warning ("Windows protected your PC") on first run. This is
  normal for any unsigned executable — click **More info → Run anyway**.
  The warning goes away permanently if the `.exe` is signed with a
  code-signing certificate (paid, from a Certificate Authority). Signing is
  optional and is *not* included in this prototype.
- **First run downloads a speech model** (~500 MB, from Hugging Face) the
  first time you use the mic. That's the only network access the app needs.

## Honest limitations of this build

- Push-to-talk only — always-on wake-word listening is a later release.
- English only, for now (`config.WHISPER_MODEL` / `WHISPER_LANGUAGE`).
- File search covers your home folder with caches and system dirs skipped.
- Email needs a Gmail app password (see setup above); WhatsApp needs the
  desktop app or browser and you tap send yourself.
- The `.exe` must be built via the GitHub workflow (see above).

## Project structure

```
desktop-assistant/
  assistant/
    main.py        # entry point: voice loop, --text mode, --list-skills
    config.py      # settings (identity, email, contacts, notes dir)
    personality.py # Jarvis greeting + butler tone
    voice/         # stt.py (faster-whisper), tts.py (pyttsx3), listen.py (loop)
    nlu/           # intents.py — rule-based command router
    skills/        # files, system, notes, web, email, messaging, reminders
    config.local.json        # YOUR secrets (gitignored — you create this)
  config.local.example.json  # template for the above
  build/windows/   # assistant.spec (PyInstaller)
  .github/workflows/  # windows-build.yml (GitHub Actions CI)
  BUILD_WINDOWS.md # step-by-step .exe instructions
  requirements.txt
```

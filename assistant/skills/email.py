"""Email skill: send via Gmail SMTP, read the latest via IMAP.

Credentials come ONLY from environment variables (JARVIS_EMAIL,
JARVIS_EMAIL_APP_PASSWORD) or assistant/config.local.json (gitignored).
They are never printed, never logged, and never leave this machine except
in the encrypted SMTP/IMAP connection to Google.

Sending always asks for confirmation first (confirm-before-it-counts).
"""

import imaplib
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

from .. import config
from .base import Skill, ask_yes_no

SETUP_HELP = (
    "Email isn't set up yet. "
    "Copy config.local.example.json to assistant/config.local.json and add "
    "your Gmail address and an app password — or set the JARVIS_EMAIL and "
    "JARVIS_EMAIL_APP_PASSWORD environment variables. "
    "To get a Gmail app password: Google Account → Security → turn on "
    "2-Step Verification → App passwords → generate one for Mail, "
    "then paste it in. Never use your real Google password here."
)


def _creds():
    """Return (address, app_password) or (None, None) when not configured."""
    if config.EMAIL_ADDRESS and config.EMAIL_APP_PASSWORD:
        return config.EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD
    return None, None


def _resolve_email(recipient):
    """Turn a name, address, or contacts alias into an email address."""
    recipient = (recipient or "").strip().strip(",.")
    if "@" in recipient:
        return recipient
    contact = config.CONTACTS.get(recipient.lower())
    if isinstance(contact, dict) and contact.get("email"):
        return contact["email"]
    if isinstance(contact, str) and "@" in contact:
        return contact
    return None


class SendEmailSkill(Skill):
    name = "send_email"
    description = "Send an email via Gmail (asks for confirmation first)."
    examples = [
        "email sara about dinner saying I'll be there at 8",
        "send email to boss@company.com about report saying the draft is attached",
    ]

    def run(self, args):
        address, app_password = _creds()
        if not address or not app_password:
            return SETUP_HELP
        to = (args.get("to") or "").strip()
        subject = (args.get("subject") or "").strip().rstrip(".")
        body = (args.get("body") or "").strip()
        if not to or not subject:
            return (
                "To send an email, say: email <name> about <subject> "
                "saying <message>."
            )
        recipient = _resolve_email(to)
        if not recipient:
            return (
                f"I don't have an email address for '{to}'. "
                "Add one under contacts in assistant/config.local.json — "
                "see config.local.example.json."
            )
        if not body:
            return "What should the email say?"
        if not ask_yes_no(
            f"Should I send this email to {recipient}? Subject: {subject}"
        ):
            return "Email discarded."
        try:
            msg = EmailMessage()
            msg["From"] = address
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(body)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
                smtp.login(address, app_password)
                smtp.send_message(msg)
        except Exception as exc:
            return (
                f"I couldn't send the email: {exc}. "
                "Check that your app password is correct."
            )
        return f"Done. Email sent to {recipient}."


class CheckEmailSkill(Skill):
    name = "check_email"
    description = "Read back the subjects of your latest emails."
    examples = [
        "check my email",
        "read my latest emails",
        "read my last 5 emails",
    ]

    def run(self, args):
        address, app_password = _creds()
        if not address or not app_password:
            return SETUP_HELP
        try:
            count = int(args.get("count") or 3)
        except (TypeError, ValueError):
            count = 3
        count = max(1, min(count, 10))
        try:
            with imaplib.IMAP4_SSL("imap.gmail.com", timeout=20) as imap:
                imap.login(address, app_password)
                imap.select("INBOX", readonly=True)
                _, data = imap.search(None, "ALL")
                ids = data[0].split()
                if not ids:
                    return "Your inbox is empty."
                latest = ids[-count:][::-1]
                lines = []
                for i, num in enumerate(latest, 1):
                    _, fetched = imap.fetch(
                        num, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])"
                    )
                    raw = fetched[0][1].decode("utf-8", errors="replace")
                    sender = parseaddr(self._header(raw, "From"))[0] or "unknown"
                    subject = self._header(raw, "Subject") or "(no subject)"
                    lines.append(f"{i}. {subject} — from {sender}")
        except Exception as exc:
            return (
                f"I couldn't read your email: {exc}. "
                "Check that your app password is correct."
            )
        return "Here are your latest emails:\n" + "\n".join(lines)

    @staticmethod
    def _header(raw, name):
        for line in raw.splitlines():
            if line.lower().startswith(name.lower() + ":"):
                return line.split(":", 1)[1].strip()
        return ""

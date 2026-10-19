"""Messaging skill: WhatsApp via wa.me links.

No API key, no login, no background service — Jarvis opens the WhatsApp chat
with the message prefilled in the browser (or the WhatsApp app, if installed)
and the user taps send. Honest by design: the reply always says the message
is *ready*, never that it was sent.

Contacts live in assistant/config.local.json (gitignored):
    "contacts": { "sara": { "phone": "+923001234567" } }
A bare phone number also works: "message 03001234567 on whatsapp saying hi".
"""

import re
import webbrowser
from urllib.parse import quote

from .. import config
from .base import Skill


def _resolve_phone(name):
    """Return digits-only phone number for an alias or a raw number."""
    name = (name or "").strip().strip(",.")
    digits = re.sub(r"[^\d]", "", name)
    if len(digits) >= 7:  # a raw number was spoken/typed directly
        return digits
    contact = config.CONTACTS.get(name.lower())
    if isinstance(contact, dict):
        contact = contact.get("phone")
    if contact:
        digits = re.sub(r"[^\d]", "", str(contact))
        if len(digits) >= 7:
            return digits
    return None


class SendWhatsAppSkill(Skill):
    name = "send_whatsapp"
    description = "Open a WhatsApp chat with your message prefilled (you tap send)."
    examples = [
        "message sara on whatsapp saying I'll be late",
        "whatsapp mom saying call me when you're free",
    ]

    def run(self, args):
        name = (args.get("name") or "").strip()
        message = (args.get("message") or "").strip()
        if not name or not message:
            return (
                "To message on WhatsApp, say: message <name> on whatsapp "
                "saying <your message>."
            )
        phone = _resolve_phone(name)
        if not phone:
            return (
                f"I don't have a WhatsApp number for '{name}'. "
                "Add it under contacts in assistant/config.local.json — "
                "see config.local.example.json."
            )
        url = f"https://wa.me/{phone}?text={quote(message)}"
        try:
            webbrowser.open(url)
        except Exception:
            pass  # the URL is the payload; a missing browser isn't fatal
        display = name if not name[:1].isdigit() else phone
        return (
            f"I've opened WhatsApp with your message to {display} ready — "
            "tap send to deliver it."
        )

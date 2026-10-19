"""Web search via the default browser."""

import webbrowser
from urllib.parse import quote_plus

from .base import Skill


class WebSearchSkill(Skill):
    name = "web_search"
    description = "Search the web and open the results."
    examples = ["search for weather in Karachi", "google python tutorials"]

    def run(self, args):
        query = (args.get("query") or "").strip().rstrip(".")
        if not query:
            return "What should I search for?"
        url = "https://www.google.com/search?q=" + quote_plus(query)
        try:
            opened = webbrowser.open(url)
        except Exception:
            opened = False
        if opened:
            return f"Searching the web for {query}."
        return f"I couldn't open a browser here. Search for this yourself: {url}"

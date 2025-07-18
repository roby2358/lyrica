# loop_bot.py
import time, os
from .bluesky_transport import BlueskyTransport
from my_llm import craft_reply          # your OpenAI call, Claude, etc.

bsky = BlueskyTransport(os.getenv("BSKY_HANDLE"),
                        os.getenv("BSKY_APP_PASSWORD"))

while True:
    for note in bsky.fetch_mentions():
        text = craft_reply(note["text"], note["author"]["handle"])
        bsky.reply(text, note)
    bsky.mark_seen()
    time.sleep(30)

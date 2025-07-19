# loop_bot.py
import time, os, sys, logging
from pathlib import Path

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

# Import appropriate TOML library based on Python version
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from .bluesky_transport import BlueskyTransport
from my_llm import craft_reply          # your OpenAI call, Claude, etc.

# Load credentials from TOML file
credentials_path = Path("credentials.toml")
with open(credentials_path, "rb") as f:
    credentials = tomllib.load(f)

bsky = BlueskyTransport(credentials["bluesky"]["handle"],
                        credentials["bluesky"]["app_password"])

while True:
    for note in bsky.fetch_mentions():
        text = craft_reply(note["text"], note["author"]["handle"])
        bsky.reply(text, note)
    bsky.mark_seen()
    time.sleep(30)

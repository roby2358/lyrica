# loop_bot.py
import time, os, sys, logging
from pathlib import Path

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Import appropriate TOML library based on Python version
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from .bluesky_transport import BlueskyTransport
from .ai_brain import AiBrain
from .introspection import introspect_object

# Load credentials from TOML file
credentials_path = Path("credentials.toml")
with open(credentials_path, "rb") as f:
    credentials = tomllib.load(f)

bsky = BlueskyTransport(credentials["bluesky"]["handle"],
                        credentials["bluesky"]["app_password"])
brain = AiBrain(credentials["anthropic"]["api_key"])

while True:
    try:
        mentions = bsky.fetch_mentions()
        processed_count = 0
        
        for note in mentions:
            try:
                # Deep introspection of the notification object
                logger.info("=" * 50)
                logger.info(f"PROCESSING NOTIFICATION {processed_count + 1}")
                logger.info("=" * 50)
                introspect_object(note, "notification", max_depth=3)
                logger.info("=" * 50)
                
                text = brain.craft_reply(note.record.text, note.author.handle)
                bsky.reply(text, note)
                processed_count += 1
                logger.info(f"Successfully processed mention {processed_count} of {len(mentions)}")
            except Exception as e:
                logger.error(f"Failed to process mention from @{getattr(note.author, 'handle', 'unknown')}: {e}")
                continue
        
        logger.info(f"Processed {processed_count} mentions")
        logger.info("~=" * 25)
        
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    
    time.sleep(20)

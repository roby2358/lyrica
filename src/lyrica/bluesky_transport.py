from pathlib import Path
import logging
from atproto import Client                    # SDK is actively maintained — "pip install atproto":contentReference[oaicite:0]{index=0}

logger = logging.getLogger(__name__)

class BlueskyTransport:
    def __init__(self, handle, app_password, config_path=None):
        logger.info(f"Initializing BlueskyTransport for handle: {handle}")
        self.client = Client()
        try:
            self.client.login(handle, app_password)
            logger.info("Successfully logged in to Bluesky")
        except Exception as e:
            logger.error(f"Failed to login to Bluesky: {e}")
            raise
        
        if config_path is None:
            self.cursor_file = self._cursor_config_path()
        else:
            self.cursor_file = config_path
        logger.info(f"Using cursor file: {self.cursor_file}")

    def _cursor_config_path(self):
        """Get the cursor file path in the current working directory."""
        return Path("cursor.txt")

    def _load_cursor(self):
        try:
            cursor = Path(self.cursor_file).read_text().strip()
            logger.debug(f"Loaded cursor: {cursor}")
            return cursor
        except FileNotFoundError:
            logger.debug("No cursor file found, starting fresh")
            return None

    def _save_cursor(self, c):
        Path(self.cursor_file).write_text(c)
        logger.debug(f"Saved cursor: {c}")

    def fetch_mentions(self):
        logger.info("Fetching mentions from Bluesky")
        cursor = self._load_cursor()
        try:
            res = self.client.app.bsky.notification.list_notifications(cursor=cursor)  # endpoint docs:contentReference[oaicite:1]{index=1}
            self._save_cursor(res.get("cursor", cursor or ""))
            
            mention_count = 0
            for n in res["notifications"]:
                if n["reason"] == "mention":
                    mention_count += 1
                    logger.info(f"Found mention from @{n.get('author', {}).get('handle', 'unknown')}")
                    yield n
            
            logger.info(f"Processed {mention_count} mentions")
        except Exception as e:
            logger.error(f"Failed to fetch mentions: {e}")
            raise

    def reply(self, text, reply_to):
        logger.info(f"Sending reply to {reply_to.get('uri', 'unknown URI')}")
        logger.debug(f"Reply text: {text[:100]}...")  # Log first 100 chars
        try:
            self.client.send_post(text, reply_to=reply_to["uri"])
            logger.info("Reply sent successfully")
        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
            raise

    def mark_seen(self):
        logger.info("Marking notifications as seen")
        try:
            self.client.app.bsky.notification.update_seen()         # docs:contentReference[oaicite:2]{index=2}
            logger.info("Notifications marked as seen")
        except Exception as e:
            logger.error(f"Failed to mark notifications as seen: {e}")
            raise

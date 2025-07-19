from pathlib import Path
import logging
from atproto import Client                    # SDK is actively maintained — "pip install atproto":contentReference[oaicite:0]{index=0}
from atproto import models
from datetime import datetime

logger = logging.getLogger(__name__)

class BlueskyTransport:
    def __init__(self, handle, app_password, config_path="cursor.txt"):
        logger.info(f"Initializing BlueskyTransport for handle: {handle}")
        self.client = Client()
        self.client.login(handle, app_password)
        logger.info("Successfully logged in to Bluesky")
        
        self.cursor_file = Path(config_path)
        logger.info(f"Using cursor file: {self.cursor_file}")

    def _load_cursor(self):
        try:
            cursor = Path(self.cursor_file).read_text().strip()
            logger.debug(f"Loaded cursor: {cursor}")
            return cursor
        except FileNotFoundError:
            logger.debug("No cursor file found, starting fresh")
            return None

    def _save_cursor(self, c):
        if c is not None:
            Path(self.cursor_file).write_text(str(c))
            logger.debug(f"Saved cursor: {c}")
        else:
            logger.debug("No cursor to save")

    def _truncate_text(self, text):
        """Truncate text to max_length characters if needed."""
        logger.warning(f"Text too long ({len(text)} chars), truncating to {300} chars")
        return text[:296] + "..."

    def fetch_mentions(self):
        logger.info("Fetching mentions from Bluesky")

        params = {}
        cursor = self._load_cursor()
        if cursor:
            params['cursor'] = cursor
        
        res = self.client.app.bsky.notification.list_notifications(**params)
        
        self.pending_cursor = getattr(res, "cursor", None)
        self._save_cursor(self.pending_cursor)
        
        mention_count = 0
        mentions_to_process = []
        
        for n in res.notifications:
            if n.reason == "mention":
                mention_count += 1
                logger.info(f"Found mention from @{getattr(n.author, 'handle', 'unknown')}")
                mentions_to_process.append(n)
        
        logger.info(f"Found {mention_count} new mentions to process")
        return mentions_to_process

    def reply(self, text, reply_to):
        logger.info(f"Sending reply to {getattr(reply_to, 'uri', 'unknown URI')}")
        logger.debug(f"Reply text: {len(text)} chars: {text[:100]}...")
        
        if len(text) >= 300:
            text = self._truncate_text(text)
        
        reply_ref = models.AppBskyFeedPost.ReplyRef(
            root=models.ComAtprotoRepoStrongRef.Main(
                uri=reply_to.uri,
                cid=reply_to.cid
            ),
            parent=models.ComAtprotoRepoStrongRef.Main(
                uri=reply_to.uri,
                cid=reply_to.cid
            )
        )
        self.client.send_post(text, reply_to=reply_ref)
        logger.info(f"Reply sent {reply_to} : {text}")

    def mark_seen(self):
        logger.info("Marking notifications as seen")
        
        # Use the client's built-in time method for consistency
        seen_at = self.client.get_current_time_iso()
        
        self.client.app.bsky.notification.update_seen({"seenAt": seen_at})
        logger.info("Notifications marked as seen")

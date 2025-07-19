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
        self.processed_uris = set()  # Track processed notification URIs
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

    def _is_already_processed(self, notification):
        """Check if a notification has already been processed to avoid duplicates"""
        notification_uri = getattr(notification, 'uri', None)
        if notification_uri and notification_uri in self.processed_uris:
            logger.debug(f"Skipping already processed notification: {notification_uri}")
            return True
        return False

    def fetch_mentions(self):
        logger.info("Fetching mentions from Bluesky")

        params = {}
        cursor = self._load_cursor()
        if cursor:
            params['cursor'] = cursor
        
        res = self.client.app.bsky.notification.list_notifications(**params)
        
        # Store the new cursor but don't save it yet - only save after successful processing
        self.pending_cursor = getattr(res, "cursor", None)
        
        mention_count = 0
        mentions_to_process = []
        
        for n in res.notifications:
            if n.reason == "mention":
                if self._is_already_processed(n):
                    continue
                    
                mention_count += 1
                logger.info(f"Found mention from @{getattr(n.author, 'handle', 'unknown')}")
                mentions_to_process.append(n)
        
        logger.info(f"Found {mention_count} new mentions to process")
        return mentions_to_process

    def mark_processed(self, notification):
        """Mark a notification as processed to avoid duplicate replies"""
        notification_uri = getattr(notification, 'uri', None)
        if notification_uri:
            self.processed_uris.add(notification_uri)
            # Limit the size of processed URIs to prevent memory issues
            if len(self.processed_uris) > 1000:
                # Remove oldest half when limit is reached
                oldest_uris = list(self.processed_uris)[:500]
                for uri in oldest_uris:
                    self.processed_uris.remove(uri)
                logger.info("Cleaned up old processed URIs to prevent memory issues")
            logger.debug(f"Marked notification as processed: {notification_uri}")

    def commit_progress(self):
        """Save the cursor after successful processing of all mentions"""
        if hasattr(self, 'pending_cursor'):
            self._save_cursor(self.pending_cursor)
            logger.info("Committed cursor progress after successful processing")
            delattr(self, 'pending_cursor')

    def reply(self, text, reply_to):
        logger.info(f"Sending reply to {getattr(reply_to, 'uri', 'unknown URI')}")
        logger.debug(f"Reply text: {text[:100]}...")
        
        if len(text) > 300:
            logger.warning(f"Text too long ({len(text)} chars), truncating to 300 chars")
            text = text[:297] + "..."
        
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
        logger.info(f"reply_to {reply_to} : {text}")
        logger.info("Reply sent successfully")

    def mark_seen(self):
        logger.info("Marking notifications as seen")

        self.client.app.bsky.notification.update_seen({
            'seen_at': datetime.now().isoformat() + 'Z'
        })
        logger.info("Notifications marked as seen")

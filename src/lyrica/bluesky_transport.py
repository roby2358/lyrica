from pathlib import Path
import platform
from atproto import Client                    # SDK is actively maintained — "pip install atproto":contentReference[oaicite:0]{index=0}

class BlueskyTransport:
    def __init__(self, handle, app_password, config_path=None):
        self.client = Client()
        self.client.login(handle, app_password)
        
        if config_path is None:
            self.cursor_file = self._cursor_config_path()
        else:
            self.cursor_file = config_path

    def _cursor_config_path(self):
        """Get the platform-specific cursor file path for lyrica."""
        if platform.system() == "Windows":
            app_data = Path.home() / "AppData" / "Roaming" / "lyrica"
        else:
            app_data = Path.home() / ".lyrica"
        
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data / "cursor.txt"

    def _load_cursor(self):
        try:
            return Path(self.cursor_file).read_text().strip()
        except FileNotFoundError:
            return None

    def _save_cursor(self, c): Path(self.cursor_file).write_text(c)

    def fetch_mentions(self):
        cursor = self._load_cursor()
        res = self.client.app.bsky.notification.list_notifications(cursor=cursor)  # endpoint docs:contentReference[oaicite:1]{index=1}
        self._save_cursor(res.get("cursor", cursor or ""))
        for n in res["notifications"]:
            if n["reason"] == "mention":
                yield n

    def reply(self, text, reply_to):
        self.client.send_post(text, reply_to=reply_to["uri"])

    def mark_seen(self):
        self.client.app.bsky.notification.update_seen()         # docs:contentReference[oaicite:2]{index=2}

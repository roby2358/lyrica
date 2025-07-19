import sys
from pathlib import Path
import anthropic

# Import appropriate TOML library based on Python version
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class AiBrain:
    def __init__(self, api_key, system_prompt_path="resources/prompts/system.txt", user_prompt_path="resources/prompts/user.txt"):
        """Initialize the AI brain with Anthropic API key and prompt file paths."""
        self.api_key = api_key
        self.system_prompt_path = Path(system_prompt_path)
        self.user_prompt_path = Path(user_prompt_path)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Load and cache prompts once during initialization
        self._load_prompts()
    
    def _load_prompts(self):
        """Load system and user prompt templates from files."""
        with open(self.system_prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read().strip()
        
        with open(self.user_prompt_path, "r", encoding="utf-8") as f:
            self.user_prompt_template = f.read().strip()

    def craft_reply(self, message_text, author_handle):
        """
        Craft a reply to a Bluesky mention using Anthropic's Haiku model.
        
        Args:
            message_text (str): The text of the message to reply to
            author_handle (str): The handle of the user who mentioned us
            
        Returns:
            str: The crafted reply text
        """
        # Format the user prompt with the actual message and author
        user_prompt = self.user_prompt_template.format(
            author_handle=author_handle,
            message_text=message_text
        )
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            # Fallback response if API call fails
            return f"🎵 @{author_handle}, I hear your call but can't find the words to sing right now! 🎵"

 
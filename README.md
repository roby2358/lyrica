# Lyrica

A Bluesky bot that responds to users in song verse.

## Description

Lyrica is an AI-powered social media bot that monitors Bluesky mentions and responds with creative, musical verse using Anthropic's Claude AI. The bot crafts poetic replies in structured song formats (verse, chorus, or bridge) while maintaining a friendly, engaging personality. All responses are kept concise and PG-rated for social media interaction.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lyrica
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up credentials by copying the template:
   ```bash
   cp credentials.toml.template credentials.toml
   ```

4. Edit `credentials.toml` with your actual API keys:
   ```toml
   [bluesky]
   handle = "your-handle.bsky.social"
   app_password = "your-app-password"

   [anthropic]
   api_key = "your-anthropic-api-key"
   ```

## Usage

Run the bot using uv:
```bash
uv run python lyrica.py
```

The bot will continuously monitor Bluesky for mentions and respond with song verse. It maintains a cursor to track processed notifications and includes error handling for robust operation.

Example interaction:
- **User mentions:** "@lyrica How are you today?"
- **Lyrica responds:** 
  ```
  [Verse]
  Today I'm humming through the wires
  Feeling good with digital fires
  Your words light up my coded heart
  Music and friendship, that's my art
  ```

## Requirements

- Python 3.8+
- Bluesky account with app password
- Anthropic API key for Claude access

**Dependencies:**
- `atproto` - Bluesky API client
- `anthropic` - Claude AI integration
- `requests` - HTTP client
- `python-dotenv` - Environment management
- `tomli/tomllib` - TOML configuration parsing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing code style
4. Test your changes thoroughly
5. Submit a pull request

For development, install dev dependencies:
```bash
uv sync --dev
```

This includes pytest, black, and flake8 for testing and code formatting.

## License

MIT

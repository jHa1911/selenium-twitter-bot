# 🤖 Selenium Twitter Bot

An intelligent Twitter automation bot built with Python and Selenium that can automatically engage with tweets, generate contextual replies, and manage Twitter interactions while mimicking human behavior patterns.

## ✨ Features

- **Smart Tweet Detection**: Automatically finds and analyzes tweets based on keywords and hashtags
- **AI-Powered Replies**: Generates contextual and engaging replies using advanced text processing
- **Human-like Behavior**: Implements random delays, scrolling patterns, and realistic interaction timing
- **Stealth Mode**: Anti-detection features to avoid Twitter's automation detection
- **Rate Limiting**: Built-in safeguards to respect Twitter's rate limits and avoid account suspension
- **Robust Error Handling**: Comprehensive logging and error recovery mechanisms
- **Configurable Settings**: Easy-to-modify configuration for different use cases

## 📁 Project Structure

```
selenium-twitter-bot/
├── .vscode/                    # VS Code configuration
├── src/
│   ├── bot/
│   │   ├── twitter_bot.py      # Main Twitter bot logic
│   │   ├── selenium_manager.py # WebDriver management
│   │   └── reply_generator.py  # AI reply generation
│   ├── config/
│   │   ├── settings.py         # Configuration settings
│   │   └── credentials.py      # Twitter credentials
│   └── utils/
│       ├── logger.py           # Logging utilities
│       └── helpers.py          # Helper functions
├── tests/                      # Unit tests
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── main.py                     # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- Twitter account credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/selenium-twitter-bot.git
   cd selenium-twitter-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```env
   TWITTER_USERNAME=your_twitter_username
   TWITTER_PASSWORD=your_twitter_password
   TWITTER_EMAIL=your_twitter_email

   # Optional: Advanced settings
   HEADLESS_MODE=false
   LOG_LEVEL=INFO
   MAX_REPLIES_PER_HOUR=10
   ```

5. **Configure bot settings**

   Edit `src/config/settings.py` to customize:
   - Target keywords and hashtags
   - Reply generation parameters
   - Rate limiting settings
   - Browser configurations

### Usage

1. **Basic usage**
   ```bash
   python main.py
   ```

2. **Run in headless mode**
   ```bash
   python main.py --headless
   ```

3. **Custom configuration**
   ```bash
   python main.py --config custom_settings.json
   ```

## ⚙️ Configuration

### Bot Settings (`src/config/settings.py`)

```python
# Target keywords to search for
TARGET_KEYWORDS = [
    "python programming",
    "web development",
    "artificial intelligence"
]

# Reply generation settings
REPLY_CONFIG = {
    'max_length': 280,
    'tone': 'helpful',
    'include_hashtags': True
}

# Rate limiting (respects Twitter's limits)
RATE_LIMITS = {
    'replies_per_hour': 10,
    'tweets_per_day': 50,
    'follows_per_day': 20
}
```

### Selenium Settings

```python
SELENIUM_CONFIG = {
    'headless': False,
    'timeout': 10,
    'window_size': (1920, 1080),
    'user_agent': 'custom_user_agent'
}
```

## 🛡️ Safety Features

- **Rate Limiting**: Automatic throttling to prevent account suspension
- **Random Delays**: Human-like timing patterns between actions
- **Error Recovery**: Graceful handling of network issues and page changes
- **Stealth Mode**: Anti-detection measures to avoid bot detection
- **Logging**: Comprehensive activity logging for monitoring and debugging

## 📊 Monitoring & Logging

The bot creates detailed logs in the `logs/` directory:

- `bot_activity.log` - General bot operations
- `selenium_actions.log` - Browser automation details
- `errors.log` - Error tracking and debugging

View real-time activity:
```bash
tail -f logs/bot_activity.log
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_bot.py

# Run with coverage
python -m pytest tests/ --cov=src
```

## 🚨 Important Disclaimers

⚠️ **Use Responsibly**: This bot is for educational and legitimate automation purposes only.

- Always comply with Twitter's Terms of Service
- Respect rate limits to avoid account suspension
- Don't use for spam, harassment, or malicious activities
- Test thoroughly before deploying to production
- Consider the ethical implications of automation

## 🔧 Troubleshooting

### Common Issues

**Chrome Driver Issues**
```bash
# Update Chrome and dependencies
pip install --upgrade webdriver-manager selenium
```

**Login Problems**
- Verify credentials in `.env` file
- Check for 2FA requirements
- Ensure account isn't locked or restricted

**Rate Limiting**
- Reduce frequency settings in configuration
- Check Twitter's current rate limits
- Monitor logs for rate limit warnings

### Debug Mode

Enable verbose logging:
```python
# In settings.py
LOG_LEVEL = 'DEBUG'
SELENIUM_CONFIG['headless'] = False
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Selenium WebDriver](https://selenium.dev/) for browser automation
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager) for driver management
- [Python Twitter Community](https://twitter.com/hashtag/python) for inspiration

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/selenium-twitter-bot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/selenium-twitter-bot/discussions)

---

**⭐ Star this repo if you find it helpful!**

> **Note**: This tool is for educational purposes. Always ensure compliance with platform terms of service and applicable laws.

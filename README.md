# 🤖 Selenium Twitter Bot with Web UI

An intelligent Twitter automation bot built with Python and Selenium that can automatically engage with tweets, generate contextual replies, and manage Twitter interactions while mimicking human behavior patterns. Now featuring a **web-based control panel** for easy management!

## ✨ Features

### Core Bot Features
- **Smart Tweet Detection**: Automatically finds and analyzes tweets based on keywords and hashtags
- **AI-Powered Replies**: Generates contextual and engaging replies using advanced text processing
- **Human-like Behavior**: Implements random delays, scrolling patterns, and realistic interaction timing
- **Stealth Mode**: Anti-detection features to avoid Twitter's automation detection
- **Rate Limiting**: Built-in safeguards to respect Twitter's rate limits and avoid account suspension
- **Robust Error Handling**: Comprehensive logging and error recovery mechanisms

### 🎛️ Web UI Features (NEW!)
- **Real-time Dashboard**: Monitor bot status and activity from your browser
- **Dynamic Configuration**: Adjust all bot settings without editing code
- **Start/Stop Controls**: Control your bot with the click of a button
- **Mobile Responsive**: Manage your bot from any device
- **Live Status Updates**: See bot status changes in real-time
- **Settings Validation**: Input validation to prevent configuration errors

## 🏗️ Architecture

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
│   ├── utils/
│   │   ├── logger.py           # Logging utilities
│   │   └── helpers.py          # Helper functions
│   └── web/                    # Web UI (NEW!)
│       ├── app.py              # Flask backend
│       ├── config_manager.py   # Configuration management
│       ├── templates/          # HTML templates
│       │   ├── base.html
│       │   └── index.html
│       └── static/             # CSS, JS, assets
│           ├── css/style.css
│           └── js/main.js
├── tests/                      # Unit tests
├── logs/                       # Application logs
├── config.json                 # Web UI settings (auto-generated)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── main.py                     # Bot entry point
├── web_ui.py                   # Web UI entry point (NEW!)
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- Twitter account credentials

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/jHa1911/selenium-twitter-bot.git
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

# Optional: Default settings
HEADLESS_MODE=false
LOG_LEVEL=INFO
```

## 🎯 Usage

### Method 1: Web UI (Recommended)

1. **Start the web interface**
```bash
python web_ui.py
```

2. **Open your browser**
Navigate to: `http://localhost:5000`

3. **Configure your bot**
- Adjust reply limits, delays, and auto-actions
- Click "Save Configuration"

4. **Start the bot**
Click the "Start Bot" button in the web interface

### Method 2: Command Line (Traditional)

```bash
python main.py
```

### Method 3: Background Process

```bash
# Start web UI in background
nohup python web_ui.py > web_ui.log 2>&1 &

# Control bot through web interface at http://localhost:5000
```

## ⚙️ Configuration

### Web UI Settings

Access the web dashboard at `http://localhost:5000` to configure:

| Setting | Description | Default |
|---------|-------------|---------|
| **Max Replies Per Day** | Maximum daily reply limit | 50 |
| **Max Replies Per Hour** | Maximum hourly reply limit | 10 |
| **Min Delay (seconds)** | Minimum delay between actions | 60 |
| **Max Delay (seconds)** | Maximum delay between actions | 180 |
| **Enable Auto Follow Back** | Automatically follow back followers | true |
| **Enable Auto Like Following** | Like tweets from followed users | true |
| **Max Follows Per Day** | Maximum daily follow limit | 20 |
| **Max Likes Per Day** | Maximum daily like limit | 100 |
| **Max Likes Per Hour** | Maximum hourly like limit | 15 |

### Advanced Configuration (Code)

For advanced users, you can still edit configuration files directly:

**Target Keywords** (`src/config/settings.py`):
```python
TARGET_KEYWORDS = [
    "python programming",
    "web development",
    "artificial intelligence"
]
```

**Reply Generation**:
```python
REPLY_CONFIG = {
    'max_length': 280,
    'tone': 'helpful',
    'include_hashtags': True
}
```

## 🛡️ Safety Features

- **Rate Limiting**: Automatic throttling to prevent account suspension
- **Random Delays**: Human-like timing patterns between actions
- **Error Recovery**: Graceful handling of network issues and page changes
- **Stealth Mode**: Anti-detection measures to avoid bot detection
- **Comprehensive Logging**: Detailed activity logs for monitoring and debugging

## 📊 Monitoring & Logs

The bot creates detailed logs in the `logs/` directory:
- `bot_activity.log` - General bot operations
- `selenium_actions.log` - Browser automation details
- `errors.log` - Error tracking and debugging

**View real-time activity:**
```bash
tail -f logs/bot_activity.log
```

**Web UI also provides:**
- Real-time status indicator
- Configuration change confirmations
- Error notifications in the browser

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

## 🔧 Troubleshooting

### Common Issues

**Chrome Driver Issues**
```bash
pip install --upgrade webdriver-manager selenium
```

**Login Problems**
- Verify credentials in `.env` file
- Check for 2FA requirements
- Ensure account isn't locked or restricted

**Web UI Not Loading**
- Check if port 5000 is available
- Try `python web_ui.py` and look for error messages
- Ensure Flask dependencies are installed: `pip install flask flask-cors`

**Rate Limiting**
- Reduce frequency settings in web UI
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

## ⚖️ Ethical Usage

- Always comply with Twitter's Terms of Service
- Respect rate limits to avoid account suspension
- Don't use for spam, harassment, or malicious activities
- Test thoroughly before deploying to production
- Consider the ethical implications of automation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Selenium WebDriver](https://selenium.dev/) for browser automation
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager) for driver management
- [Flask](https://flask.palletsprojects.com/) for the web interface
- [Bootstrap](https://getbootstrap.com/) for responsive UI components

## 📞 Support

- 📧 Email: [your.email@example.com](mailto:your.email@example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/jHa1911/selenium-twitter-bot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/jHa1911/selenium-twitter-bot/discussions)

## 🌟 Show Your Support

⭐ Star this repo if you find it helpful!

---

**Note**: This tool is for educational purposes. Always ensure compliance with platform terms of service and applicable laws.

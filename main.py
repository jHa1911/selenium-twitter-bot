import argparse
import sys
import os
import json
from pathlib import Path


def load_bot_config():
    """Load configuration from config.json if it exists"""
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('bot_settings', {})
        except json.JSONDecodeError:
            pass
    return {}

# Load configuration at startup
BOT_CONFIG = load_bot_config()

# Apply configuration to environment or settings
for key, value in BOT_CONFIG.items():
    os.environ[key] = str(value)

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bot.twitter_bot import TwitterBot
from config.settings import Settings
from utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description='Twitter Reply Bot')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logger()

    try:
        # Load settings
        try:
            settings = Settings()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            logger.error("Make sure .env file exists and contains all required variables")
            sys.exit(1)

        logger.info("Settings loaded successfully:")

        # Initialize bot
        bot = TwitterBot(settings, test_mode=args.test)

        # Start bot
        logger.info("Starting Twitter Reply Bot...")
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main()

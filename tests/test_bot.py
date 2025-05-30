import pytest
from unittest.mock import Mock, patch
from src.bot.twitter_bot import TwitterBot
from src.config.settings import Settings

class TestTwitterBot:
    def test_bot_initialization(self):
        settings = Mock(spec=Settings)
        bot = TwitterBot(settings, test_mode=True)
        assert bot.test_mode == True
        assert bot.replies_today == 0

    def test_should_continue_today(self):
        settings = Mock(spec=Settings)
        settings.max_replies_per_day = 50
        bot = TwitterBot(settings)
        bot.replies_today = 25
        assert bot._should_continue_today() == True

        bot.replies_today = 50
        assert bot._should_continue_today() == False

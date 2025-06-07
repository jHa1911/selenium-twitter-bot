import os
from typing import List
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Twitter Credentials
    twitter_username: str = Field(..., env="TWITTER_USERNAME")
    twitter_password: str = Field(..., env="TWITTER_PASSWORD")
    twitter_email: str = Field(..., env="TWITTER_EMAIL")
    twitter_api_key: str = Field(..., env="TWITTER_API_KEY")

    # Bot Configuration
    max_replies_per_day: int = Field(50, env="MAX_REPLIES_PER_DAY")
    max_replies_per_hour: int = Field(10, env="MAX_REPLIES_PER_HOUR")
    min_delay_seconds: int = Field(60, env="MIN_DELAY_SECONDS")
    max_delay_seconds: int = Field(180, env="MAX_DELAY_SECONDS")

    # Search Configuration
    default_search_query: str = Field("python programming", env="SEARCH_QUERY")
    reply_keywords: str = Field("giverep, @giverep", env="REPLY_KEYWORDS")

    # Auto-follow and Auto-like Configuration
    enable_auto_follow_back: bool = Field(True, env="ENABLE_AUTO_FOLLOW_BACK")
    enable_auto_like_following: bool = Field(True, env="ENABLE_AUTO_LIKE_FOLLOWING")
    max_follows_per_day: int = Field(20, env="MAX_FOLLOWS_PER_DAY")
    max_likes_per_day: int = Field(100, env="MAX_LIKES_PER_DAY")
    max_likes_per_hour: int = Field(15, env="MAX_LIKES_PER_HOUR")
    check_followers_interval: int = Field(3600, env="CHECK_FOLLOWERS_INTERVAL")  # seconds
    like_following_posts_interval: int = Field(1800, env="LIKE_FOLLOWING_POSTS_INTERVAL")  # seconds

    # Browser Configuration
    headless_mode: bool = Field(False, env="HEADLESS_MODE")
    browser_timeout: int = Field(30, env="BROWSER_TIMEOUT")
    page_load_timeout: int = Field(15, env="PAGE_LOAD_TIMEOUT")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/twitter_bot.log", env="LOG_FILE")

    # Development
    debug_mode: bool = Field(True, env="DEBUG_MODE")
    testing_mode: bool = Field(False, env="TESTING_MODE")

    @property
    def reply_keywords_list(self) -> List[str]:
        return [kw.strip() for kw in self.reply_keywords.split(',')]

    class Config:
        env_file = ".env"

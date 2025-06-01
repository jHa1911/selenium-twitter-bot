import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
from config.settings import Settings
from config.credentials import CredentialsManager
from bot.selenium_manager import SeleniumManager
from bot.reply_generator import ReplyGenerator
from utils.helpers import random_delay

class TwitterBot:
    def __init__(self, settings: Settings, test_mode: bool = False):
        self.settings = settings
        self.test_mode = test_mode
        self.credentials_manager = CredentialsManager(settings)
        self.selenium_manager: Optional[SeleniumManager] = None
        self.reply_generator = ReplyGenerator()

        # Tracking variables
        self.replies_today = 0
        self.replies_this_hour = 0
        self.last_hour_reset = datetime.now().hour
        self.replied_tweets = set()  # Track tweets we've already replied to
        self._initialized = False

        self.follows_today = 0
        self.likes_today = 0
        self.likes_this_hour = 0
        self.last_follower_check = datetime.now() - timedelta(hours=2)  # Check immediately on first run
        self.last_like_check = datetime.now() - timedelta(minutes=30)   # Check immediately on first run
        self.followed_users = set()  # Track users we've already followed
        self.liked_posts = set()     # Track posts we've already liked


        logger.info(f"TwitterBot initialized {'(TEST MODE)' if test_mode else ''}")

    def run(self):
        """Main bot execution loop"""
        try:
            # Setup and login
            if not self._initialize():
                logger.error("Failed to initialize bot")
                return

            # Main loop
            while True:
                try:
                    self._check_hourly_reset()
                    self._reset_daily_counters_if_needed()

                    # Execute reply cycle if within limits
                    if self._should_continue_today():
                        self._execute_reply_cycle()
                    else:
                        logger.info("Daily reply limit reached. Skipping reply cycle...")

                    # Execute auto-follow cycle if enabled and time has come
                    if self._should_check_followers():
                        self._execute_auto_follow_cycle()
                        self.last_follower_check = datetime.now()

                    # Execute auto-like cycle if enabled and time has come
                    if self._should_like_following_posts():
                        self._execute_auto_like_cycle()
                        self.last_like_check = datetime.now()

                    # Wait before next iteration
                    if not any([
                        self._should_continue_today(),
                        self._should_check_followers(),
                        self._should_like_following_posts()
                    ]):
                        logger.info("All limits reached or intervals not met. Waiting...")
                        time.sleep(1800)  # Wait 30 minutes before checking again
                    else:
                        # Short wait between cycles
                        time.sleep(60)  # 1 minute between checks

                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    # Wait before retrying
                    time.sleep(300)  # 5 minutes

        finally:
            self._cleanup()

    def _initialize(self) -> bool:
        """Initialize the bot - setup driver and login"""
        try:
            # Initialize SeleniumManager
            self.selenium_manager = SeleniumManager(self.settings)

            # Setup WebDriver
            if not self.selenium_manager.setup_driver():
                logger.error("Failed to setup WebDriver")
                self.selenium_manager = None
                return False

            # Navigate to Twitter to check login status
            logger.info("Checking login status...")
            if not self.selenium_manager.navigate_to_twitter_home():
                logger.error("Failed to navigate to Twitter")
                return False

            # Check if already logged in
            if self.selenium_manager.is_logged_in():
                logger.info("Already logged in to Twitter - skipping login")
                self._initialized = True
                return True

            # If not logged in, navigate to login page
            logger.info("Not logged in, proceeding with login...")
            if not self.selenium_manager.navigate_to_twitter():
                logger.error("Failed to navigate to Twitter login page")
                return False

            # Navigate to Twitter
    #        if not self.selenium_manager.navigate_to_twitter():
    #            logger.error("Failed to navigate to Twitter")
    #            return False

            # Login
            credentials = self.credentials_manager.get_twitter_credentials()
            if not self.selenium_manager.login(**credentials):
                logger.error("Failed to login to Twitter")
                return False

            self._initialized = True
            logger.info("Bot initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.selenium_manager = None
            return False

    def _execute_auto_follow_cycle(self):
        """Execute auto-follow back cycle"""
        if not self.settings.enable_auto_follow_back:
            return

        if not self._initialized or not self.selenium_manager:
            return

        try:
            logger.info("Starting auto-follow back cycle...")

            # Get followers who aren't being followed back
            followers = self.selenium_manager.get_followers(limit=30)

            followed_count = 0
            for follower in followers:
                if self.follows_today >= self.settings.max_follows_per_day:
                    logger.info("Daily follow limit reached")
                    break

                username = follower['username']
                if username in self.followed_users:
                    continue

                if self.selenium_manager.follow_user(follower):
                    self.follows_today += 1
                    self.followed_users.add(username)
                    followed_count += 1

                    # Random delay between follows
                    delay = random.randint(30, 60)  # 30-60 seconds between follows
                    logger.info(f"Waiting {delay} seconds before next follow...")
                    time.sleep(delay)

            logger.info(f"Auto-follow cycle completed. Followed {followed_count} users back.")

        except Exception as e:
            logger.error(f"Error in auto-follow cycle: {e}")

    def _execute_auto_like_cycle(self):
        """Execute auto-like posts from following cycle"""
        if not self.settings.enable_auto_like_following:
            return

        if not self._initialized or not self.selenium_manager:
            return

        try:
            logger.info("Starting auto-like following posts cycle...")

            # Get recent posts from following
            posts = self.selenium_manager.get_following_posts(limit=25)

            liked_count = 0
            for post in posts:
                if (self.likes_today >= self.settings.max_likes_per_day or
                    self.likes_this_hour >= self.settings.max_likes_per_hour):
                    logger.info("Like limit reached")
                    break

                # Create unique identifier for post
                post_id = f"{post['username']}:{hash(post['tweet_text'])}"
                if post_id in self.liked_posts:
                    continue

                if self.selenium_manager.like_post(post):
                    self.likes_today += 1
                    self.likes_this_hour += 1
                    self.liked_posts.add(post_id)
                    liked_count += 1

                    # Random delay between likes
                    delay = random.randint(5, 15)  # 5-15 seconds between likes
                    logger.info(f"Waiting {delay} seconds before next like...")
                    time.sleep(delay)

            logger.info(f"Auto-like cycle completed. Liked {liked_count} posts.")

        except Exception as e:
            logger.error(f"Error in auto-like cycle: {e}")

    def _should_check_followers(self) -> bool:
        """Check if it's time to run follower check"""
        return (datetime.now() - self.last_follower_check).seconds >= self.settings.check_followers_interval

    def _should_like_following_posts(self) -> bool:
        """Check if it's time to like following posts"""
        return (datetime.now() - self.last_like_check).seconds >= self.settings.like_following_posts_interval

    def _reset_daily_counters_if_needed(self):
        """Reset daily counters at midnight"""
        now = datetime.now()
        if now.date() != getattr(self, '_last_date', now.date()):
            self.replies_today = 0
            self.follows_today = 0
            self.likes_today = 0
            self._last_date = now.date()
            logger.info("Daily counters reset")

    # Modify the _check_hourly_reset method to also reset likes counter:
    def _check_hourly_reset(self):
        """Reset hourly counter if hour has changed"""
        current_hour = datetime.now().hour
        if current_hour != self.last_hour_reset:
            self.replies_this_hour = 0
            self.likes_this_hour = 0  # Add this line
            self.last_hour_reset = current_hour
            logger.info("Hourly reply and like counters reset")

    def _execute_reply_cycle(self):
        """Execute one cycle of finding and replying to tweets"""
        if not self._initialized or not self.selenium_manager:
            logger.error("Bot not properly initialized")
            return

        try:
            # Search for tweets
            if not self.selenium_manager.search_tweets(self.settings.default_search_query):
                logger.warning("Search failed, retrying...")
                return

            # Get tweets
            tweets = self.selenium_manager.get_tweets(limit=20)
            if not tweets:
                logger.warning("No tweets found")
                return

            # Process tweets
            replied_count = 0
            for tweet in tweets:
                if self._should_stop_replying():
                    break

                if self._process_tweet(tweet):
                    replied_count += 1
                    self.replies_today += 1
                    self.replies_this_hour += 1

                    # Random delay between replies
                    delay = random.randint(
                        self.settings.min_delay_seconds,
                        self.settings.max_delay_seconds
                    )
                    logger.info(f"Waiting {delay} seconds before next action...")
                    time.sleep(delay)

            logger.info(f"Reply cycle completed. Replied to {replied_count} tweets.")

            # Longer delay between cycles
            cycle_delay = random.randint(300, 600)  # 5-10 minutes
            logger.info(f"Cycle complete. Waiting {cycle_delay} seconds before next cycle...")
            time.sleep(cycle_delay)

        except Exception as e:
            logger.error(f"Error in reply cycle: {e}")

    def _process_tweet(self, tweet_data: Dict) -> bool:
        """Process a single tweet - decide if we should reply and do it"""
        if not self.selenium_manager:
            logger.error("SeleniumManager not available")
            return False

        try:
            tweet_text = tweet_data.get('text', '')
            username = tweet_data.get('username', '')

            # Create unique identifier for this tweet
            tweet_id = f"{username}:{hash(tweet_text)}"

            # Skip if we've already replied to this tweet
            if tweet_id in self.replied_tweets:
                return False

            # Check if we should reply
            if not self.reply_generator.should_reply_to_tweet(
                tweet_text,
                self.settings.reply_keywords_list
            ):
                return False

            # Generate reply
            reply_text = self.reply_generator.generate_reply(
                tweet_text,
                self.settings.reply_keywords_list
            )

            if not reply_text:
                logger.warning("Failed to generate reply")
                return False

            # In test mode, just log what we would do
            if self.test_mode:
                logger.info(f"TEST MODE - Would reply to @{username}: {reply_text}")
                self.replied_tweets.add(tweet_id)
                return True

            # Actually reply
            if self.selenium_manager.reply_to_tweet(tweet_data, reply_text):
                logger.info(f"Successfully replied to @{username}")
                self.replied_tweets.add(tweet_id)
                return True
            else:
                logger.warning(f"Failed to reply to @{username}")
                return False

        except Exception as e:
            logger.error(f"Error processing tweet: {e}")
            return False

    def _should_continue_today(self) -> bool:
        """Check if we should continue replying today"""
        return self.replies_today < self.settings.max_replies_per_day

    def _should_stop_replying(self) -> bool:
        """Check if we should stop replying in this cycle"""
        return (
            self.replies_this_hour >= self.settings.max_replies_per_hour or
            self.replies_today >= self.settings.max_replies_per_day
        )

    ''' def _check_hourly_reset(self):
        """Reset hourly counter if hour has changed"""
        current_hour = datetime.now().hour
        if current_hour != self.last_hour_reset:
            self.replies_this_hour = 0
            self.last_hour_reset = current_hour
            logger.info("Hourly reply counter reset")

'''

    def _cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'selenium_manager') and self.selenium_manager is not None:
                self.selenium_manager.close()
                logger.info("Selenium WebDriver closed")
                self.selenium_manager = None
            else:
                logger.info("SeleniumManager was not initialized or already cleaned up")
            logger.info("Bot cleanup completed")
        except AttributeError as e:
            logger.warning(f"AttributeError during cleanup: {e}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self._initialized = False

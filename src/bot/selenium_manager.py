from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
import tempfile
import time
import random
from loguru import logger
from config.settings import Settings
from typing import Optional

class SeleniumManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_webdriver_env()

    def _setup_webdriver_env(self):
        """Setup environment variables to prevent WebDriver cleanup issues"""
        # Disable WebDriverManager logging to prevent nul file creation
        os.environ['WDM_LOG_LEVEL'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

        # Set proper cache directory
        cache_dir = os.path.join(tempfile.gettempdir(), 'selenium_cache')
        os.makedirs(cache_dir, exist_ok=True)
        os.environ['WDM_CACHE_DIR'] = cache_dir

    def _ensure_initialized(self) -> None:
        """Ensure driver and wait are initialized, raise error if not"""
        if not self.driver or not self.wait:
            success = self.setup_driver()
            if not success or not self.driver or not self.wait:
                raise RuntimeError("Failed to initialize WebDriver and WebDriverWait")

        # Type assertions to help Pylance understand these are not None
        assert self.driver is not None
        assert self.wait is not None

    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()

            # Basic options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")

            # Prevent cleanup issues
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")

            # User agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # Headless mode if configured
            if self.settings.headless_mode:
                chrome_options.add_argument("--headless=new")  # Use new headless mode
                chrome_options.add_argument("--window-size=1920,1080")

            # Setup service with proper logging
            try:
                # Use ChromeDriverManager with proper configuration
                driver_path = ChromeDriverManager().install()

                service = Service(
                    driver_path,
                    log_path=os.devnull if os.name != 'nt' else 'NUL'
                )
            except Exception as e:
                logger.warning(f"ChromeDriverManager failed, trying system Chrome: {e}")
                service = Service()

            # Create driver with error handling
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.settings.page_load_timeout)
            self.driver.implicitly_wait(10)

            # Setup WebDriverWait
            self.wait = WebDriverWait(self.driver, self.settings.browser_timeout)

            logger.info("Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            self._cleanup_driver()
            return False

    def _cleanup_driver(self):
        """Safely cleanup driver resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error during driver cleanup: {e}")
            finally:
                self.driver = None
                self.wait = None

    def navigate_to_twitter(self):
        """Navigate to Twitter login page

        Returns:
            bool: True if navigation successful, False otherwise

        Raises:
            RuntimeError: If WebDriver setup fails
        """
        self._ensure_initialized()

        # Local reference for type safety
        driver = self.driver
        assert driver is not None

        try:
            driver.get("https://x.com/login")
            logger.info("Navigated to Twitter login page")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to Twitter: {e}")
            return False

    def login(self, username: str, password: str, email: Optional[str] = None):
        """Login to Twitter"""
        self._ensure_initialized()

        # Local references for type safety
        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            # Wait for username input
            username_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )

            # Enter username
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(random.uniform(1, 2))

            # Click Next button
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/parent::*/parent::*'))
            )
            next_button.click()
            time.sleep(random.uniform(2, 3))

            # Handle potential email verification
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
                if email_input and email:
                    email_input.send_keys(email)
                    next_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/parent::*/parent::*'))
                    )
                    next_button.click()
                    time.sleep(random.uniform(2, 3))
            except:
                pass  # Email verification not required

            # Enter password
            password_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="current-password"]'))
            )
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(random.uniform(1, 2))

            # Click Login button
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]/parent::*/parent::*'))
            )
            login_button.click()

            # Wait for successful login
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
            )

            logger.info("Successfully logged into Twitter")
            return True

        except TimeoutException as e:
            logger.error(f"Login timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def search_tweets(self, query: str):
        """Search for tweets with given query"""
        self._ensure_initialized()

        # Local reference for type safety
        driver = self.driver
        assert driver is not None

        try:
            # Navigate to search
            search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))

            logger.info(f"Searched for: {query}")
            return True

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False

    def get_tweets(self, limit: int = 10):
        """Get tweets from current page"""
        self._ensure_initialized()

        # Local reference for type safety
        driver = self.driver
        assert driver is not None

        tweets = []
        try:
            # Wait for tweets to load
            time.sleep(random.uniform(2, 4))

            # Find tweet elements
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

            for i, tweet_element in enumerate(tweet_elements[:limit]):
                try:
                    # Extract tweet data
                    tweet_data = self._extract_tweet_data(tweet_element)
                    if tweet_data:
                        tweets.append(tweet_data)
                except Exception as e:
                    logger.warning(f"Failed to extract tweet {i}: {e}")
                    continue

            logger.info(f"Found {len(tweets)} tweets")
            return tweets

        except Exception as e:
            logger.error(f"Failed to get tweets: {e}")
            return []

    def _extract_tweet_data(self, tweet_element):
        """Extract data from tweet element"""
        try:
            # Get tweet text
            tweet_text_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            tweet_text = tweet_text_element.text if tweet_text_element else ""

            # Get username
            username_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"] a')
            username = username_element.get_attribute('href').split('/')[-1] if username_element else ""

            # Get reply button
            reply_button = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')

            return {
                'text': tweet_text,
                'username': username,
                'element': tweet_element,
                'reply_button': reply_button
            }

        except Exception as e:
            logger.warning(f"Failed to extract tweet data: {e}")
            return None

    def reply_to_tweet(self, tweet_data: dict, reply_text: str):
        """Reply to a specific tweet"""
        self._ensure_initialized()

        # Local references for type safety
        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            # Click reply button
            reply_button = tweet_data['reply_button']
            driver.execute_script("arguments[0].scrollIntoView(true);", reply_button)
            time.sleep(random.uniform(1, 2))
            reply_button.click()

            # Wait for reply dialog
            reply_textarea = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )

            # Type reply
            reply_textarea.click()
            time.sleep(random.uniform(0.5, 1))

            # Type with human-like delays
            for char in reply_text:
                reply_textarea.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))

            time.sleep(random.uniform(1, 2))

            # Click reply button
            reply_submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButtonInline"]'))
            )
            reply_submit.click()

            # Wait for reply to be posted
            time.sleep(random.uniform(2, 4))

            logger.info(f"Successfully replied to @{tweet_data['username']}")
            return True

        except Exception as e:
            logger.error(f"Failed to reply to tweet: {e}")
            return False

    def close(self):
        """Close the WebDriver safely"""
        logger.info("Closing WebDriver...")
        self._cleanup_driver()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.close()

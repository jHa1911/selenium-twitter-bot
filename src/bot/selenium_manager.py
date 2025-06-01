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
from pathlib import Path
import time
import random
from loguru import logger
from config.settings import Settings
from typing import Optional
from urllib.parse import quote_plus

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

            # Create persistent user data directory
            user_data_dir = Path("browser_data")
            user_data_dir.mkdir(exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={user_data_dir.absolute()}")

            # Profile directory for session persistence
            chrome_options.add_argument("--profile-directory=TwitterBot")

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

    def _safe_click(self, element):
        """Safely click element using JavaScript if regular click fails"""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        try:
            element.click()
        except WebDriverException as e:
            logger.warning(f"Regular click failed, trying JavaScript click: {e}")
            self.driver.execute_script("arguments[0].click();", element)

    def _dismiss_overlays(self):
        """Dismiss any potential overlays or modals that might block clicks"""
        if not self.driver:
            return

        try:
            # Common overlay close selectors
            overlay_selectors = [
                '[data-testid="app-bar-close"]',
                '[aria-label="Close"]',
                '[data-testid="mask"]',
                '.r-1p0dtai',  # Common Twitter overlay class
                '[role="button"][aria-label*="Close"]'
            ]

            for selector in overlay_selectors:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for overlay in overlays:
                    if overlay.is_displayed() and overlay.is_enabled():
                        logger.info("Dismissing overlay")
                        self._safe_click(overlay)
                        time.sleep(random.uniform(0.5, 1))
                        break
        except Exception as e:
            logger.debug(f"No overlays to dismiss: {e}")

    def navigate_to_twitter_home(self):
        """Navigate to Twitter home page to check login status"""
        self._ensure_initialized()

        driver = self.driver
        assert driver is not None

        try:
            driver.get("https://x.com/home")
            time.sleep(3)  # Wait for page to load
            logger.info("Navigated to Twitter home page")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to Twitter home: {e}")
            return False

    def is_logged_in(self):
        """Check if user is currently logged in to Twitter"""
        if not self.driver:
            return False

        try:
            # Check for elements that indicate we're logged in
            login_indicators = [
                '[data-testid="SideNav_NewTweet_Button"]',  # Tweet button
                '[data-testid="AppTabBar_Home_Link"]',       # Home tab
                '[data-testid="primaryColumn"]',             # Main timeline
                '[aria-label="Home timeline"]',              # Timeline aria label
                '[data-testid="SideNav_AccountSwitcher_Button"]'  # Profile menu
            ]

            for indicator in login_indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                if elements and elements[0].is_displayed():
                    logger.info("User is already logged in")
                    return True

            # Check if we're on login page (indicates we're not logged in)
            current_url = self.driver.current_url
            if 'login' in current_url or 'signin' in current_url:
                logger.info("User is not logged in - on login page")
                return False

            # Additional check for login form elements
            login_elements = [
                'input[autocomplete="username"]',
                '[data-testid="LoginForm_Login_Button"]'
            ]

            for element in login_elements:
                if self.driver.find_elements(By.CSS_SELECTOR, element):
                    logger.info("User is not logged in - login form detected")
                    return False

            # If we can't determine clearly, assume not logged in for safety
            logger.warning("Could not determine login status clearly, assuming not logged in")
            return False

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

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
            search_url = f"https://twitter.com/search?q={quote_plus(query)}&src=typed_query&f=live"
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
        """Reply to a specific tweet with enhanced error handling"""
        self._ensure_initialized()

        # Local references for type safety
        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            # Dismiss any potential overlays first
            self._dismiss_overlays()

            # Get reply button
            reply_button = tweet_data['reply_button']

            # Enhanced scrolling - scroll to center of viewport
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'center'
                });
            """, reply_button)

            # Wait longer for any animations to complete
            time.sleep(random.uniform(2, 4))

            # Wait specifically for this reply button to be clickable
            try:
                # Wait for the specific reply button to be clickable
                wait.until(lambda d: reply_button.is_displayed() and reply_button.is_enabled())

                # Additional check - wait for element to be clickable using EC
                clickable_reply = wait.until(
                    EC.element_to_be_clickable(reply_button)
                )

            except TimeoutException:
                logger.warning("Reply button not immediately clickable, trying alternative approach")
                # Try finding reply button again by tweet element
                try:
                    tweet_element = tweet_data['element']
                    clickable_reply = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                except:
                    raise Exception("Could not locate clickable reply button")

            # Dismiss overlays again in case any appeared during scroll
            self._dismiss_overlays()

            # Try safe click
            logger.info(f"Attempting to click reply button for @{tweet_data['username']}")
            self._safe_click(clickable_reply)

            # Wait for reply dialog with multiple possible selectors
            reply_textarea = None
            textarea_selectors = [
                '[data-testid="tweetTextarea_0"]',
                '[data-testid="tweetTextarea_1"]',
                'div[role="textbox"][data-testid*="tweetTextarea"]',
                'div[contenteditable="true"][role="textbox"]'
            ]

            for selector in textarea_selectors:
                try:
                    reply_textarea = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found reply textarea with selector: {selector}")
                    break
                except TimeoutException:
                    continue

            if not reply_textarea:
                raise Exception("Could not find reply textarea")

            # Wait for textarea to be interactive
            wait.until(EC.element_to_be_clickable(reply_textarea))

            # Click textarea to focus
            self._safe_click(reply_textarea)
            time.sleep(random.uniform(0.5, 1))

            # Clear any existing text
            reply_textarea.clear()
            time.sleep(random.uniform(0.3, 0.7))

            # Type reply with human-like delays
            logger.info("Typing reply text...")
            for i, char in enumerate(reply_text):
                reply_textarea.send_keys(char)

                # Variable delays - faster for common letters, slower for punctuation
                if char in ' .,!?':
                    delay = random.uniform(0.1, 0.3)
                else:
                    delay = random.uniform(0.05, 0.15)

                time.sleep(delay)

                # Occasional longer pauses to simulate thinking
                if i > 0 and i % random.randint(15, 25) == 0:
                    time.sleep(random.uniform(0.5, 1.2))

            # Wait before submitting
            time.sleep(random.uniform(1, 2))

            # Find and click reply submit button
            submit_selectors = [
                '[data-testid="tweetButtonInline"]',
                '[data-testid="tweetButton"]',
                'div[role="button"][data-testid*="tweet"]'
            ]

            reply_submit = None
            for selector in submit_selectors:
                try:
                    reply_submit = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not reply_submit:
                raise Exception("Could not find reply submit button")

            # Submit the reply
            self._safe_click(reply_submit)

            # Wait for reply to be posted - look for success indicators
            time.sleep(random.uniform(2, 4))

            # Try to detect successful posting
            try:
                # Look for success indicators
                success_indicators = [
                    '[data-testid="toast"]',  # Success toast
                    '[role="alert"]',         # Success alert
                ]

                for indicator in success_indicators:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        logger.info("Reply posting success indicator found")
                        break
            except:
                pass  # Success detection is optional

            logger.info(f"Successfully replied to @{tweet_data['username']}")
            return True

        except TimeoutException as e:
            logger.error(f"Reply timeout - element not found/clickable: {e}")
            return False
        except WebDriverException as e:
            logger.error(f"WebDriver error during reply: {e}")
            return False
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

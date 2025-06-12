from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
        self._element_cache = {}
        self._selector_cache = {
            'login_indicators': [
                '[data-testid="SideNav_NewTweet_Button"]',
                '[data-testid="AppTabBar_Home_Link"]',
                '[data-testid="primaryColumn"]',
                '[aria-label="Home timeline"]',
                '[data-testid="SideNav_AccountSwitcher_Button"]'
            ],
            'compose_selectors': [
                '[data-testid="SideNav_NewTweet_Button"]',
                'a[href="/compose/tweet"]'
            ],
            'overlay_selectors': [
                '[data-testid="app-bar-close"]',
                '[aria-label="Close"]',
                '[data-testid="mask"]',
                '.r-1p0dtai',
                '[role="button"][aria-label*="Close"]'
            ]
        }
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
            # Single DOM query for all overlay types
            all_overlays = self.driver.execute_script("""
                const selectors = arguments[0];
                const results = [];
                selectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        if (el.offsetParent !== null && !el.disabled) {
                            results.push(el);
                        }
                    });
                });
                return results;
            """, self._selector_cache['overlay_selectors'])

            if all_overlays:
                # Click first visible overlay
                self.driver.execute_script("arguments[0].click();", all_overlays[0])
                time.sleep(random.uniform(0.3, 0.6))  # Reduced wait time
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

    # Post a tweet with the given text

    def post_tweet(self, text: str) -> bool:
        """Post a tweet with the given text"""
        self._ensure_initialized()

        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            # Navigate to home page to ensure we're in the right context
            driver.get("https://x.com/home")
            time.sleep(random.uniform(2, 4))

            # Dismiss any overlays
            self._dismiss_overlays()

            # Find the tweet button
            compose_selectors = [
                '[data-testid="SideNav_NewTweet_Button"]',
                'a[href="/compose/tweet"]'
            ]

            compose_button = None
            for selector in compose_selectors:
                try:
                    compose_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue

            if not compose_button:
                raise Exception("Could not find compose tweet button")

            # Click the compose button
            self._safe_click(compose_button)
            time.sleep(random.uniform(1, 2))

            # Wait for the tweet textarea
            textarea = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                '[data-testid="tweetTextarea_0"]'))
            )

            # Focus and type the tweet
            self._safe_click(textarea)
            time.sleep(random.uniform(0.5, 1))

            # Type tweet with human-like delays
            for char in text:
                textarea.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))

            time.sleep(random.uniform(1, 2))

            # Find the tweet button
            tweet_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                '[data-testid="tweetButton"]'))
            )

            # Click the tweet button
            self._safe_click(tweet_button)

            # Wait for confirmation
            time.sleep(random.uniform(3, 5))

            logger.info(f"Successfully posted tweet: {text[:50]}...")
            return True

        except TimeoutException as e:
            logger.error(f"Timeout while posting tweet: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return False

    def get_followers(self, limit: int = 50):
        """Get list of followers who are not being followed back"""
        self._ensure_initialized()

        driver = self.driver
        assert driver is not None

        try:
            # Navigate to followers page
            driver.get("https://x.com/followers")
            time.sleep(random.uniform(3, 5))

            followers_to_follow = []
            processed_count = 0

            # Scroll and collect followers
            last_height = driver.execute_script("return document.body.scrollHeight")

            while processed_count < limit:
                # Find follower elements
                follower_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserCell"]')

                for element in follower_elements[processed_count:]:
                    try:
                        # Extract username
                        username_element = element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"] a')
                        href = username_element.get_attribute('href')

                        if not href:
                            logger.warning("Username element found but href is None, skipping")
                            continue

                        username = href.split('/')[-1]

                        if not username:
                            logger.warning("Empty username extracted, skipping")
                            continue

                        # Check if there's a "Follow" button (meaning we're not following them)
                        follow_buttons = element.find_elements(By.CSS_SELECTOR, '[data-testid="follow"]')
                        if follow_buttons and follow_buttons[0].is_displayed():
                            followers_to_follow.append({
                                'username': username,
                                'element': element,
                                'follow_button': follow_buttons[0]
                            })

                        processed_count += 1
                        if processed_count >= limit:
                            break

                    except Exception as e:
                        logger.warning(f"Failed to process follower element: {e}")
                        continue

                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))

                # Check if we've reached the bottom
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            logger.info(f"Found {len(followers_to_follow)} followers to follow back")
            return followers_to_follow

        except Exception as e:
            logger.error(f"Failed to get followers: {e}")
            return []

    def follow_user(self, user_data: dict):
        """Follow a specific user"""
        self._ensure_initialized()

        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            follow_button = user_data['follow_button']

            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", follow_button)
            time.sleep(random.uniform(1, 2))

            # Click follow button
            self._safe_click(follow_button)

            # Wait for button to change (confirmation)
            time.sleep(random.uniform(2, 3))

            logger.info(f"Successfully followed @{user_data['username']}")
            return True

        except Exception as e:
            logger.error(f"Failed to follow @{user_data['username']}: {e}")
            return False

    def get_following_posts(self, limit: int = 20):
        """Get recent posts from people we're following"""
        self._ensure_initialized()

        driver = self.driver
        assert driver is not None

        try:
            # Navigate to home timeline (following feed)
            driver.get("https://x.com/home")
            time.sleep(random.uniform(3, 5))

            posts_to_like = []
            processed_count = 0

            # Scroll and collect posts
            while processed_count < limit:
                tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

                for element in tweet_elements[processed_count:]:
                    try:
                        # Get username
                        username_element = element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"] a')
                        href = username_element.get_attribute('href')

                        if not href:
                            logger.warning("Username element found but href is None, skipping post")
                            continue

                        username = href.split('/')[-1]

                        if not username:
                            logger.warning("Empty username extracted, skipping post")
                            continue

                        # Get like button
                        like_button = element.find_element(By.CSS_SELECTOR, '[data-testid="like"]')

                        # Check if already liked (button would have different attributes)
                        button_class = like_button.get_attribute("class")
                        is_liked = button_class is not None and "r-1777fci" in button_class  # Twitter's liked button class

                        if not is_liked:
                            # Get tweet text for logging
                            try:
                                tweet_text_element = element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                                tweet_text = tweet_text_element.text[:100] + "..." if len(tweet_text_element.text) > 100 else tweet_text_element.text
                            except:
                                tweet_text = "[No text content]"

                            posts_to_like.append({
                                'username': username,
                                'tweet_text': tweet_text,
                                'element': element,
                                'like_button': like_button
                            })

                        processed_count += 1
                        if processed_count >= limit:
                            break

                    except Exception as e:
                        logger.warning(f"Failed to process post element: {e}")
                        continue

                # Scroll down for more posts
                driver.execute_script("window.scrollTo(0, window.scrollY + 800);")
                time.sleep(random.uniform(2, 4))

            logger.info(f"Found {len(posts_to_like)} posts to like")
            return posts_to_like

        except Exception as e:
            logger.error(f"Failed to get following posts: {e}")
            return []

    def like_post(self, post_data: dict):
        """Like a specific post"""
        self._ensure_initialized()

        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            like_button = post_data['like_button']

            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
            time.sleep(random.uniform(1, 2))

            # Click like button
            self._safe_click(like_button)

            # Wait for animation
            time.sleep(random.uniform(1, 2))

            logger.info(f"Successfully liked post by @{post_data['username']}")
            return True

        except Exception as e:
            logger.error(f"Failed to like post by @{post_data['username']}: {e}")
            return False

    def search_tweets(self, query: str):
        """Search for tweets with given query"""
        self._ensure_initialized()

        # Local reference for type safety
        driver = self.driver
        assert driver is not None

        try:
            # Navigate to search page
            base_url = "https://x.com/home" if query == "home" else f"https://x.com/search?q={quote_plus(query)}&src=typed_query&f=live"

            driver.get(base_url)
            time.sleep(random.uniform(3, 5))

            logger.info(f"Searched for: {query}")
            return True

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False

    def get_tweets(self, limit: int = 200):
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
            tweet_text_elements = tweet_element.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            tweet_text = tweet_text_elements[0].text if tweet_text_elements else ""

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

    def get_tweets_with_scroll(self, max_tweets: int = 500, scroll_pause_time: float = 1.5):
        """Get tweets by continuously scrolling and collecting new ones"""
        self._ensure_initialized()

        driver = self.driver
        assert driver is not None

        all_tweets = []
        processed_tweet_ids = set()
        consecutive_no_new = 0
        max_consecutive_no_new = 3

        try:
            logger.info(f"Starting to collect up to {max_tweets} tweets with scrolling...")

            while len(all_tweets) < max_tweets and consecutive_no_new < max_consecutive_no_new:
                # Batch extract all tweet data in single JavaScript execution
                time.sleep(random.uniform(0.8, 2.5))

                if random.random() < 0.2:  # Occasionally wait longer
                    time.sleep(random.uniform(3.0, 5.0))


                tweet_data_batch = driver.execute_script("""
                    const tweets = document.querySelectorAll('[data-testid="tweet"]');
                    const results = [];

                    tweets.forEach((tweet, index) => {
                        try {
                            // Extract username
                            const userLink = tweet.querySelector('[data-testid="User-Name"] a');
                            if (!userLink || !userLink.href) return;

                            const username = userLink.href.split('/').pop();
                            if (!username) return;

                            // Extract tweet text
                            const textElement = tweet.querySelector('[data-testid="tweetText"]');
                            const text = textElement ? textElement.textContent : '';

                            // Extract reply button
                            const replyButton = tweet.querySelector('[data-testid="reply"]');
                            if (!replyButton) return;

                            results.push({
                                username: username,
                                text: text,
                                index: index,
                                hasReplyButton: true
                            });
                        } catch (e) {
                            // Skip problematic tweets
                        }
                    });

                    return results;
                """)

                new_tweets_found = 0

                # Process batch results
                for tweet_data in tweet_data_batch:
                    if random.random() < 0.15:  # Occasionally skip processing to simulate human-like behavior
                        continue
                    try:
                        tweet_id = f"{tweet_data['username']}:{hash(tweet_data['text'])}"

                        if tweet_id in processed_tweet_ids:
                            continue

                        processed_tweet_ids.add(tweet_id)

                        # Get actual elements for interaction (only when needed)
                        tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                        if tweet_data['index'] < len(tweet_elements):
                            tweet_element = tweet_elements[tweet_data['index']]
                            reply_button = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')

                            all_tweets.append({
                                'text': tweet_data['text'],
                                'username': tweet_data['username'],
                                'element': tweet_element,
                                'reply_button': reply_button
                            })
                            new_tweets_found += 1

                        if len(all_tweets) >= max_tweets:
                            break

                    except Exception as e:
                        logger.warning(f"Failed to process tweet: {e}")
                        continue

                if new_tweets_found == 0:
                    consecutive_no_new += 1
                else:
                    consecutive_no_new = 0
                    logger.info(f"Found {new_tweets_found} new tweets. Total: {len(all_tweets)}")

                # Optimized scrolling with momentum
                if len(all_tweets) < max_tweets and consecutive_no_new < max_consecutive_no_new:
                    # Smart scroll with end detection
                    reached_end = driver.execute_script("""
                        const currentHeight = document.body.scrollHeight;
                        window.scrollTo(0, currentHeight + Math.floor(Math.random() * 300 + 100));

                        // Quick end detection
                        const endIndicators = [
                            "you're all caught up",
                            "nothing more to load",
                            "end of timeline"
                        ];

                        const pageText = document.body.textContent.toLowerCase();
                        return endIndicators.some(indicator => pageText.includes(indicator));
                    """)

                    if reached_end:
                        logger.info("Reached end of timeline")
                        break

                    scroll_pause = scroll_pause_time + random.uniform(-0.5, 1.5)
                    time.sleep(scroll_pause)


            logger.info(f"Optimized tweet collection completed. Found {len(all_tweets)} tweets total.")
            return all_tweets

        except Exception as e:
            logger.error(f"Error in get_tweets_with_scroll: {e}")
            return all_tweets  # Return what we have so far

    def scroll_to_load_more_tweets(self, scroll_count: int = 3, pause_time: float = 3.0):
        """Scroll down multiple times to load more tweets"""
        self._ensure_initialized()

        driver = self.driver
        assert driver is not None

        try:
            for i in range(scroll_count):
                logger.debug(f"Scroll {i+1}/{scroll_count}")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(pause_time)

                # Check if we've hit any end-of-timeline indicators
                if self._check_timeline_end_indicators():
                    logger.info("Detected end of timeline, stopping scroll")
                    break

            return True

        except Exception as e:
            logger.error(f"Error scrolling to load more tweets: {e}")
            return False

    def _check_timeline_end_indicators(self):
        """Check for various end-of-timeline indicators"""
        if not self.driver:
            return False

        try:
            # Text-based indicators
            page_text = self.driver.page_source.lower()
            end_phrases = [
                "you're all caught up",
                "nothing more to load",
                "end of timeline",
                "no more tweets"
            ]

            for phrase in end_phrases:
                if phrase in page_text:
                    return True

            # Element-based indicators
            end_elements = [
                '[data-testid="emptyState"]',
                '.css-1dbjc4n.r-1loqt21',  # Common empty state classes
                '[aria-label*="end"]',
                '[aria-label*="caught up"]'
            ]

            for selector in end_elements:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(el.is_displayed() for el in elements):
                    return True

            return False

        except Exception as e:
            logger.debug(f"Error checking timeline end indicators: {e}")
            return False

    def get_current_scroll_position(self):
        """Get current scroll position"""
        if not self.driver:
            return 0
        try:
            return self.driver.execute_script("return window.pageYOffset;")
        except:
            return 0

    def get_page_height(self):
        """Get total page height"""
        if not self.driver:
            return 0
        try:
            return self.driver.execute_script("return document.body.scrollHeight;")
        except:
            return 0

    def has_reached_bottom(self):
        """Check if we've reached the bottom of the page"""
        if not self.driver:
            return True
        try:
            # Get scroll position and page dimensions
            scroll_top = self.driver.execute_script("return window.pageYOffset;")
            window_height = self.driver.execute_script("return window.innerHeight;")
            doc_height = self.driver.execute_script("return document.body.scrollHeight;")

            # Consider "bottom" if we're within 100px of the actual bottom
            return (scroll_top + window_height) >= (doc_height - 100)
        except:
            return True

    def reply_to_tweet(self, tweet_data: dict, reply_text: str):
        """Ultra-fast tweet reply with optimized text injection"""
        self._ensure_initialized()

        driver = self.driver
        wait = self.wait
        assert driver is not None
        assert wait is not None

        try:
            self._dismiss_overlays()

            time.sleep(random.uniform(2.7, 3.5))

            reply_button = tweet_data['reply_button']

            # Optimized scroll and click
            driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center'});
                arguments[0].click();
            """, reply_button)

            time.sleep(random.uniform(2.2, 3.7))

            # Fast textarea detection with multiple selectors
            reply_textarea = driver.execute_script("""
                const selectors = [
                    '[data-testid="tweetTextarea_0"]',
                    '[data-testid="tweetTextarea_1"]',
                    'div[role="textbox"][data-testid*="tweetTextarea"]',
                    'div[contenteditable="true"][role="textbox"]'
                ];

                for (let selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element && element.offsetParent !== null) {
                        return element;
                    }
                }
                return null;
            """)

            if not reply_textarea:
                raise Exception("Could not find reply textarea")

            time.sleep(random.uniform(12, 15.4))

            # Lightning-fast text injection with proper React event handling
            driver.execute_script("""
                const textarea = arguments[0];
                const text = arguments[1];

                // Focus and clear
                textarea.focus();
                textarea.value = '';

                // Create and dispatch paste event for React compatibility
                const dataTransfer = new DataTransfer();
                dataTransfer.setData('text/plain', text);
                const pasteEvent = new ClipboardEvent('paste', {
                    clipboardData: dataTransfer,
                    bubbles: true,
                    cancelable: true
                });

                textarea.dispatchEvent(pasteEvent);

                // Fallback: direct value set with events
                textarea.value = text;

                // Trigger React events
                const inputEvent = new Event('input', { bubbles: true });
                const changeEvent = new Event('change', { bubbles: true });
                textarea.dispatchEvent(inputEvent);
                textarea.dispatchEvent(changeEvent);
            """, reply_textarea, reply_text)

            time.sleep(random.uniform(4.5, 5.8))

            # Fast submit button detection and click
            reply_submit = driver.execute_script("""
                const selectors = [
                    '[data-testid="tweetButtonInline"]',
                    '[data-testid="tweetButton"]',
                    'div[role="button"][data-testid*="tweet"]'
                ];

                for (let selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element && element.offsetParent !== null && !element.disabled) {
                        element.click();
                        return true;
                    }
                }
                return false;
            """)

            if not reply_submit:
                raise Exception("Could not find or click reply submit button")

            time.sleep(1.5)  # Reduced wait for posting

            logger.info(f"Successfully replied to @{tweet_data['username']}")
            return True

        except Exception as e:
            logger.error(f"Failed to reply to tweet: {e}")
            return False

    def close(self):
        """Close the WebDriver safely"""
        logger.info("Closing WebDriver...")
        self._cleanup_driver()

    def reset_for_reuse(self):
        """Reset driver state for reuse without full recreation"""
        if not self.driver:
            return False

        try:
            # Clear caches
            self._element_cache.clear()

            # Clear browser state efficiently
            self.driver.execute_script("""
                // Clear any dialogs or overlays
                const overlays = document.querySelectorAll('[role="dialog"], .modal, [data-testid="mask"]');
                overlays.forEach(overlay => overlay.remove());

                // Clear any form states
                document.querySelectorAll('textarea, input').forEach(el => {
                    if (el.value) el.value = '';
                });
            """)

            # Navigate to home if not already there
            current_url = self.driver.current_url
            if not current_url.endswith('/home'):
                self.driver.get("https://x.com/home")
                time.sleep(1)

            logger.info("Driver reset for reuse completed")
            return True

        except Exception as e:
            logger.error(f"Failed to reset driver for reuse: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.close()

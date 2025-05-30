import time
import random
from typing import Optional
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Add random delay to mimic human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def safe_click(driver, element: WebElement, max_retries: int = 3) -> bool:
    """Safely click an element with retries"""
    for attempt in range(max_retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            random_delay(0.5, 1.5)
            element.click()
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            random_delay(1, 2)
    return False

def safe_send_keys(element: WebElement, text: str, clear_first: bool = True):
    """Safely send keys to an element"""
    if clear_first:
        element.clear()

    # Type with random delays to mimic human typing
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def wait_for_element(driver, by, value, timeout: int = 10) -> Optional[WebElement]:
    """Wait for element to be present and return it"""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None

def wait_for_clickable(driver, by, value, timeout: int = 10) -> Optional[WebElement]:
    """Wait for element to be clickable and return it"""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
    except TimeoutException:
        return None

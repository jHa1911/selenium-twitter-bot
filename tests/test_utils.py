import pytest
from src.utils.helpers import random_delay, safe_click
import time

def test_random_delay():
    start_time = time.time()
    random_delay(0.1, 0.2)
    end_time = time.time()

    elapsed = end_time - start_time
    assert 0.1 <= elapsed <= 0.3  # Allow some tolerance

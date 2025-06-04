import random
from typing import List, Optional
from loguru import logger

class ReplyGenerator:
    def __init__(self):
        self.python_replies = [
            "GN @giverep",
            "Lets connect @giverep"
        ]

        self.programming_replies = [
            "GN @giverep",
            "Lets connect @giverep"
        ]

        self.coding_replies = [
            "GN @giverep",
            "Lets connect @giverep"
        ]

        self.tutorial_replies = [
            "GN @giverep",
            "Lets connect @giverep"
        ]

        self.generic_replies = [
            "GN @giverep",
            "Lets connect @giverep"
        ]

    def generate_reply(self, tweet_text: str, keywords: List[str]) -> Optional[str]:
        """Generate an appropriate reply based on tweet content and keywords"""
        try:
            tweet_lower = tweet_text.lower()

            # Determine the most relevant category
            if any(keyword in tweet_lower for keyword in ['giverep']):
                replies = self.python_replies
            elif any(keyword in tweet_lower for keyword in ['giverep']):
                replies = self.programming_replies
            elif any(keyword in tweet_lower for keyword in ['giverep']):
                replies = self.coding_replies
            elif any(keyword in tweet_lower for keyword in ['giverep']):
                replies = self.tutorial_replies
            else:
                replies = self.generic_replies

            # Return random reply from selected category
            return random.choice(replies)

        except Exception as e:
            logger.error(f"Failed to generate reply: {e}")
            return None

    def should_reply_to_tweet(self, tweet_text: str, keywords: List[str]) -> bool:
        """Determine if we should reply to this tweet"""
        try:
            tweet_lower = tweet_text.lower()

            # Check if tweet contains any of our keywords
            for keyword in keywords:
                if keyword.lower() in tweet_lower:
                    return True

            # Additional checks
            # Avoid replying to retweets
            if tweet_text.startswith('RT @'):
                return False

            # Avoid very short tweets
            if len(tweet_text.strip()) < 20:
                return False

            # Avoid tweets with too many hashtags (likely spam)
            hashtag_count = tweet_text.count('#')
            if hashtag_count > 5:
                return False

            return False

        except Exception as e:
            logger.error(f"Error checking if should reply: {e}")
            return False

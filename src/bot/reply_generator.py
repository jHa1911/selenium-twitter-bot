from google import genai
import google.genai as genai
import random
from typing import List, Optional
from loguru import logger

class ReplyGenerator:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):

        self.model_name = model
        self.client = genai.Client(api_key=api_key)


        # Simple custom replies by keyword
        self.custom_replies = {
            "@giverep": ["Let's connect @giverep", "GM @giverep", "GN @giverep", "Hey @giverep, how's it going?"],
            "giverep": ["Let's connect @giverep", "GM @giverep", "GN @giverep", "Hey @giverep, how's it going?"],

        }

    def generate_reply(self, tweet_text: str, keywords: List[str], max_length: int = 280) -> Optional[str]:
        """Generate an appropriate reply based on tweet content and keywords"""
        try:
            tweet_lower = tweet_text.lower()
            # Check if any keyword matches and return custom reply
            for keyword in keywords:
                if keyword.lower() in tweet_lower:
                    if keyword.lower() in self.custom_replies:
                        reply = random.choice(self.custom_replies[keyword.lower()])
                        logger.info(f"Custom reply for '{keyword}': {reply}")
                        return reply

            prompt = f'Write one brief, engaging reply to this tweet that sounds natural and human: : "{tweet_lower}"'

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            if response and response.text:
                reply = response.text.strip()

                # Remove quotes if Gemini adds them
                if reply.startswith('"') and reply.endswith('"'):
                    reply = reply[1:-1]

                # Ensure it's within Twitter's character limit
                if len(reply) > max_length:
                    reply = reply[:max_length-3] + "..."

                logger.info(f"Generated AI reply: {reply}...")
                return reply

            # Fallback
            return "Thanks for sharing!"



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

            """# Avoid very short tweets
            if len(tweet_text.strip()) < 20:
                return False"""

            # Avoid tweets with too many hashtags (likely spam)
            hashtag_count = tweet_text.count('#')
            if hashtag_count > 5:
                return False

            return False

        except Exception as e:
            logger.error(f"Error checking if should reply: {e}")
            return False


        """
        # Determine the most relevant category
            if any(keyword in tweet_lower for keyword in keywords):
                replies = self.python_replies
            elif any(keyword in tweet_lower for keyword in keywords):
                replies = self.programming_replies
            elif any(keyword in tweet_lower for keyword in keywords):
                replies = self.coding_replies
            elif any(keyword in tweet_lower for keyword in keywords):
                replies = self.tutorial_replies
            else:
                replies = self.generic_replies

            # Return random reply from selected category
            return random.choice(replies)
        """

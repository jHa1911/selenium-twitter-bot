import random
from typing import List, Optional
from loguru import logger

class ReplyGenerator:
    def __init__(self):
        self.python_replies = [
            "Great point! Python's simplicity makes it perfect for beginners. Have you tried exploring libraries like pandas or numpy?",
            "Python is indeed powerful! The vast ecosystem of libraries makes it versatile for any project.",
            "Love seeing Python discussions! The community is so supportive and welcoming to newcomers.",
            "Python's readability is one of its biggest strengths. It really follows the 'code is read more than written' principle.",
            "Awesome! Python's versatility never ceases to amaze me. What's your favorite Python framework?",
            "Python makes complex tasks look simple. That's the beauty of good language design!",
            "The Python community is fantastic! Always willing to help and share knowledge.",
            "Python + automation = productivity boost! Have you tried automating any workflows?",
            "Great example! Python's clean syntax makes code so much more maintainable.",
            "Python's 'batteries included' philosophy really shines in projects like this!"
        ]

        self.programming_replies = [
            "Clean code is so important! Thanks for sharing this approach.",
            "Love the problem-solving approach here! Programming is all about breaking down complex problems.",
            "Great debugging tip! These kinds of insights are incredibly valuable for developers.",
            "The programming community never stops learning. Thanks for contributing to the knowledge pool!",
            "Solid solution! It's always great to see different approaches to the same problem.",
            "This is why I love programming - there's always a more elegant solution waiting to be discovered.",
            "Documentation like this makes such a difference for other developers. Thank you!",
            "Programming best practices in action! This will help many developers.",
            "The evolution of programming practices is fascinating. Thanks for sharing your experience!",
            "Code review culture at its best! Constructive feedback makes us all better programmers."
        ]

        self.coding_replies = [
            "Code readability matters so much! This is a great example of clean, understandable code.",
            "Love seeing well-structured code! Organization makes such a difference in maintainability.",
            "This coding pattern is really useful! Thanks for sharing your implementation.",
            "Great coding practice! This approach will definitely help other developers.",
            "Clean code principles in action! This is how readable code should look like.",
            "Excellent coding style! The comments and structure make it easy to follow.",
            "This is why coding standards are so important. Great example!",
            "Coding is an art, and this is a beautiful piece of work!",
            "The attention to detail in this code is impressive. Well done!",
            "This coding approach saves so much time and effort. Thanks for sharing!"
        ]

        self.tutorial_replies = [
            "Excellent tutorial! The step-by-step approach makes it easy to follow along.",
            "This tutorial fills a real gap in the learning resources. Thank you for creating it!",
            "Love how you explained this concept! Tutorials like this make learning so much easier.",
            "Great educational content! The examples really help solidify the concepts.",
            "This tutorial is going to help so many people. Thanks for taking the time to create it!",
            "Perfect timing! I was just looking for a tutorial on this topic.",
            "The clarity in this tutorial is outstanding. You have a gift for teaching!",
            "Bookmarking this tutorial! It's going to be a great reference resource.",
            "This tutorial approach makes complex topics accessible. Really well done!",
            "Educational content like this is what makes the tech community so strong!"
        ]

        self.generic_replies = [
            "Thanks for sharing! This is really insightful.",
            "Great point! I hadn't thought about it from this perspective.",
            "This is exactly what I needed to see today. Thank you!",
            "Valuable insights! Thanks for contributing to the discussion.",
            "Appreciate you sharing your experience and knowledge!",
            "This resonates with me. Thanks for the thoughtful post!",
            "Great contribution to the community! This will help many people.",
            "Thanks for taking the time to share this. It's really helpful!",
            "Your perspective adds real value to this conversation.",
            "This kind of knowledge sharing makes our community stronger!"
        ]

    def generate_reply(self, tweet_text: str, keywords: List[str]) -> Optional[str]:
        """Generate an appropriate reply based on tweet content and keywords"""
        try:
            tweet_lower = tweet_text.lower()

            # Determine the most relevant category
            if any(keyword in tweet_lower for keyword in ['python', 'py', 'django', 'flask', 'pandas', 'numpy']):
                replies = self.python_replies
            elif any(keyword in tweet_lower for keyword in ['programming', 'software', 'developer', 'development']):
                replies = self.programming_replies
            elif any(keyword in tweet_lower for keyword in ['code', 'coding', 'function', 'class', 'method']):
                replies = self.coding_replies
            elif any(keyword in tweet_lower for keyword in ['tutorial', 'guide', 'how to', 'learn', 'beginner']):
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

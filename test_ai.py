import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Get API key directly from environment
api_key = os.getenv('TWITTER_API_KEY')
if not api_key:
    raise ValueError("TWITTER_API_KEY not found in .env file")

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

# Generate content using Gemini 2.0 Flash
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works in a few words"
)

# Print the response
print(response.text)

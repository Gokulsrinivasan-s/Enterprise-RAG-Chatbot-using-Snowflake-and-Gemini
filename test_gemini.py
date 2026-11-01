import os
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Ask Gemini
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello to Gokul."
)

print(response.text)
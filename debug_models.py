
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
print(f"API Key present: {bool(api_key)}")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Client initialized. Listing models...")
        # Note: The new SDK might use a different method to list models.
        # I'll try to iterate if possible, or print what I can find.
        # Based on typical google-genai usage:
        for model in client.models.list():
            print(f"Model: {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("No API KEY found.")

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiService:

    def ask(self, question):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question,
        )

        return response.text
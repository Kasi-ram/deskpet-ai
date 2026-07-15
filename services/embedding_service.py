import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class EmbeddingService:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model = os.getenv(
            "EMBEDDING_MODEL",
            "gemini-embedding-001"
        )

    def embed(self, text):

        if not text or not text.strip():

            raise ValueError(
                "Embedding text cannot be empty."
            )

        response = self.client.models.embed_content(
            model=self.model,
            contents=text
        )

        return response.embeddings[0].values
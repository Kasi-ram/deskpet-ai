import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class OpenAIService:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5-mini"
        )

    def ask(self, prompt):

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text

    def stream(self, prompt):

        with self.client.responses.stream(
            model=self.model,
            input=prompt
        ) as stream:

            for event in stream:

                if (
                    event.type
                    == "response.output_text.delta"
                ):
                    yield event.delta

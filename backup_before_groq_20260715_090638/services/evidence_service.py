import json

from services.openai_service import OpenAIService


class EvidenceService:

    def __init__(self):
        self.llm_service = OpenAIService()

    def select(self, question, results):

        formatted_chunks = []

        for index, result in enumerate(results):
            formatted_chunks.append(
                f"""
CHUNK_ID: {index}

CONTENT:
{result["document"]}
"""
            )

        chunks_text = "\n".join(formatted_chunks)

        prompt = f"""
You are an evidence selection system.

Your task is to identify which chunks directly help answer
the user's question.

Return only a JSON array containing the relevant CHUNK_ID values.

Do not explain your answer.

Example response:
[1, 4]

If no chunk directly supports the answer, return:
[]

USER QUESTION:
{question}

CHUNKS:
{chunks_text}
"""

        response = self.llm_service.ask(prompt)

        return self._parse_response(
            response,
            results
        )

    def _parse_response(self, response, results):

        try:
            chunk_ids = json.loads(response)

            return [
                results[chunk_id]
                for chunk_id in chunk_ids
                if 0 <= chunk_id < len(results)
            ]

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):
            return []
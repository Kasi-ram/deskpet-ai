import json

from services.groq_service import GroqService


class EvidenceService:

    def __init__(self):
        self.llm_service = GroqService()

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

Select chunks that contain information useful for answering
the user's question.

Understand semantically equivalent wording.

Examples of semantic equivalence:

- travel commenced = travel started
- schedule change = date, flight, or route change
- after departure = after travel started

Prefer chunks containing an explicit policy rule.

Do not answer the user's question.

Return ONLY a JSON array of CHUNK_ID values.

Example:

[2, 4]

If no useful evidence exists:

[]

USER QUESTION:

{question}

CHUNKS:

{chunks_text}
"""

        response = self.llm_service.ask(prompt)

        print("\nEVIDENCE SELECTOR RESPONSE")
        print(response)

        return self._parse_response(
            response,
            results
        )

    def _parse_response(self, response, results):

        try:

            response = response.strip()

            if response.startswith("```"):

                response = response.replace(
                    "```json",
                    ""
                )

                response = response.replace(
                    "```",
                    ""
                )

                response = response.strip()

            chunk_ids = json.loads(response)

            if not isinstance(chunk_ids, list):
                return []

            return [
                results[chunk_id]
                for chunk_id in chunk_ids
                if (
                    isinstance(chunk_id, int)
                    and 0 <= chunk_id < len(results)
                )
            ]

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):

            print(
                "FAILED TO PARSE EVIDENCE RESPONSE:",
                response
            )

            return []
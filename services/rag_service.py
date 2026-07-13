from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService
from services.gemini_service import GeminiService


class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.gemini_service = GeminiService()

    def ask(self, question):
        question_embedding = self.embedding_service.embed(
            question
        )

        chunks = self.chroma_service.search(
            question_embedding,
            limit=5
        )

        context = "\n\n".join(chunks)

        prompt = f"""
        You are an airline knowledge assistant.

        Answer the user's question using the provided context.

        You may interpret semantically equivalent terms and make direct logical
        inferences that are clearly supported by the context.

        For example:
        - "travel schedule changes" may refer to date, flight, or route changes.
        - "hand luggage" may refer to cabin baggage or carry-on baggage.

        Do not add facts that are not supported by the context.

        If the context does not contain enough information to answer the question,
        say:
        "I could not find this information in the available knowledge base."

        CONTEXT:
        {context}

        USER QUESTION:
        {question}

        ANSWER:
        """

        return self.gemini_service.ask(prompt)
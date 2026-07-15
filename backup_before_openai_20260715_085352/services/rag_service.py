from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService
from services.gemini_service import GeminiService
from services.evidence_service import EvidenceService


class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.gemini_service = GeminiService()
        self.evidence_service = EvidenceService()

    def _build_sources(self, results):

        sources = []

        for result in results:

            metadata = result["metadata"]

            source = {
                "source": metadata["source"],
                "page": metadata["page"]
            }

            if source not in sources:
                sources.append(source)

        return sources

    def retrieve(self, question):

        question_embedding = self.embedding_service.embed(question)

        results = self.chroma_service.search(
            question_embedding,
            limit=10
        )

        if not results:
            return None

        evidence = self.evidence_service.select(
            question,
            results
        )

        if not evidence:
            return None

        return evidence

    def build_prompt(self, question, evidence):

        chunks = [
            result["document"]
            for result in evidence
        ]

        context = "\n\n".join(chunks)

        return f"""
    You are an airline knowledge assistant.

    Answer the user's question using ONLY the provided context.

    If the answer is not available, reply:

    "I could not find this information in the available knowledge base."

    CONTEXT:
    {context}

    USER QUESTION:
    {question}

    ANSWER:
    """

    def ask(self, question):

        evidence = self.retrieve(question)

        if not evidence:
            return {
                "answer": (
                    "I could not find this information "
                    "in the available knowledge base."
                ),
                "sources": []
            }

        prompt = self.build_prompt(
            question,
            evidence
        )

        answer = self.gemini_service.ask(prompt)

        return {
            "answer": answer,
            "sources": self._build_sources(evidence)
        }
    
    def stream(self, question):

        evidence = self.retrieve(question)

        if not evidence:

            yield {
                "type": "error",
                "message": (
                    "I could not find this information "
                    "in the available knowledge base."
                )
            }

            return

        prompt = self.build_prompt(
            question,
            evidence
        )

        yield {
            "type": "sources",
            "sources": self._build_sources(evidence)
        }

        for token in self.gemini_service.stream(prompt):

            yield {
                "type": "token",
                "value": token
            }
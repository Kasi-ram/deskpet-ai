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

    def ask(self, question):

        question_embedding = (
            self.embedding_service.embed(question)
        )

        results = self.chroma_service.search(
            question_embedding,
            limit=10
        )

        if not results:
            return {
                "answer": (
                    "I could not find this information "
                    "in the available knowledge base."
                ),
                "sources": []
            }
        
        evidence = self.evidence_service.select(
                question,
                results
            )

        if not evidence:
                return {
                    "answer": (
                        "I could not find this information "
                        "in the available knowledge base."
                    ),
                    "sources": []
                }

        chunks = [
            result["document"]
            for result in evidence
        ]

        context = "\n\n".join(chunks)

        prompt = f"""
    You are an airline knowledge assistant.

    Answer the user's question using the provided context.

    You may interpret semantically equivalent terms and make direct
    logical inferences clearly supported by the context.

    Do not add facts that are not supported by the context.

    If the context does not contain enough information to answer,
    say:
    "I could not find this information in the available knowledge base."

    CONTEXT:
    {context}

    USER QUESTION:
    {question}

    ANSWER:
    """

        answer = self.gemini_service.ask(prompt)

        sources = self._build_sources(evidence)

        return {
            "answer": answer,
            "sources": sources
        }
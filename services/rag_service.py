from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService
from services.groq_service import GroqService
from services.evidence_service import EvidenceService


class RAGService:

    NOT_FOUND = (
        "I could not find this information "
        "in the available knowledge base."
    )

    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

        self.chroma_service = (
            ChromaService()
        )

        self.llm_service = GroqService()

        self.evidence_service = (
            EvidenceService()
        )

    def _build_sources(
        self,
        results
    ):

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

    def retrieve(
        self,
        question
    ):

        question_embedding = (
            self.embedding_service.embed(
                question
            )
        )

        return self.chroma_service.search(
            question_embedding,
            limit=10
        )

    def ask(
        self,
        question
    ):

        results = self.retrieve(
            question
        )

        if not results:

            return {
                "answer": self.NOT_FOUND,
                "sources": [],
                "found": False
            }

        evidence = (
            self.evidence_service.select(
                question,
                results
            )
        )

        if not evidence:

            return {
                "answer": self.NOT_FOUND,
                "sources": [],
                "found": False
            }

        context = "\n\n".join(
            [
                f"""
EVIDENCE {index}

SOURCE:
{result["metadata"]["source"]}

PAGE:
{result["metadata"]["page"]}

CONTENT:
{result["document"]}
"""
                for index, result
                in enumerate(
                    evidence,
                    start=1
                )
            ]
        )

        prompt = f"""
You are DeskPet AI, an airline knowledge assistant.

Answer the user's exact question using only
the provided evidence.

Rules:

1. Do not add unsupported facts.

2. Do not answer a different but similar question.

3. Complimentary tickets and complimentary bags
   are different concepts.

4. If the evidence does not answer the exact
   question, respond exactly:

"{self.NOT_FOUND}"

5. Give a direct concise answer.

6. Do not mention EVIDENCE numbers in the answer.

EVIDENCE:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        answer = self.llm_service.ask(
            prompt
        ).strip()

        if self.NOT_FOUND.lower() in answer.lower():

            return {
                "answer": self.NOT_FOUND,
                "sources": [],
                "found": False
            }

        return {
            "answer": answer,
            "sources": self._build_sources(
                evidence
            ),
            "found": True
        }
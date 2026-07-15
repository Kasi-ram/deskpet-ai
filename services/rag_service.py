from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService
from services.groq_service import GroqService
from services.evidence_service import EvidenceService


class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.llm_service = GroqService()
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

        question_embedding = (
            self.embedding_service.embed(question)
        )

        results = self.chroma_service.search(
            question_embedding,
            limit=10
        )

        if not results:
            return None

        return results

    def build_prompt(self, question, evidence):

            context_parts = []

            for index, result in enumerate(evidence, start=1):

                metadata = result["metadata"]

                context_parts.append(
                    f"""
        EVIDENCE {index}
        SOURCE: {metadata["source"]}
        PAGE: {metadata["page"]}

        {result["document"]}
        """
                )

            context = "\n\n".join(context_parts)

            return f"""
        You are an airline policy knowledge assistant.

        Answer the user using ONLY the supplied evidence.

        If the user's question does not exactly match the available policy,
        but you find closely related information,
        state that the exact policy was not found and then present the related policy.
        Do not imply that the related policy answers the original question.

        RULES:

        1. Identify the evidence that most directly answers the user's exact intent.
        2. Prefer a direct policy statement over a related or indirect statement.
        3. Do not substitute a rule about name changes when the user asks about date, flight, route, or travel schedule changes.
        4. Semantically equivalent wording should be interpreted naturally.
        5. If a direct policy statement answers the question, use that statement.
        6. Do not invent information.
        7. Only say information is unavailable when none of the evidence answers the question.
        8. Pay close attention to conditions, timing, and exceptions.
        9. A policy applying AFTER an event must not automatically
        be applied BEFORE that event.
        10. If the user asks about "before commencement" and the
            context only contains a rule for "once travel has commenced",
            do not use that rule as the answer.
        11. Do not reverse a policy rule or infer the opposite.
        12. If the evidence does not directly establish the answer,
            say:
            "I could not find this information in the available knowledge base."

        EVIDENCE:

        {context}

        USER QUESTION:

        {question}

        Return a short, direct answer.
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

        answer = self.llm_service.ask(prompt)

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

        for token in self.llm_service.stream(prompt):

            yield {
                "type": "token",
                "value": token
            }
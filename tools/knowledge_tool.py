from services.rag_service import RAGService


class KnowledgeTool:

    def __init__(self):

        self.rag = RAGService()

    def execute(
        self,
        question,
        knowledge_base_id="default"
    ):

        return self.rag.ask(
            question,
            knowledge_base_id
        )

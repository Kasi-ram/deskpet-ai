from services.rag_service import RAGService


class KnowledgeTool:

    def __init__(self):
        self.rag = RAGService()

    def execute(self, question):

        return self.rag.ask(question)
from services.rag_service import RAGService


rag = RAGService()


question = "whether travel schedule changes are allowed once travel has commenced?"


answer = rag.ask(question)


print("QUESTION")
print(question)

print("\nANSWER")
print(answer)
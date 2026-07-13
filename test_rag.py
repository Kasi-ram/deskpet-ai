from services.rag_service import RAGService


rag = RAGService()

question = (
    "whether travel schedule changes are allowed "
    "once travel has commenced?"
)

response = rag.ask(question)


print("\nQUESTION")
print(question)


print("\nANSWER")
print(response["answer"])


print("\nSOURCES")

for source in response["sources"]:

    print(
        f'{source["source"]} '
        f'- Page {source["page"]}'
    )
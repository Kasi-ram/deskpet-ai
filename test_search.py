from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService


embedding_service = EmbeddingService()
chroma_service = ChromaService()


question = "Who won the Cricket World Cup?"


question_embedding = embedding_service.embed(
    question
)


results = chroma_service.search(
    question_embedding,
    limit=10
)


print("\nQUESTION")
print(question)


print("\nRETRIEVAL RESULTS")


for index, (chunk, distance) in enumerate(results):

    print("\n" + "=" * 60)

    print(
        f"RESULT {index + 1} | "
        f"DISTANCE: {distance:.4f}"
    )

    print("=" * 60)

    print(chunk)
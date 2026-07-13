from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService
from services.evidence_service import EvidenceService


embedding_service = EmbeddingService()
chroma_service = ChromaService()
evidence_service = EvidenceService()


question = (
    "whether travel schedule changes are allowed "
    "once travel has commenced?"
)


question_embedding = embedding_service.embed(
    question
)


results = chroma_service.search(
    question_embedding,
    limit=10
)


evidence = evidence_service.select(
    question,
    results
)


print("\nSELECTED EVIDENCE")


for result in evidence:

    print("\n" + "=" * 60)

    print(
        "DISTANCE:",
        result["distance"]
    )

    print(
        "SOURCE:",
        result["metadata"]
    )

    print(result["document"])
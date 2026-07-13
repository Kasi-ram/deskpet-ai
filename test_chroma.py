from services.pdf_service import PDFService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService


pdf_service = PDFService()
chunk_service = ChunkService()
embedding_service = EmbeddingService()
chroma_service = ChromaService()


pages = pdf_service.extract_pages(
    "data/airline_policy.pdf"
)

chunks = chunk_service.split_pages(pages)

print("Total chunks:", len(chunks))


embeddings = []

for index, chunk in enumerate(chunks):

    print(
        f"Generating embedding {index + 1}/{len(chunks)}"
    )

    embedding = embedding_service.embed(
            chunk["text"]
        )

    embeddings.append(embedding)


chroma_service.add_chunks(
    chunks,
    embeddings,
    source="British Airways Group Terms"
)

print("Indexing completed.")
from services.pdf_service import PDFService
from services.chunk_service import ChunkService


pdf_service = PDFService()
chunk_service = ChunkService()


text = pdf_service.extract_text(
    "data/airline_policy.pdf"
)

chunks = chunk_service.split_text(text)


print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    print("\n")
    print("=" * 50)
    print(f"CHUNK {index + 1}")
    print("=" * 50)
    print(chunk)
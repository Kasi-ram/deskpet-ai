from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService
from services.document_processor import DocumentProcessor
from services.document_registry import DocumentRegistry


class DocumentIngestionService:

    def __init__(self):

        self.document_processor = (
            DocumentProcessor()
        )

        self.chunk_service = ChunkService()

        self.embedding_service = (
            EmbeddingService()
        )

        self.chroma_service = (
            ChromaService()
        )

        self.registry = DocumentRegistry()

    def ingest_document(
        self,
        uploaded_file
    ):

        file_bytes = uploaded_file.getvalue()

        file_hash = (
            self.registry.calculate_hash(
                file_bytes
            )
        )

        if self.registry.exists(file_hash):

            return {
                "status": "duplicate",
                "source": uploaded_file.name
            }

        try:

            pages = (
                self.document_processor.process(
                    uploaded_file
                )
            )

            chunks = []

            for page_number, text in pages:

                page_chunks = (
                    self.chunk_service.split_text(
                        text
                    )
                )

                for chunk_text in page_chunks:

                    if not chunk_text.strip():
                        continue

                    chunks.append(
                        {
                            "text": chunk_text,
                            "page": page_number
                        }
                    )

            if not chunks:

                return {
                    "status": "empty",
                    "source": uploaded_file.name,
                    "pages": len(pages),
                    "chunks": 0
                }

            embeddings = [
                self.embedding_service.embed(
                    chunk["text"]
                )
                for chunk in chunks
            ]

            self.chroma_service.add_chunks(
                chunks=chunks,
                embeddings=embeddings,
                source=uploaded_file.name
            )

            self.registry.register(
                file_hash=file_hash,
                filename=uploaded_file.name,
                pages=len(pages),
                chunks=len(chunks)
            )

            return {
                "status": "success",
                "source": uploaded_file.name,
                "pages": len(pages),
                "chunks": len(chunks)
            }

        except Exception as error:

            return {
                "status": "failed",
                "source": uploaded_file.name,
                "message": str(error)
            }

    def reset(self):

        self.chroma_service.clear()

        self.registry.clear()

    def stats(self):

        return {
            "documents": self.registry.count(),
            "chunks": self.chroma_service.count()
        }

    def documents(self):

        return self.registry.list_documents()
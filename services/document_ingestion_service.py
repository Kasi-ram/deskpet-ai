import os
import tempfile

from services.pdf_service import PDFService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.chroma_service import ChromaService


class DocumentIngestionService:

    def __init__(self):

        self.pdf_service = PDFService()
        self.chunk_service = ChunkService()
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()

    def ingest_pdf(self, uploaded_file):

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = temp_file.name

            pages = self.pdf_service.extract_pages(
                temp_path
            )

            chunks = []

            for page_number, text in pages:

                page_chunks = (
                    self.chunk_service.split_text(
                        text
                    )
                )

                for chunk_text in page_chunks:

                    chunks.append(
                        {
                            "text": chunk_text,
                            "page": page_number
                        }
                    )

            if not chunks:

                return {
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

            return {
                "source": uploaded_file.name,
                "pages": len(pages),
                "chunks": len(chunks)
            }

        finally:

            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                os.remove(temp_path)
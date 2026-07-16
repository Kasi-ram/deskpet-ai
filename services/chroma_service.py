import chromadb
import hashlib
from pathlib import Path


class ChromaService:

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DB_PATH = str(PROJECT_ROOT / "chroma_db")
    COLLECTION_NAME = "airline_documents"

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=self.DB_PATH
        )

        self._load_collection()

    def _load_collection(self):

        self.collection = (
            self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        )

    def add_chunks(
        self,
        chunks,
        embeddings,
        source,
        document_id,
        knowledge_base_id
    ):

        ids = [
            hashlib.sha256(
                f"{document_id}:{index}".encode("utf-8")
            ).hexdigest()
            for index, _ in enumerate(chunks)
        ]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "source": source,
                "page": chunk["page"],
                "document_id": document_id,
                "knowledge_base_id": knowledge_base_id
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        knowledge_base_id,
        limit=10
    ):

        where = {
            "knowledge_base_id": knowledge_base_id
        }

        total_count = self.collection.count()

        if total_count == 0:
            return []

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=min(limit, total_count),
            where=where
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        return [
            {
                "document": document,
                "metadata": metadata,
                "distance": distance
            }
            for document, metadata, distance
            in zip(
                documents,
                metadatas,
                distances
            )
        ]

    def count(self, knowledge_base_id):

        results = self.collection.get(
            where={"knowledge_base_id": knowledge_base_id},
            include=[]
        )

        return len(results["ids"])

    def delete_document(
        self,
        document_id,
        knowledge_base_id
    ):

        self.collection.delete(
            where={
                "$and": [
                    {"document_id": document_id},
                    {"knowledge_base_id": knowledge_base_id}
                ]
            }
        )

    def clear(self, knowledge_base_id):

        self.collection.delete(
            where={"knowledge_base_id": knowledge_base_id}
        )

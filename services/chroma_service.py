import chromadb
import uuid


class ChromaService:

    DB_PATH = "chroma_db"
    COLLECTION_NAME = "airline_documents"

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=self.DB_PATH
        )

        self._load_collection()

    def _load_collection(self):

        self.collection = (
            self.client.get_or_create_collection(
                name=self.COLLECTION_NAME
            )
        )

    def add_chunks(
        self,
        chunks,
        embeddings,
        source
    ):

        ids = [
            str(uuid.uuid4())
            for _ in chunks
        ]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "source": source,
                "page": chunk["page"]
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        limit=10
    ):

        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=min(
                limit,
                self.collection.count()
            )
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

    def count(self):

        return self.collection.count()

    def clear(self):

        try:
            self.client.delete_collection(
                name=self.COLLECTION_NAME
            )

        except Exception:
            pass

        self._load_collection()
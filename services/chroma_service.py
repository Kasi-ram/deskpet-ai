import chromadb


class ChromaService:

    def __init__(self, path="chroma_db"):
        self.client = chromadb.PersistentClient(
            path=path
        )

        self.collection = self.client.get_or_create_collection(
            name="deskpet_knowledge"
        )

    def add_chunks(
        self,
        chunks,
        embeddings,
        source
    ):
        ids = [
            f"chunk_{index}"
            for index in range(len(chunks))
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
        limit=10,
        max_distance=0.85
    ):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=[
                "documents",
                "distances",
                "metadatas"
            ]
        )

        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        relevant_results = []

        for document, distance, metadata in zip(
            documents,
            distances,
            metadatas
        ):
            if distance <= max_distance:
                relevant_results.append({
                    "document": document,
                    "distance": distance,
                    "metadata": metadata
                })

        return relevant_results
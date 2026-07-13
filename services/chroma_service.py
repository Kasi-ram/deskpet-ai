import chromadb


class ChromaService:

    def __init__(self, path="chroma_db"):
        self.client = chromadb.PersistentClient(
            path=path
        )

        self.collection = self.client.get_or_create_collection(
            name="deskpet_knowledge"
        )

    def add_chunks(self, chunks, embeddings):
        ids = [
            f"chunk_{index}"
            for index in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings
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
            include=["documents", "distances"]
        )

        documents = results["documents"][0]
        distances = results["distances"][0]

        relevant_results = []

        for document, distance in zip(
            documents,
            distances
        ):
            if distance <= max_distance:
                relevant_results.append(
                    (document, distance)
                )

        return relevant_results
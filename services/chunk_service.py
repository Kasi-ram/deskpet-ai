from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkService:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def split_text(self, text):
        return self.splitter.split_text(text)
    
    def split_pages(self, pages):
        chunks = []

        for page in pages:

            page_chunks = self.split_text(
                page["text"]
            )

            for chunk in page_chunks:
                chunks.append({
                    "text": chunk,
                    "page": page["page"]
                })

        return chunks
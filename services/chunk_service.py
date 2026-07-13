class ChunkService:

    def split_text(self, text, chunk_size=500, overlap=100):
        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:

            end = min(start + chunk_size, text_length)

            if end < text_length:
                end = self._find_boundary(text, start, end)

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = end - overlap

            # Safety check: always move forward
            if next_start <= start:
                next_start = end

            start = self._find_start_boundary(
                text,
                next_start
            )

        return chunks


    def _find_boundary(self, text, start, end):

        search_start = start + int(
            (end - start) * 0.7
        )

        boundaries = [
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            " "
        ]

        for boundary in boundaries:

            position = text.rfind(
                boundary,
                search_start,
                end
            )

            if position != -1:
                return position + len(boundary)

        return end
    
    def _find_start_boundary(self, text, start):

        if start <= 0:
            return 0

        while (
            start < len(text)
            and not text[start].isspace()
        ):
            start += 1

        while (
            start < len(text)
            and text[start].isspace()
        ):
            start += 1

        return start
class TextService:

    def extract_pages(self, text_bytes):

        text = text_bytes.decode("utf-8")

        return [
            (
                1,
                text
            )
        ]
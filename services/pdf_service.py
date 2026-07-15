import fitz


class PDFService:

    def extract_pages(self, pdf_bytes):

        pages = []

        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as doc:

            for page_number, page in enumerate(
                doc,
                start=1
            ):

                text = page.get_text()

                if text and text.strip():

                    pages.append(
                        (
                            page_number,
                            text.strip()
                        )
                    )

        return pages


    def extract_text(self, pdf_bytes):

        pages = self.extract_pages(pdf_bytes)

        return "\n".join(
            page_text
            for _, page_text in pages
        )